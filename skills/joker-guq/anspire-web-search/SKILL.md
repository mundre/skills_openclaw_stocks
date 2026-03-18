---
name: anspire-web-search
description: Use when the user asks for up-to-date web information, recent news, current events, policy changes, market signals, or other real-time information that requires web search.
user-invocable: false
metadata: {"openclaw":{"emoji":"🔎","primaryEnv":"ANSPIRE_API_KEY","requires":{"env":["ANSPIRE_API_KEY"],"bins":["curl"]}}}
---

# Anspire Web Search

Use the Anspire search API when the request depends on real-time web information.

## When to use

- The user asks to search the web, browse, look up, or verify recent information
- The question depends on current events, recent news, policy changes, market updates, releases, or other time-sensitive facts
- The answer would be unreliable without live internet access

## When not to use

- The request can be answered from stable knowledge alone
- The user only wants rewriting, translation, brainstorming, or code edits unrelated to live information
- `ANSPIRE_API_KEY` is unavailable

## Required behavior

1. Build a concise search query from the user's request.
2. Call the Anspire API with `curl --get --data-urlencode` so the query is encoded safely.
3. Read the JSON response and extract the most relevant items, typically `title`, `url`, and `snippet`.
4. Summarize the results in Chinese unless the user asks for another language.
5. Mention the source domains or titles for important claims.
6. If the API call fails or returns no useful results, say so clearly and do not fabricate a live answer.

## API call

```bash
QUERY="latest OpenClaw releases"
curl --silent --show-error --fail --location --get \
  "https://plugin.anspire.cn/api/ntsearch/search" \
  --data-urlencode "query=$QUERY" \
  --data-urlencode "top_k=10" \
  --header "Authorization: Bearer $ANSPIRE_API_KEY" \
  --header "Content-Type: application/json" \
  --header "Accept: application/json"
```

## Optional filters

Use these only when the user request needs them:

- `Insite`: restrict to a specific site or domain
- `FromTime`: lower time bound, for example `2026-03-01`
- `ToTime`: upper time bound
- `mode`: search mode when supported by the API

## Output expectations

- Prefer a short answer first, then a compact result list if useful
- Preserve uncertainty when results conflict
- If the user asks for the latest information, explicitly say the answer is based on live search results
- Do not expose the API key or ask the user to paste secrets into the prompt

See `examples.md` for example user prompts and response patterns.

