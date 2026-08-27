"""Stage 2 — pure, discriminated token verification (B4, B5, B11, C3).

Source:
    docs/design/login-redesign-2026-05-17.md §2.3 (verification path).
    docs/audits/login-system-constraints-2026-05-17.md §3.4, §8.1.
    Frozen reference tag: login-redesign-v1.

Constraints anchored:
    B4   no DB writes on a read; verifier touches no DB.
    B5   401 outcomes carry a discriminated `code` (see CODES below).
    B11  no optional-secret dependency on the success path.
    C3   four orthogonal owners: provider verifies a token, DB lookup
         resolves a row, materializer writes a row, profile fetcher
         (off-path background) fills optional metadata.

This module uses the AuthProvider abstraction's `verify_credential`
where appropriate, but the new `verify_token` raises `AuthError` with
a discriminated `code` so route handlers can emit a structured 401
envelope `{error:{code,message}}`.
"""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from backend.core.config import settings
from backend.services.auth_provider import AuthClaims
from backend.services.mock_parser import MOCK_NAMESPACE, parse_mock_token

logger = logging.getLogger("noni.auth_verifier")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


CODES = frozenset(
    {
        "auth.no_credential",
        "auth.malformed",
        "auth.signature_invalid",
        "auth.expired",
        "auth.issuer_mismatch",
        "auth.subject_missing",
        "auth.transient_verifier_unavailable",
        "auth.account_deleted",
        "auth.transient_db_unavailable",
    }
)


class AuthError(Exception):
    """Discriminated authentication failure (B5, R1)."""

    def __init__(self, code: str, message: Optional[str] = None) -> None:
        if code not in CODES:
            raise ValueError(f"Unknown AuthError code: {code!r}")
        self.code = code
        self.message = message or _default_message(code)
        super().__init__(self.message)


def _default_message(code: str) -> str:
    return {
        "auth.no_credential": "No credential presented.",
        "auth.malformed": "Credential is malformed.",
        "auth.signature_invalid": "Credential signature is invalid.",
        "auth.expired": "Credential has expired.",
        "auth.issuer_mismatch": "Credential issuer is not trusted.",
        "auth.subject_missing": "Credential is missing a subject claim.",
        "auth.transient_verifier_unavailable": (
            "Identity provider verification is temporarily unavailable."
        ),
        "auth.account_deleted": "Account has been deleted.",
        "auth.transient_db_unavailable": "Account store is temporarily unavailable.",
    }[code]


def parse_bearer(authorization: Optional[str]) -> Optional[str]:
    """Extract the token from `Authorization: Bearer <token>`."""
    if not authorization or not isinstance(authorization, str):
        return None
    parts = authorization.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    token = parts[1].strip()
    return token or None


def _verify_mock(token: str) -> AuthClaims:
    email = parse_mock_token(token)
    if email is None:
        raise AuthError("auth.malformed")
    return AuthClaims(
        auth_user_id=uuid.uuid5(MOCK_NAMESPACE, email),
        email=email,
        display_name=None,
        subject=email,
    )


def _verify_magic(token: str) -> AuthClaims:
    from backend.services.auth_provider import get_auth_provider

    provider = get_auth_provider()
    claims = provider.verify_credential(token)
    if claims is None:
        raise AuthError("auth.signature_invalid")
    return claims


def verify_token(token: Optional[str]) -> AuthClaims:
    """Verify a Bearer token and return AuthClaims (B4, B5, B11, C3).

    Raises:
        AuthError: on any verification failure. `error.code` is one of
            CODES; the route handler emits it via
            `record_auth_session_outcome` and serialises it into the
            response envelope `{"error": {"code": ..., "message": ...}}`.

    Never touches the database.
    """
    if token is None or not token:
        raise AuthError("auth.no_credential")
    provider = settings.AUTH_PROVIDER.strip().lower()
    if provider == "mock":
        return _verify_mock(token)
    if provider == "magic":
        return _verify_magic(token)
    logger.error("unsupported_auth_provider: %r", provider)
    raise AuthError("auth.transient_verifier_unavailable")
