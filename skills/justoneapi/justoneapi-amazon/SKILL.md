---
name: justoneapi_amazon
description: Use JustOneAPI Amazon endpoints through JustOneAPI HTTP APIs.
author: JustOneAPI
homepage: https://api.justoneapi.com
metadata: {"openclaw":{"homepage":"https://api.justoneapi.com","primaryEnv":"JUST_ONE_API_TOKEN","requires":{"bins":["node"],"env":["JUST_ONE_API_TOKEN"]},"skillKey":"justoneapi_amazon"}}
---

# Amazon

Use this skill for JustOneAPI `Amazon` endpoints.

## When To Use It

- The user needs data from the `Amazon` platform exposed by JustOneAPI.
- The user wants to inspect or call a specific JustOneAPI endpoint for this platform.
- The user needs raw API output plus a short structured explanation.

## How To Work

1. Read `generated/operations.md` before choosing an endpoint.
2. Pick the smallest matching operation instead of guessing.
3. Ask the user for any missing required parameter. Do not invent values.
4. Call the helper with:

```bash
node {baseDir}/bin/run.mjs --operation "<operation-id>" --params-json '{"key":"value"}'
```

## Environment

- Required: `JUST_ONE_API_TOKEN`

## Output Rules

- Start with a short conclusion in plain language.
- Then include the most relevant fields from the response.
- Include raw JSON when the user asks for it or when the structure matters.
- If the API returns an error, explain the failure clearly and include the backend error payload.
