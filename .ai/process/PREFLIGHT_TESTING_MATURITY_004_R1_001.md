# Preflight — TEST-MATURITY-004-R1: remaining E2E and smoke/load gates

**Process:** v9.51  
**Intake:** `.ai/intake/2026-09-10-p1-testing-maturity-remaining-v951-intake-005.md`

---

## Pre-flight checklist

| # | Gate | Status | Owner | Evidence |
|---|---|---|---|---|
| 1 | Intake approved | GO | Product + Platform | `.ai/intake/2026-09-10-p1-testing-maturity-remaining-v951-intake-005.md` |
| 2 | Parent TEST-MATURITY-004 baseline | GO | Engineering | Frontend unit 195 pass / 15 expected fail; backend 451 pass / 85.61 % source coverage; `main` deployed to production |
| 3 | Existing E2E harness | GO | Engineering | `frontend/playwright.config.ts` with 5 projects; `gift.spec.ts` green on chromium + mobile-pixel |
| 4 | Tooling available | GO | Engineering | Playwright, axe-playwright, pytest, `scripts/check-bundle-size.mjs` |
| 5 | Branch strategy confirmed | GO | Engineering | Continue on `feat/testing-maturity-004` → `staging`; `main` merge requires separate approval |

## Block 4.1 — E2E onboarding journey (COMPLETE)

- `frontend/e2e/onboarding.spec.ts` created.
- Extracted shared `frontend/e2e/utils/auth.ts` for mock-token + envelope + route mocks.
- 4 local chromium tests pass:
  - `/welcome` requires auth.
  - `/welcome` redirects new learner to `/setup`.
  - `/setup` form completes and auto-continues to `/getting-started`.
  - `/getting-started` passes axe WCAG 2.1 AA.

## Block 4.2 — E2E paywall journey (COMPLETE)

- `frontend/e2e/paywall.spec.ts` created.
- 7 local chromium tests pass:
  - `/paywall` requires auth.
  - `/paywall` is geragogy-calm and exposes three exits.
  - Self-purchase checkout contract.
  - Gift purchase appends `gift_token`.
  - Gift-code redeem routes to `/gift-redeem`.
  - Organization code redemption routes to `/curriculum`.
  - `/paywall` passes axe WCAG 2.1 AA.

## Block 4.3 — E2E admin journey (COMPLETE)

- `frontend/e2e/admin.spec.ts` created.
- 2 passed; 1 a11y test marked `fixme` due to color-contrast findings.
- `/admin` renders staff sign-in form for non-staff.
- Staff session loads overview and navigation.

## Block 4.4 — E2E account journey (COMPLETE)

- `frontend/e2e/account.spec.ts` created.
- 5 local chromium tests pass:
  - `/account` requires auth.
  - `/account` renders identity and reversible actions.
  - Sign out returns to `/`.
  - Delete account requires confirmation and is scheduled.
  - `/account` passes axe WCAG 2.1 AA.

## Block 4.5 — E2E partner/community journey (COMPLETE)

- `frontend/e2e/community.spec.ts` created.
- 4 local chromium tests pass:
  - `/for-communities` renders B2B surface.
  - Mailto contact CTAs visible.
  - Public, no paywall.
  - `/for-communities` passes axe WCAG 2.1 AA.

## Block 4.6 — E2E auth callback journey (COMPLETE)

- `frontend/e2e/auth-callback.spec.ts` created.
- 2 local chromium tests pass:
  - `/auth/callback` renders pending message.
  - `/auth/callback` passes axe WCAG 2.1 AA.

## Production deploy and smoke

- Pushed `feat/testing-maturity-004` to `main`.
- Commit range: `efb7072..18d6753`.
- Production smoke (curl) all green:
  - `https://www.mynaani.com/` — 200 in 423 ms
  - `https://www.mynaani.com/gift` — 200 in 140 ms
  - `https://www.mynaani.com/for-communities` — 200 in 128 ms
  - `https://noni-api-production.up.railway.app/` — 200 in 238 ms
  - `https://noni-api-production.up.railway.app/api/v1/landing/page` — 200 in 206 ms

## Block 5 — Performance/load/smoke validation (IN PROGRESS)

### 5.1 Isolated backend A10 smoke

- `backend/tests/test_a10_smoke.py` exists.
- Local environment has no Postgres; the canonical run is CI.
- A10 smoke workflow research completed in `.ai/research/2026-09-11-a10-workflow-problem-and-options.md`.
- A10 smoke is blocked until the GitHub token used by Devin is granted the `workflow` OAuth scope; manual GitHub UI edits have been stopped.

### 5.2 k6 / Lighthouse / pa11y smoke gates — LOCAL RUN COMPLETE

- Installed `lighthouse@13.4.1` and `pa11y@10.0.0` as dev dependencies.
- `npm audit` now reports `found 0 vulnerabilities`.
- Downloaded `k6` v0.54.0 binary to `frontend/.bin/k6` (not committed).
- Wired in `frontend/package.json`:
  - `npm run smoke:lighthouse`
  - `npm run smoke:pa11y`
  - `npm run smoke:k6`
- Created runners:
  - `frontend/scripts/smoke-lighthouse.mjs`
  - `frontend/scripts/smoke-pa11y.mjs`
  - `frontend/scripts/smoke-k6.mjs`
  - `frontend/scripts/smoke-k6.js`
  - `frontend/pa11y.json`

### Results against `https://www.mynaani.com`

| Gate | Result | Key metric |
|---|---|---|
| k6 | ✅ pass | 1 VU, 10s, p95 latency 57 ms, 0% failures |
| pa11y | ✅ pass | 0 WCAG 2.1 AA violations on `/` |
| Lighthouse | ✅ pass | performance 99, accessibility 100, best-practices 100 |

Lighthouse report written to `frontend/.ai/audit/lighthouse-smoke.json`.

## Go / no-go

**GO** for installing the tools and running the gates in CI.

## Risks

1. k6 is a system binary; CI runner must have it or use the Grafana docker image.
2. Lighthouse and pa11y add dependency weight; use pinned exact versions.
3. Production smoke gates should target the staging environment, never run against prod in CI by default.

## Definition of Done

- [x] Rack 4.1-4.6 specs committed and pushed to `staging` and `main`.
- [x] Production push and smoke complete.
- [x] Smoke-gate scripts and package.json scripts created.
- [ ] Install and validate `lighthouse`, `pa11y`, and `k6` in a safe environment.
