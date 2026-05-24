#!/usr/bin/env bash
# infra/scripts/deploy-prod.sh
#
# Full production deploy: Supabase migrations, Fly backend (with Alembic via
# release_command), Cloudflare Pages frontend, smoke test.

set -euo pipefail

INFRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT_DIR="$(cd "$INFRA_DIR/.." && pwd)"

require() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: required CLI missing: $1"; exit 1; }; }
require flyctl
require wrangler

FLY_APP="${FLY_APP_NAME:-noni-api}"
CF_PAGES_PROJECT="${CLOUDFLARE_PAGES_PROJECT:-noni-web}"

# Step 1 only runs when a Supabase project is configured (SUPABASE_PROJECT_REF).
# When the database is Fly Postgres (or any non-Supabase Postgres) the
# RLS / pg_cron migrations under supabase/migrations don't apply; the
# canonical schema is owned by Alembic and runs inside the FastAPI
# lifespan on every backend boot. Skip this step in that case.
if [[ -n "${SUPABASE_PROJECT_REF:-}" ]]; then
  require supabase
  echo "==> 1/4 supabase db push (RLS, pg_cron, extensions)"
  cd "$ROOT_DIR"
  supabase db push --include-all || { echo "ERROR: supabase db push failed"; exit 1; }
else
  echo "==> 1/4 supabase db push  SKIPPED (SUPABASE_PROJECT_REF unset; using Alembic via lifespan)"
fi

echo "==> 2/4 flyctl deploy (Alembic runs in release_command)"
flyctl deploy --remote-only --app "$FLY_APP" || { echo "ERROR: fly deploy failed"; exit 1; }

echo "==> 3/4 wrangler pages deploy frontend"
cd "$ROOT_DIR/frontend"
npm run build
wrangler pages deploy dist --project-name "$CF_PAGES_PROJECT" --branch main || { echo "ERROR: cloudflare pages deploy failed"; exit 1; }

echo "==> 4/4 smoke test"
cd "$ROOT_DIR"
bash "$INFRA_DIR/scripts/smoke-prod.sh"

echo ""
echo "OK. Production deploy complete."
