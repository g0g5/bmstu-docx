from __future__ import annotations

from pathlib import Path

from bmstu_docx.markdown_parser import MarkdownParser
from bmstu_docx.models import HeadingBlock, ImageBlock, ParagraphBlock, TableBlock


def test_parser_attaches_table_caption() -> None:
    parser = MarkdownParser()
    blocks = parser.parse("Table 1 - Caption\n\n| A | B |\n| - | - |\n| 1 | 2 |\n")

    assert len(blocks) == 1
    assert isinstance(blocks[0], TableBlock)
    assert blocks[0].caption is not None
    assert blocks[0].caption.text == "Table 1 - Caption"


def test_parser_attaches_figure_caption_and_explanatory_text(tmp_path: Path) -> None:
    image_path = tmp_path / "img.png"
    image_path.write_bytes(b"fake")
    parser = MarkdownParser()
    markdown = "![alt](img.png)\n\nOrdinary explanation.\n\nFigure 1 - Caption\n"

    blocks = parser.parse(markdown, base_path=tmp_path)

    assert len(blocks) == 1
    assert isinstance(blocks[0], ImageBlock)
    assert blocks[0].caption is not None
    assert blocks[0].caption.text == "Figure 1 - Caption"
    assert blocks[0].explanatory is not None
    assert blocks[0].explanatory.text == "Ordinary explanation."


def test_parser_marks_structural_heading() -> None:
    parser = MarkdownParser()
    blocks = parser.parse("# ВВЕДЕНИЕ\n\nТекст.\n")

    assert isinstance(blocks[0], HeadingBlock)
    assert blocks[0].structural is True
    assert isinstance(blocks[1], ParagraphBlock)
