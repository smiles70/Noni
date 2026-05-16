"""Test-suite environment defaults.

The Noni runtime container ships with `AUTH_PROVIDER=clerk` so the app
boots ready to verify real Clerk JWTs. The pytest suite, on the other
hand, uses the mock provider exclusively (`Bearer mock:<email>`); the
canonical Clerk JWT flow is covered by integration tests separately.

If a test process inherits `AUTH_PROVIDER=clerk` from the container env,
ClerkAuthProvider tries to RS256-verify a mock token and fails with
`DecodeError('Not enough segments')`. That manifests as every signed-in
test 401'ing, which is a confusing failure mode that has bitten us in
local Docker runs.

We pin the provider to "mock" at collection time so the test suite is
hermetic — independent of whatever the host shell or container env
happens to set. Clerk-specific values are blanked for the same reason
(`get_auth_provider` would otherwise raise if AUTH_PROVIDER=clerk and
CLERK_JWKS_URL=""). Tests that need the Clerk provider should override
these explicitly via monkeypatch.
"""

from __future__ import annotations

import os

# Must run before `backend.core.config.settings` is imported by any test
# module. Pytest evaluates conftest.py first per `testpaths`, so setting
# os.environ here is sufficient — pydantic-settings reads env at Settings()
# instantiation time, which happens lazily inside the app modules.
os.environ.setdefault("AUTH_PROVIDER", "mock")
os.environ["AUTH_PROVIDER"] = "mock"  # override even if container set "clerk"
os.environ.setdefault("CLERK_JWKS_URL", "")
os.environ.setdefault("CLERK_ISSUER", "")
os.environ.setdefault("CLERK_SECRET_KEY", "")
