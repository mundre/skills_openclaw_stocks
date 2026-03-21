---
name: strider-gcal
description: Manage Google Calendar via Strider Labs MCP connector. Create, update, and delete events. Search availability, set reminders, and handle recurring meetings. AI agents can schedule on behalf of users.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "productivity"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Google Calendar Connector

MCP connector for Google Calendar management. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-gcal
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "gcal": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-gcal"]
    }
  }
}
```

## Available Tools

### gcal.create_event
Create a new calendar event.

**Input Schema:**
```json
{
  "title": "string",
  "start_time": "string (ISO 8601)",
  "end_time": "string (ISO 8601)",
  "description": "string (optional)",
  "location": "string (optional)",
  "attendees": ["email1@example.com", "email2@example.com"],
  "reminders": [{"method": "email", "minutes": 30}]
}
```

**Output:**
```json
{
  "event_id": "abc123xyz",
  "html_link": "https://calendar.google.com/event?eid=...",
  "status": "confirmed"
}
```

### gcal.get_events
List events within a date range.

**Input Schema:**
```json
{
  "start_date": "string (YYYY-MM-DD)",
  "end_date": "string (YYYY-MM-DD)",
  "calendar_id": "string (optional, defaults to primary)"
}
```

### gcal.find_availability
Find free time slots for scheduling.

**Input Schema:**
```json
{
  "date": "string (YYYY-MM-DD)",
  "duration_minutes": "number",
  "start_hour": "number (0-23, optional)",
  "end_hour": "number (0-23, optional)"
}
```

### gcal.update_event
Modify an existing event.

**Input Schema:**
```json
{
  "event_id": "string",
  "title": "string (optional)",
  "start_time": "string (optional)",
  "end_time": "string (optional)",
  "location": "string (optional)"
}
```

### gcal.delete_event
Remove an event from calendar.

**Input Schema:**
```json
{
  "event_id": "string",
  "send_notifications": "boolean (optional)"
}
```

### gcal.list_calendars
Get all calendars accessible to the user.

## Authentication

Uses Google OAuth 2.0:
1. First use opens Google authorization
2. User grants calendar access
3. Tokens stored encrypted per-user
4. Automatic refresh when tokens expire

No API key required — connector manages OAuth flow.

## Usage Examples

**Schedule a meeting:**
```
Schedule a team standup tomorrow at 9am for 30 minutes
```

**Find availability:**
```
Find a free hour next Tuesday for a client call
```

**Check schedule:**
```
What meetings do I have this week?
```

**Reschedule:**
```
Move my 3pm meeting to 4pm
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Google session expired | Re-authenticate |
| CALENDAR_NOT_FOUND | Invalid calendar ID | Check calendar list |
| TIME_CONFLICT | Overlapping event | Find different time |
| RATE_LIMITED | Too many requests | Retry after delay |

## Use Cases

- Meeting scheduling: create and manage calendar events
- Availability check: find free time slots for booking
- Event reminders: set up notifications before events
- Recurring events: schedule weekly/monthly meetings
- Shared calendars: manage team calendars

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-gcal
- Strider Labs: https://striderlabs.ai
- Google Calendar API: https://developers.google.com/calendar
