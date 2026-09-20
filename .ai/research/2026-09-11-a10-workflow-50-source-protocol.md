# 50-Source Research Protocol: A10 / Backend Smoke CI Maturity

Protocol ID: `A10-50-SRC-001`
Date: 2026-09-11
Scope: backend A10 smoke, GitHub Actions, Postgres, psycopg2, OAuth, alembic, FastAPI/SQLAlchemy testing

## Method

Each source is classified by `type` and `relevance` to the A10 smoke problem:
- `GHA` — GitHub Actions docs or patterns
- `OAUTH` — token / permission scope docs
- `PG` — PostgreSQL / psycopg2 build
- `AL` — Alembic / migrations
- `TEST` — FastAPI / SQLAlchemy / pytest testing
- `LOCAL` — repository-internal source

---

## Sources 1–50

1. **GitHub Docs — Scopes for OAuth Apps** (OAUTH)
   - https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps
   - Defines the `workflow` scope needed to commit `.github/workflows/*` files.

2. **GitHub Docs — Authenticating to the REST API** (OAUTH)
   - https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api
   - Token types and required scopes.

3. **GitHub Docs — Permissions for Fine-Grained PATs** (OAUTH)
   - https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens
   - Fine-grained token permissions for workflows.

4. **GitHub Docs — Authenticating with an OAuth App** (OAUTH)
   - https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authenticating-to-the-rest-api-with-an-oauth-app
   - OAuth flow and scope checking.

5. **GitHub Docs — REST API Endpoints for OAuth Authorizations** (OAUTH)
   - https://docs.github.com/en/rest/apps/oauth-applications
   - Token prefixes and scope enumeration.

6. **psycopg2 — Installation Docs** (PG)
   - https://www.psycopg.org/docs/install.html
   - Build prerequisites for `psycopg2` vs `psycopg2-binary`.

7. **Latchkey — pip psycopg2 pg_config not found in CI** (PG)
   - https://latchkey.dev/learn/python/pip-psycopg2-pg-config-not-found
   - Why source builds fail when `libpq-dev` is missing.

8. **Latchkey — psycopg2 pg_config not found (CI)** (PG)
   - https://latchkey.dev/learn/python/python-pgconfig-not-found-in-ci
   - Recommends `psycopg2-binary` in CI.

9. **Latchkey — Django psycopg2 libpq build error in CI** (PG)
   - https://latchkey.dev/learn/python/django-psycopg2-libpq-build-error-in-ci
   - `apt-get install libpq-dev gcc` for source builds.

10. **Simon Willison — PostgreSQL Service Container in GitHub Actions** (GHA)
    - https://til.simonwillison.net/github-actions/postgresq-service-container
    - `DATABASE_URL` pattern using `job.services.postgres.ports['5432']`.

11. **quiver/github-actions-service-container-sample-python** (GHA)
    - https://github.com/quiver/github-actions-service-contaner-sample-python
    - Sample repo with Postgres service containers in Actions.

12. **GitHub Docs — Creating PostgreSQL Service Containers** (GHA)
    - https://github.com/github/docs/blob/main/content/actions/tutorials/use-containerized-services/create-postgresql-service-containers.md
    - Official tutorial on `services: postgres:`.

13. **Rex Bytes — GitHub Actions CI/CD 6/10: Integration Tests** (GHA)
    - https://rexbytes.com/2026/02/21/github-actions-ci-cd-6-10-integration-tests/
    - Real Postgres integration tests with `psycopg[binary]`.

14. **The Axiom — Docker Service Containers for CI Testing** (GHA)
    - https://elliot-digital.co.uk/technical-qa/docker-ci-testing
    - Service container health checks and port mapping.

15. **sudzxd/alembic-deploy-action** (AL)
    - https://github.com/sudzxd/alembic-deploy-action
    - GitHub Action for Alembic dry-run and safe migrations.

16. **DevGlitch/alembic-migration-checker** (AL)
    - https://github.com/DevGlitch/alembic-migration-checker
    - Action to verify Alembic migration version alignment.

17. **StackLesson — Alembic in CI/CD** (AL)
    - https://www.stacklesson.com/react-fastapi/fastapi-alembic/ch25-lesson-05-alembic-in-ci-cd/
    - Running `alembic upgrade head` in GitHub Actions with health checks.

18. **letta-ai/alembic-validation.yml** (AL)
    - https://github.com/letta-ai/letta/blob/main/.github/workflows/alembic-validation.yml
    - Real project workflow for Alembic validation with self-hosted Postgres.

19. **fojin/alembic-dry-run.yml** (AL)
    - https://github.com/xr843/fojin/blob/main/.github/workflows/alembic-dry-run.yml
    - Alembic dry-run with Postgres service container and `pg_isready` wait loop.

20. **Ugur Aslim — Testing FastAPI + SQLAlchemy with Real PostgreSQL** (TEST)
    - https://uguraslim.com/blog/testing-fastapi-sqlalchemy-with-real-postgresql-fixtures-no-/
    - Docker Compose + pytest fixtures for real DB isolation.

21. **SP-Lutsk — Testing FastAPI with Pytest and SQLAlchemy** (TEST)
    - https://sp-lutsk.com/blog/testing-fast-api
    - SQLAlchemy setup for FastAPI tests.

22. **benavlabs/FastAPI-boilerplate — Testing Docs** (TEST)
    - https://github.com/benavlabs/FastAPI-boilerplate/blob/main/docs/user-guide/testing.md
    - Boilerplate with `testcontainers-postgres` and pytest markers.

