# ADR 0025 — Secrets and Configuration Management

Date: 2026-05-11
Status: Accepted

## Context

The system spans five vendors (ADR 0022). The same secret often must exist in multiple vendor dashboards (Fly secrets, Cloudflare Pages env vars, Supabase, GitHub Actions, local dev). The operator constraint is binding: **no secret is typed into a vendor dashboard by hand more than once, and rotation is one command.**

## Decision

### Single source of truth

`infra/.env.prod.sops.yaml` — SOPS-encrypted, committed to the repo.

- Encryption backend: `age`. Keys live in `~/.config/sops/age/keys.txt` and are backed up to 1Password (manual, documented).
- The plaintext file `infra/.env.prod` is gitignored and is the working copy during edits only.
- `infra/.env.example` is the canonical key list (committed, no values).

### Propagation

A single Make target, `make secrets-sync`, decrypts the SOPS file and pushes each key to its target vendor(s) via their CLIs:

| Secret group | Targets |
|---|---|
| `DATABASE_URL`, `DATABASE_URL_DIRECT`, `SUPABASE_*`, `SESSION_SECRET`, `STRIPE_*`, `GOOGLE_OAUTH_*` | Fly secrets (`flyctl secrets set`) |
| `VITE_API_BASE_URL` | Cloudflare Pages env (`wrangler pages secret put`) |
| OAuth provider client_id/secret | Supabase Auth provider config (`supabase secrets set`) |
| GitHub Actions secrets used by CI | `gh secret set` |

`make secrets-sync` prints a table: `KEY | VENDOR | STATUS`. Any `MISSING` or `ERROR` row aborts the workflow.

### Rotation

`make secrets-rotate KEY=FOO` regenerates the named secret (or prompts for the new value if vendor-issued), updates the SOPS file, runs `secrets-sync`, and prints which artifacts (e.g., Fly machines, Cloudflare Pages deployments) require a restart.

### Drift detection

CI workflow `.github/workflows/secrets-drift.yml` runs daily. It compares the key set in `infra/.env.example` against the keys present in Fly, Cloudflare Pages, Supabase, and GitHub. Any drift opens a GitHub issue tagged `secrets-drift`.

### Local development

- `.env` (gitignored) drives local dev.
- `make env-from-sops` decrypts the prod SOPS file into a temporary `.env.prod` for the duration of a deploy and shreds it on exit.
- Developers without the age key cannot decrypt prod secrets; local mocks (`stripe-mock`, mock auth provider) cover all dev workflows.

### Boundary rules

- No vendor dashboard is the source of truth for any secret. Vendors are sinks; the SOPS file is the source.
- No secret value appears in logs, commit messages, or chat. CI lint enforces (`gitleaks` pre-commit + workflow).
- `SESSION_SECRET`, `STRIPE_WEBHOOK_SECRET`, and `STRIPE_SECRET_KEY` rotate quarterly at minimum; an additional ad-hoc rotation accompanies any suspected exposure.

## Upgrade path

If any of the following triggers fires, migrate to a hosted secrets broker (Doppler or Infisical), keeping the same operator interface:

- A third human joins the engineering team.
- `make secrets-sync` runs more than once per week on average for a month.
- Vendor count grows beyond seven.

The Make targets remain; their implementation switches from SOPS+CLI to the broker's CLI. The repo's `.env.example` stays the canonical key list.

## Consequences

- Rotating any secret is one command.
- A fresh laptop can fully provision the environment with `git clone && make bootstrap` plus a one-time age key import.
- Vendor dashboards are not authoritative; their drift is detected and reported daily.

## Non-goals

- Per-environment SOPS files for staging are out of scope at launch; staging uses the same age key with a parallel `.env.staging.sops.yaml`. Separation of duties between staging and prod is deferred until the team grows.

## References

- `docs/architecture/VENDORS.md`
- ADR 0022
