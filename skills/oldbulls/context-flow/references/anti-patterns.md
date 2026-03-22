# Context Governance Anti-Patterns

## Purpose

This file records common failure modes in group collaboration, child-agent delegation, subagent usage, phase checkpoints, and resume flows.

Read it when:
- a collaboration thread becomes noisy
- a child agent drifts beyond scope
- a subagent starts carrying too much context
- a resume flow risks reviving the wrong task line
- outputs are becoming vague, overloaded, or misaligned

## Anti-pattern: Dumping the full transcript into a child agent

### Symptoms
- The child agent starts mixing old and new task lines
- Scope expands without explicit approval
- Output becomes broad, generic, or inconsistent

### Why this is bad
- Most transcript content is not actually needed for the local task
- The important constraints become harder to preserve
- The child agent wastes context budget on irrelevant history

### Preferred pattern
- Send a task card, not the whole transcript
- Specify goal, scope, constraints, and output format
- Put stable background into docs or memory files

## Anti-pattern: Using the group as the full execution context

### Symptoms
- Long logs, long reasoning, and large diffs appear in the group
- Status sync and execution detail get mixed together
- The thread becomes hard to scan and hard to steer

### Why this is bad
- Group chat should be for alignment, not full execution storage
- Noise makes it easier to lose the task line
- Human collaborators stop seeing the real state quickly

### Preferred pattern
- Keep group updates thin
- Use the group for owners, states, blockers, and short summaries
- Keep detailed execution context in docs, memory, or local task cards

## Anti-pattern: Letting a subagent carry the full task line

### Symptoms
- A subagent starts reasoning about the overall strategy instead of its local job
- It drifts into unrelated edits or analysis
- It returns too much narrative and too little local evidence

### Why this is bad
- Subagents are best used as short-horizon workers
- Giving them the whole task line weakens task isolation
- Local verification quality drops when the scope becomes broad

### Preferred pattern
- Give subagents one local problem
- Minimize background aggressively
- Require local conclusions, evidence, and next-step suggestions

## Anti-pattern: Continuing after interruption without a checkpoint

### Symptoms
- The resumed run reconnects to the wrong task line
- Old constraints are forgotten or partially remembered
- The run feels active but the main objective is off

### Why this is bad
- Interruptions break the continuity that long tasks depend on
- Raw transcript replay is not the same as a trustworthy checkpoint
- Recovery without re-anchoring creates silent drift

### Preferred pattern
- Create a short checkpoint before resuming
- Resume from current goal, completed work, active constraints, and next step
- If the new task is not explicit, ask before continuing

## Anti-pattern: Treating injected historical memory as task authority

### Symptoms
- Old message ids or historical notes get revived as if they are current orders
- The system resumes work the user did not explicitly ask for now
- The active task line becomes polluted by stale intent

### Why this is bad
- Historical memory is context, not current authorization
- Injected memory may be incomplete, stale, or explicitly untrusted
- This is a common source of wrong-task recovery

### Preferred pattern
- Treat historical memory as a clue only
- Require a current explicit task signal before resuming execution
- Prefer summaries and current user instructions over old injected fragments

## Anti-pattern: Mixing status sync with execution detail

### Symptoms
- Status sections become mini-reports
- A status update contains logs, reasoning, and file-level detail
- Readers cannot tell what is done versus what is being analyzed

### Why this is bad
- Status sync should reduce ambiguity, not add more content
- Mixed layers make coordination slower
- The group loses the ability to scan quickly

### Preferred pattern
- Keep status sync short and structured
- Put deep detail in a separate artifact when needed
- Use `分工安排` / `当前状态` / `协作摘要` only when there is real collaboration

## Anti-pattern: Expanding scope without re-anchoring constraints

### Symptoms
- The agent quietly starts doing adjacent tasks
- "Nice to have" work gets mixed into the main objective
- Previously agreed boundaries disappear from the output

### Why this is bad
- Scope drift is one of the main ways context gets overloaded
- Extra work often arrives without updated constraints
- Quality drops because the task is no longer well bounded

### Preferred pattern
- Re-anchor constraints before expanding scope
- Split adjacent work into a new stage or a new task card
- Make the scope change explicit instead of implicit
