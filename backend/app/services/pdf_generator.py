"""Render a professional A4 invoice PDF with ReportLab.

The renderer is intentionally decoupled from the DB: it takes a plain context
dict so it can serve both saved invoices and stateless live previews.
"""

import base64
import re
from decimal import Decimal
from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Palette
INK = colors.HexColor("#1a2233")
MUTED = colors.HexColor("#6b7280")
ACCENT = colors.HexColor("#2563eb")
LIGHT = colors.HexColor("#f1f5f9")
BORDER = colors.HexColor("#e2e8f0")
ZEBRA = colors.HexColor("#f8fafc")

CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "INR": "₹",
    "JPY": "¥",
    "AUD": "A$",
    "CAD": "C$",
    "AED": "AED ",
    "SGD": "S$",
}


def _money(amount: Decimal | float | int | str, currency: str) -> str:
    value = Decimal(str(amount or 0)).quantize(Decimal("0.01"))
    symbol = CURRENCY_SYMBOLS.get((currency or "").upper(), f"{currency} ")
    # Thousands separators, two decimals.
    return f"{symbol}{value:,.2f}"


def _qty(value: Decimal | float | int | str) -> str:
    d = Decimal(str(value or 0))
    if d == d.to_integral_value():
        return f"{int(d)}"
    return f"{d.normalize()}"


def _logo_flowable(data_url: str, max_w: float, max_h: float) -> Image | None:
    """Decode a base64 data URL into a sized ReportLab Image, preserving aspect."""
    if not data_url:
        return None
    try:
        match = re.match(r"^data:(?P<mime>[^;]+);base64,(?P<data>.+)$", data_url.strip(), re.DOTALL)
        raw = base64.b64decode(match.group("data")) if match else base64.b64decode(data_url)
        buf = BytesIO(raw)
        img = Image(buf)
        iw, ih = img.imageWidth, img.imageHeight
        if not iw or not ih:
            return None
        scale = min(max_w / iw, max_h / ih)
        img.drawWidth = iw * scale
        img.drawHeight = ih * scale
        return img
    except Exception:
        return None


