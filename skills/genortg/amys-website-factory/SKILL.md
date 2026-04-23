---
name: "amys-website-factory"
id: "amys-website-factory"
version: "0.1.0"
description: "Self-contained website factory skill for scaffold, build, test, deploy"
entry: "index.js"
---

# amys-website-factory skill

Provides a self-contained OpenClaw skill that exposes the website factory bundled in this skill's `factory/` folder as a reusable skill.

Capabilities
- create new site from template
- list existing sites
- run headless checks (dev server + Playwright smoke)
- publish/deploy helper wrappers (Vercel scripts wrapper)

Usage
- Use this skill when you want programmatic access to the factory: spawning builds,
  running tests, or creating site repos.

Implementation notes
- The skill is a lightweight wrapper around the existing scripts and templates in the
  workspace. It intentionally delegates heavy work to those scripts (`scripts/*.sh`) so
  the skill remains declarative and safe.

Paths
- Factory root (bundled): factory/

Documentation bundled in skill:
- docs/DESIGN_GUIDE.md — theming + Tailwind integration (CSS-vars + tailwind config snippet)
- docs/PACKS_RESEARCH.md — recommended component packs and tradeoffs (shadcn, Radix, Tailwind UI, Flowbite, etc.)
- docs/WORKFLOW.md — agent workflow (brief → scaffold → verify → deploy)
- docs/COPYWRITING.md — copy templates and SEO metadata

Action examples
- List sites: run `node index.js list` (shows bundled example sites)
- Create new site: `node index.js create <name>` (scaffolds Next.js + Tailwind, injects theme vars)
- Run checks: `node index.js check <name>` (headless verify wrapper)
- Deploy: `node index.js deploy <name> --prod` (requires explicit credentials/approval)

Security
- Non-destructive by default. Any deploy/publish actions require explicit approval or
  user-provided credentials (Vercel token, git remote).

Contact
- AMY (assistant) — use sessions_spawn or run scripts in a spawned subagent for long jobs.

