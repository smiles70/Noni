#!/usr/bin/env bash
# infra/scripts/stripe-promote.sh
#
# Promote Stripe configuration from test mode to live mode.
# Assumes the operator has finished Stripe account activation in the dashboard.

set -euo pipefail

INFRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> This will switch the production app to Stripe LIVE mode."
echo "    Required: Stripe account has completed activation."
read -rp "Proceed? [yes/NO] " ANSWER
[[ "$ANSWER" == "yes" ]] || { echo "Aborted."; exit 1; }

echo "==> Re-run stripe-bootstrap with live credentials"
echo "    Ensure your local 'stripe' CLI is logged in to the live key."
echo "    Edit infra/.env.prod.sops.yaml to set STRIPE_SECRET_KEY / STRIPE_PUBLISHABLE_KEY"
echo "    to the live values, then run:"
echo ""
echo "       make stripe-bootstrap"
echo "       make secrets-sync"
echo "       make smoke-prod-live"
