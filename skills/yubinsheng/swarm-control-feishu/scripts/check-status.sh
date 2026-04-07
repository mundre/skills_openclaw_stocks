#!/bin/bash
# ============================================================
# 检查状态脚本
# 版本：2.0.0
# 说明：检查飞书智能体集群的运行状态
# ============================================================

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Swarm Control Feishu - 状态检查${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. 检查网关状态
echo -e "${YELLOW}[1/6] OpenClaw 网关状态${NC}"
if openclaw status >/dev/null 2>&1; then
    echo -e "${GREEN}✓ 网关运行中${NC}"
    openclaw status | head -5
else
    echo -e "${RED}✗ 网关未运行${NC}"
    echo "   启动命令：openclaw gateway start"
fi
echo ""

# 2. 检查配置
echo -e "${YELLOW}[2/6] 配置文件${NC}"
CONFIG_FILE="$HOME/.openclaw/openclaw.json"
if [ -f "$CONFIG_FILE" ]; then
    echo -e "${GREEN}✓ 配置文件存在${NC}"
    echo "   路径：$CONFIG_FILE"
    
    # 检查 agent 数量
    AGENT_COUNT=$(cat "$CONFIG_FILE" | grep -c '"id": "m')
    echo "   Agent 数量：$AGENT_COUNT"
else
    echo -e "${RED}✗ 配置文件不存在${NC}"
fi
echo ""

# 3. 检查语音服务
echo -e "${YELLOW}[3/6] 语音服务${NC}"
if curl -s http://localhost:8080/health | grep -q "ok"; then
    echo -e "${GREEN}✓ 语音服务运行中${NC}"
    curl -s http://localhost:80880/health
else
    echo -e "${RED}✗ 语音服务未运行${NC}"
    echo "   启动命令：bash ~/.openclaw/workspace/skills/swarm-control-feishu/files/start-voice-service.sh"
fi
echo ""

# 4. 检查 sessions
echo -e "${YELLOW}[4/6] Sessions${NC}"
SESSION_COUNT=$(openclaw sessions list 2>/dev/null | grep -c "agent:" || echo "0")
echo "活跃 sessions：$SESSION_COUNT"
if [ "$SESSION_COUNT" -gt 0 ]; then
    echo ""
    echo "Sessions 列表："
    openclaw sessions list 2>/dev/null | head -10
fi
echo ""

# 5. 检查工作空间
echo -e "${YELLOW}[5/6] 工作空间${NC}"
WORKSPACES=("workspace" "workspace-xg" "workspace-xc" "workspace-xd")
for ws in "${WORKSPACES[@]}"; do
    WS_PATH="$HOME/.openclaw/$ws"
    if [ -d "$WS_PATH" ]; then
        echo -e "${GREEN}✓ $ws${NC} - $WS_PATH"
        
        # 检查 AGENTS.md
        if [ -f "$WS_PATH/AGENTS.md" ]; then
            echo -e "  ├─ AGENTS.md"
        fi
        
        # 检查 IDENTITY.md
        if [ -f "$WS_PATH/IDENTITY.md" ]; then
            echo -e "  ├─ IDENTITY.md"
        fi
    else
        echo -e "${RED}✗ $ws${NC} - 不存在"
    fi
done
echo ""

# 6. 检查 sudo 配置
echo -e "${YELLOW}[6/6] 系统权限${NC}"
if sudo -n whoami 2>/dev/null; then
    echo -e "${GREEN}✓ sudo 免密已配置${NC}"
else
    echo -e "${YELLOW}⚠ sudo 需要密码${NC}"
    echo "   配置命令：sudo bash -c 'echo \"lehua ALL=(ALL) NOPASSWD: ALL\" > /etc/sudoers.d/lehua'"
fi
echo ""

# 完成
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}检查完成${NC}"
echo -e "${BLUE}========================================${NC}"
