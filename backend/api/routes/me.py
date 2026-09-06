"""Self-service account endpoints: deletion request, cancel, export.

Trust rubric items T-delete/T-export (TRUST_PRIVACY_RUBRIC_001):
- POST /me/delete -> 202 {status: "requested", scheduled_for} — schedules
  deletion after DELETION_GRACE_PERIOD_DAYS, soft-deletes immediately and
  revokes sessions (spec: test_a6_retention_deletion.py).
- POST /me/delete/cancel -> restores the account inside the grace window.
- GET /me/export -> the account's own data as JSON (GDPR-style export).

All responses fail closed and use calm envelope ids — never 500.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session as DbSession

from backend.api.deps import get_current_account, get_db
from backend.models.accounts import Account
from backend.services.deletion import cancel_deletion, request_deletion

router = APIRouter()


@router.post("/delete", status_code=status.HTTP_202_ACCEPTED)
def request_account_deletion(
    account: Account = Depends(get_current_account),
    db: DbSession = Depends(get_db),
) -> dict:
    """Schedule deletion; idempotent (reuses any pending request)."""
    req = request_deletion(db, account)
    db.commit()
    return {
        "status": "requested",
        "scheduled_for": req.scheduled_for.isoformat(),
    }


@router.post("/delete/cancel")
def cancel_account_deletion(
    account: Account = Depends(get_current_account),
    db: DbSession = Depends(get_db),
) -> dict:
    """Cancel a pending deletion inside the grace window."""
    req = cancel_deletion(db, account)
    if req is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"envelope_id": "account.delete_not_pending"},
        )
    db.commit()
    return {"status": "cancelled"}


@router.get("/export")
def export_account_data(
    account: Account = Depends(get_current_account),
) -> Response:
    """Return the account's own data as a JSON download."""
    import json

    body = {
        "account": {
            "email": account.email,
            "display_name": account.display_name,
            "created_at": account.created_at.isoformat()
            if account.created_at
            else None,
        },
        "deletion_scheduled": account.deleted_at.isoformat()
        if account.deleted_at
        else None,
    }
    return Response(
        content=json.dumps(body, indent=2),
        media_type="application/json",
        headers={
            "Content-Disposition": "attachment; filename=mynaani-my-data.json"
        },
    )
