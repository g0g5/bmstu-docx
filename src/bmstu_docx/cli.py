from __future__ import annotations

import argparse
from pathlib import Path

from .converter import convert_file


def build_output_path(
    input_path: str | Path, output_path: str | Path | None = None
) -> Path:
    input_file = Path(input_path)
    if output_path is not None:
        return Path(output_path)
    return input_file.with_suffix(".docx")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert Markdown to BMSTU-style DOCX."
    )
    parser.add_argument("input_markdown", help="Path to the input Markdown file")
    parser.add_argument("-o", "--output", help="Path to the output DOCX file")
    args = parser.parse_args(argv)

    input_path = Path(args.input_markdown)
    if not input_path.exists() or not input_path.is_file():
        parser.error(f"input file does not exist: {input_path}")

    output_path = build_output_path(input_path, args.output)
    convert_file(input_path, output_path)
    print(f"Created {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
