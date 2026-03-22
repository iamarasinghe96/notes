"""
Albury Wodonga Health – PROGRESS NOTES (FAW0004)
Fillable PDF generator, mobile-optimised.

Usage:
    python3 generate_progress_notes.py
Output:
    progress_notes_FAW0004.pdf
"""

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

# ── Dimensions ────────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4          # 595.28 x 841.89 pt
MARGIN_L   = 18 * mm         # left margin (inside barcode area)
MARGIN_R   = 22 * mm         # right margin (inside green tab)
MARGIN_T   = 8  * mm
MARGIN_B   = 8  * mm

GREEN      = HexColor("#5BBD2E")   # AWH green from the tab
LIGHT_GREY = HexColor("#E8ECF0")   # header fill
LINE_GREY  = HexColor("#AAAAAA")   # table grid lines
TEXT_BLACK = colors.black

# ── Helpers ───────────────────────────────────────────────────────────────────

def draw_awh_logo(c: canvas.Canvas, cx: float, cy: float, radius: float = 9 * mm):
    """Approximate the Albury Wodonga Health triple-ring logo."""
    lw = radius * 0.22
    c.setLineWidth(lw)
    c.setStrokeColor(TEXT_BLACK)

    # ring centres arranged in an equilateral triangle
    import math
    r_sep = radius * 0.72
    centres = [
        (cx,              cy + r_sep * 0.65),          # top
        (cx - r_sep * 0.58, cy - r_sep * 0.32),        # bottom-left
        (cx + r_sep * 0.58, cy - r_sep * 0.32),        # bottom-right
    ]
    for (rx, ry) in centres:
        c.circle(rx, ry, radius * 0.62, stroke=1, fill=0)


def textfield(c: canvas.Canvas, name: str, x, y, w, h,
              fontsize=9, tooltip=""):
    """Add a tappable AcroForm text field."""
    c.acroForm.textfield(
        name=name,
        tooltip=tooltip,
        x=x, y=y, width=w, height=h,
        fontSize=fontsize,
        borderStyle="underlined",
        borderColor=colors.transparent,
        fillColor=HexColor("#F5F8FF"),
        textColor=TEXT_BLACK,
        forceBorder=True,
    )


# ── Main builder ──────────────────────────────────────────────────────────────

def build_pdf(output_path: str = "progress_notes_FAW0004.pdf"):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle("Progress Notes – FAW0004")
    c.setAuthor("Albury Wodonga Health")
    c.setSubject("Fillable Progress Notes")

    _draw_page(c)

    c.save()
    data = buf.getvalue()
    with open(output_path, "wb") as f:
        f.write(data)
    print(f"✓  Saved → {output_path}  ({len(data)//1024} KB)")


