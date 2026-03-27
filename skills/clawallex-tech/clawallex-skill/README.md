# Clawallex Skill

Pay for anything with USDC. Clawallex converts your stablecoin balance into virtual cards that work at any online checkout.

## Features

- **Flash Cards** — one-time use virtual cards for single payments
- **Stream Cards** — reloadable cards for subscriptions, top up with `refill`
- **Mode A** — pay from your USDC wallet balance
- **Mode B** — on-chain x402 payment for callers with self-custody wallets (agent or user) — signing is performed by the caller
- **Zero dependencies** — Python 3.9+ stdlib only

## Install

Copy the skill folder into your agent's skill directory:

```bash
git clone https://github.com/clawallex/clawallex-skill.git
```

## Quick Start

### 1. Get API Credentials

Sign up at [app.clawallex.com](https://app.clawallex.com) and create an API Key pair at **Settings > API Keys**.

### 2. Connect

```bash
python3 scripts/clawallex.py setup --action connect --api-key YOUR_KEY --api-secret YOUR_SECRET
```

### 3. Pay

```bash
# One-time payment
python3 scripts/clawallex.py pay --amount 50 --description "OpenAI API credits"

# Subscription
python3 scripts/clawallex.py subscribe --amount 100 --description "AWS monthly billing"

# Check balance
python3 scripts/clawallex.py wallet
```

## Commands

| Command | Description |
|---------|-------------|
| `setup` | Configure credentials |
| `whoami` | Check API Key binding status |
| `bootstrap` | Bind client_id to API Key |
| `pay` | Create a one-time flash card |
| `subscribe` | Create a reloadable stream card |
| `refill` | Top up a stream card |
| `wallet` | Check wallet balance |
| `recharge-addresses` | Get on-chain deposit addresses |
| `cards` | List virtual cards |
| `card-balance` | Check a card's balance |
| `card-details` | Get card PAN/CVV/expiry (encrypted) |
| `transactions` | View transaction history |
| `x402-address` | Get x402 on-chain payee address |

## For AI Agent Developers

See [SKILL.md](SKILL.md) for the full skill specification, including Mode B (x402 on-chain) flows, card data decryption, and agent integration details.

## License

MIT
