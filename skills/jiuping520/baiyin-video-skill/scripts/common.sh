#!/usr/bin/env bash
# 公共函数：缓存路径、环境变量校验、curl 认证头

# 缓存文件路径（可通过 BAIYIN_CACHE_FILE 覆盖）
get_cache_file() {
  if [[ -n "${BAIYIN_CACHE_FILE:-}" ]]; then
    echo "$BAIYIN_CACHE_FILE"
  elif [[ "$(uname)" == "MINGW"* ]] || [[ "$(uname)" == "CYGWIN"* ]]; then
    echo "${TEMP:-${TMP:-C:/Temp}}/baiyin_config.json"
  else
    echo "/tmp/baiyin_config.json"
  fi
}

# 校验必需的环境变量
check_env() {
  export BAIYIN_OPEN_URL="${BAIYIN_OPEN_URL:-https://ai.hikoon.com}"
  if [[ -z "${BAIYIN_OPEN_KEY:-}" ]]; then
    echo "ERROR: 环境变量 BAIYIN_OPEN_KEY 未设置" >&2
    exit 1
  fi
}

# 带认证的 curl（附加超时）
curl_auth() {
  curl -s --connect-timeout 10 --max-time 30 \
    -H "Authorization: Bearer ${BAIYIN_OPEN_KEY}" \
    -H "Content-Type: application/json" \
    "$@"
}
