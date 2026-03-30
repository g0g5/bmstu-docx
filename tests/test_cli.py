from __future__ import annotations

from pathlib import Path

from bmstu_docx.cli import build_output_path, main


def test_build_output_path_uses_docx_suffix() -> None:
    assert build_output_path("report.md") == Path("report.docx")


def test_cli_creates_output_file(tmp_path, capsys) -> None:
    input_file = tmp_path / "input.md"
    output_file = tmp_path / "result.docx"
    input_file.write_text("# Heading\n\nSimple paragraph.", encoding="utf-8")

    exit_code = main([str(input_file), "-o", str(output_file)])

    assert exit_code == 0
    assert output_file.exists()
    assert f"Created {output_file}" in capsys.readouterr().out
