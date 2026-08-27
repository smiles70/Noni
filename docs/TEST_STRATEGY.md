# Test Strategy — Mynaani

## Backend

- **Framework:** `pytest` in `backend/tests/`.
- **Types:** acceptance (A2-A10), curriculum, enterprise/business logic, integration, provider (Stripe), telemetry, UI state, geragogy signals.
- **Coverage:** `pytest-cov` configured in `pyproject.toml`.
- **CI:** `ruff`, `black --check`, `mypy`, Alembic round-trip, and `pytest` in `.github/workflows/ci.yml`.

## Frontend

- **Unit tests:** `vitest` (`frontend/package.json` script `test:unit`).
- **E2E tests:** `playwright` with `axe-playwright` for WCAG 2.1 AA (`test:e2e`).
- **Type checking:** `tsc --noEmit`.
- **Bundle size:** `npm run bundle-size` with budget in `frontend/package.json`.
- **CI:** type-check, build, and bundle-size budget in `.github/workflows/ci.yml`.

## Security and quality gates

- `bandit backend/`
- `truffleHog filesystem .`
- `npm audit --audit-level=moderate`
- `trivy` container scan

## Local execution

```bash
source .venv/bin/activate
pytest backend/tests

export PATH=".tools/node/bin:$PATH"
npm run test:unit
npm run test:e2e
npm run build
```

## Test data

- Mocks for auth and Stripe.
- Local PostgreSQL via `docker compose`.
