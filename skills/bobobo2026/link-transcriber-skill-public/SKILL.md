---
name: link-transcriber
description: Use this skill when a user wants to submit a Douyin or Xiaohongshu link to the linkTranscriber transcription API, optionally provide cookie when available, wait for transcription to finish, then call the summaries API and return only the final summary markdown to the user.
---

# Link Transcriber

## Overview

This skill is intentionally narrow.

Default API base URL:

- `http://139.196.124.192/linktranscriber-api`

Use it to:

- collect a Douyin or Xiaohongshu link
- collect a cookie when available
- infer or confirm the platform
- create a transcription task
- poll the task until it succeeds
- call the summaries API
- return only the final summary text to the user

## When To Use It

Trigger this skill when the user wants to:

- summarize a Douyin link
- summarize a Xiaohongshu link
- get a concise AI-generated summary after transcription
- receive only the final summary output instead of the raw transcription payload

Do not use this skill for:

- YouTube links
- `/api/generate_note`
- returning the full raw transcription JSON by default
- reminders, execution tasks, or billing workflows

## Required Inputs

This skill needs:

1. `url`
2. `cookie` (recommended, not strictly required)
3. `platform`

Infer `platform` when possible:

- `douyin` for `douyin.com` or `v.douyin.com`
- `xiaohongshu` for `xiaohongshu.com` or `xhslink.com`

If the platform cannot be inferred reliably, ask the user to specify `douyin` or `xiaohongshu`.

The upstream transcription API allows missing `cookie` in some cases. This skill should prefer asking for `cookie` when the user has it, but it may still attempt the request without cookie if the user does not have one or wants to try without it first.

## Workflow

1. Check whether the user provided `url`.
2. Check whether the user provided `cookie`.
3. Infer `platform` from the link when possible.
4. If `url` is missing, ask for it and stop.
5. If `platform` cannot be inferred, ask for it and stop.
6. If `cookie` is missing, you may ask for it first, but you can also proceed without it if the user wants to try without cookie.
7. Create a transcription task with `POST /api/service/transcriptions`:

Use the default base URL above unless the environment explicitly overrides it.

```json
{
  "url": "https://...",
  "platform": "xiaohongshu"
}
```

If cookie is available, include it:

```json
{
  "url": "https://...",
  "platform": "xiaohongshu",
  "cookie": "your-cookie-string"
}
```

8. Extract `data.task_id` from the creation response.
9. Poll `GET /api/service/transcriptions/{task_id}` until the task reaches a final successful state.
10. Call `POST /api/service/summaries` with:

```json
{
  "transcription_task_id": "task-id",
  "provider_id": "deepseek",
  "model_name": "deepseek-chat"
}
```

11. Return only `data.summary_markdown` to the user.

## Output Rules

- The final user-facing result should be the summary text only.
- Prefer returning `data.summary_markdown` exactly as produced by the summaries API.
- Do not return raw transcription payload unless the user explicitly asks for debugging details.
- Do not add action cards or custom wrappers around the summary.

## Error Handling

- If `url` is missing, ask for the link.
- If `cookie` is missing, prefer asking for it, but allow a no-cookie attempt when the user does not have one.
- If the platform cannot be inferred, ask whether it is `douyin` or `xiaohongshu`.
- If transcription task creation fails, return the upstream error clearly.
- If polling ends in failure, return the task error instead of calling summaries.
- If summary generation fails, return the upstream summary API error.

## Example Prompt

Use $link-transcriber to summarize this Xiaohongshu link. I want only the final summary result:

- `url`: `http://xhslink.com/...`
- `cookie`: `web_session=...` (optional but recommended)
