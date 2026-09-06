# Rollback Guide — Mynaani

## Backend (Railway)

1. Identify the last known good git SHA.
2. Roll back via the Railway dashboard to the previous successful deployment, or check out the SHA and run `railway up --service noni-api`.
3. If a bad Alembic migration was applied, run `alembic downgrade <target>` before the next deploy.
4. Verify `/health` and run backend smoke tests from `backend/tests`.

## Backend (railway.app — legacy)

railway.app is the previous backend host. To roll back to Railway during the migration:

1. Identify the last known good git SHA or Railway image.
2. Deploy it: `railway deploy --remote-only --image <image>` or `git checkout <sha> && railway deploy --remote-only`.
3. Verify `/health`.

## Frontend (Cloudflare Pages)

1. Revert the git SHA and re-run the deploy workflow, or roll back to the previous Pages build in the Cloudflare dashboard.
2. Verify the production URL.

## Database

- Use `alembic downgrade` for schema rollbacks.
- For data corruption, restore from the nightly backup. See `docs/ops/restore-drill.yml` and `docs/ops/nightly-backup.yml`.

## Third-party services

- **Stripe:** inspect `processed_webhook_events` for duplicate event IDs before refunding or voiding.
- **Auth provider:** sessions expire by TTL once a provider is selected; mock tokens are not rolled back.

## Epic-specific rollback example

`docs/ops/epic002-rollback-plan.md` contains the original Epic 002 rollback plan and can be used as a template.
