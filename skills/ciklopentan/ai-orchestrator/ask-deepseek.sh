#!/bin/bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TODAY=$(date '+%Y-%m-%d %H:%M %Z')

SEARCH_MODE=false
THINK_MODE=false
SESSION_NAME="${DEEPSEEK_SESSION:-}"
SESSION_FLAG=""
NEW_CHAT=""
END_SESSION=""
EXTRA_FLAGS=""
USE_DAEMON=false
SEARCH_TEMP_SESSION=false
QUESTION=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --search) SEARCH_MODE=true; shift ;;
    --think) THINK_MODE=true; shift ;;
    --session)
      SESSION_NAME="$2"
      SESSION_FLAG="--session $2"
      shift 2
      ;;
    --new-chat) NEW_CHAT="--new-chat"; shift ;;
    --end-session) END_SESSION="--end-session"; shift ;;
    --daemon) USE_DAEMON=true; shift ;;
    --visible) EXTRA_FLAGS="$EXTRA_FLAGS --visible"; shift ;;
    --wait) EXTRA_FLAGS="$EXTRA_FLAGS --wait"; shift ;;
    --close) EXTRA_FLAGS="$EXTRA_FLAGS --close"; shift ;;
    --debug) EXTRA_FLAGS="$EXTRA_FLAGS --debug"; shift ;;
    --help|-h)
      cat <<'EOF'
ask-deepseek.sh — универсальный wrapper (Puppeteer с демоном)

Использование:
  ask-deepseek.sh "вопрос"                    — одиночный запрос
  ask-deepseek.sh --session work "вопрос"     — сессия
  ask-deepseek.sh --session work "ещё вопрос" — продолжение сессии
  ask-deepseek.sh --session work --new-chat "вопрос" — новый чат в сессии
  ask-deepseek.sh --session work --end-session    — завершить сессию
  ask-deepseek.sh --search "запрос"           — поиск в интернете
  ask-deepseek.sh --daemon                    — использовать демон (быстрее)

Флаги:
  --session NAME   Имя сессии
  --search         Включить веб-поиск
  --think          Включить глубокое мышление (DeepThink)
  --new-chat       Начать новый чат в сессии
  --end-session    Завершить сессию
  --daemon         Использовать фоновый Chrome (ускоряет запросы)
  --visible        Открыть видимый браузер (если нужна авторизация)
  --wait           Ждать ручной авторизации (с --visible)
  --close          Закрыть браузер после ответа (без демона)
  --debug          Включить отладку
  -h, --help       Показать эту справку

Демон:
  Запуск демона:   pm2 start deepseek-daemon.js --name deepseek-daemon --no-autorestart
  Останов:         pm2 stop deepseek-daemon
  Автозапуск:      pm2 save && pm2 startup systemd -u $USER --hp $HOME
EOF
      exit 0
      ;;
    --)
      shift
      while [[ $# -gt 0 ]]; do
        QUESTION="${QUESTION:+$QUESTION }$1"
        shift
      done
      ;;
    -*)
      echo "Неизвестный флаг: $1. Запусти --help"
      exit 1
      ;;
    *)
      QUESTION="${QUESTION:+$QUESTION }$1"
      shift
      ;;
  esac
done

QUESTION=$(echo "$QUESTION" | xargs)

# End session
if [[ -n "$END_SESSION" ]]; then
  if [[ -n "$SESSION_NAME" ]]; then
    node "$SCRIPT_DIR/ask-puppeteer.js" $SESSION_FLAG --end-session 2>/dev/null || true
    rm -f "$SCRIPT_DIR/.sessions/${SESSION_NAME}.json"
    echo "Сессия '$SESSION_NAME' завершена"
  else
    echo "Ошибка: --end-session требует --session NAME" >&2
    exit 1
  fi
  exit 0
fi

if [[ -z "$QUESTION" ]]; then
  echo "Ошибка: нужен вопрос. Запусти --help для справки"
  exit 1
fi

# Промпт с датой и режимами
FULL_PROMPT="[Дата: ${TODAY}]"
[[ "$SEARCH_MODE" = true ]] && FULL_PROMPT="$FULL_PROMPT [РЕЖИМ: ПОИСК В ИНТЕРНЕТЕ]"
[[ "$THINK_MODE" = true ]] && FULL_PROMPT="$FULL_PROMPT [РЕЖИМ: DEEP THINK]"
FULL_PROMPT="$FULL_PROMPT $QUESTION"

# Флаги для ask-puppeteer.js
PUPPETEER_FLAGS=""
[[ "$SEARCH_MODE" = true ]] && PUPPETEER_FLAGS="$PUPPETEER_FLAGS --search"
[[ "$THINK_MODE" = true ]] && PUPPETEER_FLAGS="$PUPPETEER_FLAGS --think"
[[ -n "$SESSION_NAME" ]] && PUPPETEER_FLAGS="$PUPPETEER_FLAGS $SESSION_FLAG"
[[ -n "$NEW_CHAT" ]] && PUPPETEER_FLAGS="$PUPPETEER_FLAGS $NEW_CHAT"
[[ "$USE_DAEMON" = true ]] && PUPPETEER_FLAGS="$PUPPETEER_FLAGS --daemon"
[[ -n "$EXTRA_FLAGS" ]] && PUPPETEER_FLAGS="$PUPPETEER_FLAGS $EXTRA_FLAGS"

echo "📅 $TODAY"
[[ -n "$SESSION_NAME" ]] && echo "🔄 Сессия: $SESSION_NAME"
[[ "$SEARCH_MODE" = true ]] && echo "🔍 Поиск"
[[ "$THINK_MODE" = true ]] && echo "🧠 DeepThink"
[[ "$USE_DAEMON" = true ]] && echo "⚡ Режим демона (быстрый)"
echo ""

# Проверяем демон
if [[ "$USE_DAEMON" = true ]]; then
  if [[ ! -f "$SCRIPT_DIR/.daemon-ws-endpoint" ]]; then
    echo "❌ Демон не запущен. Запусти: cd \"$SCRIPT_DIR\" && pm2 start deepseek-daemon.js --name deepseek-daemon --no-autorestart"
    exit 1
  fi
fi

# Запускаем puppeteer
if [[ "$USE_DAEMON" = true ]]; then
  node "$SCRIPT_DIR/ask-puppeteer.js" "$FULL_PROMPT" $PUPPETEER_FLAGS 2>&1
else
  # Без демона — закрываем браузер после
  node "$SCRIPT_DIR/ask-puppeteer.js" "$FULL_PROMPT" $PUPPETEER_FLAGS --close 2>&1
fi

EXIT_CODE=$?

# Если был временный демон (автозапуск), не убиваем — пусть живёт для следующих запросов

exit $EXIT_CODE
