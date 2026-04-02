---
name: token-stats-reporter
description: Generate and append standardized token-usage statistics in replies. Use when users ask for token usage, when channel policy requires token stats in every message, or when sending periodic reports where cost/usage transparency is needed.
---

# Token Stats Reporter

## Overview
Use this skill to produce consistent token statistics lines and append them to user-facing replies.

## Quick workflow
1. Get token stats from the local counter script:
   - `python3 /home/admin/.openclaw/workspace/scripts/token-show.py`
2. Append the returned line to the end of the reply without changing its structure.
3. If the script is unavailable, fallback to `session_status` and clearly label it as fallback output.

## Output standard
Prefer this exact one-line format (as returned by the script):

`📊 Token: X in / X out | 本月: 约 N 次 | 累计 X.XXM | 💰 ¥X.XX`

Rules:
- Keep it as a single line at the end of the message.
- Do not include multiple token lines in one reply.
- Do not guess numbers; use tool/script output.
- If numbers are temporarily unavailable, state that explicitly and provide a fallback after `session_status`.

## Reliability checks
- Run token collection right before sending the final reply.
- In long multi-step tasks, refresh token stats again before final delivery.
- For scheduled/push reports, include token stats in every outgoing report message.