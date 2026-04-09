# Weak-Model Guide
#tags: skills review

## Weak-model cheat sheet
- route first
- for skill topics classify skill
- paste real artifact inline
- no path-only review
- minimum round block is enough if extended block is too heavy
- if accepted fix exists, patch before next review
- if continuation is missing, continue
- if response is vague twice, narrow or switch to `analysis-only`
- stop only on explicit convergence

## Minimum viable path
### For skill topics
1. Route.
2. Classify the skill.
3. Paste the real skill text inline.
4. Get critique.
5. Decide.
6. Patch if accepted.
7. Emit the minimum round block.
8. Continue or stop.

### For non-skill topics
1. Route.
2. Paste the real artifact or context inline.
3. Get critique.
4. Decide.
5. Patch if needed.
6. Emit the minimum round block.
7. Continue or stop.

## Design rules
- keep the visible runtime short
- flatten branch depth
- name the mode early
- avoid hidden cross-references for core enums and minimum fields
- keep stop rules short and explicit
- force a structured round block
- do not rely on vague prose as a success signal
- treat `analysis-only` as a valid mode, not a failure state

## Common failure patterns
- too many nested sections
- implicit state tracking
- long detours before the first action
- path-only review
- omitted docs or tests checks for the asked scope
- stopping after the first useful comment
- carrying publish logic into generic review too early

## Safe default
If the skill is ambiguous, choose the smallest safe action that still makes progress and record the choice.
