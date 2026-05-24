from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.config import get_settings
from app.models.invoice import Invoice


def render_invoice_pdf(invoice: Invoice) -> bytes:
    settings = get_settings()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    story = [
        Paragraph(f"<b>{settings.business_name}</b>", styles["Title"]),
        Paragraph(settings.business_address, styles["Normal"]),
        Spacer(1, 18),
        Paragraph(f"<b>Invoice #{invoice.invoice_number}</b>", styles["Heading2"]),
        Paragraph(f"Issue date: {invoice.issue_date}", styles["Normal"]),
        Paragraph(f"Due date: {invoice.due_date}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph(f"<b>Total: {invoice.total} {invoice.currency}</b>", styles["Heading3"]),
    ]
    doc.build(story)
    return buffer.getvalue()
