#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PMO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

mkdir -p "$PMO_DIR/data"

for src in "$PMO_DIR"/templates/*.csv; do
  dst="$PMO_DIR/data/$(basename "$src")"
  if [[ ! -f "$dst" ]]; then
    cp "$src" "$dst"
    echo "created: $dst"
  else
    echo "exists:  $dst"
  fi
done
