"""Internal staff-console sessions (ADMIN-LOGIN-001).

Learner auth (mock/magic) is untouched. Staff sessions are
HMAC-signed bearer tokens prefixed `staff.` and keyed by
SESSION_SECRET. Credentials live ONLY in env vars — usernames in
ADMIN_CONSOLE_USERS, the password as ADMIN_CONSOLE_PASSWORD_SHA256
(hex). Plaintext is never stored, logged, or committed.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
import uuid
from typing import Optional

from backend.core.config import settings

STAFF_PREFIX = "staff."
TOKEN_TTL_SECONDS = 8 * 60 * 60  # 8h staff shift window

# Dedicated namespace for staff-session auth identities — distinct from
# the mock-auth namespace so a learner mock token can never collide.
_STAFF_NS = uuid.UUID("00000000-0000-0000-0000-000000000002")


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _unb64(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def _secret() -> bytes:
    return (settings.SESSION_SECRET or "").encode("utf-8")


def _sign(payload: bytes) -> str:
    return _b64(hmac.new(_secret(), payload, hashlib.sha256).digest())


def credentials_ok(username: str, password: str) -> bool:
    """Constant-time credential check. Fails closed on missing config."""
    users = {
        u.strip().lower()
        for u in (settings.ADMIN_CONSOLE_USERS or "").split(",")
        if u.strip()
    }
    expected = (settings.ADMIN_CONSOLE_PASSWORD_SHA256 or "").strip().lower()
    if not users or len(expected) != 64:
        return False
    name_ok = any(hmac.compare_digest(username.strip().lower(), u) for u in users)
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    pass_ok = hmac.compare_digest(digest, expected)
    return name_ok and pass_ok


def staff_auth_user_id(username: str) -> uuid.UUID:
    return uuid.uuid5(_STAFF_NS, f"admin:{username.strip().lower()}")


def issue_staff_token(username: str) -> Optional[str]:
    """Return `staff.<payload>.<sig>` or None when SESSION_SECRET unset."""
    if not _secret():
        return None
    payload = _b64(
        json.dumps(
            {
                "u": username.strip().lower(),
                "exp": int(time.time()) + TOKEN_TTL_SECONDS,
            },
            separators=(",", ":"),
        ).encode("utf-8")
    ).encode("ascii")
    return STAFF_PREFIX + payload.decode("ascii") + "." + _sign(payload)


def verify_staff_token(token: str) -> Optional[str]:
    """Return the staff username for a valid, unexpired token, else None."""
    if not _secret() or not isinstance(token, str):
        return None
    if not token.startswith(STAFF_PREFIX):
        return None
    body = token[len(STAFF_PREFIX) :]
    if "." not in body:
        return None
    payload_b64, sig = body.rsplit(".", 1)
    try:
        payload = _b64(_unb64(payload_b64))
    except Exception:
        return None
    if not hmac.compare_digest(_sign(payload.encode("ascii")), sig):
        return None
    try:
        claims = json.loads(_unb64(payload_b64))
    except Exception:
        return None
    exp = claims.get("exp")
    username = claims.get("u")
    if not isinstance(exp, int) or not isinstance(username, str):
        return None
    if exp < int(time.time()):
        return None
    users = {
        u.strip().lower()
        for u in (settings.ADMIN_CONSOLE_USERS or "").split(",")
        if u.strip()
    }
    if username.strip().lower() not in users:
        return None
    return username.strip().lower()


def staff_subject(authorization: Optional[str]) -> Optional[str]:
    """Parse `Authorization: Bearer staff.<…>` → username, else None."""
    if not authorization or not isinstance(authorization, str):
        return None
    parts = authorization.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return verify_staff_token(parts[1].strip())
