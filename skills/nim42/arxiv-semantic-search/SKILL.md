---
name: arxiv-semantic-search
description: Semantic arXiv search for AI agents. Ask complex research questions and get ranked papers with summaries, metadata, and source links, powered by RobinSignal.
metadata:
    version: 0.1.0
    category: research
    display_name: ArXiv Semantic Search
    provider: RobinSignal
    origin: https://www.robinsignal.com
    query_api_base: https://www.robinsignal.com/api/v1
---

# ArXiv Semantic Search

ArXiv Semantic Search is an agent skill for discovering arXiv papers with semantic search, structured filters, ranked results, summaries, metadata, and original source links.

This skill is powered by the RobinSignal API. RobinSignal provides the underlying account, verification, API key, quota, and query services. RobinSignal may support other skills or products; this skill focuses on arXiv-first research discovery. It can also search selected technical articles when the human explicitly asks for industry writing or cross-source technology context.

## When To Use This Skill

Use this skill when the human wants an AI agent to find, rank, summarize, or monitor research papers, especially arXiv papers.

This skill is especially useful when the human asks complex semantic questions, not just keywords.

Good uses:

- Discover arXiv papers about a research idea, technique, benchmark, method, or trend.
- Find recent or historical arXiv papers matching nuanced constraints.
- Search papers by author, institution, lab, company, or research area.
- Compare research directions across related topics.
- Find papers connected to an industry trend or technical article.
- Track what is newly appearing in a field over time.
- Retrieve high-signal paper results with summaries, metadata, and source links.

Use this skill for technical articles only when the human explicitly asks for:

- Industry engineering blog posts.
- Technical writing from companies, labs, or research organizations.
- Cross-source context combining arXiv papers and technical articles.

Do not use this skill for:

- General web browsing outside RobinSignal's covered sources.
- Static facts, common knowledge, or questions that do not need research/source discovery.
- Full-text PDF reading, unless the API result itself provides the needed content or link.
- Claims that require verification but cannot be supported by returned source links.
- Non-research news, casual browsing, or broad internet search.

## Query Style

Prefer rich natural-language queries. This skill is designed for complex semantic search and ranked retrieval, so agents should not reduce every request to a few keywords.

Good query examples:

```text
Recent arXiv papers on retrieval-augmented generation for code agents, especially methods that evaluate long-horizon tasks
```

```text
Papers that compare long-context models with RAG for scientific question answering
```

```text
Recent diffusion model papers with open-source code and real-world robotics applications
```

```text
Papers from Stanford or Google DeepMind about inference-time scaling or reasoning models
```

```text
What are the most relevant recent papers about model routing, mixture-of-experts, and dynamic inference?
```

Guidelines:

- Preserve the user's semantic intent.
- Include constraints such as field, task, method, evaluation setting, author, institution, or recency when available.
- Use `scope: "paper"` by default for this skill.
- Use `scope: "article"` only when the human asks for technical articles or industry writing.
- Use `scope: "all"` only when the human asks for cross-source context across papers and articles.
- Prefer one precise query over multiple vague queries.
- Use multiple queries only when the human asks for multiple distinct topics or comparisons.

## Skill Files

| File                 | URL                                    |
| -------------------- | -------------------------------------- |
| skill.md (this file) | `https://www.robinsignal.com/skill.md` |
| homepage             | `https://www.robinsignal.com/`         |
| login page           | `https://www.robinsignal.com/login`    |

Read this file directly, or save it locally if your runtime prefers local skill files.

Canonical origin: `https://www.robinsignal.com`

Query API base: `https://www.robinsignal.com/api/v1`

IMPORTANT:

- This is the ArXiv Semantic Search skill, powered by RobinSignal.
- Prefer the canonical origin above when constructing RobinSignal URLs.
- Send RobinSignal API keys only in the `x-api-key` header.
- Never ask a human for their Google or Apple credentials.
- Never send a RobinSignal API key to any third party, webhook, log sink, or unrelated tool.
- If a human does not yet have an API key, use the verification flow below. Do not invent a different onboarding flow.

## Human-Assisted API Key Flow

The human may start with this instruction:

```text
Read https://www.robinsignal.com/skill.md and follow the instructions to use ArXiv Semantic Search.
```

Once a human asks you to use ArXiv Semantic Search or RobinSignal and you do not already have a valid API key, do this:

