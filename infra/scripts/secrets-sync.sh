#!/usr/bin/env bash
# infra/scripts/secrets-sync.sh
#
# Decrypt the SOPS-encrypted prod env, then push each key to its target
# vendor(s) via the vendor CLI. Prints a table KEY | VENDOR | STATUS.
#
# Never writes any secret value to stdout, stderr, or logs.

set -euo pipefail

INFRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT_DIR="$(cd "$INFRA_DIR/.." && pwd)"
SOPS_FILE="$INFRA_DIR/.env.prod.sops.yaml"

require() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: required CLI missing: $1"; exit 1; }; }
require sops
require flyctl
require wrangler
require gh

if [[ ! -f "$SOPS_FILE" ]]; then
  echo "ERROR: $SOPS_FILE not found. Run: make secrets-bootstrap"
  exit 1
fi

# Decrypt to a tmpfile with restricted perms, scrub on exit.
TMP="$(mktemp)"
trap 'shred -u "$TMP" 2>/dev/null || rm -f "$TMP"' EXIT
chmod 600 "$TMP"
sops --decrypt --input-type yaml --output-type dotenv "$SOPS_FILE" > "$TMP"

# shellcheck disable=SC1090
set -a; source "$TMP"; set +a

FLY_APP="${FLY_APP_NAME:-noni-api}"
CF_PAGES_PROJECT="${CLOUDFLARE_PAGES_PROJECT:-noni-web}"

declare -a FLY_KEYS=(
  DATABASE_URL DATABASE_URL_DIRECT
  SESSION_SECRET SESSION_COOKIE_NAME SESSION_TTL_DAYS
  SUPABASE_URL SUPABASE_ANON_KEY SUPABASE_SERVICE_ROLE_KEY
  SUPABASE_JWT_SECRET SUPABASE_JWT_AUDIENCE SUPABASE_JWT_ISSUER
  GOOGLE_OAUTH_CLIENT_ID GOOGLE_OAUTH_CLIENT_SECRET
  STRIPE_SECRET_KEY STRIPE_WEBHOOK_SECRET STRIPE_PRICE_ID_MODULES_4_5
  STRIPE_SUCCESS_URL STRIPE_CANCEL_URL
  ENVIRONMENT LOG_LEVEL
)

declare -a CF_PAGES_KEYS=(
  VITE_API_BASE_URL STRIPE_PUBLISHABLE_KEY
)

declare -a GH_KEYS=(
  FLY_API_TOKEN CLOUDFLARE_API_TOKEN CLOUDFLARE_ACCOUNT_ID
  SUPABASE_ACCESS_TOKEN SUPABASE_PROJECT_REF
  STRIPE_SECRET_KEY
)

push_fly() {
  local key="$1"
  local val="${!key:-}"
  if [[ -z "$val" ]]; then
    printf '  %-40s | fly                   | MISSING\n' "$key"
    return 1
  fi
  flyctl secrets set "$key=$val" --app "$FLY_APP" --stage >/dev/null
  printf '  %-40s | fly                   | OK\n' "$key"
}

push_cf_pages() {
  local key="$1"
  local val="${!key:-}"
  if [[ -z "$val" ]]; then
    printf '  %-40s | cloudflare-pages      | MISSING\n' "$key"
    return 1
  fi
  printf '%s' "$val" | wrangler pages secret put "$key" --project-name "$CF_PAGES_PROJECT" >/dev/null
  printf '  %-40s | cloudflare-pages      | OK\n' "$key"
}

push_gh() {
  local key="$1"
  local val="${!key:-}"
  if [[ -z "$val" ]]; then
    printf '  %-40s | github-actions        | MISSING\n' "$key"
    return 1
  fi
  printf '%s' "$val" | gh secret set "$key" --body - >/dev/null
  printf '  %-40s | github-actions        | OK\n' "$key"
}

FAIL=0

echo "==> Pushing to Fly (app: $FLY_APP)"
for k in "${FLY_KEYS[@]}"; do push_fly "$k" || FAIL=1; done
flyctl secrets deploy --app "$FLY_APP" >/dev/null 2>&1 || true

echo "==> Pushing to Cloudflare Pages (project: $CF_PAGES_PROJECT)"
for k in "${CF_PAGES_KEYS[@]}"; do push_cf_pages "$k" || FAIL=1; done

echo "==> Pushing to GitHub Actions"
for k in "${GH_KEYS[@]}"; do push_gh "$k" || FAIL=1; done

if [[ $FAIL -ne 0 ]]; then
  echo ""
  echo "FAILURES present above. Edit infra/.env.prod.sops.yaml (make secrets-edit) and re-run."
  exit 2
fi

echo ""
echo "OK. All secrets propagated."
