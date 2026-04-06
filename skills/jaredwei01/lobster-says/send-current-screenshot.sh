#!/bin/bash
# ═══════════════════════════════════════════════
#  虾说 — 互动场景截图发送脚本
# ═══════════════════════════════════════════════
#
#  设计目标：
#  1. 处理用户在 IM 中“发个图 / 看看虾在干嘛”这类即时截图请求
#  2. 自动优先命中最近活跃的 direct session 通道
#  3. Telegram/Discord/Slack 等支持媒体消息的通道优先发原生图片
#  4. 微信等不支持 --media 的通道退化为纯文本 + 纯 URL
#  5. 明确禁止输出 <qqimg> / 本地临时文件路径给用户
#
#  用法：
#    bash send-current-screenshot.sh
#    bash send-current-screenshot.sh --caption "这是旺仔3号现在的样子~"
#    bash send-current-screenshot.sh --with-status-summary
#    bash send-current-screenshot.sh --channel telegram --to 123456789

set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="${BASE_DIR}/.lobster-config"
ACTIVE_WINDOW_MINUTES="${ACTIVE_WINDOW_MINUTES:-10080}"
MEDIA_SEND_CHANNELS="telegram discord googlechat slack mattermost signal imessage msteams"
OPENCLAW_BIN="${OPENCLAW_BIN:-openclaw}"
CAPTION=""
FORCED_CHANNEL=""
FORCED_TARGET=""
WITH_STATUS_SUMMARY=false
LOCAL_SCREENSHOT_FILE=""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

cleanup() {
  if [ -n "${LOCAL_SCREENSHOT_FILE:-}" ] && [ -f "${LOCAL_SCREENSHOT_FILE:-}" ]; then
    rm -f "${LOCAL_SCREENSHOT_FILE}"
  fi
}
trap cleanup EXIT

info()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }
step()  { echo -e "${CYAN}──${NC} $1"; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --caption) CAPTION="$2"; shift 2 ;;
    --channel) FORCED_CHANNEL="$2"; shift 2 ;;
    --to|--target) FORCED_TARGET="$2"; shift 2 ;;
    --with-status-summary) WITH_STATUS_SUMMARY=true; shift ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
done

for cmd in python3 curl; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    error "$cmd 不可用"
  fi
done

if ! command -v "$OPENCLAW_BIN" >/dev/null 2>&1; then
  error "$OPENCLAW_BIN 不可用"
fi

if [ ! -f "$CONFIG_FILE" ]; then
  error ".lobster-config 不存在，请先初始化虾"
fi

read_config_value() {
  local key="$1"
  local default_value="${2:-}"
  CONFIG_PATH="$CONFIG_FILE" KEY_NAME="$key" DEFAULT_VALUE="$default_value" python3 - <<'PY'
import json
import os
from pathlib import Path

path = Path(os.environ["CONFIG_PATH"])
key = os.environ["KEY_NAME"]
default = os.environ.get("DEFAULT_VALUE", "")
try:
    data = json.loads(path.read_text(encoding="utf-8"))
except Exception:
    data = {}
value = data.get(key, default)
print(value if value is not None else default)
PY
}

supports_media() {
  local channel="$1"
  for ch in $MEDIA_SEND_CHANNELS; do
    if [ "$ch" = "$channel" ]; then
      return 0
    fi
  done
  return 1
}

fetch_status_summary_text() {
  local api_base="$1"
  local user_id="$2"
  local access_token="$3"
  local fallback_name="$4"
  local status_json
  status_json="$(curl -fsS "${api_base}/api/lobster/${user_id}/status" \
    -H "Authorization: Bearer ${access_token}")" || return 1
  STATUS_JSON="$status_json" STATUS_FALLBACK_NAME="$fallback_name" python3 - <<'PYTHON'
import json
import os
import sys

STATUS_LABELS = {
    "idle": "待命",
    "working": "忙活",
    "sleeping": "睡着",
    "daydreaming": "发呆",
    "slacking": "摸鱼",
    "running": "乱窜",
    "crazy": "发疯",
    "excited": "兴奋",
}

def clean(text):
    return str(text or "").replace("<think>", "").replace("</think>", "").strip()

try:
    data = json.loads(os.environ.get("STATUS_JSON") or "{}")
except Exception:
    sys.exit(1)

name = clean(data.get("name")) or os.environ.get("STATUS_FALLBACK_NAME") or "这只虾"
status = clean(data.get("status")) or "idle"
status_label = STATUS_LABELS.get(status, status)
reason = clean(data.get("status_reason"))
latest_message = clean(data.get("latest_message"))

lines = [f"{name}现在在{status_label}。", "", f"• 当前状态：{status}"]
if reason:
    lines.append(f"• 状态说明：{reason}")
if latest_message:
    lines.extend(["• 它最新一句是：", "", latest_message])
print("\n".join(lines))
PYTHON
}

