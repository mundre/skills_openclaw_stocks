---
name: strider-avis
description: Rent cars from Avis via Strider Labs MCP connector. Search availability, book rentals, modify reservations, and manage Avis Preferred status.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "travel"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Avis Connector

MCP connector for renting cars from Avis. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-avis
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "avis": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-avis"]
    }
  }
}
```

## Available Tools

### avis.search_vehicles
Search for available rental vehicles.

**Input Schema:**
```json
{
  "pickup_location": "string (airport code or address)",
  "pickup_date": "string (YYYY-MM-DD)",
  "pickup_time": "string (HH:MM)",
  "return_date": "string (YYYY-MM-DD)",
  "return_time": "string (HH:MM)",
  "vehicle_class": "Economy | Compact | Midsize | SUV | Luxury (optional)"
}
```

**Output:**
```json
{
  "vehicles": [
    {
      "class": "string",
      "make_model": "string",
      "daily_rate": "number",
      "total_price": "number",
      "features": ["string"],
      "availability": "string"
    }
  ]
}
```

### avis.book_rental
Book a rental car reservation.

### avis.modify_reservation
Change pickup/return dates or upgrade vehicle.

### avis.cancel_reservation
Cancel an existing reservation.

### avis.get_reservation
Retrieve reservation details by confirmation number.

### avis.get_preferred_status
Check Avis Preferred loyalty status and benefits.

## Authentication

First use triggers OAuth authorization flow:
1. User is redirected to Avis to authorize
2. Tokens are stored encrypted per-user
3. Automatic refresh handles token expiration

## Usage Examples

**Search for rentals:**
```
Find rental cars at LAX airport from March 15-18
```

**Book an SUV:**
```
Book an SUV from Avis at Denver airport, picking up Friday 2pm, returning Sunday 6pm
```

**Modify a reservation:**
```
Change my Avis reservation to return one day later
```

**Check Preferred status:**
```
What's my Avis Preferred status?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| NO_AVAILABILITY | Class unavailable | Search alternatives |
| RATE_LIMITED | Too many requests | Retry after delay |
| MODIFICATION_LOCKED | Cannot modify | Contact support |

## Use Cases

- Airport rentals: Pick up/drop off at major airports
- Business travel: Corporate rates with Avis Preferred
- Road trips: Multi-day rentals with unlimited mileage
- One-way rentals: Different pickup and return locations

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-avis
- Strider Labs: https://striderlabs.ai
- MCP Registry: https://registry.modelcontextprotocol.io
