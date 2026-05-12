"""Identity provider abstraction.

See ADR 0023.

Two concrete providers:
- MockAuthProvider: returns claims for any token of the form
  "mock:<email>". Used in dev and tests. Never enabled in production.
- SupabaseAuthProvider: verifies a Supabase-issued JWT (HS256, signed
  with the project's JWT secret). Sprint B2 wired this up; previously
  a closed-by-default stub.

Both providers fail closed: any verification problem returns None rather
than raising. The caller treats None as 401 + envelope auth.signed_out.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import Optional, Protocol

import jwt
from jwt import InvalidTokenError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AuthClaims:
    """Subset of identity-provider claims we depend on."""

    auth_user_id: uuid.UUID
    email: str
    display_name: Optional[str] = None


class AuthProvider(Protocol):
    """Identity provider contract.

    Implementations must fail closed on any verification error and
    return None rather than raising for expected failures (expired
    token, bad signature, missing claim).
    """

    def verify_credential(self, credential: str) -> Optional[AuthClaims]: ...


class MockAuthProvider:
    """Accepts credentials of the form 'mock:<email>'.

    Dev / test only. The auth_user_id is deterministically derived from
    the email so repeated logins for the same email reuse the same
    `accounts.auth_user_id`, mirroring real provider behavior.
    """

    NAMESPACE = uuid.UUID("00000000-0000-0000-0000-000000000001")
    PREFIX = "mock:"

    def verify_credential(self, credential: str) -> Optional[AuthClaims]:
        if not isinstance(credential, str) or not credential.startswith(self.PREFIX):
            return None
        email = credential[len(self.PREFIX) :].strip().lower()
        if not email or "@" not in email:
            return None
        return AuthClaims(
            auth_user_id=uuid.uuid5(self.NAMESPACE, email),
            email=email,
            display_name=None,
        )


class SupabaseAuthProvider:
    """Verifies Supabase-issued JWTs (HS256, project JWT secret).

    Supabase access tokens are JWTs signed with HS256 using the project's
    `JWT secret` (project Settings -> API -> JWT Settings). We verify:
      - signature  : HS256 against the configured secret
      - expiry     : `exp` claim (PyJWT enforces by default)
      - audience   : `aud` claim must match SUPABASE_JWT_AUDIENCE
      - issuer     : `iss` claim must match SUPABASE_JWT_ISSUER if set
      - shape      : `sub` (UUID) and `email` must be present and well-formed

    Any failure returns None. The auth route then returns 401 with the
    `auth.signed_out` envelope id; the user sees the same outcome whether
    the token was expired, tampered with, or simply not a Supabase token.

    `display_name` comes from the optional `user_metadata.full_name` claim
    (set by the OAuth provider, e.g. Google). It is not used for auth.
    """

    def __init__(
        self,
        jwt_secret: str,
        *,
        audience: str = "authenticated",
        issuer: Optional[str] = None,
    ) -> None:
        if not jwt_secret:
            raise ValueError(
                "SupabaseAuthProvider requires a non-empty JWT secret. "
                "Set SUPABASE_JWT_SECRET in the environment.",
            )
        self._jwt_secret = jwt_secret
        self._audience = audience
        self._issuer = issuer or None  # empty string -> skip issuer check

    def verify_credential(self, credential: str) -> Optional[AuthClaims]:
        if not isinstance(credential, str) or not credential:
            return None

        try:
            options = {"require": ["exp", "sub", "aud"]}
            decoded = jwt.decode(
                credential,
                self._jwt_secret,
                algorithms=["HS256"],
                audience=self._audience,
                issuer=self._issuer if self._issuer else None,
                options=options,
            )
        except InvalidTokenError as exc:
            # Includes ExpiredSignatureError, InvalidAudienceError,
            # InvalidIssuerError, InvalidSignatureError, DecodeError,
            # MissingRequiredClaimError.
            logger.info("supabase_jwt_rejected: %s", exc.__class__.__name__)
            return None

        sub = decoded.get("sub")
        email = decoded.get("email")
        if not isinstance(sub, str) or not isinstance(email, str):
            return None
        email = email.strip().lower()
        if "@" not in email:
            return None

        try:
            auth_user_id = uuid.UUID(sub)
        except (ValueError, TypeError):
            return None

        display_name: Optional[str] = None
        meta = decoded.get("user_metadata")
        if isinstance(meta, dict):
            candidate = meta.get("full_name") or meta.get("name")
            if isinstance(candidate, str) and candidate.strip():
                display_name = candidate.strip()

        return AuthClaims(
            auth_user_id=auth_user_id,
            email=email,
            display_name=display_name,
        )


def get_auth_provider() -> AuthProvider:
    """Resolve the configured provider. Defaults to mock in dev/tests."""
    from backend.core.config import settings

    if settings.AUTH_PROVIDER == "supabase":
        return SupabaseAuthProvider(
            jwt_secret=settings.SUPABASE_JWT_SECRET,
            audience=settings.SUPABASE_JWT_AUDIENCE or "authenticated",
            issuer=settings.SUPABASE_JWT_ISSUER or None,
        )
    return MockAuthProvider()
