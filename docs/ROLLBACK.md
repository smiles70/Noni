# Rollback Guide — Noni

## Backend (Fly.io)

1. Identify the last known good git SHA or Fly image.
2. Deploy it: `flyctl deploy --remote-only --image <image>` or `git checkout <sha> && flyctl deploy --remote-only`.
3. If a bad Alembic migration was applied, run `alembic downgrade <target>` before the next deploy.
4. Verify `/health` and run backend smoke tests from `backend/tests`.

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
