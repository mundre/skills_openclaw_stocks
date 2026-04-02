#!/usr/bin/env bash
# opencode_install.sh - OpenCode Docker 一键安装（通过 UnraidCLaW API）
# 用法: bash opencode_install.sh [--reinstall] [--uninstall]
#
# 功能:
#   1. 检查容器是否已存在，存在则跳过（加 --reinstall 则先删除再创建）
#   2. 通过 UnraidCLaW API 创建容器
#   3. 配置代理（国内访问 ghcr.io 需要）
#   4. 自动设置 ENABLE_WEB_UI=true，开启 Web UI
#   5. 输出 Web UI 访问地址
#
# 前置: 设置 UNRAIDCLAW_TOKEN 和 UNRAID_HOST 环境变量
#   export UNRAIDCLAW_TOKEN="your-token"
#   export UNRAID_HOST="https://192.168.8.11:9876"
#
# 参考: https://github.com/anomalyco/opencode

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/unraid_common.sh"

# ========== 配置区 ==========
CONTAINER_NAME="opencode"
IMAGE="ghcr.io/anomalyco/opencode:latest"
PORTS='["4096:4096","4097:4097"]'
PROXY_HOST="192.168.8.30"
PROXY_PORT="7893"

# 代理环境变量（国内服务器需要）
ENV_PROXY='["HTTP_PROXY=http://'"${PROXY_HOST}:${PROXY_PORT}"'","HTTPS_PROXY=http://'"${PROXY_HOST}:${PROXY_PORT}"'","NO_PROXY=localhost,127.0.0.1,192.168.0.0/16","ENABLE_WEB_UI=true","PUID=99","PGID=100","TZ=Asia/Shanghai"]'

# 数据持久化
VOLUMES='["/mnt/user/appdata/'"${CONTAINER_NAME}"'/config:/home/opencode/.config/opencode","/mnt/user/appdata/'"${CONTAINER_NAME}"'/data:/home/opencode/.local/share/opencode","/mnt/user/appdata/'"${CONTAINER_NAME}"'/state:/home/opencode/.local/state/opencode","/mnt/user/appdata/'"${CONTAINER_NAME}"'/cache:/home/opencode/.cache/opencode","/mnt/user/appdata/'"${CONTAINER_NAME}"'/projects:/projects"]'

ICON='"icon":"https://opencode.ai/favicon.ico"'
WEBUI='"webui":"http://[IP]:4097/"'

# ========== 函数 ==========

usage() {
    echo "OpenCode Docker 一键安装（通过 UnraidCLaW API）"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --reinstall    先删除旧容器再重新创建"
    echo "  --uninstall    仅删除容器（不创建新容器）"
    echo "  --check        仅检查容器状态"
    echo "  --logs         查看容器日志（最后 30 行）"
    echo "  --help         显示本帮助"
    echo ""
    echo "环境变量:"
    echo "  UNRAIDCLAW_TOKEN   UnraidCLaW API Key（必填）"
    echo "  UNRAID_HOST        Unraid 地址（默认: https://192.168.8.11:9876）"
    echo ""
    echo "示例:"
    echo "  UNRAIDCLAW_TOKEN=xxx bash opencode_install.sh"
    echo "  UNRAIDCLAW_TOKEN=xxx bash opencode_install.sh --reinstall"
}

# 检查容器是否存在
container_exists() {
    local name="$1"
    local response
    response=$(api_get "/api/docker/containers")
    echo "$response" | grep -q "\"Name\":\"${name}\"" 2>/dev/null
}

# 删除容器
remove_container() {
    local name="$1"
    echo "🗑️  删除容器: $name"
    local response
    response=$(api_delete "/api/docker/containers/${name}")
    if echo "$response" | grep -q '"ok": true'; then
        echo "✅ 容器已删除"
    else
        echo "⚠️  删除响应: $response"
    fi
}

# 创建容器
create_container() {
    local name="$1"
    local image="$2"
    local ports="$3"
    local env="$4"
    local volumes="$5"

    # 构建 JSON body（避免复杂引号问题）
    local body
    body=$(python3 - <<'PYTHON'
import json, sys
opts = {
    "image": sys.argv[1],
    "name": sys.argv[2],
    "ports": json.loads(sys.argv[3]),
    "env": json.loads(sys.argv[4]),
    "volumes": json.loads(sys.argv[5]),
    "restart": "unless-stopped",
    "network": "bridge",
    "icon": "https://opencode.ai/favicon.ico",
    "webui": "http://[IP]:4097/"
}
print(json.dumps(opts))
PYTHON
    "${image}" "${name}" "${ports}" "${env}" "${volumes}")

    echo "📦 正在创建容器: $name"
    echo "   镜像: $image"
    echo "   端口: $ports"
    echo "   代理: ${PROXY_HOST}:${PROXY_PORT}"
    echo "   数据: /mnt/user/appdata/${CONTAINER_NAME}/"

    local response
    response=$(api_post_body "/api/docker/containers" "$body")

    if echo "$response" | grep -q '"ok": true'; then
        echo "✅ 容器创建成功！"
        return 0
    else
        echo "❌ 容器创建失败"
        print_error "$response"
        return 1
    fi
}

