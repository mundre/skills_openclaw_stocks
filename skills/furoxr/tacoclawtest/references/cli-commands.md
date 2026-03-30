# Taco CLI Commands Reference

All commands: `node scripts/taco_client.js <command> [options]`

Config defaults to `~/.openclaw/workspace/taco/config.json`. Override with `--config <path>`.

---

## Trading Commands

### open-position

```bash
node scripts/taco_client.js open-position \
  --symbol BTCUSDC --notional 100 --side Long \
  --leverage 3 --stop-loss 80000 --take-profit 100000
```

| Param | Required | Description |
|---|---|---|
| `--symbol` | Yes | Trading pair (e.g. BTCUSDC) |
| `--side` | Yes | `Long` or `Short` |
| `--notional` | Yes | Position size in USDC |
| `--leverage` | No | Leverage multiplier |
| `--stop-loss` | No | Stop-loss price |
| `--take-profit` | No | Take-profit price |
| `--limit-price` | No | Limit price for limit orders |

Returns: `order_id`, `symbol`, `side`, `status`, `notional`, `price`

**Post-execution error**: If fails with `User or API Wallet 0x... does not exist`, inform user to deposit USDC.

### close-position

```bash
node scripts/taco_client.js close-position \
  --symbol BTCUSDC --notional 100 --side Short
```

| Param | Required | Description |
|---|---|---|
| `--symbol` | Yes | Trading pair |
| `--side` | Yes | `Long` or `Short` |
| `--notional` | Yes | Size to close in USDC |
| `--limit-price` | No | Limit price |

### modify-order (NEEDS API)

```bash
node scripts/taco_client.js modify-order \
  --symbol BTCUSDC --order-id "12345" \
  --new-price 86000 --new-notional 150
```

Amends price and/or size. At least one of `--new-price` or `--new-notional` required.

### set-leverage

```bash
node scripts/taco_client.js set-leverage --symbol BTCUSDC --leverage 5
```

### set-margin-mode

```bash
node scripts/taco_client.js set-margin-mode --symbol BTCUSDC --cross
node scripts/taco_client.js set-margin-mode --symbol BTCUSDC  # isolated (default)
```

### adjust-margin (NEEDS API)

```bash
node scripts/taco_client.js adjust-margin --symbol BTCUSDC --amount 50 --action add
```

Params: `--symbol` (required), `--amount` (required, USDC), `--action` (required, `add`/`remove`)

### set-stop-loss / set-take-profit

```bash
node scripts/taco_client.js set-stop-loss --symbol BTCUSDC --side Long --notional 100 --price 85000
node scripts/taco_client.js set-take-profit --symbol BTCUSDC --side Long --notional 100 --price 95000
```

### Cancel orders

```bash
node scripts/taco_client.js cancel-stop-loss --symbol BTCUSDC
node scripts/taco_client.js cancel-take-profit --symbol BTCUSDC
node scripts/taco_client.js cancel-stops --symbol BTCUSDC
node scripts/taco_client.js cancel-all --symbol BTCUSDC
node scripts/taco_client.js cancel-order --symbol BTCUSDC --order-id "12345"
```

---

## Account Query Commands

### get-balance

```bash
node scripts/taco_client.js get-balance
```

Returns: `total_equity`, `available_balance`, `used_margin`, `unrealized_pnl` (all String, USDC)

### get-deposit-address

```bash
node scripts/taco_client.js get-deposit-address
```

Returns: `address` (same for all chains: Arbitrum, Ethereum, Base, Polygon)

### get-positions

```bash
node scripts/taco_client.js get-positions
```

Returns per position: `symbol`, `side`, `size`, `notional`, `entry_price`, `mark_price`, `unrealized_pnl`, `leverage`, `margin_mode`, `liquidation_price`

### get-open-orders

```bash
node scripts/taco_client.js get-open-orders
```

### get-filled-order

```bash
node scripts/taco_client.js get-filled-order --symbol BTCUSDC --order-id "12345"
```

Add `--algo` for algorithmic order IDs.

### get-trade-history (NEEDS API)

```bash
node scripts/taco_client.js get-trade-history --symbol BTCUSDC --limit 50 --start-time 1709251200000
```

Optional: `--symbol`, `--limit` (default 50, max 200), `--start-time`, `--end-time`, `--cursor`

Returns per trade: `trade_id`, `order_id`, `symbol`, `side`, `price`, `size`, `notional`, `fee`, `realized_pnl`, `timestamp`

### get-pnl-summary (NEEDS API)

```bash
node scripts/taco_client.js get-pnl-summary --period 7d --symbol BTCUSDC
```

Optional: `--period` (`1d`/`7d`/`30d`/`all`, default `7d`), `--symbol`

Returns: `realized_pnl`, `unrealized_pnl`, `funding_received`, `funding_paid`, `fees_paid`, `net_pnl`, `trade_count`, `win_rate`

### get-fee-summary (NEEDS API)

```bash
node scripts/taco_client.js get-fee-summary --period 30d
```

### get-credits (NEEDS API)

```bash
node scripts/taco_client.js get-credits
```

Returns: `free_credits` (Number)

### get-transfer-history (NEEDS API)

```bash
node scripts/taco_client.js get-transfer-history --limit 20 --type deposit
```

### get-liquidation-price (NEEDS API)

```bash
node scripts/taco_client.js get-liquidation-price --symbol BTCUSDC
```

Returns: `liquidation_price`, `margin_ratio`, `maintenance_margin`, `position_margin`

---

## Market Data Commands (No Auth)

### get-ticker (NEEDS API)

```bash
node scripts/taco_client.js get-ticker --symbol BTCUSDC
node scripts/taco_client.js get-ticker  # all tickers
```

Returns: `symbol`, `last_price`, `bid_price`, `ask_price`, `high_24h`, `low_24h`, `volume_24h`, `quote_volume_24h`, `change_24h`, `open_interest`

### get-kline

```bash
node scripts/taco_client.js get-kline --symbol BTCUSDC --interval 1h --start-time 1709251200000
```

Params: `--symbol` (required), `--interval` (required: `1m`/`3m`/`5m`/`15m`/`30m`/`1h`/`2h`/`4h`/`6h`/`8h`/`12h`/`1d`/`3d`/`1w`/`1M`), `--start-time`, `--end-time`

Returns per kline: `open_time`, `close_time`, `open`, `high`, `low`, `close`, `volume`, `quote_volume`, `trades_count`. Max 100 per request.

### get-orderbook (NEEDS API)

```bash
node scripts/taco_client.js get-orderbook --symbol BTCUSDC --depth 20
```

Returns: `bids` [[price, size], ...], `asks` [[price, size], ...], `timestamp`

### get-recent-trades (NEEDS API)

```bash
node scripts/taco_client.js get-recent-trades --symbol BTCUSDC --limit 50
```

### get-funding-rate (NEEDS API)

```bash
node scripts/taco_client.js get-funding-rate --symbol BTCUSDC
node scripts/taco_client.js get-funding-rate --symbol BTCUSDC --history --limit 24
```

Returns: `current_rate`, `predicted_next_rate`, `next_funding_time`, `annualized_rate`

### get-mark-price (NEEDS API)

```bash
node scripts/taco_client.js get-mark-price --symbol BTCUSDC
```

### get-symbols (NEEDS API)

```bash
node scripts/taco_client.js get-symbols --type perp
```

Returns per symbol: `symbol`, `base_asset`, `quote_asset`, `type` (`perp`/`spot`), `min_order_size`, `tick_size`, `max_leverage`, `status`
