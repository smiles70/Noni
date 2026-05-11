# infra/scripts

Vendor-touching automation invoked by `infra/Makefile`. Each script is intended to be idempotent and to fail closed on missing CLIs or secrets.

| Script | Make target | Purpose |
|---|---|---|
| `secrets-bootstrap.sh` | `make secrets-bootstrap` | Generate age key, encrypt `.env.prod.draft` into `.env.prod.sops.yaml`. |
| `secrets-sync.sh` | `make secrets-sync` | Push every secret to Fly, Cloudflare Pages, and GitHub Actions. |
| `secrets-rotate.sh` | `make secrets-rotate KEY=...` | Rotate one secret end-to-end. |
| `secrets-audit.sh` | `make secrets-audit` | Detect drift between `.env.example` and vendor state. |
| `deploy-prod.sh` | `make deploy-prod` | Supabase migrations + Fly deploy + Cloudflare Pages deploy + smoke. |
| `smoke-prod.sh` | `make smoke-prod [--live]` | Hit deployed endpoints and verify expected JSON. |
| `stripe-bootstrap.sh` | `make stripe-bootstrap` | Create product, price, and webhook in Stripe (test mode by default). |
| `stripe-promote.sh` | `make stripe-promote` | Documented sequence to switch from Stripe test to live mode. |
| `restore-drill.sh` | `make restore-drill` | Quarterly: restore latest R2 backup into an ephemeral Postgres and diff. |
| `backup-now.sh` | `make backup-now` | One-off `pg_dump` to R2. |
| `observability-bootstrap.sh` | `make observability-bootstrap` | Create BetterStack monitors via API. |

## Conventions

- All scripts use `set -euo pipefail`.
- Secrets are decrypted into a `mktemp` file with `chmod 600`, sourced, and shredded on exit.
- No script echoes a secret value.
- All scripts require the relevant vendor CLI (`flyctl`, `wrangler`, `supabase`, `stripe`, `sops`, etc.) to be authenticated.

## Making scripts executable (one-time)

```bash
chmod +x infra/scripts/*.sh
```

This is also done automatically by `make bootstrap`.
