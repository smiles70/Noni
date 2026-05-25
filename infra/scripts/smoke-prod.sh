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
# backend/app/main.py returns {"status":"healthy", ...}; accept "ok" too
# for forward-compat if a future ADR canonicalises the shorter token.
echo "$HEALTH" | jq -e '.status == "healthy" or .status == "ok"' >/dev/null \
  || { echo "FAIL: /health not healthy"; exit 1; }

echo "==> GET $API_BASE/auth/config"
AUTH_CFG="$(curl -fsS "$API_BASE/auth/config")"
echo "$AUTH_CFG" | jq -e '.provider == "clerk" or .provider == "mock"' >/dev/null \
  || { echo "FAIL: /auth/config provider unrecognised"; exit 1; }

echo "==> GET $API_BASE/api/ui-envelope/landing.intro"
ENV_JSON="$(curl -fsS "$API_BASE/api/ui-envelope/landing.intro")"
echo "$ENV_JSON" | jq -e '.state_id == "landing.intro"' >/dev/null || { echo "FAIL: envelope mismatch"; exit 1; }

if [[ "$MODE" == "live" ]]; then
  echo "==> Verifying Stripe LIVE mode reachable"
  curl -fsS "$API_BASE/api/billing/health" | jq -e '.stripe_mode == "live"' >/dev/null \
    || { echo "FAIL: backend not in live Stripe mode"; exit 1; }
fi

echo ""
echo "==> Login scenario smoke (S4 rejection taxonomy + CORS + SLA)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$SCRIPT_DIR/smoke-login.sh" "$API_BASE" \
  || { echo "FAIL: login scenarios"; exit 1; }

echo ""
echo "OK. Smoke test passed ($MODE)."
