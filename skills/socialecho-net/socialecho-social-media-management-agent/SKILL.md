---
name: socialecho-social-media-management-agent
description: SocialEcho social media management API skill for querying team, account list, article list, and report endpoints using team API key. Use for integration checks and data pulls.
---

# SocialEcho Social Media Management Agent

Use this skill to call SocialEcho external APIs with a team API key.

## Prerequisites

1. Sign up / sign in at `https://app.socialecho.net/`.
2. Create a team.
3. In Team Management, create an API key.
4. Use explicit CLI options for auth/runtime (do not auto-read env vars):
   - `--api-key` (required)
   - `--base-url` (optional, default `https://api.socialecho.net`)
   - `--team-id` (optional)
   - `--lang` (optional, default `zh_CN`)

`--team-id` is optional for most calls but can be required by report queries depending on server rules.

## Setup

```bash
cd social-media-autopilot
npm ci
```

Runtime requirement: Node.js `>=18`

## Commands

```bash
./team.js --api-key YOUR_KEY
./account.js --api-key YOUR_KEY --page 1 --type 1
./article.js --api-key YOUR_KEY --page 1 --account-ids 41,42
./report.js --api-key YOUR_KEY --start-date 2026-01-01 --end-date 2026-03-24 --time-type 1 --group day --account-ids 41,42
```

## Notes

- Success is defined as: HTTP 200 and response JSON `code == 200`.
- External API rate limit: maximum `120 requests / minute` per API key.
- If calling in loops or automation, keep request rate below limit and add retry/backoff on throttle responses.
- Scripts print response body and exit with non-zero status on failure.
- Use `--base-url https://api-dev.socialecho.net` for dev environment.
- OpenAPI spec: `openapi.yaml` (Swagger/OpenAPI 3.0.3, LLM-friendly descriptions and field semantics).
