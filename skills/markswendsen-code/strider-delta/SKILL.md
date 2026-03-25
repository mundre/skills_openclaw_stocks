---
name: strider-delta
description: Book Delta Air Lines flights, check flight status, manage reservations, and access SkyMiles rewards via Strider Labs MCP connector. Search flights, select seats, and track real-time departure info.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "travel"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Delta Connector

MCP connector for Delta Air Lines booking, flight tracking, and SkyMiles management. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-delta
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "delta": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-delta"]
    }
  }
}
```

## Available Tools

### delta.search_flights
Search for available flights between destinations.

**Input Schema:**
```json
{
  "origin": "string (airport code)",
  "destination": "string (airport code)",
  "departure_date": "string (YYYY-MM-DD)",
  "return_date": "string (optional for one-way)",
  "passengers": "number",
  "cabin_class": "economy | premium | business | first"
}
```

**Output:**
```json
{
  "flights": [{
    "flight_number": "DL1234",
    "departure": "2024-03-22T08:00:00",
    "arrival": "2024-03-22T11:30:00",
    "duration": "3h 30m",
    "price": 249.00,
    "miles_price": 18500,
    "seats_available": 12
  }]
}
```

### delta.get_flight_status
Check real-time status of a specific flight.

**Input Schema:**
```json
{
  "flight_number": "string",
  "date": "string (YYYY-MM-DD)"
}
```

### delta.get_reservations
List upcoming reservations for the authenticated user.

### delta.select_seats
Select seats for a booked reservation.

**Input Schema:**
```json
{
  "confirmation_number": "string",
  "seat_preferences": [{
    "passenger": "string",
    "preference": "window | aisle | middle"
  }]
}
```

### delta.get_skymiles_balance
Check SkyMiles balance and Medallion status.

### delta.book_flight
Book a selected flight.

## Authentication

First use triggers OAuth authorization flow:
1. User is redirected to Delta to authorize
2. Tokens are stored encrypted per-user
3. Automatic refresh handles token expiration

No API key required — connector manages OAuth flow.

## Usage Examples

**Search for flights:**
```
Find Delta flights from LAX to JFK on March 25th for 2 passengers
```

**Check flight status:**
```
What's the status of Delta flight 1234 today?
```

**Book with miles:**
```
Book the 8am Delta flight to Atlanta using my SkyMiles
```

**Select seats:**
```
Select window seats for my Delta reservation ABCD12
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| FLIGHT_NOT_FOUND | Invalid flight/date | Verify flight number |
| SOLD_OUT | No seats available | Try alternate flights |
| RATE_LIMITED | Too many requests | Retry after delay |

## Use Cases

- Flight booking: search and book flights with cash or miles
- Trip management: view and modify reservations
- Status tracking: real-time departure and arrival info
- Seat selection: choose preferred seats
- Loyalty tracking: monitor SkyMiles balance and status

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-delta
- Strider Labs: https://striderlabs.ai
- MCP Registry: https://registry.modelcontextprotocol.io
