# Sprint 14: Pin Backend Dependencies (CLOSED)

Tag: `sprint-14-pinned-deps-v1`. Replaces four drift-prone inline package lists with a single pair of pinned requirements files (per ADR 0012).

## Phases

- 14.1 `requirements.txt` (runtime, exact pins) + `requirements-dev.txt` (`-r requirements.txt` + tooling)
- 14.2 `backend/Dockerfile` installs via `pip install -r requirements.txt`
- 14.3 CI workflow: `backend` job uses `requirements-dev.txt`, `e2e` job uses `requirements.txt`
- 14.4 `README.md` and `CONTRIBUTING.md` setup commands collapsed to `pip install -r requirements-dev.txt`
- 14.5 ADR 0012
- 14.6 Verified: ruff clean, 58/58 tests, frontend builds, install from the new files succeeds

## Out of scope

- Lockfile-style transitive pinning (pip-tools / uv / poetry) - deferred until a concrete trigger
- Python version bump - 3.12 stays canonical
