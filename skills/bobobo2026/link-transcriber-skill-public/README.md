# Link Transcriber Skill

`link-transcriber` is a minimal Codex-compatible skill for summarizing Douyin and Xiaohongshu links.

It uses the live linkTranscriber service at:

- `http://139.196.124.192/linktranscriber-api`

The skill workflow is:

1. accept a Douyin or Xiaohongshu link
2. optionally accept a cookie when available
3. infer the platform when possible
4. create a transcription task
5. poll until transcription finishes
6. call the summaries API
7. return only the final summary text

## Install In Codex

Install from this GitHub repository, then restart Codex so it picks up the skill.

After installation, use it in natural language:

```text
Use $link-transcriber to summarize this link: http://xhslink.com/o/23s4jTem6em
```

If you have cookie information, you can include it:

```text
Use $link-transcriber to summarize this link: http://xhslink.com/o/23s4jTem6em
cookie: web_session=...
```

## Behavior

- Supports Douyin and Xiaohongshu
- Cookie is optional but recommended
- Platform is inferred from the URL when possible
- Default summaries provider: `deepseek`
- Default summaries model: `deepseek-chat`
- Final user-facing output is only the summary text

## Local Smoke

Run the example script directly:

```bash
python3 scripts/call_service_example.py 'http://xhslink.com/o/23s4jTem6em'
```

Override the API base URL if needed:

```bash
LINK_SKILL_API_BASE_URL=http://139.196.124.192/linktranscriber-api \
python3 scripts/call_service_example.py 'http://xhslink.com/o/23s4jTem6em'
```

## Files

- `SKILL.md` - canonical skill behavior
- `agents/openai.yaml` - Codex UI metadata
- `scripts/call_service_example.py` - transcribe + poll + summarize example
- `CLAWHUB.md` - ClawHub-oriented publish copy
