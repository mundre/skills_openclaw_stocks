---
name: reivo
description: LLM proxy that cuts API costs 40-60% via smart model routing. Tracks spending, enforces budgets, detects loops, auto-stops runaway agents. Supports OpenAI, Anthropic, Google. One base URL change to install.
homepage: https://reivo.dev
user-invocable: true
metadata: {"openclaw": {"emoji": "🦞", "homepage": "https://reivo.dev", "requires": {"env": ["REIVO_API_KEY"]}, "envVars": [{"name": "REIVO_API_KEY", "required": true, "description": "Reivo API key (starts with rv_). Get at reivo.dev/settings"}], "author": "tazsat0512", "links": {"homepage": "https://reivo.dev", "repository": "https://github.com/tazsat0512/reivo", "documentation": "https://reivo.dev/llms-full.txt"}}}
---

# Reivo — LLM Cost Optimizer

## What it does

- Routes each LLM request to the cheapest model that can handle it (40-60% cost reduction)
- Tracks cost per session, agent, and model in real time
- Enforces budget limits — blocks requests when the limit is reached
- Detects agent loops using prompt hashing and similarity analysis — auto-stops runaway agents
- Verifies output quality via logprob analysis — auto-retries with the original model if quality drops
- Works with OpenAI, Anthropic, and Google via a single base URL change

## Commands

| Command | Description |
|---------|-------------|
| `/reivo status` | Check proxy connectivity and show dashboard link |
| `/reivo month` | Monthly cost and savings summary |
| `/reivo defense` | View budget usage, loop detection, and blocked request stats |
| `/reivo optimize` | Show cost optimization recommendations (cache, max_tokens, unused tools) |
| `/reivo budget [amount]` | View current budget or set a new monthly cap (e.g. `/reivo budget 50`) |
| `/reivo slack [url]` | Configure Slack webhook for budget/loop/anomaly alerts |
| `/reivo mode` | Info on changing routing mode (auto/conservative/aggressive) |
| `/reivo on` | Info on enabling Smart Routing |
| `/reivo off` | Info on disabling Smart Routing |
| `/reivo share` | Generate a link to your dashboard |

## Setup

### Quick (interactive)

```bash
npx clawhub@latest install reivo
node setup.js
```

The interactive setup walks you through:
1. API key validation
2. Provider key configuration (OpenAI, Anthropic, Google)
3. Monthly budget cap
4. Slack webhook for alerts

### Manual

1. Sign up at [reivo.dev](https://reivo.dev) and generate an API key
2. Set the environment variable:

```bash
export REIVO_API_KEY="rv_your_reivo_key"
```

3. Run `/reivo status` to confirm connectivity

## Configuration

All configuration is accessible from the CLI:

- **Provider keys:** Set during `setup.js` or in the [dashboard](https://app.reivo.dev/settings)
- **Budget:** `/reivo budget 50` to set a $50/month cap
- **Slack alerts:** `/reivo slack https://hooks.slack.com/...`
- **Routing mode:** Via [dashboard](https://app.reivo.dev/settings) (auto, conservative, aggressive, off)

### LLM Provider Keys

Provider API keys (OpenAI, Anthropic, Google) are encrypted and stored on Reivo's servers. They are never logged or exposed. Configure them during setup or in the dashboard.

## Requirements

- Reivo account (free tier: 10,000 requests/month)
- At least one LLM provider API key configured

## Links

- Website: https://reivo.dev
- GitHub: https://github.com/tazsat0512/reivo
- Dashboard: https://app.reivo.dev
