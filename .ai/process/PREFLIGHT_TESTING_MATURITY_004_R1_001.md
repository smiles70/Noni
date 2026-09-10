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

## Block 4.2 — E2E paywall journey (IN PROGRESS)

- `frontend/e2e/paywall.spec.ts` created.
- 7 local chromium tests pass:
  - `/paywall` requires auth.
  - `/paywall` is geragogy-calm and exposes three exits.
  - Self-purchase checkout contract.
  - Gift purchase appends `gift_token`.
  - Gift-code redeem routes to `/gift-redeem`.
  - Organization code redemption routes to `/curriculum`.
  - `/paywall` passes axe WCAG 2.1 AA.

## Go / no-go

**GO** for **Block 4.3 — E2E admin journey**.

## Risks

1. Cross-browser failures may be browser-binary availability only; CI is the canonical matrix.
2. Each new E2E spec will run 25 times in CI (5 projects); keep specs concise.
3. Mock-token routes may need `mynaani.staff_token` for staff-only admin views.

## Definition of Done

- [x] Rack 4.1 spec committed and pushed to `staging`.
- [x] Rack 4.2 spec committed and pushed to `staging`.
