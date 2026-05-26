"""Identity provider abstraction.

See ADR 0023 (session model) and ADR 0024 (Clerk migration).

Implemented:
- MockAuthProvider: returns claims for any token of the form
  "mock:<email>". Used in dev and tests. Never enabled in production.
- ClerkAuthProvider: verifies Clerk-issued RS256 JWTs via JWKS, with
  caching and self-healing key-rotation retry.

Providers fail closed: any verification problem returns None rather
than raising. The caller treats None as 401 + envelope auth.signed_out.

The previous SupabaseAuthProvider (HS256 + project JWT secret) was
removed during decommission of Supabase-as-IdP. Supabase remains the
Postgres database; it is no longer an identity provider.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import Optional, Protocol

import httpx
from pybreaker import CircuitBreaker
from prometheus_client import Counter

from backend.core.config import settings

# Sprint 27 H3: shared circuit breaker for all Clerk Backend API calls.
# fail_max=5, reset_timeout=30s. Open state causes 503 degraded response.
_circuit_state_transitions = Counter(
    "noni_circuit_breaker_state_transitions_total",
    "Circuit breaker state transitions",
    ["service", "from_state", "to_state"],
)


class _ClerkCircuitListener:
    """Prometheus listener for Clerk circuit breaker state changes."""

    def state_change(self, cb, old_state, new_state):
        _circuit_state_transitions.labels(
            service="clerk",
            from_state=old_state.name,
            to_state=new_state.name,
        ).inc()
        logger.warning(
            "circuit_breaker.state_change",
            extra={
                "service": "clerk",
                "from_state": old_state.name,
                "to_state": new_state.name,
            },
        )


logger = logging.getLogger(__name__)

CLERK_CIRCUIT_BREAKER = CircuitBreaker(
    fail_max=5,
    reset_timeout=30,
    expected_exception=(httpx.HTTPError,),
    listeners=[_ClerkCircuitListener()],
)


@dataclass(frozen=True)
class AuthClaims:
    """Subset of identity-provider claims we depend on.

    `subject` is the provider-native subject (Clerk's `sub`, e.g.
    "user_2abc..."). It's distinct from `auth_user_id`, which is the
    UUID we hash that subject into so it fits accounts.auth_user_id.
    Carrying the raw subject lets `deps._upsert_account` look up the
    user's profile from Clerk's Backend API on first sight, since
    Clerk's default session token does NOT include an `email` claim
    (see clerk.com/docs/guides/sessions/session-tokens).
    """

    auth_user_id: uuid.UUID
    email: Optional[str] = None
    display_name: Optional[str] = None
    subject: Optional[str] = None


@dataclass(frozen=True)
class UserProfile:
    """User profile fields fetched from the provider's Backend API.

    Used to populate `accounts.email` (NOT NULL UNIQUE) on first sight
    when the verified credential didn't carry email itself.
    """

    email: str
    display_name: Optional[str] = None


class AuthProvider(Protocol):
    """Identity provider contract.

    Implementations must fail closed on any verification error and
    return None rather than raising for expected failures (expired
    token, bad signature, missing claim).

    `fetch_user_profile` is called on first-sight account creation when
    `verify_credential` returned an AuthClaims without `email` (the
    Clerk default-token case). Implementations that always return a
    fully-populated AuthClaims (e.g. MockAuthProvider) may return None.
    """

    def verify_credential(self, credential: str) -> Optional[AuthClaims]: ...

    def fetch_user_profile(self, subject: str) -> Optional[UserProfile]: ...


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
            subject=email,
        )

    def fetch_user_profile(self, subject: str) -> Optional[UserProfile]:
        """Mock claims always carry email; this should never be called.

        Returning None is safe — the caller treats it as a hard failure
        and 401s, which is the right answer if anyone ever does ask the
        mock for a profile (it would mean their AuthClaims is malformed).
        """
        return None


class ClerkAuthProvider:
    """Verifies Clerk-issued session JWTs (RS256) via JWKS.

    Clerk session tokens are short-lived (default 60s) RS256 JWTs signed
    by per-instance keys exposed at the JWKS URL. We verify:
      * signature (against the JWKS-published RSA public key),
      * `exp` (built-in, with leeway=0 to match Clerk's freshness model),
      * `iss` (the Clerk frontend-API host, if configured),
      * presence of `sub` (Clerk's user_id, e.g. "user_2abc...").

    `PyJWKClient` caches keys in-process and re-fetches when the kid in
    a token's header isn't in the cache — this provides the self-healing
    rotation behaviour Clerk expects without any extra plumbing on our
    side.

    Email and display name are NOT read from the JWT — Clerk's default
    session token does not include them (see
    clerk.com/docs/guides/sessions/session-tokens for the canonical
    claim list). Instead, `fetch_user_profile` looks up the user via
    Clerk's Backend API (`GET /v1/users/{user_id}` with
    `Authorization: Bearer $CLERK_SECRET_KEY`) on first-sight account
    creation. After the first lookup, `accounts.email` is cached on
    the row and subsequent requests verify the JWT only — no extra
    network call.

    Provider fails closed: any verification error logs the reason at
    INFO and returns None.
    """

    BACKEND_API_BASE = "https://api.clerk.com/v1"
    LOOKUP_TIMEOUT_SECONDS = 5.0

    def __init__(
        self,
        jwks_url: str,
        issuer: Optional[str],
        secret_key: Optional[str] = None,
    ) -> None:
        if not jwks_url:
            raise ValueError("ClerkAuthProvider requires CLERK_JWKS_URL to be set")
        self._jwks_url = jwks_url
        self._issuer = issuer or None
        self._secret_key = secret_key or None

    def verify_credential(self, credential: str) -> Optional[AuthClaims]:
        # Sprint 22 S1: delegated to shared ClerkVerifier.
        # Fail-closed logging lives in ClerkVerifier.verify().
        # Lazy import to break circular dependency:
        # clerk_verifier imports AuthClaims from this module.
        from backend.services.clerk_verifier import ClerkVerifier

        if not isinstance(credential, str) or not credential:
            return None
        verifier = ClerkVerifier(
            jwks_url=self._jwks_url,
            issuer=self._issuer,
        )
        return verifier.verify(credential)

    @CLERK_CIRCUIT_BREAKER
    def fetch_user_profile(self, subject: str) -> Optional[UserProfile]:
        """Fetch email + display name from Clerk's Backend API by user_id.

        Endpoint: GET https://api.clerk.com/v1/users/{user_id}
        Auth:     Authorization: Bearer $CLERK_SECRET_KEY
        Docs:     clerk.com/docs/reference/backend-api/tag/Users

        Picks the email matching `primary_email_address_id`, falling
        back to the first verified entry if the primary id isn't in the
        list (rare but possible after primary-email transitions).

        Fails closed: any non-200, network error, or missing email
        returns None. Caller treats None as 401.
        """
        if not self._secret_key:
            logger.info(
                "clerk_user_lookup_no_secret_key subject=%s",
                subject,
            )
            return None
        if not isinstance(subject, str) or not subject.strip():
            return None
        try:
            resp = httpx.get(
                f"{self.BACKEND_API_BASE}/users/{subject}",
                headers={"Authorization": f"Bearer {self._secret_key}"},
                timeout=self.LOOKUP_TIMEOUT_SECONDS,
            )
        except httpx.HTTPError as exc:
            logger.info(
                "clerk_user_lookup_failed: %s",
                exc.__class__.__name__,
            )
            return None
        if resp.status_code != 200:
            logger.info(
                "clerk_user_lookup_status=%d subject=%s",
                resp.status_code,
                subject,
            )
            return None
        try:
            data = resp.json()
        except ValueError:
            return None

        from backend.models.clerk_profile import ClerkUserProfile

        try:
            profile = ClerkUserProfile.model_validate(data)
        except Exception:
            logger.info("clerk_user_lookup_invalid_shape subject=%s", subject)
            return None

        email = profile.primary_email
        if email is None:
            logger.info("clerk_user_lookup_no_email subject=%s", subject)
            return None

        return UserProfile(
            email=email,
            display_name=profile.display_name,
        )


def get_auth_provider() -> AuthProvider:
    """Resolve the configured provider.

    AUTH_PROVIDER controls the selection:
      * "mock"   -> MockAuthProvider (dev/tests).
      * "clerk"  -> ClerkAuthProvider (production; requires CLERK_JWKS_URL).
      * anything else (e.g. legacy "supabase") -> ValueError on import-time
        access. We surface this as a hard failure so a misconfigured
        deployment cannot silently fall back to the mock provider.
    """
    provider = settings.AUTH_PROVIDER.strip().lower()
    if provider == "mock":
        return MockAuthProvider()
    if provider == "clerk":
        return ClerkAuthProvider(
            jwks_url=settings.CLERK_JWKS_URL,
            issuer=settings.CLERK_ISSUER or None,
            secret_key=settings.CLERK_SECRET_KEY or None,
        )
    raise ValueError(
        f"Unsupported AUTH_PROVIDER={settings.AUTH_PROVIDER!r}. "
        "Expected 'mock' or 'clerk'."
    )
