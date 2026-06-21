from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.invoice import InvoiceStatus


class InvoiceLineItemCreate(BaseModel):
    description: str
    quantity: Decimal = Decimal("1")
    unit_price: Decimal = Decimal("0")


class InvoiceLineItemRead(InvoiceLineItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    line_total: Decimal


class InvoiceCreate(BaseModel):
    """Full invoice entry payload — used for create, preview, and PDF rendering.

    Everything needed to render an invoice is entered in-app: sender identity,
    optional logo, inline client details, line items, tax, and notes.
    """

    # Sender / business identity
    sender_name: str = ""
    sender_address: str | None = None
    sender_email: str | None = None
    sender_phone: str | None = None
    logo_data_url: str | None = None  # base64 data URL, e.g. "data:image/png;base64,..."

    # Inline client details (ad-hoc, no client record required)
    client_name: str = ""
    client_email: str | None = None
    client_address: str | None = None
    client_phone: str | None = None

    # Invoice meta
    invoice_number: str | None = None  # auto-generated if omitted
    issue_date: date
    due_date: date
    tax_rate: Decimal = Decimal("0")
    currency: str = "USD"
    notes: str | None = None

    line_items: list[InvoiceLineItemCreate] = Field(default_factory=list)


class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_number: str
    status: InvoiceStatus

    sender_name: str
    sender_address: str | None
    sender_email: str | None
    sender_phone: str | None
    logo_data_url: str | None

    client_name: str
    client_email: str | None
    client_address: str | None
    client_phone: str | None

    issue_date: date
    due_date: date
    subtotal: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    total: Decimal
    currency: str
    notes: str | None
    line_items: list[InvoiceLineItemRead]
    created_at: datetime
    updated_at: datetime
