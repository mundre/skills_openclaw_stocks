---
name: agnt-data
description: "Unified social data API for AI agents. One API key for LinkedIn, YouTube, TikTok, X, Instagram, Reddit, and Facebook."
version: 1.0.11
metadata:
  openclaw:
    requires:
      env:
        - AGNTDATA_API_KEY
      bins:
        - curl
    primaryEnv: AGNTDATA_API_KEY
    emoji: "\u26A1"
    homepage: https://agntdata.dev/docs
---

# agnt-data — Unified Social Data for AI Agents

One subscription, one API key, access to structured social data across seven platforms. No scraping infra, no managing upstream vendor accounts. Every response is structured JSON optimized for LLM and agent consumption.

## Recommended: Install the agnt-data Plugin

**For the best experience, install the agnt-data plugin instead of this skill.** The plugin provides:

- Native MCP tools for each platform (no curl required)
- Automatic authentication with browser-based login
- Structured tool schemas with full parameter validation
- Direct integration with your agent's tool system

**Master skill** (this bundle):

```bash
clawhub install agnt-data
```

**Master plugin** (all platforms; npm name matches generated `package.json`):

```bash
openclaw plugins install @agntdata/openclaw-agnt-data
```

For a single platform only, use that platform’s skill and plugin instead, for example:

```bash
clawhub install agntdata-facebook
openclaw plugins install @agntdata/openclaw-facebook
```

This skill is useful for environments where plugins are not supported, or when you need a lightweight reference.

## Authentication

Before making API calls, you need an API key. Get one from the [agntdata dashboard](https://app.agntdata.dev/dashboard).

The API key should be available as the `AGNTDATA_API_KEY` environment variable. Every request must include it as a Bearer token:

```
Authorization: Bearer $AGNTDATA_API_KEY
```

If the environment variable is not set, ask the user to provide their API key or direct them to https://app.agntdata.dev/dashboard to create one.

## API Key Activation

After setting your API key, activate it by calling the registration endpoint. This only needs to be done once per key:

```bash
curl -X POST https://api.agntdata.dev/v1/register \
  -H "Authorization: Bearer $AGNTDATA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"intendedApis": ["linkedin", "youtube"], "useCase": "Brief description of your use case"}'
```

Replace `intendedApis` with the platforms you plan to use, and `useCase` with a short description of how you plan to use the API.

## Discovery Endpoints

These public endpoints (no API key required) help you explore available platforms and their capabilities:

**List all platforms:**

```bash
curl https://api.agntdata.dev/v1/platforms
```

Returns: slug, name, endpoint count, and description for each platform.

**Get platform details:**

```bash
curl https://api.agntdata.dev/v1/platforms/{slug}
```

Returns: full endpoint list, OpenAPI spec, features, use cases, and documentation links.

Use these endpoints to discover capabilities before making authenticated API calls.

## Base URL

```
https://api.agntdata.dev/v1/{platform}
```

## Available APIs

| Platform | Slug | Endpoints | Description |
|----------|------|-----------|-------------|
| LinkedIn | `linkedin` | 52 | Enrich companies and profiles in real time. Designed for agents that need reliable structured data without managing dozens of vendor accounts. |
| YouTube | `youtube` | 22 | Unified access to video metadata, channel discovery, comments, subtitles, and recommendations. Built for LLMs and automation — not one-off scraping. |
| TikTok | `tiktok` | 12 | Unified access to video details, creator profiles, and search across accounts and videos. Built for LLMs and automation — not one-off scraping. |
| X (Twitter) | `x` | 52 | Unified access to tweets, user profiles, followers, search, and hashtag streams. Built for LLMs and automation — not one-off scraping. |
| Instagram | `instagram` | 22 | Unified access to user profiles, reels, explore, locations, and hashtag media. Built for LLMs and automation — not one-off scraping. |
| Reddit | `reddit` | 29 | Unified access to subreddit metadata, post threads, user activity, and search. Built for LLMs and automation — not one-off scraping. |
| Facebook | `facebook` | 35 | Unified access to page and group posts, marketplace listings, video content, and ad discovery. Built for LLMs and automation — not one-off scraping. |

## Choosing the Right API

- **B2B enrichment / sales intelligence** — use `linkedin`
- **Video content / creator intelligence** — use `youtube` or `tiktok`
- **Real-time social listening / trends** — use `x` or `reddit`
- **Visual content / influencer data** — use `instagram`
- **Pages, groups, marketplace, ads** — use `facebook`

## Example

```bash
curl -X GET 'https://api.agntdata.dev/v1/linkedin/get-company-details?username=microsoft' \
  -H 'Authorization: Bearer $AGNTDATA_API_KEY'
```

## Per-Platform Plugins

Install a platform-specific plugin for native MCP tools and detailed endpoint schemas:

- Skill: `clawhub install agntdata-linkedin` — Plugin: `openclaw plugins install @agntdata/openclaw-linkedin` — LinkedIn
- Skill: `clawhub install agntdata-youtube` — Plugin: `openclaw plugins install @agntdata/openclaw-youtube` — YouTube
- Skill: `clawhub install agntdata-tiktok` — Plugin: `openclaw plugins install @agntdata/openclaw-tiktok` — TikTok
- Skill: `clawhub install agntdata-x` — Plugin: `openclaw plugins install @agntdata/openclaw-x` — X (Twitter)
- Skill: `clawhub install agntdata-instagram` — Plugin: `openclaw plugins install @agntdata/openclaw-instagram` — Instagram
- Skill: `clawhub install agntdata-reddit` — Plugin: `openclaw plugins install @agntdata/openclaw-reddit` — Reddit
- Skill: `clawhub install agntdata-facebook` — Plugin: `openclaw plugins install @agntdata/openclaw-facebook` — Facebook

## Links

- [Dashboard](https://app.agntdata.dev/dashboard)
- [Documentation](https://agntdata.dev/docs)
- [ClawHub skill](https://clawhub.ai/agntdata/agnt-data)
