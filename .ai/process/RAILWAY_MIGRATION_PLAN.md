# Railway Migration Plan — Noni

**Date:** 2026-08-27
**Process:** v9.51
**Goal:** move the Noni backend from Fly.io to Railway without affecting the Cloudflare Pages frontend.

## Phase 0 — Intake, ADR, and graph

- [x] Create `.ai/intake/2026-08-27-railway-migration.md`.
- [x] Create `.ai/process/RAILWAY_MIGRATION_PLAN.md`.
- [x] Update `.ai/process/PHASE_INVENTORY.md`.
- [x] Update knowledge graph with Railway migration capability, tests, and evidence.

## Phase 1 — GitHub Actions deploy workflow

- [] Update `.github/workflows/deploy.yml`:
  - Replace `fly-deploy-backend` with `railway-deploy-backend`.
  - Preflight checks for `RAILWAY_TOKEN`, `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`.
  - Keep `cloudflare-pages-deploy` and smoke test.
- [] Use `VITE_API_BASE_URL` from GitHub secret or `vars`.

## Phase 2 — Secrets sync and environment

- [] Update `infra/scripts/secrets-sync.sh` to push backend secrets to Railway.
- [] Update `infra/.env.example` with `RAILWAY_TOKEN` and `RAILWAY_SERVICE_NAME`.
- [] Update `infra/.env.prod.sops.yaml` with Railway placeholders.
- [] Update `docs/DEVELOPER_PRODUCTION_GUIDE.md` with Railway commands.

## Phase 3 — Smoke and docs

- [] Update `infra/scripts/smoke-prod.sh` to use `PROD_API_BASE_URL` from env.
- [] Update `docs/CURRENT_STATE.md` with the migration status.
- [] Update `docs/ROLLBACK.md` with the Fly-to-Railway rollback path.

## Phase 4 — Verification and release

- [] Run `npm run type-check` and `npm run build`.
- [] Run `pytest backend/tests/test_magic_verifier.py` etc.
- [] Commit each phase.
- [] Push to `main`.
- [] Set `RAILWAY_TOKEN` in GitHub Actions and `infra/.env.prod.sops.yaml`.
- [] Run `secrets-sync.sh` or `railway up` manually for the first deploy.

## Constraints

- No frontend code changes.
- No auth provider changes.
- No database schema changes.
- Cloudflare Pages remains the static host.
