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
