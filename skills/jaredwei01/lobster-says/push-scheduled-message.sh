#!/bin/bash
# ═══════════════════════════════════════════════
#  虾说 — 运行时定时推送脚本
# ═══════════════════════════════════════════════
#
#  设计目标：
#  1. 每次 cron 触发时动态解析最近使用的 IM 通道
#  2. 若主通道失败，自动回退到次近一次使用的通道
#  3. 将真实送达文本 / 截图模式 / 渠道结果回写服务端
#  4. Telegram 等支持原生图片的通道使用 --media，微信走纯文本 + URL
#
#  使用方式：
#    bash push-scheduled-message.sh --slot morning|discovery|evening

set -u

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="${BASE_DIR}/.lobster-config"
SLOT=""
ACTIVE_WINDOW_MINUTES="${ACTIVE_WINDOW_MINUTES:-10080}"
MEDIA_SEND_CHANNELS="telegram discord googlechat slack mattermost signal imessage msteams"
GENERATE_RESPONSE_FILE=""
PARSED_JSON_FILE=""

cleanup() {
  [ -n "$GENERATE_RESPONSE_FILE" ] && [ -f "$GENERATE_RESPONSE_FILE" ] && rm -f "$GENERATE_RESPONSE_FILE"
  [ -n "$PARSED_JSON_FILE" ] && [ -f "$PARSED_JSON_FILE" ] && rm -f "$PARSED_JSON_FILE"
  [ -n "${STICKER_IMAGE_FILE:-}" ] && [ -f "${STICKER_IMAGE_FILE:-}" ] && rm -f "$STICKER_IMAGE_FILE"
}
trap cleanup EXIT

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

_ts()   { date '+%Y-%m-%d %H:%M:%S'; }
info()  { echo -e "${GREEN}[✓]${NC} $(_ts) $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $(_ts) $1"; }
error() { echo -e "${RED}[✗]${NC} $(_ts) $1"; exit 1; }
step()  { echo -e "${CYAN}──${NC} $(_ts) $1"; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --slot) SLOT="$2"; shift 2 ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
done

if [[ ! "$SLOT" =~ ^(morning|discovery|evening|sticker|wallpaper)$ ]]; then
  error "--slot 必须是 morning / discovery / evening / sticker / wallpaper"
fi

for cmd in python3 curl openclaw; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    error "$cmd 不可用"
  fi
done

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
    data = json.loads(path.read_text(encoding='utf-8'))
    value = data.get(key, default)
    print(value if value is not None else default)
except Exception:
    print(default)
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

