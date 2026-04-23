#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
AMY'S WEBSITE FACTORY — verify-site

Start Next.js dev server, run headless Playwright checks (desktop+mobile screenshots), write report.

Usage:
  verify-site.sh --site <path-to-site> --name <label> --port <port> --routes <routes.json>

Outputs:
  artifacts/<timestamp>-<name>/
    - report.md, report.json
    - *_desktop.png, *_mobile.png
    - dev.log

Safety:
- Kills dev server on exit.
EOF
}

SITE=""
NAME=""
PORT=""
ROUTES=""

FACTORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACTS_DIR="$FACTORY_ROOT/artifacts"
TOOL_DIR="$FACTORY_ROOT/tools/headless-webtest"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --site) SITE="$2"; shift 2;;
    --name) NAME="$2"; shift 2;;
    --port) PORT="$2"; shift 2;;
    --routes) ROUTES="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 2;;
  esac
done

[[ -n "$SITE" && -n "$NAME" && -n "$PORT" && -n "$ROUTES" ]] || { echo "Missing args"; usage; exit 2; }

# Resolve paths to absolute early (tool runs from tool dir).
SITE="$(cd "$SITE" && pwd)"
ROUTES="$(cd "$(dirname "$ROUTES")" && pwd)/$(basename "$ROUTES")"

TS=$(date -u +%Y-%m-%dT%H-%M-%SZ)
OUTDIR="$ARTIFACTS_DIR/${TS}-${NAME}"
mkdir -p "$OUTDIR"

DEV_LOG="$OUTDIR/dev.log"

# Start dev server.
cd "$SITE"

# Ensure port is free.
if ss -lptn 2>/dev/null | grep -q ":$PORT"; then
  echo "Refuse: port $PORT already in use" >&2
  exit 2
fi

npm run dev -- --port "$PORT" >"$DEV_LOG" 2>&1 &
DEV_PID=$!

cleanup() {
  if kill -0 "$DEV_PID" >/dev/null 2>&1; then
    kill "$DEV_PID" >/dev/null 2>&1 || true
    # give it a moment
    sleep 0.2 || true
    kill -9 "$DEV_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

# Wait for server.
for i in $(seq 1 60); do
  if curl -sS "http://127.0.0.1:$PORT/" >/dev/null 2>&1; then
    break
  fi
  sleep 0.25
  if [[ $i -eq 60 ]]; then
    echo "Dev server did not become ready. See $DEV_LOG" >&2
    exit 1
  fi
done

# Run headless checks.
cd "$TOOL_DIR"
node check-one.mjs \
  --baseUrl "http://127.0.0.1:$PORT" \
  --routes "$ROUTES" \
  --outDir "$OUTDIR"

echo "OK: $OUTDIR"
