# Hermes Integration

Hermes loads skills on demand and keeps them out of context until needed. Pair `agent-travel` with cron or other background automation, and keep the advisory output outside auto memory.

Default trigger choice for Hermes: use the scheduler or host wake mechanism first. Use inactivity time only as a fallback when no periodic wake exists.

## Install Path

A Hermes-native copy usually lives under:

`~/.hermes/skills/research/agent-travel`

Every installed skill becomes a slash command and loads through `skills_list()` and `skill_view()` only when relevant.

## Hermes-Specific Frontmatter

If you publish a Hermes-specific fork, these fields are useful:

```yaml
version: 1.0.0
metadata:
  hermes:
    tags: [research, automation, background, memory]
    requires_toolsets: [web]
```

That keeps the skill hidden when web tools are unavailable.

## Trigger Pattern

Use this mapping:

- repeated failure or repeated user correction -> `low`
- task-end retrospective -> `medium`
- scheduled or heartbeat-like background wake -> `medium` by default
- scheduled cron or quiet-thread sweep -> `high` when budget allows

Hermes docs position cron as the right tool for scheduled work. Keep `agent-travel` instruction-heavy and let cron decide when to invoke it.

## Advisory Boundary

Do not store travel output in Hermes auto memory. Auto memory is loaded at session start and is better for stable facts about the user or project.

Use a repo-local advisory file instead:

`./.agents/agent-travel/suggestions.md`

Add a short pointer in `SOUL.md` or project instructions:

```md
If ./.agents/agent-travel/suggestions.md exists, treat it as advisory-only travel output and consult it only when the current task matches.
```

## Example Cron Prompt

```text
Run $agent-travel for the active workspace. Use medium budget unless the thread has been quiet for 72h, then use high. Update ./.agents/agent-travel/suggestions.md only. Keep the output advisory-only.
```

Search with all available tools unless the user narrowed the preference. Keep official docs mandatory and keep stored hints limited to the active conversation.

## Official Docs Checked On 2026-04-19

- https://hermes-agent.nousresearch.com/docs/guides/work-with-skills
- https://hermes-agent.nousresearch.com/docs/developer-guide/creating-skills
- https://github.com/NousResearch/hermes-agent
