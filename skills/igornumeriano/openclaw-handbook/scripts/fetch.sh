#!/usr/bin/env bash
# Fetch a single OpenClaw doc page.
# Usage: fetch.sh <path>
# Accepts with/without .md extension and with/without leading slash.
# Examples:
#   fetch.sh concepts/soul
#   fetch.sh concepts/soul.md
#   fetch.sh /channels/telegram.md
set -eu
[ $# -lt 1 ] && { echo "usage: $0 <path>" >&2; exit 2; }
path="$1"
path="${path#/}"
case "$path" in
  *.md) ;;
  *)    path="${path}.md" ;;
esac
curl -sfL "https://docs.openclaw.ai/${path}"
