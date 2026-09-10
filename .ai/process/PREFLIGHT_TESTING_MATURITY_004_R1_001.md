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

## Go / no-go

**GO** for **Block 4.1 — E2E onboarding journey** (`/welcome`, `/getting-started`, `/account-setup`).

## Block 4.1 acceptance criteria

- `frontend/e2e/onboarding.spec.ts` created.
- Covers `/welcome` → `/getting-started` → `/account-setup` navigation.
- Asserts reversible exit, no urgency language, and axe WCAG 2.1 AA.
- Passes on chromium and mobile-pixel locally.
- Committed and pushed to `staging`.

## Risks

1. Onboarding may read from backend endpoints or `localStorage`; mock or seed accordingly.
2. Cross-browser failures may be browser-binary availability only; CI is the canonical matrix.
3. Each new E2E spec will run 25 times in CI (5 projects); keep specs concise.

## Definition of Done

- [ ] Rack 4.1 spec committed.
- [ ] Local chromium / mobile-pixel pass.
- [ ] Intake and preflight updated with evidence.
