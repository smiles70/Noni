"""Session lifecycle service.

See ADR 0023. Owns:
- create_session: mints token, persists hash, returns signed cookie value
- lookup_session: validates cookie, returns Session row if active
- revoke_session: row-level revocation
- find_or_create_account_for_claims: idempotent account upsert by auth_user_id
"""

from __future__ import annotations

import ipaddress
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from sqlalchemy.orm import Session as DbSession

from backend.core.config import settings
from backend.core.security import generate_session_token, verify_session_cookie
from backend.models.accounts import Account
from backend.models.auth import Session as SessionRow
from backend.services.auth_provider import AuthClaims


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _coerce_ip(value: Optional[str]) -> Optional[str]:
    """Return `value` only if it parses as a valid IPv4/IPv6 address.

    Starlette's TestClient supplies the literal string 'testclient' as
    `request.client.host`, which the Postgres INET type rejects. We fail
    soft: store NULL instead of raising, since this column is
    diagnostic, not security-bearing.
    """
    if not value:
        return None
    try:
        ipaddress.ip_address(value)
    except ValueError:
        return None
    return value


def find_or_create_account_for_claims(db: DbSession, claims: AuthClaims) -> Account:
    """Upsert account keyed by `auth_user_id`. Email is updated if changed."""
    account = (
        db.query(Account)
        .filter(Account.auth_user_id == claims.auth_user_id)
        .one_or_none()
    )
    if account is None:
        account = Account(
            id=uuid.uuid4(),
            auth_user_id=claims.auth_user_id,
            email=claims.email,
            display_name=claims.display_name,
        )
        db.add(account)
        db.flush()
    else:
        # Keep email + display_name in sync with provider.
        account.email = claims.email
        if claims.display_name is not None:
            account.display_name = claims.display_name
        account.updated_at = _utcnow()
    return account


def create_session(
    db: DbSession,
    account: Account,
    *,
    last_ip: Optional[str] = None,
    last_user_agent: Optional[str] = None,
    ttl_days: Optional[int] = None,
) -> Tuple[SessionRow, str]:
    """Create a session row, return (row, signed_cookie_value).

    The plaintext token is never persisted; the cookie value carries it
    in signed form and the DB stores only sha256(raw).
    """
    _, cookie_value, token_hash = generate_session_token()
    ttl = ttl_days if ttl_days is not None else settings.SESSION_TTL_DAYS
    row = SessionRow(
        id=uuid.uuid4(),
        account_id=account.id,
        session_token_hash=token_hash,
        issued_at=_utcnow(),
        expires_at=_utcnow() + timedelta(days=ttl),
        last_ip=_coerce_ip(last_ip),
        last_user_agent=last_user_agent,
    )
    db.add(row)
    db.flush()
    return row, cookie_value


def lookup_session(db: DbSession, signed_cookie_value: str) -> Optional[SessionRow]:
    """Verify cookie signature, return active session row or None.

    Fails closed on:
      - tampered / missing signature
      - no row in DB
      - revoked_at set
      - expires_at in the past
    """
    token_hash = verify_session_cookie(signed_cookie_value)
    if token_hash is None:
        return None
    row = (
        db.query(SessionRow)
        .filter(SessionRow.session_token_hash == token_hash)
        .one_or_none()
    )
    if row is None:
        return None
    if row.revoked_at is not None:
        return None
    if row.expires_at <= _utcnow():
        return None
    return row


def revoke_session(
    db: DbSession,
    session_row: SessionRow,
    reason: str = "user_signed_out",
) -> None:
    session_row.revoked_at = _utcnow()
    session_row.revocation_reason = reason
    db.flush()
