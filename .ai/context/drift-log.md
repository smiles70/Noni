# Drift Log — Noni Codebase

> Maintained by Codebase Context Agent v4.
> Each session appends diffs between documented architecture and live map.

---

## Session: 2026-06-20 (Onboarding / Full Rebuild)

### Baseline Established
- `ARCHITECTURE.md` exists and reflects the 10 non-negotiable rules.
- 720 Assessment (`docs/assessments/720-assessment-2026-05-28.md`) shows score 521/720 (Stage 4: Soft Launch).

### Drift Detected: Documented vs. Live

| Category | Documented (ARCHITECTURE.md / 720 Assessment) | Live Reality | Drift Type | Severity |
|---|---|---|---|---|
| Auth model | ADR 0023 session-cookie design | ADR 0024 stateless Bearer JWT; `sessions` table unused | Architecture migrated, docs reference old ADR | Low (ADR 0024 docs exist) |
| Frontend router | "Simple view-state machine (no router)" comment in `App.tsx` | React Router v6 with 10 routes, lazy loading | Comment stale | Low |
| HTTP client | None specified | Native fetch; `axios` removed | Improvement not reflected in comments | Low |
| `window.setTimeout` | Fixed per P11/P23 | `globalThis.setTimeout` in `api/client.ts` | Match | None |
| Sessions table | Present in schema | Unused post-ADR-0024; "scheduled for deletion" | Schema drift | Medium |
| DebugAuth | Not in V1 inventory | Present, runtime-gated by `IS_DEV`, neon green `#0f0` | Unauthorized component; geragogy violation | Medium |
| Error reporting | No frontend error reporting | Still no Sentry | Persistent RED gap | High |

### Resolution
- Baseline accepted. No contradictions block pipeline operation.
- Stale `App.tsx` comment noted for cleanup.
- `sessions` table deletion tracked as deferred task.

---

## Session: 2026-06-20 (TRANSIENT_ERROR Fix)

### Change Summary
- Fixed `TRANSIENT_ERROR` spatial stability violation in `AuthPendingBanner.tsx`.
- Removed "Please refresh the page to try again." exhausted-state copy.
- "Try now" button now visible at all times; manual click resets auto-retry cycle.
- Auto-retry limit (3 attempts) preserved to prevent oscillation.

### Files Modified
| File | Change |
|---|---|
| `frontend/src/components/AuthPendingBanner.tsx` | Keep button visible when exhausted; reset retry count on manual click; calmer copy |
| `frontend/src/components/__tests__/AuthPendingBanner.test.tsx` | Updated exhausted-state test; added manual-retry-reset test |

### Drift Resolved
| Previous Drift | Status |
|---|---|
| P12: `TRANSIENT_ERROR` triggers full page reload | 🟢 FIXED — no refresh instruction; spatial stability preserved |

### Verification Pending
- Frontend unit tests (`vitest`) require `npm install` to run; command queued.

---

## Session: 2026-06-20 (Deep Diagnosis — 401 Loop)

### Root Cause
`useAuthSession.ts` `handleError` parsed the 401 response body as `data.error.code`, but FastAPI's `HTTPException` wraps `detail` in a `{"detail": ...}` envelope. The actual body is `{"detail": {"error": {"code": "auth.no_credential"}}}`. Because `data.error` is undefined, `code` was always undefined for 401s, causing **all 401 responses to be misclassified as `TRANSIENT_ERROR`**. The `AuthPendingBanner` then auto-retried every 15s with the same expired token — an infinite loop.

### Fix Applied
- `frontend/src/auth/useAuthSession.ts`: Added explicit `status === 401` guard in `handleError` that transitions to `SIGNED_OUT` before body parsing. 401 is semantically definitive (retrying with the same token can never succeed).
- `frontend/src/auth/__tests__/AuthProvider.test.tsx`: Fixed pre-existing test infrastructure bugs (incomplete env mock, React `ref` reserved prop, missing `fetch` mock). Added regression test: `transitions to SIGNED_OUT on 401 from /auth/session`.

