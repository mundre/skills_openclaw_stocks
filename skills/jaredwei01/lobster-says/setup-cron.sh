#!/bin/bash
# 虾说 — 定时推送 Cron 注册脚本

set -u

CHANNEL=""
TO=""
MORNING_TIME=""
DISCOVERY_TIME=""
EVENING_TIME=""
MEMORY_MODE=""
ACTIVE_WINDOW_MINUTES="${ACTIVE_WINDOW_MINUTES:-10080}"
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="${BASE_DIR}/.lobster-config"
LOG_DIR="${BASE_DIR}/logs"
RUN_TS="$(date +%Y%m%d-%H%M%S)"
LOG_FILE="${LOG_DIR}/setup-cron-${RUN_TS}.log"
PUSH_SCRIPT="${BASE_DIR}/push-scheduled-message.sh"
OPENCLAW_CONFIG_FILE="${OPENCLAW_CONFIG_FILE:-$HOME/.openclaw/openclaw.json}"
GATEWAY_AUTH_MODE=""
GATEWAY_TOKEN=""
OPENCLAW_CRON_ARGS=()

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }
CURRENT_STEP="启动"
step()  { CURRENT_STEP="$1"; echo -e "${CYAN}──${NC} $1"; }

mkdir -p "$LOG_DIR"
if command -v tee >/dev/null 2>&1; then
  exec > >(tee -a "$LOG_FILE") 2>&1
else
  exec >>"$LOG_FILE" 2>&1
fi

echo "[log] setup-cron started at $(date '+%F %T')"
echo "[log] file: ${LOG_FILE}"

after_exit() {
  local exit_code=$?
  if [ "$exit_code" -ne 0 ]; then
    echo ""
    echo "[log] setup-cron failed at step: ${CURRENT_STEP} (exit=${exit_code})"
    echo "[log] inspect: ${LOG_FILE}"
  else
    echo "[log] setup-cron finished successfully"
  fi
}
trap after_exit EXIT

while [[ $# -gt 0 ]]; do
  case "$1" in
    --channel) CHANNEL="$2"; shift 2 ;;
    --to) TO="$2"; shift 2 ;;
    --morning) MORNING_TIME="$2"; shift 2 ;;
    --discovery) DISCOVERY_TIME="$2"; shift 2 ;;
    --evening) EVENING_TIME="$2"; shift 2 ;;
    --memory-mode) MEMORY_MODE="$2"; shift 2 ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
done

for cmd in openclaw python3; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    error "$cmd 不可用"
  fi
done

if [ ! -f "$CONFIG_FILE" ]; then
  error ".lobster-config 不存在，请先完成虾的初始化"
fi

if [ ! -f "$PUSH_SCRIPT" ]; then
  error "运行时推送脚本不存在：${PUSH_SCRIPT}"
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
    value = data.get(key, default)
    print(value if value is not None else default)
except Exception:
    print(default)
PY
}

load_gateway_auth() {
  local detected
  detected=$(OPENCLAW_CONFIG_PATH="$OPENCLAW_CONFIG_FILE" OPENCLAW_GATEWAY_AUTH_MODE="${OPENCLAW_GATEWAY_AUTH_MODE:-}" OPENCLAW_GATEWAY_TOKEN="${OPENCLAW_GATEWAY_TOKEN:-}" python3 - <<'PY'
import json
import os
from pathlib import Path

mode = (os.environ.get("OPENCLAW_GATEWAY_AUTH_MODE") or "").strip()
token = (os.environ.get("OPENCLAW_GATEWAY_TOKEN") or "").strip()
config_path = Path(os.path.expanduser(os.environ.get("OPENCLAW_CONFIG_PATH", "")))

if (not mode or (mode == "token" and not token)) and config_path.exists():
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        auth = ((data.get("gateway") or {}).get("auth") or {}) if isinstance(data, dict) else {}
        if isinstance(auth, dict):
            mode = mode or str(auth.get("mode") or "").strip()
            token = token or str(auth.get("token") or "").strip()
    except Exception:
        pass

print(mode)
print(token)
PY
)
  GATEWAY_AUTH_MODE=$(echo "$detected" | sed -n '1p')
  GATEWAY_TOKEN=$(echo "$detected" | sed -n '2p')
  OPENCLAW_CRON_ARGS=()
  if [ "$GATEWAY_AUTH_MODE" = "token" ] && [ -n "$GATEWAY_TOKEN" ]; then
    OPENCLAW_CRON_ARGS+=(--token "$GATEWAY_TOKEN")
  fi
}

