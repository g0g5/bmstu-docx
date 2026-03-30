from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentConfig:
    page_width_mm: float = 210.0
    page_height_mm: float = 297.0
    margin_left_cm: float = 3.0
    margin_right_cm: float = 1.0
    margin_top_cm: float = 2.0
    margin_bottom_cm: float = 2.0
    body_font_name: str = "Times New Roman"
    body_font_size_pt: int = 14
    code_font_name: str = "Consolas"
    fallback_code_font_name: str = "Courier New"
    code_font_size_pt: int = 11
    table_font_size_pt: int = 12
    body_first_line_indent_cm: float = 1.25
    body_line_spacing: float = 1.5
    body_space_before_pt: int = 0
    body_space_after_pt: int = 0
    heading1_size_pt: int = 16
    heading2_size_pt: int = 14
    heading3_size_pt: int = 14
    caption_space_before_pt: int = 0
    caption_space_after_pt: int = 6
    blockquote_left_indent_cm: float = 1.0
    image_max_width_cm: float = 15.5


DEFAULT_CONFIG = DocumentConfig()
