---
name: wander
description: "Monitor any async task that takes time and needs completion notification — CI, builds, deploys, releases. Use when the user triggers any long-running async task and should not have to poll for results manually."
---

# Wander — Async Task Completion Monitor

**Don't watch. Wander.** The core philosophy: when you trigger something async, you should be notified when it finishes — not polling, not refreshing, not waiting.

## Mental model (first principles)

Every async task has the same shape:

```
Trigger  →  Task runs remotely  →  Result
(Agent)     (can't speed up)       (Agent + User both need to know)
```

Wander owns the middle-to-right transition. The Agent triggers and moves on. Wander closes the loop back to **both the user (notification) and the Agent (result context)**.

**The loop is only complete when the Agent knows the result.** After Wander reports completion, the Agent must:

1. **Read the terminal output** from the Wander background process to get the actual result.
2. **Act on the result** — do not consider the task "done" until the result is confirmed:
   - ✅ success → proceed to next step (e.g., announce PR ready, deploy, tag release)
   - ❌ failure → immediately surface the failure, fetch failed logs, propose fix
3. **Never assume success** — a background monitor starting is not the same as the task succeeding.

```bash
# After Wander background process exits, check result:
gh run view <RUN_ID> --json conclusion -q .conclusion
# → "success" | "failure" | "cancelled" | "timed_out"

# If failure, fetch logs for Agent to diagnose:
gh run view <RUN_ID> --log-failed
```

**Task taxonomy** — what counts as a "task" Wander should monitor:

| Task type | Examples | Wander support |
|-----------|----------|---------------|
| CI test | lint, unit test, e2e | ✅ Native (GitHub Actions) |
| Build | Docker, web bundle | ✅ Native (GHA `build.yml`) |
| Mobile build | EAS iOS/Android | ⚠️ GHA wrapper only (not EAS CLI direct) |
| Deploy | Railway, Fly, Vercel | ✅ Native (GHA deploy workflow) |
| Release / publish | npm, ClawHub, App Store | ✅ Native (GHA publish workflow) |
| Ad-hoc long task | DB migration, data job | ⚠️ Manual: wrap in GHA workflow_dispatch |

**Current engine**: GitHub Actions only. For EAS builds triggered via `eas build` CLI, Wander cannot monitor directly — use a GHA wrapper workflow that calls EAS, then monitor that workflow.

