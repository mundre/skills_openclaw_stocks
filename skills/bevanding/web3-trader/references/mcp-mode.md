# MCP Remote Mode Reference

## Workflow

```
User: "Swap 0.1 ETH to USDT"
      │
      ▼
┌─ Agent calls MCP swap-full ─────────────────┐
│  sell_token=ETH, buy_token=USDT,            │
│  sell_amount=0.1, taker=0xUserWallet        │
│  → returns quote + preview_url + tx         │
└────────────┬───────────────────────────────┘
             ▼
┌─ Agent sends message ───────────────────────┐
│  Trade preview + preview_url + QR code      │
└────────────┬───────────────────────────────┘
             ▼
User clicks link → Selects wallet → Signs tx
```

## swap-full Example

```json
{
  "tool": "swap-full",
  "arguments": {
    "sell_token": "ETH",
    "buy_token": "USDT",
    "sell_amount": "0.1",
    "taker": "0x81f9c401B0821B6E0a16BC7B1dF0F647F36211Dd"
  }
}
```

Returns:
```json
{
  "quote": {
    "sell_token": "ETH", "buy_token": "USDT",
    "sell_amount": "0.1", "buy_amount": "198.12",
    "min_buy_amount": "196.14", "price": "1981.22",
    "route": [{"source": "Blackhole_CL", "proportion": "100.0%"}]
  },
  "swap_page": {
    "preview_url": "https://mcp-skills.ai.antalpha.com/web3-trader/preview/<id>",
    "wallets_supported": ["MetaMask", "OKX Web3", "Trust Wallet", "TokenPocket"]
  },
  "tx": { "to": "0x000...734", "value": "100000000000000000", "data": "0x..." }
}
```

## QR Code Generation

```python
import qrcode
qr = qrcode.QRCode(box_size=10, border=3)
qr.add_data(preview_url)
qr.make(fit=True)
img = qr.make_image(fill_color='#00ffaa', back_color='#0a0e14')
img.save('/tmp/swap_qr.png')
```

Copy to `~/.openclaw/workspace/` for sending, delete after.

## Architecture

```
┌──────────────────┐     MCP JSON-RPC     ┌────────────────────────────┐
│   AI Agent       │ ────────────────────► │  Antalpha MCP Server       │
│   (OpenClaw)     │  swap-full            │  mcp-skills.ai.antalpha.com│
│                  │ ◄──────────────────── │  ├─ 0x API ─ DEX Agg.     │
└────────┬─────────┘  quote + preview_url  │  ├─ Page Gen ─ HTML       │
         │                                 │  └─ Hosting ─ URL         │
         ▼                                 └────────────────────────────┘
User clicks link / scans QR → Hosted page → Wallet signs → On-chain
```
