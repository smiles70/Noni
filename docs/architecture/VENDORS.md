# Third-Party Vendor Topology

How the 5 vendors interconnect, who holds which secret, and what flows where.

Status: binding. Referenced by ADRs 0022 (vendor topology) and 0025 (secrets and configuration management).

## Consolidation principle

Every vendor must earn its slot. A vendor earns its slot only if (a) it is irreducible (Stripe, Google OAuth) or (b) it collapses two or more other vendors into one dashboard and one CLI. Every secret has one source of truth and one command to propagate.

## Vendor set at launch

| # | Vendor | Role | CLI |
|---|---|---|---|
| 1 | Google Cloud Console | OAuth client (touched once at setup) | `gcloud` |
| 2 | Supabase | Auth + Postgres + RLS + pg_cron | `supabase` |
| 3 | Fly.io | FastAPI backend host + secrets | `flyctl` |
| 4 | Cloudflare | Pages, DNS, WAF, R2, Registrar | `wrangler` |
| 5 | Stripe | Checkout, webhooks, receipts | `stripe` |
| 6 | BetterStack (optional at launch) | Logs, uptime, alerts | API |

GitHub is already in the stack for source control and CI; it is not counted as a new vendor.

## Diagram

```mermaid
flowchart LR
    subgraph Dev["Developer Workstation"]
        ENV["infra/.env.prod.sops.yaml<br/>(SOPS-encrypted, in repo)<br/>SINGLE SOURCE OF TRUTH"]
        MK["make secrets-sync"]
    end

    subgraph GH["GitHub"]
        REPO["Repo<br/>fly.toml · wrangler.toml<br/>supabase/ · alembic/<br/>.github/workflows/"]
        GHA["Actions<br/>CI + deploy<br/>nightly backup<br/>secrets drift check"]
        GHS["Encrypted Secrets"]
    end

    subgraph V1["1. Google Cloud Console"]
        GC["OAuth Client<br/>client_id + secret<br/>(set once, rarely rotated)"]
    end

    subgraph V2["2. Supabase"]
        SAUTH["Auth<br/>- Google provider config<br/>- JWKS endpoint"]
        SPG["Postgres + RLS<br/>+ pg_cron"]
        SCFG["config.toml + migrations<br/>(in repo)"]
    end

    subgraph V3["3. Fly.io"]
        FAPP["noni-api app<br/>fly.toml release_command<br/>= alembic upgrade head"]
        FSEC["Fly Secrets<br/>DATABASE_URL<br/>SUPABASE_JWT_SECRET<br/>STRIPE_SECRET_KEY<br/>STRIPE_WEBHOOK_SECRET<br/>SESSION_SECRET"]
    end

    subgraph V4["4. Cloudflare"]
        CFP["Pages project<br/>noni-web"]
        CFPE["Pages env vars<br/>VITE_API_BASE_URL"]
        CFW["WAF rules<br/>rate limits<br/>bot mgmt"]
        CFR2["R2 bucket<br/>noni-backups"]
        CFDNS["DNS + Registrar"]
    end

    subgraph V5["5. Stripe"]
        SPROD["Product: noni-modules-4-5<br/>one-time price"]
        SWH["Webhook endpoint<br/>signing secret"]
    end

    subgraph V6["6. BetterStack (optional)"]
        BS1["Log source token"]
        BS2["Uptime monitors"]
    end

    ENV --> MK
    MK -- "flyctl secrets set" --> FSEC
    MK -- "wrangler pages secret put" --> CFPE
    MK -- "supabase secrets set" --> SAUTH
    MK -- "gh secret set" --> GHS
    MK -- "stripe (read-only verify)" --> SWH

    REPO -- "push" --> GHA
    GHA -- "flyctl deploy" --> FAPP
    GHA -- "wrangler pages deploy" --> CFP
    GHA -- "supabase db push" --> SPG
    GHA -- "pg_dump nightly" --> CFR2

    GC -. "OAuth redirect" .-> SAUTH
    SAUTH -. "JWKS" .-> FAPP
    SWH -. "webhooks" .-> FAPP
    FAPP -. "SQL" .-> SPG
    CFW -. "proxies /api" .-> FAPP
    CFP -. "static" .-> CFDNS
    FAPP -- "logs" --> BS1
    CFW -- "edge logs" --> BS1

    classDef sot fill:#fbbf24,color:#000,stroke:#92400e,stroke-width:3px
    classDef vendor fill:#1f2937,color:#fff,stroke:#111
    class ENV sot
    class GC,SAUTH,SPG,FAPP,CFP,CFW,CFR2,CFDNS,SPROD,SWH,BS1,BS2 vendor
```

## Properties this topology guarantees

- **One source of truth (yellow box):** `infra/.env.prod.sops.yaml`. One file, one command (`make secrets-sync`) writes to all five vendors.
- **No secret is typed into a vendor dashboard by hand.** Every line that touches a vendor is a CLI call.
- **No vendor talks to another vendor without crossing the API.** Stripe -> Fly. Google -> Supabase -> Fly. There is no Stripe -> Supabase or Google -> Fly shortcut.
- **Every config artifact lives in the repo:** `fly.toml`, `wrangler.toml`, `supabase/migrations/`, `alembic/versions/`. Bootstrapping from a fresh laptop is `git clone && make bootstrap`.

## Operator surface (daily ops)

| Task | Command | Vendor dashboards touched |
|---|---|---|
| Bootstrap a fresh staging env | `make bootstrap-staging` | 0 |
| Rotate a secret | edit `.env.prod` -> `make secrets-sync` | 0 |
| Deploy backend | `git push` -> CI runs `flyctl deploy` | 0 |
| Deploy frontend | `git push` -> Cloudflare Pages auto-builds | 0 |
| New DB migration | `alembic revision -m ...` -> `git push` | 0 |
| Add a new RLS policy | edit `supabase/migrations/*.sql` -> `supabase db push` | 0 |
| Restore backup drill | `make restore-drill` | 0 |
| Investigate a 3am page | BetterStack URL in the alert email | 1 |

## Trade-offs accepted explicitly

1. **Supabase is the single biggest concentration of vendor risk** (auth + identity + data + RLS + cron). Mitigation: nightly off-platform `pg_dump` to R2 and a documented "migrate to another Postgres in 1 day" runbook.
2. **SOPS + Makefile is a 1-2 person solution.** Trigger to switch to Doppler/Infisical: a third human joins, or `secrets-sync` runs more than once a week.
