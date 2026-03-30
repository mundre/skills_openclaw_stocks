# Analysis Scenarios & Workflows

## Table of Contents

1. [Response Templates](#response-templates)
2. [Analysis Scenarios](#analysis-scenarios)
3. [Cross-Step Workflows](#cross-step-workflows)
4. [Suggest Next Steps](#suggest-next-steps)
5. [Domain Knowledge Thresholds](#domain-knowledge-thresholds)

---

## Response Templates

### "余额多少" / "Balance?"

**API calls**: `get-balance` → `get-positions` → `get-ticker` per position

```
Taco 账户余额
总权益: XX.XX USDC
可用余额: XX.XX USDC
已用保证金: XX.XX USDC
未实现盈亏: ±XX.XX USDC

当前持仓 (N 个):
  ETHUSDC 多头 | 入场 2147.4 | 现价 2144.6 | 浮动 -1.32 USDC (-X.X%)
```

If available balance < 5 USDC, append:
```
⚠️ 可用余额不足 5 USDC，建议充值 USDC 后再进行交易。
支持充值链：Arbitrum（推荐）、Ethereum、Base、Polygon，地址相同。
```

Note: "现价" MUST come from `get-ticker`. Fallback: Hyperliquid `allMids`.

### "我的仓位" / "Show positions"

**API calls**: `get-positions` → `get-ticker` per position → `get-liquidation-price` per position

```
ETHUSDC 多头
  入场价: 2147.4 | 现价: 2144.6 (来自实时报价)
  仓位: XX USDC | 杠杆: 10x
  浮动盈亏: -1.32 USDC (-X.X%)
  强平价格: 1932.7 (距现价 -9.9%)
  止损: 2083.0 | 止盈: 2276.1
```

Note: "强平价格" MUST come from `get-liquidation-price` API. Never calculate it.

### "BTC 多少了" / "Price of ETH?"

**API calls**: `get-ticker --symbol <SYM>`

```
BTC: $87,500.00 (24h +2.3%)
```

---

## Analysis Scenarios

### Scenario A: Technical Analysis

**Trigger**: "technical analysis", "should I long or short", "support/resistance", "该怎么做"

**Flow**:
1. `get-kline --interval 1h --start-time <24h_ago>` → short-term
2. `get-kline --interval 1d --start-time <30d_ago>` → long-term
3. `get-ticker` → current price, 24h change, volume
4. `get-funding-rate` → long/short bias
5. `get-orderbook --depth 10` → buy/sell pressure

**Judgment**: Support/resistance from kline highs/lows, volume vs 7d average, funding rate sign, orderbook imbalance.

**Output**: Short-term (4h-24h) + long-term (1w+) view. Include: price, key levels, momentum, funding cost, suggestion with risk caveat.

### Scenario B: Liquidity / Slippage Analysis

**Trigger**: "liquidity", "slippage", "depth", "can I trade $X without moving price"

**Flow**:
1. `get-orderbook --depth 50`
2. `get-ticker` → 24h volume, spread
3. `get-recent-trades --limit 100`

**Judgment**: Spread > 0.1% = wide. Depth within 1% < $50k = thin. Walk ask ladder for slippage simulation. Order > 5% daily volume = significant impact.

**Output**: Spread %, depth summary, simulated slippage, order type recommendation.

### Scenario C: Funding Rate Arbitrage

**Trigger**: "funding arbitrage", "high funding", "funding rate comparison"

**Flow**:
1. `get-symbols --type perp` → all perps
2. `get-funding-rate` for top symbols
3. Candidates with |rate| > 0.01%: check `get-ticker` (volume) + `get-orderbook` (liquidity)

**Judgment**: |rate| > 0.01%/8h (~13% annualized), volume > $5M, depth within 0.5% > $100k.

**Output**: Ranked candidates with: symbol, rate, annualized, volume, depth, risks.

### Scenario D: Portfolio Review

**Trigger**: "review portfolio", "allocation", "仓位配比"

**Flow**:
1. `get-positions` + `get-balance`
2. Per position: `get-ticker`, `get-funding-rate`, `get-liquidation-price`
3. `get-pnl-summary --period 7d`

**Judgment**: Concentration > 40% = high. Liq distance < 10% = danger. Sum funding vs PnL. Correlated positions = hidden risk.

**Output**: Position table + concentration score, risk rating, adjustment suggestions.

### Scenario E: Market Overview

**Trigger**: "market overview", "行情", "大盘怎么样"

**Flow**:
1. `get-ticker` (all) → sort by volume, 24h change
2. Top 3 gainers, losers, volume
3. `get-funding-rate` for BTC + ETH → sentiment

**Output**: BTC/ETH price + change, top movers, funding sentiment, brief outlook.

---

## Cross-Step Workflows

### Pre-Trade Research → Execute

```
1. get-ticker → current price
2. get-kline --interval 4h → trend
3. get-funding-rate → holding cost
4. get-orderbook --depth 10 → liquidity
5. get-balance → funds check (see Pre-Trade Validation in SKILL.md)
   ↓ present analysis + estimated margin, user confirms
6. open-position
7. get-liquidation-price → inform user
```

### Daily Portfolio Check

```
1. get-balance → equity
2. get-positions → all positions
3. Per position: get-liquidation-price, get-funding-rate
4. get-pnl-summary --period 1d
5. get-trade-history --start-time <today>
6. get-credits
```

### Post-Trade Review

```
1. get-trade-history --start-time <week_start>
2. get-pnl-summary --period 7d
3. get-fee-summary --period 7d
4. get-balance
```

### Signal-Driven Quick Trade

```
1. get-ticker → price + 24h change
2. get-kline --interval 1h → recent action
3. get-funding-rate → sentiment
4. get-orderbook --depth 20 → liquidity
5. get-balance → capital
   ↓ analysis + recommendation
6. If confirmed → open-position (conservative sizing)
```

---

## Suggest Next Steps

After executing a command, suggest 2-3 relevant follow-ups conversationally (never expose command names):

| After | Suggest |
|---|---|
| Price check | View chart, check orderbook, open position |
| Kline | Check funding rate, view orderbook, run technical analysis |
| Positions | Check liquidation prices, review PnL, portfolio review |
| Balance | View positions, trade history, AI credits. If < 5 USDC → deposit |
| Open position | Set stop-loss, check liquidation price, view position |
| Trade history | PnL summary, fee summary |
| Funding rate | Arbitrage screen, view kline |
| Orderbook | Simulate slippage, open position |
| PnL summary | Review positions, fee breakdown, trade history |

---

## Domain Knowledge Thresholds

| Metric | Threshold | Interpretation |
|---|---|---|
| Spread (ask-bid)/mid | > 0.1% | Wide, use limit orders |
| Spread (ask-bid)/mid | > 0.5% | Very thin, high slippage |
| Orderbook depth (1%) | < $50k | Low liquidity |
| Orderbook depth (1%) | > $500k | Healthy |
| 24h volume | < $1M | Low activity |
| Funding rate (8h) | > 0.05% | Expensive longs |
| Funding rate (8h) | < -0.05% | Expensive shorts |
| Funding rate (8h) | > 0.1% | Extreme, potential arb |
| Leverage | > 5x | Elevated liq risk |
| Leverage | > 10x | High risk, warn strongly |
| Position / equity | > 30% | Concentration risk |
| Position / equity | > 50% | Dangerous |
| Liq distance | < 10% | Danger zone |
| Liq distance | < 5% | Critical |
| Order / 24h volume | > 5% | Market impact |
| Win rate | < 40% | Review strategy |
