#!/usr/bin/env bash
# unraid_docker.sh - Unraid Docker 容器管理
# 依赖: unraid_common.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/unraid_common.sh"

ACTION="${1:-}"
CONTAINER_NAME="${2:-}"
IMAGE="${3:-}"
PORTS="${4:-}"
ENV_VARS="${5:-}"
VOLUMES="${6:-}"
RESTART_POLICY="${7:-unless-stopped}"
NETWORK="${8:-bridge}"

# 使用示例
usage() {
    echo "用法: $0 <action> [args...]"
    echo ""
    echo "Actions:"
    echo "  list                                          列出所有容器"
    echo "  inspect <name>                                查看容器详情"
    echo "  logs <name> [tail=50]                        查看日志"
    echo "  create <name> <image> [ports] [env] [volumes] [restart] [network]  创建容器"
    echo "  start <name>                                  启动容器"
    echo "  stop <name>                                   停止容器"
    echo "  restart <name>                                重启容器"
    echo "  pause <name>                                  暂停容器"
    echo "  unpause <name>                                恢复容器"
    echo "  remove <name>                                 删除容器"
    echo "  create-full <json_file>                      从 JSON 文件创建容器"
    echo ""
    echo "环境变量: UNRAIDCLAW_TOKEN, UNRAID_HOST"
}

# 列出所有容器
do_list() {
    echo "=== Docker 容器列表 ==="
    local response
    response=$(api_get "/api/docker/containers")
    if check_ok "$response"; then
        echo "$response" | format_json
    else
        print_error "$response"
        return 1
    fi
}

# 查看容器详情
do_inspect() {
    if [ -z "$CONTAINER_NAME" ]; then
        echo "错误: 请指定容器名" >&2
        return 1
    fi
    echo "=== 容器详情: $CONTAINER_NAME ==="
    local response
    response=$(api_get "/api/docker/containers/${CONTAINER_NAME}")
    if check_ok "$response"; then
        echo "$response" | format_json
    else
        print_error "$response"
        return 1
    fi
}

# 查看日志
do_logs() {
    local name="${2:-}"
    local tail="${3:-50}"
    if [ -z "$name" ]; then
        echo "错误: 请指定容器名" >&2
        return 1
    fi
    echo "=== 日志: $name (tail=$tail) ==="
    local response
    response=$(api_get "/api/docker/containers/${name}/logs?stdout=1&stderr=1&tail=${tail}")
    if check_ok "$response"; then
        echo "$response" | format_json
    else
        # logs 可能直接返回原始文本
        echo "$response"
    fi
}

# 构建创建容器的 JSON body
build_create_body() {
    local name="$1"
    local image="$2"
    local ports="$3"
    local env_vars="$4"
    local volumes="$5"
    local restart="$6"
    local network="$7"

    local body='{"image":"'"${image}"'","name":"'"${name}"'"'

    [ -n "$ports" ] && body+=',"ports":'"$(echo "$ports" | jq -Rcs 'split(",")')"
    [ -n "$env_vars" ] && body+=',"env":'"$(echo "$env_vars" | jq -Rcs 'split(",")')"
    [ -n "$volumes" ] && body+=',"volumes":'"$(echo "$volumes" | jq -Rcs 'split(",")')"
    [ -n "$restart" ] && body+=',"restart":"'"${restart}"'"'
    [ -n "$network" ] && body+=',"network":"'"${network}"'"'

    body+='}'
    echo "$body"
}

# 创建容器
do_create() {
    local name="$2"
    local image="$3"
    local ports="${4:-}"
    local env_vars="${5:-}"
    local volumes="${6:-}"
    local restart="${7:-unless-stopped}"
    local network="${8:-bridge}"

    if [ -z "$name" ] || [ -z "$image" ]; then
        echo "错误: name 和 image 是必填参数" >&2
        return 1
    fi

    echo "=== 创建容器: $name (镜像: $image) ==="

    # 如果没有 jq，降级处理
    if ! command -v jq &>/dev/null; then
        local body='{"image":"'"${image}"'","name":"'"${name}"'","restart":"'"${restart}"'","network":"'"${network}"'"}'
        [ -n "$ports" ] && body=$(echo "$body" | sed 's/"network":"'"$network"'"/"ports":["'"${ports//,/\"\,\"}'"],"network":"'"${network}"'"/')
    else
        local body
        body=$(build_create_body "$name" "$image" "$ports" "$env_vars" "$volumes" "$restart" "$network")
    fi

    echo "Request Body: $body"
    local response
    response=$(api_post_body "/api/docker/containers" "$body")

    if echo "$response" | grep -q '"ok": true'; then
        echo "✅ 容器创建成功"
        echo "$response" | format_json
    else
        echo "❌ 容器创建失败"
        print_error "$response"
        return 1
    fi
}

# 从 JSON 文件创建容器
do_create_full() {
    local json_file="$2"
    if [ -z "$json_file" ] || [ ! -f "$json_file" ]; then
        echo "错误: 请指定有效的 JSON 文件" >&2
        return 1
    fi
    echo "=== 从文件创建容器: $json_file ==="
    local body
    body=$(cat "$json_file")
    local response
    response=$(api_post_body "/api/docker/containers" "$body")
    if echo "$response" | grep -q '"ok": true'; then
        echo "✅ 创建成功"
        echo "$response" | format_json
    else
        echo "❌ 创建失败"
        print_error "$response"
        return 1
    fi
}

# 容器操作（启动/停止/重启/暂停/恢复/删除）
do_action() {
    local act="$1"
    local name="$2"
    if [ -z "$name" ]; then
        echo "错误: 请指定容器名" >&2
        return 1
    fi
    local response
    response=$(api_post "/api/docker/containers/${name}/${act}")
    if echo "$response" | grep -q '"ok": true'; then
        echo "✅ $name $act 成功"
    else
        echo "❌ $name $act 失败"
        print_error "$response"
        return 1
    fi
}

# 主入口
case "$ACTION" in
    list)      do_list ;;
    inspect)   do_inspect ;;
    logs)      do_logs "$@" ;;
    create)    do_create "$@" ;;
    create-full) do_create_full "$@" ;;
    start)     do_action "start" "$CONTAINER_NAME" ;;
    stop)     do_action "stop" "$CONTAINER_NAME" ;;
    restart)   do_action "restart" "$CONTAINER_NAME" ;;
    pause)     do_action "pause" "$CONTAINER_NAME" ;;
    unpause)   do_action "unpause" "$CONTAINER_NAME" ;;
    remove|delete) do_action "remove" "$CONTAINER_NAME" ;;
    *)         usage ;;
esac