def _draw_page(c: canvas.Canvas):
    W, H = PAGE_W, PAGE_H

    # ── Green right-side tab ──────────────────────────────────────────────────
    tab_w = 16 * mm
    tab_x = W - tab_w
    c.setFillColor(GREEN)
    c.rect(tab_x, 0, tab_w, H, stroke=0, fill=1)

    # "PROGRESS NOTES" rotated text on tab
    c.saveState()
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 8.5)
    c.translate(tab_x + tab_w * 0.5, H * 0.5 + 10 * mm)
    c.rotate(270)
    c.drawCentredString(0, 0, "PROGRESS NOTES")
    c.restoreState()

    # "MR4" on tab
    c.saveState()
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.translate(tab_x + tab_w * 0.5, 22 * mm)
    c.rotate(270)
    c.drawCentredString(0, 0, "MR4")
    c.restoreState()

    # ── Left barcode strip ────────────────────────────────────────────────────
    bc_strip_w = 15 * mm
    bc_x_centre = bc_strip_w * 0.5

    # Code-128 barcode (vertical)
    bc = code128.Code128(
        "FAW0004",
        barHeight=38 * mm,
        barWidth=0.9,
        humanReadable=False,
        quiet=False,
    )
    bc_w = bc.width
    bc_h = bc.height

    c.saveState()
    # Position barcode mid-height of the header region, rotated 90°
    header_h = 55 * mm
    header_top = H - MARGIN_T
    header_mid = header_top - header_h * 0.5

    c.translate(bc_x_centre, header_mid)
    c.rotate(90)
    bc.drawOn(c, -bc_h * 0.5, -bc_w * 0.5)
    c.restoreState()

    # "FAW0004" label below barcode (rotated)
    c.saveState()
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(TEXT_BLACK)
    c.translate(bc_x_centre, header_mid - 22 * mm)
    c.rotate(90)
    c.drawCentredString(0, 0, "FAW0004")
    c.restoreState()

    # ── Usable area ───────────────────────────────────────────────────────────
    # Content sits between the barcode strip and the green tab
    content_x = bc_strip_w + 1 * mm
    content_w = tab_x - content_x - 2 * mm
    content_top = H - MARGIN_T

    # ── Header block ──────────────────────────────────────────────────────────
    header_h = 55 * mm
    header_y = content_top - header_h

    # Outer header border
    c.setStrokeColor(TEXT_BLACK)
    c.setLineWidth(0.8)
    c.rect(content_x, header_y, content_w, header_h, stroke=1, fill=0)

    # Vertical divider splitting logo+title | patient-id box
    divider_x = content_x + content_w * 0.42
    c.line(divider_x, header_y, divider_x, content_top)

    # ─ Left panel: logo + title ───────────────────────────────────────────────
    logo_cx = content_x + (divider_x - content_x) * 0.35
    logo_cy = content_top - 14 * mm
    draw_awh_logo(c, logo_cx, logo_cy, radius=8 * mm)

    # Organisation name
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(TEXT_BLACK)
    txt_x = logo_cx + 11 * mm
    c.drawString(txt_x, content_top - 9 * mm,  "Albury")
    c.drawString(txt_x, content_top - 14 * mm, "Wodonga")
    c.drawString(txt_x, content_top - 19 * mm, "Health")

    # "PROGRESS NOTES" title
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(
        content_x + (divider_x - content_x) * 0.5,
        header_y + 8 * mm,
        "PROGRESS NOTES"
    )

    # ─ Right panel: patient ID ─────────────────────────────────────────────────
    pid_x   = divider_x + 3 * mm
    pid_w   = content_x + content_w - divider_x - 4 * mm
    pid_top = content_top - 3 * mm

    c.setFont("Helvetica", 7)
    c.drawString(pid_x, pid_top - 4 * mm, "(Affix Patient Identification Label here)")

    # Dotted field rows
    field_labels = ["UR No:", "Surname:", "Given Names:", "Date of Birth:"]
    field_names  = ["ur_no", "surname", "given_names", "dob"]
    row_h = 7.5 * mm
    for i, (label, fname) in enumerate(zip(field_labels, field_names)):
        fy = pid_top - 11 * mm - i * row_h
        c.setFont("Helvetica", 7.5)
        c.drawString(pid_x, fy, label)
        lbl_w = c.stringWidth(label, "Helvetica", 7.5)
        field_x = pid_x + lbl_w + 1 * mm
        field_w = pid_w - lbl_w - 2 * mm

        if fname == "dob":
            # Split DOB and Sex on one row
            dob_w = field_w * 0.58
            textfield(c, "dob", field_x, fy - 1.5 * mm,
                      dob_w, row_h - 1 * mm, fontsize=8, tooltip="Date of Birth")
            sex_label_x = field_x + dob_w + 1 * mm
            c.drawString(sex_label_x, fy, "Sex:")
            sex_lbl_w = c.stringWidth("Sex:", "Helvetica", 7.5)
            textfield(c, "sex", sex_label_x + sex_lbl_w + 1 * mm, fy - 1.5 * mm,
                      pid_w - lbl_w - dob_w - sex_lbl_w - 5 * mm,
                      row_h - 1 * mm, fontsize=8, tooltip="Sex")
        else:
            textfield(c, fname, field_x, fy - 1.5 * mm,
                      field_w, row_h - 1 * mm, fontsize=8, tooltip=label.rstrip(":"))

    # ── Sub-header row (table column headings) ────────────────────────────────
    subhdr_h = 8 * mm
    subhdr_y = header_y - subhdr_h

    c.setFillColor(colors.white)
    c.setStrokeColor(TEXT_BLACK)
    c.setLineWidth(0.8)
    c.rect(content_x, subhdr_y, content_w, subhdr_h, stroke=1, fill=1)

    # Column widths
    date_col_w = 26 * mm
    note_col_x = content_x + date_col_w
    note_col_w = content_w - date_col_w

    c.line(note_col_x, subhdr_y, note_col_x, subhdr_y + subhdr_h)

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(TEXT_BLACK)
    c.drawCentredString(content_x + date_col_w * 0.5,
                        subhdr_y + 2 * mm, "Date/Time")
    c.drawCentredString(note_col_x + note_col_w * 0.5,
                        subhdr_y + 2 * mm,
                        "Please sign each entry and print surname and designation")

    # ── Table rows (fillable lines) ────────────────────────────────────────────
    table_top = subhdr_y
    table_bottom = MARGIN_B + 12 * mm   # leave room for footer
    table_h = table_top - table_bottom

    # Outer table border
    c.setStrokeColor(LINE_GREY)
    c.setLineWidth(0.5)
    c.rect(content_x, table_bottom, content_w, table_h, stroke=1, fill=0)
    # Vertical column divider through table
    c.setStrokeColor(LINE_GREY)
    c.line(note_col_x, table_bottom, note_col_x, table_top)

    row_h_table = 7.2 * mm
    num_rows = int(table_h / row_h_table)
    field_pad = 1.0 * mm

    for i in range(num_rows):
        ry = table_top - (i + 1) * row_h_table

        # Horizontal row line
        c.setStrokeColor(LINE_GREY)
        c.setLineWidth(0.4)
        c.line(content_x, ry, content_x + content_w, ry)

        # Date/Time field
        textfield(
            c,
            name=f"dt_{i}",
            x=content_x + field_pad,
            y=ry + field_pad,
            w=date_col_w - field_pad * 2,
            h=row_h_table - field_pad * 2,
            fontsize=8,
            tooltip=f"Date/Time row {i+1}",
        )

        # Notes field
        textfield(
            c,
            name=f"note_{i}",
            x=note_col_x + field_pad,
            y=ry + field_pad,
            w=note_col_w - field_pad * 2,
            h=row_h_table - field_pad * 2,
            fontsize=8,
            tooltip=f"Notes row {i+1}",
        )

    # ── Footer ────────────────────────────────────────────────────────────────
    c.setFont("Helvetica", 6.5)
    c.setFillColor(TEXT_BLACK)
    footer_y = MARGIN_B + 4 * mm
    c.drawString(content_x, footer_y, "Version 1.0   March 2021")
    c.drawString(content_x + 40 * mm, footer_y, "Store Order No.: 90083")
    c.setFont("Helvetica-Bold", 7)
    c.drawRightString(tab_x - 3 * mm, footer_y, "Please turn over")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    build_pdf("progress_notes_FAW0004.pdf")
