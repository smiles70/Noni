> **Deprecated:** legacy platform retired; production runs on Railway.

# PROCESS_CURRENT_STATE — Mynaani

**Process version:** v9.51
**Last refreshed:** 2026-08-26
**Repository:** smiles70/Mynaani

## Current-state snapshot

- `README.md`, `ARCHITECTURE.md`, `CONTRIBUTING.md` present at repo root.
- `docs/` contains architecture, decisions, ops, audits, integrations, design, and sprints.
- Backend stack: FastAPI + Alembic + PostgreSQL (requires Python 3.11+).
- Frontend stack: React 18 + Vite + TypeScript (strict).
- CI/CD: GitHub Actions (`.github/workflows/ci.yml`, `deploy.yml`, `nightly-backup.yml`, `restore-drill.yml`, `secrets-drift.yml`).
- Auth: Clerk (RS256 JWKS).
- Payments: Stripe.
- Deployment: the legacy platform backend, Cloudflare Pages frontend.
- `PROCESS_V9.51_SPEC.md` is loaded at repo root from the latest v9.51 process in `Downloads/`.

## Gaps (explicitly tracked)

- No `SECURITY.md` at repo root (threat model exists in `docs/audits/`).
- No `CODEOWNERS` file.
- No canonical top-level `docs/CURRENT_STATE.md`.
- No canonical top-level `docs/ONBOARDING.md`, `docs/RUNBOOK.md`, `docs/ROLLBACK.md`.

## Open items from latest PRA

- Frontend dependency vulnerabilities need breaking-change upgrades (`vite`, `react-router-dom`).
- Backend local test environment not verified in this session (Python 3.14.4 available, dependencies not installed).
- Performance baseline not established (Lighthouse / pa11y).
- SIEM integration not configured.
