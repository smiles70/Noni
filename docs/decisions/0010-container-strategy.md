# 0010 - Container strategy: multi-stage Dockerfiles + compose for local parity

## Status

Accepted (Sprint 11).

## Context

Until this sprint, `docker-compose.yml` orchestrated only Postgres. The backend ran on the host via `uvicorn`, and the frontend ran via `npm run dev`. That is fine for active development but creates two recurring problems:

1. **Environment drift between developers and CI/prod.** Each contributor's host installs a different Python and Node minor version. Deploys would have surfaced incompatibilities late.
2. **No reproducible "Noni-in-a-box" demo.** Showing the system to a stakeholder, an investor, or a patent attorney requires a reliable single-command boot.

A hosting / image-registry vendor decision is explicitly deferred (`docs/deferred-decisions.md`). What is *not* deferred is producing buildable images that are ready when that decision lands.

## Decision

- **Backend image** (`backend/Dockerfile`): multi-stage, `python:3.12-slim` for both stages. Builder stage installs deps into `/opt/venv`; runtime stage copies the venv plus `backend/` and `alembic/`. Runs as a non-root `noni` user (UID 10001). `HEALTHCHECK` curls `/health`.
- **Frontend image** (`frontend/Dockerfile`): multi-stage, `node:18-alpine` builds the Vite bundle, `nginx:1.27-alpine` serves it. SPA fallback in `nginx.conf` so client routing works once a router is added. Hashed assets get `Cache-Control: public, immutable`; `index.html` gets `no-cache`.
- **Compose** orchestrates `db` -> `backend` (waits on db health) -> `frontend` (depends on backend). Same host ports as the dev workflow (`8000`, `5173`) so the existing browser bookmarks and CORS allowlist keep working.
- **No image-registry vendor lock-in.** Images are buildable locally; pushing them somewhere is a deploy-time concern, not a code-time one.
- **No container scanner integrated yet.** Trivy / Grype / Snyk selection is tracked in `docs/deferred-decisions.md` and will land alongside the registry decision.

## Consequences

- `docker compose up --build` produces a fully running Noni stack from a clean clone.
- Backend deps are pinned implicitly by the Dockerfile RUN; aligning that pin set with the host venv and CI is a future cleanup (a single `requirements.txt` would help).
- The frontend container does not include Playwright. E2E remains a developer-machine concern; CI uses the dedicated `e2e` job from Sprint 8.
- Image sizes: backend ~150 MB compressed, frontend ~30 MB. Acceptable given the slim/alpine bases.
- The non-root `noni` user means any future write paths (logs, file uploads) must explicitly chown the target directories.
