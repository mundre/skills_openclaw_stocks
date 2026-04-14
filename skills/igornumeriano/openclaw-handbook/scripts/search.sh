#!/usr/bin/env bash
# Full-text search across all OpenClaw docs.
# Usage: search.sh <keyword> [context-lines]
# Returns matching sections with surrounding context, capped at 200 lines.
set -eu
[ $# -lt 1 ] && { echo "usage: $0 <keyword> [context-lines]" >&2; exit 2; }
ctx="${2:-10}"
curl -sfL https://docs.openclaw.ai/llms-full.txt \
  | grep -i -A "$ctx" -B 2 "$1" \
  | head -200
