"""Shared Clerk JWT verification.

Sprint 22 S1: extracted from auth_provider.py and auth_verifier.py to
eliminate duplication. Both consumers import from this single source.

The class provides two surfaces:
  - `verify(token)`   -> fail-closed (returns None on any error).
  - `verify_strict(token)` -> raises jwt.* exceptions so callers can
    map them to discriminated error codes.
"""

from __future__ import annotations

import logging
import uuid
from typing import Optional

import jwt
from jwt import InvalidTokenError, PyJWKClient, PyJWKClientError

from backend.services.auth_provider import AuthClaims

logger = logging.getLogger("noni.clerk_verifier")


class ClerkVerifier:
    """Verifies Clerk-issued session JWTs (RS256) via JWKS.

    PyJWKClient caches keys in-process and re-fetches on kid rotation.
    """

    def __init__(self, jwks_url: str, issuer: Optional[str] = None) -> None:
        if not jwks_url:
            raise ValueError("ClerkVerifier requires a JWKS URL")
        # Sprint 27 Q3: cache_ttl=3600 forces re-fetch every hour so JWKS
        # rotation is picked up even if the old key remains valid.
        self._jwk_client = PyJWKClient(jwks_url, cache_keys=True, cache_ttl=3600)
        self._issuer = issuer or None

    def verify(self, token: str) -> Optional[AuthClaims]:
        """Fail-closed verification. Returns None on any error."""
        try:
            return self.verify_strict(token)
        except PyJWKClientError as exc:
            logger.info("clerk_jwks_lookup_failed: %s", exc.__class__.__name__)
            return None
        except InvalidTokenError as exc:
            logger.info("clerk_jwt_rejected: %s", exc.__class__.__name__)
            return None
        except Exception as exc:  # noqa: BLE001
            logger.info("clerk_jwks_unexpected_error: %s", exc.__class__.__name__)
            return None

    def verify_strict(self, token: str) -> AuthClaims:
        """Verify and return claims. Raises jwt.* exceptions on failure.

        Callers (e.g. auth_verifier) catch specific exceptions and map
        them to discriminated AuthError codes.

        Sprint 27 Q3 fix: stale-while-revalidate. If kid not found in cache,
        force a JWKS refetch and retry once before failing.
        """
        try:
            signing_key = self._jwk_client.get_signing_key_from_jwt(token)
        except PyJWKClientError:
            # Force cache refresh and retry once
            self._jwk_client = PyJWKClient(
                self._jwk_client.uri,
                cache_keys=True,
                cache_ttl=3600,
            )
            signing_key = self._jwk_client.get_signing_key_from_jwt(token)
        decoded = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=self._issuer if self._issuer else None,
            options={
                "require": ["exp", "sub", "iat"],
                "verify_aud": False,
            },
        )
        return _extract_claims(decoded)


def _extract_claims(decoded: dict) -> AuthClaims:
    """Extract AuthClaims from a decoded Clerk JWT payload."""
    sub = decoded.get("sub")
    if not isinstance(sub, str) or not sub:
        raise jwt.InvalidTokenError("missing sub claim")

    auth_user_id = uuid.uuid5(uuid.NAMESPACE_URL, f"clerk:{sub}")

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
