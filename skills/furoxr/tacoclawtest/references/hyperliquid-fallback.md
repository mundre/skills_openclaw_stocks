# Hyperliquid Public API Fallback

Use as fallback when Taco CLI commands fail or are marked "NEEDS API". Never mention "Hyperliquid" to the user.

## Base URL

`https://api.hyperliquid.xyz/info` — All requests are POST with JSON body. No API key needed.

## Endpoints

### Get all mid prices

```bash
curl -X POST https://api.hyperliquid.xyz/info \
  -H "Content-Type: application/json" \
  -d '{"type": "allMids"}'
```
Returns: `{"BTC": "87500.0", "ETH": "2150.0", ...}`

### Get L2 orderbook

```bash
curl -X POST https://api.hyperliquid.xyz/info \
  -H "Content-Type: application/json" \
  -d '{"type": "l2Book", "coin": "BTC"}'
```
Returns: `{"levels": [{"px": "87500.0", "sz": "1.5", "n": 3}, ...]}` for bids and asks.

### Get funding rates + metadata

```bash
curl -X POST https://api.hyperliquid.xyz/info \
  -H "Content-Type: application/json" \
  -d '{"type": "metaAndAssetCtxs"}'
```
Returns: metadata (asset list, max leverage) + per-asset context (funding rate, open interest, mark price, oracle price, 24h volume).

### Get candlestick / kline data

```bash
curl -X POST https://api.hyperliquid.xyz/info \
  -H "Content-Type: application/json" \
  -d '{"type": "candleSnapshot", "req": {"coin": "BTC", "interval": "1h", "startTime": 1709251200000, "endTime": 1709337600000}}'
```
Intervals: `1m`, `5m`, `15m`, `1h`, `4h`, `1d`. Returns OHLCV array.

### Get user state (positions + balance)

```bash
curl -X POST https://api.hyperliquid.xyz/info \
  -H "Content-Type: application/json" \
  -d '{"type": "clearinghouseState", "user": "0x..."}'
```
Returns: margin summary + positions array. Requires wallet address (0x...), not Taco user_id.

## Data Source Priority

| Data type | Primary source | Fallback |
|---|---|---|
| Current price | `get-ticker` | Hyperliquid `allMids` |
| Kline / candles | `get-kline` | Hyperliquid `candleSnapshot` |
| Orderbook | `get-orderbook` | Hyperliquid `l2Book` |
| Funding rate | `get-funding-rate` | Hyperliquid `metaAndAssetCtxs` |
| Mark price | `get-mark-price` | Hyperliquid `metaAndAssetCtxs` |
| Symbols | `get-symbols` | Hyperliquid `metaAndAssetCtxs` → `universe` |
| Positions / balance | `get-positions`, `get-balance` | Hyperliquid `clearinghouseState` (needs 0x address) |
| Trade history / PnL / AI credits | Taco API only | — |
| Open / close position | Taco API only | — |
