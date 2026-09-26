#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

GODOT_BIN="$(command -v godot4 || command -v godot || true)"
if [[ -z "$GODOT_BIN" ]]; then
  echo "[ERROR] Godot executable not found." >&2
  exit 1
fi

IMPORT_TIMEOUT="${SHINOBI_IMPORT_TIMEOUT:-120}"
REGRESSION_TIMEOUT="${SHINOBI_REGRESSION_TIMEOUT:-180}"
EXPORT_TIMEOUT="${SHINOBI_EXPORT_TIMEOUT:-300}"

stamp() {
  date -u '+%Y-%m-%dT%H:%M:%SZ'
}

diag() {
  echo "[DIAG] $(stamp) process snapshot"
  ps -eo pid,ppid,stat,etime,cmd | grep -E 'godot|BUILD_WEB_LINUX|PID' || true
  echo "[DIAG] disk usage"
  df -h . || true
  echo "[DIAG] web directory"
  ls -lah web 2>/dev/null || true
}

trap 'rc=$?; echo "[ERROR] $(stamp) BUILD_WEB_LINUX failed rc=${rc}"; diag; exit ${rc}' ERR

echo "[INFO] $(stamp) Godot: $($GODOT_BIN --version)"
echo "[INFO] timeouts import=${IMPORT_TIMEOUT}s regression=${REGRESSION_TIMEOUT}s export=${EXPORT_TIMEOUT}s"

echo "[1/3] $(stamp) Importing project resources..."
if ! timeout --foreground "${IMPORT_TIMEOUT}s" "$GODOT_BIN" --headless --editor --path . --import; then
  rc=$?
  echo "[ERROR] $(stamp) Import failed or timed out after ${IMPORT_TIMEOUT}s (rc=${rc})." >&2
  diag
  exit 1
fi
echo "[PASS] $(stamp) Import complete."

echo "[2/3] $(stamp) Running regression..."
rm -f web_regression.log
"$GODOT_BIN" --headless --path . -- --shinobi-regression > >(tee web_regression.log) 2>&1 &
REG_PID=$!
REG_START=$(date +%s)
REG_PASS=0
while kill -0 "$REG_PID" 2>/dev/null; do
  if grep -Fq 'SHINOBI_REGRESSION PASS ALL:' web_regression.log 2>/dev/null; then
    REG_PASS=1
    echo "[PASS] $(stamp) Regression PASS ALL detected; stopping residual Godot process ${REG_PID}."
    kill -TERM "$REG_PID" 2>/dev/null || true
    for _ in 1 2 3 4 5; do
      kill -0 "$REG_PID" 2>/dev/null || break
      sleep 1
    done
    kill -KILL "$REG_PID" 2>/dev/null || true
    wait "$REG_PID" 2>/dev/null || true
    break
  fi
  NOW=$(date +%s)
  if (( NOW - REG_START >= REGRESSION_TIMEOUT )); then
    echo "[ERROR] $(stamp) Regression timed out after ${REGRESSION_TIMEOUT}s." >&2
    diag
    kill -TERM "$REG_PID" 2>/dev/null || true
    sleep 2
    kill -KILL "$REG_PID" 2>/dev/null || true
    wait "$REG_PID" 2>/dev/null || true
    exit 124
  fi
  sleep 1
done

if [[ "$REG_PASS" -ne 1 ]]; then
  wait "$REG_PID" 2>/dev/null || REG_RC=$?
  REG_RC="${REG_RC:-0}"
  if grep -Fq 'SHINOBI_REGRESSION PASS ALL:' web_regression.log 2>/dev/null; then
    REG_PASS=1
  else
    echo "[ERROR] $(stamp) Regression process exited without PASS ALL (rc=${REG_RC})." >&2
    tail -n 120 web_regression.log 2>/dev/null || true
    exit 1
  fi
fi

if grep -Fq 'ERROR:' web_regression.log; then
  echo '[ERROR] Godot reported an ERROR line.' >&2
  tail -n 120 web_regression.log || true
  exit 1
fi
echo "[PASS] $(stamp) Regression complete."

echo "[3/3] $(stamp) Exporting Web release..."
mkdir -p web
if ! timeout --foreground "${EXPORT_TIMEOUT}s" "$GODOT_BIN" --headless --path . --export-release 'Web' 'web/index.html'; then
  rc=$?
  echo "[ERROR] $(stamp) Web export failed or timed out after ${EXPORT_TIMEOUT}s (rc=${rc})." >&2
  diag
  exit 1
fi

test -s web/index.html
test -s web/index.js
test -s web/index.pck
test -s web/index.wasm

echo "[PASS] $(stamp) Web release generated in ./web/"
echo "[INFO] index.wasm bytes: $(wc -c < web/index.wasm)"
