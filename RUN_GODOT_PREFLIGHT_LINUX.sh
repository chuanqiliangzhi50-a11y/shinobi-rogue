#!/bin/bash
set -u
cd "$(dirname "$0")"
GODOT=""
if command -v godot4 >/dev/null 2>&1; then GODOT="$(command -v godot4)"; fi
if [ -z "$GODOT" ] && command -v godot >/dev/null 2>&1; then GODOT="$(command -v godot)"; fi
if [ -z "$GODOT" ]; then echo "[NG] Godot 4 executable was not found."; exit 10; fi
"$GODOT" --headless --editor --quit --path "$PWD" || exit $?
"$GODOT" --headless --path "$PWD" -- --shinobi-regression || exit $?
echo "[PASS] Godot preflight completed."
