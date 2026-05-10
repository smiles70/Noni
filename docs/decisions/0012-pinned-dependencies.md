# 0012 - Pinned Python dependencies via requirements files

## Status

Accepted (Sprint 14).

## Context

Until this sprint, backend Python dependencies were specified four times in four different places, each with no version pins:

1. The README setup steps (`pip install fastapi 'uvicorn[standard]' ...`).
2. `CONTRIBUTING.md` (same list, slightly different wording).
3. `.github/workflows/ci.yml` (twice: the `backend` job and the `e2e` job).
4. `backend/Dockerfile` (the builder stage `RUN pip install`).

Any time a dep got added, removed, or upgraded, four places had to be edited in lockstep, and they regularly drifted in practice. There was also nothing preventing CI or a fresh dev machine from picking up a newer breaking release of fastapi/pydantic/sqlalchemy on a Tuesday and silently failing on a Wednesday.

A vendor-grade Python project pins its deps and installs from one file. Tools like `pip-tools` or `uv` go further (lockfiles for transitive deps), but those carry their own onboarding cost. For Sprint 14 we pin only the **direct** deps and let pip resolve transitives consistent with that set; that catches 90% of drift while keeping the toolchain familiar.

## Decision

- **`requirements.txt`** — runtime deps only (fastapi, uvicorn, pydantic, sqlalchemy, psycopg2-binary, alembic, numpy, python-dotenv, httpx, pydantic-settings). Each pinned to the exact version verified across Sprints 8-13.
- **`requirements-dev.txt`** — starts with `-r requirements.txt`, then adds `pytest`, `ruff`, `black`, `mypy`, `pre-commit`. Used by contributors and the backend CI job.
- The backend `Dockerfile`, CI workflow (both `backend` and `e2e` jobs), README, and CONTRIBUTING.md all install via `pip install -r ...` against these files. **No raw package list survives in any of the four old locations.**
- Upgrades are now a single-file edit + a single CI run.
- Lockfile-style transitive pinning (pip-tools / uv / poetry) is **deferred**. We will adopt one once we have an explicit reason (CVE response time, reproducible-build SLA, etc.).

## Consequences

- One-line dep upgrades. Reviewers see exactly which version moved.
- A clean clone reproduces the verified environment exactly for direct deps; transitives may still drift slightly between fresh installs months apart, which is acceptable at this maturity stage.
- Contributors who skim the README no longer copy-paste a stale package list.
- The CI `e2e` job installs only runtime deps (it does not need pytest or ruff). This was not possible before because the inline list bundled everything.
- Future Python upgrades are constrained: bumping to 3.13 would require revalidating every pinned version. This is the correct tradeoff for a system whose backend authority claim depends on stable behavior.
