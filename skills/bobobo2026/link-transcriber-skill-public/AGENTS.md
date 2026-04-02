# AGENTS

## Project Snapshot

This repository is the public distribution repo for the `link-transcriber` skill.

Current purpose:

- distribute a Codex-compatible public skill
- support Douyin and Xiaohongshu link summarization
- call the live `linkTranscriber` API
- return only the final summary text to the end user

This repo is intentionally small and should stay focused on the skill distribution surface only.

## Current Status

What is already done:

- `SKILL.md` is valid and installed locally in Codex
- `agents/openai.yaml` exists and matches the current skill behavior
- `scripts/call_service_example.py` supports:
  - infer platform from URL
  - optional cookie
  - create transcription task
  - poll transcription task
  - call summaries API
  - print only final summary text
- default live API base URL is wired in:
  - `http://139.196.124.192/linktranscriber-api`
- real API smoke has already succeeded against Xiaohongshu
- public GitHub repo has already been created and pushed:
  - `https://github.com/bobobo2026/link-transcriber-skill`

ClawHub status:

- CLI login is valid
- publish command was executed
- current blocker is platform policy:
  - GitHub account must be at least 14 days old
- last observed platform message:
  - `Try again in 1 day`

## Source Of Truth

Behavior source of truth:

- [SKILL.md](/Users/yibo/Documents/company/IdeaProjects/moreHelper/link-transcriber-skill-public/SKILL.md)

Codex UI metadata source of truth:

- [agents/openai.yaml](/Users/yibo/Documents/company/IdeaProjects/moreHelper/link-transcriber-skill-public/agents/openai.yaml)

Public repo overview:

- [README.md](/Users/yibo/Documents/company/IdeaProjects/moreHelper/link-transcriber-skill-public/README.md)

ClawHub-oriented copy:

- [CLAWHUB.md](/Users/yibo/Documents/company/IdeaProjects/moreHelper/link-transcriber-skill-public/CLAWHUB.md)

Smoke / example runner:

- [scripts/call_service_example.py](/Users/yibo/Documents/company/IdeaProjects/moreHelper/link-transcriber-skill-public/scripts/call_service_example.py)

## Key Product Behavior

Supported platforms:

- `douyin`
- `xiaohongshu`

Not supported in this repo’s current public skill positioning:

- YouTube
- action cards
- reminders
- execution tasks
- raw transcription JSON as the default user-facing result

End-user behavior:

1. user provides a link
2. user may provide cookie, but cookie is optional
3. skill infers platform when possible
4. skill creates transcription task
5. skill polls until transcription finishes
6. skill calls summaries API
7. skill returns only `summary_markdown`

## Live API Details

Default API base URL:

- `http://139.196.124.192/linktranscriber-api`

Health check:

- `GET /api/sys_check`

Transcription create:

- `POST /api/service/transcriptions`

Transcription lookup:

- `GET /api/service/transcriptions/{task_id}`

Summary generation:

- `POST /api/service/summaries`

Default summary settings:

- `provider_id=deepseek`
- `model_name=deepseek-chat`

## Validation Commands

Validate skill structure:

```bash
/Users/yibo/Documents/company/IdeaProjects/moreHelper/link-transcriber/.venv-pytest/bin/python \
  /Users/yibo/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  /Users/yibo/Documents/company/IdeaProjects/moreHelper/link-transcriber-skill-public
```

Compile script:

```bash
python3 -m compileall /Users/yibo/Documents/company/IdeaProjects/moreHelper/link-transcriber-skill-public/scripts
```

Run live smoke:

```bash
python3 /Users/yibo/Documents/company/IdeaProjects/moreHelper/link-transcriber-skill-public/scripts/call_service_example.py \
  'http://xhslink.com/o/23s4jTem6em'
```

Optional API base override:

```bash
LINK_SKILL_API_BASE_URL=http://139.196.124.192/linktranscriber-api \
python3 /Users/yibo/Documents/company/IdeaProjects/moreHelper/link-transcriber-skill-public/scripts/call_service_example.py \
  'http://xhslink.com/o/23s4jTem6em'
```

## Todo

Immediate:

- retry ClawHub publish after account-age restriction clears
- record the final ClawHub page URL in `README.md` and this file
- verify one real Douyin smoke path in addition to Xiaohongshu

Short-term:

- improve `CLAWHUB.md` from compatibility note to final publish copy if ClawHub needs richer listing text
- add one concrete “natural language user examples” section to `README.md`
- verify Codex installation from the public GitHub repo on a clean machine or clean Codex profile

Optional:

- add a lightweight changelog section in `README.md`
- add a second smoke example for no-cookie and with-cookie modes

## Constraints

- Keep this repo focused on public skill distribution only
- Do not pull backend implementation, deployment docs, or unrelated project history into this repo
- Do not reintroduce action-card / reminder / execution-task positioning into public skill copy
- Prefer updating `SKILL.md`, `agents/openai.yaml`, `README.md`, and `CLAWHUB.md` together so public descriptions stay aligned
