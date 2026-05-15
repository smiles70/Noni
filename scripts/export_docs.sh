#!/usr/bin/env bash
# Convert Markdown files to .txt, .pdf, and .docx and copy to a destination folder.
#
# Usage:
#   scripts/export_docs.sh                  # exports every *.md in the repo
#   scripts/export_docs.sh README.md docs/staging-deploy.md
#   DEST=/mnt/c/Users/kimem/Desktop/Noni scripts/export_docs.sh
#
# Requires: pandoc, wkhtmltopdf  (apt install pandoc wkhtmltopdf).

set -euo pipefail

DEST="${DEST:-/mnt/c/Users/kimem/Desktop/Noni}"
mkdir -p "$DEST"

command -v pandoc      >/dev/null || { echo "pandoc not installed" >&2; exit 1; }
command -v wkhtmltopdf >/dev/null || { echo "wkhtmltopdf not installed" >&2; exit 1; }

# Collect inputs.
if [ "$#" -gt 0 ]; then
  FILES=("$@")
else
  mapfile -t FILES < <(find . -type f -name '*.md' \
      -not -path './node_modules/*' \
      -not -path './frontend/node_modules/*' \
      -not -path './.git/*' \
      -not -path './venv/*' \
      | sort)
fi

[ "${#FILES[@]}" -eq 0 ] && { echo "No markdown files found." >&2; exit 0; }

# Detect basename collisions; disambiguate with parent folder name.
declare -A _seen=()
for src in "${FILES[@]}"; do
  b="$(basename "${src%.md}")"
  _seen["$b"]=$(( ${_seen["$b"]:-0} + 1 ))
done

echo "Exporting ${#FILES[@]} file(s) to: $DEST"
echo

for src in "${FILES[@]}"; do
  if [ ! -f "$src" ]; then
    echo "  skip: $src (not found)"
    continue
  fi
  base="$(basename "${src%.md}")"
  if [ "${_seen["$base"]}" -gt 1 ]; then
    parent="$(basename "$(dirname "$src")")"
    base="${parent}_${base}"
  fi
  printf '  %-55s -> %s.{txt,pdf,docx}\n' "$src" "$base"

  pandoc "$src" -t plain -o "$DEST/$base.txt"
  pandoc "$src"          -o "$DEST/$base.docx"
  pandoc "$src" -s --metadata title="$base" \
      --pdf-engine=wkhtmltopdf \
      -V margin-top=20mm -V margin-bottom=20mm \
      -V margin-left=20mm -V margin-right=20mm \
      -o "$DEST/$base.pdf"
done

echo
echo "Done. Output folder: $DEST"
