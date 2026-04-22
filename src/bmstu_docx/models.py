from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class InlineSpan:
    text: str
    bold: bool = False
    italic: bool = False


@dataclass(slots=True)
class Block:
    pass


@dataclass(slots=True)
class ParagraphBlock(Block):
    spans: list[InlineSpan]
    kind: str = "body"

    @property
    def text(self) -> str:
        return "".join(span.text for span in self.spans)


@dataclass(slots=True)
class HeadingBlock(Block):
    level: int
    spans: list[InlineSpan]
    structural: bool = False

    @property
    def text(self) -> str:
        return "".join(span.text for span in self.spans)


@dataclass(slots=True)
class CodeBlock(Block):
    code: str
    info: str = ""


@dataclass(slots=True)
class ListItem:
    blocks: list[Block] = field(default_factory=list)


@dataclass(slots=True)
class ListBlock(Block):
    ordered: bool
    items: list[ListItem] = field(default_factory=list)


@dataclass(slots=True)
class TableCell:
    spans: list[InlineSpan]


@dataclass(slots=True)
class TableRow:
    cells: list[TableCell]
    header: bool = False


@dataclass(slots=True)
class TableBlock(Block):
    rows: list[TableRow]
    caption: ParagraphBlock | None = None


@dataclass(slots=True)
class ImageBlock(Block):
    path: str
    alt_text: str = ""
    caption: ParagraphBlock | None = None
    explanatory: ParagraphBlock | None = None
