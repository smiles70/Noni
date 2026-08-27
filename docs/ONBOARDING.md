# Onboarding — Mynaani

## Prerequisites

- Python 3.11+ (the local venv uses the system `python3` at `/home/hazbyn/Mynaani/.venv`).
- Node 20+ and npm (the local toolchain is at `/home/hazbyn/Mynaani/.tools/node`).
- Docker and docker-compose for the Postgres service.
- Git.

## Quick start

1. Clone `https://github.com/smiles70/Mynaani`.
2. Activate the Python venv: `source .venv/bin/activate`
3. Ensure Node is on `PATH`: `export PATH=/home/hazbyn/Mynaani/.tools/node/bin:$PATH`
4. Install JS dependencies: `npm install`
5. Start infrastructure: `docker compose up -d`
6. Run migrations: `alembic upgrade head` (from `backend/`)
7. Run backend tests: `pytest backend/tests`
8. Run frontend unit tests: `npm run test:unit`
9. Start dev:
   - Backend: `uvicorn backend.app.main:app --reload` (or `cd backend` and run the configured command).
   - Frontend: `cd frontend && npm run dev`

## Environment

- Copy `.env.example` to `.env` and fill Stripe (`STRIPE_*`) and Postgres values. Auth is `mock` by default; for Magic.link see below.
- See `docs/integrations-setup.md` for Stripe setup.
- See `docs/staging-deploy.md` for staging and production deployment.

## Using Magic.link (production auth)

1. Create a Magic Auth app at `https://dashboard.magic.link` (not Magic Connect).
2. Copy the publishable key to `VITE_MAGIC_PUBLISHABLE_KEY`.
3. Copy the secret key to `MAGIC_API_SECRET_KEY`.
4. Set `AUTH_PROVIDER=magic` and `VITE_AUTH_PROVIDER=magic` in your `.env`.
5. Run the backend and frontend; sign in via the email form.
6. See ADR 0027, `.ai/process/MAGIC_LINK_INTEGRATION_PLAN.md`, and
   `.ai/process/MAGIC_IMPLEMENTATION_RESEARCH.md` for edge cases and best
   practices.
