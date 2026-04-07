#!/bin/bash
# ============================================================
# Swarm Control Feishu - 一键部署脚本
# 版本：2.0.0
# 说明：自动部署飞书智能体集群
# ============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
OPENCLAW_DIR="$HOME/.openclaw"
CONFIG_FILE="$SKILL_DIR/files/openclaw-config.json"
AGENTS_FILE="$SKILL_DIR/files/AGENTS.md"
TEMPLATE_FILE="$SKILL_DIR/files/AGENTS_TEMPLATE.md"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Swarm Control Feishu - 部署工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查文件
echo -e "${YELLOW}[1/6] 检查文件...${NC}"
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}错误：找不到配置文件 $CONFIG_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 文件检查通过${NC}"
echo ""

# 备份现有配置
echo -e "${YELLOW}[2/6] 备份现有配置...${NC}"
if [ -f "$OPENCLAW_DIR/openclaw.json" ]; then
    BACKUP_DIR="$OPENCLAW_DIR/backups"
    mkdir -p "$BACKUP_DIR"
    BACKUP_FILE="$BACKUP_DIR/openclaw.json.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$OPENCLAW_DIR/openclaw.json" "$BACKUP_FILE"
    echo -e "${GREEN}✓ 配置已备份到 $BACKUP_FILE${NC}"
else
    echo -e "${GREEN}✓ 无需备份（首次安装）${NC}"
fi
echo ""

# 复制配置文件
echo -e "${YELLOW}[3/6] 复制配置文件...${NC}"
cp "$CONFIG_FILE" "$OPENCLAW_DIR/openclaw.json"
echo -e "${GREEN}✓ OpenClaw 配置已复制${NC}"
echo ""

# 创建工作空间
echo -e "${YELLOW}[4/6] 创建工作空间...${NC}"
WORKSPACES=("workspace" "workspace-xg" "workspace-xc" "workspace-xd")
for ws in "${WORKSPACES[@]}"; do
    if [ ! -d "$OPENCLAW_DIR/$ws" ]; then
        mkdir -p "$OPENCLAW_DIR/$ws"
        echo -e "${GREEN}✓ 创建工作空间 $ws${NC}"
    else
        echo -e "${GREEN}✓ 工作空间 $ws 已存在${NC}"
    fi
done
echo ""

# 复制 AGENTS 配置
echo -e "${YELLOW}[5/6] 复制 AGENTS 配置...${NC}"
for ws in "${WORKSPACES[@]}"; do
    cp "$AGENTS_FILE" "$OPENCLAW_DIR/$ws/AGENTS.md"
    echo -e "${GREEN}✓ $ws/AGENTS.md 已复制${NC}"
done
cp "$TEMPLATE_FILE" "$OPENCLAW_DIR/AGENTS_TEMPLATE.md"
echo -e "${GREEN}✓ AGENTS_TEMPLATE.md 已复制${NC}"
echo ""

"配置 sudo 免密
echo -e "${YELLOW}[6/6] 配置系统权限...${NC}"
if [ -w "/etc/sudoers.d" ]; then
    echo "lehua ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/lehua >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ sudo 免密已配置${NC}"
    else
        echo -e "${YELLOW}⚠ 需要手动配置 sudo 免密${NC}"
        echo "   请运行：sudo bash -c 'echo \"lehua ALL=(ALL) NOPASSWD: ALL\" > /etc/sudoers.d/lehua'"
    fi
else
    echo -e "${YELLOW}⚠ 无法配置 sudo 免密（需要 root 权限）${NC}"
    echo "   请运行：sudo bash -c 'echo \"lehua ALL=(ALL) NOPASSWD: ALL\" > /etc/sudoers.d/lehua'"
fi
echo ""

# 完成
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}下一步：${NC}"
echo "1. 检查配置：cat ~/.openclaw/openclaw.json"
echo "2. 重启网关：openclaw gateway restart"
echo "3. 启动语音服务：bash $SKILL_DIR/files/start-voice-service.sh"
echo "4. 检查状态：bash $SCRIPT_DIR/check-status.sh"
echo ""
echo -e "${YELLOW}注意：${NC}"
echo "- 确保已修改 config.json 中的飞书 App ID 和 App Secret"
echo "- 确保已修改 config.json 中的 LLM API Key"
echo ""
