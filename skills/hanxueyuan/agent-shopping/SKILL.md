---
name: agent-shopping
description: "Agent-powered smart shopping assistant"
metadata:
  { "openclaw": { "emoji": "🛒", "version": "0.1.0", "author": "hanxueyuan", "tags": ["shopping","agent-commerce","shopping"] } }
---

# 🛒 Agent Shopping

Agent-powered smart shopping assistant

## What It Does

Search products, compare prices, and purchase items through AI agent conversations. Supports natural language queries like 'find me a USB-C cable under $10' and returns structured product recommendations with buy links.

## Usage

When the user mentions buying, purchasing, shopping, or looking for product deals, this skill activates to help find the best options.

### Example Prompts

- "Find me the best deal on [product]"
- "Compare prices for [product] across platforms"
- "Is there a coupon for [product]?"
- "Help me buy [product] under [budget]"

## Configuration

Set up API credentials in environment variables as needed for each supported platform.

## Architecture

```
User Request → Intent Parser → Product Search API → Result Ranker → Recommendation Display
```

## Roadmap

- v0.1: Basic product search via web search
- v0.2: Platform API integration
- v0.3: Price tracking and alerts
- v1.0: Full autonomous purchasing flow

## Author

Created by hanxueyuan as part of the Agent Commerce initiative.
License: MIT