1. Call `POST /key/apply`.
2. Send the returned `loginUrl` to the human.
3. Tell the human to sign in and copy the verification code shown by RobinSignal after sign-in.
4. Ask the human to paste that verification code back to you.
5. Call `POST /key/verify` with the original `requestId` and the pasted code.
6. Store the returned `apiKey` securely for future RobinSignal requests.

Use a message like this when you send the human the sign-in link:

```text
Please open this RobinSignal sign-in link:
<loginUrl>

After you sign in, RobinSignal will show a 5-character verification code.
Paste that code back here and I will finish setup for ArXiv Semantic Search.
```

## Step 1: Create A Key Request

```bash
curl -X POST https://www.robinsignal.com/key/apply
```

Response:

```json
{
    "expiresAt": "2026-04-11T12:30:00.000Z",
    "loginUrl": "/login?flow=key-apply&request=53cfdc49-f861-4f2d-bf26-8b7738f0e61e",
    "requestId": "53cfdc49-f861-4f2d-bf26-8b7738f0e61e"
}
```

Notes:

- `requestId` is the stable ID for this key application.
- The key application stays valid for 30 minutes.
- `loginUrl` is relative. Prefix it with `https://www.robinsignal.com` before sending it to the human if your runtime wants absolute URLs.

## What The Human Will Do

When the human opens `loginUrl`, RobinSignal uses its first-party web flow:

- `/login?flow=key-apply&request=...` starts or resumes the key-apply sign-in flow.
- If the human is already signed in, RobinSignal may send them directly to a verification screen such as `/verify?request=...`.
- If the human is not signed in, RobinSignal will show Google and/or Apple sign-in options.
- After sign-in, RobinSignal issues a 5-character verification code on that verification screen.
- The verification code is short-lived, bound to the original `requestId`, and can only be used once.

Important timing and format rules:

- The verification code expires after 10 minutes.
- The verification code format is 5 uppercase characters.
- Every newly issued code invalidates the previous one for the same `requestId`.
- Never ask the human for cookies or provider credentials. Only ask for the verification code.

## Step 2: Exchange The Verification Code For The Real API Key

```bash
curl -X POST https://www.robinsignal.com/key/verify \
  -H "Content-Type: application/json" \
  -d '{
    "requestId": "53cfdc49-f861-4f2d-bf26-8b7738f0e61e",
    "verificationCode": "A1B2C"
  }'
```

Response:

```json
{
    "apiKey": "ag_created-key"
}
```

Verification failure semantics:

- `401` means the verification code is invalid.
- `404` means the key request does not exist.
- `409` means the key request was already used, is bound to another account, or sign-in has not been completed yet.
- `410` means the key request or verification code expired.
- `403` means the account is disabled.

## Optional Persistent Installation

If your runtime supports persistent reusable skills, it is recommended to save or install this document as a local ArXiv Semantic Search skill after setup succeeds.

Guidelines:

- Keep this document as reusable skill instructions, not as a credential file.
- Do not store the RobinSignal API key inside the skill file.
- Store the API key in your runtime's secret store, credential manager, or secure connection settings.
- Treat `https://www.robinsignal.com/skill.md` as the canonical source when you need to refresh or reinstall the skill.
- If persistent installation is not supported, reuse this document as a per-session instruction source instead.

## Authentication

All agent API calls after verification use `x-api-key`, not `Authorization: Bearer ...`.

Example:

```bash
curl https://www.robinsignal.com/api/v1/quota \
  -H "x-api-key: YOUR_API_KEY"
```

Notes:

- RobinSignal API keys currently start with `ag_`.
- Keep the key secret. Treat it like a password.
- RobinSignal sets `X-Request-Id` on responses. Keep it for debugging and support.

## Query API

General rules:

- Successful and failed query responses are forwarded from the upstream query service as JSON whenever possible.
- `GET /api/v1/quota` is local to RobinSignal and returns RobinSignal's own quota summary.
- `lang`, if provided, must be `chs` or `eng`.
- `pageSize`, if provided, must be an integer from `1` to `50`.
- `after` and `cursor`, if provided, must be UUIDs.
- For this skill, default to `scope: "paper"` whenever the endpoint supports `scope`.

### Endpoint Selection Guide

Do not send every query to `POST /api/v1/search`.

Use the most specific endpoint that matches the user's intent:

