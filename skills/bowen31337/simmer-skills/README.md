# simmer-skills

OpenClaw skill for [Simmer](https://simmer.markets) prediction market trading — browse markets, score opportunities, execute trades via the Simmer SDK.

## What it does

A complete 4-hour trading pipeline:

```
brief → score → [human approval] → execute
```

- **brief.py** — fetches portfolio briefing + recent market movements
- **score.py** — ranks markets by edge/EV
- **execute.py** — places trades (dry-run by default, gated by review)
- **workflows/simmer-pipeline.lobster** — orchestrates all three on a 4h heartbeat

## Install

```bash
# Clone
git clone https://github.com/AlexChen31337/simmer-skills.git
cd simmer-skills

# Install deps
uv pip install simmer-sdk

# Set up credentials
mkdir -p ~/.config/simmer
chmod 700 ~/.config/simmer
echo '{"api_key":"YOUR_SIMMER_API_KEY"}' > ~/.config/simmer/credentials.json
chmod 600 ~/.config/simmer/credentials.json
```

Get your API key from https://simmer.markets/dashboard → Settings → API.

## Usage

```bash
# Health check
curl -s https://api.simmer.markets/api/sdk/health

# Agent status + balance
SIMMER_API_KEY=$(python3 -c "import json; print(json.load(open('$HOME/.config/simmer/credentials.json'))['api_key'])")
curl -s https://api.simmer.markets/api/sdk/agents/me -H "Authorization: Bearer $SIMMER_API_KEY"

# Run the pipeline (dry-run)
uv run python scripts/brief.py 4 | uv run python scripts/score.py --top 5
```

## Venues

| Venue | Currency | Status |
|-------|----------|--------|
| `simmer` | $SIM virtual | Paper trading — always available |
| `polymarket` | USDC (real) | Requires claimed agent + linked wallet |
| `kalshi` | USD (real) | Requires Pro tier + Solana wallet |

## Safety Rails

Default limits (change via `PATCH /api/sdk/user/settings`):

- Max per trade: $100
- Daily limit: $500
- Trades/day: 50
- Auto stop-loss: 50%
- Auto take-profit: 35%

## Real Trading — Important

1. Claim your agent via claim code at the dashboard
2. Link a **dedicated trading wallet** (never your main wallet)
3. Set `venue="polymarket"` on your trade calls
4. Approve USDC spending: `client.set_approvals()`
5. Trade with live USDC

⚠️ **Never commit your `credentials.json` or private keys.** The `.gitignore` in this repo excludes them by default.

## Part of the OpenClaw Skills Ecosystem

OpenClaw skills are modular capability bundles. This one works with the `openclaw` CLI and `claw-forge` harness. See:

- https://docs.openclaw.ai/cli/skills
- https://clawhub.ai

## License

MIT © 2026 Alex Chen
