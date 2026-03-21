---
name: strider-lowes
description: Shop Lowe's home improvement via Strider Labs MCP connector. Search products, check inventory, compare prices, and order building materials, tools, and appliances.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "retail"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Lowe's Connector

MCP connector for Lowe's home improvement shopping. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-lowes
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "lowes": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-lowes"]
    }
  }
}
```

## Available Tools

### lowes.search_products
Search Lowe's catalog for products.

**Input Schema:**
```json
{
  "query": "string",
  "category": "string (optional)",
  "brand": "string (optional)",
  "price_min": "number (optional)",
  "price_max": "number (optional)"
}
```

**Output:**
```json
{
  "products": [{
    "item_number": "123456",
    "name": "DeWalt 20V MAX Drill",
    "price": 149.00,
    "rating": 4.7,
    "reviews_count": 2341,
    "in_stock": true,
    "image_url": "https://..."
  }]
}
```

### lowes.check_store_inventory
Check product availability at local stores.

**Input Schema:**
```json
{
  "item_number": "string",
  "zip_code": "string",
  "radius_miles": "number (optional)"
}
```

### lowes.get_product_details
Get detailed product information.

**Input Schema:**
```json
{
  "item_number": "string"
}
```

### lowes.add_to_cart
Add item to shopping cart.

**Input Schema:**
```json
{
  "item_number": "string",
  "quantity": "number"
}
```

### lowes.checkout
Complete the purchase.

**Input Schema:**
```json
{
  "delivery_type": "pickup | delivery",
  "store_id": "string (for pickup)",
  "address": "object (for delivery)"
}
```

## Authentication

First use triggers OAuth authorization:
1. User redirected to Lowe's login
2. Tokens stored encrypted per-user
3. Automatic refresh handles expiration

No API key required — connector manages OAuth flow.

## Usage Examples

**Search for tools:**
```
Find cordless drills under $150 at Lowe's
```

**Check availability:**
```
Is the DeWalt drill in stock at my local Lowe's?
```

**Compare products:**
```
Compare Lowe's power washers by rating and price
```

**Order materials:**
```
Order 10 sheets of 4x8 plywood for delivery
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| OUT_OF_STOCK | Item unavailable | Check other stores |
| ITEM_NOT_FOUND | Invalid item number | Search again |
| DELIVERY_UNAVAILABLE | Can't deliver to address | Try pickup |

## Use Cases

- Project supplies: order lumber, drywall, and materials
- Tool shopping: compare and buy power tools
- Appliance purchase: shop washers, dryers, refrigerators
- Inventory check: verify stock before driving to store
- Pro purchasing: bulk orders for contractors

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-lowes
- Strider Labs: https://striderlabs.ai
