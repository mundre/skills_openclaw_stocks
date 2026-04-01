---
name: polymarket-spread-sniper
description: Snipe mispriced markets by comparing Polymarket AMM price vs live CLOB orderbook midpoint. Buys the underpriced side when spread > 4% on liquid markets. Pure algorithm, zero LLM, no outcome prediction needed.
metadata:
  author: "openclaw"
  version: "1.1.0"
  displayName: "Polymarket Spread Sniper"
  difficulty: "intermediate"
---

# Polymarket Spread Sniper

> **This is a template.** Buys the underpriced side when the CLOB midpoint diverges from the AMM price. No outcome prediction needed — pure spread arbitrage.

## The Edge

Polymarket has two pricing mechanisms:
1. **AMM** — pool-based price, slow to update
2. **CLOB** — live orderbook, reflects real money

When they diverge by >4%, the AMM is mispriced. This skill buys the cheap side and profits when prices converge.

## Quick Start

```bash
export SIMMER_API_KEY=sk_live_...

# Dry run (safe)
python spread_sniper.py

# Live trading
python spread_sniper.py --live

# Show positions
python spread_sniper.py --positions
```

## Configuration

| Setting | Env Var | Default | Description |
|---------|---------|---------|-------------|
| Min spread | `SIMMER_SPREAD_MIN_SPREAD` | 0.04 | Min bid-ask spread to trade (4¢) |
| Min volume | `SIMMER_SPREAD_MIN_VOLUME` | 5000 | Min 24h volume in USD |
| Max position | `SIMMER_SPREAD_MAX_POSITION` | 5.00 | Max USD per trade |
| Max trades/run | `SIMMER_SPREAD_MAX_TRADES` | 3 | Max trades per scan |
| Min price | `SIMMER_SPREAD_MIN_PRICE` | 0.10 | Never buy below 10¢ |
| Max price | `SIMMER_SPREAD_MAX_PRICE` | 0.90 | Never buy above 90¢ |
| Max hours | `SIMMER_SPREAD_MAX_HOURS` | 48 | Skip markets resolving >48h |
