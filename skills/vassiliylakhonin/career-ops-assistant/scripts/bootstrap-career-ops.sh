#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-$PWD}"

if [ ! -d "$TARGET_DIR" ]; then
  echo "ERROR: target directory not found: $TARGET_DIR" >&2
  exit 1
fi

cd "$TARGET_DIR"

echo "[1/6] Installing npm deps..."
npm install

echo "[2/6] Installing Playwright Chromium..."
npx playwright install chromium

echo "[3/6] Ensuring profile config..."
[ -f config/profile.yml ] || cp config/profile.example.yml config/profile.yml

echo "[4/6] Ensuring portals config..."
[ -f portals.yml ] || cp templates/portals.example.yml portals.yml

echo "[5/6] Ensuring cv.md..."
if [ ! -f cv.md ]; then
  cat > cv.md <<'EOF'
# CV
Paste CV in markdown.
EOF
fi

echo "[6/6] Running doctor..."
npm run doctor

echo "Done. Career-Ops baseline is ready."
