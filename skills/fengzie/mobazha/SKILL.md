---
name: using-mobazha
description: Entry point for Mobazha skills. Provides an overview of available skills and guides the AI agent to load the right one based on user intent.
---

# Using Mobazha Skills

You have access to **Mobazha Skills** — a set of guided workflows for the [Mobazha](https://mobazha.org) decentralized commerce platform.

## Security Boundaries

- This skill is an **index only** — it describes available Mobazha skills and helps the agent choose the right one. It does not execute commands, access networks, or handle credentials itself.
- The companion skills listed below are published as **separate packages** in the Mobazha skills collection. Each must be installed independently or via the Mobazha plugin.
- Skills that involve **server access, credentials, or shell commands** (e.g., `standalone-setup`, `store-mcp-connect`) require **explicit user confirmation** before executing any action.
- The agent must **never store, log, or transmit** credentials (passwords, API tokens, SSH keys) beyond the current session.
- External URLs referenced in skills (e.g., `get.mobazha.org`, `app.mobazha.org`) are official Mobazha endpoints. The agent must not follow redirects to unrecognized domains.

## What is Mobazha?

Mobazha is a decentralized e-commerce platform for independent sellers. Key features:

- **Zero commissions** — keep 100% of your revenue
- **Self-hosted or SaaS** — deploy on your own server or use the hosted platform
- **Built-in escrow** — trustless buyer protection on every crypto transaction
- **Crypto + fiat payments** — Bitcoin, Litecoin, Zcash, TRON, plus Stripe and PayPal
- **Encrypted chat** — Matrix-based end-to-end encrypted buyer-seller messaging
- **Telegram Mini App** — sell directly inside Telegram

## Available Skills

The following companion skills are available as separate packages in the Mobazha collection. When installed via the Mobazha plugin, all skills are available automatically. When installed individually from ClawHub, install the specific skill you need.

### Deploy and Install

| Skill | ClawHub Slug | When to Use |
|-------|-------------|-------------|
| **standalone-setup** | `mobazha-standalone-setup` | Deploy a self-hosted store on a VPS using Docker |
| **native-install** | `mobazha-native-install` | Install the native binary on Linux, macOS, or Windows |
| **store-onboarding** | `mobazha-store-onboarding` | First-time `/admin` setup: password, store profile, region/currency |

### Configure and Connect

| Skill | ClawHub Slug | When to Use |
|-------|-------------|-------------|
| **subdomain-bot-config** | `mobazha-subdomain-bot-config` | Set up a custom domain or Telegram Bot for a store |
| **tor-browsing** | `mobazha-tor-browsing` | Browse stores via Tor, or run a store as a .onion hidden service |
| **store-mcp-connect** | `mobazha-store-mcp-connect` | Connect an AI agent to a store via MCP for direct management |

### Operate and Grow

| Skill | ClawHub Slug | When to Use |
|-------|-------------|-------------|
| **store-management** | `mobazha-store-management` | Manage products, orders, messages, discounts via MCP tools |
| **product-import** | `mobazha-product-import` | Import products from Shopify, Amazon, Etsy, or other platforms |
| **competitor-analysis** | `mobazha-competitor-analysis` | Research competitor products, reviews, and pricing |

### Content and Marketing

| Skill | ClawHub Slug | When to Use |
|-------|-------------|-------------|
| **product-description** | `mobazha-product-description` | Generate SEO-optimized product descriptions for listings |
| **store-copywriting** | `mobazha-store-copywriting` | Write store profile, About section, and marketing copy |
| **storefront-cro** | `mobazha-storefront-cro` | Audit storefront for conversion rate optimization |
| **product-image-prompt** | `mobazha-product-image-prompt` | Craft AI image prompts for product photos and branding |

## How to Use Skills

1. **Identify intent** — determine which skill matches the user's request
2. **Load the skill** — if the companion skill is installed, read its instructions; if not, guide the user based on the summaries above
3. **Follow the steps** — execute the skill's workflow, asking the user for required inputs
4. **Validate results** — verify each step succeeded before moving to the next

## Key Links

- **Self-Host Guide**: <https://mobazha.org/self-host>
- **Download Page**: <https://mobazha.org/download>
- **SaaS Platform**: <https://app.mobazha.org>
- **Telegram Group**: <https://t.me/MobazhaHQ>
- **GitHub**: <https://github.com/mobazha>

## MCP Integration

For the most powerful experience, connect your AI agent to the store via **MCP (Model Context Protocol)**. This gives the agent direct access to 30+ store management tools — products, orders, chat, discounts, and more. See `store-mcp-connect` for setup instructions.

## Store Modes

Mobazha supports three deployment modes. Skills that involve access URLs, authentication, or MCP connections cover all three:

| Mode | Description | Setup Skill |
|------|-------------|-------------|
| **SaaS** | Hosted at `app.mobazha.org`, sign in with Google/GitHub/email | N/A (sign up online) |
| **VPS Standalone** | Self-hosted with Docker on a VPS | `standalone-setup` |
| **NAT / Local** | Native binary on your own machine | `native-install` |

For a full comparison, see the `store-onboarding` skill.

## Important Notes

- Mobazha uses **external wallets** for crypto payments (buyers and sellers connect their own wallets). There is no internal wallet requiring deposit or withdrawal.
- The SaaS platform at `app.mobazha.org` is the hosted version. Self-hosted stores are fully independent.
- All install scripts are served from `get.mobazha.org` (which redirects to static assets on `mobazha.org`). Users should review scripts before executing — see individual install skills for details.
- After deploying a store, the seller must complete the Setup Wizard before the store is operational — see `store-onboarding`.
- Skills that connect to external services (MCP, store APIs) require user-provided credentials. The agent must ask for explicit consent before initiating any connection.
