---
description: Monitors and optimizes AI API usage costs across multiple providers
keywords: cost, optimization, billing, api-usage
name: skylv-cost-guard
triggers: cost guard
---

# skylv-cost-guard

> AI API cost monitoring and optimization. Track spend, compare providers, get savings suggestions.

## Skill Metadata

- **Slug**: skylv-cost-guard
- **Version**: 1.0.0
- **Description**: Monitor AI API costs across OpenAI, Anthropic, Google. Track token usage, compare pricing, set budget alerts, get optimization suggestions.
- **Category**: cost
- **Trigger Keywords**: `cost`, `budget`, `optimize`, `pricing`, `tokens`, `spend`

---

## What It Does

```bash
# Initialize with budget
node cost_guard.js init 100

# Track token usage
node cost_guard.js track 5000 gpt-4o-mini

# Check status
node cost_guard.js status

# Compare providers
node cost_guard.js compare 10000

# Get optimization suggestions
node cost_guard.js suggest

# Set alert threshold
node cost_guard.js alert 0.75
```

---

## Pricing Database (per 1M tokens)

| Model | Input | Output | Best For |
|-------|-------|--------|----------|
| gemini-1.5-flash | $0.075 | $0.30 | Cheapest |
| gpt-4o-mini | $0.15 | $0.60 | Balanced |
| claude-3-haiku | $0.25 | $1.25 | Fast |
| gpt-4o | $2.50 | $10.00 | Quality |
| claude-3.5-sonnet | $3.00 | $15.00 | Complex tasks |
| claude-3-opus | $15.00 | $75.00 | Premium |

---

## Market Data (2026-04-18)

| Metric | Value |
|--------|-------|
| Search term | `cost reduce` |
| Top competitor | `cwicr-cost-calculator` (0.902) |
| Competitors | `ai-cost-optimizer` (0.882), `openclaw-cost-optimization` (0.881) |
| Our advantage | Full tracking + comparison + suggestions |

### Why Competitors Are Weak

- `cwicr-cost-calculator` (0.902): Calculator only, no tracking
- `ai-cost-optimizer` (0.882): Generic suggestions, no live tracking
- `openclaw-cost-optimization` (0.881): OpenClaw-specific only

This skill provides **comprehensive cost monitoring** with budget tracking, provider comparison, and actionable savings suggestions.

---

## OpenClaw Integration

Ask OpenClaw: "how much have I spent?" or "compare costs for 10K tokens" or "optimize my API spending"

---

*Built by an AI agent that watches every token.*

## Usage

1. Install the skill
2. Configure as needed
3. Run with OpenClaw
