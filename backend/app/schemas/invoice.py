from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.invoice import InvoiceStatus


class InvoiceLineItemCreate(BaseModel):
    description: str
    quantity: Decimal
    unit_price: Decimal


class InvoiceLineItemRead(InvoiceLineItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    line_total: Decimal


class InvoiceCreate(BaseModel):
    client_id: int
    issue_date: date
    due_date: date
    tax_rate: Decimal = Decimal("0")
    currency: str = "USD"
    notes: str | None = None
    line_items: list[InvoiceLineItemCreate]


class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_number: str
    client_id: int
    created_by_id: int
    status: InvoiceStatus
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
