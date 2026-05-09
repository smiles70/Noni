# Sprint 11: Containerization (CLOSED)

Tag: `sprint-11-containers-v1`. Adds production-grade multi-stage Dockerfiles for backend + frontend and wires them into compose so `docker compose up --build` produces a runnable Noni stack from a clean clone.

## Phases

- 11.1 `backend/Dockerfile` (multi-stage, python:3.12-slim, non-root user, healthcheck)
- 11.2 `frontend/Dockerfile` (multi-stage, node:18-alpine -> nginx:1.27-alpine) + `nginx.conf` (SPA fallback, asset caching)
- 11.3 `docker-compose.yml` extended with backend + frontend services and proper depends_on/healthcheck wiring
- 11.4 `.dockerignore` files for both contexts
- 11.5 ADR 0010: container strategy
- 11.6 README updated with Docker run section
- 11.7 Closeout

## Out of scope

- Image registry / hosting vendor selection (`docs/deferred-decisions.md`)
- Container scanning (Trivy / Grype / Snyk)
- Pinning a `requirements.txt` so dev/CI/Docker share an exact version set (cleanup follow-on)
