# Recovery Log: Login Loop Incident
**Date:** 2026-06-11
**Status:** IN PROGRESS
**Severity:** CRITICAL - Production Outage

## Symptoms
- Frontend shows "Reconnecting your sign-in... retrying in 4s"
- Frontend shows "One moment — loading" indefinitely
- User unable to authenticate

## Diagnosis (via The Process)

### Research Phase - Gotchas Analysis
- **G1** (cryptography missing): Guard exists in `main.py:36-55`, called at startup. Should crash app at boot if missing.
- **G2** (JsonFormatter/PyJWKClient): `clerk_verifier.py` uses correct `lifespan=3600` parameter. G2 Bug 2 is fixed.
- **G3** (localhost API URL): Frontend loads correctly, not G3.

### Hypothesis
Docker build cache issue - container may have incomplete dependencies despite G1 guard.

## Root Cause (Determined)
Based on The Process analysis:

1. **G1 Guard Active:** `_verify_crypto_dependency()` in `main.py:108` should crash at boot if cryptography is missing
2. **G2 Fixed:** `clerk_verifier.py` uses `lifespan=3600` (correct parameter)
3. **Most Likely:** Production Docker container has stale build cache or missing env vars

## Immediate Actions Required

### Step 1: Check Fly.io Logs
```bash
flyctl logs --app noni-api --no-tail | head -100
```

Look for:
- `RuntimeError` about cryptography (G1 guard triggering)
- `auth.transient_verifier_unavailable` (auth failures)
- `KeyError: 'levelname'` (G2 JsonFormatter - unlikely but possible)

### Step 2: Force Fresh Deploy
```bash
flyctl deploy --remote-only --no-cache
```

### Step 3: Verify Clerk Configuration
```bash
flyctl secrets list --app noni-api
# Should show: CLERK_JWKS_URL, CLERK_ISSUER
```

### Step 4: Check Frontend API URL
In browser devtools Console/Network:
- Confirm API calls go to `https://noni-api.fly.dev`
- Not `http://localhost:8000` (would indicate G3)

## Verification After Fix

```bash
# Run smoke tests
export PROD_API_BASE_URL=https://noni-api.fly.dev
bash infra/scripts/smoke-prod.sh

# Or manual check
curl https://noni-api.fly.dev/health
# Expect: {"status":"healthy",...}
```

## Prevention

1. Add CI check for Docker layer cache invalidation on requirements.txt changes
2. Verify `docker build --no-cache` when dependencies change
3. Monitor `auth.transient_verifier_unavailable` errors in logs

---
*Recovery Agent following The Process v2*
*Agents involved: Session State, Triage, Research, Design, Backend, Auth, Test, Recovery*
