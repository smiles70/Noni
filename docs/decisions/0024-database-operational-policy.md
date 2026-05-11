# ADR 0024 — Database Operational Policy

Date: 2026-05-11
Status: Accepted

## Context

The Netflix DBA critique surfaced concrete operational gaps in the proposed Postgres usage: connection pooling on a serverless DB, migration concurrency under multi-machine deploys, idempotency for webhooks, in-memory state that does not survive restarts, append-only telemetry without retention, and an absent restore drill.

This ADR sets the operational policy. Schema decisions live in `docs/architecture/SCHEMA.md` and ADR 0023.

## Decisions

### Hosting

- Primary: Supabase Postgres (us-east).
- Off-platform backup target: Cloudflare R2 (us-east).

### Connection pooling

- Application connects via Supabase's pooler in **transaction mode**.
- asyncpg / SQLAlchemy configured with `statement_cache_size=0` and `prepare_threshold=None` to be compatible with the transaction-mode pooler.
- Per-process pool: `pool_size=5`, `max_overflow=10`. Fly machine count and worker count set such that total connections stay under 60% of the pooler's per-branch ceiling.
- A `DATABASE_URL_DIRECT` (non-pooled) variant is used only by Alembic migrations and admin tooling.

### Migration policy

- App schema migrations: Alembic in `backend/alembic/versions/`.
- DB-level concerns (extensions, RLS policies, `pg_cron` jobs): Supabase migrations in `supabase/migrations/`.
- Production application of migrations is performed by Fly's `release_command = "alembic upgrade head"` so exactly one machine runs migrations per release.
- Down-migrations are written for every up-migration; reversibility is enforced by CI (`alembic upgrade head && alembic downgrade -1 && alembic upgrade head`).
- Destructive migrations (renames, type changes) are deployed in two phases: (1) additive, (2) cleanup, separated by a deploy boundary.

### Row Level Security

- RLS is enabled on every table that contains user data.
- Policies live in `supabase/migrations/*.sql` with named rules and per-table tests.
- The service role bypasses RLS and is used only by the FastAPI backend; the anon role is used only by the SPA for the sign-in flow.
- Tables read or written only by service-role: `processed_webhook_events`, `products`, `units`.

### Webhook idempotency

- `processed_webhook_events(event_id PK, event_type, processed_at, idempotency_outcome)`.
- Webhook handlers insert into this table inside the same transaction as the entitlement grant or revocation. A unique-violation indicates duplicate delivery and the transaction is rolled back as a no-op.

### Estimator persistence

- `InterfaceStateEstimator` state is persisted per `(account_id, scope)` in `estimator_state`.
- The estimator loads state on first use per request and writes back on each approved decision.
- No in-memory module-level estimator may be reintroduced (CI lint rule to be added in Sprint A5).

### Telemetry retention

- `telemetry_events.expires_at` is populated on insert per a single retention policy table maintained in `backend/services/telemetry_retention.py`.
- A `pg_cron` job sweeps expired rows nightly. Sweep volume and lag are observable.
- Default retention: 90 days for `iscs_decision` and `unit_view`; 365 days for `purchase_*`.

### Backups and disaster recovery

- Targets: RPO ≤ 5 minutes (Supabase PITR), RTO ≤ 1 hour.
- Nightly `pg_dump --format=custom` to R2 via GitHub Actions, retained 30 days.
- Quarterly restore drill: `make restore-drill` provisions an ephemeral Neon/Supabase branch, restores the latest dump, runs a schema-diff check. CI workflow `restore-drill.yml` enforces.

### Account deletion

- User-initiated deletion creates a `deletion_requests` row with a 7-day grace period.
- On completion: PII columns on `accounts` are zeroed; child rows in `purchases`, `entitlements`, and `processed_webhook_events` are retained anonymized (no PII present).
- Soft delete via `accounts.deleted_at` is the default state during the grace period.

### Rate limiting

- Primary: Cloudflare WAF (zone-level rate-limit rules in `infra/cloudflare/waf-rules.json`).
- Secondary: application-level `rate_limit_counters` for routes requiring per-account or per-resource limits the WAF cannot express.
- Cleanup: `pg_cron` sweeps expired counter rows.

## Consequences

- Single migration runner per release eliminates Alembic race conditions.
- Webhook handling is provably idempotent.
- Estimator state survives restarts.
- Data retention is bounded; storage costs are predictable.
- Restore is rehearsed quarterly, not improvised in an incident.

## Reversibility

- Pool sizes and modes are env vars.
- Retention policies are a single Python dict.
- The pooler mode can be flipped to session if a non-pooled workload emerges; the cost is connection count.

## References

- `docs/architecture/SCHEMA.md`
- ADR 0022, ADR 0023, ADR 0025
