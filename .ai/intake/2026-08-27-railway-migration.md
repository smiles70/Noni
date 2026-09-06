> **Deprecated:** legacy platform retired; production runs on Railway.

# Intake — Railway backend migration

**Date:** 2026-08-27
**Process:** v9.51
**Source:** decision to migrate Mynaani backend off the legacy platform to Railway.

## Trigger

the legacy platform account has an overdue-invoice block, preventing `the legacy CLI deploy` from completing. The production frontend build (Cloudflare Pages) is also currently coupled to the `noni-api-production.up.railway.app` backend URL. A migration to Railway, which the project owner already uses for other apps, removes the billing blocker and keeps Cloudflare Pages for the frontend.

## Scope

1. Replace the legacy platform backend deploy with Railway.
2. Keep Cloudflare Pages for the frontend.
3. Migrate secrets from `the legacy CLI secrets set` to `railway variables set`.
4. Update CI/CD, secret sync, smoke tests, and documentation.
5. Leave the Postgres decision open: use Railway Postgres or an external Postgres service (Neon/Supabase). The plan is DB-agnostic in the first phase.

## Decision

Use Railway as the new backend host. Railway natively supports Docker, has a CLI (`railway`), and the Mynaani repo already has a portable `Dockerfile`.

## Risks and assumptions

- `RAILWAY_TOKEN` must be added to GitHub Actions and `infra/.env.prod.sops.yaml`.
- `DATABASE_URL` will change and must be updated in `infra/.env.prod.sops.yaml`.
- The backend URL will change from `https://noni-api-production.up.railway.app` to a Railway-provided URL (or custom domain).
- `railway.json` may be used for explicit build/deploy config, but the existing `Dockerfile` is sufficient for `railway up`.
- Magic.link and mock auth are unchanged.

## Related

- ADR 0027 (Magic.link auth) remains in effect.
- `docs/DEVELOPER_PRODUCTION_GUIDE.md` will be updated with Railway commands.
- `.ai/process/RAILWAY_MIGRATION_PLAN.md` holds the phase inventory.
