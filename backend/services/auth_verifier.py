"""Stage 2 — pure, discriminated token verification (B4, B5, B11, C3).

Source:
    docs/design/login-redesign-2026-05-17.md §2.3 (verification path).
    docs/audits/login-system-constraints-2026-05-17.md §3.4, §8.1.
    Frozen reference tag: login-redesign-v1.

Constraints anchored:
    B4   no DB writes on a read; verifier touches no DB.
    B5   401 outcomes carry a discriminated `code` (see CODES below).
    B11  no optional-secret dependency on the success path; no Clerk
         Backend API call here.
    C3   four orthogonal owners: provider verifies a token, DB lookup
         resolves a row, materializer writes a row, profile fetcher
         (off-path background) fills optional metadata.

This module deliberately does NOT use the existing AuthProvider
abstraction's `verify_credential(credential) -> Optional[AuthClaims]`
because that surface squashes every failure into None. The new
`verify_token` raises `AuthError` with a discriminated `code`, which
the route handler emits via `record_auth_session_outcome` and
serialises into the response envelope `{error:{code,message}}`.

The legacy `get_optional_account` path (used by /auth/whoami) is
unchanged so existing surfaces keep working until the frontend cuts
over.
"""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from jwt import (
    ExpiredSignatureError,
    InvalidIssuerError,
    InvalidTokenError,
    MissingRequiredClaimError,
    PyJWKClientError,
)

from backend.core.config import settings
from backend.services.auth_provider import AuthClaims
from backend.services.clerk_verifier import ClerkVerifier
from backend.services.mock_parser import MOCK_NAMESPACE, parse_mock_token

logger = logging.getLogger("noni.auth_verifier")
# Surface verifier failure modes (e.g. clerk_jwks_lookup_failed) under
# uvicorn's default log config; mirrors the dedicated handler on
# noni.telemetry. INFO-level so failure reasons appear without raising
# the bar for everything else.
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


# Discriminated reason codes. The set is closed: every code that can
# appear in an /auth/session* 401 envelope is enumerated here so the
# frontend classifier (DEFINITIVE / TRANSIENT / SIGNED_OUT) is total.
CODES = frozenset(
    {
        "auth.no_credential",
        "auth.malformed",
        "auth.signature_invalid",
        "auth.expired",
        "auth.issuer_mismatch",
        "auth.subject_missing",
        "auth.transient_verifier_unavailable",
        # Materializer-emitted; lives in this set so the FE classifier
        # is total across every AuthError that can reach a response.
        "auth.account_deleted",
        "auth.transient_db_unavailable",
    }
)


class AuthError(Exception):
    """Discriminated authentication failure (B5, R1).

    `code` is one of CODES. `message` is short, human-readable, and
    safe to surface in the response (no token bytes, no header values,
    no PII — B10).
    """

    def __init__(self, code: str, message: Optional[str] = None) -> None:
        if code not in CODES:
            # Defensive: any new code must be added to CODES so the FE
            # classifier stays total. Fail loud in dev/tests.
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
        "auth.transient_db_unavailable": ("Account store is temporarily unavailable."),
    }[code]


def parse_bearer(authorization: Optional[str]) -> Optional[str]:
    """Extract the token from `Authorization: Bearer <token>`.

    Returns None for any malformed input. Never logs the header value
    (B10): unlike `backend.api.deps._parse_bearer`, this function does
    not print or log any prefix of the credential.
    """
    if not authorization or not isinstance(authorization, str):
        return None
    parts = authorization.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    token = parts[1].strip()
    return token or None


# ---------------------------------------------------------------------------
# Mock provider verification (dev/tests).
# Sprint '2nd Safe Yellow' P13: delegated to shared mock_parser.
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Clerk provider verification (production).
#
# Sprint 22 S1: delegated to shared ClerkVerifier. Discriminated error
# mapping is preserved here; the shared class raises raw jwt exceptions.
# ---------------------------------------------------------------------------


def _verify_clerk(token: str) -> AuthClaims:
    jwks_url = settings.CLERK_JWKS_URL
    if not jwks_url:
        raise AuthError("auth.transient_verifier_unavailable")
    verifier = ClerkVerifier(
        jwks_url=jwks_url,
        issuer=settings.CLERK_ISSUER or None,
    )
    try:
        return verifier.verify_strict(token)
    except PyJWKClientError as exc:
        logger.info("clerk_jwks_lookup_failed: %s", exc.__class__.__name__)
        raise AuthError("auth.transient_verifier_unavailable") from exc
    except ExpiredSignatureError as exc:
        raise AuthError("auth.expired") from exc
    except InvalidIssuerError as exc:
        raise AuthError("auth.issuer_mismatch") from exc
    except MissingRequiredClaimError as exc:
        if getattr(exc, "claim", None) == "sub":
            raise AuthError("auth.subject_missing") from exc
        raise AuthError("auth.malformed") from exc
    except InvalidTokenError as exc:
        raise AuthError("auth.signature_invalid") from exc
    except Exception as exc:  # noqa: BLE001
        logger.info("clerk_jwks_unexpected: %s", exc.__class__.__name__)
        raise AuthError("auth.transient_verifier_unavailable") from exc


# ---------------------------------------------------------------------------
# Public entry point.
# ---------------------------------------------------------------------------


def verify_token(token: Optional[str]) -> AuthClaims:
    """Verify a Bearer token and return AuthClaims (B4, B5, B11, C3).

    Raises:
        AuthError: on any verification failure. `error.code` is one of
            CODES; the route handler emits it via
            `record_auth_session_outcome` and serialises it into the
            response envelope `{"error": {"code": ..., "message": ...}}`.

    Never touches the database; never calls the identity provider's
    Backend API.
    """
    if token is None or not token:
        raise AuthError("auth.no_credential")
    # Sprint 22 S7: production must never silently fall back to mock auth.
    # The /auth/config endpoint already enforces this; the verifier must
    # match exactly so the two never desync (recovery 2026-06-13).
    provider = (
        "clerk"
        if settings.ENVIRONMENT == "production"
        else settings.AUTH_PROVIDER.strip().lower()
    )
    if provider == "mock":
        return _verify_mock(token)
    if provider == "clerk":
        return _verify_clerk(token)
    # Misconfiguration; surface as transient so users aren't blamed.
    logger.error("unsupported_auth_provider: %r", provider)
    raise AuthError("auth.transient_verifier_unavailable")
