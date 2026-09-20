# Backend Maturity Research Protocol

Pipeline: `feat/agentic-ci-audit-pipeline-001`  
Status: initiated 2026-09-11  

## Blocker 1 — Backend coverage is ~42% (target: 87% statement / 75% branch)

### Definition
**Statement coverage** is the percentage of executable Python statements that were exercised by the test suite. **Branch coverage** is the percentage of `if`/`else`/`elif`/`try`/`except`/loop decision branches taken at least once.

### Current evidence
- Full backend run: `451 passed, 2 skipped, 14 xfailed`.
- `pytest-cov` reports approximately **42% total statement coverage** for the `backend` package.
- Branch coverage has not yet been measured because `pytest.ini` does not pass `--cov-branch`.

### Research questions
1. Which backend modules have zero or near-zero test coverage?
2. Which route families are missing contract/integration tests?
3. Are utility modules, exception branches, and validation logic covered?
4. What is the realistic delta between 42% and 87% in terms of net-new tests?

### Proposed protocol
1. Run `pytest --cov=backend --cov-report=html` and open `htmlcov/index.html`.
2. Export the missing-coverage file list and sort by line count.
3. Group modules into:
   - A. Route layer (`api/routes/*`) — highest priority for launch.
   - B. Service layer (`services/*`) — business logic.
   - C. Model & utility layer (`models/*`, `core/*`, `utils/*`).
4. For each route family (curriculum, auth, billing, paywall, gifts, accounts), write
   at least one integration test using the embedded Postgres harness.
5. Re-run coverage and record deltas until statement ≥ 87% and branch ≥ 75%.

### Acceptance criteria
- `pytest --cov=backend --cov-branch` passes `fail_under=75` for branch.
- Total statement coverage ≥ 87%.
- No critical route file is below 80% statement coverage.

---

## Blocker 2 — `magic-admin` pins a vulnerable `requests` version

### Definition
A **transitive dependency conflict** occurs when a pinned sub-dependency in one package blocks the version that resolves a security advisory in another package.

### Current evidence
- `pip-audit` flagged `requests==2.32.5` with known CVEs.
- `magic-admin==2.5.0` declares `requests==2.32.5` as an exact dependency.
- Upgrading `requests` to `2.34.2` makes `pip check` fail:
  ```text
  magic-admin 2.5.0 requires requests==2.32.5, but you have requests 2.34.2
  ```

### Research questions
1. Does `magic-admin` actually import the parts of `requests` that are vulnerable?
2. Is there a newer `magic-admin` release with an unpinned or patched `requests`?
3. Can `magic-admin` be replaced by direct `did`/`siwe` or Magic Link SDK calls?
4. If `magic-admin` cannot be upgraded, can we pin a patched fork or vendor the package?

### Proposed protocol
1. Inspect `magic-admin` source for its `requests` usage (likely `magic_admin/http_client.py`).
2. Check PyPI for `magic-admin` versions newer than 2.5.0 and test `pip-audit` after each.
3. If no safe version exists, evaluate:
   - Replacing `magic-admin` with `magic-admin-py` or direct API calls.
   - Vendoring a minimal `magic-admin` client that permits a secure `requests`.
4. Update `pyproject.toml` and run `backend/tests/test_auth*.py` plus a manual `pip-audit`.

### Acceptance criteria
- `pip-audit` reports zero vulnerabilities in the `requests` lineage.
- `pip check` passes.
- All auth-related tests still pass.

---

## Blocker 3 — Branch-coverage gate is not yet wired in CI

### Definition
A **branch-coverage gate** enforces that every decision point (e.g., `if`, `else`, `try`/`except`) has been executed at least once, not just every line.

### Current evidence
- `pytest.ini` only sets `--cov-fail-under=85` for overall (statement) coverage.
- `pyproject.toml` `[tool.coverage.run]` does not set `branch = true`.

### Research questions
1. Does enabling `branch = true` change the current `fail_under` behavior?
2. What is the branch-coverage percentage if enabled now?
3. Which critical paths have untested branches?

### Proposed protocol
1. Temporarily add `branch = true` under `[tool.coverage.run]` in `pyproject.toml`.
2. Run `pytest --cov=backend --cov-report=term-missing` and record the branch metric.
3. Add missing tests for the most impactful untested branches.
4. Set a separate branch-coverage threshold in CI (≥ 75%).
5. Consider splitting gates:
   - `pytest --cov=backend --cov-fail-under=87` (statement)
   - `coverage report --fail-under=75` after `coverage combine` (branch)

### Acceptance criteria
- CI runs branch coverage by default.
- Branch coverage ≥ 75% and statement coverage ≥ 87% both pass.

---

## Blocker 4 — Feature flags, Alembic downgrade validation, and PII/GDPR scan are not implemented

### Definition
- **Feature flags** are runtime toggles (often env-var or database-backed) that allow canary or dark-launch without code deployment.
- **Alembic downgrade validation** is the practice of proving a migration can be rolled back without data loss.
- **PII/GDPR scan** is the audit of code and logs for unmasked personal data.

