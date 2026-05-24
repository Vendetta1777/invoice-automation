from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.approval import ApprovalStatus


class ApprovalRequest(BaseModel):
    invoice_id: int
    approver_id: int
    comment: str | None = None


class ApprovalDecision(BaseModel):
    comment: str | None = None


class ApprovalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    requested_by_id: int
    approver_id: int
    status: ApprovalStatus
    comment: str | None
    created_at: datetime
    updated_at: datetime
