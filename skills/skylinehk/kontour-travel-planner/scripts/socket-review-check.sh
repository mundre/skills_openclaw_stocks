#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

fail() {
  echo "[FAIL] $1" >&2
  exit 1
}

pass() {
  echo "[PASS] $1"
}

echo "Running static trust review checks..."

# 1) Runtime scripts/helpers should not make outbound network calls.
if rg -n "\b(curl|wget)\b|\b(fetch|axios|requests)\s*\(|urllib\.(request|error|robotparser)\b|http\.client|aiohttp|ftplib|socket\." scripts/plan.sh scripts/export-gmaps.sh scripts/gen-airports.py >/tmp/socket-review-network.txt; then
  cat /tmp/socket-review-network.txt >&2
  fail "Runtime scripts/helpers include network-related patterns."
fi
pass "Runtime scripts/helpers contain no network-client patterns."

# 2) Runtime scripts/helpers should avoid dynamic command execution primitives.
if rg -n "eval\(|\beval\b|bash -c|sh -c|source <\(|os\.system|subprocess\.|exec\(|__import__\(|compile\(" scripts/plan.sh scripts/export-gmaps.sh scripts/gen-airports.py >/tmp/socket-review-exec.txt; then
  cat /tmp/socket-review-exec.txt >&2
  fail "Runtime scripts/helpers include dynamic execution patterns."
fi
pass "Runtime scripts/helpers contain no dynamic execution primitives."

# 2b) Python helper should not import network client modules.
if rg -n "^\s*(import|from)\s+(socket|requests|urllib|http\.client|ftplib|aiohttp)\b" scripts/gen-airports.py >/tmp/socket-review-python-imports.txt; then
  cat /tmp/socket-review-python-imports.txt >&2
  fail "Python helper imports network client modules."
fi
pass "Python helper imports stay offline-safe."

# 3) Ensure publish metadata keeps the approved license.
if ! rg -n "^license:\s*MIT-0$" SKILL.md >/dev/null; then
  fail "SKILL.md license is not MIT-0."
fi
pass "SKILL.md license remains MIT-0."

# 4) Spot obvious credential-like strings in tracked content.
if rg -n "AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{20,}" SKILL.md scripts references README.md >/tmp/socket-review-secrets.txt; then
  cat /tmp/socket-review-secrets.txt >&2
  fail "Potential credential pattern detected."
fi
pass "No obvious credential patterns detected."

echo "All static trust review checks passed."