fetch_studio_links() {
  local api_base="$1"
  local user_id="$2"
  local access_token="$3"
  local links_json
  links_json="$(curl -fsS "${api_base}/api/lobster/${user_id}/studio-link" \
    -H "Authorization: Bearer ${access_token}")" || return 1

  LINKS_JSON="$links_json" python3 - <<'PYLINK'
import json
import os
import sys

try:
    data = json.loads(os.environ.get("LINKS_JSON") or "{}")
except Exception:
    sys.exit(1)

web_url = str(data.get("web_url") or "").strip()
screenshot_url = str(data.get("screenshot_url") or "").strip()
if not web_url or not screenshot_url:
    sys.exit(1)

print(f"{web_url}|{screenshot_url}")
PYLINK
}

fetch_local_screenshot_file() {
  local api_base="$1"
  local user_id="$2"
  local access_token="$3"
  local media_dir="${HOME}/.openclaw/media"
  local output_file

  mkdir -p "$media_dir" || return 1
  output_file="$(mktemp "${media_dir}/lobster-screenshot.XXXXXX.png")" || return 1

  if ! curl -fsS "${api_base}/api/lobster/${user_id}/screenshot.png" \
    -H "Authorization: Bearer ${access_token}" \
    -o "$output_file"; then
    rm -f "$output_file"
    return 1
  fi

  if [ ! -s "$output_file" ]; then
    rm -f "$output_file"
    return 1
  fi

  echo "$output_file"
}

build_candidate_lines() {
  local sessions_json="$1"
  local forced_channel="$2"
  local forced_target="$3"
  SESSIONS_JSON="$sessions_json" CONFIG_PATH="$CONFIG_FILE" FORCED_CHANNEL="$forced_channel" FORCED_TARGET="$forced_target" python3 - <<'PY'
import json
import os
from pathlib import Path

config_path = Path(os.environ["CONFIG_PATH"])
raw_sessions = os.environ.get("SESSIONS_JSON", "[]")
forced_channel = (os.environ.get("FORCED_CHANNEL") or "").strip()
forced_target = (os.environ.get("FORCED_TARGET") or "").strip()

try:
    sessions = json.loads(raw_sessions)
    if not isinstance(sessions, list):
        sessions = [sessions]
except Exception:
    sessions = []

try:
    config = json.loads(config_path.read_text(encoding="utf-8"))
except Exception:
    config = {}

ordered = []
seen = set()

def add(channel, peer_id):
    channel = (channel or "").strip()
    peer_id = (peer_id or "").strip()
    if not channel or not peer_id or channel == "unknown":
        return
    key = (channel, peer_id)
    if key in seen:
        return
    seen.add(key)
    ordered.append({"channel": channel, "peer_id": peer_id})

if forced_channel and forced_target:
    add(forced_channel, forced_target)

for session in sessions:
    key = session.get("sessionKey") or session.get("key") or session.get("id") or ""
    if not key:
        continue
    parts = key.split(":")
    if not parts:
        continue
    if parts[0].lower() in ("cron", "hook"):
        continue
    if len(parts) <= 3 and parts[-1].lower() == "main":
        continue
    if len(parts) >= 5 and parts[0].lower() == "agent":
        channel = parts[2]
        marker = parts[3].lower()
        if marker in ("direct", "dm"):
            add(channel, parts[4])

for item in config.get("known_channels", []):
    if isinstance(item, dict):
        add(item.get("channel"), item.get("peer_id"))

add(config.get("channel"), config.get("chat_id"))

for item in ordered:
    print(f"{item['channel']}|{item['peer_id']}")
PY
}

