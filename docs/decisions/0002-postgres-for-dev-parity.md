# 0002 — PostgreSQL via Docker Compose for development parity

## Status

Accepted (Sprint 1, durably documented in Sprint 4).

## Context

Noni stores telemetry as a durable audit trail (ARCHITECTURE rule on telemetry). Telemetry is queried for analysis and downstream export. Production will use a managed PostgreSQL.

Two options for development:
- SQLite (zero-setup, single file)
- PostgreSQL via Docker (real engine, parity with production)

## Decision

Use PostgreSQL 15 via `docker-compose.yml` for all local development and CI. SQLite is not used.

## Consequences

- Developers must run Docker locally; documented in README.
- CI uses a `postgres:15` service container.
- Schema features unique to Postgres (JSONB, advisory locks, etc.) are usable without a parity surprise in production.
- Test runs require Docker; offline development requires `docker compose up -d db` first.
- This is the right default for an audit-grade telemetry product.
