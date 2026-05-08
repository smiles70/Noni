# 0005 — Alembic migrations replace `Base.metadata.create_all()`

## Status

Accepted (Sprint 4).

## Context

Earlier sprints used `Base.metadata.create_all(bind=engine)` in the FastAPI lifespan to materialize tables on first run. This is convenient for scaffolding but is unsuitable for any environment with persisted data:

- No history of schema changes.
- No reversibility.
- No coordination with deploy pipeline (cannot run migrations *before* the new app version starts).
- No ability to backfill, rename, or restructure columns safely.

Fortune-500 production discipline requires every schema change to be a reviewable, forward-only (or downgrade-explicit) migration committed to the repo.

## Decision

- Adopt **Alembic** for all schema changes.
- `alembic/env.py` reads `DATABASE_URL` from `backend.core.config.settings`.
- All ORM model modules are imported in `env.py` so `Base.metadata` is populated for autogenerate.
- The FastAPI `lifespan` calls `run_migrations()` (which executes `alembic upgrade head`) on startup. This is acceptable for development; production deploys should run migrations as a *separate pipeline step* before the new container version is rolled out.
- The original `init_db()` (calling `create_all`) is removed from production code paths.
- Existing dev databases are reconciled via `alembic stamp head` to mark them as already at the baseline revision.

## Consequences

- Every model change now requires `alembic revision --autogenerate -m "describe change"` and a code review of the generated SQL.
- Production deploys gain a clean rollback story: revert app version + `alembic downgrade -1`.
- CI runs `alembic upgrade head` against an ephemeral Postgres before tests, exercising every migration.
- New developers must run `alembic upgrade head` once after cloning (or rely on the lifespan to do it on first startup).
