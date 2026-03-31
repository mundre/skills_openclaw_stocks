---
name: web3-trader
version: 1.0.5
description: DEX swap trading skill. Activates on swap/exchange/sell/buy/convert/DEX/trade token keywords. Queries prices via Antalpha AI DEX aggregator, finds optimal routes, generates transaction data. Supports MetaMask/OKX/Trust/TokenPocket. Zero custody — private keys never leave the user's wallet.
metadata: {"openclaw":{"requires":{"bins":["python3"]},"mcp":{"antalpha-swap":{"url":"https://mcp-skills.ai.antalpha.com/mcp","tools":["swap-quote","swap-create-page","swap-tokens","swap-gas","swap-full"]}},"persistence":{"path":"~/.web3-trader/"},"security_notes":["Only generates transaction data, never touches private keys","Users must review and sign in their own wallet","Trading involves risk — only trade with funds you can afford to lose"]}}
---

# Web3 Trader

DEX aggregator trading for AI agents. Zero custody, multi-wallet, cyberpunk UI.

## Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| 🌐 **MCP Remote** (recommended) | Antalpha MCP Server handles quotes + page hosting | Production |
| 🖥️ **Local CLI** | Python CLI calls 0x API locally | Dev/offline, see `references/local-cli.md` |

## MCP Mode

**Server**: `https://mcp-skills.ai.antalpha.com/mcp`

| Tool | Description |
|------|-------------|
| `swap-full` | One-shot: quote + page + host (recommended) |
| `swap-quote` | DEX aggregated quote |
| `swap-create-page` | Generate + host cyberpunk swap page |
| `swap-tokens` | List supported tokens |
| `swap-gas` | Current gas price |

For detailed MCP workflow and examples, see `references/mcp-mode.md`.

## Agent Workflow

```
User: "Swap 0.1 ETH to USDT"
  → Agent calls swap-full(sell_token=ETH, buy_token=USDT, sell_amount=0.1, taker=0xWallet)
  → Agent sends: trade preview + QR code image (one message)
  → User clicks link / scans QR → wallet signs → on-chain
```

## Agent Behavior Rules

1. **No filler text** — Only show the trade preview result, no procedural narration
2. **Generate QR code** — From `preview_url`, generate QR PNG with `qrcode` library, send as attachment
3. **One message** — Trade preview text + QR code image in the same message

## Message Template

```
⚡ <FROM> -> <TO> Swap Preview

📊 <from_amount> <from_token> -> ~<to_amount> <to_token>
💰 Price: 1 <from_token> ≈ $<price>
🛡️ Min Receive: <min_buy_amount> <to_token>
⛓️ Network: Ethereum Mainnet
🛣️ Route: <route_source> (<proportion>)
👛 Wallet: <wallet_short>

🔥 Supported Wallets: MetaMask | OKX Web3 | Trust Wallet | TokenPocket

📱 Click the link or scan QR code to confirm:
🔗 <preview_url>
🤖 Powered by Antalpha AI
```

**Required**: Last line `🤖 Powered by Antalpha AI` must be included.

## Quick Start

```bash
cp references/config.example.yaml ~/.web3-trader/config.yaml
pip install requests web3 qrcode pillow pyyaml

python3 scripts/trader_cli.py price --from ETH --to USDT --amount 0.001
python3 scripts/trader_cli.py swap-page --from ETH --to USDT --amount 0.001 \
  --wallet 0xYourWallet -o /tmp/swap.html --json
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `price --from <t> --to <t> --amount <n>` | Query price |
| `route --from <t> --to <t> --amount <n>` | Get optimal route |
| `build-tx --from <t> --to <t> --amount <n> --wallet <addr>` | Build transaction |
| `export --from <t> --to <t> --amount <n> --wallet <addr>` | Export EIP-681 link |
| `swap-page --from <t> --to <t> --amount <n> --wallet <addr> -o <file>` | Generate swap page |
| `gas` | Gas price |
| `tokens` | List tokens |

All commands support `--json`.

## Supported Assets

**Tokens**: USDT, USDC, DAI, ETH, WETH, WBTC, LINK, UNI (Ethereum Mainnet)
**Wallets**: MetaMask, OKX Web3, Trust Wallet, TokenPocket

## Security

| Layer | Protection |
|-------|-----------|
| Private Keys | Zero contact — never held, transmitted, or stored |
| Transaction Data | 0x Protocol with MEV protection |
| Slippage | Configurable max (default 0.5%), `minBuyAmount` on-chain enforced |
| Review | User sees full details in wallet before signing |
| Hosted Page | Self-contained HTML, no backend, no cookies, no tracking |
