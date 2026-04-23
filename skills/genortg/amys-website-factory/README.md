# AMY's Website Factory — skill README

Purpose
- Self-contained OpenClaw skill that scaffolds, verifies, and deploys static/Next.js sites.
- All content and examples are OSS-focused and agent-friendly.

Install
- Copy this folder to an OpenClaw skills directory (e.g. `~/.openclaw/skills/`).
- Ensure `node` is available.

Quick commands (run from the skill folder)
- List sites: `node index.js list`
- Create site (scaffold): `node index.js create <name>`
- Verify site: `node index.js check <name>` (runs headless checks)
- Deploy site: `node index.js deploy <name> [--prod]` (requires approval/credentials)

Where to look
- factory/ — bundled templates, scripts, and example sites
- docs/ — DESIGN_GUIDE.md, PACKS_RESEARCH.md, PACKS_USAGE.md, WORKFLOW.md, COPYWRITING.md
- SKILL.md — frontmatter and short agent-facing metadata

Agent guidance
- All docs use short actionable steps and snippets so an AI agent can follow them reliably.
- No paid/proprietary components are required.

*** End of README

