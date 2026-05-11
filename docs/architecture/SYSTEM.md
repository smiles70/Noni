# System Diagram

Authoritative request flow, authority boundaries, and where each contract is enforced.

Status: binding. Referenced by ADRs 0019, 0022, 0023, 0024, 0025.

## Diagram

```mermaid
flowchart TB
    subgraph Learner["Learner / Caregiver Browser"]
        SPA["Vite SPA<br/>React + TS<br/>RenderGuard (fail-closed)<br/>Design tokens only"]
    end

    subgraph CF["Cloudflare Edge"]
        CDN["Pages CDN<br/>Static SPA assets"]
        WAF["WAF + Rate Limits<br/>Bot management<br/>TLS termination"]
        R2["R2 Bucket<br/>Nightly pg_dump"]
    end

    subgraph Fly["Fly.io (us-east)"]
        API["FastAPI Backend<br/>Authority for: envelope,<br/>curriculum, ISCS, entitlement,<br/>session, webhooks"]
        EST["InterfaceStateEstimator<br/>per-user, persisted"]
    end

    subgraph Supa["Supabase (us-east)"]
        AUTH["Auth<br/>Google OAuth provider<br/>JWKS"]
        PG["Postgres<br/>RLS enabled<br/>pg_cron retention"]
        POOL["Pooler<br/>transaction mode"]
    end

    subgraph Vendors["External Authorities"]
        GOOG["Google OAuth<br/>(identity issuer)"]
        STRIPE["Stripe<br/>Checkout + Webhooks<br/>+ built-in receipts"]
    end

    subgraph Ops["Observability (optional at launch)"]
        BS["BetterStack<br/>Logs + Uptime + Alerts"]
    end

    SPA -- "HTTPS" --> WAF
    WAF --> CDN
    WAF -- "/api/*" --> API
    CDN -- "SPA shell" --> SPA

    SPA -. "sign-in redirect" .-> AUTH
    AUTH -. "OAuth" .-> GOOG
    AUTH -- "callback w/ JWT" --> API
    API -- "verifies JWT vs JWKS<br/>issues HTTP-only session cookie" --> SPA

    SPA -- "Checkout link" --> STRIPE
    STRIPE -- "signed webhook" --> API
    API -- "SQL via pooler" --> POOL --> PG
    API <--> EST
    EST -- "persist state" --> PG

    PG -- "nightly pg_dump" --> R2
    API -- "stdout JSON" --> BS
    WAF -- "edge logs" --> BS

    classDef authority fill:#1f2937,color:#fff,stroke:#111
    classDef edge fill:#0ea5e9,color:#fff,stroke:#0369a1
    classDef data fill:#10b981,color:#fff,stroke:#065f46
    classDef ext fill:#a855f7,color:#fff,stroke:#6b21a8
    class API,EST authority
    class CDN,WAF,R2 edge
    class AUTH,PG,POOL data
    class GOOG,STRIPE,BS ext
```

## Authority rules visible in the diagram

- The SPA never decides anything; it asks the API for an envelope and renders inside `RenderGuard`.
- The API is the only writer to Postgres and the only verifier of JWTs and webhooks.
- Stripe and Google are the only external authorities; everything else is infrastructure.
- The estimator is per-user and persisted; restart-safe.

## Invariants this diagram enforces

1. **No client-supplied trust.** The SPA holds no decision logic; everything renderable comes from an authoritative envelope.
2. **One authority for state.** All Postgres writes route through FastAPI; no direct browser-to-DB path.
3. **One verifier of external claims.** JWT and Stripe webhook signature verification happen in exactly one place.
4. **Restart-safe stability.** The ISCS estimator persists per user; a Fly restart does not silently regress learner state.
5. **Edge does not bypass.** Cloudflare proxies `/api/*` to Fly; the origin is never addressed directly by the browser.
