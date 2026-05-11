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
