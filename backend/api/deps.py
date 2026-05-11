"""FastAPI dependencies for the authenticated request path.

See ADR 0023.

Conventions:
- `get_db` yields a request-scoped SQLAlchemy session.
- `get_optional_account` returns None on absent/invalid session (used by
  endpoints that handle both signed-in and signed-out states).
- `get_current_account` requires a valid session and returns 401 +
  envelope id `auth.signed_out` otherwise.
"""

from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session as DbSession

from backend.core.config import settings
from backend.core.database import SessionLocal
from backend.models.accounts import Account
from backend.services.sessions import lookup_session


def get_db():
    """Request-scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_optional_account(
    request: Request,
    db: DbSession = Depends(get_db),
) -> Optional[Account]:
    cookie_value = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not cookie_value:
        return None
    session_row = lookup_session(db, cookie_value)
    if session_row is None:
        return None
    return db.query(Account).filter(Account.id == session_row.account_id).one_or_none()


def get_current_account(
    account: Optional[Account] = Depends(get_optional_account),
) -> Account:
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"envelope_id": "auth.signed_out"},
        )
    return account


def require_entitlement(product_code: str):
    """Dependency factory that gates a route behind an active entitlement.

    See ADR 0021. Behaviour:
      - No session at all       -> 402 + envelope billing.signin_or_purchase_required
      - Session but no grant    -> 402 + envelope billing.purchase_required
      - Active grant            -> returns the Account

    402 (Payment Required) is intentional: the resource exists but cannot
    be served without payment. The frontend reads `envelope_id` to decide
    between showing the sign-in page or the paywall page.
    """
    # Local import keeps this module import-cycle free at startup.
    from backend.services import entitlements

    def _dep(
        account: Optional[Account] = Depends(get_optional_account),
        db: DbSession = Depends(get_db),
    ) -> Account:
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "envelope_id": "billing.signin_or_purchase_required",
                    "product_code": product_code,
                },
            )
        if not entitlements.has_active(db, account.id, product_code):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "envelope_id": "billing.purchase_required",
                    "product_code": product_code,
                },
            )
        return account

    return _dep
