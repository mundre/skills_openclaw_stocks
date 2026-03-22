---
name: strider-wendys
description: Order from Wendy's via Strider Labs MCP connector. Browse menu, customize burgers and combos, schedule pickup or delivery, and earn Wendy's Rewards.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "food"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Wendy's Connector

MCP connector for Wendy's ordering. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-wendys
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "wendys": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-wendys"]
    }
  }
}
```

## Available Tools

### wendys.get_menu
Get menu for a location.

**Input Schema:**
```json
{
  "location_id": "string (optional)",
  "category": "burgers | chicken | salads | sides | drinks | breakfast (optional)"
}
```

**Output:**
```json
{
  "items": [{
    "item_id": "baconator",
    "name": "Baconator",
    "price": 8.99,
    "calories": 960,
    "description": "Two beef patties with bacon and cheese",
    "combo_price": 11.49
  }]
}
```

### wendys.find_nearby
Find Wendy's locations.

**Input Schema:**
```json
{
  "address": "string",
  "radius_miles": "number (optional)"
}
```

### wendys.add_to_order
Add item to order.

**Input Schema:**
```json
{
  "item_id": "string",
  "quantity": "number",
  "make_combo": "boolean",
  "customizations": ["no onions", "add bacon"]
}
```

### wendys.apply_deal
Apply available deals or offers.

**Input Schema:**
```json
{
  "deal_code": "string"
}
```

### wendys.place_order
Submit order for pickup or delivery.

**Input Schema:**
```json
{
  "order_type": "pickup | delivery | drive_thru",
  "location_id": "string",
  "scheduled_time": "string (optional)"
}
```

### wendys.get_rewards
Check Wendy's Rewards balance.

## Authentication

First use triggers OAuth authorization:
1. User redirected to Wendy's app login
2. Rewards linked automatically
3. Tokens stored encrypted per-user

No API key required — connector manages OAuth flow.

## Usage Examples

**Order a burger:**
```
Order a Baconator combo with a large frosty from Wendy's
```

**Use deals:**
```
What deals are available at Wendy's right now?
```

**Mobile pickup:**
```
Place a Wendy's order for drive-thru pickup in 15 minutes
```

**Check rewards:**
```
How many Wendy's reward points do I have?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| LOCATION_CLOSED | Store not open | Try different location |
| ITEM_UNAVAILABLE | Menu item out | Choose alternative |
| DEAL_EXPIRED | Offer no longer valid | Remove deal |

## Use Cases

- Quick meals: fast food ordering
- Combo deals: value meals with drinks and fries
- Mobile ordering: skip the line
- Rewards: earn and redeem points
- Late night: order from 24-hour locations

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-wendys
- Strider Labs: https://striderlabs.ai
