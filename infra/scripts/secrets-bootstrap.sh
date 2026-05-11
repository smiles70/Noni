#!/usr/bin/env bash
# infra/scripts/secrets-bootstrap.sh
#
# One-time: generate an age key, encrypt the initial production env file.
# Idempotent: refuses to overwrite an existing encrypted file.

set -euo pipefail

INFRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT_DIR="$(cd "$INFRA_DIR/.." && pwd)"
SOPS_FILE="$INFRA_DIR/.env.prod.sops.yaml"
DRAFT_FILE="$INFRA_DIR/.env.prod.draft"
AGE_KEY_DIR="${SOPS_AGE_KEY_DIR:-$HOME/.config/sops/age}"
AGE_KEY_FILE="$AGE_KEY_DIR/keys.txt"
SOPS_CONFIG="$ROOT_DIR/.sops.yaml"

require() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: required CLI missing: $1"; exit 1; }; }
require sops
require age-keygen

if [[ -f "$SOPS_FILE" ]]; then
  echo "ERROR: $SOPS_FILE already exists. To edit, run: make secrets-edit"
  exit 1
fi

if [[ ! -f "$AGE_KEY_FILE" ]]; then
  echo "==> Generating new age key at $AGE_KEY_FILE"
  mkdir -p "$AGE_KEY_DIR"
  age-keygen -o "$AGE_KEY_FILE"
  chmod 600 "$AGE_KEY_FILE"
  echo ""
  echo "BACK UP THIS KEY NOW. Copy it into 1Password (or your team password manager)."
  echo "Without this key, the production secrets cannot be decrypted."
  echo ""
fi

PUBKEY="$(grep -E '^# public key:' "$AGE_KEY_FILE" | awk '{print $4}')"
if [[ -z "$PUBKEY" ]]; then
  PUBKEY="$(age-keygen -y "$AGE_KEY_FILE")"
fi
echo "==> Age public key: $PUBKEY"

# Update .sops.yaml with the real public key.
if grep -q 'REPLACE_WITH_AGE_PUBLIC_KEY_FROM_make_secrets-bootstrap' "$SOPS_CONFIG"; then
  sed -i.bak "s|REPLACE_WITH_AGE_PUBLIC_KEY_FROM_make_secrets-bootstrap|$PUBKEY|g" "$SOPS_CONFIG"
  rm -f "${SOPS_CONFIG}.bak"
  echo "==> Updated $SOPS_CONFIG with the age public key"
fi

# Expect the operator to have prepared a draft file from infra/.env.example.
if [[ ! -f "$DRAFT_FILE" ]]; then
  echo ""
  echo "Next step:"
  echo "  1. cp $INFRA_DIR/.env.example $DRAFT_FILE"
  echo "  2. Fill in real production values in $DRAFT_FILE"
  echo "  3. Re-run: make secrets-bootstrap"
  exit 0
fi

echo "==> Encrypting $DRAFT_FILE -> $SOPS_FILE"
sops --encrypt --input-type dotenv --output-type yaml --age "$PUBKEY" "$DRAFT_FILE" > "$SOPS_FILE"

echo "==> Shredding plaintext draft"
if command -v shred >/dev/null 2>&1; then
  shred -u "$DRAFT_FILE"
else
  rm -f "$DRAFT_FILE"
fi

echo ""
echo "OK. $SOPS_FILE created. Next: make secrets-sync"
