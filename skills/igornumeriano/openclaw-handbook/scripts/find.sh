#!/usr/bin/env bash
# Find OpenClaw doc pages matching a keyword.
# Usage: find.sh <keyword>
# Output: one match per line, format "Title  path.md"
set -eu
[ $# -lt 1 ] && { echo "usage: $0 <keyword>" >&2; exit 2; }
curl -sfL https://docs.openclaw.ai/llms.txt \
  | grep -iE "^- \[.*$1.*\]" \
  | sed -E 's|^- \[(.*)\]\(https://docs.openclaw.ai/(.*)\)|\1\t\2|'
