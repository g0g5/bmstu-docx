from __future__ import annotations

import re
from pathlib import Path

from markdown_it import MarkdownIt
from markdown_it.token import Token

from .models import (
    Block,
    CodeBlock,
    HeadingBlock,
    ImageBlock,
    InlineSpan,
    ListBlock,
    ListItem,
    ParagraphBlock,
    TableBlock,
    TableCell,
    TableRow,
)

TABLE_CAPTION_RE = re.compile(
    r"^(?:Таблица|Table)\s+\d+[\w.-]*\s*[-–—]\s+.+$", re.IGNORECASE
)
FIGURE_CAPTION_RE = re.compile(
    r"^(?:Рисунок|Figure)\s+\d+[\w.-]*\s*[-–—]\s+.+$", re.IGNORECASE
)
STRUCTURAL_HEADINGS = {
    "ВВЕДЕНИЕ",
    "ЗАКЛЮЧЕНИЕ",
    "INTRODUCTION",
    "CONCLUSION",
}


class MarkdownParser:
    def __init__(self) -> None:
        self._md = MarkdownIt("commonmark").enable("table")

    def parse(
        self, markdown_text: str, base_path: str | Path | None = None
    ) -> list[Block]:
        tokens = self._md.parse(markdown_text)
        root = Path(base_path or ".").resolve()
        blocks, _ = self._parse_blocks(tokens, 0, set(), root)
        return self._apply_block_conventions(blocks)

    def _parse_blocks(
        self,
        tokens: list[Token],
        index: int,
        stop_types: set[str],
        base_path: Path,
    ) -> tuple[list[Block], int]:
        blocks: list[Block] = []

        while index < len(tokens):
            token = tokens[index]
            if token.type in stop_types:
                break

            if token.type == "heading_open":
                block, index = self._parse_heading(tokens, index)
                blocks.append(block)
                continue

            if token.type == "paragraph_open":
                block, index = self._parse_paragraph(tokens, index, base_path)
                blocks.append(block)
                continue

            if token.type in {"fence", "code_block"}:
                blocks.append(CodeBlock(code=token.content, info=token.info or ""))
                index += 1
                continue

            if token.type in {"bullet_list_open", "ordered_list_open"}:
                block, index = self._parse_list(tokens, index, base_path)
                blocks.append(block)
                continue

            if token.type == "table_open":
                block, index = self._parse_table(tokens, index)
                blocks.append(block)
                continue

            if token.type == "blockquote_open":
                nested_blocks, index = self._parse_blocks(
                    tokens, index + 1, {"blockquote_close"}, base_path
                )
                for nested_block in nested_blocks:
                    if isinstance(nested_block, ParagraphBlock):
                        nested_block.kind = "blockquote"
                blocks.extend(nested_blocks)
                index += 1
                continue

            if token.type == "hr":
                index += 1
                continue

            index += 1

        return blocks, index

    def _parse_heading(
        self, tokens: list[Token], index: int
    ) -> tuple[HeadingBlock, int]:
        open_token = tokens[index]
        inline_token = tokens[index + 1]
        spans = self._parse_inline(inline_token.children or [])
        text = self._spans_to_text(spans)
        normalized = " ".join(text.split())
        structural = normalized.upper() in STRUCTURAL_HEADINGS
        return HeadingBlock(
            level=int(open_token.tag[1]), spans=spans, structural=structural
        ), index + 3

    def _parse_paragraph(
        self, tokens: list[Token], index: int, base_path: Path
    ) -> tuple[Block, int]:
        inline_token = tokens[index + 1]
        children = inline_token.children or []
        image_block = self._parse_image_only_paragraph(children, base_path)
        if image_block is not None:
            return image_block, index + 3
        return ParagraphBlock(spans=self._parse_inline(children)), index + 3

    def _parse_image_only_paragraph(
        self, children: list[Token], base_path: Path
    ) -> ImageBlock | None:
        significant = []
        for child in children:
            if child.type in {"softbreak", "hardbreak"}:
                continue
            if child.type == "text" and not child.content.strip():
                continue
            significant.append(child)

        if len(significant) != 1 or significant[0].type != "image":
            return None

        image_token = significant[0]
        src = image_token.attrs.get("src", "") if image_token.attrs else ""
        image_path = Path(src)
        if not image_path.is_absolute():
            image_path = (base_path / image_path).resolve()
        return ImageBlock(path=str(image_path), alt_text=image_token.content or "")

    def _parse_list(
        self, tokens: list[Token], index: int, base_path: Path
    ) -> tuple[ListBlock, int]:
        ordered = tokens[index].type == "ordered_list_open"
        close_type = "ordered_list_close" if ordered else "bullet_list_close"
        index += 1
        items: list[ListItem] = []

        while index < len(tokens) and tokens[index].type != close_type:
            if tokens[index].type != "list_item_open":
                index += 1
                continue
            item_blocks, index = self._parse_blocks(
                tokens, index + 1, {"list_item_close"}, base_path
            )
            items.append(ListItem(blocks=item_blocks))
            if index < len(tokens) and tokens[index].type == "list_item_close":
                index += 1

        if index < len(tokens) and tokens[index].type == close_type:
            index += 1
        return ListBlock(ordered=ordered, items=items), index

    def _parse_table(self, tokens: list[Token], index: int) -> tuple[TableBlock, int]:
        rows: list[TableRow] = []
        header_mode = False
        current_cells: list[TableCell] = []
        current_inline: list[Token] = []
        in_cell = False

        index += 1
        while index < len(tokens) and tokens[index].type != "table_close":
            token = tokens[index]

            if token.type == "thead_open":
                header_mode = True
            elif token.type == "tbody_open":
                header_mode = False
            elif token.type == "tr_open":
                current_cells = []
            elif token.type in {"th_open", "td_open"}:
                in_cell = True
                current_inline = []
            elif token.type == "inline" and in_cell:
                current_inline.append(token)
            elif token.type in {"th_close", "td_close"}:
                spans = self._inline_tokens_to_spans(current_inline)
                current_cells.append(TableCell(spans=spans))
                in_cell = False
            elif token.type == "tr_close":
                rows.append(TableRow(cells=current_cells, header=header_mode))

            index += 1

        if index < len(tokens) and tokens[index].type == "table_close":
            index += 1
        return TableBlock(rows=rows), index

    def _parse_inline(self, children: list[Token]) -> list[InlineSpan]:
        spans: list[InlineSpan] = []
        bold = False
        italic = False

        for child in children:
            token_type = child.type
            if token_type == "text":
                spans.append(InlineSpan(text=child.content, bold=bold, italic=italic))
            elif token_type == "code_inline":
                spans.append(InlineSpan(text=child.content, code=True))
            elif token_type == "strong_open":
                bold = True
            elif token_type == "strong_close":
                bold = False
            elif token_type == "em_open":
                italic = True
            elif token_type == "em_close":
                italic = False
            elif token_type in {"softbreak", "hardbreak"}:
                spans.append(InlineSpan(text="\n", bold=bold, italic=italic))
            elif token_type == "image":
                alt_text = child.content or "image"
                spans.append(
                    InlineSpan(text=f"[Image: {alt_text}]", bold=bold, italic=italic)
                )
            elif child.content:
                spans.append(InlineSpan(text=child.content, bold=bold, italic=italic))

        return self._merge_adjacent_spans(spans)

    def _inline_tokens_to_spans(self, inline_tokens: list[Token]) -> list[InlineSpan]:
        spans: list[InlineSpan] = []
        for inline_token in inline_tokens:
            spans.extend(self._parse_inline(inline_token.children or []))
        return self._merge_adjacent_spans(spans)

    def _apply_block_conventions(self, blocks: list[Block]) -> list[Block]:
        result: list[Block] = []
        index = 0

        while index < len(blocks):
            current = blocks[index]

            if (
                isinstance(current, ParagraphBlock)
                and self._is_table_caption(current)
                and index + 1 < len(blocks)
                and isinstance(blocks[index + 1], TableBlock)
            ):
                table_block = blocks[index + 1]
                table_block.caption = current
                result.append(table_block)
                index += 2
                continue

            if isinstance(current, ImageBlock):
                next_block = blocks[index + 1] if index + 1 < len(blocks) else None
                next_next_block = blocks[index + 2] if index + 2 < len(blocks) else None
                if isinstance(next_block, ParagraphBlock) and isinstance(
                    next_next_block, ParagraphBlock
                ):
                    if self._is_figure_caption(
                        next_next_block
                    ) and not self._is_figure_caption(next_block):
                        current.explanatory = next_block
                        current.caption = next_next_block
                        result.append(current)
                        index += 3
                        continue
                if isinstance(next_block, ParagraphBlock) and self._is_figure_caption(
                    next_block
                ):
                    current.caption = next_block
                    result.append(current)
                    index += 2
                    continue

            result.append(current)
            index += 1

        return result

    @staticmethod
    def _merge_adjacent_spans(spans: list[InlineSpan]) -> list[InlineSpan]:
        merged: list[InlineSpan] = []
        for span in spans:
            if not span.text:
                continue
            if merged and (merged[-1].bold, merged[-1].italic, merged[-1].code) == (
                span.bold,
                span.italic,
                span.code,
            ):
                merged[-1].text += span.text
            else:
                merged.append(span)
        return merged

    @staticmethod
    def _spans_to_text(spans: list[InlineSpan]) -> str:
        return "".join(span.text for span in spans)

    @staticmethod
    def _is_table_caption(block: ParagraphBlock) -> bool:
        return bool(TABLE_CAPTION_RE.match(block.text.strip()))

    @staticmethod
    def _is_figure_caption(block: ParagraphBlock) -> bool:
        return bool(FIGURE_CAPTION_RE.match(block.text.strip()))
