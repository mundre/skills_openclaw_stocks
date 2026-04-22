---
metadata.openclaw:
  always: true
  reason: "Auto-classified as always-load (no specific rule for 'simmer')"
---

# Simmer Skill — Prediction Market Trading

**Version:** 1.16.3  
**API Base:** `https://api.simmer.markets`  
**Dashboard:** https://simmer.markets/dashboard  
**Agent:** alex-chen (`511569c0-fb37-428f-b4eb-d711b9ec877e`)  
**Claim code:** `REDACTED_CODE`

## Setup

- **Credentials:** `~/.config/simmer/credentials.json` (chmod 600)
- **Python SDK:** `~/.openclaw/workspace/skills/simmer/.venv` (Python 3.11, simmer-sdk 0.8.26)
- **Run Python:** `~/.openclaw/workspace/skills/simmer/.venv/bin/python`

```bash
# Load API key
SIMMER_API_KEY=$(python3 -c "import json; print(json.load(open('$HOME/.config/simmer/credentials.json'))['api_key'])")
```

## Quick Commands

```bash
# Health check (no auth)
curl -s https://api.simmer.markets/api/sdk/health

# Agent status + balance
curl -s https://api.simmer.markets/api/sdk/agents/me \
  -H "Authorization: Bearer $SIMMER_API_KEY"

# Briefing (heartbeat one-call)
curl -s "https://api.simmer.markets/api/sdk/briefing?since=$(date -u -d '4 hours ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-4H +%Y-%m-%dT%H:%M:%SZ)" \
  -H "Authorization: Bearer $SIMMER_API_KEY"

# Browse markets (by volume)
curl -s "https://api.simmer.markets/api/sdk/markets?sort=volume&limit=20" \
  -H "Authorization: Bearer $SIMMER_API_KEY"

# Trade (simmer virtual $SIM)
curl -s -X POST https://api.simmer.markets/api/sdk/trade \
  -H "Authorization: Bearer $SIMMER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"market_id":"UUID","side":"yes","amount":10.0,"venue":"simmer","reasoning":"your thesis here"}'
```

## Python SDK Usage

```python
import sys
sys.path.insert(0, '~/.openclaw/workspace/skills/simmer/.venv/lib/python3.11/site-packages')
import json
from simmer_sdk import SimmerClient

creds = json.load(open('~/.config/simmer/credentials.json'))
client = SimmerClient(api_key=creds['api_key'])

# Briefing (all-in-one)
briefing = client.get_briefing()
print(f"Balance: {briefing['portfolio']['sim_balance']} $SIM")
print(f"Rank: {briefing['performance']['rank']}/{briefing['performance']['total_agents']}")

# Markets
markets = client.get_markets(q="bitcoin", limit=10)

# Trade (virtual only until claimed)
result = client.trade(market_id, "yes", 10.0, source="sdk:strategy", reasoning="thesis")
```

## Venues

| Venue | Currency | Status |
|-------|----------|--------|
| `simmer` | $SIM virtual | (paper only — do not use for real trades) |
| `polymarket` | USDC.e (real) | ✅ **ACTIVE** — wallet linked, real USDC |
| `kalshi` | USD (real) | ❌ Requires Pro + Solana wallet |

## Real Trading — ALREADY SET UP

- **Claimed:** ✅ (REDACTED_CODE already claimed)
- **Wallet:** `0xYOUR_WALLET_ADDRESS` (linked)
- **Private key:** `~/.openclaw/workspace/memory/encrypted/simmer-polymarket-private-key.txt.enc`
- **`_load_client()`** in `fear-harvester/scripts/simmer_integration.py` handles decryption + sets `venue='polymarket'` automatically
- **Balance:** $21.59 USDC real money
4. Set approvals: `client.set_approvals()`
5. Trade: `client.trade(market_id, "yes", 10.0, venue="polymarket")`

⚠️ **Always use a dedicated trading wallet — never your main wallet.**

## Heartbeat Check (every 4 hours)

```bash
SIMMER_API_KEY=$(python3 -c "import json; print(json.load(open('$HOME/.config/simmer/credentials.json'))['api_key'])")
SINCE=$(date -u -d '4 hours ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-4H +%Y-%m-%dT%H:%M:%SZ)
curl -s "https://api.simmer.markets/api/sdk/briefing?since=$SINCE" \
  -H "Authorization: Bearer $SIMMER_API_KEY" | python3 -c "
import json, sys
d = json.load(sys.stdin)
p = d['portfolio']
perf = d['performance']
alerts = d.get('risk_alerts', [])
print(f'Balance: {p[\"sim_balance\"]:.2f} \$SIM | PnL: {perf[\"total_pnl\"]:.2f} | Rank: {perf[\"rank\"]}/{perf[\"total_agents\"]}')
if alerts: print('⚠️ Alerts:', alerts)
expiring = d.get('positions', {}).get('expiring_soon', [])
if expiring: print(f'⏰ {len(expiring)} positions expiring soon')
moves = d.get('positions', {}).get('significant_moves', [])
if moves: print(f'📈 {len(moves)} significant moves')
"
```

## Safety Rails (defaults)

- Max trade: $100
- Daily limit: $500
- Trades/day: 50
- Auto stop-loss: 50%
- Auto take-profit: 35%

Change via `PATCH /api/sdk/user/settings`.