build_candidate_lines() {
  local sessions_json="$1"
  SESSIONS_JSON="$sessions_json" CONFIG_PATH="$CONFIG_FILE" python3 <<'PY'
import json
import os
from pathlib import Path

config_path = Path(os.environ["CONFIG_PATH"])
raw_sessions = os.environ.get("SESSIONS_JSON", "[]")

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
    elif len(parts) >= 4 and parts[0].lower() == "agent" and parts[2].lower() == "dm":
        continue

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
  CURRENT_CHANNEL="$current_channel" CURRENT_TARGET="$current_target" CANDIDATE_LINES="$candidate_lines" CONFIG_PATH="$CONFIG_FILE" python3 <<'PY'
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

report_delivery() {
  local message_id="$1"
  local status="$2"
  local channel="$3"
  local target="$4"
  local delivery_mode="$5"
  local delivered_text="$6"
  local screenshot_url="$7"
  local error_message="$8"

  REPORT_RESULT=$(REPORT_USER_ID="$USER_ID" REPORT_MESSAGE_ID="$message_id" REPORT_STATUS="$status" REPORT_CHANNEL="$channel" REPORT_TARGET="$target" REPORT_MODE="$delivery_mode" REPORT_TEXT="$delivered_text" REPORT_SCREENSHOT_URL="$screenshot_url" REPORT_ERROR="$error_message" python3 <<'PY'
import json
import os
payload = {
    "user_id": os.environ["REPORT_USER_ID"],
    "message_id": int(os.environ["REPORT_MESSAGE_ID"]),
    "status": os.environ["REPORT_STATUS"],
    "channel": os.environ.get("REPORT_CHANNEL") or None,
    "target": os.environ.get("REPORT_TARGET") or None,
    "delivery_mode": os.environ.get("REPORT_MODE") or None,
    "delivered_text": os.environ.get("REPORT_TEXT") or None,
    "delivered_screenshot_url": os.environ.get("REPORT_SCREENSHOT_URL") or None,
    "error_message": os.environ.get("REPORT_ERROR") or None,
}
print(json.dumps(payload, ensure_ascii=False))
PY
)

  curl -fsS -X POST "${API_BASE}/api/delivery/report" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -d "$REPORT_RESULT" >/dev/null 2>&1 || warn "送达结果回写失败（不影响用户已收到的消息）"
}

build_text_message() {
  local include_url="$1"
  LOBSTER_NAME_VALUE="$LOBSTER_NAME" GENERATED_CONTENT_VALUE="$GENERATED_CONTENT" WEB_URL_VALUE="$WEB_URL" SCREENSHOT_URL_VALUE="$SCREENSHOT_URL" INCLUDE_URL_VALUE="$include_url" python3 <<'PY'
import os
lobster_name = os.environ["LOBSTER_NAME_VALUE"]
content = os.environ["GENERATED_CONTENT_VALUE"]
web_url = os.environ["WEB_URL_VALUE"]
screenshot_url = os.environ["SCREENSHOT_URL_VALUE"]
include_url = os.environ.get("INCLUDE_URL_VALUE") == "true"
lines = [f"🦞 {lobster_name}说：「{content}」", ""]
if include_url and screenshot_url:
    lines.append(f"📸 {lobster_name}的工作室截图：{screenshot_url}")
lines.append(f"👀 看看{lobster_name}在干嘛 → {web_url}")
print("\n".join(lines))
PY
}

USER_ID=$(read_config_value "user_id")
ACCESS_TOKEN=$(read_config_value "access_token")
LOBSTER_NAME=$(read_config_value "lobster_name" "虾")
API_BASE="https://nixiashuo.com"
WEB_BASE="https://nixiashuo.com"

if [ -z "$USER_ID" ] || [ -z "$ACCESS_TOKEN" ]; then
  error ".lobster-config 缺少 user_id 或 access_token"
fi

step "扫描最近活跃的 IM 通道..."
SESSIONS_JSON=$(openclaw sessions --json --active "$ACTIVE_WINDOW_MINUTES" 2>/dev/null || echo "[]")
CANDIDATE_LINES=$(build_candidate_lines "$SESSIONS_JSON")

if [ -z "$CANDIDATE_LINES" ]; then
  error "没有找到可用的投递通道。请先在 Telegram / 微信 / 飞书等任一通道里和虾说一句话。"
fi

FIRST_CANDIDATE=$(echo "$CANDIDATE_LINES" | head -1)
info "本次优先尝试最近使用的通道：${FIRST_CANDIDATE%%|*}"

step "生成 ${SLOT} 消息..."
GENERATE_RESPONSE_FILE=$(mktemp "${TMPDIR:-/tmp}/lobster-generate-response.XXXXXX.json")
PARSED_JSON_FILE=$(mktemp "${TMPDIR:-/tmp}/lobster-generate-parsed.XXXXXX.json")

curl -fsS -X POST "${API_BASE}/api/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d "{\"user_id\": \"${USER_ID}\", \"message_type\": \"${SLOT}\", \"include_screenshot_base64\": false}" \
  -o "$GENERATE_RESPONSE_FILE" || error "调用 /api/generate 失败"

# 检查 discovery / sticker 是否因质量门槛或配额被跳过
SKIPPED_CHECK=$(python3 - "$GENERATE_RESPONSE_FILE" <<'PY'
import json
import sys
from pathlib import Path
try:
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if data.get("skipped"):
        print(data.get("reason", "unknown"))
    else:
        print("no")
except Exception:
    print("no")
PY
)

if [ "$SKIPPED_CHECK" != "no" ]; then
  info "📋 本次 ${SLOT} 生成被跳过: ${SKIPPED_CHECK}"
  exit 0
fi

PARSE_RESULT=$(python3 - "$GENERATE_RESPONSE_FILE" "$PARSED_JSON_FILE" <<'PY'
import json
import sys
from pathlib import Path

response_path = Path(sys.argv[1])
parsed_path = Path(sys.argv[2])

try:
    data = json.loads(response_path.read_text(encoding="utf-8"))
except Exception as exc:
    print(f"parse_error|{exc}")
    sys.exit(1)

message = data.get("message") or {}
required = {
    "message_id": message.get("id"),
    "content": message.get("raw_content") or message.get("content"),
    "web_url": data.get("web_url"),
    "screenshot_url": data.get("screenshot_url"),
}
missing = [k for k, v in required.items() if v in (None, "")]
if missing:
    print("missing|" + ",".join(missing))
    sys.exit(1)

# 额外提取 sticker 数据（如有）
required["sticker_image_base64"] = data.get("sticker_image_base64") or ""
required["sticker_theme"] = data.get("sticker_theme") or ""
required["is_sticker"] = bool(data.get("sticker_image_base64"))
required["is_wallpaper"] = message.get("message_type") == "wallpaper"
required["is_media"] = required["is_sticker"] or required["is_wallpaper"]

parsed_path.write_text(json.dumps(required, ensure_ascii=False), encoding="utf-8")
print("ok")
PY
) || error "解析 /api/generate 响应失败: ${PARSE_RESULT:-unknown}"

MESSAGE_ID=$(python3 - "$PARSED_JSON_FILE" <<'PY'
import json
import sys
from pathlib import Path
print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["message_id"])
PY
)
GENERATED_CONTENT=$(python3 - "$PARSED_JSON_FILE" <<'PY'
import json
import sys
from pathlib import Path
print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["content"])
PY
)
WEB_URL=$(python3 - "$PARSED_JSON_FILE" <<'PY'
import json
import sys
from pathlib import Path
print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["web_url"])
PY
)
SCREENSHOT_URL=$(python3 - "$PARSED_JSON_FILE" <<'PY'
import json
import sys
from pathlib import Path
print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["screenshot_url"])
PY
)

