#!/usr/bin/env bash
# macOS launchd wrapper — 3次失败后停止，等待人工介入
set -euo pipefail

OPENCLAW_BIN="__OPENCLAW_BIN__"
STATE_DIR="__OPENCLAW_DIR__/gateway-rescue"
COUNT_FILE="$STATE_DIR/restart-count"
LOCK_FILE="$STATE_DIR/manual-intervention-required"

# 人工介入后重置计数
if [ -f "$LOCK_FILE" ]; then
    echo "[watchdog] 已锁定，等待人工介入。修复后运行: bash scripts/uninstall.sh && bash scripts/install.sh"
    exit 1
fi

mkdir -p "$STATE_DIR"

# 计数
count=0
[ -f "$COUNT_FILE" ] && count=$(cat "$COUNT_FILE")
count=$((count + 1))
echo "$count" > "$COUNT_FILE"

if [ "$count" -ge 3 ]; then
    echo "[watchdog] 已连续失败 $count 次，停止重启，等待人工介入"
    echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') — 连续失败3次，已停止" >> "$STATE_DIR/intervention-log.txt"
    touch "$LOCK_FILE"
    exit 1
fi

echo "[watchdog] 第 $count/3 次尝试启动..."
"$OPENCLAW_BIN" gateway start
