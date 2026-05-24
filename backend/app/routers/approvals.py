from fastapi import APIRouter, HTTPException, status

from app.schemas.approval import ApprovalDecision, ApprovalRead, ApprovalRequest

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("/pending", response_model=list[ApprovalRead])
def list_pending_approvals() -> list[ApprovalRead]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Approval listing not implemented yet — wire up in v0.1.",
    )


@router.post("/request", response_model=ApprovalRead, status_code=status.HTTP_201_CREATED)
def request_approval(payload: ApprovalRequest) -> ApprovalRead:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Approval request not implemented yet — see services/approval_workflow.py.",
    )


@router.post("/{approval_id}/approve", response_model=ApprovalRead)
def approve(approval_id: int, decision: ApprovalDecision) -> ApprovalRead:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Approve action not implemented yet — see services/approval_workflow.py.",
    )


@router.post("/{approval_id}/reject", response_model=ApprovalRead)
def reject(approval_id: int, decision: ApprovalDecision) -> ApprovalRead:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Reject action not implemented yet — see services/approval_workflow.py.",
    )
