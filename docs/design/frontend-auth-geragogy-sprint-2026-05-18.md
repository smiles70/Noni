# Sprint Plan — Frontend Auth UX, Geragogy Contract Alignment

**Date opened:** 2026-05-18
**Status:** Planned. **Do not execute** without explicit approval.
**Predecessor:** `docs/design/login-redesign-2026-05-17.md` (Stages 0-2
backend + AuthProvider scaffolding — landed and verified).
**Authority:** `docs/library/CONTRACT.md` (P1) and
`docs/library/IDD-2026-cognitively-protective-iscs.md` (P2),
adopted by ADR 0019.

---

## 1. Why this sprint exists

Stages 0-2 produced a backend auth contract that is fully aligned with
the geragogy contract: discriminated errors, ops-fault vs user-fault
distinction, pure-read session resolver, sole-writer materialization,
deletion terminality, telemetry on every outcome. End-to-end runtime
proof captured 2026-05-17:

- `GET /auth/session` with a real Clerk session JWT → `200 materialized=false`.
- `POST /auth/session/init` with same JWT → `200 {account_id:...}`.
- Re-`GET /auth/session` → `200 materialized=true` with the same id.

The **backend** is contract-clean.

The **frontend** is not. The `AuthProvider` state machine exists, but
six surface-level behaviours required by the geragogy contract are
either missing or violated. The user-facing UX therefore does not yet
realise the protective properties the architecture was built to
guarantee. This sprint closes that gap.

This sprint **does not** add features. It only brings the existing
auth UI into compliance with the contract that ADR 0019 made
authoritative.

---

## 2. Inventory of planned changes

Each row in the grid below is a discrete, independently verifiable
work item. None of these are executed by this document — execution
requires an explicit go-ahead and (where the contract requires) an ADR
for any item that introduces or removes a permitted UI component.

| #   | Item                                            | Contract / IDD anchor                                            | Current state                                                              | Target state                                                                                                                | Files touched                                                          | Acceptance check                                                                                                          | Risk / blocker                                                                                                |
| --- | ----------------------------------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| F1  | Remove `DebugAuth` from production renders      | CONTRACT §I.D (component inventory closed)                       | Always-on widget rendered bottom-left in `App.tsx`                         | Gated behind `import.meta.env.DEV` so production bundles never include it. Component remains for dev sessions.              | `frontend/src/App.tsx`                                                 | Production bundle search (`npm run build && grep -ri "DebugAuth" dist/`) returns nothing.                                 | None.                                                                                                         |
| F2  | Add `PendingBanner` for `TRANSIENT_ERROR`       | CONTRACT §III state transparency; §I.D PendingBanner             | `AuthProvider` enters `TRANSIENT_ERROR` but nothing renders for the user.  | A muted-amber (`#C9A24D`) banner above the page frame: "Reconnecting…" with a manual "Try again" affordance.                | new `frontend/src/components/auth/AuthPendingBanner.tsx`, `App.tsx`    | Manual: kill backend, observe banner; restart, observe banner clears; spatial frame did not reflow.                       | None — `PendingBanner` is already in V1 inventory.                                                            |
| F3  | Add `BlockedNotice` for `REJECTED`              | CONTRACT §I.D BlockedNotice; §III "errors as system states"      | `AuthProvider` sets `REJECTED` with `errorCode` but nothing renders.       | Full-page `BlockedNotice` carrying the discriminated message ("Your session has expired", "Account has been deleted", etc). | new `frontend/src/components/auth/AuthBlockedNotice.tsx`, `App.tsx`    | Manual: feed an expired token; assert message text matches the discriminator; no red color outside `#B85C5C`.             | Copy needs review against §III "no alarmist phrasing".                                                        |
| F4  | Sign-out gated by `ConfirmDialog`               | CONTRACT §I.F ≤1 irreversible; §III require confirmation         | `signOut()` fires on a single click in `AccountSettingsPage`.              | Click opens `ConfirmDialog`: "This will sign you out. You can continue or go back." Sign-out only on explicit confirm.      | `frontend/src/components/AccountSettingsPage.tsx`, dialog component    | Manual: click sign-out, verify dialog appears; "go back" leaves session intact; "continue" signs out.                     | `ConfirmDialog` is in V1 inventory but may not exist yet as a component — inventory check before this starts. |
| F5  | Color discipline for transient vs definitive    | CONTRACT §I.A color system; restricted `#B85C5C` for errors      | No banner / notice exists yet, but ad-hoc styling likely to use red.       | Transient: amber `#C9A24D` (non-urgent). Definitive: restricted red `#B85C5C`. No other colors introduced.                  | F2 and F3 component CSS / Tailwind tokens                              | Visual audit + grep for hex codes against the contract's palette.                                                         | May require an ADR if any new token slips in.                                                                 |
| F6  | Spatial stability across BOOT→AUTHENTICATING→READY | CONTRACT §I.B "positions stable across states"                | `App.tsx` may swap route or whole component on auth transitions.           | NavBar + page frame remain mounted across the entire auth flow; only the content slot changes.                              | `frontend/src/App.tsx` routing                                         | Playwright test that records DOM bounding boxes of NavBar before/after sign-in; deltas must be 0px.                       | Existing routing logic may force unmount on first sign-in.                                                    |
| F7  | Verify `useAuth()` consumers honour state machine | I-G (no two components hold contradicting auth state)         | NavBar, AccountSettingsPage cut over; need to confirm no stragglers.       | Repo-wide grep proves only `AuthProvider` reads Clerk SDK or localStorage `noni.mock_token`.                                | Audit + (if any found) refactor                                        | `grep -RE "useClerkAuth\|useUser\|noni\.mock_token" frontend/src` returns only `AuthProvider.tsx` and `SignInPage.tsx`.    | None — already audited but worth re-running.                                                                  |
| F8  | Wire `notifyAuthChanged()` cleanly              | T7 (one auth resolution per boot, but explicit refresh on event) | Event listener present in `AuthProvider`; SignInPage dispatches.           | Confirm event is also dispatched on signOut completion (so DebugAuth and any test harness see immediate state change).      | `AuthProvider.tsx`                                                     | Manual: sign in, sign out, observe two state transitions in `DebugAuth` without page reload.                              | None.                                                                                                         |
| F9  | Promote `xfail` acceptance tests                | login-redesign §6 acceptance suite                               | T-B3, T-G2, T-H1, T-H3 passing; T-A1, T-A2, T-B1, T-G1, others still xfail.| Promote tests whose preconditions are now met after F1-F8.                                                                  | `frontend/tests/e2e/auth/*`                                            | `pytest` (or playwright) reports the listed tests as passing; CI green.                                                   | Some tests may surface real bugs — log them as new sprint items, do not weaken tests.                         |
| F10 | Startup guard against G1 (cryptography missing) | `docs/gotchas.md` G1; ADR 0012                                   | Verifier silently maps the ImportError into `auth.transient_verifier_*`.   | `main.py` startup probe imports `cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey` when AUTH_PROVIDER=clerk; raises with explicit remediation text if missing. | `backend/app/main.py`                                                  | Manual: `pip uninstall cryptography -y && uvicorn …` exits non-zero with the remediation message; reinstall, restarts ok. | Backend-side; included here because it closes the loop that caused the 30-hour rathole.                       |
| F11 | ADR for any V1 component additions              | CONTRACT §VI decision governance                                 | F2 (`AuthPendingBanner`) and F3 (`AuthBlockedNotice`) are *uses* of existing inventory components, not new types. Confirm. | Either confirmed-no-new-component (no ADR needed) or an ADR is drafted before F2/F3 execution.                              | possibly `docs/decisions/0026-*.md`                                    | Inventory check: F2 = PendingBanner instance; F3 = BlockedNotice instance. Documented in PR description.                  | If review concludes these are new component *kinds*, ADR is mandatory before code lands.                      |
| F12 | Remove temporary `sys` import in `auth_verifier.py` | minor cleanup                                                | `import sys` added during 2026-05-17 diagnosis, unused.                    | Removed.                                                                                                                    | `backend/services/auth_verifier.py`                                    | `ruff` / pyflakes clean.                                                                                                  | None.                                                                                                         |

