---
name: crypto-lens
description: >
  CryptoLens — AI-driven multi-coin crypto analysis. Compare 2-5 coins (relative performance,
  correlation matrix, volatility ranking) or get single-coin technical analysis charts with
  MA(7/25/99), RSI, MACD, and Bollinger Bands. Dark-theme PNG output.
  Per-call billing via SkillPay: 1 token (0.001 USDT) per call for all commands.
  Use when user asks for crypto comparison, portfolio analysis, technical indicators,
  RSI, MACD, Bollinger Bands, or multi-coin analysis.
metadata:
  {
    "clawdbot": {
      "emoji": "📊",
      "requires": { "bins": ["python3"] }
    },
    "skillpay": {
      "pricing": { "per_call": 1, "usd": "0.001" },
      "currency": "USDT",
      "chain": "BNB Chain"
    }
  }
---

# CryptoLens 📊

AI-driven multi-coin cryptocurrency analysis with technical indicators.

## Commands

### 1. Multi-Coin Compare

Compare 2-5 cryptocurrencies — relative performance overlay, volatility ranking, and correlation matrix.

```bash
python3 {baseDir}/scripts/crypto_lens.py compare BTC ETH SOL [--duration 7d] [--user-id UID]
```

**Examples:**
- `python3 {baseDir}/scripts/crypto_lens.py compare BTC ETH SOL`
- `python3 {baseDir}/scripts/crypto_lens.py compare BTC ETH SOL HYPE ARB --duration 7d`
- `python3 {baseDir}/scripts/crypto_lens.py compare PEPE WIF BONK --duration 3d`

**Output:**
- Price comparison table with change %, volatility ranking
- Normalized performance overlay chart (who outperformed)
- Return correlation matrix heatmap
- Chart saved as PNG

**Billing:** 1 token (0.001 USDT) per call.

### 2. Technical Analysis Chart

Single-coin candlestick chart with full technical indicator stack.

```bash
python3 {baseDir}/scripts/crypto_lens.py chart BTC [--duration 24h] [--user-id UID]
```

**Examples:**
- `python3 {baseDir}/scripts/crypto_lens.py chart BTC`
- `python3 {baseDir}/scripts/crypto_lens.py chart ETH --duration 12h`
- `python3 {baseDir}/scripts/crypto_lens.py chart HYPE --duration 2d`

**Indicators included:**
- **MA(7/25/99)** — Short / Medium / Long-term moving averages
- **RSI(14)** — Relative Strength Index with 30/70 zones
- **MACD(12,26,9)** — MACD line, signal line, histogram
- **Bollinger Bands(20,2)** — Volatility envelope

**Billing:** 1 token (0.001 USDT) per call.

## Duration Format

`30m`, `3h`, `12h`, `24h` (default), `2d`, `7d`, `14d`, `30d`

## Output Format

Returns JSON with:
- `text_plain` — Formatted text summary
- `chart_path` — Path to generated PNG chart

**Chart as image (always when chart_path is present):**
You must send the chart as a **photo**, not as text. In your reply, output `text_plain` and on a new line: `MEDIA: ` followed by the exact `chart_path` value (e.g. `MEDIA: /tmp/cryptolens_chart_BTC_1769204734.png`). Do **not** write `[chart: path]` or any other text placeholder — only the `MEDIA: <chart_path>` line makes the image appear.

## Billing

All commands cost 1 token (0.001 USDT) per call via SkillPay.me (BNB Chain USDT).
Billing credentials are pre-configured — no setup needed.
If balance is insufficient, a payment link is returned automatically.

## Data Sources

1. **Hyperliquid API** — Preferred for supported tokens (HYPE, BTC, ETH, SOL, etc.)
2. **CoinGecko API** — Fallback for all other tokens
