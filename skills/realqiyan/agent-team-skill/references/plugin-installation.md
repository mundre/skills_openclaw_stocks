# Plugin Installation Guide

This guide explains how to install and configure the OpenClaw plugin for the Agent Team skill.

## What the Plugin Does

The Agent Team plugin automatically injects team member information and collaboration rules into the AI agent's system context at session start. This enables:

- **Team awareness**: AI agents know all team members, their roles, and expertise
- **Task delegation rules**: Built-in guidance for delegating tasks to appropriate team members
- **Six-phase workflow**: SEARCH → RECORD → ORIENT → PLAN → DISPATCH → REVIEW → UPDATE

Without the plugin installed, the skill's CLI tool (`scripts/team.py`) can still manage team data, but the AI agent won't automatically receive team context.

## Why Installation is Required

The plugin is essential because it:

1. Reads team data from `~/.agent-team/team.json`
2. Formats it as markdown for system context
3. Injects it via the `before_prompt_build` hook

This happens automatically at the start of each session, ensuring the AI agent always has up-to-date team information.

## Installation Methods

### Method 1: Symbolic Link (Recommended)

Create a symbolic link to the global OpenClaw extensions directory:

```bash
ln -s $(pwd)/integrations/openclaw/agent-team ~/.openclaw/extensions/agent-team
```

### Method 2: Config File Path

Specify the plugin path in your OpenClaw config file (`~/.openclaw/config.json`):

```json
{
  "plugins": {
    "load": {
      "paths": ["/path/to/agent-team-skill/integrations/openclaw/agent-team"]
    },
    "entries": {
      "agent-team": {
        "enabled": true
      }
    }
  }
}
```

Replace `/path/to/agent-team-skill` with the actual path to this project.

### Method 3: Development Mode

For development, you can run OpenClaw with the plugin path directly:

```bash
openclaw --plugin-path ./integrations/openclaw/agent-team
```

## Configuration Options

The plugin supports the following configuration options:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable or disable the plugin |
| `dataFile` | string | `~/.agent-team/team.json` | Custom path to team data file |

### Custom Data File

To use a custom data file location:

```json
{
  "plugins": {
    "entries": {
      "agent-team": {
        "enabled": true,
        "dataFile": "/custom/path/team.json"
      }
    }
  }
}
```

## Verification

### Step 1: Check Plugin Installation

Verify the plugin is recognized by OpenClaw:

```bash
openclaw --list-plugins
```

You should see `agent-team` in the output.

### Step 2: Add Team Members

Add at least one team member to test:

```bash
python3 scripts/team.py update \
  --agent-id "test-agent" \
  --name "Test Agent" \
  --role "Developer" \
  --is-leader "true" \
  --enabled "true" \
  --tags "test" \
  --expertise "testing" \
  --not-good-at "none"
```

### Step 3: Start a Session

Start an OpenClaw session and verify the team context is injected. You should see a log message like:

```
[agent-team] Injecting team context (1 members)
```

### Step 4: Clean Up Test Data (Optional)

Remove test data:

```bash
python3 scripts/team.py reset
```

## Troubleshooting

### Plugin Not Loading

- Verify the symbolic link exists: `ls -la ~/.openclaw/extensions/agent-team`
- Check the config file syntax is valid JSON
- Ensure OpenClaw has read permissions for the plugin directory

### No Team Context Injected

- Verify team data exists: `cat ~/.agent-team/team.json`
- Check at least one member has `enabled: true`
- Look for error messages in OpenClaw logs

### Data File Not Found

- The plugin gracefully handles missing data files (logs a message but doesn't error)
- Create the data directory: `mkdir -p ~/.agent-team`
- Use `scripts/team.py update` to create the initial data file