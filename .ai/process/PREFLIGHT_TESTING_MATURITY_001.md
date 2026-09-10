# Preflight — TEST-MATURITY-004: grade A testing across all rubric dimensions

**Process:** v9.51  
**Intake:** `.ai/intake/2026-09-10-p1-testing-maturity-v951-intake-004.md`

---

## Pre-flight checklist

| # | Gate | Status | Owner | Evidence |
|---|---|---|---|---|
| 1 | Intake approved | GO | Product + Platform | `.ai/intake/2026-09-10-p1-testing-maturity-v951-intake-004.md` |
| 2 | Rubric and gap analysis reviewed | GO | Engineering | `.ai/research/2026-09-10-testing-rubric-and-gaps.md` |
| 3 | Existing CI understood | GO | Engineering | `.github/workflows/ci.yml`, `deploy-staging.yml`, `deploy.yml` |
| 4 | Baseline test state captured | GO | Engineering | Frontend unit 138 pass / 15 expected fail; backend 451 pass / 2 skipped / 14 xfailed / 85.61 % source coverage |
| 5 | Tooling available | GO | Engineering | Vitest, Playwright, pytest, `pytest-cov` in `requirements-dev.txt`, `@vitest/coverage-v8` in `frontend/package.json` |
| 6 | Branch strategy confirmed | GO | Engineering | `feat/testing-maturity-004` → `staging` → `main` (human approval) |
| 7 | No production deploy in scope | GO | Product | Intake explicitly targets staging; `main` merge requires separate approval |
| 8 | Dependent intakes identified | GO | Product | `P1-GIFT-CHECKOUT-002`, `P2-JOURNEY-LOOP-003`, `WI-003` |

## Go / no-go

**GO** for Phase 0. Create branch `feat/testing-maturity-004`, commit the preflight, and begin **Block 1 — CI hygiene and backend contract reconvergence**.

## Batch 0 — Branch and commit the preflight

| Step | Command / action | Artifact |
|---|---|---|
| 0.1 | `git checkout -b feat/testing-maturity-004` | feature branch |
| 0.2 | Stage this preflight and the intake only | `.ai/process/PREFLIGHT_TESTING_MATURITY_001.md`, `.ai/intake/2026-09-10-p1-testing-maturity-v951-intake-004.md` |
| 0.3 | `git diff --cached --stat` | confirm only intended files staged |
| 0.4 | `git commit` | preflight in git |
| 0.5 | `git push origin feat/testing-maturity-004` | remote branch |

**Gate:** `PREFLIGHT` — workspace clean, only the preflight and intake committed, branch is `feat/testing-maturity-004`.

## Risks

1. Backend contract drift may be larger than one rack; time-box and escalate to a dedicated intake if needed.
2. Playwright cross-browser matrix will extend CI duration; consider project sharding if runtime exceeds 15 minutes.
3. Coverage thresholds must be introduced gradually to avoid blocking unrelated in-flight work.
4. Any CI workflow edits require `ALLOW_WORKFLOW_CHANGES=1 git commit` and ship as their own commit.

## Block 1 completion evidence

- `pytest backend/tests/` with `tinypg`: **451 passed, 2 skipped, 14 xfailed**.
- Backend source coverage: **85.61 %**.
- `ruff check backend/` and `black --check backend/` pass.
- `bandit -r backend -x backend/tests` returns no issues.
- `npm audit --audit-level=high` in `frontend/` returns 0 vulnerabilities.
- Coverage gate committed in `7ac3c6a` on `feat/testing-maturity-004`.
- Pushed to `staging` (`7ac3c6a`).

## Block 3 — Frontend unit/component backfill (GRADE A — COMPLETE)

- Rack 3.1 (`1e359b2`): `MissingComponents.test.tsx`.
- Rack 3.2 (`959c03d`): `client.test.ts`, `logger.test.ts`, extended
  `useViewport.test.ts`.
- Rack 3.3 (`710c59a`): extended `PurchaseSuccessPage.test.tsx`.
- Rack 3.4 (`1abbf24`): `HowItWorksDialog.test.tsx`.
- Rack 3.5-3.6 (`a699164`): `PageTypes.render.test.tsx`, extended
  `LandingPage.brand.test.tsx`.
- Locked `vitest.config.ts` coverage thresholds at grade-A floors:
  - statements 87 %, branches 75 %, functions 84 %, lines 88 %.
- Frontend unit test run: **24 files, 195 passed, 15 expected fail**.
- Latest `feat/testing-maturity-004` pushed to `staging` (`a699164`).

## Block 2 — Backend placeholder file disposition (COMPLETE)

- Re-reviewed the 9 files previously listed as empty placeholders.
- All 9 now contain real `def test_` functions and participate in the suite.
- No removal or conversion is required.

## Next go / no-go

**GO** for **Block 4 — E2E journey and a11y expansion** against staging,
OR **Block 5 — performance/load/smoke validation**.

## Definition of Done for this preflight

- [x] `feat/testing-maturity-004` branch exists and is pushed.
- [x] Intake and preflight committed and reviewable.
- [x] Baseline CI state captured (backend tests green, bandit clean, npm audit clean).
- [x] Block 1 rack list accepted and completed.
