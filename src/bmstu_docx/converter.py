from __future__ import annotations

from pathlib import Path

from .config import DEFAULT_CONFIG, DocumentConfig
from .docx_renderer import DocxRenderer
from .markdown_parser import MarkdownParser


def convert_markdown_text(
    markdown_text: str,
    output_path: str | Path,
    *,
    base_path: str | Path | None = None,
    config: DocumentConfig = DEFAULT_CONFIG,
) -> Path:
    parser = MarkdownParser()
    renderer = DocxRenderer(config=config)
    blocks = parser.parse(markdown_text, base_path=base_path)
    return renderer.save(blocks, output_path)


def convert_file(
    input_path: str | Path,
    output_path: str | Path,
    *,
    config: DocumentConfig = DEFAULT_CONFIG,
) -> Path:
    input_file = Path(input_path)
    markdown_text = input_file.read_text(encoding="utf-8")
    return convert_markdown_text(
        markdown_text, output_path, base_path=input_file.parent, config=config
    )
