from sqlalchemy.orm import Session

from app.models.approval import Approval, ApprovalStatus
from app.models.invoice import Invoice, InvoiceStatus


def request_approval(
    db: Session, invoice: Invoice, requested_by_id: int, approver_id: int
) -> Approval:
    approval = Approval(
        invoice_id=invoice.id,
        requested_by_id=requested_by_id,
        approver_id=approver_id,
        status=ApprovalStatus.PENDING,
    )
    invoice.status = InvoiceStatus.PENDING_APPROVAL
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval


def approve(db: Session, approval: Approval, comment: str | None = None) -> Approval:
    approval.status = ApprovalStatus.APPROVED
    approval.comment = comment
    invoice = db.get(Invoice, approval.invoice_id)
    if invoice:
        invoice.status = InvoiceStatus.APPROVED
    db.commit()
    db.refresh(approval)
    return approval


def reject(db: Session, approval: Approval, comment: str | None = None) -> Approval:
    approval.status = ApprovalStatus.REJECTED
    approval.comment = comment
    invoice = db.get(Invoice, approval.invoice_id)
    if invoice:
        invoice.status = InvoiceStatus.REJECTED
    db.commit()
    db.refresh(approval)
    return approval
