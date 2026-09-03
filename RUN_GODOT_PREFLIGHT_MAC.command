#!/bin/bash
set -u
cd "$(dirname "$0")"
GODOT=""

if command -v godot4 >/dev/null 2>&1; then GODOT="$(command -v godot4)"; fi
if [ -z "$GODOT" ] && command -v godot >/dev/null 2>&1; then GODOT="$(command -v godot)"; fi
if [ -z "$GODOT" ] && [ -x "/Applications/Godot.app/Contents/MacOS/Godot" ]; then GODOT="/Applications/Godot.app/Contents/MacOS/Godot"; fi

if [ -z "$GODOT" ]; then
  echo "[NG] Godot 4 executable was not found."
  exit 10
fi

echo "[1/2] Godot parser/editor startup check..."
"$GODOT" --headless --editor --quit --path "$PWD" || exit $?

echo "[2/2] SHINOBI non-destructive regression..."
"$GODOT" --headless --path "$PWD" -- --shinobi-regression || exit $?

echo "[PASS] Godot preflight completed."
