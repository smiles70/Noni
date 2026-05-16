"""Account self-service routes: delete / cancel-delete.

See ADR 0023 (original) and ADR 0024 (Bearer migration).

Post-Bearer-migration note: deletion no longer clears a session cookie
because there is no session cookie. The frontend is responsible for
calling `clerk.signOut()` (or clearing the mock token) after a
successful 202; any straggling Bearer tokens we issued expire on their
own and reference an account row that's been marked for deletion.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from backend.api.deps import get_current_account, get_db
from backend.models.accounts import Account
from backend.services.deletion import cancel_deletion, request_deletion

router = APIRouter()


@router.post("/delete", status_code=status.HTTP_202_ACCEPTED)
def request_account_deletion(
    account: Account = Depends(get_current_account),
    db: DbSession = Depends(get_db),
):
    req = request_deletion(db, account)
    db.commit()
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
