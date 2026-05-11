# Noni Infrastructure

This directory holds everything required to operate Noni across the five-vendor topology defined in ADR 0022:

```
infra/
  Makefile                    Operator surface (see `make help`)
  .env.example                Canonical environment variable manifest
  .env.prod.sops.yaml         SOPS-encrypted production secrets (created by bootstrap)
  scripts/                    Implementation of vendor-dependent Make targets
  cloudflare/                 WAF rules and Pages config (as code)
  fly/                        Fly app configuration (fly.toml lives at repo root)
```

## Quick start (local dev only — no vendor accounts needed)

```bash
make bootstrap        # one-time: deps, hooks, sanity checks
make up               # docker compose up: Postgres + backend + frontend
make migrate          # apply Alembic migrations
make test             # full test suite
```

## Going to production (Phase B)

1. Create vendor accounts (see `docs/architecture/VENDORS.md`).
2. `make cli-auth` — log in to each vendor CLI interactively (one sitting).
3. `make secrets-bootstrap` — generate age key, encrypt initial production env.
4. `make secrets-sync` — push every secret to every vendor.
5. `make deploy-prod` — apply DB migrations, deploy backend, deploy frontend, smoke test.
6. `make stripe-bootstrap` — create product, price, webhook in Stripe test mode.
7. `make smoke-prod` — end-to-end smoke against the deployed system.

## Reading the Makefile

Targets are grouped by purpose:

- **Local dev:** `bootstrap`, `up`, `down`, `demo`, `demo-test`
- **Quality:** `test`, `lint`, `fmt`
- **Database:** `migrate`, `migrate-new`, `migrate-down`, `db-shell`, `db-reset`
- **Vendor CLIs:** `check-clis`, `cli-auth`
- **Secrets:** `secrets-bootstrap`, `secrets-edit`, `secrets-sync`, `secrets-rotate`, `secrets-audit`
- **Deploy:** `deploy-prod`, `smoke-prod`, `smoke-prod-live`, `stripe-bootstrap`, `stripe-promote`
- **DR / observability:** `restore-drill`, `backup-now`, `observability-bootstrap`

Run `make help` for the live, authoritative list.

## Invariants

1. Every vendor-touching target is implemented as a script in `infra/scripts/`. The Makefile orchestrates; scripts implement.
2. No script writes a secret to stdout or to a log.
3. No vendor dashboard is the source of truth for any secret. The SOPS file is.
4. Every target either works locally with zero vendor secrets, or prints a clear `MISSING: <secret>` message and exits non-zero.

## See also

- `docs/decisions/0022-vendor-topology.md`
- `docs/decisions/0023-auth-and-session-model.md`
- `docs/decisions/0024-database-operational-policy.md`
- `docs/decisions/0025-secrets-and-configuration.md`
- `docs/architecture/VENDORS.md`