---

## 3. Acceptance criteria for the sprint as a whole

Borrowed from IDD §III (trajectory-based, not checklist):

- **Cognitive load trajectory:** the number of distinct UI states a
  user passes through to reach a working signed-in session is **≤** the
  count today. F2/F3 add visibility but do not add steps.
- **Confidence trajectory:** ops-fault failures (JWKS hiccup, DB blip)
  no longer evict the user. F2 keeps the session sticky with a
  non-blaming banner.
- **Predictability trajectory:** the same failure class produces the
  same surface, every time. F3 + F5 enforce this by binding each
  discriminator to one rendered notice with one color.

The sprint is **done** when all 12 items above are checked AND a
Playwright run exercising the full sign-in / transient-failure /
expired-token / sign-out path passes on chromium, firefox, and webkit
(ADR 0011) with axe (ADR 0008) reporting no violations.

---

## 4. Out of scope (deliberately deferred)

- **Stage 3 `/me/progress`** — separate sprint, depends on this one
  for a clean auth state machine.
- **`ProviderProfileFetcher`** (off-path email backfill, B12) — does
  not affect UX, can ship anytime after Stage 2 backend.
- **Multi-factor / passwordless** — explicitly out of scope for
  login-redesign-v1.
- **Account-deletion confirmation flow polish** — exists already at
  `AccountSettingsPage`; revisit only if F4 audit surfaces a gap.

---

## 5. Open questions (must resolve before execution)

1. Does `ConfirmDialog` exist as an implemented V1 component? If not,
   F4 expands to "implement V1 ConfirmDialog per CONTRACT §I.D" and
   may need its own ADR.
2. Is `PendingBanner` distinct from `BlockedNotice`, or are they the
   same component with different severity levels? Contract §I.D lists
   them separately; need a one-line ADR-or-not decision.
3. Color: should the F2 transient amber `#C9A24D` also be applied to
   the `AUTHENTICATING` micro-state (i.e., a brief "Signing you in…"
   ribbon for slow Clerk handshakes), or only for `TRANSIENT_ERROR`?
   IDD §II ("anticipatory guidance") leans toward yes; need a decision.

---

## 6. Cross-references

- `docs/library/CONTRACT.md` — primary authority.
- `docs/library/IDD-2026-cognitively-protective-iscs.md` — acceptance
  framework.
- `docs/design/login-redesign-2026-05-17.md` — backend design this
  sprint depends on.
- `docs/design/login-execution-playbook-2026-05-17.md` — Stages 0-2.
- `docs/gotchas.md#g1` — the runtime trap F10 closes.
- `docs/decisions/0019-closed-world-design-contract.md` — adopts the
  contract this sprint enforces.
- `docs/decisions/0023-auth-and-session-model.md` — original
  session-cookie design (superseded for the new endpoints).
