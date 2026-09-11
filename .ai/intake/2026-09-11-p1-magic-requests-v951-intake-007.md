# Intake: `magic-admin` / `requests` dependency conflict — research closed

**Process:** v9.51  
**Date:** 2026-09-11  
**ID:** P1-MAGIC-REQUESTS-007  
**Status:** INTAKE — BUILD AUTHORIZED — implementation ready.  
**Owner:** Security + Backend  
**Source:** `.ai/research/2026-09-11-backend-maturity-research-protocol.md` §2

---

## 1. Problem statement

`pip-audit` flags `requests==2.32.5` as vulnerable. The `magic-admin==2.5.0` package strictly pins `requests==2.32.5`, so a normal upgrade is blocked by a resolver conflict. The conflict has been reproduced and the remediation options documented.

## 2. ICP / personas

| Persona | Goal | Frustration if unfixed |
|---|---|---|
| **Security / compliance** | Pass dependency audit | CVE remains in production build |
| **Engineer** | Use safe dependency versions | Cannot upgrade `requests` without breaking `magic-admin` |
| **Ops** | Deploy without manual patches | CI `pip-audit` fails at build time |

## 3. Research summary

### Internal evidence

- `pip-audit` reported vulnerabilities in `requests 2.32.5` and `pydantic-settings 2.14.0`.
- `pydantic-settings` and `pip` were upgraded cleanly.
- `magic-admin==2.5.0` requires `requests==2.32.5` exactly.
- Upgrading `requests` to `2.34.2` makes `pip check` fail.

### External baseline

- `pip-audit` and `safety` are standard Python dependency-audit tools.
- Best practice is to remove or upgrade the transitive pin rather than ignore the advisory.

## 4. Options evaluated

| Option | Description | Verdict |
|---|---|---|
| A — upgrade `magic-admin` | Check for a newer release with unpinned `requests` | **Recommended first step** |
| B — vendor a minimal client | Replace `magic-admin` with a thin direct API client | Viable if Option A fails |
| C — pin a patched fork | Use a fork of `magic-admin` that allows secure `requests` | Not preferred; increases maintenance |
| D — accept risk | Suppress the CVE and keep the pin | **Rejected** — launch security risk |

## 5. Architecture / approach

No architecture changes. When implementation is authorized:

1. Search PyPI for `magic-admin > 2.5.0` and attempt a clean `pip install` with `requests>=2.33.0`.
2. If no safe `magic-admin` version exists, evaluate a minimal direct client.
3. Update `pyproject.toml` constraints.
4. Run auth tests and `pip-audit`.

## 6. Design decisions

| Decision | Choice | Rationale |
|---|---|---|
| Target `requests` | `>=2.33.0` or latest non-vulnerable | Fixes the CVE |
| Test path | `backend/tests/test_auth*.py` | Verifies Magic integration still works |
| Audit gate | `pip-audit` in CI | Prevents reintroduction |

## 7. MLDC alignment

- No UI changes.
- Auth flow contract remains unchanged.

## 8. Nelson repo-hygiene / knowledge graph

- Conflict is now traceable to `P1-MAGIC-REQUESTS-007`.
- Dependency risk is recorded in the command center report.

## 9. Epic / Block / Rack plan

Build is **not authorized** at this closure. If authorized:

| Block | Rack | Deliverable | Owner |
|---|---|---|---|
| 1. Investigate | 1.1 | Test `magic-admin` versions on PyPI | Security |
| | 1.2 | Document `requests` usage in `magic-admin` | Security |
| 2. Resolve | 2.1 | Upgrade `magic-admin` or replace with direct client | Backend |
| 3. Validate | 3.1 | Run auth tests and `pip-audit` | QA |

## 10. Test plan

- `pip-audit` reports zero vulnerabilities.
- `pip check` passes.
- `pytest backend/tests/test_auth*.py` passes.

## 11. Risks and mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Newer `magic-admin` has breaking changes | Medium | Pin upper bound and run full auth test suite |
| Replacing `magic-admin` takes longer than expected | High | Time-box spike; fall back to vendor fork if needed |

## 12. Acceptance criteria / Definition of Done

- `pip-audit` shows no `requests` CVEs.
- `pip check` is clean.
- All authentication tests pass.

## 13. Rollback / operational notes

- Lock `requests` to a non-vulnerable version in `pyproject.toml`.
- Staging-only deploy; production requires explicit owner approval.

## 14. Evidence

- `.ai/research/2026-09-11-backend-maturity-research-protocol.md` §2
- `.ai/audit/2026-09-11-agentic-ci-pipeline-002.md` security section
- `/home/h/Downloads/mynaani-command-center-report.html` security panel
