# Taco API Reference

## Base URL
`https://api.dev.taco.trading`

## Authentication
Authenticated endpoints require:
- Query parameter: `user_id`
- Header: `Authorization: Bearer <api_token>`
- Request body (POST): include `api_token` and `user_id`

---

## MARKET DATA (No Auth Required)

#### get_kline
- endpoint: /market/klines
- method: GET
- parameters:
    - query parameters:
        - symbol (required): trading pair symbol, e.g. `BTCUSDC`, `ETHUSDC`
        - interval (required): kline interval. Supported values: `1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `8h`, `12h`, `1d`, `3d`, `1w`, `1M`
        - start_time (optional): start time in Unix milliseconds
        - end_time (optional): end time in Unix milliseconds
- response:
  ```json
  {
    "base_response": { "status_code": 200, "status_msg": "success" },
    "klines": [
      {
        "symbol": "BTCUSDC",
        "interval": "1h",
        "open_time": 1709251200000,
        "close_time": 1709254800000,
        "open": "62345.50",
        "high": "62890.00",
        "low": "62100.00",
        "close": "62780.30",
        "volume": "1234.567",
        "quote_volume": "77012345.89",
        "trades_count": 45678
      }
    ]
  }
  ```
- notes: Maximum 100 klines per response. Prices as strings for decimal precision.


#### get_ticker 
- endpoint: /market/ticker
- method: GET
- parameters:
    - query parameters:
        - symbol (optional): trading pair. Omit for all tickers.
- expected response:
  ```json
  {
    "base_response": { "status_code": 200, "status_msg": "success" },
    "tickers": [
      {
        "symbol": "BTCUSDC",
        "last_price": "87500.00",
        "bid_price": "87499.50",
        "ask_price": "87500.50",
        "high_24h": "88200.00",
        "low_24h": "85100.00",
        "volume_24h": "12345.67",
        "quote_volume_24h": "1080000000.00",
        "change_24h": "2.35",
        "open_interest": "55000.00",
        "timestamp": 1709337600000
      }
    ]
  }
  ```


#### get_orderbook 
- endpoint: /market/orderbook
- method: GET
- parameters:
    - query parameters:
        - symbol (required): trading pair
        - depth (optional): number of levels per side, default 20, max 100
- expected response:
  ```json
  {
    "base_response": { "status_code": 200, "status_msg": "success" },
    "symbol": "BTCUSDC",
    "bids": [["87499.50", "12.5"], ["87499.00", "8.3"]],
    "asks": [["87500.50", "10.2"], ["87501.00", "15.7"]],
    "timestamp": 1709337600000
  }
  ```


#### get_recent_trades 
- endpoint: /market/recent_trades
- method: GET
- parameters:
    - query parameters:
        - symbol (required): trading pair
        - limit (optional): max trades, default 50, max 200
- expected response:
  ```json
  {
    "base_response": { "status_code": 200, "status_msg": "success" },
    "trades": [
      {
        "symbol": "BTCUSDC",
        "price": "87500.00",
        "size": "0.5",
        "side": "buy",
        "timestamp": 1709337600000
      }
    ]
  }
  ```


#### get_funding_rate 
- endpoint: /market/funding_rate
- method: GET
- parameters:
    - query parameters:
        - symbol (required): trading pair
        - history (optional): `true` for historical rates
        - limit (optional): number of periods for historical, default 8
- expected response:
  ```json
  {
    "base_response": { "status_code": 200, "status_msg": "success" },
    "symbol": "BTCUSDC",
    "current_rate": "0.0001",
    "predicted_next_rate": "0.00012",
    "next_funding_time": 1709352000000,
    "annualized_rate": "3.65",
    "history": [
      { "rate": "0.0001", "timestamp": 1709337600000 }
    ]
  }
  ```


#### get_mark_price 
- endpoint: /market/mark_price
- method: GET
- parameters:
    - query parameters:
        - symbol (required): trading pair
- expected response:
  ```json
  {
    "base_response": { "status_code": 200, "status_msg": "success" },
    "symbol": "BTCUSDC",
    "mark_price": "87500.00",
    "index_price": "87495.00",
    "last_price": "87500.50",
    "estimated_funding_rate": "0.0001"
  }
  ```


#### get_symbols 
- endpoint: /market/symbols
- method: GET
- parameters:
    - query parameters:
        - type (optional): `perp`, `spot`, or omit for all
- expected response:
  ```json
  {
    "base_response": { "status_code": 200, "status_msg": "success" },
    "symbols": [
      {
        "symbol": "BTCUSDC",
        "base_asset": "BTC",
        "quote_asset": "USDC",
        "type": "perp",
        "min_order_size": "0.001",
        "tick_size": "0.10",
        "max_leverage": 50,
        "status": "active"
      }
    ]
  }
  ```


---

## TRADING (Auth Required)

#### open_position
- endpoint: /auth/tacoclaw/trade/open_position
- method: POST
- parameters:
    - query parameters:
        - user_id: taco user id
    - request body:
      ```json
      {
        "api_token": "<bearer token>",
        "user_id": "<user_id>",
        "side": "Long",
        "symbol": "BTCUSDC",
        "notional_position": 100.0,
        "leverage": 3,
        "sl_price": 80000.0,
        "tp_price": 100000.0,
        "limit_price": 87000.0
      }
      ```
    - `leverage`, `sl_price`, `tp_price`, `limit_price` are optional.


#### close_position
- endpoint: /auth/tacoclaw/trade/close_position
- method: POST
- parameters:
    - query parameters:
        - user_id: taco user id
    - request body:
      ```json
      {
        "api_token": "<bearer token>",
        "user_id": "<user_id>",
        "symbol": "BTCUSDC",
        "notional_position": 100.0,
        "side": "Short",
        "limit_price": 88000.0
      }
      ```
    - `limit_price` is optional.


#### modify_order 
- endpoint: /auth/tacoclaw/trade/modify_order
- method: POST
- parameters:
    - query parameters:
        - user_id: taco user id
    - request body:
      ```json
      {
        "api_token": "<bearer token>",
        "user_id": "<user_id>",
        "symbol": "BTCUSDC",
        "order_id": "12345",
        "new_price": 86000.0,
        "new_notional_position": 150.0
      }
      ```
    - `new_price` and `new_notional_position` are both optional; at least one must be provided.


#### set_leverage
- endpoint: /auth/tacoclaw/trade/set_leverage
- method: POST
- parameters:
    - query parameters:
        - user_id: taco user id
    - request body:
      ```json
      {
        "api_token": "<bearer token>",
        "user_id": "<user_id>",
        "symbol": "BTCUSDC",
        "leverage": 5
      }
      ```


#### set_margin_mode
- endpoint: /auth/tacoclaw/trade/set_margin_mode
- method: POST
- parameters:
    - query parameters:
        - user_id: taco user id
    - request body:
      ```json
      {
        "api_token": "<bearer token>",
        "user_id": "<user_id>",
        "symbol": "BTCUSDC",
        "is_cross_margin": true
      }
      ```


#### adjust_margin 
- endpoint: /auth/tacoclaw/trade/adjust_margin
- method: POST
- parameters:
    - query parameters:
        - user_id: taco user id
    - request body:
      ```json
      {
        "api_token": "<bearer token>",
        "user_id": "<user_id>",
        "symbol": "BTCUSDC",
        "amount": 50.0,
        "action": "add"
      }
      ```
    - `action`: `add` or `remove`


#### set_stop_loss
- endpoint: /auth/tacoclaw/trade/set_stop_loss
- method: POST
- parameters:
    - query parameters:
        - user_id: taco user id
    - request body:
      ```json
      {
        "api_token": "<bearer token>",
        "user_id": "<user_id>",
        "symbol": "BTCUSDC",
        "side": "Long",
        "notional_position": 100.0,
        "price": 85000.0
      }
      ```


#### set_take_profit
- endpoint: /auth/tacoclaw/trade/set_take_profit
- method: POST
- parameters:
    - query parameters:
        - user_id: taco user id
    - request body:
      ```json
      {
        "api_token": "<bearer token>",
        "user_id": "<user_id>",
        "symbol": "BTCUSDC",
        "side": "Long",
        "notional_position": 100.0,
        "price": 95000.0
      }
      ```


#### cancel_stop_loss_orders
- endpoint: /auth/tacoclaw/trade/cancel_stop_loss_orders
- method: POST
- body: `{ "api_token", "user_id", "symbol" }`

#### cancel_take_profit_orders
- endpoint: /auth/tacoclaw/trade/cancel_take_profit_orders
- method: POST
- body: `{ "api_token", "user_id", "symbol" }`

#### cancel_stop_orders
- endpoint: /auth/tacoclaw/trade/cancel_stop_orders
- method: POST
- body: `{ "api_token", "user_id", "symbol" }`

#### cancel_all_orders
- endpoint: /auth/tacoclaw/trade/cancel_all_orders
- method: POST
- body: `{ "api_token", "user_id", "symbol" }`

#### cancel_order_by_order_id
- endpoint: /auth/tacoclaw/trade/cancel_order_by_order_id
- method: POST
- body: `{ "api_token", "user_id", "symbol", "order_id" }`


---

## ACCOUNT QUERIES (Auth Required)

#### get_positions
- endpoint: /auth/tacoclaw/trade/get_positions
- method: GET
- parameters:
    - query parameters:
        - user_id: taco user id

#### get_open_orders
- endpoint: /auth/tacoclaw/trade/get_open_orders
- method: GET
- parameters:
    - query parameters:
        - user_id: taco user id

#### get_balance
- endpoint: /auth/tacoclaw/trade/get_balance
- method: GET
- parameters:
    - query parameters:
        - user_id: taco user id

#### get_filled_order_by_order_id
- endpoint: /auth/tacoclaw/trade/get_filled_order_by_order_id
- method: GET
- parameters:
    - query parameters:
        - user_id: taco user id
        - symbol: trading pair
        - order_id: the order ID
        - is_algo_id (optional): true if order_id is an algo order ID


#### get_trade_history 
- endpoint: /auth/tacoclaw/trade/get_trade_history
- method: GET
- parameters:
    - query parameters:
        - user_id (required): taco user id
        - symbol (optional): filter by symbol
        - limit (optional): max records, default 50, max 200
        - start_time (optional): Unix ms
        - end_time (optional): Unix ms
        - cursor (optional): pagination cursor
- expected response:
  ```json
  {
    "base_response": { "status_code": 200, "status_msg": "success" },
    "trades": [
      {
        "trade_id": "t_123456",
        "order_id": "o_789",
        "symbol": "BTCUSDC",
        "side": "Long",
        "price": "87500.00",
        "size": "0.01",
        "notional": "875.00",
        "fee": "0.35",
        "realized_pnl": "12.50",
        "timestamp": 1709337600000
      }
    ],
    "next_cursor": "cursor_abc123",
    "has_more": true
  }
  ```


#### get_pnl_summary 
- endpoint: /auth/tacoclaw/account/get_pnl_summary
- method: GET
- parameters:
    - query parameters:
        - user_id (required)
        - period (optional): `1d`, `7d`, `30d`, `all`. Default `7d`
        - symbol (optional): filter by symbol
- expected response:
  ```json
  {
    "base_response": { "status_code": 200, "status_msg": "success" },
    "period": "7d",
    "realized_pnl": "1250.00",
    "unrealized_pnl": "-320.00",
    "funding_received": "15.00",
    "funding_paid": "-45.00",
    "fees_paid": "-180.00",
    "net_pnl": "720.00",
    "trade_count": 34,
    "win_rate": "0.62"
  }
  ```


#### get_fee_summary 
- endpoint: /auth/tacoclaw/account/get_fee_summary
- method: GET
- parameters:
    - query parameters:
        - user_id (required)
        - period (optional): `1d`, `7d`, `30d`, `all`. Default `30d`
- expected response:
  ```json
  {
    "base_response": { "status_code": 200, "status_msg": "success" },
    "period": "30d",
    "maker_fees": "-120.00",
    "taker_fees": "-380.00",
    "funding_fees_net": "-30.00",
    "total_fees": "-530.00",
    "fee_tier": "VIP1",
    "maker_rate": "0.0002",
    "taker_rate": "0.0005"
  }
  ```

#### get_credits
- endpoint: /auth/portfolio
- method: GET
- parameters:
    - query parameters:
        - user_id (required)
- expected response:
  ```json
  {
    "base_response": { "status_code": 200, "status_msg": "success" },
    "email": "email@abc.xyz",
    "free_credits": 30,
    "user_id": "did:privy:cmmn6zf1602ub0cl5016mwz2m"
  }
  ```

#### get_deposit_address
- endpoint: /auth/deposit/smart_wallet_address/get
- method: GET
- parameters:
    - query parameters:
        - user_id (required)
- expected response:
  ```json
  {
    "base_response": { "status_code": 200, "status_msg": "success" },
    "address": "0x123"
  }
  ```


#### get_transfer_history 
- endpoint: /auth/tacoclaw/account/get_transfer_history
- method: GET
- parameters:
    - query parameters:
        - user_id (required)
        - type (optional): `deposit`, `withdrawal`, or omit for all
        - limit (optional): max records, default 20
        - start_time (optional): Unix ms
        - end_time (optional): Unix ms
- expected response:
  ```json
  {
    "base_response": { "status_code": 200, "status_msg": "success" },
    "transfers": [
      {
        "transfer_id": "tf_001",
        "type": "deposit",
        "amount": "1000.00",
        "asset": "USDC",
        "status": "completed",
        "tx_hash": "0xabc...",
        "timestamp": 1709337600000
      }
    ]
  }
  ```

#### get_liquidation_price 
- endpoint: /auth/tacoclaw/trade/get_liquidation_price
- method: GET
- parameters:
    - query parameters:
        - user_id (required)
        - symbol (required): trading pair
- expected response:
  ```json
  {
    "base_response": { "status_code": 200, "status_msg": "success" },
    "symbol": "BTCUSDC",
    "side": "Long",
    "liquidation_price": "72500.00",
    "margin_ratio": "0.15",
    "maintenance_margin": "125.00",
    "position_margin": "875.00"
  }
  ```
