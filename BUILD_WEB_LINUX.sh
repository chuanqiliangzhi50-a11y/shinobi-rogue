#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
GODOT_BIN="$(command -v godot4 || command -v godot || true)"
if [[ -z "$GODOT_BIN" ]]; then
  echo "[ERROR] Godot executable not found." >&2
  exit 1
fi

echo "[1/3] Importing project resources..."
"$GODOT_BIN" --headless --editor --path . --quit-after 2

echo "[2/3] Running regression..."
"$GODOT_BIN" --headless --path . -- --shinobi-regression 2>&1 | tee web_regression.log
grep -Fq 'SHINOBI_REGRESSION PASS ALL:' web_regression.log
if grep -Fq 'ERROR:' web_regression.log; then
  echo '[ERROR] Godot reported an ERROR line.' >&2
  exit 1
fi

echo "[3/3] Exporting Web release..."
mkdir -p web
"$GODOT_BIN" --headless --path . --export-release 'Web' 'web/index.html'
echo '[PASS] Web release generated in ./web/'
