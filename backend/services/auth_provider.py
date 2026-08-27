"""Identity provider abstraction.

See ADR 0023 (session model) and ADR 0027 (Magic.link provider).

Implemented:
- MockAuthProvider: returns claims for any token of the form
  "mock:<email>". Used in dev and tests. Never enabled in production.
- MagicAuthProvider: validates Magic.link DID tokens and fetches user
  metadata for account materialisation.

Providers fail closed: any verification problem returns None rather
than raising. The caller treats None as 401 + envelope auth.signed_out.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional, Protocol

from backend.services.magic_verifier import (
    MAGIC_NAMESPACE,
    fetch_user_profile_by_token,
    validate_did_token,
)
from backend.services.mock_parser import MOCK_NAMESPACE, MOCK_PREFIX, parse_mock_token


@dataclass(frozen=True)
class AuthClaims:
    """Subset of identity-provider claims we depend on."""

    auth_user_id: uuid.UUID
    email: Optional[str] = None
    display_name: Optional[str] = None
    subject: Optional[str] = None


@dataclass(frozen=True)
class UserProfile:
    """User profile fields fetched from the provider's Backend API."""

    email: str
    display_name: Optional[str] = None


class AuthProvider(Protocol):
    """Identity provider contract.

    Implementations must fail closed on any verification error and
    return None rather than raising for expected failures.
    """

    def verify_credential(self, credential: str) -> Optional[AuthClaims]: ...

    def fetch_user_profile(
        self, subject: str, credential: Optional[str] = None
    ) -> Optional[UserProfile]: ...


class MockAuthProvider:
    """Accepts credentials of the form 'mock:<email>'.

    Dev / test only. The auth_user_id is deterministically derived from
    the email so repeated logins for the same email reuse the same
    `accounts.auth_user_id`, mirroring real provider behavior.
    """

    NAMESPACE = MOCK_NAMESPACE
    PREFIX = MOCK_PREFIX

    def verify_credential(self, credential: str) -> Optional[AuthClaims]:
        email = parse_mock_token(credential)
        if email is None:
            return None
        return AuthClaims(
            auth_user_id=uuid.uuid5(self.NAMESPACE, email),
            email=email,
            display_name=None,
            subject=email,
        )

    def fetch_user_profile(
        self, subject: str, credential: Optional[str] = None
    ) -> Optional[UserProfile]:
        """Mock claims always carry email; this should never be called."""
        return None


class MagicAuthProvider:
    """Validates Magic.link DID tokens and fetches user metadata.

    The DID token is cryptographically validated locally. User metadata
    (email) is fetched from the Magic API only when needed for account
    materialisation (B4: no network calls on the pure read path).
    """

    def verify_credential(self, credential: str) -> Optional[AuthClaims]:
        claim = validate_did_token(credential)
        if claim is None:
            return None

        sub = claim.get("sub")
        if not sub:
            return None

        return AuthClaims(
            auth_user_id=uuid.uuid5(MAGIC_NAMESPACE, sub),
            email=None,
            display_name=None,
            subject=sub,
        )

    def fetch_user_profile(
        self, subject: str, credential: Optional[str] = None
    ) -> Optional[UserProfile]:
        if not credential:
            return None
        data = fetch_user_profile_by_token(credential)
        if data is None:
            return None
        email = data.get("email")
        if not email or not isinstance(email, str):
            return None
        return UserProfile(
            email=email,
            display_name=data.get("display_name") or None,
        )


def get_auth_provider() -> AuthProvider:
    """Return the configured identity provider.

    See ADR 0027. MagicAuthProvider is available when `AUTH_PROVIDER=magic`.
    """
    from backend.core.config import settings

    provider = settings.AUTH_PROVIDER.strip().lower()
    if provider == "mock":
        return MockAuthProvider()
    if provider == "magic":
        return MagicAuthProvider()
    raise RuntimeError(f"Unsupported AUTH_PROVIDER: {provider!r}")
