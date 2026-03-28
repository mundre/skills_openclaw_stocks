# AlphaLens API Skill Package

This folder contains a publishable skill package for the AlphaLens API.

**Note:** This skill requires an active [AlphaLens subscription](https://alphalens.ai) with API access. Contact sales@alphalens.ai for pricing.

## Contents

- `SKILL.md`: Main skill definition used by agent runtimes
- `workflows/`: Deliverable workflow files (market maps, investor network, peer benchmark, suite)
- `references/REFERENCE.md`: Endpoint catalog and pipeline operations
- `references/EXAMPLES.md`: Example prompts and request shapes

## Local Use

To make this skill available locally in a supported agent runtime, copy this folder to one of:

- `.claude/skills/alphalens-api/` (Claude Code)
- `.agents/skills/alphalens-api/` (OpenAI Codex)
- `~/.cursor/skills/alphalens-api/` (Cursor)
- `~/.openclaw/skills/alphalens-api/` (OpenClaw)

The final path must contain `SKILL.md` directly inside the `alphalens-api` directory.

## HTML Output

Market maps, investor networks, and peer benchmarks are rendered as standalone HTML files with company logos, interactive charts, and PDF export. Favicons are embedded as base64 data URIs — no external dependencies, no proxy required. The HTML opens in any browser, including Claude.ai artifacts.

## Publish For Installer Use

If you want to install this with a repo-based installer:

```bash
npx skills add your-org/your-skills-repo
```

publish a repository that includes this `alphalens-api/` directory with `SKILL.md` inside it.

## Claude Code

For Claude Code, follow that tool's skill/plugin install flow against the published repo. The exact commands can differ by runtime version, but the skill package content in this folder is the part you need to publish.
