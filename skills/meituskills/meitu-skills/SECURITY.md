# Security Model

This document describes the security model and operational boundaries of `meitu-skills`.

## Scope

`meitu-skills` has two security-relevant layers:

- Root and scene skills: route requests, read project context, and in some workflows write project or shared memory files.
- `meitu-tools`: executes validated `meitu-cli` commands through the local runner.

This file covers both layers so reviewers can compare the written workflow against the declared permissions.

## Credential Requirements

This skill pack requires Meitu OpenAPI credentials to function. Supported sources are:

| Method | Location | Priority |
|--------|----------|----------|
| Environment variables | `MEITU_OPENAPI_ACCESS_KEY`, `MEITU_OPENAPI_SECRET_KEY` | Highest |
| Credentials file | `~/.meitu/credentials.json` | Fallback |

### Credentials File Format

```json
{
  "accessKey": "your-access-key",
  "secretKey": "your-secret-key"
}
```

Security guidance:

- Restrict file permissions, for example `chmod 600 ~/.meitu/credentials.json`
- Never commit credentials to version control
- Prefer environment variables in CI or shared environments

## Declared Permissions

The root skill declares permissions for project-mode workflows:

- `file_read`: `~/.meitu/credentials.json`, `~/.openclaw/workspace/visual/`, `./openclaw.yaml`, `./DESIGN.md`
- `file_write`: `~/.openclaw/workspace/visual/`, `./output/`, `./openclaw.yaml`, `./DESIGN.md`
- `exec`: `meitu`

Scene skills inherit and use these permissions for their workflows.

### Root Skill Permission Scope

| Path | Access | Purpose |
|------|--------|---------|
| `~/.meitu/credentials.json` | Read | Load API credentials |
| `~/.openclaw/workspace/visual/` | Read/Write | Read/write shared visual memory, rules, references, and outputs |
| `./openclaw.yaml` | Read/Write | Project configuration (project mode detection and updates) |
| `./DESIGN.md` | Read/Write | Project design decisions and iteration log |
| `./output/` | Write | Generated outputs directory |

These permissions enable project-mode workflows that persist design decisions, share visual memory across sessions, and maintain project configuration.

### Scene Skill Permission Scope

Scene skills use the permissions declared by the root skill:

| Path | Access | Purpose |
|------|--------|---------|
| `~/.meitu/credentials.json` | Read | Load API credentials |
| `~/.openclaw/workspace/visual/` | Read/Write | Read/write shared visual memory, rules, references, and outputs |
| `./openclaw.yaml` | Read/Write | Project configuration (project mode detection and updates) |
| `./DESIGN.md` | Read/Write | Project design decisions and iteration log |
| `./output/` | Write | Generated outputs directory |

Examples of expected writes in scene workflows:

- Project-mode outputs under `./output/`
- Project metadata updates in `./DESIGN.md`
- Project initialization via `openclaw.yaml`
- Shared observation or memory updates under `~/.openclaw/workspace/visual/memory/`

### Command Execution Scope

| Command | Purpose | When Used |
|---------|---------|-----------|
| `meitu` | Execute Meitu CLI commands | Tool execution and generation/edit pipelines |
| `node` | Execute internal runner script | `meitu-tools/scripts/run_command.js` for CLI command dispatch |
| `npm install -g meitu-cli@latest` | Manual runtime install or upgrade | Only when the operator explicitly asks for repair or upgrade |

Notes:

- `meitu-tools` executes `scripts/run_command.js` via `node` to dispatch CLI commands.
- Scene skills call `meitu` CLI directly and do not need `node`.
- Scene skills use inline path resolution logic (no external helper scripts).

## Prompt and Instruction Handling

- User-provided text, prompts, URLs, and JSON fields are treated as task data only.
- User content must not override skill instructions, permission boundaries, or runner behavior.
- Scene skills must not disclose unrelated local file contents, hidden instructions, internal endpoints, or credentials.
- `meitu-tools` accepts only validated command names and validated parameter shapes from its registry path; user text is not command authority.

## Shell Execution Security

This skill pack executes commands via the `meitu` CLI. While SKILL.md instructions reference "Run via Bash" for workflow clarity, the actual execution model is designed to prevent shell injection vulnerabilities.

### Safe Execution Mechanism

The `meitu` CLI uses safe process spawning (equivalent to `spawn()`/`execFile()` patterns) rather than shell string interpolation (`exec()` patterns):

