#!/usr/bin/env bash
set -euo pipefail

FIXTURE="${1:-$(dirname "$0")/fixtures/weak-model-shortcut-round.txt}"

require() {
  local needle="$1"
  if ! grep -Fq "$needle" "$FIXTURE"; then
    echo "[FAIL] missing field: $needle" >&2
    exit 1
  fi
}

require 'ROUND:'
require 'MODE:'
require 'DECISION:'
require 'NEXT_ACTION:'
require 'RESUME_SNIPPET:'
require 'LAST_CONSULTANT:'

echo '[OK] weak-model shortcut fixture passed'