For the full **v1 scope** statement (GHA vs non-GHA CLIs, workarounds, roadmap links), see the repository README: [v1 scope: GitHub Actions today](https://github.com/ERerGB/wander/blob/main/README.md#v1-scope-github-actions-today).

---

## Agent auto-trigger (mandatory)

**After triggering ANY async task that maps to a GitHub Actions workflow, start Wander in background mode** unless the user opts out.

Trigger signals to watch for:
- `git push` to a branch that has CI/CD configured
- PR created or merged (if deploy workflow triggers on merge)
- `gh workflow run` (manual dispatch)
- `eas build` that is backed by a GHA wrapper

Steps:
1. Check if `.workflows.yml` exists → use it to pick the right workflow name and timing.
2. If `.workflows.yml` is absent but `.github/workflows/` exists → run `scan_workflows` (or ask user) to identify the right workflow, then start.
3. Use `watch-workflow-bg.sh <workflow.yml>` — always background unless user explicitly wants to block.
4. After ~8s check terminal output and report initial status.
5. Tell the user: "Wander is watching `<workflow>`. I'll notify you when it finishes — continue working."
6. **Poll for result**: periodically check the terminal output file or run `gh run view <RUN_ID> --json conclusion`. Do not declare the task complete until conclusion is `success`.
7. **On result**:
   - success → report to user, proceed with next planned step
   - failure → immediately fetch `gh run view <RUN_ID> --log-failed`, surface the error, propose a fix

If `.github/workflows/` does not exist: offer monitoring but do not auto-start.

---

## When to use this skill

- User triggers anything async that will take > 30 seconds
- User says "let me know when CI is done" / "notify me when the build finishes"
- User is about to wait or refresh manually
- Long pipelines: E2E, mobile build wrappers, release publish, DB migrations via GHA
- Any `git push` that touches a branch with a workflow `on: push` trigger

## When NOT to use

- Task completes in < 10 seconds (just wait inline)
- No GitHub Actions involved and no GHA wrapper exists
- User explicitly said they want to watch synchronously

---

## Prerequisites

- `gh` CLI installed and authenticated
- `jq` installed
- Wander on disk: `WANDER_HOME` (default `~/code/wander`)
- macOS for notification center; Linux/headless: output-only mode still works

## Install

```bash
git clone https://github.com/ERerGB/wander.git ~/code/wander
cd ~/code/wander && chmod +x *.sh
```

Add to shell rc:

```bash
export WANDER_HOME="${WANDER_HOME:-$HOME/code/wander}"
export PATH="$WANDER_HOME:$PATH"
alias wf='watch-workflow.sh'
alias wfbg='watch-workflow-bg.sh'
alias wfdt='watch-workflow-detached.sh'
```

---

## Picking the right mode

| Mode | Script | Use case |
|------|--------|----------|
| Background | `watch-workflow-bg.sh` | **Default.** Keep working; get notified. |
| Detached | `watch-workflow-detached.sh` | Close terminal; logs to `~/.wander_logs/` |
| Foreground | `watch-workflow.sh` | Block session until done (rare) |

**Rule of thumb**: always background. Switch to detached for >5 min tasks where you'll close the terminal.

---

## Workflow registry (`.workflows.yml`)

Each workflow has different timing. The registry tells Wander what to expect:

```yaml
workflows:
  - name: "ci.yml"
    description: "Lint + unit tests"
    check_window: 180      # grace window if already finished when we start
    expected_duration: 45  # typical runtime
    category: "smoke"

  - name: "build.yml"
    description: "Docker build + push"
    check_window: 600
    expected_duration: 180
    category: "build"

  - name: "deploy.yml"
    description: "Railway deploy"
    check_window: 900
    expected_duration: 300
    category: "deploy"
```

**`check_window`** = if the workflow already finished by the time Wander starts, how far back should we still accept it as "the run we triggered"? Set this to ~6x `expected_duration`.

**Auto-generate** for a repo:
```bash
cd /path/to/repo
"$WANDER_HOME/scripts-registry.sh" scan-workflows --auto-scope
```

Default `check_window` when unconfigured: 300s.

---

## Canonical usage patterns

### After any git push

```bash
git push origin main && "$WANDER_HOME/watch-workflow-bg.sh" ci.yml
```

### With project wrapper (recommended for teams)

```bash
# scripts/watch-ci.sh
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WANDER_DIR="${WANDER_HOME:-$(dirname "$REPO_ROOT")/wander}"
exec "$WANDER_DIR/watch-workflow-bg.sh" ci.yml "$@"
```

Then: `git push && ./scripts/watch-ci.sh`

### EAS mobile build (via GHA wrapper)

If your EAS build is triggered by a GHA workflow (e.g. `eas-build.yml`):

```bash
git push origin feat/my-branch && "$WANDER_HOME/watch-workflow-bg.sh" eas-build.yml
```

If EAS is triggered directly via CLI (no GHA), Wander cannot monitor it natively — consider creating a `workflow_dispatch` wrapper.

### Manual workflow dispatch

```bash
gh workflow run deploy.yml --ref main
"$WANDER_HOME/watch-workflow-bg.sh" deploy.yml main
```

---

## Edge cases

| Scenario | Behavior |
|----------|----------|
| Workflow finishes before Wander starts | Detected via `check_window`; instant result + notify |
| Run not appearing after 30s | Wander waits up to 30s, then exits with tips |
| Wrong branch filter on workflow | No run found; Wander reports and exits |
| Very short workflow (<30s) | Fast path: `check_window` catches it immediately |
| Very long workflow (>10min) | Use detached mode; logs survive terminal close |

---

## When a task fails

```bash
# View failed step logs
gh run view <RUN_ID> --log-failed

# Re-run only failed jobs
gh run rerun <RUN_ID> --failed
```

---

## WANDER_HOME resolution

1. `$WANDER_HOME` env var
2. Sibling of current repo: `$(dirname "$REPO_ROOT")/wander`
3. Default: `~/code/wander`

---

## Known limitation: non-GHA tasks

Wander v1 is GitHub Actions-native. For tasks outside GHA (EAS CLI, Railway CLI, custom scripts), the correct pattern is:

1. Wrap the task in a GHA `workflow_dispatch` workflow.
2. Trigger via `gh workflow run`.
3. Monitor with Wander.

A future version may support pluggable backends (EAS, Railway, etc.) via a task adapter layer.

---

## Reference

- [Wander README](https://github.com/ERerGB/wander)
- [EDGE_CASES.md](https://github.com/ERerGB/wander/blob/main/EDGE_CASES.md)
- [COFFEE_BREAK.md](https://github.com/ERerGB/wander/blob/main/COFFEE_BREAK.md)
