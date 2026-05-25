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
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DbSession

from backend.api.deps import get_current_account, get_db
from backend.app.telemetry import record_auth_session_outcome
from backend.core.config import settings
from backend.models.accounts import Account
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
    # Sprint 22 S7: never echo the raw AUTH_PROVIDER string publicly.
    # In production we always claim "clerk" regardless of backend config
    # to avoid information leakage; dev/tests see the real value.
    provider = (
        "clerk"
        if settings.ENVIRONMENT == "production"
        else settings.AUTH_PROVIDER.strip().lower()
    )
    return AuthConfigResponse(provider=provider, version=settings.VERSION)


# ---------------------------------------------------------------------------
# Redesign envelope + helpers.
# ---------------------------------------------------------------------------


def auth_error(code: str, message: str = "") -> None:
    """Emit telemetry then raise 401 with the discriminated envelope (B5).

    Always raises HTTPException; never returns. The helper centralises
    the contract `{error:{code,message}}` so no handler can accidentally
    return a 401 with a different shape.
    """
    record_auth_session_outcome(code)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error": {"code": code, "message": message or code}},
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

    Merged contract (see `docs/design/login-redesign-2026-05-17.md` §2.4
    and the FE AuthProvider in `frontend/src/auth/AuthProvider.tsx`):

    STEP 1 — token extraction (B10: parse_bearer never logs the header).
    STEP 2 — verify_token raises AuthError with a discriminated `code`
             (B5, C3, B11).
    STEP 3 — subject resolution. The verifier hashes the provider `sub`
             into a stable UUID (see auth_verifier._verify_clerk and
             _verify_mock); we filter on that UUID, NOT the raw `sub`,
             so existing rows continue to match.
    STEP 4 — single SELECT, no filter on deleted_at yet (we want to
             distinguish "no row" from "soft-deleted row").
    STEP 5 — deleted-account is terminal (B7, I-E): 401 with
             auth.account_deleted rather than materialized=false (which
             would invite the FE to POST /init and resurrect the row).
    STEP 6 — response. materialized=True if a live row exists;
             materialized=False if no row yet (FE then POSTs /init).
    """
    # STEP 1: token extraction.
    token = parse_bearer(authorization)
    if not token:
        auth_error("auth.no_credential")

    # STEP 2: verify token. AuthError already carries a code from the
    # closed CODES set in auth_verifier.
    try:
        claims = verify_token(token)
    except AuthError as err:
        auth_error(err.code, err.message)

    # STEP 3: subject resolution. claims.auth_user_id is the stable UUID
    # the verifier derives from the provider sub (uuid5).
    if not claims.auth_user_id:
        auth_error("auth.subject_missing")

    # STEP 4: read-only DB lookup. Single SELECT; deleted_at handled in
    # STEP 5 so we can distinguish "no row" from "deleted row".
    try:
        account = (
            db.query(Account)
            .filter(Account.auth_user_id == claims.auth_user_id)
            .one_or_none()
        )
    except Exception:
        auth_error("auth.transient_db_unavailable")

    # STEP 5: deleted-account gate (B7, I-E).
    if account is not None and account.deleted_at is not None:
        auth_error("auth.account_deleted")

    # STEP 6: response.
    if account is not None:
        record_auth_session_outcome("ok.materialized")
        return AuthSessionResponse(
            subject=str(claims.subject or claims.auth_user_id),
            materialized=True,
            account_id=str(account.id),
            email=account.email,
            display_name=account.display_name,
        )

    record_auth_session_outcome("ok.unmaterialized")
    return AuthSessionResponse(
        subject=str(claims.subject or claims.auth_user_id),
        materialized=False,
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
    """Materialize the account row for a verified subject (B4, T6, B7, B8).

    The ONLY write path for account creation. Idempotent.

    STEP 1 — token extraction (same as /auth/session).
    STEP 2 — verify_token (same verifier; AuthError carries the code).
    STEP 3 — subject resolution (UUID, not raw sub — preserves existing
             rows; avoids the init-loop class).
    STEP 4 — check existing. If a row exists:
                 - and is soft-deleted → 401 auth.account_deleted (B7, I-E).
                 - else return its id (idempotent).
    STEP 5 — create. The only INSERT path in the auth domain (B4).
    STEP 6 — race recovery: on IntegrityError, another writer won; re-
             SELECT and return that row, after applying the same
             deletion gate (B7). No relink branch (B8, I-D).
    """
    # STEP 1.
    token = parse_bearer(authorization)
    if not token:
        auth_error("auth.no_credential")

    # STEP 2.
    try:
        claims = verify_token(token)
    except AuthError as err:
        auth_error(err.code, err.message)

    # STEP 3.
    if not claims.auth_user_id:
        auth_error("auth.subject_missing")

    # STEP 4: check existing.
    existing = (
        db.query(Account)
        .filter(Account.auth_user_id == claims.auth_user_id)
        .one_or_none()
    )

    if existing is not None:
        # B7, I-E: deletion is terminal.
        if existing.deleted_at is not None:
            auth_error("auth.account_deleted")
        record_auth_session_outcome("ok.materialized")
        return AuthSessionInitResponse(account_id=str(existing.id))

    # STEP 5: create.
    try:
        account = Account(
            auth_user_id=claims.auth_user_id,
            email=claims.email,  # optional (B12)
            display_name=claims.display_name,
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        record_auth_session_outcome("ok.created")
        return AuthSessionInitResponse(account_id=str(account.id))

    except IntegrityError:
        db.rollback()

        # STEP 6: race recovery.
        existing = (
            db.query(Account)
            .filter(Account.auth_user_id == claims.auth_user_id)
            .one_or_none()
        )
        if existing is None:
            # An IntegrityError without a recoverable row implies a
            # different constraint failed; surface as transient.
            auth_error("auth.transient_db_unavailable")
        if existing.deleted_at is not None:
            auth_error("auth.account_deleted")
        record_auth_session_outcome("ok.race_resolved")
        return AuthSessionInitResponse(account_id=str(existing.id))
