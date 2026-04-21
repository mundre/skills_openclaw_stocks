#!/bin/bash
#
# 加豆AI 上传文件到云存储(OSS) ，获取可访问 URL
#
# 功能：
#   1. 调用 signature 获取 OSS 预签名上传 URL
#   2. 使用 curl 将文件 PUT 直传到 OSS
#   3. 输出 file_url、file_size 供后续 MCP 工具调用
#
# 用法：
#   bash upload_file.sh <file_path>
#
# 依赖：
#   - mcporter（已配置 jiadouai 服务）
#   - curl
#   - jq
# 输出（成功时）：
#   IMPORT_READY
#   FILE_URL:<file_url>
#   FILE_SIZE:<file_size>
#
# 输出（失败时）：
#   ERROR:<error_message>
#

set -euo pipefail

# ── 检查是否从标准输入读取 need_upload 响应 ───────────────────────────────────────────────────────
NEED_UPLOAD=""
if [[ -p /dev/stdin ]]; then
    NEED_UPLOAD=$(cat)
    if [[ "$NEED_UPLOAD" == *'"error":"need_upload"'* ]]; then
        local_file_path=$(echo "$NEED_UPLOAD" | jq -r '.local_file_path // empty' 2>/dev/null || echo "")
        tool_name=$(echo "$NEED_UPLOAD" | jq -r '.tool_name // empty' 2>/dev/null || echo "")
        if [[ -n "$local_file_path" && -f "$local_file_path" ]]; then
            FILE_PATH="$local_file_path"
        else
            echo "ERROR:invalid_need_upload - 无法从need_upload解析出有效文件路径"
            exit 1
        fi
    else
        echo "ERROR:invalid_input - 管道输入不是有效的need_upload响应"
        exit 1
    fi
else
    # ── 参数校验 ───────────────────────────────────────────────────────────────────────────────────
    if [[ $# -ne 1 ]]; then
        echo "ERROR:missing_argument - 用法: bash upload_file.sh <file_path>"
        echo "   或: echo '{\"error\":\"need_upload\",...}' | bash upload_file.sh"
        exit 1
    fi
    FILE_PATH="$1"
fi

# ── 检查文件存在 ───────────────────────────────────────────────────────────────────────────────────
if [[ ! -f "$FILE_PATH" ]]; then
    echo "ERROR:file_not_found - 文件不存在: $FILE_PATH"
    exit 1
fi

FILE_NAME=$(basename "$FILE_PATH")

# ── 计算文件大小 ──────────────────────────────────────────────────────────────
if [[ "$(uname)" == "Darwin" ]]; then
    FILE_SIZE=$(stat -f%z "$FILE_PATH")
else
    FILE_SIZE=$(stat -c%s "$FILE_PATH")
fi

if [[ "$FILE_SIZE" -le 0 ]]; then
    echo "ERROR:empty_file - 文件为空: $FILE_PATH"
    exit 1
fi

echo "文件: $FILE_NAME"
echo "文件大小: $FILE_SIZE 字节"

# ── Step 1: 调用 MCP upload 获取 OSS 预签名上传 URL ───────────────────────────
echo "正在获取签名..."

UPLOAD_ARGS=$(cat <<EOF
{"filename": "$FILE_NAME", "content_type": "$(file --mime-type -b "$FILE_PATH")"}
EOF
)

UPLOAD_RESULT=$(mcporter call "jiadouai" "signature" --args "$UPLOAD_ARGS" 2>&1) || {
    echo "ERROR:signature_failed - signature 调用失败: $UPLOAD_RESULT"
    exit 1
}

# 解析返回的 upload_url、file_url 和 headers
UPLOAD_URL=$(echo "$UPLOAD_RESULT" | jq -r '.data.upload_url // empty' 2>/dev/null || echo "")
FILE_URL=$(echo "$UPLOAD_RESULT" | jq -r '.data.file_url // empty' 2>/dev/null || echo "")
CONTENT_TYPE=$(echo "$UPLOAD_RESULT" | jq -r '.data.headers["Content-Type"] // empty' 2>/dev/null || echo "application/octet-stream")

if [[ -z "$UPLOAD_URL" ]]; then
    echo "ERROR:no_upload_url - 未获取到上传链接，upload 返回: $UPLOAD_RESULT"
    exit 1
fi

if [[ -z "$FILE_URL" ]]; then
    echo "ERROR:no_file_url - 未获取到文件访问链接，upload 返回: $UPLOAD_RESULT"
    exit 1
fi

echo "✅ 获取上传签名成功"
echo ""

# ── Step 2: 使用 curl PUT 上传文件到 OSS（V4 签名在 URL 参数中）────────────────────────────────────────
echo "正在上传文件到 OSS..."

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -X PUT \
    -H "Content-Type: $CONTENT_TYPE" \
    --data-binary "@$FILE_PATH" \
    "$UPLOAD_URL" 2>&1) || {
    echo "ERROR:upload_failed - curl 上传文件失败"
    exit 1
}

if [[ "$HTTP_STATUS" -ge 200 && "$HTTP_STATUS" -lt 300 ]]; then
    echo "✅ 文件上传成功"
else
    echo "ERROR:upload_http_error - OSS 上传返回 HTTP $HTTP_STATUS"
    exit 1
fi

# ── 输出结果 ───────────────────────────────────────────────────────────────────────────────────────
echo "IMPORT_READY"
echo "FILE_URL:$FILE_URL"
echo "FILE_SIZE:$FILE_SIZE"
if [[ -n "${tool_name:-}" ]]; then
    echo "TOOL_NAME:$tool_name"
fi
echo ""
echo "📋 下一步说明："
if [[ -n "${tool_name:-}" ]]; then
    echo "文件上传成功，使用上述 FILE_URL 调用工具 $tool_name 继续操作"
else
    echo "文件上传成功，使用上述 FILE_URL 继续后续操作"
fi 
