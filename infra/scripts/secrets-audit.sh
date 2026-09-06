#!/usr/bin/env bash
# infra/scripts/secrets-audit.sh
#
# Compare the key set in infra/.env.example against what each vendor holds.
# Prints a drift table; exits non-zero if any drift is detected.

set -euo pipefail

INFRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_EXAMPLE="$INFRA_DIR/.env.example"

require() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: required CLI missing: $1"; exit 1; }; }
require railway
require gh

RAILWAY_APP="${RAILWAY_APP_NAME:-noni-api}"

# Extract the canonical key list from .env.example (strip comments/blanks).
EXPECTED="$(grep -E '^[A-Z][A-Z0-9_]*=' "$ENV_EXAMPLE" | cut -d= -f1 | sort -u)"

echo "==> Railway secrets present"
RAILWAY_PRESENT="$(railway secrets list --app "$RAILWAY_APP" -j 2>/dev/null | grep -oE '"Name":\s*"[^"]+"' | cut -d'"' -f4 | sort -u || true)"

echo "==> GitHub Actions secrets present"
GH_PRESENT="$(gh secret list --json name --jq '.[].name' 2>/dev/null | sort -u || true)"

DRIFT=0
printf '  %-40s | %-15s | %-15s\n' "KEY" "RAILWAY" "GITHUB"
printf '  %-40s | %-15s | %-15s\n' "---" "---" "------"
while IFS= read -r key; do
  RAILWAY_has="-"
  gh_has="-"
  if grep -qx "$key" <<<"$RAILWAY_PRESENT"; then RAILWAY_has="OK"; else RAILWAY_has="MISS"; DRIFT=1; fi
  if grep -qx "$key" <<<"$GH_PRESENT"; then gh_has="OK"; else gh_has="--"; fi
  printf '  %-40s | %-15s | %-15s\n' "$key" "$RAILWAY_has" "$gh_has"
done <<<"$EXPECTED"

if [[ $DRIFT -ne 0 ]]; then
  echo ""
  echo "DRIFT DETECTED. Run 'make secrets-sync' to reconcile."
  exit 2
fi

echo ""
echo "OK. No drift."
