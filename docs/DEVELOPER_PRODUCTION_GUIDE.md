# Developer Production Guide — Mynaani

**Scope:** the five remaining conditions before Mynaani can be promoted to a real production environment.

---

## 0. Deploy the backend to Railway

### 0.1 Install the Railway CLI

```bash
npm install -g @railway/cli
railway login
```

### 0.2 Create the project and services

```bash
railway init --name noni
railway service create --name noni-api
railway service create --name noni-db --type database
railway add --service noni-db --type database --database postgresql
```

### 0.3 Set the production secrets

```bash
export RAILWAY_TOKEN=...           # from Railway dashboard
export RAILWAY_SERVICE_NAME=noni-api
railway variables set DATABASE_URL="postgresql://..." --service noni-api
railway variables set MAGIC_API_SECRET_KEY="sk_live_..." --service noni-api
# repeat for all backend secrets (see infra/.env.example)
```

### 0.4 Deploy

```bash
railway up --service noni-api
```

### 0.5 Add `RAILWAY_TOKEN` to GitHub Actions

```bash
gh secret set RAILWAY_TOKEN --body "<your-token>"
gh secret set RAILWAY_SERVICE_NAME --body "noni-api"
```

---

## 1. Provision Magic Auth and set the secrets

### 1.1 Create the Magic Auth app

1. Open <https://dashboard.magic.link> in a browser.
2. Create a new **Magic Auth** app (do **not** use Magic Connect).
3. Note the **Publishable API Key** (`pk_live_...`) and the **Secret API Key** (`sk_live_...`).

### 1.2 Set local `.env`

```bash
cp infra/.env.example .env
```

Edit `.env`:

```bash
AUTH_PROVIDER=magic
VITE_AUTH_PROVIDER=magic
MAGIC_API_SECRET_KEY=sk_live_...
VITE_MAGIC_PUBLISHABLE_KEY=pk_live_...
```

> Never commit `.env`. It is already in `.gitignore`.

### 1.3 Set railway.app backend secret (CLI)

```bash
railway secrets set MAGIC_API_SECRET_KEY=sk_live_... -a noni-api
```

Optional, for `MAGIC_CLIENT_ID` if Magic does not auto-detect it:

```bash
railway secrets set MAGIC_CLIENT_ID=<client_id_from_dashboard> -a noni-api
```

### 1.4 Set Cloudflare Pages build-time secret (CLI)

```bash
wrangler pages secret put VITE_MAGIC_PUBLISHABLE_KEY --project-name noni-web
```

When prompted, paste `pk_live_...`.

### 1.5 Set GitHub Actions secret (CLI)

```bash
gh secret set VITE_MAGIC_PUBLISHABLE_KEY --body "pk_live_..."
```

### 1.6 Start the local stack

```bash
docker compose up -d
source .venv/bin/activate
alembic upgrade head
uvicorn backend.app.main:app --reload
```

In a second terminal:

```bash
export PATH=/home/hazbyn/Mynaani/.tools/node/bin:$PATH
cd frontend
npm run dev
```

Open <http://localhost:5173> and sign in with an email address. Click the Magic link in the email, then confirm the app redirects back to Mynaani.

---

## 2. Verify an end-to-end Magic sign-in

### 2.1 Backend health and config

```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```

Check that the backend reports the Magic provider:

```bash
curl -s http://localhost:8000/api/v1/auth/config | python3 -m json.tool
```

Expected output includes `{"auth_provider": "magic"}`.

### 2.2 Get a DID token

After signing in through the browser, open the browser DevTools console and run:

```javascript
const token = await window.localStorage.getItem('noni.magic_token');
console.log(token);
```

Copy the printed token.

### 2.3 Test the protected init route

```bash
DID_TOKEN='did:ethr:...'
curl -X POST http://localhost:8000/api/v1/auth/session/init \
  -H "Authorization: Bearer ${DID_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool
```

A `200 OK` with `materialized: true` means the account was created and the token is valid.

### 2.4 Test a protected resource

```bash
curl http://localhost:8000/api/v1/me \
  -H "Authorization: Bearer ${DID_TOKEN}" | python3 -m json.tool
```

---

## 3. Run the full backend test suite with live PostgreSQL

### 3.1 Start a Postgres container

```bash
docker run --name noni-postgres-test \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=noni \
  -p 5432:5432 \
  -d postgres:15
```

### 3.2 Create `.env.test`

