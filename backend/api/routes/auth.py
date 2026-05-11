"""Authentication routes.

See ADR 0023.

Endpoints:
- POST /auth/callback     verify credential, mint session, set cookie
- POST /auth/signout      revoke active session, clear cookie
- GET  /auth/whoami       return current account or 401

The 'credential' field is provider-shaped: with AUTH_PROVIDER=mock it's
"mock:<email>"; with AUTH_PROVIDER=supabase it's the Supabase-issued JWT.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession

from backend.api.deps import get_current_account, get_db
from backend.core.config import settings
from backend.models.accounts import Account
from backend.services.auth_provider import get_auth_provider
from backend.services.sessions import (
    create_session,
    find_or_create_account_for_claims,
    lookup_session,
    revoke_session,
)


router = APIRouter()


class AuthCallbackRequest(BaseModel):
    credential: str


class AuthCallbackResponse(BaseModel):
    account_id: str
    email: str
    display_name: Optional[str] = None


@router.post("/callback", response_model=AuthCallbackResponse)
def auth_callback(
    body: AuthCallbackRequest,
    request: Request,
    response: Response,
    db: DbSession = Depends(get_db),
) -> AuthCallbackResponse:
    provider = get_auth_provider()
    claims = provider.verify_credential(body.credential)
    if claims is None:
        # Fail closed; do not leak which validation step failed.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"envelope_id": "auth.signed_out"},
        )

    account = find_or_create_account_for_claims(db, claims)
    _, cookie_value = create_session(
        db,
        account,
        last_ip=request.client.host if request.client else None,
        last_user_agent=request.headers.get("user-agent"),
    )
    db.commit()

    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=cookie_value,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.SESSION_TTL_DAYS * 24 * 3600,
        path="/",
    )
    return AuthCallbackResponse(
        account_id=str(account.id),
        email=account.email,
        display_name=account.display_name,
    )


@router.post("/signout")
def auth_signout(
    request: Request,
    response: Response,
    db: DbSession = Depends(get_db),
):
    cookie_value = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if cookie_value:
        session_row = lookup_session(db, cookie_value)
        if session_row is not None:
            revoke_session(db, session_row, reason="user_signed_out")
            db.commit()
    response.delete_cookie(settings.SESSION_COOKIE_NAME, path="/")
    return {"signed_out": True}


@router.get("/whoami", response_model=AuthCallbackResponse)
def auth_whoami(
    account: Account = Depends(get_current_account),
) -> AuthCallbackResponse:
    return AuthCallbackResponse(
        account_id=str(account.id),
        email=account.email,
        display_name=account.display_name,
    )