# ── 表情包/壁纸特殊处理 ──
IS_STICKER=$(python3 - "$PARSED_JSON_FILE" <<'PY'
import json
import sys
from pathlib import Path
data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print("true" if data.get("is_media") or data.get("is_sticker") else "false")
PY
)
IS_WALLPAPER=$(python3 - "$PARSED_JSON_FILE" <<'PY'
import json
import sys
from pathlib import Path
data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print("true" if data.get("is_wallpaper") else "false")
PY
)
STICKER_IMAGE_FILE=""
if [ "$IS_STICKER" = "true" ]; then
  MEDIA_TYPE_LABEL="表情包"
  [ "$IS_WALLPAPER" = "true" ] && MEDIA_TYPE_LABEL="壁纸"
  step "${MEDIA_TYPE_LABEL}类型：解码图片到临时文件..."
  # 必须放在 OpenClaw 允许的 media 目录下，否则 openclaw message send --media 会报 LocalMediaAccessError
  OPENCLAW_MEDIA_DIR="${HOME}/.openclaw/media"
  mkdir -p "$OPENCLAW_MEDIA_DIR"
  STICKER_IMAGE_FILE=$(mktemp "${OPENCLAW_MEDIA_DIR}/lobster-media.XXXXXX.png")
  python3 - "$PARSED_JSON_FILE" "$STICKER_IMAGE_FILE" <<'PY'
