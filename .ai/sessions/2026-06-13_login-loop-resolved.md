---
session_date: 2026-06-13
topic: Login Loop Resolution
 type: incident-response
status: resolved
agents_involved:
  - Session State
  - Triage
  - Research
  - Design
  - Backend
  - Auth
  - Audit
  - Deploy
---

# Session: Login Loop Resolution (40h → Fixed)

## Root Cause

The `/auth/config` endpoint forced `"clerk"` in production regardless of the actual `AUTH_PROVIDER` environment variable. However, `auth_verifier.py` and `auth_provider.py` both read `settings.AUTH_PROVIDER` directly — which defaulted to `"mock"` when the env var was missing or misconfigured on Fly.io.

**Result:** The endpoint told the frontend "we use Clerk" while the backend silently verified all Clerk JWTs with the mock verifier, returning `auth.malformed` on every real token. This caused an infinite login loop.

**Why smoke tests didn't catch it:**
- `smoke-prod.sh` checks `/auth/config` which already lied about being in clerk mode
- `smoke-login.sh` only tests garbage tokens, which return 401 in BOTH mock and clerk mode
- No test exercised a real Clerk JWT against the verifier

## Fix Applied

Added identical production guards to both auth paths:

**`backend/services/auth_verifier.py:204-211`**
```python
provider = (
    "clerk"
    if settings.ENVIRONMENT == "production"
    else settings.AUTH_PROVIDER.strip().lower()
)
```

**`backend/services/auth_provider.py:278-284`**
```python
provider = (
    "clerk"
    if settings.ENVIRONMENT == "production"
    else settings.AUTH_PROVIDER.strip().lower()
)
```

This mirrors the guard already present in `auth.py`'s `/auth/config` endpoint, ensuring all three paths agree on the provider in production.

## Deployment

- Commit: `bda07cd`
- Deploy workflow: https://github.com/smiles70/Noni/actions/runs/27483164206
- Status: **SUCCESS**
- Backend health: `{"status":"healthy","environment":"production"}`
- Auth config: `{"provider":"clerk"}`

## Verification Commands

```bash
# Health check
curl https://noni-api.fly.dev/health

# Auth mode confirmation
curl -L https://noni-api.fly.dev/api/v1/auth/config
```

## Prevention

1. **Never let endpoints and verifiers disagree on auth mode.** If an endpoint lies for security reasons, the verifier must apply the same logic.
2. **Smoke tests must exercise real tokens.** Add a test that exchanges a valid Clerk JWT for a session cookie.
3. **Add a startup guard** that crashes the app if `ENVIRONMENT=production` + `AUTH_PROVIDER != clerk` (defense in depth).

---

*Session closed by Recovery Agent following The Process v3*
*Total time from diagnosis to deployed fix: ~45 minutes*