def render_invoice_pdf(ctx: dict[str, Any]) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=f"Invoice {ctx.get('invoice_number', '')}",
    )

    base = getSampleStyleSheet()
    styles = {
        "biz": ParagraphStyle("biz", parent=base["Normal"], fontName="Helvetica-Bold",
                              fontSize=15, textColor=INK, leading=18),
        "biz_meta": ParagraphStyle("biz_meta", parent=base["Normal"], fontSize=8.5,
                                   textColor=MUTED, leading=12),
        "title": ParagraphStyle("title", parent=base["Normal"], fontName="Helvetica-Bold",
                                fontSize=26, textColor=ACCENT, alignment=TA_RIGHT, leading=28),
        "meta_label": ParagraphStyle("meta_label", parent=base["Normal"], fontSize=8,
                                     textColor=MUTED, alignment=TA_RIGHT, leading=12),
        "meta_value": ParagraphStyle("meta_value", parent=base["Normal"], fontName="Helvetica-Bold",
                                     fontSize=9.5, textColor=INK, alignment=TA_RIGHT, leading=12),
        "section": ParagraphStyle("section", parent=base["Normal"], fontName="Helvetica-Bold",
                                 fontSize=8, textColor=MUTED, leading=12, spaceAfter=2),
        "party_name": ParagraphStyle("party_name", parent=base["Normal"], fontName="Helvetica-Bold",
                                     fontSize=11, textColor=INK, leading=14),
        "party_meta": ParagraphStyle("party_meta", parent=base["Normal"], fontSize=9,
                                     textColor=MUTED, leading=13),
        "cell": ParagraphStyle("cell", parent=base["Normal"], fontSize=9, textColor=INK, leading=12),
        "cell_r": ParagraphStyle("cell_r", parent=base["Normal"], fontSize=9, textColor=INK,
                                leading=12, alignment=TA_RIGHT),
        "th": ParagraphStyle("th", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=8.5,
                            textColor=colors.white, leading=11),
        "th_r": ParagraphStyle("th_r", parent=base["Normal"], fontName="Helvetica-Bold",
                              fontSize=8.5, textColor=colors.white, leading=11, alignment=TA_RIGHT),
        "notes_h": ParagraphStyle("notes_h", parent=base["Normal"], fontName="Helvetica-Bold",
                                 fontSize=8, textColor=MUTED, leading=12),
        "notes": ParagraphStyle("notes", parent=base["Normal"], fontSize=9, textColor=INK,
                              leading=13),
        "grand": ParagraphStyle("grand", parent=base["Normal"], fontName="Helvetica-Bold",
                              fontSize=12, textColor=colors.white, alignment=TA_RIGHT, leading=14),
        "grand_l": ParagraphStyle("grand_l", parent=base["Normal"], fontName="Helvetica-Bold",
                                fontSize=10, textColor=colors.white, leading=14),
    }

    currency = ctx.get("currency", "USD")
    content_w = doc.width
    story: list[Any] = []

    def esc(text: Any) -> str:
        s = "" if text is None else str(text)
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")

    # ---- Header: logo + business identity (left) | INVOICE + meta (right) ----
    logo = _logo_flowable(ctx.get("logo_data_url"), max_w=45 * mm, max_h=24 * mm)

    left_bits: list[Any] = []
    if logo is not None:
        left_bits.append(logo)
        left_bits.append(Spacer(1, 6))
    left_bits.append(Paragraph(esc(ctx.get("sender_name") or "Your Business"), styles["biz"]))
    biz_meta = "<br/>".join(
        esc(x) for x in [ctx.get("sender_address"), ctx.get("sender_email"), ctx.get("sender_phone")] if x
    )
    if biz_meta:
        left_bits.append(Spacer(1, 3))
        left_bits.append(Paragraph(biz_meta, styles["biz_meta"]))

    meta_rows = [
        [Paragraph("Invoice No.", styles["meta_label"]),
         Paragraph(esc(ctx.get("invoice_number")), styles["meta_value"])],
        [Paragraph("Issue Date", styles["meta_label"]),
         Paragraph(esc(ctx.get("issue_date")), styles["meta_value"])],
        [Paragraph("Due Date", styles["meta_label"]),
         Paragraph(esc(ctx.get("due_date")), styles["meta_value"])],
    ]
    meta_table = Table(meta_rows, colWidths=[28 * mm, 32 * mm])
    meta_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    right_bits = [Paragraph("INVOICE", styles["title"]), Spacer(1, 8), meta_table]

    header = Table([[left_bits, right_bits]], colWidths=[content_w * 0.55, content_w * 0.45])
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(header)
    story.append(Spacer(1, 10))
    story.append(Table([[""]], colWidths=[content_w],
                       style=TableStyle([("LINEBELOW", (0, 0), (-1, -1), 1.4, ACCENT)])))
    story.append(Spacer(1, 12))

    # ---- Bill To ----
    bill_bits = [Paragraph("BILL TO", styles["section"]),
                 Paragraph(esc(ctx.get("client_name") or "—"), styles["party_name"])]
    client_meta = "<br/>".join(
        esc(x) for x in [ctx.get("client_address"), ctx.get("client_email"), ctx.get("client_phone")] if x
    )
    if client_meta:
        bill_bits.append(Spacer(1, 2))
        bill_bits.append(Paragraph(client_meta, styles["party_meta"]))
    story.append(Table([[bill_bits]], colWidths=[content_w],
                       style=TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0)])))
    story.append(Spacer(1, 14))

    # ---- Line items table ----
    col_w = [content_w * 0.50, content_w * 0.13, content_w * 0.185, content_w * 0.185]
    data = [[
        Paragraph("DESCRIPTION", styles["th"]),
        Paragraph("QTY", styles["th_r"]),
        Paragraph("UNIT PRICE", styles["th_r"]),
        Paragraph("AMOUNT", styles["th_r"]),
    ]]
    for item in ctx.get("line_items", []):
        data.append([
            Paragraph(esc(item.get("description")), styles["cell"]),
            Paragraph(_qty(item.get("quantity")), styles["cell_r"]),
            Paragraph(_money(item.get("unit_price"), currency), styles["cell_r"]),
            Paragraph(_money(item.get("line_total"), currency), styles["cell_r"]),
        ])
    if len(data) == 1:
        data.append([Paragraph("<i>No line items</i>", styles["cell"]), "", "", ""])

    items = Table(data, colWidths=col_w, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("TOPPADDING", (0, 0), (-1, 0), 7),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 7),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, BORDER),
    ]
    for row in range(1, len(data)):
        if row % 2 == 0:
            style.append(("BACKGROUND", (0, row), (-1, row), ZEBRA))
    items.setStyle(TableStyle(style))
    story.append(items)
    story.append(Spacer(1, 14))

    # ---- Totals (right-aligned) ----
    tax_rate = Decimal(str(ctx.get("tax_rate") or 0))
    totals_data = [
        [Paragraph("Subtotal", styles["cell"]),
         Paragraph(_money(ctx.get("subtotal"), currency), styles["cell_r"])],
        [Paragraph(f"Tax ({tax_rate.normalize():f}%)", styles["cell"]),
         Paragraph(_money(ctx.get("tax_amount"), currency), styles["cell_r"])],
    ]
    totals = Table(totals_data, colWidths=[content_w * 0.22, content_w * 0.18])
    totals.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))

    grand = Table(
        [[Paragraph("TOTAL DUE", styles["grand_l"]),
          Paragraph(_money(ctx.get("total"), currency), styles["grand"])]],
        colWidths=[content_w * 0.22, content_w * 0.18],
    )
    grand.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ACCENT),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    totals_stack = [totals, Spacer(1, 4), grand]
    wrap = Table([["", totals_stack]], colWidths=[content_w * 0.6, content_w * 0.4])
    wrap.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(wrap)

    # ---- Notes / payment terms ----
    if ctx.get("notes"):
        story.append(Spacer(1, 22))
        story.append(Table([[""]], colWidths=[content_w],
                           style=TableStyle([("LINEABOVE", (0, 0), (-1, -1), 0.5, BORDER)])))
        story.append(Spacer(1, 6))
        story.append(Paragraph("NOTES &amp; PAYMENT TERMS", styles["notes_h"]))
        story.append(Spacer(1, 3))
        story.append(Paragraph(esc(ctx.get("notes")), styles["notes"]))

    story.append(Spacer(1, 26))
    story.append(Paragraph(
        f"Thank you for your business{(' — ' + esc(ctx.get('sender_name'))) if ctx.get('sender_name') else ''}",
        ParagraphStyle("foot", parent=base["Normal"], fontSize=8.5, textColor=MUTED,
                       alignment=TA_LEFT, leading=12),
    ))

    doc.build(story)
    return buffer.getvalue()