### Files Modified
| File | Change |
|---|---|
| `frontend/src/auth/useAuthSession.ts` | 401 → `SIGNED_OUT` guard in `handleError` |
| `frontend/src/auth/__tests__/AuthProvider.test.tsx` | Complete rewrite: env mock, fetch mock, async assertions, 401 regression test |

### Verification
- `AuthProvider.test.tsx`: 4/4 pass
- `tsc --noEmit`: pass
- Full vitest suite: 111/135 pass (24 pre-existing failures in curriculum/billing/auth tests, unrelated to this change)

### Drift Resolved
| Previous Drift | Status |
|---|---|
| P13: `TRANSIENT_ERROR` reload loop on expired/invalid token | 🟢 FIXED — 401 now maps to `SIGNED_OUT`, breaking the retry cycle |

### New Drift Detected
| Category | Documented | Live Reality | Drift Type | Severity |
|---|---|---|---|---|
| `useCredentialSource` | Should return stable references | Returns new object every render (no `useMemo`) | Performance / subtle bug | Low |
| `AuthProvider.test.tsx` | Was passing (assumed) | Could not even load due to incomplete env mock + `ref` prop bug | Test infrastructure gap | Medium |

---

## Session: 2026-06-20 (Follow-up — Clerk Desync Loop)

### Root Cause
The initial 401 → `SIGNED_OUT` fix was correct for stopping the `TRANSIENT_ERROR` retry loop, but incomplete: it did **not** clear the Clerk session. When the backend rejected the Clerk token with 401, AuthProvider said `SIGNED_OUT`, but Clerk's SDK still reported `isSignedIn: true`. Clerk's `<SignIn routing="virtual" fallbackRedirectUrl="/" />` widget auto-redirected already-signed-in users to `/`. The landing page showed "Log in" (because our state was `SIGNED_OUT`), the user clicked it, Clerk redirected back to `/` — an endless login loop.

Additionally, the frontend parsed 401 response bodies as `data.error.code`, but FastAPI's `HTTPException` wraps errors in `data.detail.error.code`. The `deps.py` 401s use `data.detail.envelope_id`. Both shapes were unreadable, so error codes were always `undefined` for 401s.

### Fix Applied
- `frontend/src/auth/useAuthSession.ts`:
  - `handleError` is now `async`; it calls `auth.signOut?.()` before transitioning to `SIGNED_OUT` on 401. This clears Clerk's session (or the mock token) so the credential source stays in sync with the state machine.
  - Body parsing now tries `data.error.code`, then `data.detail.error.code`, then `data.detail.envelope_id` to handle both `auth.py` and `deps.py` 401 shapes.
  - `ApiErrorResponse` type updated to reflect the FastAPI `detail` wrapper.
  - `auth` parameter type now includes optional `signOut`.
- `frontend/src/auth/__tests__/AuthProvider.test.tsx`: Updated 401 regression test to assert that the mock token is cleared (verifying `signOut` is invoked).

### Verification
- `AuthProvider.test.tsx`: 4/4 pass
- `tsc --noEmit`: pass

### Drift Resolved
| Previous Drift | Status |
|---|---|
| P14: Clicking login causes endless reload loop | 🟢 FIXED — 401 now clears Clerk session before SIGNED_OUT, preventing auto-redirect desync |

### New Drift Detected
| Category | Documented | Live Reality | Drift Type | Severity |
|---|---|---|---|---|
| 401 envelope contract | Frontend expects `data.error.code` | Backend sends `data.detail.error.code` (auth.py) or `data.detail.envelope_id` (deps.py) | Contract violation — all 401 codes unreadable | High |
| Clerk dev key in prod | Production deployment | Deployed app uses Clerk development publishable key | Security / operational risk | High |
