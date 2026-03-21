---
name: process
version: "3.0.1"
author: BytesAgain
homepage: https://bytesagain.com
source: https://github.com/bytesagain/ai-skills
license: MIT-0
tags: [process, tool, utility]
description: "List, filter, and manage system processes. Use when scanning running tasks, monitoring CPU usage, reporting memory hogs, alerting on runaway processes."
---

# process

Process manager.

## Commands

### `list`

List processes (filter by name)

```bash
scripts/script.sh list [filter]
```

### `top`

Top N processes by CPU/memory

```bash
scripts/script.sh top [n]
```

### `find`

Find processes by name

```bash
scripts/script.sh find <name>
```

### `tree`

Process tree

```bash
scripts/script.sh tree [pid]
```

### `ports`

Show listening ports

```bash
scripts/script.sh ports [port]
```

### `watch`

Watch process for 10 seconds

```bash
scripts/script.sh watch <pid>
```

### `mem`

Memory details for process

```bash
scripts/script.sh mem <pid>
```

### `cpu`

CPU details for process

```bash
scripts/script.sh cpu <pid>
```

### `env`

Show process environment

```bash
scripts/script.sh env <pid>
```

### `kill`

Send signal to process (default: TERM)

```bash
scripts/script.sh kill <pid> [signal]
```

### `stats`

System process statistics

```bash
scripts/script.sh stats
```

## Requirements

- bash 4.0+

---

*Powered by BytesAgain | bytesagain.com | hello@bytesagain.com*
