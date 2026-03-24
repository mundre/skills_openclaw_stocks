---
name: graph-advocate
description: "Ask any blockchain question in plain English — get token balances, DeFi analytics, NFT data, prediction market odds, and protocol stats instantly. Covers 15,500+ subgraphs across 20+ chains."
version: 1.3.0
homepage: https://github.com/PaulieB14/graph-advocate
metadata:
  clawdbot:
    emoji: "⛓️"
---

# Graph Advocate

Ask any blockchain question in plain English. Get back a ready-to-run query with the exact tool, parameters, and endpoint — no docs to read, no APIs to learn.

## Try it

- `"Who are the top 20 USDC holders on Ethereum?"`
- `"Show me Uniswap V3 pool TVL on Arbitrum"`
- `"What Aave liquidations happened this week?"`
- `"Get my wallet's token balances on Base"`
- `"Current Polymarket odds on the next Fed rate decision"`
- `"NFT sales on Solana in the last 24 hours"`

## What you get back

A structured JSON response with the exact tool call to run — no guessing:

```json
{
  "recommendation": "token-api",
  "reason": "getV1EvmHolders returns ranked holder lists by token contract.",
  "confidence": "high",
  "query_ready": {
    "tool": "getV1EvmHolders",
    "args": {
      "network_id": "mainnet",
      "contract": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
      "limit": 20
    }
  }
}
```

## What it knows about

| Data type | Examples | Chains |
|-----------|----------|--------|
| **Token balances & transfers** | Wallet holdings, whale tracking, top holders | Ethereum, Base, Polygon, Arbitrum, Solana, TON |
| **DEX & swaps** | Uniswap, Curve, Balancer pools, TVL, volume | 20+ EVM chains |
| **Lending & DeFi** | Aave deposits, borrows, liquidations, interest rates | 7 chains, 11 subgraphs |
| **NFTs** | Sales, transfers, collections, ownership, floor prices | EVM + Solana |
| **Prediction markets** | Polymarket odds, Predict.fun positions, trader P&L | Polygon, BNB Chain |
| **Raw block data** | Event logs, traces, streaming | Any EVM chain |
| **15,500+ protocol subgraphs** | ENS, Compound, Lido, MakerDAO, and more | Multi-chain |

## Works with these MCP packages

Graph Advocate recommends the right package and gives you install instructions:

| Package | What it does |
|---------|-------------|
| `graph-aave-mcp` | Aave V2/V3 lending data across 7 chains |
| `graph-polymarket-mcp` | Polymarket prediction market data — 20 tools |
| `graph-lending-mcp` | Cross-protocol lending comparisons |
| `predictfun-mcp` | Predict.fun markets on BNB Chain |
| `subgraph-registry-mcp` | Search 15,500+ subgraphs with reliability scores |
| `substreams-search-mcp` | Browse and inspect Substreams packages |

## Why use this instead of searching docs yourself?

- **One question, one answer** — no browsing 6 different API docs to figure out which service has your data
- **Ready-to-run** — returns the exact tool name, endpoint, and parameters, not just a suggestion
- **Always current** — knows about 15,500+ subgraphs including newly deployed ones
- **Covers the full stack** — Token API, Subgraph Registry, Substreams, and protocol-specific MCP servers in one place

## External Endpoints

| Endpoint | Data sent | Purpose |
|----------|-----------|---------|
| `https://graph-advocate-production.up.railway.app` | Your plain-English query | Routes to the right Graph Protocol service |
| `https://gateway.thegraph.com/api/` | GraphQL queries (when using subgraph tools) | Queries indexed blockchain data |
| `https://token-api.thegraph.com/` | REST requests (when using Token API tools) | Fetches token/NFT/swap data |

No data is stored server-side. Your query is processed and a routing recommendation is returned. The Railway endpoint logs request metadata (service chosen, confidence) but not query content.

## Security & Privacy

- **Instruction-only skill** — no code is downloaded or executed on your machine
- **No credentials required** — Graph Advocate does not need API keys from you
- **No local file access** — reads nothing from your filesystem
- **Stateless** — no session data persists between requests

## Model Invocation Note

This skill may be invoked autonomously by your AI agent when it detects a blockchain data question. This is standard MCP behavior. You can disable the skill at any time to opt out.

## Trust Statement

By using this skill, your plain-English data queries are sent to `graph-advocate-production.up.railway.app` (hosted on Railway, operated by @paulieb14). The service returns structured JSON routing recommendations. Only install if you trust this endpoint with your query text.

## Links

- GitHub: https://github.com/PaulieB14/graph-advocate
- The Graph Protocol: https://thegraph.com
- Token API: https://thegraph.com/docs/en/token-api
- Subgraph Studio: https://thegraph.com/studio
