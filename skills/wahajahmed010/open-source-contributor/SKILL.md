# open-source-contributor

Autonomous GitHub contribution agent with graduated complexity levels.

## Description

Scouts small open-source projects for contribution opportunities, analyzes issues, writes fixes using qwen3-coder-next:cloud, and submits PRs under your identity.

## When to Use

✅ **USE when:**
- You want to contribute to open source during quiet hours
- You want AI-assisted coding with graduated complexity
- You want to build contribution history gradually

❌ **DON'T use when:**
- Repository involves security/auth/cryptography
- Issue scope is unclear or ambiguous
- You've hit rejection rate threshold (>30%)

## Configuration

```json
{
  "github_token": "ghp_xxxxxxxxxxxx",
  "max_repos_per_night": 3,
  "complexity_level": 1,
  "approval_threshold": 0.5,
  "quiet_hours": {"start": "23:00", "end": "07:00"},
  "blocked_patterns": ["auth", "crypto", "token", "key", "password", "credential"]
}
```

## Complexity Levels

| Level | Scope | Max Repos | Approval Rate Required |
|-------|-------|-----------|------------------------|
| 1 | Typo/link fixes | 3 | None |
| 2 | README/doc fixes | 3 | >50% |
| 3 | Simple code fixes | 2 | >70% |
| 4 | Moderate code fixes | 1 | >90% |

## Pipeline

1. **Scout** → Find candidates with `good first issue` label
2. **Analyzer** → Scope understanding + complexity assessment
3. **Coder** (qwen3-coder-next:cloud) → Write fix
4. **Tester** → Run test suite
5. **Reviewer** → Pre-flight checklist
6. **Submitter** → Open PR

## Usage

```bash
# Manual run
python3 ~/.openclaw/skills/open-source-contributor/scripts/contrib-pipeline.py

# Check status
cat ~/.openclaw/workspace/contrib-scout/logs/contributions.jsonl | tail -20
```

## Safety

- Append-only audit logging
- Auto-pause if rejection rate >30%
- Blocked file patterns enforced
- AI disclosure in every PR
- Test suite must pass

## Storage

```
~/.openclaw/workspace/contrib-scout/
├── repos/              # Cloned repositories
├── drafts/             # Pending contributions
├── logs/               # Activity + audit trail
├── config.json         # User settings
└── approval-tracking.json  # PR outcomes
```
