#!/bin/bash
# Test script for ppt-video skill
# 使用环境变量或相对路径

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="${HOME}/.openclaw/workspace"

# 使用环境变量或默认值
NODE_BIN="${NODE_BIN:-node}"
INPUT_DIR="${INPUT_DIR:-$WORKSPACE_DIR/wechat_articles/daily/presentation/2026-04-11}"

echo "Running ppt-video generation test..."
echo "Input directory: $INPUT_DIR"

# 动态获取 node 路径
if [ -x "$NODE_BIN" ]; then
    NODE_CMD="$NODE_BIN"
elif command -v node &> /dev/null; then
    NODE_CMD="node"
else
    echo "Error: Node.js not found"
    exit 1
fi

# 执行生成脚本
$NODE_CMD "$SCRIPT_DIR/scripts/generate.js" --input "$INPUT_DIR" --output "$SCRIPT_DIR/output/"
