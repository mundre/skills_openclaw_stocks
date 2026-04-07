#!/bin/bash
# ============================================================
# 创建工作空间脚本
# 版本：2.0.0
# 说明：为所有 agent 创建工作空间
# ============================================================

echo "创建 agent 工作空间..."

WORKSPACES=("workspace" "workspace-xg" "workspace-xc" "workspace-xd")
OPENCLAW_DIR="$HOME/.openclaw"

for ws in "${WORKSPACES[@]}"; do
    WS_PATH="$OPENCLAW_DIR/$ws"
    
    if [ ! -d "$WS_PATH" ]; then
        mkdir -p "$WS_PATH"
        echo "✓ 创建工作空间：$ws"
    else
        echo "✓ 工作空间已存在：$ws"
    fi
done

echo ""
echo "完成！工作空间路径："
for ws in "${WORKSPACES[@]}"; do
    echo "  - $OPENCLAW_DIR/$ws"
done
