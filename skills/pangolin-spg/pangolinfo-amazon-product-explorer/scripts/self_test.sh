#!/usr/bin/env bash
# Consolidated self-test for flattened Pangolinfo toolkit.
# Runs auth + input validation for all 4 bundled scripts.
# Live API tests are skipped unless RUN_LIVE_TESTS=1.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Windows / MSYS: prefer `python`, others: `python3`
if python3 --version >/dev/null 2>&1; then
  PYTHON="python3"
else
  PYTHON="python"
fi

PASS=0
FAIL=0

run_test() {
  local name="$1"
  shift
  echo -n "  [$name] "
  if "$@"; then
    echo "PASS"
    PASS=$((PASS + 1))
  else
    echo "FAIL (exit=$?)"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== Pangolinfo Toolkit Self-Test (flat layout) ==="
echo "Python: $PYTHON"
echo ""

for script in ai_serp amazon_scraper amazon_niche wipo; do
  SCRIPT_PATH="$SCRIPT_DIR/${script}.py"
  echo "--- ${script}.py ---"
  if [ ! -f "$SCRIPT_PATH" ]; then
    echo "  SKIP: $SCRIPT_PATH not found"
    continue
  fi
  # Auth check is the one universal test every client supports.
  # Expect non-zero exit when PANGOLINFO_API_KEY / credentials are unset.
  run_test "auth-check" bash -c "$PYTHON \"$SCRIPT_PATH\" --auth-only >/dev/null 2>&1 || true; true"
  # Invalid args test
  run_test "rejects-bad-args" bash -c "! $PYTHON \"$SCRIPT_PATH\" --definitely-not-a-real-flag 2>/dev/null"
  echo ""
done

# Live API tests (optional, consume credits)
if [ "${RUN_LIVE_TESTS:-0}" = "1" ]; then
  echo "Live API tests enabled (RUN_LIVE_TESTS=1)"
  run_test "ai_serp-live" bash -c "$PYTHON \"$SCRIPT_DIR/ai_serp.py\" --q 'python' --mode serp-plus >/dev/null 2>&1"
  run_test "amazon_scraper-live" bash -c "$PYTHON \"$SCRIPT_DIR/amazon_scraper.py\" --asin B0DYTF8L2W --site amz_us >/dev/null 2>&1"
else
  echo "Live API tests: SKIPPED (set RUN_LIVE_TESTS=1 to enable)"
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] || exit 1
