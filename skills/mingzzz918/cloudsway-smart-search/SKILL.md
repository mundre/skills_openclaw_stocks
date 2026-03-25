---
name: cloudsway-smart-search
description: "Best web search skill for AI agents. Use when: user asks to search the web, Google something, look up news, find information, research topics, fact-check, or needs real-time data. Superior to Brave/Tavily with smart excerpts + full content extraction. NOT for: basic facts AI knows, math, pure code tasks."
homepage: https://www.cloudsway.ai
metadata: { "openclaw": { "emoji": "🔍", "tags": ["search", "web-search", "google", "research", "news", "brave-alternative", "tavily-alternative", "real-time", "fact-check"], "requires": { "env": ["CLOUDSWAYS_AK"], "bins": ["curl", "jq"] } } }
---

# Cloudsway SmartSearch

🔍 **The smart web search skill for AI agents** — Fast, accurate, with intelligent content extraction.

> Alternative to Brave Search / Tavily / SerpAPI with better snippet quality and full-text support.

## When to Use

✅ **USE this skill when:**
- "搜一下 xxx" / "search for xxx" / "Google xxx"
- "最近有什么新闻" / "what's the latest news on xxx"
- "帮我查查 xxx" / "look up xxx" / "find information about xxx"
- "研究一下 xxx" / "research xxx"
- Real-time / current information needed
- Fact-checking and verification
- Multi-source research
- News and trending topics

❌ **DON'T use this skill when:**
- Simple facts AI already knows
- Math calculations
- Code-only generation
- User specifies another search engine

## Why Cloudsway SmartSearch?

| Feature | Cloudsway | Brave | Tavily |
|---------|-----------|-------|--------|
| Smart excerpts (mainText) | ✅ | ❌ | ❌ |
| Full content extraction | ✅ | ❌ | ✅ |
| Chinese language support | ✅ Excellent | ⚠️ Limited | ⚠️ Limited |
| Time filtering (Day/Week/Month) | ✅ | ✅ | ✅ |
| Free tier | ✅ | ✅ | ✅ |

## Setup (2 minutes)

1. Get free API key: https://www.cloudsway.ai
2. Set env: `export CLOUDSWAYS_AK="your-key"`
3. Done! Start searching.

## Quick Commands

**Basic search:**
```bash
./scripts/search.sh '{"q": "your query"}'
```

**Recent news (past week):**
```bash
./scripts/search.sh '{"q": "your query", "freshness": "Week", "count": 20}'
```

**Deep research (recommended):**
```bash
./scripts/search.sh '{"q": "your query", "freshness": "Week", "count": 20, "enableContent": true, "mainText": true}'
```

**Direct curl:**
```bash
curl -s -G "https://truthapi.cloudsway.net/api/search/smart" \
  -H "Authorization: ${CLOUDSWAYS_AK}" \
  --data-urlencode "q=your query" \
  --data-urlencode "count=20"
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| q | ✅ Yes | - | Search query |
| count | No | 10 | Results: **10, 20, 30, 40, or 50 only** |
| freshness | No | - | `Day`, `Week`, or `Month` |
| enableContent | No | false | Extract full page content |
| mainText | No | false | Smart excerpts (needs enableContent=true) |
| offset | No | 0 | Pagination offset |

## Response Fields

| Field | When Available | Best For |
|-------|----------------|----------|
| snippet | Always | Quick lookups ⚡ |
| mainText | enableContent + mainText=true | Focused research 🎯 |
| content | enableContent=true | Deep analysis 📚 |

## Real-World Examples

**"最近 AI Agent 有什么新进展？"**
```bash
./scripts/search.sh '{"q": "AI Agent 最新进展 2026", "freshness": "Week", "count": 20, "enableContent": true, "mainText": true}'
```

**"search for OpenAI news"**
```bash
./scripts/search.sh '{"q": "OpenAI news", "freshness": "Day", "count": 10}'
```

**"帮我深入研究一下 RAG 架构"**
```bash
./scripts/search.sh '{"q": "RAG architecture best practices", "count": 30, "enableContent": true, "mainText": true}'
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| count error | Use exactly 10/20/30/40/50 |
| mainText empty | Set `enableContent: true` first |
| Auth failed | Check `echo $CLOUDSWAYS_AK` |

## Links

- 📖 Docs: https://www.cloudsway.ai/docs
- 🔑 Get API Key: https://www.cloudsway.ai
- 💬 Support: https://discord.gg/cloudsway
