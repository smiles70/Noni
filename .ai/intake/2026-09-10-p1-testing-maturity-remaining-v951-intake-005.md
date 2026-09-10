# Intake: Remaining E2E + smoke / load validation for testing grade A

**Process:** v9.51
**Date:** 2026-09-10
**ID:** P1-TEST-MATURITY-004-R1
**Status:** INTAKE — ready for preflight
**Owner:** Platform + QA
**Source:** `.ai/intake/2026-09-10-p1-testing-maturity-v951-intake-004.md`

---

## 1. Problem statement

Testing Maturity v9.51 (`P1-TEST-MATURITY-004`) has reached grade A for frontend unit coverage and cleared all backend placeholder files. The remaining gaps that block full A-grade certification are:

- **E2E / journey coverage:** only landing, free-curriculum dialog, post-purchase success, and guest-gift checkout are exercised. Onboarding, paywall, admin, account, partner/community, and auth callback flows are not covered.
- **Performance / smoke gates:** bundle-size is verified; smoke-gate runners and `package.json` scripts are created for k6 / Lighthouse / pa11y, but the tools are not yet installed. The backend A10 full-launch smoke has not been run in isolation against a clean Postgres instance.
- **Cross-browser matrix:** Firefox / WebKit / mobile-iphone binaries are not installed in the local environment; CI is the canonical runner for the 5-project Playwright matrix.

This is a **P1** delivery risk: the next high-value releases (guest gift checkout, entitlement-aware routing, onboarding) cannot move to `main` with confidence unless the critical journeys and smoke gates are automated.

---

## 2. Scope of work

### Block 4 — E2E journey and a11y expansion

Add Playwright specs for the following critical user paths. Each spec must include at least one axe WCAG 2.1 AA assertion.

| Journey | Routes | Key assertions |
|---|---|---|
| Onboarding | `/welcome`, `/getting-started`, `/account-setup` | ✅ `frontend/e2e/onboarding.spec.ts` — 4 tests, axe WCAG 2.1 AA |
| Paywall | `/paywall` | ✅ `frontend/e2e/paywall.spec.ts` — 7 tests, geragogy-calm, all three exits, axe WCAG 2.1 AA |
| Admin | `/admin` | ✅ `frontend/e2e/admin.spec.ts` — staff sign-in, overview, nav; a11y color-contrast finding logged as `fixme` |
| Account | `/account` | ✅ `frontend/e2e/account.spec.ts` — auth, sign out, delete confirmation, a11y |
| Partner / communities | `/for-communities` | ✅ `frontend/e2e/community.spec.ts` — B2B surface, mailto CTAs, no paywall, a11y |
| Auth callback | `/auth/callback` | ✅ `frontend/e2e/auth-callback.spec.ts` — pending message, a11y |
| Cross-browser | all of the above | 5-project matrix green in CI |

### Block 5 — Performance, load, and isolated smoke

| Gate | Tool / method | Target |
|---|---|---|
| Build bundle budget | `frontend/scripts/check-bundle-size.mjs` | All chunks ≤ 100 kB gzipped |
| Frontend a11y smoke | Playwright `axe-playwright` | No WCAG 2.1 AA violations on critical pages |
| Backend full-launch smoke | `backend/tests/test_a10_smoke.py` with Postgres | Pending backend venv / CI |
| API latency baseline | `k6` or `ab` | Wired via `npm run smoke:k6`; pending k6 binary install |
| Lighthouse performance | `lighthouse` or `playwright-lighthouse` | Wired via `npm run smoke:lighthouse`; pending npm install |
| Pa11y regression | `pa11y` | Wired via `npm run smoke:pa11y`; pending npm install |

---

## 3. Acceptance criteria

- [x] `npm run test:e2e` is green on chromium + mobile-pixel locally; full 5-project matrix remains CI-canon.
- [x] New E2E specs cover onboarding, paywall, admin, account, partner/community, and auth callback.
- [ ] `backend/tests/test_a10_smoke.py` passes against a clean Postgres instance with `DATABASE_URL` set.
- [x] Bundle-size check remains green after every build.
- [ ] k6 or equivalent smoke records p95 latency for public endpoints (scripts wired; tools pending).
- [ ] Lighthouse / pa11y reports are generated and linked in the preflight (scripts wired; tools pending).
- [ ] PREFLIGHT updated to mark Blocks 4 and 5 COMPLETE.

---

## 4. Definition of done

- PR from `feat/testing-maturity-004-r1` → `main` passes all unit, E2E, backend, bundle-size, and smoke gates.
- Staging UAT sign-off captured in the preflight.
- Production deploy is explicitly approved in writing before `main` is updated.

---

## 5. Related files

- `.ai/process/PREFLIGHT_TESTING_MATURITY_001.md`
- `.ai/research/2026-09-10-testing-rubric-and-gaps.md`
- `frontend/playwright.config.ts`
- `frontend/e2e/`
- `backend/tests/test_a10_smoke.py`
- `frontend/scripts/check-bundle-size.mjs`