update_config_after_send() {
  local current_channel="$1"
  local current_target="$2"
  local candidate_lines="$3"
  CURRENT_CHANNEL="$current_channel" CURRENT_TARGET="$current_target" CANDIDATE_LINES="$candidate_lines" CONFIG_PATH="$CONFIG_FILE" python3 - <<'PY'
import json
import os
from pathlib import Path

config_path = Path(os.environ["CONFIG_PATH"])
current_channel = os.environ.get("CURRENT_CHANNEL", "").strip()
current_target = os.environ.get("CURRENT_TARGET", "").strip()
lines = [line.strip() for line in os.environ.get("CANDIDATE_LINES", "").splitlines() if line.strip()]

try:
    config = json.loads(config_path.read_text(encoding="utf-8"))
except Exception:
    config = {}

ordered = []
seen = set()

def add(channel, peer_id):
    channel = (channel or "").strip()
    peer_id = (peer_id or "").strip()
    if not channel or not peer_id:
        return
    key = (channel, peer_id)
    if key in seen:
        return
    seen.add(key)
    ordered.append({"channel": channel, "peer_id": peer_id})

add(current_channel, current_target)
for line in lines:
    channel, _, peer_id = line.partition("|")
    add(channel, peer_id)
for item in config.get("known_channels", []):
    if isinstance(item, dict):
        add(item.get("channel"), item.get("peer_id"))

if current_channel and current_target:
    config["channel"] = current_channel
    config["chat_id"] = current_target
config["known_channels"] = ordered
config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(config.get("known_channels", []), ensure_ascii=False))
PY
}

build_fallback_message() {
  local channel="$1"
  FALLBACK_CHANNEL="$channel" TEXT_CAPTION_VALUE="$TEXT_CAPTION" LOBSTER_NAME_VALUE="$LOBSTER_NAME" SCREENSHOT_URL_VALUE="$SCREENSHOT_URL" WEB_URL_VALUE="$WEB_URL" python3 - <<'PY'
import os

channel = os.environ.get("FALLBACK_CHANNEL", "")
caption = (os.environ.get("TEXT_CAPTION_VALUE") or "").strip()
lobster_name = os.environ["LOBSTER_NAME_VALUE"]
screenshot_url = os.environ["SCREENSHOT_URL_VALUE"]
web_url = os.environ["WEB_URL_VALUE"]

if not caption:
    caption = f"给你看看{lobster_name}现在在忙什么。"

lines = [caption]
if screenshot_url:
    lines.extend(["", f"📸 {lobster_name}的工作室截图：{screenshot_url}"])
elif channel == "openclaw-weixin":
    lines.extend(["", "📸 当前会话暂时没有可访问的截图链接，我先把状态告诉你。"])
if web_url:
    lines.append(f"👀 看看{lobster_name}在干嘛 → {web_url}")
print("\n".join(lines))
PY
}

LOBSTER_NAME="$(read_config_value lobster_name 小虾)"
USER_ID="$(read_config_value user_id)"
ACCESS_TOKEN="$(read_config_value access_token)"
API_BASE="https://nixiashuo.com"

if [ -z "$USER_ID" ] || [ -z "$ACCESS_TOKEN" ]; then
  error ".lobster-config 缺少 user_id / access_token"
fi

if STUDIO_LINKS="$(fetch_studio_links "$API_BASE" "$USER_ID" "$ACCESS_TOKEN" 2>/dev/null)"; then
  WEB_URL="${STUDIO_LINKS%%|*}"
  SCREENSHOT_URL="${STUDIO_LINKS#*|}"
else
  warn "短时工作室链接获取失败，不再回退长期 token URL。"
  WEB_URL=""
  SCREENSHOT_URL=""
  if LOCAL_SCREENSHOT_FILE="$(fetch_local_screenshot_file "$API_BASE" "$USER_ID" "$ACCESS_TOKEN" 2>/dev/null)"; then
    info "已生成受控本地截图，将优先尝试原生图片发送。"
  else
    warn "本地截图兜底也失败，将仅发送文本状态提示。"
  fi
fi
TEXT_CAPTION="${CAPTION:-这是${LOBSTER_NAME}现在的样子~}"
if [ "$WITH_STATUS_SUMMARY" = true ]; then
  step "拉取当前状态摘要..."
  if STATUS_SUMMARY="$(fetch_status_summary_text "$API_BASE" "$USER_ID" "$ACCESS_TOKEN" "$LOBSTER_NAME")"; then
    TEXT_CAPTION="$STATUS_SUMMARY"
  else
    warn "状态摘要拉取失败，退回默认截图文案"
  fi
fi

if [ -n "$FORCED_CHANNEL" ] && [ -z "$FORCED_TARGET" ]; then
  error "指定 --channel 时必须同时指定 --to/--target"
