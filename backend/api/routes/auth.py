"""Authentication routes.

See ADR 0023 (original session-cookie design) and ADR 0024 (Clerk
migration; this module's current shape).

Endpoints:

  Legacy (preserved until the frontend cuts over to /auth/session):
    GET  /auth/whoami           current account or 401 (legacy envelope).

  Redesign (Stage 2 — login-redesign-v1):
    GET  /auth/config           provider parity probe (B3, T4).
    GET  /auth/session          pure-read session resolver (B4, B5, T6).
    POST /auth/session/init     account materialization write event
                                (B4, T6, B8, I-D, I-E).

The redesigned endpoints use the discriminated 401 envelope
`{"error": {"code": "<auth.*>", "message": "..."}}` per B5. The legacy
`/whoami` endpoint keeps its existing `{"detail": {"envelope_id":
"auth.signed_out"}}` shape so the current frontend keeps working until
its <AuthProvider> migration lands.

Removed in ADR 0024 (still gone, with regression tests):
- POST /auth/callback
- POST /auth/signout
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession

from backend.api.deps import get_current_account, get_db
from backend.app.telemetry import record_auth_session_outcome
from backend.core.config import settings
from backend.models.accounts import Account
from backend.services.account_materializer import materialize
from backend.services.auth_verifier import AuthError, parse_bearer, verify_token


router = APIRouter()


# ---------------------------------------------------------------------------
# Legacy: GET /auth/whoami — unchanged for FE compatibility.
# ---------------------------------------------------------------------------


class WhoAmIResponse(BaseModel):
    """Shape returned by /auth/whoami.

    `has_active_session` is preserved as the frontend's compatibility
    field — in the Bearer model a successful response by definition
    means "active". A 401 (no/invalid token) returns no body, and the
    frontend treats that as signed-out.
    """

    account_id: str
    # Email may be missing in pathological provider states (e.g. an
    # account row predating the Clerk migration). Treat as nullable on
    # the wire so we don't 500 instead of returning a usable response.
    email: Optional[str] = None
    display_name: Optional[str] = None
    has_active_session: bool = True


@router.get("/whoami", response_model=WhoAmIResponse)
def auth_whoami(
    account: Account = Depends(get_current_account),
) -> WhoAmIResponse:
    return WhoAmIResponse(
        account_id=str(account.id),
        email=account.email,
        display_name=account.display_name,
        has_active_session=True,
    )


# ---------------------------------------------------------------------------
# Redesign: GET /auth/config — provider parity probe (B3, T4).
# ---------------------------------------------------------------------------


class AuthConfigResponse(BaseModel):
    """Backend's view of which identity provider is configured.

    The frontend asserts `provider == VITE_AUTH_PROVIDER` at boot and
    aborts the app render on mismatch (T-D2). Public; no auth required.
    """

    provider: str
    version: str


@router.get("/config", response_model=AuthConfigResponse)
def auth_config() -> AuthConfigResponse:
    return AuthConfigResponse(
        provider=settings.AUTH_PROVIDER.strip().lower(),
        version=settings.VERSION,
    )


# ---------------------------------------------------------------------------
# Redesign envelope + helpers.
# ---------------------------------------------------------------------------


def _auth_error_response(err: AuthError) -> HTTPException:
    """Map an AuthError to a 401 (or 409 for collision) with the
    discriminated envelope `{error:{code,message}}` (B5)."""
    status_code = status.HTTP_401_UNAUTHORIZED
    return HTTPException(
        status_code=status_code,
        detail={"error": {"code": err.code, "message": err.message}},
    )


class AuthSessionResponse(BaseModel):
    """Shape returned by GET /auth/session.

    `materialized=False` means the token verified but no account row
    exists for the subject yet; the frontend must POST /auth/session/init
    to create the row. `account_id`/`email`/`display_name` are populated
    only when materialized=True.
    """

    subject: str
    materialized: bool
    account_id: Optional[str] = None
    email: Optional[str] = None
    display_name: Optional[str] = None


# ---------------------------------------------------------------------------
# Redesign: GET /auth/session — pure-read session resolver (B4, B5, T6).
# ---------------------------------------------------------------------------


@router.get("/session", response_model=AuthSessionResponse)
def auth_session(
    authorization: Optional[str] = Header(default=None),
    db: DbSession = Depends(get_db),
) -> AuthSessionResponse:
    """Resolve the session for a Bearer token. NEVER writes (B4, I-B).

    Verifies the token via `auth_verifier.verify_token` (no DB, no
    provider Backend API). Then performs a single read against the
    `accounts` table filtered by `deleted_at IS NULL` (B7, I-E).

    Outcome codes (B5):
      ok.materialized          — row exists and is active.
      ok.unmaterialized        — token valid but no row yet (FE must
                                  POST /auth/session/init).
      ok.deleted_account       — row exists but is soft-deleted; surfaces
                                  as 401 auth.account_deleted (B7, I-E).
      auth.*                   — verification failure (B5).
    """
    token = parse_bearer(authorization)
    try:
        claims = verify_token(token)
    except AuthError as err:
        record_auth_session_outcome(err.code)
        raise _auth_error_response(err) from err

    # Read-only lookup. Filter out soft-deleted rows.
    account = (
        db.query(Account)
        .filter(
            Account.auth_user_id == claims.auth_user_id,
            Account.deleted_at.is_(None),
        )
        .one_or_none()
    )

    # If a row exists but is soft-deleted, the deletion is terminal
    # (B7, I-E): we 401 with auth.account_deleted rather than returning
    # `materialized=False` (which would let the FE POST /init and
    # potentially resurrect the row).
    if account is None:
        deleted = (
            db.query(Account.id)
            .filter(
                Account.auth_user_id == claims.auth_user_id,
                Account.deleted_at.isnot(None),
            )
            .first()
        )
        if deleted is not None:
            record_auth_session_outcome("auth.account_deleted")
            raise _auth_error_response(AuthError("auth.account_deleted"))
        record_auth_session_outcome("ok.unmaterialized")
        # B4: do not write. The frontend will POST /auth/session/init
        # to materialize.
        return AuthSessionResponse(
            subject=str(claims.subject or claims.auth_user_id),
            materialized=False,
        )

    record_auth_session_outcome("ok.materialized")
    return AuthSessionResponse(
        subject=str(claims.subject or claims.auth_user_id),
        materialized=True,
        account_id=str(account.id),
        email=account.email,
        display_name=account.display_name,
    )


# ---------------------------------------------------------------------------
# Redesign: POST /auth/session/init — write event (B4, T6, B8).
# ---------------------------------------------------------------------------


class AuthSessionInitResponse(BaseModel):
    account_id: str


@router.post("/session/init", response_model=AuthSessionInitResponse)
def auth_session_init(
    authorization: Optional[str] = Header(default=None),
    db: DbSession = Depends(get_db),
) -> AuthSessionInitResponse:
    """Materialize the account row for a verified subject (B4, T6).

    This is the ONLY endpoint that writes to `accounts`. Idempotent:
    a no-op INSERT on conflict returns the existing row.

    Failure modes:
      - Token verification failure → 401 with discriminated `auth.*`.
      - Materializer raises `auth.account_deleted` → 401 (B7, I-E); the
        frontend then renders the deleted-account surface and calls
        /me/recreate to clear `deleted_at` (Stage 3+).
      - Materializer raises `auth.transient_db_unavailable` → 401; FE
        treats as transient (R3) and keeps the user signed in.
    """
    token = parse_bearer(authorization)
    try:
        claims = verify_token(token)
    except AuthError as err:
        record_auth_session_outcome(err.code)
        raise _auth_error_response(err) from err

    try:
        account = materialize(db, claims)
    except AuthError as err:
        record_auth_session_outcome(err.code)
        # Materializer's deletion gate raises auth.account_deleted; all
        # other materializer errors propagate with their own codes.
        raise _auth_error_response(err) from err

    db.commit()
    record_auth_session_outcome("ok.materialized")
    return AuthSessionInitResponse(account_id=str(account.id))