### Current evidence
- No feature-flag middleware or configuration exists.
- `alembic downgrade` has not been exercised in CI; the `0003` migration requires `pgcrypto`.
- Telemetry and logging may include raw emails, names, or billing tokens.

### Research questions
1. What is the minimal env-var feature-flag implementation the app can use?
2. Which migrations are downgrade-safe vs. destructive?
3. Where does the backend log or store PII?
4. Which telemetry fields are personal data vs. aggregate?

### Proposed protocol
1. Add `backend/core/feature_flags.py` with `os.environ`-backed flags and FastAPI middleware.
2. Create a test that runs `alembic upgrade head` and `alembic downgrade -1` in the CI Postgres service.
3. Run `grep -R "email\|name\|token\|password\|billing" backend/ --include="*.py"` and classify each hit.
4. Add PII masking in `backend/app/telemetry.py` or a custom `structlog`/`logging` filter.
5. Add a `PII_SANITIZE_FIELDS` config and a `test_pii_masking.py` suite.

### Acceptance criteria
- Feature flag can disable a route or behavior via env var without redeploy.
- `alembic upgrade head && alembic downgrade -1` runs in CI with no exceptions.
- No email, name, token, or billing detail is emitted to logs without masking.

---

## Blocker 5 — Workflow file needs a token with `workflow` scope

### Definition
The **GitHub `workflow` OAuth scope** is required to push files under `.github/workflows/`. Without it, GitHub rejects pushes that create or modify workflow files.

### Current evidence
- `.github/workflows/a10-smoke.yml` has been corrected and committed locally.
- Push failed with:
  ```text
  refusing to allow an OAuth App to create or update workflow
  `.github/workflows/a10-smoke.yml` without `workflow` scope
  ```

### Research questions
1. Which token is currently configured in the local git remote?
2. Does the user have a PAT with `workflow` scope available?
3. Can the workflow be pushed via the GitHub web UI instead?

### Proposed protocol
1. Re-authenticate `git` with a token that has `workflow` scope:
   ```bash
   git remote set-url origin https://<TOKEN>@github.com/smiles70/Noni.git
   git push origin feat/agentic-ci-audit-pipeline-001
   git push origin feat/agentic-ci-audit-pipeline-001:staging
   ```
2. Alternative: open the corrected `.github/workflows/a10-smoke.yml` in the GitHub web UI and commit it manually.
3. Validate the workflow runs on the next push/PR to `backend/**`.

### Acceptance criteria
- `.github/workflows/a10-smoke.yml` is present in the remote `staging` branch.
- The workflow can be triggered manually (`workflow_dispatch`) and completes successfully.

---

## Glossary of test & quality terms

| Term | Definition |
|---|---|
| **Unit test** | A test that verifies a single function, class, or module in isolation, often with mocks. |
| **Integration test** | A test that verifies multiple components (e.g., route + database) work together with a real dependency. |
| **End-to-end (E2E) test** | A test that drives the browser or full stack through real user flows, e.g., Playwright. |
| **Smoke test** | A minimal, fast suite that confirms the application can start and the most critical path works. |
| **Load test** | A performance test that measures response time and throughput under a defined level of simulated traffic. |
| **Chaos test** | A resiliency test that introduces failures (slow DB, expired tokens, rate spikes) to verify graceful degradation. |
| **SAST** | Static Application Security Testing — analyzing source code for vulnerabilities without executing it. |
| **Dependency audit** | Scanning installed packages for known CVEs, e.g., `pip-audit` or `safety`. |
| **xfail** | A pytest marker indicating a test is expected to fail; if it unexpectedly passes, the suite fails. |
| **Expected failure** | A test intentionally written to fail (e.g., `it.fails` in Vitest) to track unimplemented behavior. |
| **Statement coverage** | Percentage of executable source lines that were run during testing. |
| **Branch coverage** | Percentage of decision branches (if/else/try/except) that were taken during testing. |
| **Liveness probe** | A health endpoint that returns 200 as long as the process is running. |
| **Readiness probe** | A health endpoint that checks the app can serve traffic (e.g., database connectivity). |
| **Feature flag** | A runtime toggle that controls feature availability without a new deployment. |
| **PII** | Personally Identifiable Information — data that can identify an individual. |
| **GDPR** | General Data Protection Regulation — EU privacy law with data minimization and right-to-erasure rules. |
| **Alembic** | SQLAlchemy migration tool used to manage database schema changes. |
| **pgcrypto** | PostgreSQL extension providing cryptographic functions, required by the `0003` migration. |

---

## Next steps

1. Address `magic-admin` / `requests` conflict first — it is a launch security risk.
2. Add branch coverage configuration and the first wave of route integration tests.
3. Implement the feature-flag module and PII masker in parallel.
4. Validate Alembic downgrades in the CI Postgres service.
5. Re-authenticate with a `workflow` scoped token and push the corrected A10 smoke workflow.
