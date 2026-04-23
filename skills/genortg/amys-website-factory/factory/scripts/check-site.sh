#!/usr/bin/env bash
set -euo pipefail

# Wrapper: invoke verify-site.sh with sane defaults so index.js can call a single script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/scripts"
FACTORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ $# -lt 1 ]]; then
  echo "Usage: check-site.sh --site <sites/<name>> [--port <port>]"
  exit 2
fi

SITE=""
PORT=3000

while [[ $# -gt 0 ]]; do
  case "$1" in
    --site) SITE="$2"; shift 2;;
    --port) PORT="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 2;;
  esac
done

NAME="$(basename "$SITE")"
ROUTES="$(cd "$(dirname "$SITE")" && pwd)/$(basename "$SITE")/routes.json"

# If routes file missing, create a minimal one targeting / and /about
if [[ ! -f "$ROUTES" ]]; then
  mkdir -p "$(dirname "$ROUTES")"
  cat > "$ROUTES" <<EOF
[
  { "path": "/" },
  { "path": "/about" }
]
EOF
fi

"${SCRIPT_DIR}/verify-site.sh" --site "$(cd "$SITE" && pwd)" --name "$NAME" --port "$PORT" --routes "$ROUTES"

