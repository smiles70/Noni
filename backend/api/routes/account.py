"""Account self-service routes: delete / cancel-delete / me.

See ADR 0023.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session as DbSession

from backend.api.deps import get_current_account, get_db
from backend.core.config import settings
from backend.models.accounts import Account
from backend.services.deletion import cancel_deletion, request_deletion

router = APIRouter()


@router.post("/delete", status_code=status.HTTP_202_ACCEPTED)
def request_account_deletion(
    response: Response,
    account: Account = Depends(get_current_account),
    db: DbSession = Depends(get_db),
):
    req = request_deletion(db, account)
    db.commit()
    # Sign the user out as soon as deletion is requested.
    response.delete_cookie(settings.SESSION_COOKIE_NAME, path="/")
    return {
        "deletion_request_id": str(req.id),
        "scheduled_for": req.scheduled_for.isoformat(),
        "status": req.status,
    }


@router.post("/delete/cancel")
def cancel_account_deletion(
    account: Account = Depends(get_current_account),
    db: DbSession = Depends(get_db),
):
    req = cancel_deletion(db, account)
    if req is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"envelope_id": "account.deletion_not_cancelable"},
        )
    db.commit()
    return {
        "deletion_request_id": str(req.id),
        "status": req.status,
    }
