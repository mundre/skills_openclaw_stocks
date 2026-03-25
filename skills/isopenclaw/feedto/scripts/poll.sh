#!/bin/bash
set -euo pipefail
# FeedTo Feed Poller — fetches pending feeds for the agent to process
# Single poll per invocation, called every minute via cron
# Requires: curl, FEEDTO_API_KEY env var

API_URL="${FEEDTO_API_URL:-https://feedto.ai}"
API_KEY="${FEEDTO_API_KEY:-}"
MAX_RETRIES=2

if [ -z "$API_KEY" ]; then
  echo "ERROR: FEEDTO_API_KEY not set."
  echo "Configure it in openclaw.json under skills.entries.feedto.env"
  echo "Get your key at: https://feedto.ai/settings"
  exit 1
fi

fetch_feeds() {
  local attempt=0
  local response=""
  while [ $attempt -lt $MAX_RETRIES ]; do
    response=$(curl -s -f --max-time 20 --connect-timeout 8 \
      -H "X-API-Key: $API_KEY" \
      "${API_URL}/api/feeds/pending?limit=10" 2>&1) && break
    attempt=$((attempt + 1))
    [ $attempt -lt $MAX_RETRIES ] && sleep 2
  done

  if [ -z "$response" ]; then
    echo ""
    return 1
  fi
  echo "$response"
}

check_feeds() {
  local response
  response=$(fetch_feeds) || {
    echo "ERROR: Failed to fetch feeds from ${API_URL}" >&2
    return 1
  }

  # Check for empty feeds array (compatible with all grep versions)
  if echo "$response" | grep -q '"feeds" *: *\[\]'; then
    return 1  # no feeds
  fi
  # Also check minified format
  if echo "$response" | grep -q '"feeds":\[\]'; then
    return 1
  fi

  # Verify we actually have feed objects (look for "id": pattern inside feeds array)
  if ! echo "$response" | grep -q '"id" *:'; then
    return 1
  fi

  # Count feeds by counting complete UUID patterns (avoids false positives from content)
  local count
  count=$(echo "$response" | grep -oE '"id" *: *"[0-9a-f-]{36}"' | wc -l | tr -d ' ')

  if [ "${count:-0}" = "0" ]; then
    return 1
  fi

  echo "NEW_FEEDS: $count"
  echo ""
  echo "$response"
  return 0
}

# Single poll
if check_feeds; then
  exit 0
fi

echo "NO_NEW_FEEDS"
exit 0
