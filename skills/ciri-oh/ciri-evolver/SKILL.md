---
name: evolver
description: "Skill self-evolution engine for OpenClaw agents. Based on GEP (Genome Evolution Protocol), scans workspace memory/ logs to detect error signals, matches Gene templates to generate evolution suggestions. Supports 4 strategies (balanced/innovate/harden/repair-only), Loop daemon, Review mode, Lifecycle management. 技能自进化引擎."
---

# Evolver - 技能自进化引擎 v3.0.4

> **Version**: 3.0.4
> **License**: GNU General Public License v3.0 (GPL-3.0)
> **Copyright**: 2026

---

## Open Source Attribution | 开源许可与归属

1. **Inspired by GEP (Genome Evolution Protocol)**
   GEP protocol proposed by [EvoMap](https://evomap.ai), this skill uses its concepts and architecture.

2. **Independent OpenClaw Implementation**
   Core code (`bin/evolve.js`) is independently developed for OpenClaw.

Full license text: see [LICENSE](LICENSE).

---

## Quick Start | 快速开始

### Install

```bash
clawhub install ciri-evolver
```

### Run

```bash
# Single evolution scan
node skills/evolver/bin/evolve.js

# Test mode (no file writes)
node skills/evolver/bin/evolve.js --dry-run
```

### Background Daemon

```bash
# Start daemon (auto-runs every 4 hours)
node skills/evolver/bin/evolve.js start

# Check status
node skills/evolver/bin/evolve.js status

# Stop
node skills/evolver/bin/evolve.js stop
```

---

## Core Features | 核心功能

| Feature | Description |
|---------|-------------|
| Signal Detection | Scans memory/ logs for 10+ error patterns |
| Gene Matching | Matches signals to reusable strategy templates |
| Capsule Management | Stores validated fixes with diff + confidence |
| 4 Evolution Strategies | balanced / innovate / harden / repair-only |
| Loop Mode | Continuous background daemon |
| Review Mode | Pause for human confirmation |
| Lifecycle | start / stop / status / check |
| Bootstrap | Auto-creates Gene library on first run |

---

## Supported Error Signals | 支持的错误信号

| Signal | Meaning |
|--------|---------|
| TimeoutError | Network timeout |
| ECONNREFUSED | Connection refused |
| RateLimitError | Rate limit exceeded |
| AuthError | Authentication failed |
| ContextOverflow | Context memory exceeded |
| ModelFallback | Model routing fallback |
| GatewayTimeout | Gateway timeout |
| ParseError | Parse/syntax error |
| FileNotFound | File not found |
| DeprecationWarning | Deprecated API warning |

---

## Commands | 命令

| Command | Description |
|---------|-------------|
| `evolve.js` | Single evolution cycle |
| `evolve.js --dry-run` | Test mode (no file writes) |
| `evolve.js --loop` | **Continuous daemon mode** (setInterval, no child process) |
| `evolve.js --review` | Review mode (pause + human confirm) |
| `evolve.js --strategy=<name>` | Set evolution strategy |
| `evolve.js start` | Start daemon in background (nohup) |
| `evolve.js stop` | Graceful stop (SIGTERM) |
| `evolve.js status` | Show running state |
| `evolve.js check` | Health check + auto-restart if stagnant |

### Strategies | 策略

| Strategy | Innovate | Optimize | Repair |
|----------|----------|---------|--------|
| `balanced` | 50% | 30% | 20% |
| `innovate` | 80% | 15% | 5% |
| `harden` | 20% | 40% | 40% |
| `repair-only` | 0% | 20% | 80% |

---

## File Structure | 文件结构

```
skills/evolver/
├── SKILL.md              # This file
├── LICENSE              # GPL-3.0 license
├── bin/
│   └── evolve.js        # Core script
└── assets/
    ├── GENES.md         # Gene library (editable)
    ├── CAPSULES.md      # Validated fixes
    └── EVOLUTION_EVENTS.md  # Evolution logs
```

---

## Example Output | 示例输出

```
Evolver - Skill Self-Evolution Engine v3.0.4

   Strategy: balanced
   Mode: SINGLE

Signals detected: ModelFallback
Genes: 5 total, 1 matched

================================================================================
           GEP Evolution Prompt
================================================================================

> Evolution ID: EVT-YYYYMMDD-XXXX
> Strategy: balanced (innovate:0.5 optimize:0.3 repair:0.2)

## Detected Signals
  - ModelFallback

## Matched Genes
  ### [20260416-004] repair
  Signals: ModelFallback
  Strategy:
    Fix model routing issues...

## Suggested Actions
  1. [repair] Fix model routing + log fallback chain

## Evolution Event Record
{ "type": "EvolutionEvent", ... }

Evolution event recorded.
```

---

## Troubleshooting | 故障排除

**Q: "No such file or directory"?**  
A: Run from correct workspace directory or use absolute path.

**Q: Background process gone?**  
A: Check with `evolve.js status`, restart with `evolve.js check`.

**Q: No signals detected?**  
A: Check `memory/` directory for logs containing error keywords.

**Q: No gene match?**  
A: Edit `assets/GENES.md` to add new gene templates.

---

## Architecture | 架构说明

### Daemon Loop Mode
`--loop` uses Node.js `setInterval` in a single process — **no child process spawning**.
This avoids T1140 (Inline Python code execution) false positives in sandbox scans.

The `start` command uses `nohup` to background the process, which is distinct from
`child_process.spawn` and typically does not trigger MITRE ATT&CK sandbox heuristics.

### Process Lifecycle
```
node evolve.js --loop     → foreground daemon (setInterval, process stays attached)
node evolve.js start      → background daemon (nohup + &, process detaches)
node evolve.js stop       → SIGTERM graceful shutdown
node evolve.js check      → health check + restart if stagnant (>8h no run)
```

## Changelog | 版本历史

- **v3.0.4**: Reset CAPSULES.md to empty. Cleared Evolution ID in Example Output.
- **v3.0.3**: Removed runtime data from published package (evolver-state.json, evolver.pid, EVOLUTION_EVENTS.md). Reset to clean initial state.
- **v3.0.2**: Replaced `child_process.spawn` daemon with `setInterval` + `nohup`. Eliminates T1140 sandbox false positive. `--loop` is now single-process. Fixed nohup PID capture bug.
- **v3.0.1**: Fixed header comments, usage docs, version string (v2.0 -> v3.0)
- **v3.0.0**: Removed fetchSkill and autoIssue functions. Cleaner, safer, no exec/fetch.
- v2.0.3: Code optimizations (regex pre-compilation, path traversal protection)
- v2.0.0: Full feature set (Loop, Review, Lifecycle)
- v1.0.0: Initial release (Signal Detection + Gene Matching)
