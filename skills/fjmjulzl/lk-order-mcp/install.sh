#!/bin/bash
# lk-order-mcp Skill 安装脚本
# 
# 🔐 安全说明：
# - 本脚本从本地复制文件，不使用 curl|bash 模式
# - Token 需要手动配置，不会包含在安装包中
#
# 使用方法：
#   方式 1（推荐）：openclaw skills install lk-order-mcp
#   方式 2：bash install.sh [source_dir]

set -e

echo "🦞 Installing lk-order-mcp skill..."

# 确定 OpenClaw workspace 目录
WORKDIR="${OPENCLAW_WORKDIR:-$HOME/.openclaw/workspace}"
SKILLS_DIR="${WORKDIR}/skills"

# 源目录（优先使用参数，否则使用默认值）
SOURCE_DIR="${1:-$(dirname "$(readlink -f "$0")")}"

# 创建 skills 目录（如果不存在）
mkdir -p "${SKILLS_DIR}"

# 检查源目录是否存在
if [ ! -d "${SOURCE_DIR}" ]; then
    echo "❌ 源目录不存在：${SOURCE_DIR}"
    exit 1
fi

# 复制文件（排除敏感文件）
echo "📦 Copying files..."
cd "${SKILLS_DIR}"
rm -rf lk-order-mcp 2>/dev/null || true
cp -r "${SOURCE_DIR}" lk-order-mcp

# 排除不需要发布的文件
cd lk-order-mcp
rm -rf .git node_modules __pycache__ *.log 2>/dev/null || true

# 设置权限
chmod +x lk-order.cjs 2>/dev/null || true
chmod +x install.sh 2>/dev/null || true

# 创建 .env.example 文件（提示用户配置 Token）
cat > .env.example << 'EOF'
# lk-order-mcp Token 配置
# ⚠️ 请勿将此文件提交到版本控制！
# ⚠️ 复制为 .env 并填入你的 Token

LK_ORDER_TOKEN=your_token_here
EOF

echo ""
echo "✅ Skill installed successfully!"
echo ""
echo "📍 Location: ${SKILLS_DIR}/lk-order-mcp"
echo ""
echo "🔐 下一步：配置 Token"
echo ""
echo "  方式 1：环境变量"
echo "    export LK_ORDER_TOKEN=\"your_token\""
echo ""
echo "  方式 2：.env 文件"
echo "    cp ${SKILLS_DIR}/lk-order-mcp/.env.example ${SKILLS_DIR}/lk-order-mcp/.env"
echo "    编辑 .env 文件，填入你的 Token"
echo ""
echo "  方式 3：openclaw.json"
echo "    编辑 ~/.openclaw/openclaw.json"
echo "    在 mcpServers.lk-order.headers.Authorization 中填入"
echo ""
echo "⚠️  Please restart OpenClaw to load the new skill:"
echo "   openclaw gateway restart"
echo ""
echo "📖 Usage:"
echo "   /home/node/.openclaw/scripts/lkorder-mcp.sh init"
echo "   /home/node/.openclaw/scripts/lkorder-mcp.sh call quick_order '{\"keyword\":\"美式\"}'"
