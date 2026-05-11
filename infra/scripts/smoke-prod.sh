#!/usr/bin/env bash
# infra/scripts/smoke-prod.sh [--live]
#
# Hit the deployed API health endpoint and a known envelope, verify expected JSON.

set -euo pipefail

MODE="test"
if [[ "${1:-}" == "--live" ]]; then MODE="live"; fi

API_BASE="${PROD_API_BASE_URL:-https://noni-api.fly.dev}"

require() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: required CLI missing: $1"; exit 1; }; }
require curl
require jq

echo "==> GET $API_BASE/health"
HEALTH="$(curl -fsS "$API_BASE/health")"
echo "$HEALTH" | jq -e '.status == "ok"' >/dev/null || { echo "FAIL: /health not ok"; exit 1; }

echo "==> GET $API_BASE/api/ui-envelope/landing.intro"
ENV_JSON="$(curl -fsS "$API_BASE/api/ui-envelope/landing.intro")"
echo "$ENV_JSON" | jq -e '.state_id == "landing.intro"' >/dev/null || { echo "FAIL: envelope mismatch"; exit 1; }

if [[ "$MODE" == "live" ]]; then
  echo "==> Verifying Stripe LIVE mode reachable"
  curl -fsS "$API_BASE/api/billing/health" | jq -e '.stripe_mode == "live"' >/dev/null \
    || { echo "FAIL: backend not in live Stripe mode"; exit 1; }
fi

echo ""
echo "OK. Smoke test passed ($MODE)."
