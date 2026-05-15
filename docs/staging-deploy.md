# Noni Staging Deploy

Sprint **B3** ships a containerized backend, an nginx-served frontend, and a
managed Postgres dependency. This guide covers a generic Docker host (VPS,
Fly.io, Render, Railway, ECS, Cloud Run). Pick whichever target you prefer;
the build artifacts are identical.

## 1. Prerequisites

- A managed Postgres 15+ instance with a connection URL (Supabase, Neon, RDS).
- A Supabase project (Google OAuth enabled). See `docs/supabase-setup.md`.
- Stripe test-mode account with a webhook endpoint reserved. See
  `docs/stripe-setup.md`.
- Docker Engine 24+ on your host (or a PaaS that builds Dockerfiles).
- A public hostname per service:
  - `api.staging.noni.example`     -> backend container (port 8000)
  - `app.staging.noni.example`     -> frontend container (port 80)

## 2. Build images locally (smoke test)

```bash
docker compose build
docker compose up -d db
docker compose up -d api
curl -fsS http://localhost:8000/health
docker compose up -d frontend
curl -fsS http://localhost:8080/ | head -5
```

`api` runs Alembic migrations during startup (see `lifespan` in
`backend/app/main.py`); the first boot may take ~5s longer than subsequent
boots.

## 3. Required environment variables (staging)

Copy `.env.example` to `.env` on the host and replace placeholders. The
non-negotiables for staging:

| Variable                     | Notes                                                  |
| ---------------------------- | ------------------------------------------------------ |
| `ENVIRONMENT`                | `staging`                                              |
| `DEBUG`                      | `false`                                                |
| `DATABASE_URL`               | Managed Postgres pooled URL                            |
| `DATABASE_URL_DIRECT`        | Non-pooled URL (Alembic). Optional but recommended.    |
| `SECRET_KEY`                 | 32+ random bytes (`openssl rand -hex 32`)              |
| `SESSION_SECRET`             | 32+ random bytes, distinct from `SECRET_KEY`           |
| `CORS_ORIGINS`               | `https://app.staging.noni.example`                     |
| `AUTH_PROVIDER`              | `supabase`                                             |
| `SUPABASE_URL`               | From Supabase project settings                         |
| `SUPABASE_JWT_SECRET`        | From Supabase project settings -> API                  |
| `SUPABASE_JWT_ISSUER`        | `<SUPABASE_URL>/auth/v1`                               |
| `PAYMENT_PROVIDER`           | `stripe`                                               |
| `STRIPE_SECRET_KEY`          | Test-mode secret key (`sk_test_...`)                   |
| `STRIPE_WEBHOOK_SECRET`      | Endpoint signing secret from Stripe Dashboard          |
| `STRIPE_PRICE_ID_MODULES_4_5`| Price ID created via `scripts/seed_products.py`        |
| `STRIPE_SUCCESS_URL`         | `https://app.staging.noni.example/purchase/success`    |
| `STRIPE_CANCEL_URL`          | `https://app.staging.noni.example/purchase/cancel`     |

Frontend build accepts:

| Variable                  | Notes                                          |
| ------------------------- | ---------------------------------------------- |
| `VITE_AUTH_PROVIDER`      | `supabase`                                     |
| `VITE_SUPABASE_URL`       | Same as backend `SUPABASE_URL`                 |
| `VITE_SUPABASE_ANON_KEY`  | From Supabase project settings -> API          |
| `VITE_API_BASE_URL`       | `https://api.staging.noni.example`             |

These must be set **at build time** (Vite inlines them); rebuild the frontend
image whenever they change.

## 4. Deploy targets

### 4a. Generic Docker host (compose)

```bash
git clone <repo> && cd noni
cp .env.example .env && $EDITOR .env
docker compose pull
docker compose build
docker compose up -d
```

Put a TLS-terminating reverse proxy (Caddy, nginx, Traefik) in front and route
`api.staging.*` -> container `api:8000`, `app.staging.*` -> container
`frontend:80`.

### 4b. Fly.io

```bash
fly launch --no-deploy --copy-config --name noni-api-staging
fly secrets set $(grep -v '^#' .env | xargs)
fly deploy
```

The `Dockerfile` at the repo root builds `backend.app.main:app`; Fly's
auto-detected `internal_port` should be `8000`. Frontend deploys as a separate
Fly app from `frontend/Dockerfile`.

### 4c. Render / Railway / Cloud Run

- **Web service** -> repo root `Dockerfile`, port `8000`, health `/health`.
- **Static / web service** -> `frontend/Dockerfile`, port `80`.
- Provision Postgres add-on; copy `DATABASE_URL` into the api service env.

## 5. Post-deploy checks

```bash
# Backend up + migrations applied.
curl -fsS https://api.staging.noni.example/health
# Expect: {"status":"healthy","version":"0.1.0","environment":"staging"}

# Frontend serves the SPA.
curl -fsSI https://app.staging.noni.example/ | head -1   # HTTP/2 200

# OAuth callback reachable (Supabase dashboard -> Auth -> URL Configuration).
# Add: https://app.staging.noni.example/auth/callback

# Stripe webhook handshake (from a workstation):
stripe listen --forward-to https://api.staging.noni.example/api/billing/webhook
stripe trigger checkout.session.completed
# Backend logs should show "webhook accepted" with idempotent grant.
```

Run the smoke suite locally against staging:

```bash
NONI_BASE_URL=https://api.staging.noni.example pytest backend/tests/test_a10_smoke.py -q
```

## 6. Rollback

```bash
docker compose pull         # if you tagged previous images
docker compose up -d --force-recreate api
```

For PaaS targets, redeploy the previous image SHA. Migrations are forward-only
(ADR 0005); a true rollback requires a compensating Alembic revision.

## 7. Known gaps (tracked in PROGRESS.md)

- No automated blue/green; expect ~5s cold-start gap during `docker compose up`.
- Frontend `VITE_*` rebuild required on env change (Vite inlines at build).
- Stripe live keys are deferred to launch (B4 currently test-mode only).
