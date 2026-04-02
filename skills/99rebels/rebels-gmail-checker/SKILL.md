---
name: gmail-checker
description: Check Gmail for unread inbox emails from the last 24 hours, filtered and prioritized. Use when asked to check emails, check inbox, email digest, email summary, or similar. Outputs a brief list sorted by priority. Skips marketing/promotions/social/update categories. Configurable via gmail-config.json.
---

# Gmail Checker

Fetch unread Gmail inbox messages, filter out noise, and deliver a prioritized digest.

## Setup

First-time users need Google OAuth credentials. If `~/.openclaw/credentials/gmail.json` doesn't exist, read [references/setup.md](references/setup.md) and walk the user through the setup flow.

**Dependencies:** `pip install google-api-python-client google-auth-oauthlib`

## How to Run

```bash
python3 <skill-path>/scripts/check_gmail.py [hours]
python3 <skill-path>/scripts/check_gmail.py --json [hours]
```

- Default: last 24 hours. Pass hours as argument for a different window.
- `--json` flag outputs structured JSON instead of plain text.
- Credentials: `~/.openclaw/credentials/gmail.json`
- Config (optional): `~/.openclaw/credentials/gmail-config.json` — copy from `config.example.json` and customize.

## Priority Rules

| Level | Criteria |
|-------|----------|
| HIGH | Sender domain matches `high_priority_domains` in config, or subject contains a `high_priority_keywords` match |
| MEDIUM | Gmail-labeled `CATEGORY_PERSONAL` |
| LOW | Everything else (still inbox, still unread) |

Filtered out entirely: labels in `labels_skip` config (defaults to promotions, updates, forums, social).

## Output Formatting

Present results cleanly for the current platform:
- **Slack/Discord:** Use bold, bullet points, section headers
- **WhatsApp:** Use `*bold*`, plain text, no markdown tables or headers
- **Terminal:** Plain text as-is from script output
