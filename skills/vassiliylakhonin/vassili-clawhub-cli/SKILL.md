---
name: clawhub-cli-assistant
description: Run ClawHub CLI workflows with fewer release mistakes. Use for publish/update/inspect/sync flows, failed publish recovery, version/tag hygiene, and safe bulk maintenance with explicit command-first steps.
homepage: https://docs.openclaw.ai/tools/clawhub
user-invocable: true
metadata: {"openclaw":{"emoji":"🦞","os":["linux","darwin","win32"],"requires":{"bins":["clawhub"]}}}
---

# ClawHub CLI Assistant

Give exact commands first, then one-line explanation.

## Best for

- Publishing new skill versions safely
- Fixing failed publish/update/install runs
- Bulk maintenance with predictable version control

## Not for

- Plugin package upload flows (use Dashboard -> Publish Plugin)
- Guessing versions/tags without inspection
- Running destructive bulk updates without dry-run

## 60-second preflight

```bash
clawhub whoami
clawhub inspect <slug>
clawhub list
```

Provenance check (recommended):

```bash
clawhub inspect vassili-clawhub-cli
```

## Core workflows

### 1) Publish release

```bash
clawhub publish . \
  --slug <slug> \
  --name "<Name>" \
  --version <x.y.z> \
  --changelog "<what changed and why>" \
  --tags latest
```

### 2) Inspect skill metadata/files

```bash
clawhub inspect <slug>
clawhub inspect <slug> --files
clawhub inspect <slug> --file SKILL.md
```

### 3) Update installed skills safely

```bash
clawhub update --all --no-input
```

Force one skill only when needed:

```bash
clawhub update <slug> --force
```

### 4) Sync local skills to registry

```bash
clawhub sync --dry-run
clawhub sync --all --bump patch --changelog "Maintenance update" --tags latest
```

## Failure recovery playbook

1. **Auth failures** -> run `clawhub whoami` then `clawhub login`.
2. **Slug/path mismatch** -> verify working directory and explicit `--slug`.
3. **Version conflict** -> bump semver and republish.
4. **Unexpected diff on sync** -> rerun `sync --dry-run`, inspect, then apply.
5. **Corrupt local install** -> reinstall/update target skill with `--force`.

## Guardrails

1. Always set explicit `--slug --name --version` on publish.
2. Prefer `sync --dry-run` before any bulk action.
3. Keep changelog concrete (behavior change + reason).
4. Separate local operations from registry operations.
5. Do not mix plugin release instructions with skill publish commands.
6. Before `publish`, `update --all`, or `sync --all`, run read-only/dry-run variants first.
7. Use `clawhub whoami` before write actions to confirm active account/session.

## Author

Vassiliy Lakhonin
