---
name: strider-robinhood
description: Trade stocks via Robinhood using Strider Labs MCP connector. Buy and sell stocks, check portfolio, view watchlists, get market data. Complete autonomous investing for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "finance"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Robinhood Connector

MCP connector for trading on Robinhood — buy and sell stocks, check your portfolio, manage watchlists, and get market data. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-robinhood
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "robinhood": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-robinhood"]
    }
  }
}
```

## Available Tools

### robinhood.get_portfolio
Get current portfolio holdings and value.

**Output:**
```json
{
  "total_value": "number",
  "cash": "number",
  "positions": [{
    "symbol": "string",
    "shares": "number",
    "avg_cost": "number",
    "current_price": "number",
    "market_value": "number",
    "gain_loss": "number",
    "gain_loss_percent": "number"
  }]
}
```

### robinhood.get_quote
Get current stock quote.

**Input Schema:**
```json
{
  "symbol": "string"
}
```

**Output:**
```json
{
  "symbol": "string",
  "price": "number",
  "change": "number",
  "change_percent": "number",
  "volume": "number",
  "market_cap": "number"
}
```

### robinhood.place_order
Place a buy or sell order.

**Input Schema:**
```json
{
  "symbol": "string",
  "side": "string (buy or sell)",
  "quantity": "number",
  "order_type": "string (market, limit)",
  "limit_price": "number (for limit orders)"
}
```

### robinhood.get_orders
Get recent and pending orders.

### robinhood.cancel_order
Cancel a pending order.

### robinhood.get_watchlist
Get stocks on your watchlist.

### robinhood.add_to_watchlist
Add a stock to your watchlist.

### robinhood.get_buying_power
Check available cash for trading.

## Authentication

First use triggers OAuth. Trades require explicit user confirmation. Tokens stored encrypted per-user.

## Usage Examples

**Check portfolio:**
```
What's my Robinhood portfolio worth today?
```

**Buy stock:**
```
Buy 10 shares of Apple on Robinhood
```

**Get quote:**
```
What's the current price of NVIDIA?
```

**Sell position:**
```
Sell all my Tesla shares on Robinhood
```

**Add to watchlist:**
```
Add Microsoft to my Robinhood watchlist
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| INSUFFICIENT_FUNDS | Not enough buying power | Add funds or reduce |
| MARKET_CLOSED | Markets not open | Queue for market open |
| ORDER_REJECTED | Trade rejected | Check requirements |

## Security

- All trades require explicit confirmation
- No automated trading without user approval
- 2FA supported for account protection
- Order history for auditing

## Use Cases

- Portfolio management: track holdings
- Stock research: quick quotes and watchlists
- Trading: buy/sell individual stocks
- Cash management: check buying power

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-robinhood
- Strider Labs: https://striderlabs.ai