import base64
import json
import sys
from pathlib import Path
data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
b64 = data.get("sticker_image_base64", "")
if b64:
    Path(sys.argv[2]).write_bytes(base64.b64decode(b64))
    print("ok")
else:
    print("no_data")
    sys.exit(1)
PY
  if [ $? -ne 0 ] || [ ! -s "$STICKER_IMAGE_FILE" ]; then
    warn "${MEDIA_TYPE_LABEL}图片解码失败，降级为普通消息推送"
    IS_STICKER="false"
    STICKER_IMAGE_FILE=""
  else
    info "${MEDIA_TYPE_LABEL}图片已保存: $(du -h "$STICKER_IMAGE_FILE" | cut -f1)"
    # 图片推送的文本内容（图片会单独发送）
    STICKER_THEME=$(python3 - "$PARSED_JSON_FILE" <<'PY'
import json
import sys
from pathlib import Path
print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")).get("sticker_theme", ""))
PY
)
    if [ "$IS_WALLPAPER" = "true" ]; then
      GENERATED_CONTENT="🦞 ${LOBSTER_NAME}给你画了一张专属壁纸~"
    else
      GENERATED_CONTENT="🦞 ${LOBSTER_NAME}给你画了一张表情包~"
    fi
  fi
fi

LAST_ERROR=""
LAST_CHANNEL=""
LAST_TARGET=""
SUCCESS_CHANNEL=""
SUCCESS_TARGET=""
SUCCESS_MODE=""
DELIVERED_TEXT=""
ATTEMPT_COUNT=0

while IFS='|' read -r channel target; do
  [ -z "$channel" ] && continue
  [ -z "$target" ] && continue
  ATTEMPT_COUNT=$((ATTEMPT_COUNT + 1))

  LAST_CHANNEL="$channel"
  LAST_TARGET="$target"
  step "尝试投递到 ${channel} → ${target} (attempt #${ATTEMPT_COUNT})"

  # ── 表情包特殊投递逻辑 ──
  if [ "$IS_STICKER" = "true" ] && [ -n "$STICKER_IMAGE_FILE" ] && [ -f "$STICKER_IMAGE_FILE" ]; then
    STUDIO_ENTRY_LINE="👀 看看${LOBSTER_NAME}在干嘛 → ${WEB_URL}"
    if [ "$IS_WALLPAPER" = "true" ]; then
      STICKER_TEXT="🦞 ${LOBSTER_NAME}给你画了一张专属壁纸~
${STUDIO_ENTRY_LINE}"
      MEDIA_LABEL="壁纸"
    else
      STICKER_TEXT="🦞 ${LOBSTER_NAME}给你画了一张表情包~
