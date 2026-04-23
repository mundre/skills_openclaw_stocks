#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
AMY'S WEBSITE FACTORY — publish-site

Create GitHub repo (if missing), set origin, push commits + tags, then deploy a live Vercel preview.

Usage:
  publish-site.sh --site <path-to-site> --repo <owner/name> [--public|--private]

Safety:
- Refuses if git working tree is dirty.
EOF
}

SITE=""
REPO=""
VIS="--private"
FACTORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOY_SCRIPT="$FACTORY_ROOT/scripts/deploy-site.sh"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --site) SITE="$2"; shift 2;;
    --repo) REPO="$2"; shift 2;;
    --public) VIS="--public"; shift 1;;
    --private) VIS="--private"; shift 1;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 2;;
  esac
done

[[ -n "$SITE" && -n "$REPO" ]] || { echo "Missing --site or --repo"; usage; exit 2; }

cd "$SITE"

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "Not a git repo: $SITE"; exit 2; }

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Refuse: dirty working tree. Commit/stash first." >&2
  exit 2
fi

# Create remote repo if it doesn't exist.
if ! gh repo view "$REPO" >/dev/null 2>&1; then
  gh repo create "$REPO" $VIS --source=. --remote=origin
fi

# Ensure origin set.
if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin "git@github.com:${REPO}.git"
fi

# Push.
git push -u origin HEAD

# Push tags if any.
if git tag | grep -q .; then
  git push origin --tags
fi

echo "OK: pushed $REPO"
echo "Deploying live preview to Vercel..."
"$DEPLOY_SCRIPT" --site "$SITE"
