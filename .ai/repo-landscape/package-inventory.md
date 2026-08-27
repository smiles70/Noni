# Noni Package Inventory

**Process:** v9.51 — Package and Version Alignment Agent view
**Date:** 2026-08-27
**Repository:** smiles70/Noni

This inventory captures the packages, services, and toolchains required to develop and run Noni, aligned with the v9.51 repo-landscape and package-alignment gates.

## Toolchain prerequisites

| Package/Tool | Version | Purpose | Source |
|---|---|---|---|
| Python | >=3.11 | Backend runtime and tooling | pyproject.toml |
| Node.js | 18+ (inferred from CI) | Frontend build / test tooling | .github/workflows/ci.yml |
| npm | bundled with Node | Frontend package manager | package-lock.json |

## Backend runtime packages

| Package | Version | Source |
|---|---|---|
| fastapi | 0.136.1 | requirements.txt |
| uvicorn[standard] | 0.46.0 | requirements.txt |
| gunicorn | 23.0.0 | requirements.txt |
| prometheus-client | 0.20.0 | requirements.txt |
| python-json-logger | 2.0.7 | requirements.txt |
| pydantic | 2.13.4 | requirements.txt |
| pydantic-settings | 2.14.0 | requirements.txt |
| SQLAlchemy | 2.0.49 | requirements.txt |
| alembic | 1.18.4 | requirements.txt |
| psycopg2-binary | 2.9.12 | requirements.txt |
| python-dotenv | 1.2.2 | requirements.txt |
| PyJWT[crypto] | 2.10.1 | requirements.txt |
| cryptography | 43.0.3 | requirements.txt |
| stripe | 11.4.1 | requirements.txt |
| httpx | 0.28.1 | requirements.txt |
| pybreaker | 1.4.1 | requirements.txt |
| celery[redis] | 5.3.0 | requirements.txt |
| magic-admin | 2.5.0 | pyproject.toml [project.dependencies] |
| numpy | 1.26.4 | requirements.txt |

## Backend development & lint tooling

| Package | Version | Source |
|---|---|---|
| pytest | 9.0.3 | requirements.txt |
| pytest-cov | 6.1.1 | requirements.txt |
| ruff | 0.15.12 | requirements.txt |
| black | 26.3.1 | requirements.txt |
| mypy | 1.20.2 | requirements.txt |
| pre-commit | 4.6.0 | requirements.txt |

## pyproject.toml runtime constraints

| Package | Constraint | Source |
|---|---|---|
| fastapi | fastapi>=0.100.0 | pyproject.toml [project].dependencies |
| uvicorn | uvicorn[standard]>=0.23.0 | pyproject.toml [project].dependencies |
| pydantic | pydantic>=2.0.0 | pyproject.toml [project].dependencies |
| pydantic-settings | pydantic-settings>=2.0.0 | pyproject.toml [project].dependencies |
| sqlalchemy | sqlalchemy>=2.0.0 | pyproject.toml [project].dependencies |
| psycopg2-binary | psycopg2-binary>=2.9.0 | pyproject.toml [project].dependencies |
| python-dotenv | python-dotenv>=1.0.0 | pyproject.toml [project].dependencies |
| redis | redis>=5.0.0 | pyproject.toml [project].dependencies |

## pyproject.toml dev constraints

| Package | Constraint | Source |
|---|---|---|
| pytest | pytest>=7.0.0 | pyproject.toml [project.optional-dependencies].dev |
| black | black>=23.0.0 | pyproject.toml [project.optional-dependencies].dev |
| isort | isort>=5.12.0 | pyproject.toml [project.optional-dependencies].dev |
| mypy | mypy>=1.5.0 | pyproject.toml [project.optional-dependencies].dev |
| ruff | ruff>=0.1.0 | pyproject.toml [project.optional-dependencies].dev |

## Frontend runtime packages

| Package | Version | Source |
|---|---|---|
| magic-sdk | ~33.9.0 | frontend/package.json dependencies |
| react | ^18.3.1 | frontend/package.json dependencies |
| react-dom | ^18.3.1 | frontend/package.json dependencies |
| react-router-dom | ^7.18.2 | frontend/package.json dependencies |

## Frontend development & test packages

| Package | Version | Source |
|---|---|---|
| @playwright/test | ^1.59.1 | frontend/package.json devDependencies |
| @types/react | ^18.3.12 | frontend/package.json devDependencies |
| @types/react-dom | ^18.3.1 | frontend/package.json devDependencies |
| @vitejs/plugin-react | ^4.3.3 | frontend/package.json devDependencies |
| axe-playwright | ^2.2.2 | frontend/package.json devDependencies |
| typescript | ^5.6.3 | frontend/package.json devDependencies |
| vite | ^5.4.10 | frontend/package.json devDependencies |
| vitest | ^2.1.4 | frontend/package.json devDependencies |
| jsdom | ^29.1.1 | root package.json devDependencies |

## Infrastructure services

| Service | Version | Purpose | Source |
|---|---|---|---|
| PostgreSQL | 15 | Primary database | docker-compose.yml |
| Docker / docker-compose | current | Container runtime and orchestration | docker-compose.yml |

## Notes

- Runtime dependencies are pinned in `requirements.txt` and mirrored in `pyproject.toml [project].dependencies`.
- Frontend dependencies are declared in `frontend/package.json`; `package-lock.json` is present for reproducible installs.
- Known frontend CVEs are tracked in `.ai/intake/2026-07-30-production-readiness.md`; they require breaking changes to `vite` and `react-router-dom`.
- Backend container image is built from `Dockerfile` using the pinned `requirements.txt`.
