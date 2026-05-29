# Sprint: Series A Step 1

**Date:** 2026-05-28
**Scope:** Two enterprise-critical gaps preventing Series A readiness
**Target Score:** 466 → 520+ / 720

---

## Gap 1: No URL Router (P3, P6, P7, P23)

**Current State:** `App.tsx` uses in-memory `useState` view machine. No deep linking, no back button, no shareable URLs.
**Target State:** React Router v6 with route guards, auth-aware redirects, and Geragogy-safe transitions.

### Architecture Decisions

- **Library:** `react-router-dom` v6 (already in `package.json` from a prior commit, or add it)
- **Guard Pattern:** Route components check `useAuth()` state; unauthenticated users redirected to `/` with `?redirect=...`
- **Back Button:** Browser history integration via `useNavigate()` + `useLocation()`
- **Deep Linking:** Every view mapped to a route (`/`, `/curriculum`, `/paywall`, `/account`, `/help`, `/gift/:code`)
- **Geragogy Contract:** No hard page reloads. Transitions use the existing calm-loading pattern.

### Route Map

| Route | View | Auth Required | Deep Linkable |
|-------|------|---------------|---------------|
| `/` | Landing | No | Yes |
| `/curriculum` | Curriculum | Yes | Yes |
| `/curriculum/:unitId` | Specific unit | Yes | Yes |
| `/paywall` | Paywall | Yes | Yes |
| `/account` | Account settings | Yes | Yes |
| `/gift/:code` | Gift redemption | No | Yes |
| `/help` | Help center | No | Yes |
| `/auth/callback` | OAuth finish | No | No (ephemeral) |

---

## Gap 2: Single Points of Failure (P11, P16, P20)

**Current State:** One Postgres instance, one Fly region, Clerk JWKS = total auth dependency.
**Target State:** Local JWKS cache + mock auth fallback when Clerk is unreachable.

### Architecture Decisions

- **Clerk JWKS:** Cache fetched JWKS in memory for 24h. If fetch fails, serve from cache. If cache empty, fallback to mock auth (already wired).
- **Postgres:** Document-only for this sprint. Read replica requires Fly Postgres provision changes (outside code). Mark as roadmap.
- **Region:** Document-only. Multi-region Fly requires `fly scale count` changes. Mark as roadmap.

### Implementation

1. `ClerkVerifier` → add `JWKS_CACHE` class-level dict with TTL
2. `verify_credential` → try Clerk first; on `PyJWKClient` failure, check cache; on cache miss, return `None` (triggers mock auth in caller)
3. `AuthProvider` → already handles `REJECTED` gracefully; no changes needed

---

## Test Plan (720-Degree Regression)

### Pass 1: Syntax & Compilation
- `py_compile backend/services/clerk_verifier.py`
- `tsc --noEmit` frontend
- `npm run build` frontend

### Pass 2: Unit Tests
- `pytest backend/tests/test_clerk_verifier.py` (new)
- `pytest backend/tests/test_auth_provider.py`
- `pytest backend/tests/test_enterprise_security.py`

### Pass 3: Integration Tests
- `pytest backend/tests/test_safe_yellow.py`

### Pass 4: Frontend Contract Tests
- `npm test` (existing suite)
- Route guard behavior: unauthenticated → `/` redirect
- Deep link: `/curriculum` → auth check → curriculum render
- Back button: `/curriculum` → back → `/` (landing)

### Pass 5: End-to-End
- `npx playwright test` (existing suite, verify no regression)

### Pass 6: CORS & API Surface
- `curl` OPTIONS preflight from `localhost:5173`
- All routes respond with correct CORS headers

### Pass 7: Deploy Smoke
- Deploy backend
- Deploy frontend
- Manual: navigate to `/help` directly → renders help page
- Manual: navigate to `/curriculum` unauthenticated → redirects to `/`
- Manual: sign in → navigate to `/curriculum` → renders curriculum

---

## Success Criteria

- [ ] `/help` renders directly without going through landing
- [ ] `/curriculum` redirects unauthenticated users to `/`
- [ ] Back button works from curriculum → landing
- [ ] Shareable URL copied from `/curriculum` opens curriculum after auth
- [ ] Clerk JWKS outage: user can still sign in with mock auth
- [ ] All existing tests pass
- [ ] No new console errors
- [ ] Deploy succeeds with green health checks
