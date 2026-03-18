---
version: "2.0.0"
name: Acmesh
description: "A pure Unix shell script ACME client for SSL / TLS certificate automation acmesh, shell, acme, acme-challenge, acme-protocol, acme-v2."
author: BytesAgain
homepage: https://bytesagain.com
source: https://github.com/bytesagain/ai-skills
---

# Acmesh

A multi-purpose utility tool for managing data entries, searching records, and exporting information from the command line. Acmesh provides a lightweight, file-based data management system with timestamped logging and full CRUD operations.

## Commands

| Command | Description |
|---------|-------------|
| `run` | Execute the main function with provided arguments |
| `config` | Display configuration file path and log the action |
| `status` | Show current operational status (reports "ready" when healthy) |
| `init` | Initialize the data directory and prepare the environment |
| `list` | List all entries stored in the data log file |
| `add` | Add a new timestamped entry to the data log |
| `remove` | Remove a specified entry from the data store |
| `search` | Search entries by keyword (case-insensitive grep) |
| `export` | Export all stored data to stdout |
| `info` | Display version number and data directory path |
| `help` | Show the full help message with all available commands |
| `version` | Print the current version string |

## Data Storage

All data is stored in plain text files under the data directory:

- **Data log**: `$DATA_DIR/data.log` — stores all entries added via `add`, one per line with date prefix
- **History log**: `$DATA_DIR/history.log` — audit trail of every command executed with timestamps
- **Config**: `$DATA_DIR/config.json` — referenced by the `config` command

Default data directory: `~/.local/share/acmesh/`

Override by setting the `ACMESH_DIR` environment variable:

```bash
export ACMESH_DIR="/custom/path/to/acmesh"
```

## Requirements

- Bash (with `set -euo pipefail` support)
- Standard Unix utilities: `grep`, `cat`, `date`, `echo`
- No external dependencies or API keys required

## When to Use

1. **Quick data logging** — When you need a fast CLI-based way to log timestamped entries without setting up a database
2. **Searching through records** — When you need to find specific entries across your data log using keyword search
3. **Exporting data for reports** — When you need to dump all stored records to stdout or pipe them into another tool
4. **Lightweight task tracking** — When you want a minimal, file-based system to track items, notes, or events
5. **System initialization checks** — When you need to verify the tool is properly initialized and check its operational status

## Examples

```bash
# Initialize acmesh and verify status
acmesh init
acmesh status

# Add several entries to the data log
acmesh add "Deploy new SSL certificate for example.com"
acmesh add "Renew wildcard cert for *.staging.example.com"
acmesh add "Revoke expired certificate for old.example.com"

# List all stored entries
acmesh list

# Search for entries containing "wildcard"
acmesh search wildcard

# Export all data (pipe to a file)
acmesh export > backup.txt

# Check version and data directory info
acmesh info
acmesh version
```

## Output

All commands return output to stdout. You can redirect to a file:

```bash
acmesh export > output.txt
acmesh list > entries.txt
```

Every command execution is logged to `$DATA_DIR/history.log` for auditing purposes.

## Configuration

Set the `ACMESH_DIR` environment variable to change the data directory. Default: `~/.local/share/acmesh/`

```bash
# Example: use a custom directory
export ACMESH_DIR="$HOME/.acmesh-data"
acmesh init
```

---

Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
