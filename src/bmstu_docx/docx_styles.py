from __future__ import annotations

from docx.document import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Mm, Pt

from .config import DocumentConfig

BODY_STYLE = "BmstuBody"
BLOCKQUOTE_STYLE = "BmstuBlockQuote"
HEADING1_STYLE = "BmstuHeading1"
HEADING2_STYLE = "BmstuHeading2"
HEADING3_STYLE = "BmstuHeading3"
STRUCTURAL_HEADING_STYLE = "BmstuStructuralHeading"
CODE_STYLE = "BmstuCode"
CAPTION_STYLE = "BmstuCaption"
FIGURE_TEXT_STYLE = "BmstuFigureText"
TABLE_TEXT_STYLE = "BmstuTableText"


def apply_document_styles(document: Document, config: DocumentConfig) -> None:
    section = document.sections[0]
    section.page_width = Mm(config.page_width_mm)
    section.page_height = Mm(config.page_height_mm)
    section.left_margin = Cm(config.margin_left_cm)
    section.right_margin = Cm(config.margin_right_cm)
    section.top_margin = Cm(config.margin_top_cm)
    section.bottom_margin = Cm(config.margin_bottom_cm)
    section.different_first_page_header_footer = True

    _configure_normal_style(document, config)
    _configure_styles(document, config)
    _configure_footer(section.footer, config)


def apply_run_font(run, font_name: str, font_size_pt: int) -> None:
    run.font.name = font_name
    run.font.size = Pt(font_size_pt)
    r_pr = run._element.get_or_add_rPr()
    r_fonts = r_pr.rFonts
    if r_fonts is None:
        r_fonts = OxmlElement("w:rFonts")
        r_pr.append(r_fonts)
    for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
        r_fonts.set(qn(f"w:{attr}"), font_name)


def _configure_normal_style(document: Document, config: DocumentConfig) -> None:
    normal = document.styles["Normal"]
    normal.font.name = config.body_font_name
    normal.font.size = Pt(config.body_font_size_pt)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.first_line_indent = Cm(config.body_first_line_indent_cm)
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    normal.paragraph_format.line_spacing = config.body_line_spacing
    normal.paragraph_format.space_before = Pt(config.body_space_before_pt)
    normal.paragraph_format.space_after = Pt(config.body_space_after_pt)
    r_pr = normal._element.get_or_add_rPr()
    r_fonts = r_pr.rFonts
    if r_fonts is None:
        r_fonts = OxmlElement("w:rFonts")
        r_pr.append(r_fonts)
    for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
        r_fonts.set(qn(f"w:{attr}"), config.body_font_name)


def _configure_styles(document: Document, config: DocumentConfig) -> None:
    styles = document.styles
    _ensure_paragraph_style(styles, BODY_STYLE, "Normal")
    _ensure_paragraph_style(styles, BLOCKQUOTE_STYLE, BODY_STYLE)
    _ensure_paragraph_style(styles, HEADING1_STYLE, BODY_STYLE)
    _ensure_paragraph_style(styles, HEADING2_STYLE, BODY_STYLE)
    _ensure_paragraph_style(styles, HEADING3_STYLE, BODY_STYLE)
    _ensure_paragraph_style(styles, STRUCTURAL_HEADING_STYLE, BODY_STYLE)
    _ensure_paragraph_style(styles, CODE_STYLE, BODY_STYLE)
    _ensure_paragraph_style(styles, CAPTION_STYLE, BODY_STYLE)
    _ensure_paragraph_style(styles, FIGURE_TEXT_STYLE, BODY_STYLE)
    _ensure_paragraph_style(styles, TABLE_TEXT_STYLE, BODY_STYLE)

    body = styles[BODY_STYLE]
    body.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    body.paragraph_format.first_line_indent = Cm(config.body_first_line_indent_cm)
    body.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    body.paragraph_format.line_spacing = config.body_line_spacing
    body.paragraph_format.space_before = Pt(config.body_space_before_pt)
    body.paragraph_format.space_after = Pt(config.body_space_after_pt)

    blockquote = styles[BLOCKQUOTE_STYLE]
    blockquote.paragraph_format.left_indent = Cm(config.blockquote_left_indent_cm)
    blockquote.paragraph_format.first_line_indent = Cm(0)

    heading1 = styles[HEADING1_STYLE]
    heading1.font.bold = True
    heading1.font.size = Pt(config.heading1_size_pt)
    heading1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    heading1.paragraph_format.first_line_indent = Cm(0)
    heading1.paragraph_format.space_before = Pt(12)
    heading1.paragraph_format.space_after = Pt(12)

    heading2 = styles[HEADING2_STYLE]
    heading2.font.bold = True
    heading2.font.size = Pt(config.heading2_size_pt)
    heading2.paragraph_format.first_line_indent = Cm(0)
    heading2.paragraph_format.space_before = Pt(12)
    heading2.paragraph_format.space_after = Pt(6)

    heading3 = styles[HEADING3_STYLE]
    heading3.font.bold = True
    heading3.font.size = Pt(config.heading3_size_pt)
    heading3.paragraph_format.first_line_indent = Cm(0)
    heading3.paragraph_format.space_before = Pt(6)
    heading3.paragraph_format.space_after = Pt(6)

    structural = styles[STRUCTURAL_HEADING_STYLE]
    structural.font.bold = True
    structural.font.size = Pt(config.heading1_size_pt)
    structural.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    structural.paragraph_format.first_line_indent = Cm(0)
    structural.paragraph_format.space_before = Pt(18)
    structural.paragraph_format.space_after = Pt(12)

    code = styles[CODE_STYLE]
    code.font.name = config.code_font_name
    code.font.size = Pt(config.code_font_size_pt)
    code.paragraph_format.first_line_indent = Cm(0)
    code.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    code.paragraph_format.space_before = Pt(0)
    code.paragraph_format.space_after = Pt(0)

    caption = styles[CAPTION_STYLE]
    caption.font.size = Pt(config.body_font_size_pt)
    caption.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption.paragraph_format.first_line_indent = Cm(0)
    caption.paragraph_format.space_before = Pt(config.caption_space_before_pt)
    caption.paragraph_format.space_after = Pt(config.caption_space_after_pt)

    figure_text = styles[FIGURE_TEXT_STYLE]
    figure_text.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    figure_text.paragraph_format.first_line_indent = Cm(0)
    figure_text.paragraph_format.space_before = Pt(0)
    figure_text.paragraph_format.space_after = Pt(6)

    table_text = styles[TABLE_TEXT_STYLE]
    table_text.font.size = Pt(config.table_font_size_pt)
    table_text.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    table_text.paragraph_format.first_line_indent = Cm(0)
    table_text.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    table_text.paragraph_format.space_before = Pt(0)
    table_text.paragraph_format.space_after = Pt(0)


def _ensure_paragraph_style(styles, name: str, base_style_name: str) -> None:
    if name in styles:
        return
    style = styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
    style.base_style = styles[base_style_name]


def _configure_footer(footer, config: DocumentConfig) -> None:
    paragraph = footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    apply_run_font(run, config.body_font_name, config.body_font_size_pt)

    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")

    run._r.append(begin)
    run._r.append(instr)
    run._r.append(end)
