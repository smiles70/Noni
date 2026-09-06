# Current State — Mynaani

**Last updated:** 2026-08-27

## What exists

- Full-stack geragogy-grounded AI learning platform for older adults.
- **Backend:** FastAPI, SQLAlchemy + Alembic, PostgreSQL, Pydantic, structured logging, Prometheus metrics.
- **Frontend:** React 18, Vite 6, TypeScript, Playwright + axe-playwright for WCAG 2.1 AA.
- **Integrations:** Mock auth (dev/tests); **Magic.link integrated** as production auth provider (ADR 0027). Mock remains the default for CI/local; Magic is opt-in via `AUTH_PROVIDER=magic` + `MAGIC_API_SECRET_KEY`. Stripe (payments). **Backend:** `https://noni-api-production.up.railway.app` (Railway). **Frontend:** `https://noni-web.pages.dev` (Cloudflare Pages).
- **CI/CD:** `.github/workflows/ci.yml` (lint, test, build, security scans), `deploy.yml`, `nightly-backup.yml`, `restore-drill.yml`, `secrets-drift.yml`.
- **Documentation:** README, ARCHITECTURE, 27 ADRs, ops runbooks, runbook, rollback guide, test strategy, security policy, and v9.51 process artifacts.
- **Local environment:** Python 3.14 venv at `.venv/`, Node 20.17.0 at `.tools/node/`, all Python and npm dependencies installed.
- **Quality gates:** `npm run type-check`, `npm run build`, `npm run test:unit` (135/135), `npm audit` 0. Backend `tests/test_iscs.py`, `tests/test_geragogy_signals.py`, and `tests/test_magic_verifier.py` pass.

## What is tracked / incomplete

- **Full backend test suite:** requires a live PostgreSQL/Redis instance (Docker unavailable in this sandbox).
- **SIEM integration:** not configured; logs are written to stdout only.
- **Performance baseline:** Lighthouse and pa11y baseline not yet established.
- **Dependency note:** `numpy==1.26.4` is not installable on Python 3.14; `numpy==2.5.2` is installed and functional.

## Blockers

- **Railway migration pending:** `RAILWAY_TOKEN` must be added to GitHub Actions and the Railway project/service created. railway.app is currently blocked by an overdue invoice, so the new `deploy.yml` will not deploy the backend until the Railway token is present.
- No code-level production blockers remain.