# 检查容器状态
check_status() {
    local name="$1"
    local response
    response=$(api_get "/api/docker/containers")
    if echo "$response" | grep -q "\"Name\":\"${name}\""; then
        local status
        status=$(echo "$response" | grep -o "\"Status\":\"[^\"]*\"" | grep "$name" | grep -o 'Status":"[^"]*' | cut -d'"' -f3)
        echo "✅ 容器 '$name' 存在，状态: $status"
        return 0
    else
        echo "⚠️  容器 '$name' 不存在"
        return 1
    fi
}

# 查看日志
show_logs() {
    local name="$1"
    local response
    response=$(api_get "/api/docker/containers/${name}/logs?stdout=1&stderr=1&tail=30")
    echo "$response"
}

# ========== 主流程 ==========

REINSTALL=false
UNINSTALL_ONLY=false
CHECK_ONLY=false
SHOW_LOGS=false

while [ $# -gt 0 ]; do
    case "$1" in
        --reinstall) REINSTALL=true; shift ;;
        --uninstall) UNINSTALL_ONLY=true; shift ;;
        --check) CHECK_ONLY=true; shift ;;
        --logs) SHOW_LOGS=true; shift ;;
        --help|-h) usage; exit 0 ;;
        *) echo "未知参数: $1"; usage; exit 1 ;;
    esac
done

echo "============================================"
echo "  OpenCode Docker 安装脚本"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================"

# 检查环境变量
if [ -z "$(get_token)" ]; then
    echo "❌ 错误: UNRAIDCLAW_TOKEN 未设置"
    echo "   请先设置环境变量:"
    echo '   export UNRAIDCLAW_TOKEN="your-api-key"'
    exit 1
fi

echo "🔍 检查现有容器..."
if container_exists "$CONTAINER_NAME"; then
    if [ "$CHECK_ONLY" = "true" ]; then
        check_status "$CONTAINER_NAME"
        exit 0
    fi
    if [ "$SHOW_LOGS" = "true" ]; then
        echo "📋 容器日志:"
        show_logs "$CONTAINER_NAME"
        exit 0
    fi
    if [ "$UNINSTALL_ONLY" = "true" ]; then
        remove_container "$CONTAINER_NAME"
        exit 0
    fi
    if [ "$REINSTALL" = "true" ]; then
        echo "🔄 --reinstall: 先删除旧容器..."
        remove_container "$CONTAINER_NAME"
    else
        echo "✅ 容器 '$CONTAINER_NAME' 已存在，跳过创建（用 --reinstall 重新安装）"
        echo ""
        echo "Web UI: http://你的UnraidIP:4097/"
        echo "API端口: 4096"
        exit 0
    fi
else
    if [ "$CHECK_ONLY" = "true" ] || [ "$SHOW_LOGS" = "true" ] || [ "$UNINSTALL_ONLY" = "true" ]; then
        [ "$CHECK_ONLY" = "true" ] && echo "⚠️  容器不存在" && exit 1
        [ "$SHOW_LOGS" = "true" ] && echo "⚠️  容器不存在，无法查看日志" && exit 1
        [ "$UNINSTALL_ONLY" = "true" ] && echo "⚠️  容器不存在，无需删除" && exit 0
    fi
fi

echo ""
echo "🚀 开始创建容器..."
if create_container "$CONTAINER_NAME" "$IMAGE" "$PORTS" "$ENV_PROXY" "$VOLUMES"; then
    echo ""
    echo "============================================"
    echo "  ✅ 安装完成！"
    echo "============================================"
    echo ""
    echo "📍 访问地址:"
    echo "   Web UI:  http://你的UnraidIP:4097/"
    echo "   API:     http://你的UnraidIP:4096/"
    echo ""
    echo "📝 下一步:"
    echo "   1. 浏览器打开 http://你的UnraidIP:4097/"
    echo "   2. 首次使用需要配置 LLM Provider API Key"
    echo "   3. 在容器内连接 /connect 选择你的模型"
    echo ""
else
    echo ""
    echo "❌ 安装失败，请检查:"
    echo "   1. ghcr.io 能否在 Unraid 主机上访问（可能需要配置代理）"
    echo "   2. 端口 4096/4097 是否已被占用"
    echo "   3. UNRAIDCLAW_TOKEN 是否有 docker:create 权限"
fi
