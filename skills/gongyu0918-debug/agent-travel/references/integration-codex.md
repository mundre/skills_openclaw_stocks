# Codex Integration

Codex supports native agent skills, `AGENTS.md`, and app automations. Keep `AGENTS.md` short and use a separate suggestion file so background research never becomes policy.

Default trigger choice for Codex: use app Automations first. Use inactivity-based travel only when the project is not attached to an automation-capable host.

## Install Path

Use one of these:

- repo-scoped: `./.agents/skills/agent-travel`
- user-scoped: `~/.agents/skills/agent-travel`
- local curated Codex setup: `~/.codex/skills/agent-travel`

Repo-scoped installs work best when the workflow belongs to the repository.

## AGENTS.md Pointer

Add a small section instead of a long embedded manual:

```md
## Agent Travel
Read ./.agents/agent-travel/suggestions.md when the current task matches a recent unresolved blocker or background research note. Treat it as advisory-only. Re-check freshness before using any hint.
```

Keep the actual advisory content in:

`./.agents/agent-travel/suggestions.md`

This follows Codex guidance to keep `AGENTS.md` as a map rather than an encyclopedia.

## Background Execution

Use Codex app Automations for recurring travel passes.
Keep the automation output narrow: update the suggestion file or create an inbox item, then stop.
Use medium search and all available search tools by default. Keep official docs mandatory and keep stored hints scoped to the active conversation.

Use explicit invocation when you want a task-end retrospective:

```text
Use $agent-travel to research the unresolved issue from the last task, keep the output advisory-only, and write it to ./.agents/agent-travel/suggestions.md.
```

## Internet Safety

When internet access is enabled, prefer a narrow domain allowlist and read-only methods.

Never let travel fetch or execute write-capable web actions. The skill should read, compare, and store hints only.

## Optional Metadata

`agents/openai.yaml` already exists in this skill folder. Set `allow_implicit_invocation: false` there if you want Codex to run `agent-travel` only from explicit prompts or automations.

## Official Docs Checked On 2026-04-19

- https://developers.openai.com/codex/skills
- https://developers.openai.com/codex/app/automations
- https://platform.openai.com/docs/codex/agent-network
- https://openai.com/index/harness-engineering/
- https://openai.com/index/introducing-codex/