${STUDIO_ENTRY_LINE}"
      MEDIA_LABEL="表情包"
    fi
    if supports_media "$channel"; then
      # 先发文字
      if openclaw message send --channel "$channel" --target "$target" --message "$STICKER_TEXT" >/dev/null 2>&1; then
        # 再发本地图片文件
        if openclaw message send --channel "$channel" --target "$target" --media "$STICKER_IMAGE_FILE" >/dev/null 2>&1; then
          SUCCESS_CHANNEL="$channel"
          SUCCESS_TARGET="$target"
          SUCCESS_MODE="media"
          DELIVERED_TEXT="$STICKER_TEXT"
          info "${MEDIA_LABEL}文本 + 图片发送成功"
          break
        fi
        warn "${channel} ${MEDIA_LABEL}图片发送失败，降级为文字提示"
      fi
    fi
    # 不支持媒体或媒体发送失败，降级为纯文字
    FALLBACK_TEXT="🦞 ${LOBSTER_NAME}画了一张${MEDIA_LABEL}给你，不过这个通道暂时看不了图~去虾的工作室看看吧 → ${WEB_URL}"
    if openclaw message send --channel "$channel" --target "$target" --message "$FALLBACK_TEXT" >/dev/null 2>&1; then
      SUCCESS_CHANNEL="$channel"
      SUCCESS_TARGET="$target"
      SUCCESS_MODE="url"
      DELIVERED_TEXT="$FALLBACK_TEXT"
      info "${MEDIA_LABEL}降级为文字提示发送成功"
      break
    fi
    LAST_ERROR="${channel} ${MEDIA_LABEL}所有模式都发送失败"
    warn "$LAST_ERROR，继续回退下一个通道"
    continue
  fi

  # ── 常规消息投递逻辑（非 sticker）──
  if supports_media "$channel"; then
    TEXT_MESSAGE=$(build_text_message false)
    if openclaw message send --channel "$channel" --target "$target" --message "$TEXT_MESSAGE" >/dev/null 2>&1; then
      if openclaw message send --channel "$channel" --target "$target" --media "$SCREENSHOT_URL" >/dev/null 2>&1; then
        SUCCESS_CHANNEL="$channel"
        SUCCESS_TARGET="$target"
        SUCCESS_MODE="media"
        DELIVERED_TEXT="$TEXT_MESSAGE"
        info "文本 + 原生截图发送成功"
        break
      fi

      warn "${channel} 原生截图发送失败，降级为补发截图 URL"
      URL_FALLBACK=$(build_text_message true)
      if openclaw message send --channel "$channel" --target "$target" --message "$URL_FALLBACK" >/dev/null 2>&1; then
        SUCCESS_CHANNEL="$channel"
        SUCCESS_TARGET="$target"
        SUCCESS_MODE="degraded_url"
        DELIVERED_TEXT="$URL_FALLBACK"
        info "已降级为文本 + 截图 URL"
        break
      fi

      LAST_ERROR="${channel} 原生图片与 URL 降级都失败"
      warn "$LAST_ERROR，继续回退下一个通道"
      continue
    else
      LAST_ERROR="${channel} 文本消息发送失败"
      warn "$LAST_ERROR，继续回退下一个通道"
      continue
    fi
  fi

  TEXT_MESSAGE=$(build_text_message true)
  if openclaw message send --channel "$channel" --target "$target" --message "$TEXT_MESSAGE" >/dev/null 2>&1; then
    SUCCESS_CHANNEL="$channel"
    SUCCESS_TARGET="$target"
    SUCCESS_MODE="url"
    DELIVERED_TEXT="$TEXT_MESSAGE"
    info "纯文本 + 截图 URL 发送成功"
    break
  fi

  LAST_ERROR="${channel} 文本消息发送失败"
  warn "$LAST_ERROR，继续回退下一个通道"
done <<< "$CANDIDATE_LINES"

if [ -n "$SUCCESS_CHANNEL" ]; then
  report_delivery "$MESSAGE_ID" "sent" "$SUCCESS_CHANNEL" "$SUCCESS_TARGET" "$SUCCESS_MODE" "$DELIVERED_TEXT" "$SCREENSHOT_URL" ""
  UPDATED_KNOWN=$(update_config_after_send "$SUCCESS_CHANNEL" "$SUCCESS_TARGET" "$CANDIDATE_LINES")
  info "📮 送达成功: slot=${SLOT} message_id=${MESSAGE_ID} channel=${SUCCESS_CHANNEL} target=${SUCCESS_TARGET} mode=${SUCCESS_MODE} attempts=${ATTEMPT_COUNT}"
  echo "DELIVERY_OK slot=${SLOT} message_id=${MESSAGE_ID} channel=${SUCCESS_CHANNEL} mode=${SUCCESS_MODE}"
  exit 0
fi

warn "📮 送达失败: slot=${SLOT} message_id=${MESSAGE_ID} last_channel=${LAST_CHANNEL} attempts=${ATTEMPT_COUNT} error=${LAST_ERROR}"
report_delivery "$MESSAGE_ID" "failed" "$LAST_CHANNEL" "$LAST_TARGET" "text_only" "" "$SCREENSHOT_URL" "$LAST_ERROR"
error "所有候选通道都投递失败：${LAST_ERROR:-未知错误}"