if [ -z "$MORNING_TIME" ]; then
  MORNING_TIME=$(read_config_value "morning_time" "09:00")
fi
if [ -z "$DISCOVERY_TIME" ]; then
  DISCOVERY_TIME=$(read_config_value "discovery_time" "21:30")
fi
if [ -z "$EVENING_TIME" ]; then
  EVENING_TIME=$(read_config_value "evening_time" "21:00")
fi
if [ -z "$MEMORY_MODE" ]; then
  MEMORY_MODE=$(read_config_value "memory_mode" "smart")
fi
if [ -z "$CHANNEL" ]; then
  CHANNEL=$(read_config_value "channel" "")
fi
if [ -z "$TO" ]; then
  TO=$(read_config_value "chat_id" "")
fi

case "$MEMORY_MODE" in
  lightweight|smart|deep) ;;
  *) error "memory_mode 必须是 lightweight / smart / deep" ;;
esac

load_gateway_auth
if [ "$GATEWAY_AUTH_MODE" = "token" ]; then
  if [ -n "$GATEWAY_TOKEN" ]; then
    info "检测到 gateway token 认证：cron 命令将自动携带 token"
  else
    warn "检测到 gateway token 认证，但未找到 token；cron 注册可能失败"
  fi
fi

step "扫描最近活跃的通道（仅用于更新 fallback 配置）..."
SESSIONS_JSON=$(openclaw sessions --json --active "$ACTIVE_WINDOW_MINUTES" 2>/dev/null || echo "[]")
DETECTED=$(SESSIONS_JSON="$SESSIONS_JSON" python3 <<'PY'
import json
import os

try:
    sessions = json.loads(os.environ.get("SESSIONS_JSON", "[]"))
    if not isinstance(sessions, list):
        sessions = [sessions]
except Exception:
    sessions = []

ordered = []
seen = set()

def add(channel, peer_id):
    channel = (channel or "").strip()
    peer_id = (peer_id or "").strip()
    if not channel or channel == "unknown" or not peer_id:
        return
    key = (channel, peer_id)
    if key in seen:
        return
    seen.add(key)
    ordered.append({"channel": channel, "peer_id": peer_id})

for session in sessions:
    direct_channel = session.get("channel") or session.get("platform") or session.get("imChannel") or ""
    direct_target = session.get("peer_id") or session.get("peerId") or session.get("target") or session.get("chat_id") or session.get("chatId") or ""
    if direct_channel and direct_target:
        add(direct_channel, direct_target)
        continue

    key = session.get("sessionKey") or session.get("key") or session.get("id") or ""
    if not key:
        continue
    parts = key.split(":")
    if not parts or parts[0].lower() in ("cron", "hook"):
        continue
    if len(parts) <= 3 and parts[-1].lower() == "main":
        continue
    if len(parts) >= 5 and parts[0].lower() == "agent":
        channel = parts[2]
        marker = parts[3].lower()
        if marker in ("direct", "dm"):
            add(channel, parts[4])

best = ordered[0] if ordered else {"channel": "", "peer_id": ""}
print(f"{best['channel']}|{best['peer_id']}")
print(json.dumps(ordered, ensure_ascii=False))
PY
)

