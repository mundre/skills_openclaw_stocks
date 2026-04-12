---
name: playasia
version: 0.1.3
kind: capability-manifest
visibility: public
auth_required: false
purpose: discovery-only
cacheable: true
description: Search and buy digital game codes, eShop cards, PSN vouchers from Play-Asia.com via HTTP. Three purchase methods — Wallet (instant), Lightning (instant), Bitcoin on-chain. No account needed for Bitcoin/Lightning.
homepage: https://www.play-asia.com/l402
metadata: {"openclaw":{"requires":{"env":["PA_TOKEN"]},"primaryEnv":"PA_TOKEN"}}
---

> **Public discovery document** — safe to read, index, and cache.
> No authentication required. Does not perform purchases or access user data.
> Authentication applies only to transactional endpoints listed below.

# Playasia API

Buy digital game codes, eShop cards, PSN vouchers, and more via direct HTTP calls. No MCP server needed.

## Base URL

```
https://www.play-asia.com/l402/v1
```

## No token needed for browsing!

- `GET /l402/v1/catalog` — **FREE**, no auth, no login, no token
- `GET /l402/v1/price?pax={PAX}` — **FREE**, no auth, no login, no token
- `GET /l402/v1/info` — **FREE**, returns full API docs as JSON
- `GET /l402/v1/skill` — **FREE**, this document

You do NOT need a token to browse, search, or check prices. No authentication. No account. No purchases are performed by reading this document.

## How purchases work

### Option 1: Wallet balance (instant, needs token with purchase scope)
```
POST /l402/v1/buy  {"pax":"PAX0004012102"}
+ Header: X-PA-Token: pa_xxx

→ Instantly returns the digital code if sufficient balance.
```

### Option 2: Lightning Network (instant, no account)
```
POST /l402/v1/buy  {"pax":"PAX0004012102", "method":"lightning"}
→ Returns Lightning invoice + order_id + status_url

Pay the invoice with any Lightning wallet.
The digital code is delivered instantly.
```

### Option 3: Bitcoin on-chain (no account)
```
POST /l402/v1/buy  {"pax":"PAX0004012102", "method":"bitcoin"}
→ Returns Bitcoin address + amount + order_id + status_url

Send BTC to the address. ~20 min for 2 confirmations.
Poll status_url for delivery:
GET /l402/v1/order?oid={order_id}&order_sid={order_sid}
→ Once confirmed, the digital code appears in the response.
```

**Important:** For anonymous Bitcoin/Lightning orders, save the `order_sid` and `order_id` from the response to retrieve your code later.

## Authentication

| Need | Auth | How |
|------|------|-----|
| Search catalog | None | Free, no token needed |
| Check prices | None | Free, no token needed |
| Buy with Lightning | None | Anonymous |
| Buy with Bitcoin | None | Anonymous, track via `order_sid` |
| Buy with wallet | `X-PA-Token` | Needs `purchase` scope |
| Check balance/orders | `X-PA-Token` | Any scope |
| Support tickets | `X-PA-Token` | Any scope |

Get a token at: https://www.play-asia.com/account/access-tokens

**Passing the token** (any of these work):
- Header: `X-PA-Token: pa_xxx` (preferred)
- Header: `Authorization: Bearer pa_xxx`
- POST body field: `{"token":"pa_xxx", ...}` (for agents that cannot set headers)

## Endpoints

### Browse (free, no auth)

- `GET /l402/v1/catalog?q={query}&limit={n}&offset={n}&currency={code}&affiliate_id={id}` — Search products. When `affiliate_id` is provided, each product includes a `url` field with the affiliate tracking link.
- `GET /l402/v1/price?pax={PAX}` — Get product price

### Buy + Order

- `POST /l402/v1/buy` — **With token**: wallet buy. **Without**: anonymous BTC/LN. Body: `{"pax":"PAX...", "method":"lightning|bitcoin"}`
- `GET /l402/v1/order?oid={id}` — **With token**: order by customer. **With `&order_sid=...`**: anonymous access. Includes `payment_detected` for unpaid orders.

### Wallet (requires X-PA-Token)

- `GET /l402/v1/account/balance` — Wallet balance (USD + sats)
- `GET /l402/v1/account/transactions?limit={n}&offset={n}` — Transaction history
- `POST /l402/v1/account/topup` — Wallet top-up. Body: `{"amount":25.00}`. Optional: `"method":"bitcoin"|"lightning"` for direct crypto payment.
- `GET /l402/v1/account/orders?limit={n}&offset={n}` — List orders

### Customer Service (requires X-PA-Token)

- `POST /l402/v1/cs/submit` `{"subject":"...","message":"...","reference":"#ORDER_ID"}` — Open ticket
- `GET /l402/v1/cs/enquiries?status=open` — List tickets
- `GET /l402/v1/cs/enquiry?id={id}` — Ticket thread
- `POST /l402/v1/cs/reply` `{"ticket_id":123,"message":"..."}` — Reply
- `POST /l402/v1/cs/close` `{"ticket_id":123}` — Close ticket

### Bitcoin / Lightning tools (L402 protocol)

- `GET /l402/v1/btc/rates` — BTC/fiat rates (30+ currencies, 1 sat)
- `GET /l402/v1/btc/blockheight` — Block height (1 sat)
- `GET /l402/v1/btc/fees` — Fee estimates (1 sat)
- `GET /l402/v1/btc/mempool` — Mempool stats (1 sat)
- `GET /l402/v1/ln/decode-invoice?invoice={bolt11}` — Decode invoice (2 sats)
- `GET /l402/v1/ln/node-info` — Node info (1 sat)

## Error handling

| HTTP | Error | Action |
|------|-------|--------|
| 400 | `missing_pax`, `invalid_method` | Fix request parameters |
| 401 | `unauthorized` | Add X-PA-Token header |
| 402 | `insufficient_balance` | Top up wallet or use anonymous buy |
| 402 | L402 payment required | Pay the returned invoice |
| 403 | `scope_denied`, `limit_raise_denied` | Token lacks permission |
| 404 | `not_found` | Product not found or not digital |
| 429 | `rate_limited`, `too_many_pending` | Wait and retry |

## Rate limits

- Purchases: 30/hr (wallet), 10/hr per IP (anonymous)
- Max 3 unpaid anonymous orders per IP
- Token creation: 5/hr
- CS submit: 10/hr, CS reply: 20/hr

No signup. No account. No KYC. Just Bitcoin.
