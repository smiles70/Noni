#!/usr/bin/env bash
# infra/scripts/backup-now.sh
#
# Trigger a one-off pg_dump of production and upload to R2.

set -euo pipefail

INFRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOPS_FILE="$INFRA_DIR/.env.prod.sops.yaml"

require() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: required CLI missing: $1"; exit 1; }; }
require sops
require pg_dump
require wrangler

TMP="$(mktemp)"
trap 'shred -u "$TMP" 2>/dev/null || rm -f "$TMP"' EXIT
chmod 600 "$TMP"
sops --decrypt --input-type yaml --output-type dotenv "$SOPS_FILE" > "$TMP"
# shellcheck disable=SC1090
set -a; source "$TMP"; set +a

STAMP="$(date -u +%Y%m%d-%H%M%S)"
OUT="/tmp/noni-prod-${STAMP}.dump"
echo "==> pg_dump (custom format) -> $OUT"
pg_dump --format=custom --no-owner --no-acl --dbname="$DATABASE_URL_DIRECT" -f "$OUT"

BUCKET="${CLOUDFLARE_R2_BUCKET:-noni-backups}"
echo "==> Uploading to r2://$BUCKET/"
wrangler r2 object put "$BUCKET/noni-prod-${STAMP}.dump" --file "$OUT"

rm -f "$OUT"
echo ""
echo "OK. Backup uploaded: r2://$BUCKET/noni-prod-${STAMP}.dump"