```bash
cat > .env.test <<'EOF'
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/noni
DATABASE_URL_DIRECT=postgresql+psycopg2://postgres:postgres@localhost:5432/noni
AUTH_PROVIDER=mock
MAGIC_API_SECRET_KEY=
VITE_MAGIC_PUBLISHABLE_KEY=
SESSION_SECRET=test-secret-not-for-production
EOF
```

### 3.3 Install backend test dependencies

```bash
source .venv/bin/activate
pip install -e ".[dev,test]"
```

### 3.4 Run migrations and tests

```bash
set -a; source .env.test; set +a
alembic upgrade head
pytest backend/tests --no-cov -q
```

### 3.5 Stop the test container

```bash
docker stop noni-postgres-test
docker rm noni-postgres-test
```

---

## 4. Configure SIEM with Sentry

### 4.1 Create a Sentry project

1. Open <https://sentry.io> and create a project for `noni-api`.
2. Copy the DSN (looks like `https://...@....ingest.sentry.io/...`).

### 4.2 Install Sentry SDKs

Backend:

```bash
source .venv/bin/activate
pip install "sentry-sdk[fastapi]>=2.0"
```

Frontend:

```bash
export PATH=/home/hazbyn/Mynaani/.tools/node/bin:$PATH
cd frontend
npm install @sentry/react @sentry/browser
```

### 4.3 Set the Sentry DSN

```bash
railway secrets set SENTRY_DSN=https://...@....ingest.sentry.io/... -a noni-api
gh secret set SENTRY_DSN --body "https://...@....ingest.sentry.io/..."
```

Add to `frontend/.env`:

```bash
VITE_SENTRY_DSN=https://...@....ingest.sentry.io/...
```

### 4.4 Wire Sentry into the backend

Append this to `backend/app/main.py` after the other imports:

```python
import sentry_sdk
from backend.core.config import settings

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.1,
    )
```

Then add `SENTRY_DSN` to `backend/core/config.py` as an optional `Pydantic` field.

### 4.5 Wire Sentry into the frontend

Add near the top of `frontend/src/main.tsx`:

```typescript
import * as Sentry from "@sentry/react";

if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    environment: import.meta.env.VITE_ENVIRONMENT || "development",
    tracesSampleRate: 0.1,
  });
}
```

### 4.6 Create a Sentry release (CLI)

```bash
sentry-cli releases new "noni@$(git rev-parse --short HEAD)"
sentry-cli releases set-commits "noni@$(git rev-parse --short HEAD)" --auto
sentry-cli releases finalize "noni@$(git rev-parse --short HEAD)"
```

---

## 5. Establish a Lighthouse and pa11y baseline

### 5.1 Install the tools

```bash
export PATH=/home/hazbyn/Mynaani/.tools/node/bin:$PATH
npm install -g lighthouse pa11y
```

Or use `npx` without a global install:

```bash
npm install --save-dev lighthouse pa11y
```

### 5.2 Run a local production build

```bash
export PATH=/home/hazbyn/Mynaani/.tools/node/bin:$PATH
npm run build
```

### 5.3 Serve the build

```bash
cd frontend
npx serve -s dist -p 4173 &
SERVE_PID=$!
```

### 5.4 Run Lighthouse

```bash
npx lighthouse http://localhost:4173 \
  --output=html \
  --output-path=./lighthouse-baseline.html \
  --preset=desktop \
  --chrome-flags="--headless"
```

Open `./lighthouse-baseline.html` in a browser.

### 5.5 Run pa11y

```bash
npx pa11y http://localhost:4173 --reporter cli > pa11y-baseline.txt
```

Review `pa11y-baseline.txt`. Any WCAG 2.1 AA issues should be opened as issues or fixed before release.

### 5.6 Stop the static server

```bash
kill $SERVE_PID
```

---

## Completion checklist

Use this before calling the release ready:

```bash
# 1. Magic e2e works
curl -s http://localhost:8000/api/v1/me -H "Authorization: Bearer $DID_TOKEN" | grep '"id"'

# 2. Full backend tests pass
pytest backend/tests --no-cov -q

# 3. No audit findings
npm audit --workspaces
source .venv/bin/activate && pip-audit || true

# 4. Build and bundle guards pass
npm run build

# 5. Sentry is receiving events
# Trigger a test error and confirm it appears in Sentry.
```

---

*Generated under Process v9.51. Adjust secret values, project names, and URLs to match your own Magic, railway.app, Cloudflare, and Sentry accounts.*
