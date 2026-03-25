---
name: simple-code
description: "Plan and build small, readable coding projects with a strict workflow: think first, make a short plan, then delegate implementation/testing/bug-fixing/documentation/step-tracking to a sub-agent using an OAuth-backed OpenAI Codex model (not an API-key model). Use when the user asks for simple code, a small project, a self-contained utility, or a straightforward implementation that should stay easy to read and easy to manage."
---

# Simple Code

## Overview

Follow a lightweight project workflow for small coding tasks where readability matters more than cleverness.

## Workflow

1. If the task is project-like, create a properly named project folder under `agent_code/<project-name>` first.
2. When creating that project folder, also create a `.steps/` folder inside it.
3. Initialize `.gitignore` in the project folder if needed, and make sure it ignores `.steps/` and everything under it from the start.
4. Do all further work inside that project folder.
5. Think through the request before coding.
6. Make a short plan and state the chosen approach briefly.
7. Spawn a coding sub-agent through OpenClaw (`runtime="subagent"`) using an OAuth-backed OpenAI Codex model (preferred); do not use an API-key-based model.
8. Sub-agent work must run without blocking the current active channel session; delegate heavy coding first, then continue channel interaction normally.
9. After delegation, all following execution work must be done by the sub-agent inside the project folder: coding, testing, bug-fixing, documentation, and `.steps/` tracking.
10. Keep the implementation simple, readable, and standard-library-first unless the user asks otherwise.
11. Add tests for the most important functionality inside the same project folder.
12. Verify the project by running the relevant build/test commands from the project folder.
13. If tests fail, fix the issues and re-run until the final code passes and runs.
14. Use git inside the project folder, not at the whole-workspace level, unless the user explicitly wants workspace-level git.
15. For each request that results in a commit, create one concise tracking note in `.steps/` after the commit, named `<YYYYMMDD-HHMM>-<abbr>-<commit-hash>.md`.
16. In that tracking note, record only: request summary, short plan, and execution outcome against plan. Keep it concise and brief.
17. When the sub-agent session finishes, send a short ping that the code is ready and briefly state what was done.

## Coding Rules

- Prefer clear names over compact tricks.
- Prefer fewer files and a smaller API when possible.
- Prefer standard tools for the language ecosystem.
- Avoid unnecessary dependencies.
- Handle invalid input and obvious failure cases clearly.
- Do not leave the code unverified if a local build/test command is available.

## Project Layout Rules

For project-like requests, create this structure first and work only inside it by default:

- `agent_code/<project-name>/`
- `agent_code/<project-name>/.steps/`
- source files in that folder root unless there is a good reason to add subdirectories
- tests in the same folder if the project is very small
- add a simple build file when appropriate, such as `CMakeLists.txt` for C++
- add or update `.gitignore` early so `.steps/` is ignored before commits start

## Git Rules

- Initialize git in the project folder if needed.
- Add `.steps/` to `.gitignore` before the first commit in a new project when possible.
- Commit meaningful milestones after verification.
- After each such commit, create a matching `.steps/<YYYYMMDD-HHMM>-done-<abbr>-<commit-hash>.md` note.
- Keep each `.steps` note short: request, plan, and outcome only.
- If the workspace root has temporary bootstrap git history and the user asks to remove it, remove only that root-level history.
- Do not rewrite git history unless the user explicitly asks.

## Response Style

When reporting back to the user after sub-agent completion:

- start with a short ping that the code is ready
- briefly state what was built
- include where it lives
- briefly mention verification status
- include the latest relevant commit hash if git was used
