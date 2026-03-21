---
name: strider-alaska
description: Book Alaska Airlines flights via Strider Labs MCP connector. Search flights, manage reservations, check in, and track Mileage Plan rewards.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "travel"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Alaska Airlines Connector

MCP connector for booking and managing Alaska Airlines flights. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-alaska
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "alaska": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-alaska"]
    }
  }
}
```

## Available Tools

### alaska.search_flights
Search for available Alaska Airlines flights.

**Input Schema:**
```json
{
  "origin": "string (airport code)",
  "destination": "string (airport code)",
  "departure_date": "string (YYYY-MM-DD)",
  "return_date": "string (optional)",
  "passengers": "number (default: 1)",
  "cabin_class": "Main | First | Premium (optional)"
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
      "stops": "number"
    }
  ]
}
```

### alaska.book_flight
Book a flight and add to reservation.

### alaska.check_in
Check in for an upcoming flight (within 24 hours of departure).

### alaska.get_reservation
Retrieve details of an existing reservation by confirmation code.

### alaska.get_mileage_balance
Check Mileage Plan miles balance and status.

### alaska.cancel_reservation
Cancel a flight reservation.

## Authentication

First use triggers OAuth authorization flow:
1. User is redirected to Alaska Airlines to authorize
2. Tokens are stored encrypted per-user
3. Automatic refresh handles token expiration

## Usage Examples

**Search for flights:**
```
Find Alaska Airlines flights from SEA to LAX next Friday
```

**Book a roundtrip:**
```
Book a roundtrip Alaska flight from Seattle to San Francisco, leaving Monday returning Wednesday
```

**Check in:**
```
Check me in for my Alaska flight tomorrow, confirmation code ABCDEF
```

**Check miles:**
```
What's my Alaska Mileage Plan balance?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| FLIGHT_SOLD_OUT | No seats available | Search alternatives |
| RATE_LIMITED | Too many requests | Retry after delay |
| CHECK_IN_TOO_EARLY | Not within 24 hours | Wait until window opens |

## Use Cases

- West Coast travel: Alaska's hub network covers Pacific Northwest and California
- Miles redemption: Use Mileage Plan points for award flights
- Business travel: Manage corporate bookings and check-ins
- Multi-city trips: Book complex itineraries with connections

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-alaska
- Strider Labs: https://striderlabs.ai
- MCP Registry: https://registry.modelcontextprotocol.io
