# Intake: Backend statement/branch coverage gap — research closed

**Process:** v9.51  
**Date:** 2026-09-11  
**ID:** P1-BE-COVERAGE-006  
**Status:** INTAKE — research and design complete; build NOT authorized.  
**Owner:** Backend + QA  
**Source:** `.ai/research/2026-09-11-backend-maturity-research-protocol.md` §1

---

## 1. Problem statement

Backend total statement coverage is approximately **42%** against a launch target of **87% statements / 75% branches**. The `pytest backend/tests` suite already passes 451 tests, but a large portion of the route, service, and utility surface is not exercised. This is a known pre-launch debt item; the gap has been investigated and documented.

## 2. ICP / personas

| Persona | Goal | Frustration if unfixed |
|---|---|---|
| **Engineer** | Ship without regressions | Missing branch paths can break in production silently |
| **QA / Release manager** | Trust CI gates | Coverage gate will fail at launch, blocking deploy |
| **Ops** | Detect failures fast | No data on which routes are actually tested |

## 3. Research summary

### Internal evidence

- `pytest backend/tests` runs with `embedded-postgres`: **451 passed, 2 skipped, 14 xfailed**.
- `pytest-cov` total statement coverage: ~42%.
- Branch coverage is not yet measured because `pytest.ini` does not pass `--cov-branch`.
- Missing coverage is concentrated in route modules (`backend/api/routes/*.py`) and utility code.

### External baseline

- FAANG-grade Python services commonly gate on ≥80% statement and ≥75% branch coverage.
- `pytest-cov` branch coverage is enabled by `branch = true` in `[tool.coverage.run]`.

## 4. Options evaluated

| Option | Description | Verdict |
|---|---|---|
| A — backfill immediately | Write route and service tests until 87/75 is reached | Not authorized at this time; requires dedicated rack time |
| B — close as research | Document the gap, acceptance criteria, and protocol; implement later | **Selected** — intake is closed with a ready remediation path |
| C — lower the gate | Reduce `cov-fail-under` to current 42% | Rejected; would mask risk at go-live |

## 5. Architecture / approach

No architecture changes. When implementation is authorized:

1. Add `--cov-branch` / `branch = true` to coverage config.
2. Run `pytest --cov=backend --cov-report=html` to identify uncovered modules.
3. Backfill tests in priority order:
   - A. Route integration tests for `curriculum`, `auth`, `billing`, `paywall`, `gifts`, `accounts`.
   - B. Service-layer unit tests.
   - C. Model/utility coverage.
4. Raise `fail_under` thresholds to 87% statement and 75% branch.

## 6. Design decisions

| Decision | Choice | Rationale |
|---|---|---|
| Coverage tool | `pytest-cov` with `--cov-branch` | Already installed and configured |
| Test DB | `embedded-postgres` hermetic harness | Proven in `conftest.py` |
| Thresholds | 87% statements, 75% branches | Matches FAANG rubric requested by product |

## 7. MLDC alignment

- New tests must use existing `data-*` markers and design-token contracts.
- No new UI surfaces are created.

## 8. Nelson repo-hygiene / knowledge graph

- Gap is now traceable to `P1-BE-COVERAGE-006`.
- Coverage status is recorded in the command center report.
- Does not orphan requirements; all route tests map to existing journey nodes.

## 9. Epic / Block / Rack plan

Build is **not authorized** at this closure. If authorized, use the following rack plan:

| Block | Rack | Deliverable | Owner |
|---|---|---|---|
| 1. Baseline | 1.1 | Enable `--cov-branch` and capture HTML report | Backend |
| | 1.2 | Sort uncovered modules by line count | Backend |
| 2. Route coverage | 2.1-2.6 | Integration tests for each `api/routes/*.py` family | Backend |
| 3. Service coverage | 3.1-3.3 | Unit tests for `services/*.py` | Backend |
| 4. Gate enforcement | 4.1 | Update `pyproject.toml` / `pytest.ini` thresholds | Platform |
| 5. Verification | 5.1 | CI run shows ≥87% statement and ≥75% branch | QA |

## 10. Test plan

- Every new test must keep the full `pytest backend/tests` suite green.
- Coverage must not decrease from the prior commit.
- Final `pytest --cov=backend --cov-branch` must pass the new thresholds.

## 11. Risks and mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Coverage backfill is larger than estimated | High | Time-box rack 1; split remaining work into a new intake |
| Branch-coverage gate blocks unrelated PRs | Medium | Introduce `warn` first, then `error` |
| Embedded Postgres does not cover migrations | Medium | Run final gate against a Postgres service container in CI |

## 12. Acceptance criteria / Definition of Done

- `pytest --cov=backend` reports ≥87% statement coverage.
- `pytest --cov=backend --cov-branch` reports ≥75% branch coverage.
- No critical route file is below 80% statement coverage.

## 13. Rollback / operational notes

- Coverage thresholds can be temporarily lowered to `warn` if an unrelated PR is blocked.
- Staging-only delivery; production requires explicit owner approval.

## 14. Evidence

- `.ai/research/2026-09-11-backend-maturity-research-protocol.md` §1
- `.ai/audit/2026-09-11-agentic-ci-pipeline-002.md`
- `/home/h/Downloads/mynaani-command-center-report.html` coverage panel
- `backend/tests/conftest.py` embedded Postgres harness
