from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.invoice import Invoice, InvoiceLineItem
from app.schemas.invoice import InvoiceCreate, InvoiceRead
from app.services.invoice_calc import (
    build_pdf_context,
    compute_totals,
    invoice_to_pdf_context,
    next_invoice_number,
)
from app.services.pdf_generator import render_invoice_pdf

router = APIRouter(prefix="/invoices", tags=["invoices"])


def _safe_filename(invoice: Invoice) -> str:
    client = "".join(c if c.isalnum() or c in "-_" else "-" for c in (invoice.client_name or "client"))
    return f"Invoice-{invoice.invoice_number}-{client}.pdf".replace("--", "-")


@router.get("/", response_model=list[InvoiceRead])
def list_invoices(db: Session = Depends(get_db)) -> list[Invoice]:
    return list(
        db.scalars(
            select(Invoice).options(selectinload(Invoice.line_items)).order_by(Invoice.id.desc())
        )
    )


@router.post("/", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db)) -> Invoice:
    if not payload.line_items:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "At least one line item is required.")

    totals = compute_totals(payload)
    invoice_number = payload.invoice_number or next_invoice_number(db)

    if db.scalar(select(Invoice).where(Invoice.invoice_number == invoice_number)):
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"Invoice number '{invoice_number}' already exists."
        )

    invoice = Invoice(
        invoice_number=invoice_number,
        sender_name=payload.sender_name,
        sender_address=payload.sender_address,
        sender_email=payload.sender_email,
        sender_phone=payload.sender_phone,
        logo_data_url=payload.logo_data_url,
        client_name=payload.client_name,
        client_email=payload.client_email,
        client_address=payload.client_address,
        client_phone=payload.client_phone,
        issue_date=payload.issue_date,
        due_date=payload.due_date,
        currency=payload.currency,
        notes=payload.notes,
        subtotal=totals["subtotal"],
        tax_rate=totals["tax_rate"],
        tax_amount=totals["tax_amount"],
        total=totals["total"],
        line_items=[
            InvoiceLineItem(
                description=li["description"],
                quantity=li["quantity"],
                unit_price=li["unit_price"],
                line_total=li["line_total"],
            )
            for li in totals["line_items"]
        ],
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/{invoice_id}", response_model=InvoiceRead)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)) -> Invoice:
    invoice = db.scalar(
        select(Invoice).options(selectinload(Invoice.line_items)).where(Invoice.id == invoice_id)
    )
    if invoice is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invoice not found.")
    return invoice


@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(invoice_id: int, db: Session = Depends(get_db)) -> Response:
    invoice = db.scalar(
        select(Invoice).options(selectinload(Invoice.line_items)).where(Invoice.id == invoice_id)
    )
    if invoice is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invoice not found.")

    pdf = render_invoice_pdf(invoice_to_pdf_context(invoice))
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{_safe_filename(invoice)}"'},
    )


@router.post("/preview-pdf")
def preview_pdf(payload: InvoiceCreate) -> StreamingResponse:
    """Stateless PDF render — no DB write, no auth, instant for the live demo."""
    totals = compute_totals(payload)
    invoice_number = payload.invoice_number or "DRAFT"
    ctx = build_pdf_context(payload, invoice_number, totals)
    pdf = render_invoice_pdf(ctx)
    from io import BytesIO

    return StreamingResponse(
        BytesIO(pdf),
        media_type="application/pdf",
        headers={"Content-Disposition": 'inline; filename="invoice-preview.pdf"'},
    )
