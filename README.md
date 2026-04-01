# bmstu-docx

`bmstu-docx` converts Markdown reports into BMSTU-style `.docx` documents.

The project parses a focused subset of Markdown and renders a Word document with page setup, fonts, paragraph styles, captions, and numbering conventions that match typical BMSTU report formatting.

## Features

- Converts Markdown files to `.docx` from the command line.
- Applies BMSTU-oriented page settings: A4, `3 cm` left margin, `1 cm` right margin, `2 cm` top/bottom margins.
- Uses `Times New Roman` 14 pt for body text and `Consolas` for code.
- Supports headings, paragraphs, blockquotes, ordered and unordered lists, fenced code blocks, tables, inline bold/italic/code, and images.
- Detects table captions like `Table 1 - ...` / `Таблица 1 - ...` and figure captions like `Figure 1 - ...` / `Рисунок 1 - ...`.
- Treats structural headings such as `ВВЕДЕНИЕ`, `ЗАКЛЮЧЕНИЕ`, `INTRODUCTION`, and `CONCLUSION` specially.
- Adds a centered page number field in the footer.

## Requirements

- Python `3.12+`
- Dependencies from `pyproject.toml`:
  - `markdown-it-py`
  - `python-docx`

## Installation

This project uses `uv` for dependency and environment management.

### Install as a local CLI tool

After cloning the repository, install it as a local command-line program:

```bash
uv tool install -e .
```

Then you can run:

```bash
bmstu-docx examples/basic.md
```

### Development setup

For development, create and sync the project environment with:

```bash
uv sync
```

Then run commands inside the managed environment, for example:

```bash
uv run bmstu-docx examples/basic.md
uv run pytest
```

## CLI usage

```bash
bmstu-docx input.md
bmstu-docx input.md -o output/report.docx
```

Arguments:

- `input_markdown`: path to the source Markdown file.
- `-o`, `--output`: optional output path. If omitted, the output file uses the input name with a `.docx` suffix.

Example:

```bash
bmstu-docx examples/full.md -o out/full.docx
```

## Python API

```python
from bmstu_docx import convert_file, convert_markdown_text

convert_file("examples/basic.md", "out/basic.docx")

convert_markdown_text(
    "# ВВЕДЕНИЕ\n\nТекст отчета.",
    "out/from-string.docx",
)
```

## Supported Markdown patterns

The parser is intentionally focused on report-like documents. The current implementation supports:

- ATX headings (`#`, `##`, `###`)
- regular paragraphs and blockquotes
- unordered and ordered lists, including nested lists
- fenced code blocks and inline code
- GitHub-style tables
- standalone images in paragraphs
- table captions immediately before a table
- figure explanatory text and captions immediately after an image

Caption detection expects these shapes:

```text
Table 1 - Caption text
Таблица 1 - Подпись
Figure 1 - Caption text
Рисунок 1 - Подпись
```

## Examples

Sample Markdown files are available in `examples/`:

- `examples/basic.md` - headings and body text
- `examples/lists-code.md` - lists and code blocks
- `examples/table-image.md` - tables, images, explanatory text, captions
- `examples/full.md` - combined example

## Development

Run tests:

```bash
uv run pytest
```

The current test suite covers:

- CLI output path behavior
- caption and structural heading parsing
- basic DOCX rendering and page setup

## Project structure

- `src/bmstu_docx/markdown_parser.py` - Markdown token parsing into internal blocks
- `src/bmstu_docx/docx_renderer.py` - DOCX rendering with `python-docx`
- `src/bmstu_docx/docx_styles.py` - document styles, margins, footer page number
- `src/bmstu_docx/converter.py` - high-level conversion helpers
- `src/bmstu_docx/cli.py` - command-line entry point

## Limitations

- The parser handles a practical subset of Markdown rather than full CommonMark coverage.
- Image embedding expects local file paths that are valid relative to the input Markdown file.
- Only a fixed BMSTU-oriented style configuration is exposed through the current CLI.
