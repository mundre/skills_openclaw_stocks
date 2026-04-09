# Skill Review Mode
#tags: skills review

## Skill Architecture Mode
Use this mode when the topic is a skill or a skill-adjacent artifact.

### Required review angles
1. purpose clarity
2. scope correctness
3. runtime determinism
4. weak-model execution reliability
5. ambiguity and hidden assumptions
6. safety, halt, and rollback behavior
7. operability in real agent loops
8. state and continuity needs
9. docs architecture
10. tests and validation needs
11. integration quality with other skills
12. publishable quality when the asked scope includes shipping or readiness

### Skill class first
Classify the skill before critique:
- memory skill
- continuity skill
- network diagnosis skill
- orchestrator skill
- tooling or skill-creator skill
- workflow or methodology skill
- infra or deployment skill
- hybrid skill

Then add the class checklist from `references/skill-classes.md`.

### Round 1 contract for skills
A skill review round 1 must include:
- Skill Topic
- Skill Intent
- Current Skill Role
- What Kind of Skill Task This Is
- My Current Position
- What Seems Strong Already
- What Might Still Be Weak
- Required Review Angles
- Task Material with the real `SKILL.md` pasted inline
- Skill Review Contract
- Questions

### Skill Review Contract
Act as a critical skill architect, not just a reviewer.
For every major weakness, name the issue, explain why it matters, classify severity, propose the smallest strong fix, and say whether the fix belongs in runtime, docs, tests, schema, scripts, or integrations.

### Skill deliverables
A skill task should end with:
- what to keep
- what to rewrite
- what to add
- what to delete
- whether another round is still worth it
- a lifecycle status for the asked scope

### Lifecycle status
Use exactly one of:
- Draft
- Reviewed
- Hardened
- Validated
- Packaged
- Published
- Deferred
