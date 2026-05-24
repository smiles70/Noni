#!/usr/bin/env bash
# infra/scripts/secrets-patch.sh
#
# Apply a sed-style substitution to a SOPS-encrypted dotenv file, in place,
# without ever leaving plaintext on disk longer than necessary. Used for
# small, deterministic edits where opening `sops` in an editor would
# require manual seek-and-find (which we forbid; see ADR 0025 §
# "operational discipline").
#
# Usage:
#   bash infra/scripts/secrets-patch.sh <sops-file> <sed-expression>
#
# Example (rewrite legacy postgres:// scheme to postgresql:// for
# SQLAlchemy 2.0 compatibility):
#   bash infra/scripts/secrets-patch.sh \
#     infra/.env.prod.sops.yaml \
#     's|^DATABASE_URL=postgres://|DATABASE_URL=postgresql://|'

set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <sops-file> <sed-expression>" >&2
  exit 1
fi

SOPS_FILE="$1"
SED_EXPR="$2"

if [[ ! -f "$SOPS_FILE" ]]; then
  echo "ERROR: $SOPS_FILE not found" >&2
  exit 1
fi

export SOPS_AGE_KEY_FILE="${SOPS_AGE_KEY_FILE:-$HOME/.config/sops/age/keys.txt}"

# Decrypt to a tempfile, patch, re-encrypt. The trap shreds the
# plaintext even if any step fails. `shred` may not exist on all
# systems (e.g. minimal Alpine); fall back to `rm -f` then.
#
# IMPORTANT: the tempfile path must match the creation rule in
# .sops.yaml so `sops --encrypt` finds an age recipient. We derive
# the tmp path from the sops file by stripping `.sops.yaml` and
# appending `.tmp` (e.g. infra/.env.prod.sops.yaml -> infra/.env.prod.tmp).
TMP="${SOPS_FILE%.sops.yaml}.tmp"
trap '{ shred -u "$TMP" 2>/dev/null || rm -f "$TMP"; } || true' EXIT
: > "$TMP"
chmod 600 "$TMP"

# Force the dotenv store on both sides. The encrypted file lives under
# a `.yaml` extension (so editors syntax-highlight it), but the cleartext
# payload is dotenv (KEY=value). Without `--output-type dotenv` here,
# sops would emit canonical YAML (`KEY: value`), which then fails to
# re-encrypt as dotenv on the way back. See getsops/sops #1196.
sops --decrypt --input-type yaml --output-type dotenv "$SOPS_FILE" > "$TMP"

BEFORE=$(grep -c . "$TMP" || true)
sed -i "$SED_EXPR" "$TMP"
AFTER=$(grep -c . "$TMP" || true)

if [[ "$BEFORE" != "$AFTER" ]]; then
  echo "ERROR: sed changed line count ($BEFORE -> $AFTER); refusing to write" >&2
  exit 1
fi

# Re-encrypt. Replace the existing file atomically: write to a
# sibling path first, then mv into place, so a partial encrypt
# doesn't leave the SOPS file unreadable.
NEW="$SOPS_FILE.new"
sops --encrypt --input-type dotenv --output-type yaml "$TMP" > "$NEW"
mv "$NEW" "$SOPS_FILE"

echo "OK. Patched $SOPS_FILE."
