#!/usr/bin/env bash
# Record a routing miss for later synonym-map promotion.
# Usage: record_miss.sh "<user question>" "<path you ended up fetching>"
# Appends one line to ~/.openclaw/openclaw-docs/misses.md.
# Never auto-edits SKILL.md. Promotion to the Synonym Map is a human decision
# after three comparable hits (see Evolution Loop in SKILL.md).
set -eu
[ $# -lt 2 ] && { echo 'usage: record_miss.sh "<question>" "<path>"' >&2; exit 2; }
q="$1"
path="$2"
dir="$HOME/.openclaw/openclaw-docs"
log="$dir/misses.md"
mkdir -p "$dir"
if [ ! -f "$log" ]; then
  printf '# Routing misses\n\nOne line per miss: timestamp | question | fetched path.\nPromote to SKILL.md Synonym Map only after 3 comparable hits.\n\n' > "$log"
fi
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
# Flatten newlines in the question so each miss stays on one line.
q_one=$(printf '%s' "$q" | tr '\n' ' ')
printf '%s | %s | %s\n' "$ts" "$q_one" "$path" >> "$log"
printf 'recorded: %s\n' "$log"
