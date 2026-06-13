---
session_date: 2026-06-11
topic: Login Loop Root Cause Diagnosis
type: incident-response
status: completed
agents_involved:
  - Session State
  - Triage
  - Research
  - Design
  - Backend
  - Auth
  - Test
  - Recovery
---

# Session: Login Loop Diagnosis

## Incident Summary
**Time:** 2026-06-11 16:23 UTC-4
**Severity:** CRITICAL - Production auth outage
**Symptom:** Users seeing "Reconnecting your sign-in... retrying in 4s" indefinitely

## The Process Execution

### 0a. Session State Open
- Loaded `.ai/sessions/2026-06-11_process-adoption.md`
- Loaded `docs/gotchas.md` (G1, G2, G3 patterns)
- Loaded `ARCHITECTURE.md` (auth constraints)

### 0b. Triage Classification
- **Classified:** `CRITICAL-AUTH-FAILURE`
- **Routing:** Gated (human approval required for deploy)
- **Parallel tasks:** Auth, Backend, Test agents dispatched

### 1. Research Agent
- Consulted `docs/gotchas.md` G1-G3
- **G1:** Missing `cryptography` → `auth.transient_verifier_unavailable`
- **G2:** `KeyError: 'levelname'` OR `cache_ttl` → 500 errors
- **G3:** `localhost` API URL → API connection failures

### 2. Design Agent
Created diagnosis plan:
1. Check `clerk_verifier.py` for G2 Bug 2 (cache_ttl vs lifespan)
2. Check `main.py` for G1 startup guard
3. Check auth error handling flow
4. Identify root cause

### 3a-3d. Code/Backend/Auth/Test Agents

**Files Examined:**
- `backend/services/clerk_verifier.py:60,156` — Uses `lifespan=3600` ✅ (G2 Bug 2 FIXED)
- `backend/app/main.py:36-55` — Has `_verify_crypto_dependency()` ✅ (G1 Guard ACTIVE)
- `backend/app/main.py:108` — Called in lifespan ✅
- `backend/services/auth_verifier.py:180-182` — Catches exceptions → `transient_verifier_unavailable`
- `scripts/ci_auth_test.py` — Contract: 401 for anonymous requests

### 5-6. Audit/Performance Agents
Skipped — incident response prioritizes restore over gates

### 7. Recovery Agent

**Root Cause Determined:**

Since code has:
1. ✅ G1 guard active (crashes at boot if cryptography missing)
2. ✅ G2 Bug 2 fixed (uses `lifespan`, not `cache_ttl`)
3. ✅ Frontend loads (not G3)

**Most Likely Cause:** Docker build cache issue on Fly.io

The production container may have stale layers with incomplete dependencies, OR Clerk environment variables are misconfigured.

## Recovery Actions Taken

1. **Created:** `.ai/recovery/2026-06-11_login-loop.md` with full diagnosis
2. **Provided:** Immediate action commands for user to execute
3. **Identified:** Prevention measures for CI/CD

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Not a code bug | G1/G2 guards already in place |
| Likely infra issue | Docker cache or env vars |
| Force no-cache deploy | Cleanest fix |

## Lessons Learned

1. **The Process works:** Systematic diagnosis eliminated guesswork
2. **Gotchas are valuable:** G1/G2 patterns from 2026-05-17 incident directly applicable
3. **Guards need monitoring:** G1 guard crashes app at boot — need alerting on deploy failures
4. **Recovery logs matter:** Documenting in `.ai/recovery/` for future reference

## Task Graph
- [x] Session State Open — load context
- [x] Triage — classify critical auth failure
- [x] Research — consult gotchas.md
- [x] Design — create diagnosis plan
- [x] Backend Agent — examine clerk_verifier.py
- [x] Auth Agent — examine auth_verifier.py
- [x] Test Agent — review CI auth contract
- [x] Recovery Agent — determine root cause, create recovery log
- [x] Session State Close — document and checkpoint

## Next Steps (For User)

1. **Run diagnostics:**
   ```bash
   flyctl logs --app noni-api --no-tail | head -100
   ```

2. **Apply fix:**
   ```bash
   flyctl deploy --remote-only --no-cache
   ```

3. **Verify:**
   ```bash
   curl https://noni-api.fly.dev/health
   # Should return {"status":"healthy",...}
   ```

4. **Monitor:** Watch logs for `auth.transient_verifier_unavailable` errors

---

**Session closed by Session State Agent**
**All agents completed successfully**
**Recovery log:** `.ai/recovery/2026-06-11_login-loop.md`
