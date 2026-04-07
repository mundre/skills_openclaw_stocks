#!/bin/bash
# ============================================================
# 同步配置脚本
# 版本：2.0.0
# 说明：同步 AGENTS.md 到所有 agent 工作空间
# ============================================================

echo "同步 AGENTS 配置到所有 agent..."

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../files"
OPENCLAW_DIR="$HOME/.openclaw"
AGENTS_FILE="$SKILL_DIR/AGENTS.md"

if [ ! -f "$AGENTS_FILE" ]; then
    echo "错误：找不到 AGENTS.md"
    exit 1
fi

WORKSPACES=("workspace" "workspace-xg" "workspace-xc" "workspace-xd")
SYNCED=0

for ws in "${WORKSPACES[@]}"; do
    WS_PATH="$OPENCLAW_DIR/$ws"
    
    if [ -d "$WS_PATH" ]; then
        cp "$AGENTS_FILE" "$WS_PATH/AGENTS.md"
        echo "✓ 已同步到 $ws/AGENTS.md"
        ((SYNCED++))
    else
        echo "✗ 跳过 $ws（工作空间不存在）"
    fi
done

echo ""
echo "同步完成！已同步 $SYNCED 个工作空间。"
