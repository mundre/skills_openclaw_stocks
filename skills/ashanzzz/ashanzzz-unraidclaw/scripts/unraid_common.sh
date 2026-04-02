#!/usr/bin/env bash
# unraid_common.sh - UnraidCLaW API 公共函数库
# 用法: source unraid_common.sh

# 读取凭据（支持 env 文件）
load_env() {
    local env_file="${1:-$(dirname "$0")/../../.env}"
    if [ -f "$env_file" ]; then
        set -a
        source "$env_file"
        set +a
    fi
}

# API Key（优先使用环境变量）
get_token() {
    echo "${UNRAIDCLAW_TOKEN:-}"
}

# API Host
get_host() {
    echo "${UNRAID_HOST:-https://192.168.8.11:9876}"
}

# 核心 API 调用函数
# 用法: api_get "/api/docker/containers"
api_get() {
    local endpoint="$1"
    local host host token

    host=$(get_host)
    token=$(get_token)

    curl -s -k \
        -H "x-api-key: ${token}" \
        "${host}${endpoint}"
}

# POST 调用（无 Body）
api_post() {
    local endpoint="$1"
    local host token

    host=$(get_host)
    token=$(get_token)

    curl -s -k -X POST \
        -H "x-api-key: ${token}" \
        -H "Content-Type: application/json" \
        "${host}${endpoint}"
}

# POST 调用（带 Body）
api_post_body() {
    local endpoint="$1"
    local body="$2"
    local host token

    host=$(get_host)
    token=$(get_token)

    curl -s -k -X POST \
        -H "x-api-key: ${token}" \
        -H "Content-Type: application/json" \
        -d "${body}" \
        "${host}${endpoint}"
}

# DELETE 调用
api_delete() {
    local endpoint="$1"
    local host token

    host=$(get_host)
    token=$(get_token)

    curl -s -k -X DELETE \
        -H "x-api-key: ${token}" \
        "${host}${endpoint}"
}

# 健康检查
api_health() {
    api_get "/api/health"
}

# 格式化输出 JSON（如果有 python3）
format_json() {
    if command -v python3 &>/dev/null; then
        python3 -m json.tool 2>/dev/null
    elif command -v jq &>/dev/null; then
        jq . 2>/dev/null
    else
        cat
    fi
}

# 检查上一个命令是否成功
check_ok() {
    local response="$1"
    echo "$response" | grep -q '"ok": true' && return 0 || return 1
}

# 打印错误
print_error() {
    echo "$1" | grep -o '"message": "[^"]*"' | sed 's/"message": "//;s/"//g' >&2
}

# 打印使用说明
usage() {
    echo "UnraidCLaW API 公共函数库"
    echo "提供函数: api_get, api_post, api_post_body, api_delete, api_health, load_env"
    echo "环境变量: UNRAIDCLAW_TOKEN, UNRAID_HOST"
}
