# LinkTranscriber ClawHub Publish Notes

This file is only a lightweight compatibility note for legacy ClawHub-style publishing.

- Canonical skill source: `skill/SKILL.md`
- Canonical UI metadata: `skill/agents/openai.yaml`
- Default API base URL: `http://139.196.124.192/linktranscriber-api`
- Supported platforms in this minimal version: Douyin and Xiaohongshu only
- Inputs: `url`, optional `cookie`, and inferred or confirmed `platform`
- Behavior: create a transcription task, poll the task result, call summaries, return only the final summary text

When preparing old-channel listing copy, keep it minimal:

- collects link and cookie
- can attempt transcription without cookie when needed
- creates a transcription task through the service API
- calls the summaries API after transcription completes
- returns only the final summary text
