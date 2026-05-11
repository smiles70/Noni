# ADR 0022 — Vendor Topology and Consolidation Principle

Date: 2026-05-11
Status: Accepted
Supersedes: portions of `docs/deferred-decisions.md` related to hosting, auth, payments, and DNS

## Context

The launch path requires identity, payments, hosting, DNS, edge protection, observability, and backups. A naive selection produces ~20 vendor dashboards and equivalent secrets-management surface. Operators have stated a binding constraint: **minimize the number of vendor dashboards manually managed; prefer CLI/API automation; never type the same secret into more than one place by hand.**

The architect review (see `docs/architecture/SYSTEM.md`) added correctness constraints that must not be diluted by the consolidation effort.

## Decision

Adopt a closed set of five vendors at launch, plus one optional observability vendor. Every vendor must earn its slot under the **consolidation principle**:

> A vendor earns its slot only if (a) it is irreducible (Stripe, Google OAuth) or (b) it collapses two or more other vendors into one dashboard and one CLI.

### Vendor set

| # | Vendor | Role | CLI |
|---|---|---|---|
| 1 | Google Cloud Console | OAuth client (one-time setup) | `gcloud` |
| 2 | Supabase | Auth + Postgres + RLS + pg_cron | `supabase` |
| 3 | Fly.io | FastAPI backend host + secrets | `flyctl` |
| 4 | Cloudflare | Pages, DNS, WAF, R2, Registrar | `wrangler` |
| 5 | Stripe | Checkout, webhooks, receipts | `stripe` |
| 6 | BetterStack (optional) | Logs, uptime, alerts | API |

GitHub is already in the stack and is not counted as a new vendor.

### Explicit non-vendors at launch

- No separate transactional-email provider. Stripe sends payment receipts natively. Email vendor reconsidered only when product email is required beyond receipts.
- No separate DNS or registrar. Cloudflare provides both.
- No separate WAF or bot-management vendor. Cloudflare provides both.
- No separate object storage. Cloudflare R2 holds backups.
- No subscription, analytics, or marketing vendor at launch.

## Consequences

- One source of truth for every secret (see ADR 0025).
- Every vendor has a real CLI; manual dashboard work is restricted to account creation and CLI authentication.
- Supabase concentrates auth + data + scheduled jobs. This concentration is accepted; mitigations are nightly off-platform `pg_dump` to R2 and a documented "migrate to another Postgres in 1 day" runbook.
- BetterStack may be deferred at launch if Fly's built-in logs are sufficient for the first weeks; the slot is reserved.

## Reversibility

- Migrating off Supabase Postgres: `pg_dump` is portable. Application reads `DATABASE_URL`; no Supabase-specific SQL outside `supabase/migrations/`.
- Migrating off Supabase Auth: `accounts.auth_user_id` is a logical UUID, not a foreign key (see ADR 0023). Users can be re-bound to another identity provider without schema rewrite.
- Migrating off Fly: container image is portable; `release_command` migration pattern works on any container host.
- Migrating off Cloudflare: DNS and Pages config in `wrangler.toml` are portable; R2 contents are S3-compatible.

## References

- `docs/architecture/VENDORS.md` (topology diagram)
- ADR 0021 (pricing and tiering — Stripe Checkout one-time)
- ADR 0023 (auth and session model)
- ADR 0025 (secrets and configuration management)
