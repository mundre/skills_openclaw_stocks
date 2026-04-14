#!/usr/bin/env bash
# Verify the skill is seeing current OpenClaw docs.
# Prints page count, sha256, and fetch timestamp — proves this is live, not cached.
set -eu
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT
curl -sfL https://docs.openclaw.ai/llms.txt > "$tmp"
pages=$(grep -c "^- \[" "$tmp" || true)
if command -v shasum >/dev/null 2>&1; then
  sha=$(shasum -a 256 "$tmp" | awk '{print $1}')
elif command -v sha256sum >/dev/null 2>&1; then
  sha=$(sha256sum "$tmp" | awk '{print $1}')
else
  sha="(no sha256 tool)"
fi
printf 'source: https://docs.openclaw.ai/llms.txt\npages:  %s\nsha256: %s\nfetched: %s\n' \
  "$pages" "$sha" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