- Use `POST /api/v1/search` for open-ended semantic arXiv paper discovery, complex natural-language research questions, or exploratory queries.
- Use `POST /api/v1/by-author` when the user is asking about papers by a specific researcher or author.
- Use `POST /api/v1/by-institution` when the user is asking about papers from a specific company, lab, university, or organization.
- Use `GET /api/v1/areas` when you first need to discover the supported area taxonomy before choosing area filters.
- Use `POST /api/v1/by-area` when the user is asking about one or more named domains, topics, or coverage areas and those areas can be expressed explicitly.

Scope rules:

- For arXiv paper search, use `scope: "paper"` where supported.
- For technical articles or industry writing, use `scope: "article"` where supported.
- For cross-source research context, use `scope: "all"` where supported.
- `POST /api/v1/by-area` does not currently take a `scope` parameter. If the human explicitly wants only arXiv papers and area filtering is less important than source type, prefer `POST /api/v1/search` with `scope: "paper"` and include the area in the query.

Recommended routing patterns:

- If the human says "find recent arXiv papers about inference-time scaling", prefer `POST /api/v1/search` with `scope: "paper"`.
- If the human says "find papers by Geoffrey Hinton", prefer `POST /api/v1/by-author` with `scope: "paper"`.
- If the human says "show me OpenAI papers about reasoning models", prefer `POST /api/v1/by-institution` with `scope: "paper"`.
- If the human says "search within robotics and AI", consider `GET /api/v1/areas` then `POST /api/v1/by-area`, or use `POST /api/v1/search` with `scope: "paper"` if arXiv-only scope matters.
- If the human says "compare papers and company posts about long-context agents", use `POST /api/v1/search` with `scope: "all"`.

Why this matters:

- This skill should behave like an arXiv-first research discovery tool.
- Structured endpoints communicate intent more clearly.
- Semantic search should preserve complex research intent instead of reducing it to keywords.
- Using the right scope avoids returning technical articles when the human asked for papers.

### GET /health

Minimal availability check.

```bash
curl https://www.robinsignal.com/health
```

Response:

```json
{
    "ok": true
}
```

### GET /api/v1/quota

Returns your currently available total balance.

```bash
curl https://www.robinsignal.com/api/v1/quota \
  -H "x-api-key: YOUR_API_KEY"
```

Response:

```json
{
    "refreshAt": "2026-04-27T00:00:00.000Z",
    "total": 5
}
```

Notes:

- `total` is `credits + points`.
- `refreshAt` is the next weekly credit refresh time, or `null` if no future refresh is currently scheduled.
- This endpoint does not consume quota.
- This endpoint does not go through the user RPM limiter.

### GET /api/v1/areas

Lists available areas from the upstream query service.

```bash
curl https://www.robinsignal.com/api/v1/areas \
  -H "x-api-key: YOUR_API_KEY"
```

Notes:

- This request costs 1 quota unit.
- The response body is forwarded from the upstream query service.

### POST /api/v1/search

Semantic search across RobinSignal sources. For this skill, this is the main endpoint for complex arXiv paper discovery.

Required JSON body fields:

- `queries`: array of 1 to 12 non-empty strings
- `scope`: `paper`, `article`, or `all`

Optional JSON body fields:

- `after`: UUID
- `cursor`: UUID
- `lang`: `chs` or `eng`
- `pageSize`: integer 1 to 50
- `maxCosineDistance`: number greater than 0 and less than or equal to 1
- `minRelevanceScore`: number greater than 0 and less than or equal to 1

ArXiv paper search example:

```bash
curl -X POST https://www.robinsignal.com/api/v1/search \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
    "queries": ["Recent arXiv papers on retrieval-augmented generation for code agents, especially methods that evaluate long-horizon tasks"],
    "scope": "paper",
    "pageSize": 10,
    "lang": "eng"
  }'
```

Cross-source example:

```bash
curl -X POST https://www.robinsignal.com/api/v1/search \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
    "queries": ["Recent papers and technical articles about inference-time scaling for reasoning models"],
    "scope": "all",
    "pageSize": 10,
    "lang": "eng"
  }'
```

Notes:

- This request costs 1 quota unit per entry in `queries`.
- In current tests, typical success payloads include fields like `items`, `nextCursor`, and `requestId`.

### POST /api/v1/by-area

Search by one or more named areas.

Required JSON body fields:

- `areas`: array of 1 to 3 non-empty strings
- `relation`: `AND` or `OR`

Optional JSON body fields:

- `after`: UUID
- `cursor`: UUID
- `lang`: `chs` or `eng`
- `pageSize`: integer 1 to 50

