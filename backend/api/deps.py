"""FastAPI dependencies for the authenticated request path.

See ADR 0023 (original session-cookie design) and ADR 0024 (Clerk
migration; this module's current shape).

Auth model — stateless Bearer:
- Every protected request carries `Authorization: Bearer <token>`.
- Token is verified per-request by `auth_provider.verify_credential`:
    * MockAuthProvider:  `mock:<email>`           (dev/tests only)
    * ClerkAuthProvider: Clerk-issued RS256 JWT   (production)
- No `sessions` row is read or written. PyJWKClient caches Clerk's
  public keys in-process, so verification is O(decode), not O(network).
- Account row is upserted lazily on first sight, keyed by the
  provider's stable subject (Clerk `sub` -> deterministic UUID).

Why this shape:
- Removes cookie/CORS/CSRF coupling that bit us during the Supabase->
  Clerk migration. Bearer tokens are stateless and same-origin-agnostic.
- Matches every public Clerk + FastAPI reference architecture
  (`fastapi-clerk-auth`, `OSSMafia/fastapi-clerk-middleware`, Clerk's
  own docs at clerk.com/docs/backend-requests/making/cross-origin).
- The `sessions` table remains in the schema for now but is unused;
  scheduled for deletion after a clean operational window.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DbSession

from backend.core.database import SessionLocal
from backend.models.accounts import Account
from backend.services.auth_provider import AuthClaims, AuthProvider, get_auth_provider


def get_db():
    """Request-scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _parse_bearer(authorization: Optional[str]) -> Optional[str]:
    """Extract the token from an `Authorization: Bearer <token>` header.

    Returns None for any malformed input (missing header, wrong scheme,
    empty token). The dep treats None as "not signed in" — never raises.
    """
    print(
        "DIAG_AUTHZ_HEADER=",
        (
            (authorization[:24] + "...")
            if isinstance(authorization, str) and len(authorization) > 24
            else authorization
        ),
        flush=True,
    )
    if not authorization:
        return None
    parts = authorization.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    token = parts[1].strip()
    return token or None


def _upsert_account(
    db: DbSession,
    claims: AuthClaims,
    provider: AuthProvider,
) -> Optional[Account]:
    """Idempotent account row for the given provider claims.

    Two execution paths:
      1. Account exists -> sync mutable fields (email, display_name)
         when the claims carry fresh values, then return. We never
         clobber a known-good email with None just because the JWT
         omitted it (Clerk's default token does).
      2. Account does not exist -> INSERT. We need an email because
         `accounts.email` is NOT NULL UNIQUE. If the JWT didn't supply
         one (Clerk default), we fetch the user's profile from the
         provider's Backend API. If even that fails, we return None
         and the caller surfaces a 401.

    Concurrent first-sight from a second tab can race us to the
    unique(auth_user_id) index; on IntegrityError we rollback and
    re-SELECT (the other request won).
    """
    account = (
        db.query(Account)
        .filter(Account.auth_user_id == claims.auth_user_id)
        .one_or_none()
    )
    now = datetime.now(timezone.utc)
    if account is not None:
        if claims.email and account.email != claims.email:
            account.email = claims.email
        if claims.display_name and account.display_name != claims.display_name:
            account.display_name = claims.display_name
        account.updated_at = now
        return account

    email = claims.email
    display_name = claims.display_name
    if not email and claims.subject:
        profile = provider.fetch_user_profile(claims.subject)
        if profile is not None:
            email = profile.email
            if not display_name:
                display_name = profile.display_name
    if not email:
        # Cannot insert without a value for NOT NULL UNIQUE accounts.email.
        # Caller treats None as 401, which is the right outcome: the
        # token verified, but we couldn't materialize a user record.
        return None

    candidate = Account(
        id=uuid.uuid4(),
        auth_user_id=claims.auth_user_id,
        email=email,
        display_name=display_name,
    )
    db.add(candidate)
    try:
        db.flush()
        return candidate
    except IntegrityError:
        db.rollback()
        # Race A: another request inserted the same auth_user_id first.
        existing = (
            db.query(Account)
            .filter(Account.auth_user_id == claims.auth_user_id)
            .one_or_none()
        )
        if existing is not None:
            return existing
        # Race B: a pre-existing row owns this email under a different
        # auth_user_id (e.g. legacy Supabase row or prior mock login).
        # Clerk is authoritative now -- relink the row to the new subject.
        existing = db.query(Account).filter(Account.email == email).one_or_none()
        if existing is not None:
            existing.auth_user_id = claims.auth_user_id
            if display_name and existing.display_name != display_name:
                existing.display_name = display_name
            existing.updated_at = datetime.now(timezone.utc)
            db.flush()
            return existing
        return None


def get_optional_account(
    authorization: Optional[str] = Header(default=None),
    db: DbSession = Depends(get_db),
) -> Optional[Account]:
    """Resolve the current account from `Authorization: Bearer ...`.

    Returns None for any verification failure (missing header,
    malformed token, signature invalid, expired, missing email,
    revoked). The caller decides whether None means 401 (gated routes)
    or "render signed-out" (entitlement routes return 402 instead).

    Commits the upsert before returning so the new row is durable even
    if the surrounding route is read-only (e.g. /auth/whoami).
    """
    token = _parse_bearer(authorization)
    if token is None:
        return None
    provider = get_auth_provider()
    claims = provider.verify_credential(token)
    if claims is None:
        return None
    account = _upsert_account(db, claims, provider)
    if account is None:
        return None
    db.commit()
    return account


def get_current_account(
    account: Optional[Account] = Depends(get_optional_account),
) -> Account:
    """Require a signed-in account; raise 401 + auth.signed_out otherwise."""
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
