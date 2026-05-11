#!/usr/bin/env bash
# infra/scripts/secrets-rotate.sh KEY
#
# Rotate a single secret end-to-end:
#   1. Decrypt SOPS file to a tmpfile.
#   2. Prompt for new value (or generate for known auto-rotatable keys).
#   3. Update the SOPS file in place.
#   4. Run secrets-sync.
#   5. Print which artifacts need a restart.

set -euo pipefail

KEY="${1:-}"
if [[ -z "$KEY" ]]; then
  echo "Usage: make secrets-rotate KEY=<NAME>"
  exit 1
fi

INFRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOPS_FILE="$INFRA_DIR/.env.prod.sops.yaml"

# Auto-generate value for known-rotatable keys.
case "$KEY" in
  SESSION_SECRET)
    NEW_VAL="$(openssl rand -hex 32)"
    echo "==> Generated new $KEY (256 bits)"
    ;;
  *)
    read -rsp "Enter new value for $KEY: " NEW_VAL
    echo ""
    ;;
esac

# Update in-place via sops.
sops --set "[\"$KEY\"] \"$NEW_VAL\"" "$SOPS_FILE"

# Propagate.
bash "$INFRA_DIR/scripts/secrets-sync.sh"

# Restart hints.
case "$KEY" in
  SESSION_SECRET)
    echo ""
    echo "NEXT: existing sessions will be invalidated. Consider scheduling rotation during low traffic."
    echo "      flyctl machines restart --app \${FLY_APP_NAME:-noni-api}"
    ;;
  STRIPE_WEBHOOK_SECRET|STRIPE_SECRET_KEY|SUPABASE_JWT_SECRET|DATABASE_URL|DATABASE_URL_DIRECT)
    echo ""
    echo "NEXT: restart backend machines: flyctl machines restart --app \${FLY_APP_NAME:-noni-api}"
    ;;
  VITE_API_BASE_URL|STRIPE_PUBLISHABLE_KEY)
    echo ""
    echo "NEXT: redeploy frontend: wrangler pages deploy frontend/dist --project-name \${CLOUDFLARE_PAGES_PROJECT:-noni-web}"
    ;;
esac
