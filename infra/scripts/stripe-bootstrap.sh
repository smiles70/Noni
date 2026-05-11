#!/usr/bin/env bash
# infra/scripts/stripe-bootstrap.sh
#
# Idempotent: creates the Modules 4-5 product, price, and webhook endpoint in
# Stripe (test mode). Writes the resulting price ID and webhook secret back to
# the SOPS-encrypted production env, then re-runs secrets-sync.

set -euo pipefail

INFRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT_DIR="$(cd "$INFRA_DIR/.." && pwd)"
SOPS_FILE="$INFRA_DIR/.env.prod.sops.yaml"

require() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: required CLI missing: $1"; exit 1; }; }
require stripe
require sops
require jq

PRODUCT_NAME="Noni Modules 4-5"
PRICE_CENTS="${STRIPE_BOOTSTRAP_PRICE_CENTS:-4900}"   # default $49 — change in ADR 0021 if needed
CURRENCY="${STRIPE_BOOTSTRAP_CURRENCY:-usd}"
WEBHOOK_URL="${PROD_WEBHOOK_URL:-https://noni-api.fly.dev/api/billing/stripe-webhook}"

echo "==> Looking for existing product '$PRODUCT_NAME'"
PRODUCT_ID="$(stripe products list --limit 100 | jq -r --arg n "$PRODUCT_NAME" '.data[] | select(.name == $n) | .id' | head -n1 || true)"

if [[ -z "$PRODUCT_ID" ]]; then
  echo "==> Creating product"
  PRODUCT_ID="$(stripe products create --name "$PRODUCT_NAME" --description "One-time purchase: Modules 4 (Skills) and 5 (Agents from Skills)." | jq -r '.id')"
fi
echo "    product: $PRODUCT_ID"

echo "==> Looking for an active price under product $PRODUCT_ID"
PRICE_ID="$(stripe prices list --product "$PRODUCT_ID" --active | jq -r '.data[0].id // empty')"

if [[ -z "$PRICE_ID" ]]; then
  echo "==> Creating price (${PRICE_CENTS} ${CURRENCY})"
  PRICE_ID="$(stripe prices create --product "$PRODUCT_ID" --unit-amount "$PRICE_CENTS" --currency "$CURRENCY" | jq -r '.id')"
fi
echo "    price:   $PRICE_ID"

echo "==> Ensuring webhook endpoint $WEBHOOK_URL"
EXISTING_WEBHOOK="$(stripe webhook_endpoints list | jq -r --arg u "$WEBHOOK_URL" '.data[] | select(.url == $u) | .id' | head -n1 || true)"

if [[ -n "$EXISTING_WEBHOOK" ]]; then
  echo "    webhook: $EXISTING_WEBHOOK (already present)"
  echo "    (secret cannot be re-fetched; rotate via 'stripe webhook_endpoints update' if lost)"
else
  WEBHOOK_JSON="$(stripe webhook_endpoints create --url "$WEBHOOK_URL" --enabled-events checkout.session.completed --enabled-events charge.refunded --enabled-events charge.dispute.created)"
  WEBHOOK_ID="$(echo "$WEBHOOK_JSON" | jq -r '.id')"
  WEBHOOK_SECRET="$(echo "$WEBHOOK_JSON" | jq -r '.secret')"
  echo "    webhook: $WEBHOOK_ID"

  echo "==> Persisting STRIPE_WEBHOOK_SECRET to SOPS file"
  sops --set "[\"STRIPE_WEBHOOK_SECRET\"] \"$WEBHOOK_SECRET\"" "$SOPS_FILE"
fi

echo "==> Persisting STRIPE_PRICE_ID_MODULES_4_5 to SOPS file"
sops --set "[\"STRIPE_PRICE_ID_MODULES_4_5\"] \"$PRICE_ID\"" "$SOPS_FILE"

echo "==> Reconciling vendor secrets"
bash "$INFRA_DIR/scripts/secrets-sync.sh"

echo ""
echo "OK. Stripe bootstrap complete."
echo "    product: $PRODUCT_ID"
echo "    price:   $PRICE_ID"
