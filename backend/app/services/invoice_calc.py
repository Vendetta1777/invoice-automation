"""Server-side money math and PDF-context helpers for invoices."""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceCreate

CENTS = Decimal("0.01")


def _round(value: Decimal) -> Decimal:
    return value.quantize(CENTS, rounding=ROUND_HALF_UP)


def compute_totals(payload: InvoiceCreate) -> dict[str, Any]:
    """Compute per-line totals and invoice subtotal/tax/total server-side."""
    line_items: list[dict[str, Any]] = []
    subtotal = Decimal("0")
    for item in payload.line_items:
        qty = Decimal(str(item.quantity))
        unit = Decimal(str(item.unit_price))
        line_total = _round(qty * unit)
        subtotal += line_total
        line_items.append({
            "description": item.description,
            "quantity": qty,
            "unit_price": _round(unit),
            "line_total": line_total,
        })

    subtotal = _round(subtotal)
    tax_rate = Decimal(str(payload.tax_rate or 0))
    tax_amount = _round(subtotal * tax_rate / Decimal("100"))
    total = _round(subtotal + tax_amount)

    return {
        "line_items": line_items,
        "subtotal": subtotal,
        "tax_rate": tax_rate,
        "tax_amount": tax_amount,
        "total": total,
    }


def next_invoice_number(db: Session) -> str:
    """Generate a sequential invoice number like INV-2026-0007."""
    year = date.today().year
    prefix = f"INV-{year}-"
    count = db.scalar(
        select(Invoice).where(Invoice.invoice_number.like(f"{prefix}%")).order_by(
            Invoice.id.desc()
        ).limit(1)
    )
    seq = 1
    if count is not None:
        try:
            seq = int(count.invoice_number.rsplit("-", 1)[-1]) + 1
        except (ValueError, IndexError):
            seq = 1
    return f"{prefix}{seq:04d}"


def build_pdf_context(payload: InvoiceCreate, invoice_number: str, totals: dict[str, Any]) -> dict[str, Any]:
    """Assemble the flat context dict the PDF renderer consumes."""
    return {
        "sender_name": payload.sender_name,
        "sender_address": payload.sender_address,
        "sender_email": payload.sender_email,
        "sender_phone": payload.sender_phone,
        "logo_data_url": payload.logo_data_url,
        "client_name": payload.client_name,
        "client_email": payload.client_email,
        "client_address": payload.client_address,
        "client_phone": payload.client_phone,
        "invoice_number": invoice_number,
        "issue_date": payload.issue_date.isoformat(),
        "due_date": payload.due_date.isoformat(),
        "currency": payload.currency,
        "notes": payload.notes,
        **totals,
    }


def invoice_to_pdf_context(invoice: Invoice) -> dict[str, Any]:
    """Build a PDF context from a persisted Invoice ORM object."""
    return {
        "sender_name": invoice.sender_name,
        "sender_address": invoice.sender_address,
        "sender_email": invoice.sender_email,
        "sender_phone": invoice.sender_phone,
        "logo_data_url": invoice.logo_data_url,
        "client_name": invoice.client_name,
        "client_email": invoice.client_email,
        "client_address": invoice.client_address,
        "client_phone": invoice.client_phone,
        "invoice_number": invoice.invoice_number,
        "issue_date": invoice.issue_date.isoformat(),
        "due_date": invoice.due_date.isoformat(),
        "currency": invoice.currency,
        "notes": invoice.notes,
        "tax_rate": invoice.tax_rate,
        "subtotal": invoice.subtotal,
        "tax_amount": invoice.tax_amount,
        "total": invoice.total,
        "line_items": [
            {
                "description": li.description,
                "quantity": li.quantity,
                "unit_price": li.unit_price,
                "line_total": li.line_total,
            }
            for li in invoice.line_items
        ],
    }