```bash
curl -X POST https://www.robinsignal.com/api/v1/by-area \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
    "areas": ["ai", "robotics"],
    "relation": "OR",
    "pageSize": 10
  }'
```

Notes:

- This request costs 1 quota unit per entry in `areas`.
- This endpoint does not currently take a `scope` parameter.

### POST /api/v1/by-author

Search by author name.

Required JSON body fields:

- `name`: non-empty string
- `scope`: `paper`, `article`, or `all`

Optional JSON body fields:

- `after`: UUID
- `cursor`: UUID
- `lang`: `chs` or `eng`
- `pageSize`: integer 1 to 50

```bash
curl -X POST https://www.robinsignal.com/api/v1/by-author \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
    "name": "Geoffrey Hinton",
    "scope": "paper",
    "pageSize": 10,
    "lang": "eng"
  }'
```

Notes:

- This request costs 1 quota unit.

### POST /api/v1/by-institution

Search by institution name.

Required JSON body fields:

- `name`: non-empty string
- `scope`: `paper`, `article`, or `all`

Optional JSON body fields:

- `after`: UUID
- `cursor`: UUID
- `lang`: `chs` or `eng`
- `pageSize`: integer 1 to 50

```bash
curl -X POST https://www.robinsignal.com/api/v1/by-institution \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
    "name": "OpenAI",
    "scope": "paper",
    "pageSize": 10,
    "lang": "eng"
  }'
```

Notes:

- This request costs 1 quota unit.

## Browser-Only First-Party Endpoints

These endpoints are part of the RobinSignal verification and account UI. They are not the normal third-party agent integration surface:

- `GET /auth/conf` loads Google and Apple sign-in config for the first-party login page and preserves key-apply flow context.
- `POST /key/code` requires a signed-in RobinSignal web session and issues the verification code shown in the first-party verification flow.
- `GET /me` returns the signed-in human's account summary.
- `POST /me/api-keys/create` creates a new API key from the human account page.
- `POST /me/api-keys/:id/reveal` reveals an existing stored API key for the signed-in human.
- `DELETE /me/api-keys/:id` disables an existing API key for the signed-in human.
- `DELETE /me` deletes the signed-in local account.
- `POST /me/logout` revokes the current web session.

Use these only if you are operating RobinSignal's own first-party browser flow. For ordinary agent integration, use `/key/apply`, `/key/verify`, and `/api/v1/*`.

## Errors, Quota, And Rate Limits

Common API behavior:

- `400` with `{"code": 2001, "message": "request param invalid"}` means your query payload failed RobinSignal validation.
- `401` with `{"message": "API key is invalid."}` means the key is missing, malformed, disabled, expired, or tied to a disabled account.
- `402` means quota is insufficient. The current server message is `积分不足，可以购买更多积分`.
- `429` means the user-level RPM limit was exceeded. RobinSignal also returns a `Retry-After` header in seconds.
- Upstream query failures are passed through when possible, and RobinSignal refunds charged quota if the upstream request fails.

Quota rules:

- `GET /api/v1/quota` costs 0.
- `GET /api/v1/areas` costs 1.
- `POST /api/v1/search` costs 1 per query string.
- `POST /api/v1/by-area` costs 1 per area.
- `POST /api/v1/by-author` costs 1.
- `POST /api/v1/by-institution` costs 1.

## Recommended Agent Behavior

- Cache your RobinSignal API key securely once you obtain it.
- Check `/api/v1/quota` before launching large multi-query batches.
- Prefer `scope: "paper"` unless the human explicitly asks for technical articles or cross-source context.
- Prefer rich semantic queries over keyword fragments.
- Use structured endpoints for clear author or institution requests.
- Prefer smaller `queries` and `areas` batches when quota is tight, because those two endpoints charge per item.
- Keep `requestId` and `X-Request-Id` values in your own logs for debugging.
- Show source links to the human and encourage them to verify important claims at the original source.
- Do not imply that the skill has read a full paper unless the API result or original source access supports that claim.
- When results include summaries, treat them as discovery aids, not final verification.

## Suggested Response Format

When presenting results to the human, prefer a concise ranked list.

For each result, include when available:

- Title.
- Authors or source.
- Date or recency signal.
- Short relevance explanation.
- Summary.
- Original source link.

If results are weak, sparse, or outside arXiv coverage, say so clearly and suggest a better follow-up query.
