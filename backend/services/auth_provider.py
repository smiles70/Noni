"""Identity provider abstraction.

See ADR 0023, and ADR 0024 (Clerk migration, in progress).

Currently implemented:
- MockAuthProvider: returns claims for any token of the form
  "mock:<email>". Used in dev and tests. Never enabled in production.

Planned (session 2/3 of the Clerk migration):
- ClerkAuthProvider: verifies Clerk-issued RS256 JWTs via JWKS, with
  self-healing key-rotation retry. Lives in this same module.

Providers fail closed: any verification problem returns None rather
than raising. The caller treats None as 401 + envelope auth.signed_out.

The previous SupabaseAuthProvider (HS256 + project JWT secret) was
removed during decommission of Supabase-as-IdP. Supabase remains the
Postgres database; it is no longer an identity provider.
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


def get_auth_provider() -> AuthProvider:
    """Resolve the configured provider.

    During the Clerk migration this only returns the mock provider.
    Session 3 of the migration restores production behavior by adding
    a ClerkAuthProvider branch keyed on AUTH_PROVIDER="clerk".
    """
    return MockAuthProvider()
