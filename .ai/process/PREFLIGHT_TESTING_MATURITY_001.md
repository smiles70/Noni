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
| 4 | Baseline test state captured | GO | Engineering | Frontend unit 138 pass / 15 expected fail; backend 285 tests with ~51 failures and 9 empty files |
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

## Definition of Done for this preflight

- [ ] `feat/testing-maturity-004` branch exists and is pushed.
- [ ] Intake and preflight committed and reviewable.
- [ ] Baseline CI failure logs captured (backend test failures, bandit, trivy tag, `VITE_API_BASE_URL` gap).
- [ ] Block 1 rack list accepted by the owner.
