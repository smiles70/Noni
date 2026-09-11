# Intake: Branch-coverage CI gate not wired — research closed

**Process:** v9.51  
**Date:** 2026-09-11  
**ID:** P1-CI-BRANCH-COVERAGE-008  
**Status:** INTAKE — research and design complete; build NOT authorized.  
**Owner:** Platform + QA  
**Source:** `.ai/research/2026-09-11-backend-maturity-research-protocol.md` §3

---

## 1. Problem statement

The `pytest.ini` coverage gate only enforces total (statement) coverage with `--cov-fail-under=85`. Branch coverage is not measured or gated. Once coverage improves, a separate branch-coverage gate (≥75%) must be added to CI to meet the FAANG-grade rubric.

## 2. ICP / personas

| Persona | Goal | Frustration if unfixed |
|---|---|---|
| **Engineer** | Know which branches are untested | Can merge code with untested `else`/`except` paths |
| **QA / Release manager** | Trust CI gates | Statement coverage alone misses critical failure branches |
| **Ops** | Stable deploys | Untested branches may fail in production |

## 3. Research summary

### Internal evidence

- `pytest.ini` contains `--cov=backend --cov-report=term-missing --cov-fail-under=85`.
- `pyproject.toml` `[tool.coverage.run]` does not set `branch = true`.
- Branch coverage percentage is currently unknown because it is not enabled.

### External baseline

- `coverage.py` branch coverage is enabled by `branch = true`.
- `pytest-cov` can output a combined report but cannot enforce two thresholds simultaneously in one run.

## 4. Options evaluated

| Option | Description | Verdict |
|---|---|---|
| A — add `branch = true` and raise total gate | Enable branch coverage in the existing run | **Recommended** as first step |
| B — two-stage CI gate | Run statement gate, then branch gate in a second step | **Recommended** for enforcement |
| C — only statement gate | Keep current behavior | Rejected; does not meet the rubric |

## 5. Architecture / approach

When implementation is authorized:

1. Add `branch = true` to `[tool.coverage.run]` in `pyproject.toml`.
2. Measure current branch coverage.
3. Add a CI step that runs `coverage report --fail-under=75` after `pytest` collects branch data.
4. Optionally keep `--cov-fail-under=87` for statement coverage.

## 6. Design decisions

| Decision | Choice | Rationale |
|---|---|---|
| Branch coverage tool | `coverage.py` built-in | No new dependency |
| Statement threshold | 87% | Matches FAANG target |
| Branch threshold | 75% | Matches FAANG target |

## 7. MLDC alignment

- No product or UI changes.
- Test code only.

## 8. Nelson repo-hygiene / knowledge graph

- Tracked as `P1-CI-BRANCH-COVERAGE-008`.
- Linked to `P1-BE-COVERAGE-006` and `P1-TEST-MATURITY-004`.

## 9. Epic / Block / Rack plan

Build is **not authorized** at this closure. If authorized:

| Block | Rack | Deliverable | Owner |
|---|---|---|---|
| 1. Baseline | 1.1 | Enable branch coverage and record current % | Platform |
| 2. Gate wiring | 2.1 | Add CI step for branch-coverage threshold | Platform |
| 3. Verification | 3.1 | CI run shows branch ≥75% | QA |

## 10. Test plan

- `pytest --cov=backend --cov-branch` runs without errors.
- `coverage report --fail-under=75` passes.
- Statement coverage gate still passes at 87%.

## 11. Risks and mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Branch-coverage gate blocks in-flight PRs | Medium | Set `warn` for one sprint before `error` |

## 12. Acceptance criteria / Definition of Done

- `pyproject.toml` has `branch = true`.
- CI enforces branch coverage ≥75%.
- Statement coverage ≥87% is also enforced.

## 13. Rollback / operational notes

- The branch gate can be disabled by reverting the CI step.
- Staging-only; production requires explicit owner approval.

## 14. Evidence

- `.ai/research/2026-09-11-backend-maturity-research-protocol.md` §3
- `.ai/audit/2026-09-11-agentic-ci-pipeline-002.md`
- `pytest.ini`
- `pyproject.toml`
