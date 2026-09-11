# Agentic CI Pipeline — Backend Maturity Pass

Pipeline: `feat/agentic-ci-audit-pipeline-001`
Date: 2026-09-11

## Phase 1 — Backend integration tests with real PostgreSQL

- Added `embedded-postgres` to `backend/tests/conftest.py` so the full 460-test suite runs hermetically without Docker or system Postgres.
- `conftest.py` now starts an isolated Postgres server, enables `citext`, and creates the schema from SQLAlchemy `Base.metadata` (avoiding the `pgcrypto` extension used by the production Alembic migration).
- Updated `backend/models/telemetry.py` to mirror the `telemetry_events` additive columns from `alembic/versions/0003_launch_schema.py` (`account_id`, `session_id`, `unit_id`, `occurred_at`, `expires_at`).
- Repaired `.github/workflows/a10-smoke.yml` (malformed top lines, missing install step) and added a full `backend/tests` run plus Postgres service container.

### Verification

```text
$ .venv/bin/python -m pytest backend/tests --no-cov -q
451 passed, 2 skipped, 14 xfailed, 3 warnings in 7.43s
```

## Phase 2 — Security scanning

- `bandit -r backend`: 1,026 low-severity findings (B101 assertions in tests, B105/B106 hardcoded strings in test/config fixtures); zero medium/high severity issues.
- `pip-audit`: zero known vulnerabilities after upgrading `pydantic-settings` and `pip`.
- Dependency conflict discovered: `magic-admin==2.5.0` pins `requests==2.32.5`, which `pip-audit` flags as vulnerable. `requests` was upgraded to `2.34.2` locally, but this conflicts with `magic-admin`. Resolution requires a `magic-admin` update or removal; flagged in the report and left as a deferred dependency risk.

## Phase 3 — Backend load test

- Added `scripts/agentic-ci/backend-smoke-start.py` to boot the backend with an embedded Postgres instance.
- Added `scripts/agentic-ci/backend-load.js` (k6) targeting `/health`, `/api/v1/landing/page`, and `/api/v1/curriculum/menu` with 25 VUs.

### Verification

```text
http_req_duration p(95): 14.75 ms  (< 500 ms threshold)
http_req_failed:        0.19%       (< 1% threshold)
checks:                 99.90%
iterations:             524
requests:               1,572
```

`0.19%` failures were three `connection refused` errors at the very first second before the server finished binding; once bound, zero unexpected failures. The `/api/v1/curriculum/menu` route returned `429` under load, confirming the rate-limiter is shedding traffic as designed.

## Phase 4 — Expected-failure triage

- Backend `xfail`: 14 tests in `backend/tests/test_login_constraints.py` are intentionally marked `@pytest.mark.xfail(strict=True, reason="redesign-pending: T-XX")`. They track the same `T-A1` through `T-H2` design tickets as the frontend contract stubs.
- Frontend `it.fails`: 15 tests in `frontend/src/__tests__/login_contract.test.ts` are `it.fails` placeholders for the same redesign cycle.
- Status: deferred design-debt (login/state-machine redesign); not launch-blocking bugs. Issue IDs are not yet assigned; recommend creating GitHub tracking issues `T-A1`..`T-H2` before launch.

## Phase 5 — CI gate enforcement

- `pyproject.toml` `[project.optional-dependencies]` updated to include `pytest-cov`, `embedded-postgres`, and `bandit` in `dev`, plus a `test` extra.
- `a10-smoke.yml` repaired and now runs migrations plus the full backend test suite on pushes/PRs to `main` and `staging`.
- Coverage enforcement: `pytest.ini` still enforces `--cov-fail-under=85`. Current total statement coverage from the backend suite is ~42%, so the coverage gate will fail until more backend route/service tests are added.
- Branch coverage is not yet configured as a separate gate. Recommended next step: split coverage gate into statement (≥87%) and branch (≥75%) checks in CI.

## Phase 6 — Production readiness (partial)

- Added `/health/live` and `/health/ready` probes in `backend/app/main.py`:
  - `/health/live`: returns `{"status":"alive"}` for liveness.
  - `/health/ready`: executes `SELECT 1` against Postgres via `backend.core.database.engine`; returns `503` if the DB is unreachable.
- Feature-flag module, migration rollback automation, and PII/GDPR scanning are not yet implemented.

## Files changed

```text
backend/app/main.py
backend/models/telemetry.py
backend/tests/conftest.py
pyproject.toml
.github/workflows/a10-smoke.yml
scripts/agentic-ci/backend-smoke-start.py   (new)
scripts/agentic-ci/backend-load.js           (new)
.ai/audit/2026-09-11-agentic-ci-pipeline-002.md (new)
```

## Verification commands

```bash
.venv/bin/python -m pytest backend/tests --no-cov -q
.venv/bin/bandit -r backend -ll -ii
.venv/bin/python -m pip_audit
.venv/bin/python scripts/agentic-ci/backend-smoke-start.py &
export PATH="$HOME/.local/bin:$PATH"
k6 run scripts/agentic-ci/backend-load.js
```

## Remaining blockers

1. Coverage is 42% — far below the 85% launch gate. Need focused backend route/service unit tests.
2. `magic-admin` pins `requests==2.32.5` (CVE). Needs vendor update or replacement.
3. Branch-coverage gate is not yet wired.
4. Feature flags, migration rollback, and PII scanning still to implement.
