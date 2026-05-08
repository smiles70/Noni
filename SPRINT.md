# Sprint 4: Engineering Foundations (CLOSED)

Goal: enforce quality gates and adopt production-grade migration discipline.

## Phases

- 4.1 Pre-commit hooks (ruff + black + standard hygiene hooks)
- 4.2 GitHub Actions CI workflow (backend + frontend, with Postgres service)
- 4.3 Alembic migrations replacing `create_all()`; lifespan runs `upgrade head`
- 4.4 ADRs 0002-0005 (Postgres, Vite+TS, tooling, Alembic)
- 4.5 Closeout

## Deferred (will surface in next sprint planning)

- Sprint 5 (Landing Copy & UI): requires draft copy decision (you write / I draft / we co-author?)
- Sprint 6 (Auth + Per-Learner State): requires auth provider choice (Auth0 / Clerk / Cognito / self-hosted JWT?)
- Sprint 7 (Real Claude Integration): requires Anthropic API key
