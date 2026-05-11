"""Identity provider abstraction.

See ADR 0023.

Two concrete providers:
- MockAuthProvider: returns claims for any token of the form
  "mock:<email>". Used in dev and tests. Never enabled in production.
- SupabaseAuthProvider: verifies a Supabase-issued JWT against the
  Supabase JWKS endpoint. Stub: full implementation lands when we
  provision the Supabase project (Phase B).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional, Protocol


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
    """Verifies Supabase JWTs against the project JWKS.

    Phase A stub: production wiring lands in B3 / B4 once SUPABASE_URL
    and SUPABASE_JWT_SECRET are present. Until then this class fails
    closed for every request.
    """

    def verify_credential(self, credential: str) -> Optional[AuthClaims]:
        # Intentionally returns None until full implementation lands.
        return None


def get_auth_provider() -> AuthProvider:
    """Resolve the configured provider. Defaults to mock in dev/tests."""
    from backend.core.config import settings

    if settings.AUTH_PROVIDER == "supabase":
        return SupabaseAuthProvider()
    return MockAuthProvider()