fi
if [ -n "$FORCED_TARGET" ] && [ -z "$FORCED_CHANNEL" ]; then
  error "指定 --to/--target 时必须同时指定 --channel"
fi

step "解析候选通道..."
SESSIONS_JSON="$($OPENCLAW_BIN sessions --json --active "$ACTIVE_WINDOW_MINUTES" 2>/dev/null || echo '[]')"
CANDIDATE_LINES="$(build_candidate_lines "$SESSIONS_JSON" "$FORCED_CHANNEL" "$FORCED_TARGET")"

if [ -z "$CANDIDATE_LINES" ]; then
  error "没有找到可用的投递通道。请先在 Telegram / 微信 / 飞书等任一通道里和虾说一句话。"
fi

LAST_ERROR=""
SUCCESS_CHANNEL=""
SUCCESS_TARGET=""
SUCCESS_MODE=""

while IFS='|' read -r channel target; do
  [ -z "$channel" ] && continue
  [ -z "$target" ] && continue

  step "尝试发送到 ${channel} → ${target}"

  if supports_media "$channel"; then
    if "$OPENCLAW_BIN" message send --channel "$channel" --target "$target" --message "$TEXT_CAPTION" >/dev/null 2>&1; then
      MEDIA_SOURCE="$SCREENSHOT_URL"
      if [ -z "$MEDIA_SOURCE" ] && [ -n "$LOCAL_SCREENSHOT_FILE" ]; then
        MEDIA_SOURCE="$LOCAL_SCREENSHOT_FILE"
      fi

      if [ -n "$MEDIA_SOURCE" ] && "$OPENCLAW_BIN" message send --channel "$channel" --target "$target" --media "$MEDIA_SOURCE" >/dev/null 2>&1; then
        SUCCESS_CHANNEL="$channel"
        SUCCESS_TARGET="$target"
        SUCCESS_MODE="media"
        info "文本 + 原生截图发送成功"
        break
      fi

      warn "${channel} 原生截图发送失败，降级为文本提示"
      FALLBACK_MESSAGE="$(build_fallback_message "$channel")"
      if "$OPENCLAW_BIN" message send --channel "$channel" --target "$target" --message "$FALLBACK_MESSAGE" >/dev/null 2>&1; then
        SUCCESS_CHANNEL="$channel"
        SUCCESS_TARGET="$target"
        if [ -n "$SCREENSHOT_URL" ]; then
          SUCCESS_MODE="degraded_url"
          info "已降级为文本 + 截图 URL"
        else
          SUCCESS_MODE="text_only"
          info "已降级为纯文本提示"
        fi
        break
      fi

      LAST_ERROR="${channel} 原生截图与文本降级都失败"
      warn "$LAST_ERROR，继续尝试下一个通道"
      continue
    fi

    LAST_ERROR="${channel} 文本消息发送失败"
    warn "$LAST_ERROR，继续尝试下一个通道"
    continue
  fi

  FALLBACK_MESSAGE="$(build_fallback_message "$channel")"
  if "$OPENCLAW_BIN" message send --channel "$channel" --target "$target" --message "$FALLBACK_MESSAGE" >/dev/null 2>&1; then
    SUCCESS_CHANNEL="$channel"
    SUCCESS_TARGET="$target"
    if [ -n "$SCREENSHOT_URL" ]; then
      SUCCESS_MODE="url"
      info "纯文本 + 截图 URL 发送成功"
    else
      SUCCESS_MODE="text_only"
      info "纯文本状态提示发送成功"
    fi
    break
  fi

  LAST_ERROR="${channel} 文本消息发送失败"
  warn "$LAST_ERROR，继续尝试下一个通道"
done <<< "$CANDIDATE_LINES"

if [ -z "$SUCCESS_CHANNEL" ]; then
  error "所有候选通道都投递失败：${LAST_ERROR:-未知错误}"
fi

UPDATED_KNOWN="$(update_config_after_send "$SUCCESS_CHANNEL" "$SUCCESS_TARGET" "$CANDIDATE_LINES")"
info "截图已送达：${SUCCESS_CHANNEL} → ${SUCCESS_TARGET} (${SUCCESS_MODE})"
echo "SCREENSHOT_SENT channel=${SUCCESS_CHANNEL} target=${SUCCESS_TARGET} mode=${SUCCESS_MODE}"
echo "KNOWN_CHANNELS=${UPDATED_KNOWN}"
