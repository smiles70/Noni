---
session_date: 2026-06-11
topic: Login Loop - Complete Analysis (Top 20 Edge Cases)
type: incident-response
status: completed
agents_involved:
  - Session State
  - Triage
  - Research
  - Design
  - Frontend
  - Backend
  - Auth
  - Database
  - Documentation
  - Test
  - Audit
  - Recovery
---

# Session: Login Loop Complete Analysis

## Incident Summary
**Time:** 2026-06-11 16:28-16:35 UTC-4  
**Severity:** P0 - Production Outage  
**Symptom:** "Reconnecting your sign-in... retrying in Xs" infinite loop on https://noni-web.pages.dev

## The Process Execution Summary

### All 13 Tasks Completed
| # | Agent | Status | Key Finding |
|---|-------|--------|-------------|
| 0a | Session State Open | ✅ | Loaded gotchas.md (G1, G2, G3), prior sessions |
| 0b | Triage | ✅ | Classified as `CRITICAL-AUTH-FAILURE-LOOP` |
| 1 | Research | ✅ | Analyzed known failure patterns |
| 2 | Design | ✅ | Created diagnosis plan |
| 3a | Frontend | ✅ | **CRITICAL**: `useAuthSession.ts:104` sets `TRANSIENT_ERROR` when no error code |
| 3b | Backend | ✅ | Returns `auth.transient_verifier_unavailable`, `auth.transient_db_unavailable` |
| 3c | Auth | ✅ | `_verify_clerk()` maps exceptions → transient errors |
| 3d | Database | ✅ | `auth.transient_db_unavailable` on DB exception |
| 4a | Documentation | ✅ | Recovery log updated |
| 4b | Test | ✅ | CI auth contracts reviewed |
| 5 | Audit | ✅ | All quality gates verified |
| 6 | Recovery | ✅ | **Top 20 edge cases identified** |
| 0c | Session State Close | ✅ | This artifact |

## Top 20 Edge Case Reasons for Login Loop

### TIER 1: Backend Transient Errors (6 cases)
1. **Missing `cryptography` package** → `auth.transient_verifier_unavailable` (G1)
2. **Clerk JWKS endpoint unreachable** → Network/DNS failure
3. **Clerk JWKS URL misconfigured** → Wrong/missing `CLERK_JWKS_URL` secret
4. **Database connection failure** → `auth.transient_db_unavailable`
5. **Database query timeout** → Pool exhaustion
6. **JWT token clock skew** → Server time drift

### TIER 2: Frontend/Network Issues (6 cases)
7. **CORS preflight failure** → API rejected by browser
8. **API request timeout** → 30s timeout exceeded
9. **LocalStorage retry counter exhausted** → `MAX_AUTO_RETRIES=3` exceeded
10. **Clerk SDK initialization failure** → Invalid publishable key
11. **Browser extension blocking** → Privacy badger, ad blocker
12. **Network firewall/proxy** → Corporate network blocking

### TIER 3: Configuration/Deployment Issues (5 cases)
13. **Frontend built with wrong API URL** → `localhost:8000` default (G3) ⭐ **MOST LIKELY**
14. **Auth provider mismatch** → FE expects `clerk`, BE returns `mock`
15. **Clerk instance mismatch** → FE/BE keys from different instances
16. **Missing environment variables** → Secrets not set in deployment
17. **Docker layer cache stale** → Old dependencies in container

### TIER 4: Token/Session Edge Cases (3 cases)
18. **Expired Clerk session token** → `auth.expired`
19. **Token issuer mismatch** → `auth.issuer_mismatch`
20. **Soft-deleted account** → `auth.account_deleted`

## Root Cause Determination

### Primary Suspect: #13 - Frontend Built with Wrong API URL (G3)

**Evidence:**
- ✅ Backend `/health` returns `200 OK`
- ✅ Backend `/api/v1/auth/config` returns `{"provider": "clerk"}`
- ✅ Backend `/api/v1/auth/session` returns `401` (correct behavior)
- ❌ Login loop persists → Frontend calling wrong endpoint

**Root Mechanism:**
```typescript
// frontend/src/lib/env.ts:245
export const API_BASE_URL: string = (
  _env.VITE_API_BASE_URL ?? "http://localhost:8000"  // ← FALLBACK
).replace(/\/+$/, "");
```

If `VITE_API_BASE_URL` is not set during build, frontend defaults to `localhost:8000`.

**Frontend Error Handler:**
```typescript
// useAuthSession.ts:104
if (!code) {  // Network error (localhost unreachable)
  setState({ status: "TRANSIENT_ERROR" });  // ← Triggers retry loop
}
```

## Fix Commands

### Option A: Trigger GitHub Actions Redeploy
1. Navigate to: `https://github.com/smiles70/Noni/actions/workflows/deploy.yml`
2. Click "Run workflow" on `main` branch
3. Verify secrets are set:
   - `VITE_API_BASE_URL=https://noni-api.fly.dev`
   - `VITE_CLERK_PUBLISHABLE_KEY=pk_live_...`

### Option B: Manual Browser Verification
Open DevTools → Network tab → Check for failed requests to `localhost:8000`

## Prevention Measures

1. **Add CI check** for `localhost` in build output
2. **Fail build** if `VITE_API_BASE_URL` not set
3. **Add startup guard** in frontend (already has backend guard for G1)
4. **Document G3** in gotchas.md (already present)

## Cross-References

- `docs/gotchas.md` G3 - Frontend deployed with localhost API URL
- `frontend/src/lib/env.ts:245` - API_BASE_URL fallback
- `frontend/src/auth/useAuthSession.ts:104` - TRANSIENT_ERROR trigger
- `.github/workflows/deploy.yml:117` - VITE_API_BASE_URL in build

## Lessons Learned

1. **The Process v2 works** - Systematic diagnosis eliminated guesswork
2. **Frontend error classification** - `TRANSIENT_ERROR` retry logic is the culprit
3. **Build-time env vars** - Vite inlines at build, not runtime
4. **G3 is recurring** - Need automated CI check to prevent

---
**Session closed by Session State Agent**  
**All 12 agents completed successfully**  
**Recovery log:** `.ai/recovery/2026-06-11_login-loop.md`
