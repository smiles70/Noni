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

import jwt
from jwt import (
    ExpiredSignatureError,
    InvalidIssuerError,
    InvalidTokenError,
    MissingRequiredClaimError,
    PyJWKClient,
    PyJWKClientError,
)

from backend.core.config import settings
from backend.services.auth_provider import AuthClaims

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
# ---------------------------------------------------------------------------


_MOCK_NAMESPACE = uuid.UUID("00000000-0000-0000-0000-000000000001")
_MOCK_PREFIX = "mock:"


def _verify_mock(token: str) -> AuthClaims:
    if not token.startswith(_MOCK_PREFIX):
        raise AuthError("auth.malformed")
    email = token[len(_MOCK_PREFIX) :].strip().lower()
    if not email or "@" not in email:
        raise AuthError("auth.malformed")
    return AuthClaims(
        auth_user_id=uuid.uuid5(_MOCK_NAMESPACE, email),
        email=email,
        display_name=None,
        subject=email,
    )


# ---------------------------------------------------------------------------
# Clerk provider verification (production).
#
# Inlined from the existing ClerkAuthProvider.verify_credential so each
# JWT/JWKS failure mode can be mapped to a distinct code. The legacy
# fail-closed-to-None method is preserved unchanged in auth_provider.py
# for the /auth/whoami path until the frontend cuts over.
# ---------------------------------------------------------------------------


_clerk_jwk_client: Optional[PyJWKClient] = None


def _get_clerk_jwk_client() -> PyJWKClient:
    global _clerk_jwk_client
    if _clerk_jwk_client is None:
        jwks_url = settings.CLERK_JWKS_URL
        if not jwks_url:
            # Misconfiguration — surface as transient so the FE shows a
            # banner rather than evicting the user. Ops will see the
            # log line and fix the config; user is not blamed.
            raise AuthError("auth.transient_verifier_unavailable")
        _clerk_jwk_client = PyJWKClient(jwks_url, cache_keys=True)
    return _clerk_jwk_client


def _verify_clerk(token: str) -> AuthClaims:
    try:
        client = _get_clerk_jwk_client()
        signing_key = client.get_signing_key_from_jwt(token)
    except AuthError:
        raise
    except PyJWKClientError as exc:
        # JWKS network failure or kid-not-found. Both are recoverable
        # from the user's perspective; the FE keeps the session and
        # shows a transient banner.
        logger.info("clerk_jwks_lookup_failed: %s", exc.__class__.__name__)
        raise AuthError("auth.transient_verifier_unavailable") from exc
    except Exception as exc:  # noqa: BLE001 - fail closed
        logger.info("clerk_jwks_unexpected: %s", exc.__class__.__name__)
        raise AuthError("auth.transient_verifier_unavailable") from exc

    issuer = settings.CLERK_ISSUER or None
    try:
        decoded = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=issuer,
            options={
                "require": ["exp", "sub", "iat"],
                "verify_aud": False,
            },
        )
    except ExpiredSignatureError as exc:
        raise AuthError("auth.expired") from exc
    except InvalidIssuerError as exc:
        raise AuthError("auth.issuer_mismatch") from exc
    except MissingRequiredClaimError as exc:
        # `exp`/`iat`/`sub` missing — treat absent sub as subject_missing,
        # absent timestamp claims as malformed (they should never reach
        # here from a real Clerk token).
        if getattr(exc, "claim", None) == "sub":
            raise AuthError("auth.subject_missing") from exc
        raise AuthError("auth.malformed") from exc
    except InvalidTokenError as exc:
        # Catch-all for the JWT library — signature failure, bad header,
        # unsupported alg, etc. We map to signature_invalid because
        # that's the most common case and the FE handling is the same
        # for any non-recoverable token error.
        raise AuthError("auth.signature_invalid") from exc

    sub = decoded.get("sub")
    if not isinstance(sub, str) or not sub:
        raise AuthError("auth.subject_missing")

    auth_user_id = uuid.uuid5(uuid.NAMESPACE_URL, f"clerk:{sub}")

    # Optional metadata. Email is best-effort: if present in a custom
    # session template we honour it; otherwise we leave it None and the
    # off-path ProviderProfileFetcher (Stage 3) will fill it later.
    email_candidate = (
        decoded.get("email")
        or decoded.get("primary_email")
        or decoded.get("email_address")
    )
    email = (
        email_candidate.strip().lower()
        if isinstance(email_candidate, str) and email_candidate.strip()
        else None
    )

    display_name = decoded.get("name")
    if not isinstance(display_name, str) or not display_name.strip():
        first = decoded.get("given_name") or decoded.get("first_name")
        last = decoded.get("family_name") or decoded.get("last_name")
        parts = [p for p in (first, last) if isinstance(p, str) and p.strip()]
        display_name = " ".join(parts) if parts else None

    return AuthClaims(
        auth_user_id=auth_user_id,
        email=email,
        display_name=display_name,
        subject=sub,
    )


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
    provider = settings.AUTH_PROVIDER.strip().lower()
    if provider == "mock":
        return _verify_mock(token)
    if provider == "clerk":
        return _verify_clerk(token)
    # Misconfiguration; surface as transient so users aren't blamed.
    logger.error("unsupported_auth_provider: %r", provider)
    raise AuthError("auth.transient_verifier_unavailable")
