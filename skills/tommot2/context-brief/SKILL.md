---
name: context-brief
description: "Optimize OpenClaw context window usage for longer, more productive conversations. Provides smart compaction strategies, critical information preservation techniques, and post-compaction recovery guidance. Completely stateless — reads NO local files, writes NO files, accesses no credentials or personal data. Use when: (1) conversations get long and agent starts losing context, (2) agent seems to forget earlier messages or decisions, (3) context window errors occur, (4) user wants to maximize conversation depth without losing important context, (5) user says 'compress context', 'save conversation', 'you keep forgetting', 'context too long'. Homepage: https://clawhub.ai/skills/context-brief"
---

# Context Brief

Maximize conversation depth by intelligently managing context.

**This skill provides strategies and guidance only.** It does NOT read or write any files, memory, or configuration. All context management happens within the current session.

## Language

Detect from the user's message language. Default: English.

## When to Activate

- Conversation exceeds ~50% of model's context window
- Agent responses reference outdated information
- User mentions forgetting or losing context
- Compaction has occurred and important info was lost
- User asks: "context check", "hva husker du", "save context", "context status"

## Context Health Check

Run periodically or when user asks. Check via `session_status`:

1. **Context usage %** — Tokens used vs window size
2. **Compaction count** — How many times context has been compacted
3. **Cache hit rate** — Efficiency indicator
4. **Key information inventory** — What critical facts exist in conversation

**Report format** (adapts to user language):

```markdown
## 🧠 Context Health Report

| Metric | Value |
|--------|-------|
| Usage | X% (Xk / Xk tokens) |
| Compactions | X |
| Cache hit | X% |
```

## Compaction Strategy

When context grows large, recommend or execute compaction in this order:

### Step 1: Identify Critical Information

Scan conversation for:
- User preferences and decisions
- Pending tasks and commitments
- Project context and goals
- Recent instructions that override earlier ones

**⚠️ NEVER persist secrets or credentials** — do not include API keys, passwords, tokens in any summaries or briefs.

### Step 2: Generate Context Brief

Create an in-session context brief (5–10 bullet points) summarizing essential state. This brief exists only in the current conversation — it is NOT written to any file.

```markdown
## Context Brief — {date}

### Active Decisions
- [Decision 1]
- [Decision 2]

### Pending Tasks
- [ ] [Task 1]

### Key Context
- [Context detail that must survive compaction]
```

### Step 3: Prioritized Retention

When compaction happens:
1. The brief above should be the last thing discussed before compaction
2. After compaction, the agent retains recent messages but the brief ensures critical context survives

### Step 4: Post-Compaction Recovery

After compaction occurs:
1. If the context brief was generated before compaction, reference it to restore state
2. Acknowledge to user (in their language): "Context ble kompakt. Viktige beslutninger er bevart i samtalen."
3. Ask the user to confirm any critical items if uncertain

## Guidelines for Agent

1. **Proactive briefs** — Don't wait for compaction. Generate context summaries when conversations get long.
2. **Concise summaries** — A 10-line brief beats a 100-line dump.
3. **Never write files** — This skill operates entirely within session context.
4. **Never read files** — This skill operates entirely within session context.
5. **Timestamp everything** — ISO 8601 for technical fields, user's locale format for display.

## Output

When context optimization is performed (adapts to user language):

```markdown
## 🧠 Context Optimized

- Context brief generated (session-only)
- Key items preserved:
  - [Item 1]
  - [Item 2]
- Freed ~X tokens of context space
```

## More by TommoT2

- **setup-doctor** — Diagnose and fix OpenClaw setup issues
- **locale-dates** — Format dates/times per locale (100+ patterns)
- **tommo-skill-guard** — Security scanner for all installed skills

Install the full starter pack:
```bash
clawhub install setup-doctor locale-dates tommo-skill-guard
```
