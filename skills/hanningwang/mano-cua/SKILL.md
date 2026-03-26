---
name: mano-cua
description: Computer use for GUI automation tasks via VLA models. Use when the user describes a task in natural language that requires visual screen interaction and no API or CLI exists for the target app.
homepage: https://github.com/HanningWang/mano-skill
metadata: {"openclaw": {"emoji": "🖥️", "install": [{"id": "brew", "kind": "brew", "formula":"HanningWang/tap/mano-cua", "bins":["mano-cua"],"label": "Install mano-cua (brew)"}]}}
---

# mano-cua

Desktop GUI automation driven by natural language. Captures screenshots, sends them to a cloud-based hybrid vision model, and executes the returned actions on the local machine — click, type, scroll, drag, and more.

## Requirements

- A system with a **graphical desktop** (macOS / Windows / Linux)
- `mano-cua` binary installed

### Installation

**macOS / Linux (Homebrew):**

```bash
brew install HanningWang/tap/mano-cua
```

**Windows:**

Download the latest `mano-cua-windows.zip` from [GitHub Releases](https://github.com/HanningWang/mano-skill/releases), extract it, and add the folder to your `PATH`.


## Usage

```bash
# Run a task
mano-cua run "your task description"

# Stop the current running task
mano-cua stop
```

```
usage: fty-nb [-h] command [task]

VLA Desktop Automation Client

positional arguments:
  command     Command: 'run' or 'stop'
  task        Task description (required for 'run')

options:
  -h, --help  show this help message and exit
```

> **Note:** Only one task can run at a time per device. If you need to start a new task, first stop the current one with `mano-cua stop`.

## Examples

```bash
# Run a task
mano-cua run "Open WeChat and tell FTY that the meeting is postponed"
mano-cua run "Search for AI news in Xiaohongshu and show the first post"

# Stop the current task (use before starting a new one)
mano-cua stop
```

## How It Works

The current screenshot is captured and sent to the cloud at each step. A hybrid vision solution decides the next action:

- **Mano model** — handles straightforward, lightweight tasks with rapid output.
- **Claude CUA model** — handles complex tasks requiring deeper reasoning.

The system automatically selects the appropriate model based on task complexity.

## Supported Interactions

click · type · hotkey · scroll · drag · mouse move · screenshot · wait · app launch · url direction

## Status Panel

A small UI panel is displayed on the top-right corner of the screen to track and manage the current session status.

## Data, Privacy & Safety

- **What is sent:** Screenshots of the primary display and the task description are sent to `mano.mininglamp.com` — these are the minimal inputs required for the vision model to determine the next action.
- **What is NOT sent:** No local files, clipboard content, or system credentials are read or transmitted. All network calls are in a single module ([`task_model.py`](https://github.com/HanningWang/mano-skill/blob/main/visual/model/task_model.py)) for easy review.
- **Authentication:** No API key or credentials are required. The client identifies itself with a locally generated device ID (`~/.myapp_device_id`) — no secrets are embedded in the binary.
- **Supply chain:** The full client is [open source](https://github.com/HanningWang/mano-skill). The Homebrew formula builds directly from this public source, ensuring the installed binary is fully auditable.
- **User control:** Users can stop any session at any time via the UI panel or `mano-cua stop`.

## Important Notes

- **Do not use the mouse or keyboard during the task.** Manual input while mano-cua is running may cause unexpected behavior.
- **Multiple displays:** only the primary display is used. All mouse movements, clicks, and screenshots are restricted to that display.

## Platform Support

macOS is the preferred and most tested platform. Adaptations for Windows and Linux are not yet fully completed — minor issues are expected.

