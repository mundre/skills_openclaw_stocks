#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
AMY'S WEBSITE FACTORY — deploy-site

Build + deploy a linked Next.js site to Vercel.

Usage:
  deploy-site.sh --site <path-to-site> [--prod]

Behavior:
- Links the site to Vercel if .vercel/project.json is missing.
- Runs npm run build before deployment.
- Deploys a preview by default.
- Use --prod for production deployment.
EOF
}

SITE=""
PROD="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --site) SITE="$2"; shift 2;;
    --prod) PROD="true"; shift 1;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 2;;
  esac
done

[[ -n "$SITE" ]] || { echo "Missing --site"; usage; exit 2; }
[[ -d "$SITE" ]] || { echo "Not a directory: $SITE"; exit 2; }
[[ -f "$SITE/package.json" ]] || { echo "No package.json found: $SITE"; exit 2; }

SITE="$(cd "$SITE" && pwd)"
TOKEN_ARGS=()
if [[ -n "${VERCEL_TOKEN:-}" ]]; then
  TOKEN_ARGS=(--token "$VERCEL_TOKEN")
fi

if [[ ! -f "$SITE/.vercel/project.json" ]]; then
  echo "Linking site to Vercel..."
  vercel link --yes --cwd "$SITE" "${TOKEN_ARGS[@]}"
fi

echo "Building site..."
(cd "$SITE" && npm run build)

echo "Deploying to Vercel..."
DEPLOY_ARGS=(--cwd "$SITE" --yes)
if [[ "$PROD" == "true" ]]; then
  DEPLOY_ARGS+=(--prod)
fi
vercel deploy "${DEPLOY_ARGS[@]}" "${TOKEN_ARGS[@]}"
