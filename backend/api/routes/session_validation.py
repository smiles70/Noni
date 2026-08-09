"""Session validation routes.

EPIC-002 Phase 4: Session validation for enhanced security.

Endpoints:
    GET /api/v1/session/validate    Validate current session
"""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from backend.api.deps import get_db
from backend.services.auth_verifier import parse_bearer, verify_token, AuthError
from backend.models.accounts import Account

router = APIRouter()


class SessionValidationResponse(BaseModel):
    """Response model for session validation."""

    valid: bool
    account_id: Optional[str] = None
    expires_in: Optional[int] = None  # seconds until expiration


@router.get("/validate", response_model=SessionValidationResponse)
def validate_session(
    authorization: Optional[str] = Header(default=None),
    db: DbSession = Depends(get_db),
) -> SessionValidationResponse:
    """Validate the current session and return expiration info.

    EPIC-002 Phase 4: This endpoint validates the current session
    and provides expiration information for proactive session management.

    Args:
        authorization: Bearer token header
        db: Database session

    Returns:
        Session validation result with expiration info

    Raises:
        401: Unauthorized (invalid or missing token)
    """
    # Token verification
    token = parse_bearer(authorization)
    if not token:
        return SessionValidationResponse(
            valid=False,
            account_id=None,
            expires_in=None,
        )

    try:
        claims = verify_token(token)
    except AuthError:
        return SessionValidationResponse(
            valid=False,
            account_id=None,
            expires_in=None,
        )

    if not claims.auth_user_id:
        return SessionValidationResponse(
            valid=False,
            account_id=None,
            expires_in=None,
        )

    # Check if account exists and is not deleted
    account = (
        db.query(Account)
        .filter(Account.auth_user_id == claims.auth_user_id)
        .filter(Account.deleted_at.is_(None))
        .first()
    )

    if not account:
        return SessionValidationResponse(
            valid=False,
            account_id=None,
            expires_in=None,
        )

    # Calculate expiration (30 minutes from session start)
    # This is a simplified implementation - in production, use actual token expiration
    expires_in = 30 * 60  # 30 minutes in seconds

    return SessionValidationResponse(
        valid=True,
        account_id=str(account.id),
        expires_in=expires_in,
    )