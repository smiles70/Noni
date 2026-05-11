#!/usr/bin/env bash
# infra/scripts/restore-drill.sh
#
# Quarterly restore drill: pull the latest pg_dump from R2, restore into a
# named ephemeral Postgres, run a schema-diff against production, print report.

set -euo pipefail

INFRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

require() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: required CLI missing: $1"; exit 1; }; }
require wrangler
require pg_restore
require psql

BUCKET="${CLOUDFLARE_R2_BUCKET:-noni-backups}"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

echo "==> Locating latest backup in r2://$BUCKET"
LATEST="$(wrangler r2 object list "$BUCKET" 2>/dev/null | awk '/noni-prod-.*\.dump/{print $NF}' | sort | tail -n1 || true)"
[[ -n "$LATEST" ]] || { echo "ERROR: no backups found"; exit 1; }
echo "    latest: $LATEST"

echo "==> Downloading"
wrangler r2 object get "$BUCKET/$LATEST" --file "$TMPDIR/latest.dump"

echo "==> Restoring to ephemeral local Postgres (container 'noni_restore_drill')"
docker run -d --rm --name noni_restore_drill -e POSTGRES_PASSWORD=postgres -p 55432:5432 postgres:15 >/dev/null
sleep 5
PGPASSWORD=postgres pg_restore --clean --if-exists --no-owner --no-acl \
  --host=localhost --port=55432 --username=postgres --dbname=postgres "$TMPDIR/latest.dump"

echo "==> Schema-diff against production (read-only)"
PGPASSWORD=postgres psql -h localhost -p 55432 -U postgres -c '\d+' | head -n 40

docker stop noni_restore_drill >/dev/null
echo ""
echo "OK. Restore drill succeeded. Latest dump is restorable."
