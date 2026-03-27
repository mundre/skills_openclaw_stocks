#!/usr/bin/env bash
set -euo pipefail

# Step 1 环境检查与依赖安装（与 SKILL.md 一致）：
# - 若不存在 .env：从 templates/env.md 复制生成骨架文件（不写入任何云厂商密钥）。
# - 校验 frontmatter 中必填环境变量在 .env 中存在（grep 行级存在即可）。
# - 不执行「自动化填入密钥」；用户须在本地编辑 .env。
#
# - SCRIPT_DIR: 当前脚本所在目录（.../<SKILL_DIR>/scripts）
# - 默认产物目录：<WORKSPACE_ROOT>/output/（见各脚本 _project_root / get_project_root）
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

SKILL_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${SKILL_DIR}/.env"
ENV_TEMPLATE="${SKILL_DIR}/templates/env.md"
SCRIPT_FOLDER="${SKILL_DIR}/scripts"

echo "[1/2] 环境检查"

if [[ ! -f "${ENV_FILE}" ]]; then
  if [[ -f "${ENV_TEMPLATE}" ]]; then
    cp "${ENV_TEMPLATE}" "${ENV_FILE}"
    echo "已根据模板创建 ${ENV_FILE}（来源：${ENV_TEMPLATE}）"
    echo "请编辑 .env 并填入必需的环境变量后重新运行。"
  else
    echo "ERROR: 未找到 ${ENV_FILE}，且模板 ${ENV_TEMPLATE} 不存在，无法自动创建。"
    exit 1
  fi
fi

required_keys=(
  "VOLC_ACCESS_KEY_ID"
  "VOLC_ACCESS_KEY_SECRET"
  "VOLC_SPACE_NAME"
  "ASR_API_KEY"
  "ASR_BASE_URL"
)

missing=()
empty=()
for k in "${required_keys[@]}"; do
  # 支持 KEY=VALUE / KEY="VALUE" / KEY='VALUE'，忽略注释行
  if ! grep -Eq "^[[:space:]]*${k}[[:space:]]*=" "${ENV_FILE}"; then
    missing+=("${k}")
    continue
  fi

  raw_line="$(grep -E "^[[:space:]]*${k}[[:space:]]*=" "${ENV_FILE}" | sed -n '1p')"
  raw_value="${raw_line#*=}"
  value="$(printf '%s' "${raw_value}" | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//')"

  # 处理 KEY="" / KEY='' 这类空值写法
  if [[ "${value}" =~ ^\".*\"$ ]]; then
    value="${value:1:${#value}-2}"
  elif [[ "${value}" =~ ^\'.*\'$ ]]; then
    value="${value:1:${#value}-2}"
  fi

  if [[ -z "${value}" ]]; then
    empty+=("${k}")
  fi
done

if (( ${#missing[@]} > 0 )); then
  echo "ERROR: ${ENV_FILE} 缺少以下 key："
  for k in "${missing[@]}"; do
    echo "  - ${k}"
  done
  echo
  echo "请按需获取并补齐对应配置："
  echo "  - 视频点播密钥获取： https://console.volcengine.com/iam/keymanage"
  echo "  - 视频点播空间获取： https://console.volcengine.com/vod"
  echo "  - 豆包语音ASR密钥& BASE URL 获取： https://console.volcengine.com/speech/new/experience/asr?projectName=default"
  exit 1
fi

if (( ${#empty[@]} > 0 )); then
  echo "ERROR: ${ENV_FILE} 以下 key 的值为空："
  for k in "${empty[@]}"; do
    echo "  - ${k}"
  done
  echo
  echo "请按需获取并补齐对应配置："
  echo "  - 视频点播密钥获取： https://console.volcengine.com/iam/keymanage"
  echo "  - 视频点播空间获取： https://console.volcengine.com/vod"
  echo "  - 豆包语音ASR密钥& BASE URL 获取： https://console.volcengine.com/speech/new/experience/asr?projectName=default"
  exit 1
fi

py_bin=""
if command -v python >/dev/null 2>&1; then
  py_bin="python"
elif command -v python3 >/dev/null 2>&1; then
  py_bin="python3"
else
  echo "ERROR: 未找到 python/python3，可执行文件不存在。"
  exit 1
fi

py_ver="$("${py_bin}" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')"
py_ok="$("${py_bin}" -c 'import sys; print(int((sys.version_info.major,sys.version_info.minor) >= (3,11)))')"

echo "Python: ${py_bin} (${py_ver})"
if [[ "${py_ok}" != "1" ]]; then
  echo "ERROR: Python 版本不满足要求：需要 >=3.11"
  echo "当前版本：${py_ver}"
  exit 1
fi

echo "[CHECKPOINT] 环境检查完成"

echo
echo "[2/2] 依赖安装"

if [[ ! -d "${SCRIPT_FOLDER}" ]]; then
  echo "ERROR: 未找到目录 ${SCRIPT_FOLDER}"
  exit 1
fi

cd "${SCRIPT_FOLDER}"

# 非交互：若 .venv 已存在则直接清理重建，避免卡在 replace 提示
"${py_bin}" -m venv .venv --clear
if [[ -f ".venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
else
  echo "ERROR: 未找到 .venv/bin/activate，请检查 python -m venv 是否成功。"
  exit 1
fi

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "[CHECKPOINT] 依赖安装完成"

