#!/usr/bin/env bash
# infra/scripts/observability-bootstrap.sh
#
# Configure BetterStack: log source token, 3 baseline monitors, status page.

set -euo pipefail

INFRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOPS_FILE="$INFRA_DIR/.env.prod.sops.yaml"

require() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: required CLI missing: $1"; exit 1; }; }
require curl
require jq
require sops

TMP="$(mktemp)"
trap 'shred -u "$TMP" 2>/dev/null || rm -f "$TMP"' EXIT
chmod 600 "$TMP"
sops --decrypt --input-type yaml --output-type dotenv "$SOPS_FILE" > "$TMP"
# shellcheck disable=SC1090
set -a; source "$TMP"; set +a

if [[ -z "${BETTERSTACK_API_TOKEN:-}" ]]; then
  echo "ERROR: BETTERSTACK_API_TOKEN not set in SOPS. Sign up at betterstack.com, then add the token."
  exit 1
fi

BASE="https://uptime.betterstack.com/api/v2"
H_AUTH="Authorization: Bearer $BETTERSTACK_API_TOKEN"
API_URL="${PROD_API_BASE_URL:-https://noni-api.fly.dev}"

create_monitor() {
  local name="$1" url="$2"
  echo "==> Monitor: $name -> $url"
  curl -fsS -X POST "$BASE/monitors" -H "$H_AUTH" -H 'Content-Type: application/json' \
    --data "$(jq -nc --arg n "$name" --arg u "$url" '{monitor_type:"status", url:$u, pronounceable_name:$n, check_frequency:60}')" \
    | jq -r '.data.id'
}

create_monitor "Noni API health"        "$API_URL/health"
create_monitor "Noni envelope landing"  "$API_URL/api/ui-envelope/landing.intro"
create_monitor "Noni billing health"    "$API_URL/api/billing/health"

echo ""
echo "OK. Observability bootstrap complete. Configure alert routing in BetterStack dashboard."
