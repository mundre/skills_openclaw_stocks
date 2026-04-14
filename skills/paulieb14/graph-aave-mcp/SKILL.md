---
name: graph-aave-mcp
description: Aave V2/V3/V4 MCP server — 40 tools across 16 Graph subgraphs + Aave V4 API. Covers reserves, positions, cross-chain liquidation risk monitoring, governance, V4 hubs/spokes, exchange rates, swap quotes, rewards, and protocol history.
version: 4.0.7
author: PaulieB14
tags: [aave, defi, lending, liquidation-risk, thegraph, subgraph, mcp, ethereum]
env:
  GRAPH_API_KEY:
    description: "API key for The Graph network. Free at https://thegraph.com/studio/ (100K queries/month)."
    required: true
---

# graph-aave-mcp

MCP server for Aave V2, V3, and V4 — 40 tools across 16 Graph subgraphs + the Aave V4 API.

## Setup

Install the npm package globally, then run it:

```bash
npm install -g graph-aave-mcp
graph-aave-mcp
```

Or add to Claude Code:
```bash
claude mcp add graph-aave -- graph-aave-mcp
```

Set your Graph API key (free at https://thegraph.com/studio/):
```bash
export GRAPH_API_KEY=your-key-here
```

## What it does

- **V2/V3** (16 tools): Reserves, positions, liquidations, borrows, supplies, flash loans, governance across 11 subgraphs on 7 chains (Ethereum, Arbitrum, Base, Polygon, Optimism, Avalanche)
- **Liquidation Risk** (8 tools): Cross-chain health factors, risk scores, risk alerts, at-risk positions across 5 chains
- **V4 API** (16 tools): Hubs, spokes, reserves, exchange rates, user positions, activities, swap quotes, claimable rewards

## Example questions

- "What are the top Aave V3 markets on Ethereum by TVL?"
- "Compare WETH borrow rates across all chains"
- "Which positions are at risk of liquidation on Arbitrum?"
- "Show me Aave V4 hub utilization"
- "Is wallet 0x... at risk of liquidation on any chain?"

## Links

- npm: https://www.npmjs.com/package/graph-aave-mcp
- GitHub: https://github.com/PaulieB14/graph-aave-mcp
