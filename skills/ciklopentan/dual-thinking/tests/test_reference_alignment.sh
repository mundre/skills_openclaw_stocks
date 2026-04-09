#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
SKILL="$ROOT/SKILL.md"
MODES="$ROOT/references/modes.md"
EXAMPLES="$ROOT/references/examples.md"

require_present() {
  local needle="$1" file="$2"
  if ! grep -Fq "$needle" "$file"; then
    echo "[FAIL] missing '$needle' in $file" >&2
    exit 1
  fi
}

require_absent() {
  local needle="$1" file="$2"
  if grep -Fq "$needle" "$file"; then
    echo "[FAIL] unexpected stale '$needle' in $file" >&2
    exit 1
  fi
}

require_present 'set `ORCHESTRATOR_MODE: multi`' "$SKILL"
require_present 'set `ORCHESTRATOR_MODE: multi`' "$MODES"
require_present '`ORCHESTRATOR_MODE: multi`' "$EXAMPLES"
require_present 'MODE:` stays the semantic task mode' "$EXAMPLES"
require_absent 'MODE: alternating-multi-orchestrator' "$EXAMPLES"
require_absent '`alternating-multi-orchestrator` when the user explicitly requested alternation before round 1.' "$MODES"

echo '[OK] reference alignment passed'
