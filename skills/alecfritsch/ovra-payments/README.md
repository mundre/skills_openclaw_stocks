# ovra-payments

Autonomous payments for AI agents with virtual Visa cards.

## What It Does

- **Buy anything online** — agent gets tokenized card data (DPAN + cryptogram), fills checkout forms or answers HTTP 402 paywalls
- **Policy-controlled spending** — per-agent limits, MCC blocks, time windows, geo restrictions
- **Real-time fraud detection** — 5-signal risk engine with auto-freeze
- **MPP/x402 compatible** — handles Machine Payment Protocol challenges natively
- **Zero card data exposure** — agents never see real card numbers

## Install

```bash
# OpenClaw
npx skills add AlecFritsch/ovra-skill

# Or manually: copy SKILL.md to your agent's skills directory
```

## Requirements

- [Ovra account](https://getovra.com) with API key
- MCP server: `npx -y @ovra/mcp`
- Configure with `OVRA_API_KEY` or `OVRA_AGENT_TOKEN`

## MCP Config

```json
{
  "mcpServers": {
    "ovra": {
      "command": "npx",
      "args": ["-y", "@ovra/mcp"],
      "env": {
        "OVRA_API_KEY": "sk_..."
      }
    }
  }
}
```

## Links

- [getovra.com](https://getovra.com) — Dashboard
- [@ovra/mcp on npm](https://www.npmjs.com/package/@ovra/mcp) — MCP Server
- [api.getovra.com](https://api.getovra.com) — API

## License

MIT
