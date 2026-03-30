#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "$SKILL_DIR/../.." && pwd)"
MCP_DIR="$REPO_ROOT/partykeys-mcp"

echo "=== Prepare PartyKeys MIDI Skill for Distribution ==="
echo "Source:  $MCP_DIR"
echo "Target:  $SKILL_DIR"
echo ""

if [ ! -d "$MCP_DIR/server" ]; then
  echo "ERROR: partykeys-mcp/server/ not found at $MCP_DIR"
  exit 1
fi

mkdir -p "$SKILL_DIR/server"
cp "$MCP_DIR/server/mcp_server.py" "$SKILL_DIR/server/"
cp "$MCP_DIR/server/script_ble_client.py" "$SKILL_DIR/server/"
cp "$MCP_DIR/server/web_gateway_server.py" "$SKILL_DIR/server/"
cp "$MCP_DIR/server/requirements.txt" "$SKILL_DIR/server/" 2>/dev/null || true

echo "[✓] server/ copied"

mkdir -p "$SKILL_DIR/web-gateway"
cp "$MCP_DIR/web-gateway/package.json" "$SKILL_DIR/web-gateway/"
for f in "$MCP_DIR/web-gateway"/*.js "$MCP_DIR/web-gateway"/*.html; do
  [ -f "$f" ] && cp "$f" "$SKILL_DIR/web-gateway/"
done

echo "[✓] web-gateway/ copied"

echo ""
echo "Distribution ready. You can now publish:"
echo "  clawhub skill publish $SKILL_DIR --slug partykeys-midi --name 'PartyKeys MIDI' --version 1.0.0"
