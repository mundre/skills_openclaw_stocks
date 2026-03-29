---
name: youcom-web-search
description: you.com web search, deep research, and content extraction for OpenClaw. Free tier for basic search; research and extract require paid API key.
version: 1.0.1
triggers:
  - "you.com"
  - "youcom"
  - "search the web"
  - "look up"
  - "find online"
  - "web search"
  - "deep research"
  - "extract content"
  - "read this page"
metadata:
  clawdbot:
    emoji: "🔎"
    requires:
      bins: [python3]
    config:
      env:
        YOUCOM_API_KEY:
          description: "API key for you.com research and extract endpoints (optional for free search)"
          required: false
---

# you.com Web Search

Free web search, deep research, and content extraction — no mandatory API key for basic search.

## Tools

| Need | Tool | Cost | API Key |
|------|------|------|---------|
| General web search | `youcom_search` | Free | ❌ |
| Deep research with citations | `youcom_research` | Paid | ✅ |
| Extract content from URLs | `youcom_extract` | Paid | ✅ |

## Quick Start

### Free Search (no setup)
```bash
python3 scripts/youcom_search.py "search query" --num 5
```

### Research / Extract (requires API key)
```bash
export YOUCOM_API_KEY="your_key"
python3 scripts/youcom_research.py "topic" --depth deep
python3 scripts/youcom_extract.py https://example.com/article
```

## Setup

### Free Search
No setup required — `youcom_search` works immediately.

### Research & Extract (Paid)

1. Get an API key at [you.com/platform/api-keys](https://you.com/platform/api-keys)
2. Add to `~/.openclaw/.env`:
   ```
   YOUCOM_API_KEY=your_key_here
   ```
3. Restart the gateway: `systemctl --user restart openclaw-gateway`

## youcom_search — Free Web Search

Use for all general web searches. No API key needed.

```bash
python3 scripts/youcom_search.py "query" [--num N]
```

| Option | Description |
|--------|-------------|
| `query` | Search term (required) |
| `--num`, `-n` | Results to return, 1–10 (default: 5) |
| `--out`, `-o` | Write JSON to file instead of stdout |

**Output:** JSON with `query`, `count`, and `results[]` (title, url, description, snippets).

**Tips:**
- Supports search operators: `site:reddit.com`, `filetype:pdf`, `time:week`
- Results include social snippets when available
- Uses python3 `urllib` — no external dependencies

## youcom_research — Deep Research (Paid)

Synthesized answer with citations. Requires `YOUCOM_API_KEY`.

```bash
python3 scripts/youcom_research.py "topic" [--depth lite|standard|deep|exhaustive]
```

| Option | Description |
|--------|-------------|
| `query` | Research topic (required) |
| `--depth`, `-d` | lite, standard (default), deep, exhaustive |

**⚠️ Always confirm cost with user before using paid endpoints.**

## youcom_extract — Content Extraction (Paid)

Extract clean text from specific URLs. Requires `YOUCOM_API_KEY`.

```bash
python3 scripts/youcom_extract.py <url> [<url>...]
```

| Option | Description |
|--------|-------------|
| `urls` | One or more URLs (space-separated) |
| `--no-highlights` | Disable highlighted passages |

**Max 20 URLs per call.** Batch larger lists into multiple calls.

## When to Use What

| Need | Tool |
|------|------|
| Quick lookup | `youcom_search` |
| Comprehensive analysis | `youcom_research` |
| Specific page content | `youcom_extract` |
| Cloudflare/GitHub blocks | `youcom_search` — bypasses them |

## Escalation Order

```
youcom_search (free) → youcom_research (paid, confirm first) → youcom_extract (paid, confirm first)
```

When free search is insufficient, escalate to paid research.

## Troubleshooting

### "YOUCOM_API_KEY environment variable is not set"
The API key is not loaded. Source your `.env` or restart the gateway:
```bash
source ~/.openclaw/.env
systemctl --user restart openclaw-gateway
```

### "HTTP Error 401 / 403"
Invalid or expired API key. Check or regenerate at [you.com/platform/api-keys](https://you.com/platform/api-keys).

### "HTTP Error 429"
Rate limit hit. Wait 30 seconds and retry.

### "name or service not known"
DNS failure. Check internet connection.

## Python Dependencies

No third-party dependencies. Uses Python standard library only:
- `urllib.request` — HTTP GET/POST
- `urllib.parse` — URL encoding
- `json` — JSON parsing
- `argparse` — CLI argument parsing

## API Endpoints Used

| Tool | Method | Endpoint |
|------|--------|----------|
| `youcom_search` | GET | `https://api.you.com/v1/agents/search` |
| `youcom_research` | POST | `https://api.you.com/v1/agents/research` |
| `youcom_extract` | POST | `https://ydc-index.io/v1/contents` |
