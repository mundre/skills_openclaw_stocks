#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
AMY'S WEBSITE FACTORY — new-site

Scaffold a new Next.js (latest) site with TS + Tailwind + ESLint, then git init and commit.

Usage:
  new-site.sh --slug <folder-name> [--dir <sites-dir>]

Notes:
- Non-destructive: refuses if target dir exists.
- Creates git repo with 1 commit: "chore: scaffold".
EOF
}

SLUG=""
SITES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/sites"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --slug) SLUG="$2"; shift 2;;
    --dir) SITES_DIR="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 2;;
  esac
done

[[ -n "$SLUG" ]] || { echo "Missing --slug"; usage; exit 2; }

TARGET="$SITES_DIR/$SLUG"
[[ ! -e "$TARGET" ]] || { echo "Refuse: target exists: $TARGET"; exit 2; }

mkdir -p "$SITES_DIR"

cd "$SITES_DIR"

npx create-next-app@latest "$SLUG" \
  --typescript --tailwind --eslint --app --src-dir \
  --import-alias "@/*" --use-npm --yes

cd "$SLUG"

# Replace scaffold README (factory standard).
cat > README.md <<EOF
# ${SLUG} — website

Built with **Next.js (App Router) + TypeScript + Tailwind**.

## Local development

```bash
npm install
npm run dev
```

## Quality gates

```bash
npm run lint
npm run build
npm audit --audit-level=low
```
EOF

git init -q
# keep default branch as-is, user can change globally.
git add -A
git commit -m "chore: scaffold" >/dev/null

echo "OK: created $TARGET"
