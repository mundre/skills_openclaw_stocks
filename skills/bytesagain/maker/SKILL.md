---
name: maker
version: 1.0.0
author: BytesAgain
license: MIT-0
tags: [maker, tool, utility]
---

# Maker

File maker — create files, directories, templates, configs from presets.

## Commands

| Command | Description |
|---------|-------------|
| `maker help` | Show usage info |
| `maker run` | Run main task |
| `maker status` | Check current state |
| `maker list` | List items |
| `maker add <item>` | Add new item |
| `maker export <fmt>` | Export data |

## Usage

```bash
maker help
maker run
maker status
```

## Examples

```bash
# Get started
maker help

# Run default task
maker run

# Export as JSON
maker export json
```

## Output

Results go to stdout. Save with `maker run > output.txt`.

## Configuration

Set `MAKER_DIR` to change data directory. Default: `~/.local/share/maker/`

---
*Powered by BytesAgain | bytesagain.com*
*Feedback & Feature Requests: https://bytesagain.com/feedback*
