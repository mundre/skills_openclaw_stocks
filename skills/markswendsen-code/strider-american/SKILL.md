---
name: strider-american
description: Book American Airlines flights via Strider Labs MCP connector. Search flights, manage reservations, check in, and track AAdvantage miles.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "travel"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider American Airlines Connector

MCP connector for booking and managing American Airlines flights. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-american
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "american": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-american"]
    }
  }
}
```

## Available Tools

### american.search_flights
Search for available American Airlines flights.

**Input Schema:**
```json
{
  "origin": "string (airport code)",
  "destination": "string (airport code)",
  "departure_date": "string (YYYY-MM-DD)",
  "return_date": "string (optional)",
  "passengers": "number (default: 1)",
  "cabin_class": "Main | Business | First (optional)"
}
```

**Output:**
```json
{
  "flights": [
    {
      "flight_number": "string",
      "departure": "datetime",
      "arrival": "datetime",
      "duration": "string",
      "price": "number",
      "cabin": "string",
      "stops": "number",
      "aircraft": "string"
    }
  ]
}
```

### american.book_flight
Book a flight and create reservation.

### american.check_in
Check in for an upcoming flight (within 24 hours of departure).

### american.get_reservation
Retrieve reservation details by record locator.

### american.get_aadvantage_balance
Check AAdvantage miles balance and elite status.

### american.upgrade_request
Request an upgrade using miles or upgrade credits.

## Authentication

First use triggers OAuth authorization flow:
1. User is redirected to American Airlines to authorize
2. Tokens are stored encrypted per-user
3. Automatic refresh handles token expiration

## Usage Examples

**Search for flights:**
```
Find American Airlines flights from DFW to JFK next Tuesday
```

**Book a business class flight:**
```
Book a business class roundtrip on American from Chicago to Miami, December 15-18
```

**Check in:**
```
Check me in for my American flight tomorrow, record locator XYZABC
```

**Check miles:**
```
What's my AAdvantage miles balance and status?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| FLIGHT_SOLD_OUT | No seats available | Search alternatives |
| RATE_LIMITED | Too many requests | Retry after delay |
| UPGRADE_UNAVAILABLE | No upgrade inventory | Wait for availability |

## Use Cases

- Domestic travel: Extensive US route network with DFW hub
- International travel: Oneworld alliance global coverage
- Miles redemption: Book award flights with AAdvantage
- Business travel: Manage corporate bookings and upgrades

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-american
- Strider Labs: https://striderlabs.ai
- MCP Registry: https://registry.modelcontextprotocol.io
