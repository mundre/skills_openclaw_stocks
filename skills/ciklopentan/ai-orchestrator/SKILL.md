---
name: ai-orchestrator
description: DeepSeek session helper for reusable conversations and quick CLI access. Use when you need a lightweight wrapper for starting, resuming, or ending DeepSeek chats.
---

# AI Orchestrator

Use `ask-deepseek.sh` for simple command-line DeepSeek chats.

## Quick start

```bash
ask-deepseek.sh "your question"
ask-deepseek.sh "your question" --session work
ask-deepseek.sh --session work --end-session
```

## Guidance

- Keep one session per topic.
- Use the same session to continue a conversation.
- If a response is incomplete, ask a follow-up in the same session.
- Prefer short, focused prompts.
