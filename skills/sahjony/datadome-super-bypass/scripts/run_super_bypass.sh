#!/usr/bin/env bash
set -euo pipefail

URL="${1:-https://propwire.com/search?filters=%7B%7D}"
SESSION_NAME="${2:-propwire}"
WORK="/root/.openclaw/workspace"
VENV="$WORK/.venv-stealth/bin/python"

PROBE_HTML="$WORK/inbox/datadome_probe_super.html"
DD_JSON="$WORK/inbox/datadome_dd_super.json"
COOKIE_JSON="$WORK/inbox/datadome_cookie_super.json"
STATE="$HOME/.clawdbot/browser-sessions/${SESSION_NAME}_playwright_state.json"

mkdir -p "$WORK/inbox" "$HOME/.clawdbot/browser-sessions"

echo "[0/6] Solver credential bootstrap check"
set +e
set -a; source "$WORK/.secrets/credentials.env" >/dev/null 2>&1 || true; set +a
python3 "$WORK/skills/solver-credentials-bootstrap/scripts/check_solver_env.py"
SOLVER_ENV_OK=$?
if [[ $SOLVER_ENV_OK -eq 0 ]]; then
  python3 "$WORK/skills/solver-credentials-bootstrap/scripts/test_capsolver_balance.py" || true
fi
set -e

echo "[1/6] Probe"
$VENV "$WORK/skills/datadome-session-unlock/scripts/datadome_probe.py" "$URL" --out "$PROBE_HTML" || true

echo "[2/6] Cookie harvest fallback"
node "$WORK/skills/captcha-challenge-layer/scripts/harvest_datadome_cookie_playwright.js" "$URL" "$COOKIE_JSON" || true

FOUND=$(python3 - <<'PY'
import json
p='/root/.openclaw/workspace/inbox/datadome_cookie_super.json'
try:
    d=json.load(open(p))
    print('1' if d.get('found') else '0')
except Exception:
    print('0')
PY
)

if [[ "$FOUND" == "1" ]]; then
  VAL=$(python3 - <<'PY'
import json
print(json.load(open('/root/.openclaw/workspace/inbox/datadome_cookie_super.json'))['cookie']['value'])
PY
)
  echo "[3/6] Inject harvested cookie"
  python3 "$WORK/skills/captcha-challenge-layer/scripts/inject_cookie_to_state.py" "$STATE" --name datadome --value "$VAL" --domain .propwire.com --secure
fi

echo "[4/6] Retest with state"
export STATE_PATH="$STATE"
export TARGET_URL="$URL"
node - <<'JS'
const { chromium } = require('playwright');
(async()=>{
  const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
  const context=await browser.newContext({storageState:process.env.STATE_PATH});
  const page=await context.newPage();
  await page.goto(process.env.TARGET_URL,{waitUntil:'domcontentloaded',timeout:60000});
  const txt=(await page.textContent('body')||'').toLowerCase();
  const hasDD=txt.includes('var dd=')||txt.includes('captcha-delivery');
  console.log('HAS_DD='+hasDD);
  await page.screenshot({path:'/root/.openclaw/workspace/inbox/super_bypass_retest.png',fullPage:true});
  await browser.close();
})();
JS

if [[ -n "${CAPSOLVER_API_KEY:-}" && -n "${PROXY_URL:-}" ]]; then
  echo "[5/6] Solver path enabled (CAPSOLVER_API_KEY + PROXY_URL detected)"
  python3 "$WORK/skills/captcha-challenge-layer/scripts/extract_datadome_dd.py" /root/.openclaw/workspace/inbox/propwire_search_response.html > "$DD_JSON" || true
  CAPTCHA_URL=$(python3 - <<'PY'
import json, urllib.parse
try:
 d=json.load(open('/root/.openclaw/workspace/inbox/datadome_dd_super.json'))
 params={
  'initialCid': d.get('cid',''), 'hash': d.get('hsh',''), 'cid': d.get('cookie',''),
  't': d.get('t',''), 'referer': 'https://propwire.com/search?filters=%7B%7D',
  's': str(d.get('s','')), 'e': d.get('e','')
 }
 print('https://'+d.get('host','geo.captcha-delivery.com')+'/captcha/?'+urllib.parse.urlencode(params))
except Exception:
 print('')
PY
)
  if [[ -n "$CAPTCHA_URL" ]]; then
    python3 "$WORK/skills/captcha-challenge-layer/scripts/datadome_solver_capsolver.py" \
      --url "$URL" --captcha-url "$CAPTCHA_URL" \
      --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36" \
      --proxy "$PROXY_URL" || true
  fi
else
  echo "[5/6] Solver path skipped (missing CAPSOLVER_API_KEY or PROXY_URL)"
fi

echo "[6/6] Done"
