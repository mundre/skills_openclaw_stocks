---
name: strider-gmail
description: Send and manage Gmail via Strider Labs MCP connector. Compose emails, search inbox, manage labels, and handle drafts through the Gmail API.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "productivity"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Gmail Connector

MCP connector for Gmail operations via the Gmail API. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-gmail
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-gmail"]
    }
  }
}
```

## Available Tools

### gmail.send_email
Compose and send an email.

**Input Schema:**
```json
{
  "to": "string | string[]",
  "subject": "string",
  "body": "string (plain text or HTML)",
  "cc": "string[] (optional)",
  "bcc": "string[] (optional)",
  "attachments": "[{filename, content_base64}] (optional)"
}
```

### gmail.search_emails
Search inbox using Gmail query syntax.

**Input:**
```json
{
  "query": "string (e.g., 'from:boss@company.com is:unread')",
  "max_results": "number (optional, default 10)"
}
```

**Output:**
```json
{
  "emails": [{
    "id": "string",
    "from": "string",
    "to": "string[]",
    "subject": "string",
    "snippet": "string",
    "date": "string",
    "labels": ["string"]
  }]
}
```

### gmail.get_email
Retrieve full email content by ID.

### gmail.create_draft
Save an email as draft without sending.

### gmail.reply_to_email
Reply to an existing email thread.

### gmail.add_label / gmail.remove_label
Manage email labels for organization.

## Authentication

First use triggers OAuth authorization flow:
1. User is redirected to Google to authorize Gmail access
2. Tokens are stored encrypted per-user
3. Automatic refresh handles token expiration

No API key required — connector manages OAuth flow via Gmail API.

## Usage Examples

**Send a quick email:**
```
Send an email to john@example.com with subject "Meeting tomorrow" saying I'll be 10 minutes late
```

**Search for important messages:**
```
Search Gmail for unread emails from my manager in the last week
```

**Draft for later:**
```
Draft a follow-up email to the client about the proposal, don't send yet
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Gmail session expired | Re-authenticate |
| AUTH_MFA_REQUIRED | Google verification needed | Notify user |
| RATE_LIMITED | Gmail API quota exceeded | Retry after delay |
| INVALID_INPUT | Bad recipient or format | Check email format |

## Use Cases

- Email triage: search and organize inbox
- Quick replies: respond to messages without opening Gmail
- Scheduled sends: compose emails for later
- Bulk operations: apply labels or archive multiple emails

## Security Notes

- OAuth scopes are limited to email operations
- No access to other Google services through this connector
- Use @striderlabs/mcp-gcal for calendar operations

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-gmail
- Strider Labs: https://striderlabs.ai
- Gmail API: https://developers.google.com/gmail/api
