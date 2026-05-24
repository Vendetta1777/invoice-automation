from fastapi import APIRouter, HTTPException, status

from app.schemas.invoice import InvoiceCreate, InvoiceRead

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("/", response_model=list[InvoiceRead])
def list_invoices() -> list[InvoiceRead]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Invoice listing not implemented yet — wire up in v0.1.",
    )


@router.post("/", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
def create_invoice(payload: InvoiceCreate) -> InvoiceRead:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Invoice creation not implemented yet — wire up in v0.1.",
    )


@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(invoice_id: int) -> dict[str, str]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="PDF generation not implemented yet — see services/pdf_generator.py.",
    )


@router.post("/{invoice_id}/send")
def send_invoice(invoice_id: int) -> dict[str, str]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Email sending not implemented yet — see services/email_sender.py.",
    )
