#!/usr/bin/env bash
#
# @module scripts/check-upgrade.sh
# @description 检查当前安装的 yingmi-skill 是否有可用更新，仅输出检查结果与更新提示
# @requirement Skill 更新检查需要在调用 MCP 前快速判断是否存在新版本，但不强制升级
# @design 通过远端 version 文件与本地版本做比对，只做版本读取、结果提示，不执行更新动作
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

REMOTE_BRANCH="master"
REMOTE_REPO_URL="${REMOTE_REPO_URL:-https://gitee.com/yingmi-tech/yingmi-skill.git}"
REMOTE_RAW_BASE_URL="${REMOTE_RAW_BASE_URL:-https://gitee.com/yingmi-tech/yingmi-skill/raw/${REMOTE_BRANCH}}"
REMOTE_VERSION_URL="${REMOTE_VERSION_URL:-${REMOTE_RAW_BASE_URL}/version}"
LOCAL_VERSION_FILE="${SKILL_DIR}/version"

if ! remote_version_content="$(curl -fsSL "${REMOTE_VERSION_URL}")"; then
  printf '检查远端版本失败：%s\n' "${REMOTE_VERSION_URL}" >&2
  printf '请确认远端仓库分支、文件路径和网络连接是否正常。\n' >&2
  exit 1
fi

local_version_content=""

if [ -f "${LOCAL_VERSION_FILE}" ]; then
  local_version_content="$(<"${LOCAL_VERSION_FILE}")"
fi

if [ -n "${local_version_content}" ] && [ "${remote_version_content}" = "${local_version_content}" ]; then
  printf '已是最新版本：%s\n' "${local_version_content}"
  exit 0
fi

if [ -n "${local_version_content}" ]; then
  local_version_hint="当前 ${local_version_content}"
else
  local_version_hint="本地未检测到版本"
fi

printf '发现可用更新：%s，最新 %s\n' "${local_version_hint}" "${remote_version_content}"
printf '建议优先立即更新 Skill「yingmi-skill」后再继续执行；继续使用旧版本可能导致能力缺失、规则过期或后续流程判断偏差。\n'
printf '更新来源：git=%s；clawhub=已发布 yingmi-skill 最新版本。如无特殊原因，建议先完成更新再继续。\n' "${REMOTE_REPO_URL}"
