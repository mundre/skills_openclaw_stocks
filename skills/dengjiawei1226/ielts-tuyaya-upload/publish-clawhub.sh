#!/bin/bash
# ClawHub 一键发布脚本
# 用法: bash publish-clawhub.sh

set -e

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
SLUG="ielts-tuyaya-upload"
NAME="IELTS Tuyaya Upload 雅思成绩一键上传"
VERSION="1.1.0"
TAGS="latest"
CHANGELOG="v1.1.0: 文档大幅增强——README 和 SKILL.md 补充完整的\"端到端一条龙\"使用指南，配合 ielts-reading-review v3.4.0+ 实现自动扫 → 生成 JSON → 批量上传的全流程。新增流程示意图、耗时参考、踩坑提示、Q&A。扩展触发词，\"批量导入历史复盘\"\"端到端同步雅思\"等表达也能触发。\n\nv1.0.0: 首个公开版本。支持多用户——本地不再硬编码 token，新增 --register（注册）/--login（登录）/--logout/--whoami 命令，token 持久化到 ~/.ielts-tuyaya-token（0600 权限，30 天有效）。批量上传能自动跳过服务器已有记录，diff 命令可提前对比本地与云端差量。替代手动拖 JSON 到 tuyaya.online/ielts/submit.html 的流程，配合 ielts-reading-review 生成的 v3 JSON 一键同步。"

echo "📦 准备发布到 ClawHub..."
echo "   Slug: $SLUG"
echo "   Version: $VERSION"
echo "   Path: $SKILL_DIR"
echo ""

# 检查 clawhub CLI 是否安装
if ! command -v clawhub &> /dev/null; then
    echo "⚠️  clawhub CLI 未安装，正在安装..."
    npm i -g clawhub
fi

# 检查是否已登录
echo "🔐 检查登录状态..."
if ! clawhub whoami &> /dev/null 2>&1; then
    echo "⚠️  未登录，请先运行: clawhub login"
    clawhub login
fi

# 发布
echo ""
echo "🚀 开始发布..."
clawhub publish "$SKILL_DIR" \
    --slug "$SLUG" \
    --name "$NAME" \
    --version "$VERSION" \
    --tags "$TAGS" \
    --changelog "$CHANGELOG"

echo ""
echo "✅ 发布完成！"
echo "   查看: https://clawhub.ai/skill/$SLUG"
echo "   安装: clawhub install $SLUG"