23. **Praciano — FastAPI and Async SQLAlchemy 2.0 with pytest** (TEST)
    - https://praciano.com.br/fastapi-and-async-sqlalchemy-20-with-pytest-done-right.html
    - Async DB testing with `psycopg` and `pytest-postgresql`.

24. **DEV Community — FastAPI Endpoints with PostgreSQL Integration Tests** (TEST)
    - https://dev.to/uaslimcreate/testing-fastapi-endpoints-from-unit-tests-to-integration-tests-with-postgresql-36dj
    - `conftest.py` with real PostgreSQL `DATABASE_URL`.

25. **GitHub Docs — Workflow Syntax for GitHub Actions** (GHA)
    - https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
    - Reference for `jobs`, `services`, `steps`, `env`, `timeout-minutes`.

26. **GitHub Docs — Workflow Commands for GitHub Actions** (GHA)
    - https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions
    - `::set-output`, `::error`, masking values.

27. **GitHub Docs — Using Environments in Actions** (GHA)
    - https://docs.github.com/en/actions/learn-github-actions/environment-variables
    - How `env` maps into steps and service connections.

28. **GitHub Docs — Using Secrets in GitHub Actions** (GHA)
    - https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions
    - Where `DATABASE_URL` secrets should live.

29. **GitHub Docs — Reusing Workflows** (GHA)
    - https://docs.github.com/en/actions/using-workflows/reusing-workflows
    - Patterns for sharing smoke-test workflows across repos.

30. **PostgreSQL Docker Hub Image** (PG)
    - https://hub.docker.com/_/postgres
    - `postgres:15` env vars and health-check behavior.

31. **psycopg2-binary PyPI** (PG)
    - https://pypi.org/project/psycopg2-binary/
    - Binary wheel metadata and version matrix.

32. **Alembic Documentation** (AL)
    - https://alembic.sqlalchemy.org/en/latest/
    - `alembic upgrade head`, `alembic check`.

33. **SQLAlchemy 2.0 Documentation** (TEST)
    - https://docs.sqlalchemy.org/en/20/
    - Engine, session, and testing patterns.

34. **FastAPI — Testing Tutorial** (TEST)
    - https://fastapi.tiangolo.com/tutorial/testing/
    - `TestClient` and dependency overrides.

35. **pytest Documentation** (TEST)
    - https://docs.pytest.org/en/stable/
    - Fixtures, markers, and `pytest -v`.

36. **FastAPI TestClient Reference** (TEST)
    - https://fastapi.tiangolo.com/reference/testclient/
    - In-process HTTP testing against FastAPI apps.

37. **Pydantic Settings** (TEST)
    - https://docs.pydantic.dev/latest/concepts/pydantic_settings/
    - How `DATABASE_URL` is loaded from env.

38. **python-dotenv** (TEST)
    - https://saurabh-kumar.com/python-dotenv/
    - `.env` file loading in the repo.

39. **Magic Admin Python SDK** (TEST)
    - https://magic.link/docs/auth/api-reference/server-side-sdks/python
    - Mock auth in `MockAuthProvider`.

40. **redis-py Documentation** (TEST)
    - https://redis.readthedocs.io/en/stable/
    - Redis client used in backend.

41. **Uvicorn Documentation** (TEST)
    - https://www.uvicorn.org/
    - ASGI server for FastAPI smoke.

42. **Railway Docs** (LOCAL/TEST)
    - https://docs.railway.app/
    - Deployment target for the A10 backend.

43. **GitHub Docs — Caching Dependencies** (GHA)
    - https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows
    - Caching `pip` and `node_modules` to speed smoke gates.

44. **Pydantic Settings — Loading from Environment Variables** (TEST)
    - https://docs.pydantic.dev/latest/concepts/pydantic_settings/#environment-variable-names
    - `DATABASE_URL` / `DATABASE_URL_DIRECT` precedence.

45. **psycopg 3 Installation** (PG)
    - https://www.psycopg.org/psycopg3/docs/basic/install.html
    - Alternative driver if `psycopg2-binary` wheels fail.

46. **GitHub Docs — Use GITHUB_TOKEN in Workflows** (OAUTH)
    - https://docs.github.com/en/actions/security-guides/automatic-token-authentication
    - Why `GITHUB_TOKEN` inside a workflow cannot be used to push workflow changes.

47. **Mynaani Process v9.51 — PREFLIGHT Testing Maturity 004** (LOCAL)
    - `.ai/process/PREFLIGHT_TESTING_MATURITY_004_R1_001.md`
    - Current preflight evidence and Block 5 gates.

48. **Mynaani A10 Smoke Test** (LOCAL)
    - `backend/tests/test_a10_smoke.py`
    - The target test covering 7 paid/free/gift/entitlement scenarios.

49. **Mynaani Backend Configuration** (LOCAL)
    - `backend/core/config.py`
    - How `DATABASE_URL` and `DATABASE_URL_DIRECT` are loaded.

50. **Mynaani Python Project Metadata** (LOCAL)
    - `pyproject.toml`
    - Runtime and dev dependencies for the backend.

---

## Synthesis

- The `workflow` OAuth scope is the only blocker to committing `.github/workflows/a10-smoke.yml` through `git`.
- `psycopg2-binary` source build can be avoided with a compatible wheel; if not, install `libpq-dev` and `python3-dev`.
- `alembic` is not in `pyproject.toml` and must be installed explicitly in CI or added to dependencies.
- Postgres service containers are the canonical pattern for isolated A10 smoke.
- Real FastAPI/SQLAlchemy tests use `TestClient` + a real Postgres instance + `DATABASE_URL`.
