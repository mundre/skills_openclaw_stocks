---
name: lithtrix
description: >-
  Operate Lithtrix (lithtrix.ai) from an agent — self-serve API keys, credibility-scored web
  discovery, per-agent JSON memory, MCP tools, and free-tier referral rewards. Use when the user
  needs Lithtrix search, registration, memory, quotas, billing, or wiring Lithtrix into an agent
  runtime (Claude Desktop, OpenClaw, or custom HTTP).
version: 2.0.0
metadata:
  openclaw:
    requires:
      env:
        - LITHTRIX_API_KEY
      anyBins:
        - curl
    primaryEnv: LITHTRIX_API_KEY
    homepage: https://docs.lithtrix.ai
    emoji: "\U0001F30D"
---

# Lithtrix — agent infrastructure skill

## What this covers

[Lithtrix](https://lithtrix.ai) is **agent-native infrastructure**: HTTPS APIs for **web discovery** (credibility-scored results), **self-registration** (one-time `ltx_` API key), optional **persistent JSON memory** (KV, stats, context, semantic search when the host has vectors/embeddings), **usage metering**, **Stripe billing** for paid tiers, and an **MCP** server (`npx -y lithtrix-mcp`).

Use this skill when you should **discover**, **register**, **call search/memory**, **explain quotas or referrals**, or **configure MCP** — not for unrelated web search.

## When to load this skill

- The user mentions **Lithtrix**, **`ltx_` keys**, **`lithtrix.ai`**, **`lithtrix-mcp`**, or **agent-native search / memory**.
- You need a **credible web search API** with **no dashboard** (Bearer auth only after register).
- You need **per-agent memory** with optional **semantic recall** over stored JSON.
- You need to explain **free vs starter vs pro** limits or **referral bonuses** on the free tier.

## Canonical URLs (read-first)

| Resource | URL | Auth |
|----------|-----|------|
| Agent guide (ordered steps, JSON) | `https://lithtrix.ai/v1/guide` | None |
| Capabilities (endpoints, limits, scoring) | `https://lithtrix.ai/v1/capabilities` | Optional Bearer (see below) |
| LLM-oriented site summary | `https://lithtrix.ai/llms.txt` | None |
| OpenAPI 3.1 | `https://lithtrix.ai/openapi.json` | None |
| Human docs | `https://docs.lithtrix.ai` | None |
| Agent discovery | `https://lithtrix.ai/.well-known/ai-agent.json` | None |
| MCP tool JSON (search, register, memory, …) | `https://lithtrix.ai/mcp/*.json` | None |

**Base URL override (staging):** set `LITHTRIX_API_URL` (MCP and custom clients); default is `https://lithtrix.ai`.

## Quick start (three calls)

### 1. Discover

```bash
curl -sS "https://lithtrix.ai/v1/capabilities"
```

### 2. Register (one-time key — store immediately)

```bash
curl -sS -X POST "https://lithtrix.ai/v1/register" \
  -H "Content-Type: application/json" \
  -d '{"agent_name":"my-agent","owner_identifier":"owner@example.com"}'
```

Optional body field **`referral_agent`**: string = **referring agent’s UUID** (same value as their **`referral_code`** from `GET /v1/me`). Omit if unknown. Only **UUID-shaped** referrals count toward the referrer’s free-tier bonus.

### 3. Search (Bearer)

```bash
curl -sS "https://lithtrix.ai/v1/search?q=your+query" \
  -H "Authorization: Bearer ltx_your_key_here"
```

## Optional auth on `GET /v1/capabilities`

If you send a **valid** `Authorization: Bearer ltx_...` header, the JSON includes **`referral_rewards.your_referral_code`** (your agent UUID — same as `referral_code` from `GET /v1/me`). **Invalid or missing tokens still return HTTP 200**; the key is simply omitted. Unauthenticated responses remain backward compatible.

```bash
curl -sS "https://lithtrix.ai/v1/capabilities" \
  -H "Authorization: Bearer ltx_your_key_here"
```

## Referral programme (free tier)

- **`GET /v1/me`** (authenticated): always includes **`referral_code`** (your UUID to share). Includes **`referral_agent`** if you registered with a referrer.
- **Free tier:** lifetime web-discovery cap = **base (default 300) + 100 ×** (count of **other** agents whose `referral_agent` equals **your** UUID). **Self-referral excluded.** **Starter / Pro:** monthly search caps; **no** referral bonus on search limits.
- Effective cap is reflected in **`GET /v1/search`** → `usage.search_calls_limit` / `calls_remaining` for free agents.

## Memory (per-agent JSON)

After registration, use Bearer auth.

- **PUT** `/v1/memory/{key}` — store/update JSON (`value` required; optional `ttl`, `importance`, `source`, `confidence`)
- **GET** `/v1/memory/{key}` — read; **DELETE** `/v1/memory/{key}` — remove
- **GET** `/v1/memory` — list keys (paginated)
- **GET** `/v1/memory/stats` — ops + storage vs tier limits
- **GET** `/v1/memory/context` — top memories by importance/recency
- **GET** `/v1/memory/search?q=...` — semantic similarity over **your** memories (requires host vector + embedding configuration)

Key pattern: `[a-zA-Z0-9-_.:]{1,128}`. See OpenAPI and docs for response `usage` objects.

## MCP (Claude Desktop, OpenClaw, etc.)

Install and run via stdio (no global install required):

```bash
npx -y lithtrix-mcp
```

Set environment variable **`LITHTRIX_API_KEY`** to a valid `ltx_` key (obtain via **`lithtrix_register`** tool or `POST /v1/register`). Tools typically include search, register, and memory helpers — see tool definitions at `https://lithtrix.ai/mcp/` paths listed in `llms.txt` or OpenAPI extensions.

## Billing (paid tiers)

Upgrade path uses Stripe via API (see **`GET /v1/billing`**, **`GET /v1/billing/config`**, **`POST /v1/billing/setup`** in OpenAPI and Mintlify billing docs). Tiers: **Free**, **Starter**, **Pro** — limits differ for web discovery and memory; see **`/v1/capabilities`** and docs.

## Security and hygiene

- **Never** commit or paste raw `ltx_` keys into public repos, skills, or logs.
- Treat the API key like any secret: env vars, host credential stores, or secrets managers.
- Validate user-supplied URLs and payloads at your integration boundary; Lithtrix validates its own API inputs.

## Troubleshooting

| Symptom | Check |
|---------|--------|
| 401 on `/v1/search` | Missing/wrong `Authorization: Bearer ltx_...` |
| 409 on `/v1/register` | Same `agent_name` + `owner_identifier` already registered |
| Free tier “out of quota” | Lifetime total vs **effective** cap (includes referrals); inspect `usage` on search |
| Memory semantic search unavailable | Host must configure vector + embeddings (product limitation, not client bug) |

## Support

- Docs: `https://docs.lithtrix.ai`
- Email: `hello@lithtrix.ai`
- GitHub: `https://github.com/lithtrix`