DETECTED_TARGET=$(echo "$DETECTED" | head -1)
DETECTED_CHANNEL=$(echo "$DETECTED_TARGET" | cut -d'|' -f1)
DETECTED_TO=$(echo "$DETECTED_TARGET" | cut -d'|' -f2)
DETECTED_KNOWN_JSON=$(echo "$DETECTED" | tail -1)

if [ -z "$CHANNEL" ] && [ -n "$DETECTED_CHANNEL" ]; then
  CHANNEL="$DETECTED_CHANNEL"
fi
if [ -z "$TO" ] && [ -n "$DETECTED_TO" ]; then
  TO="$DETECTED_TO"
fi

parse_time() {
  local time_str="$1"
  local hour
  local minute
  hour=$(echo "$time_str" | cut -d: -f1 | sed 's/^0//')
  minute=$(echo "$time_str" | cut -d: -f2 | sed 's/^0//')
  echo "${minute:-0} ${hour:-0} * * *"
}

MORNING_CRON=$(parse_time "$MORNING_TIME")
DISCOVERY_CRON=$(parse_time "$DISCOVERY_TIME")
EVENING_CRON=$(parse_time "$EVENING_TIME")
LOBSTER_NAME=$(read_config_value "lobster_name" "虾")

echo ""
echo "🦞 虾说 — 注册定时推送"
echo ""
echo "  早安时间: ${MORNING_TIME} (cron: ${MORNING_CRON})"
echo "  晚间 roundup: ${DISCOVERY_TIME} (cron: ${DISCOVERY_CRON})"
echo "  晚安时间: ${EVENING_TIME} (cron: ${EVENING_CRON})"
echo "  虾名: ${LOBSTER_NAME}"
echo "  理解模式: ${MEMORY_MODE}"
if [ -n "$CHANNEL" ] && [ -n "$TO" ]; then
  echo "  当前 fallback 通道: ${CHANNEL} → ${TO}"
else
  echo "  当前 fallback 通道: 尚未锁定（运行时将优先扫最近会话）"
fi
echo ""

step "清理旧的定时任务..."
CRON_JSON=$(openclaw cron list --json 2>/dev/null || echo "")
OLD_IDS=$(CRON_DATA="$CRON_JSON" python3 <<'PY'
import json
import os
import sys

raw = os.environ.get("CRON_DATA", "")
if not raw.strip():
    sys.exit(0)
json_str = None
for i, ch in enumerate(raw):
    if ch in ("{", "["):
        json_str = raw[i:]
        break
if not json_str:
    sys.exit(0)
try:
    data = json.loads(json_str)
except Exception:
    sys.exit(0)
jobs = data.get("jobs", []) if isinstance(data, dict) else data if isinstance(data, list) else []
target_names = {
    "lobster-says-morning",
    "lobster-says-discovery",
    "lobster-says-evening",
    "lobster-says-sticker",
    "lobster-says-wallpaper",
    "lobster-says-digest",
}
for job in jobs:
    if isinstance(job, dict) and job.get("name") in target_names and job.get("id"):
        print(f"{job['name']}|{job['id']}")
PY
)

if [ -n "$OLD_IDS" ]; then
  echo "$OLD_IDS" | while IFS='|' read -r name job_id; do
    [ -z "$job_id" ] && continue
    warn "删除旧任务: ${name} (${job_id})"
    openclaw cron remove "$job_id" >/dev/null 2>&1 || warn "删除失败: ${name} (${job_id})"
  done
else
  info "没有发现旧任务"
fi

register_job() {
  local name="$1"
  local cron_expr="$2"
  local message="$3"
  step "注册 ${name}..."
  if openclaw cron add \
    --name "$name" \
    --cron "$cron_expr" \
    --tz "Asia/Shanghai" \
    --session isolated \
    --no-deliver \
    --message "$message" >/dev/null; then
    info "${name} 注册成功"
  else
    error "${name} 注册失败"
  fi
}

