# Operations Runbook — Noni

## Incident response

See `docs/ops/incident-response-runbook.md` for severity classification, escalation, and communication steps.

## Recovery

See `docs/ops/recovery-runbook.md` for service recovery, database restore, and smoke tests.

## Deployment

- Staging and production: `docs/staging-deploy.md` and `.github/workflows/deploy.yml`.
- Pre-deploy checks: `npm run build`, `pytest backend/tests`, `alembic upgrade head`.

## Monitoring and alerting

- Prometheus metrics are exposed at `/metrics`.
- BetterStack setup: `docs/ops/betterstack-setup.md` and `docs/ops/betterstack-quick-start.md`.
- Public status page runbook: `docs/ops/status-page.md`.

## Database

- Migrations: `alembic upgrade head` / `alembic downgrade <rev>`.
- Backup/restore: `docs/ops/nightly-backup.yml` and `docs/ops/restore-drill.yml`.
- Health: `docker compose` healthchecks and backend `/health`.

## Secrets and drift

- `.github/workflows/secrets-drift.yml` runs scheduled secret scans.
- `.sops.yaml` for encrypted secrets.
- See `docs/decisions/0025-secrets-and-configuration.md`.

## Support contacts

Escalation path: see `.github/CODEOWNERS` and `SECURITY.md`.