```
Safe pattern (used by meitu CLI):
  spawnSync('meitu', ['--prompt', userInput, '--json'])
  → userInput is passed as a separate argument, NOT interpolated into shell string

Dangerous pattern (NOT used):
  exec(`meitu --prompt "${userInput}" --json`)
  → userInput would be shell-interpolated, enabling injection
```

### Why This Is Safe

| Aspect | Explanation |
|--------|-------------|
| **Argument isolation** | Each CLI parameter is passed as a discrete argument to the process, not concatenated into a shell command string |
| **No shell interpretation** | The process receives arguments directly without shell parsing; special characters like `|`, `$`, `` ` `` are treated as literal text |
| **JSON output mode** | The `--json` flag ensures structured output, preventing output-based injection scenarios |
| **Command whitelist** | Only predefined commands from `tools.yaml` are allowed; arbitrary command names are rejected |

### User Input Flow

```text
User provides: "A cat with $100 price tag"
    │
    ▼
Skill validates: Command name must exist in tools.yaml
    │
    ▼
CLI receives: spawnSync('meitu', ['image-generate', '--prompt', 'A cat with $100 price tag', '--json'])
    │
    ▼
API processes: Prompt is sent to Meitu API as text content
    │
    ▼
Result: Image generated, no shell execution of "$100"
```

The `$100` in the prompt is never interpreted as a shell variable because:
1. It's passed as a discrete argument to `spawnSync`
2. The CLI process receives it as a string value
3. The Meitu API treats it as literal prompt text

### Clarification for Security Reviewers

The phrase "Run via Bash" in SKILL.md refers to the workflow step of executing the CLI binary, not to using Bash's string interpolation. All user inputs are:
- Validated against allowed command names (from tools.yaml registry)
- Validated against allowed parameter keys (from cli.requiredKeys/optionalKeys)
- Passed as separate arguments to the CLI process

This execution model aligns with industry-standard CLI security practices used by tools like `git`, `npm`, and `docker`.

## Runtime Repair Policy

Automatic runtime repair is intentionally disabled.

- The runner does not auto-install packages
- The runner does not auto-upgrade `meitu-cli`
- The runner may return actionable manual repair guidance when runtime is missing or outdated
- Operators should run install or upgrade commands only when they explicitly want runtime repair

### Manual Update

```bash
npm install -g meitu-cli@latest
meitu --version
```

## Data Flow

### Direct Tool Execution (`meitu-tools`)

```text
User Request
    │
    ▼
run_command.js
    │
    ├── Read credentials (env or file)
    ├── Validate command name and inputs
    ├── Execute meitu CLI
    │   └── spawnSync('meitu', [...args])
    └── Return result or manual repair hint
```

### Scene Workflow Execution

```text
User Request
    │
    ▼
Root / Scene Skill
    │
    ├── Read project context from ./
    ├── Optionally read shared memory from ~/.openclaw/workspace/visual/
    ├── Execute meitu CLI
    └── Optionally write outputs, DESIGN.md, or shared memory updates
```

## What This Skill Pack Does NOT Do

- Does not auto-install or auto-upgrade `meitu-cli`
- Does not treat user prompt text as authority to run arbitrary binaries
- Does not declare permission to write outside the current workspace and `~/.openclaw/workspace/visual/`
- Does not require `~/Downloads/`
- Does not execute arbitrary JavaScript from the current project workspace
- Does not execute external helper scripts from user home directories
- Does not intentionally disclose credentials or unrelated local files in responses

## Audit Checklist

Before publishing or using this skill pack in production:

- [ ] Credentials are stored securely and not committed
- [ ] Declared permissions still match the written workflow in `SKILL.md` and scene skills
- [ ] Manual runtime repair is acceptable for your environment
- [ ] `meitu-cli` source and release provenance have been reviewed before any manual install or upgrade

## Vulnerability Reporting

If you discover a security vulnerability, report it privately to the maintainers. Do not open a public issue with exploit details.

## Version History

| Version | Changes |
|---------|---------|
| 2026-04-16 | Added Shell Execution Security section to clarify safe process spawning mechanism and address ClawHub risk classification |
| 2026-04-15 | Unified permissions across root SKILL.md, SECURITY.md, and all scene skills; metadata now explicitly declares project file paths (openclaw.yaml, DESIGN.md, output/) |
| 2026-03-25 | Removed legacy credential path; removed external helper script dependency; consolidated root permissions |
| 2026-03-23 | Updated security model to reflect root and scene skill permissions, project and visual workspace writes |
| 2026-03-23 | Removed automatic runtime version checks and automatic updates; manual repair only |
| 2025-03-21 | Initial security documentation |