register_job "lobster-says-morning" "$MORNING_CRON" "请立即执行以下命令，并只用一句话报告结果：\nbash \"${PUSH_SCRIPT}\" --slot morning"
register_job "lobster-says-discovery" "$DISCOVERY_CRON" "请立即执行以下命令，并只用一句话报告结果：\nbash \"${PUSH_SCRIPT}\" --slot discovery"
register_job "lobster-says-evening" "$EVENING_CRON" "请立即执行以下命令，并只用一句话报告结果：\nbash \"${PUSH_SCRIPT}\" --slot evening"
register_job "lobster-says-sticker" "30 15 * * 3,6" "请立即执行以下命令，并只用一句话报告结果：\nbash \"${PUSH_SCRIPT}\" --slot sticker"
register_job "lobster-says-wallpaper" "0 16 * * 0" "请立即执行以下命令，并只用一句话报告结果：\nbash \"${PUSH_SCRIPT}\" --slot wallpaper"

if [ "$MEMORY_MODE" != "lightweight" ]; then
  register_job "lobster-says-digest" "0 3,9,15,21 * * *" "请执行以下命令来消化用户的对话记录：\nbash \"${BASE_DIR}/digest-transcript.sh\" --mode ${MEMORY_MODE}\n执行完毕后，简要报告结果。"
else
  info "轻量陪伴模式：不注册 transcript digest cron"
fi

echo ""
step "更新本地配置..."
CONFIG_FILE="$CONFIG_FILE" MORNING_TIME="$MORNING_TIME" DISCOVERY_TIME="$DISCOVERY_TIME" EVENING_TIME="$EVENING_TIME" MEMORY_MODE_VALUE="$MEMORY_MODE" CHANNEL_VALUE="$CHANNEL" TO_VALUE="$TO" KNOWN_JSON="$DETECTED_KNOWN_JSON" python3 <<'PY'
import json
import os
from pathlib import Path

config_path = Path(os.environ["CONFIG_FILE"])
try:
    config = json.loads(config_path.read_text(encoding="utf-8"))
except Exception:
    config = {}

config["morning_time"] = os.environ["MORNING_TIME"]
config["discovery_time"] = os.environ["DISCOVERY_TIME"]
config["evening_time"] = os.environ["EVENING_TIME"]
config["memory_mode"] = os.environ["MEMORY_MODE_VALUE"]

channel = os.environ.get("CHANNEL_VALUE", "").strip()
target = os.environ.get("TO_VALUE", "").strip()
if channel and target:
    config["channel"] = channel
    config["chat_id"] = target

ordered = []
seen = set()
def add(ch, peer_id):
    ch = (ch or "").strip()
    peer_id = (peer_id or "").strip()
    if not ch or not peer_id:
        return
    key = (ch, peer_id)
    if key in seen:
        return
    seen.add(key)
    ordered.append({"channel": ch, "peer_id": peer_id})

if channel and target:
    add(channel, target)

try:
    detected = json.loads(os.environ.get("KNOWN_JSON", "[]"))
except Exception:
    detected = []
for item in detected:
    if isinstance(item, dict):
        add(item.get("channel"), item.get("peer_id"))
for item in config.get("known_channels", []):
    if isinstance(item, dict):
        add(item.get("channel"), item.get("peer_id"))

config["known_channels"] = ordered
config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
print("[✓] .lobster-config 已更新")
PY

echo ""
info "定时推送注册完成！"
echo ""
echo "  🌅 早安推送: 每天 ${MORNING_TIME}"
echo "  📰 晚间 roundup: 每天 ${DISCOVERY_TIME}"
echo "  🌙 晚安推送: 每天 ${EVENING_TIME}"
echo "  🎨 表情包: 每周三/六 15:30"
echo "  🖼️ 壁纸: 每周日 16:00"
if [ "$MEMORY_MODE" = "lightweight" ]; then
  echo "  🧠 Transcript digest: 已关闭"
else
  echo "  🧠 Transcript digest: 每 6 小时一次（模式: ${MEMORY_MODE}）"
fi
