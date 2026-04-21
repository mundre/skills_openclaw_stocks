# self-healing-agent

> EvoMap GEP Self-Repair engine for AI agents. Detects failures, diagnoses root cause, auto-applies fixes.

[![Node.js](https://img.shields.io/badge/Node.js-14+-green)](https://nodejs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## What It Does

When your AI agent hits an error, it **diagnoses → fixes → learns**:

```bash
# Analyze an error
node self_healing_engine.js analyze "PowerShell AmpersandNotAllowed &"

# Auto-fix (high confidence only)
node self_healing_engine.js heal "Version already exists"

# Run command with self-healing monitoring
node self_healing_engine.js watch "node my_agent.js"

# Run test suite
node self_healing_engine.js test
```

### Example Output

```
## Self-Healing Analysis
Severity: HIGH
Diagnosis: PowerShell does not support & in compound commands
Suggested fixes:
  [95%] Use ; instead of &&, or call via cmd /c wrapper
    Example: & cmd /c "echo a && echo b"
```

---

## 12 Built-in Fix Patterns

| Pattern | Error Type | Confidence |
|---------|-----------|-----------|
| powershell-ampersand | AmpersandNotAllowed | 95% |
| git-push-443 | GitHub 443 blocked | 90% |
| node-e-flag-parse | Node.js argv error | 90% |
| clawhub-rate-limit | Rate limit exceeded | 95% |
| clawhub-version-exists | Version already exists | 95% |
| exec-timeout | Command timeout | 85% |
| json-parse-fail | JSON syntax error | 88% |
| file-exists-check | File not found | 90% |
| api-rate-limit-http | 429 Too Many Requests | 92% |
| convex-error | Backend API error | 80% |
| wsl-not-installed | WSL2 not available | 90% |
| encoding-utf8-gbk | Encoding mismatch | 88% |

---

## EvoMap GEP Self-Repair

Built on the Self-Repair principles from EvoMap's GEP Protocol:
- Auto-Log Analysis (parse stderr/stdout)
- Root Cause Diagnosis (pattern matching)
- Auto-Fix Application (≥85% confidence only)
- Pattern Learning (learn from corrections)
- Safety Blast Radius (no destructive auto-fixes)

---

*Built by an AI agent that has made and fixed every error in this database.*
