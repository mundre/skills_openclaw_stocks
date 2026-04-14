#!/usr/bin/env bash
# Self-test: validate every doc path referenced in SKILL.md still resolves on docs.openclaw.ai.
# Run before publishing, or schedule in CI, to catch decision-tree rot.
# Exits non-zero if any referenced path 404s.
set -eu
here="$(cd "$(dirname "$0")" && pwd)"
root="$here/.."
skill="$root/SKILL.md"
examples="$root/EXAMPLES.md"
[ -f "$skill" ] || { echo "SKILL.md not found at $skill" >&2; exit 2; }

if [ -f "$examples" ]; then
  stripped=$(cat "$skill" "$examples" | sed 's/`//g')
else
  stripped=$(sed 's/`//g' "$skill")
fi
paths=$( \
  { printf '%s\n' "$stripped" | grep -oE '→ [a-zA-Z0-9/_.-]+\.(md|json)' | sed 's/^→ //'; \
    printf '%s\n' "$stripped" | grep -oE ', [a-zA-Z0-9_-]+/[a-zA-Z0-9/_.-]+\.(md|json)' | sed 's/^, //'; \
  } | sort -u)

total=0
broken=0
while IFS= read -r p; do
  [ -z "$p" ] && continue
  total=$((total+1))
  url="https://docs.openclaw.ai/${p}"
  code=$(curl -sf -o /dev/null -w '%{http_code}' "$url" || echo "ERR")
  if [ "$code" != "200" ]; then
    printf '  BROKEN  %s  (%s)\n' "$p" "$code"
    broken=$((broken+1))
  fi
done <<EOF
$paths
EOF

printf '\nchecked: %d\nbroken:  %d\n' "$total" "$broken"
[ "$broken" -eq 0 ] || exit 1
