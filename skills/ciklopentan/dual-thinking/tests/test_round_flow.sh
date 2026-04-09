#!/usr/bin/env bash
set -euo pipefail

FIXTURE="${1:-$(dirname "$0")/fixtures/sample-round-block.txt}"

require() {
  local needle="$1"
  if ! grep -Fq "$needle" "$FIXTURE"; then
    echo "[FAIL] missing field: $needle" >&2
    exit 1
  fi
}

require 'ROUND:'
require 'TOPIC:'
require 'MODE:'
require 'SESSION:'
require 'DECISION:'
require 'NEXT_ACTION:'
require 'CHAT_CONTINUITY:'
require 'VALIDATION_STATUS:'
require 'RESUME_SNIPPET:'

ROUND_NUM="$(awk '/^ROUND:/{print $2; exit}' "$FIXTURE")"
CHAT_CONTINUITY="$(awk -F': ' '/^CHAT_CONTINUITY:/{print $2; exit}' "$FIXTURE")"

if [[ -n "$ROUND_NUM" ]] && [[ "$ROUND_NUM" -gt 1 ]] && [[ "$CHAT_CONTINUITY" == "new" ]]; then
  echo '[FAIL] round 2+ cannot default to a new chat' >&2
  exit 1
fi

if grep -Fq 'PATCH_STATUS: applied' "$FIXTURE"; then
  require 'PATCH_MANIFEST:'
fi

VALIDATION_STATUS="$(awk -F': ' '/^VALIDATION_STATUS:/{print $2; exit}' "$FIXTURE")"
PUBLISH_STATUS="$(awk -F': ' '/^PUBLISH_STATUS:/{print $2; exit}' "$FIXTURE")"

case "$VALIDATION_STATUS" in
  passed|failed|blocked) ;;
  *)
    echo '[FAIL] VALIDATION_STATUS must be passed|failed|blocked' >&2
    exit 1
    ;;
esac

if [[ "$PUBLISH_STATUS" == "Packaged" || "$PUBLISH_STATUS" == "Published" ]]; then
  if [[ "$VALIDATION_STATUS" != "passed" ]]; then
    echo '[FAIL] packaged/published requires VALIDATION_STATUS: passed' >&2
    exit 1
  fi
fi

if grep -Fq 'CONTINUATION_SIGNAL: stop' "$FIXTURE"; then
  if grep -Fq 'PATCH_STATUS: proposed' "$FIXTURE"; then
    echo '[FAIL] stop signal cannot coexist with unapplied proposed patch' >&2
    exit 1
  fi
fi

echo '[OK] round flow fixture passed'
