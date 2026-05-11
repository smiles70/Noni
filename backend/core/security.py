"""Cryptographic helpers for sessions and cookies.

See ADR 0023.

Design notes:
- Session cookie values are 32-byte random tokens, base64-urlsafe encoded.
- We sign the cookie value with HMAC-SHA256 keyed by SESSION_SECRET so a
  tampered cookie is rejected before any DB lookup.
- Server-side we store only the SHA-256 hash of the raw token; the
  signature suffix is verified-then-stripped before hashing.

Cookie format: "<raw_token>.<base64_hmac>"
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from typing import Tuple

from backend.core.config import settings


def _secret_bytes() -> bytes:
    return settings.SESSION_SECRET.encode("utf-8")


def generate_session_token() -> Tuple[str, str, str]:
    """Generate (raw_token, signed_cookie_value, token_hash).

    Returns:
        raw_token: opaque 32-byte token (base64-urlsafe, no padding)
        signed_cookie_value: "<raw_token>.<sig>" suitable for Set-Cookie
        token_hash: hex SHA-256 of raw_token; the value to persist in DB
    """
    raw = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode("ascii")
    sig = _sign(raw)
    token_hash = hashlib.sha256(raw.encode("ascii")).hexdigest()
    return raw, f"{raw}.{sig}", token_hash


def verify_session_cookie(cookie_value: str) -> str | None:
    """Verify a signed cookie value and return the SHA-256 hash of the
    raw token (the value stored in the sessions table).

    Returns None on any verification failure (missing signature,
    constant-time mismatch, malformed input). Callers MUST fail closed.
    """
    if not cookie_value or "." not in cookie_value:
        return None
    raw, _, sig = cookie_value.rpartition(".")
    if not raw or not sig:
        return None
    expected = _sign(raw)
    if not hmac.compare_digest(sig, expected):
        return None
    return hashlib.sha256(raw.encode("ascii")).hexdigest()


def _sign(message: str) -> str:
    mac = hmac.new(_secret_bytes(), message.encode("ascii"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac).rstrip(b"=").decode("ascii")
