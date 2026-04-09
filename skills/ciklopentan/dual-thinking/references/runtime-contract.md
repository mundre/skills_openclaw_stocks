# Runtime Contract
#tags: skills review

## External Required Output
These fields are the visible runtime contract. Keep them short and machine-checkable.

### Enum blocks
Use these values exactly.
- `MODE`: `general-decision-review` | `artifact-review` | `artifact-improvement` | `skill-review` | `skill-rewrite` | `skill-hardening` | `skill-publish-readiness` | `weak-model-optimization` | `analysis-only`
- `SKILL_CLASS`: `memory` | `continuity` | `network` | `orchestrator` | `tooling` | `workflow` | `infra` | `hybrid` | `na`
- `ORCHESTRATOR_MODE`: `local` | `api` | `multi`
- `PATCH_STATUS`: `none` | `proposed` | `applied` | `re-reviewed` | `deferred`
- `CONSULTANT_QUALITY`: `strong` | `mixed` | `weak` | `failed`
- `CONTINUATION_SIGNAL`: `continue` | `stop` | `missing` | `ambiguous`

### Minimum Required Round Block
Always emit these fields.
- `ROUND`
- `TOPIC`
- `MODE`
- `SESSION`
- `DECISION`
- `PATCH_STATUS`
- `CONTINUATION_SIGNAL`
- `NEXT_ACTION`
- `CHAT_CONTINUITY`
- `RESUME_SNIPPET`

### Extended Round Block
Add these when useful.
- `SKILL_CLASS`
- `ORCHESTRATOR`
- `ORCHESTRATOR_MODE`
- `CONSULTANT_QUALITY`
- `COMPARISON`
- `DOC_STATUS`
- `TEST_STATUS`
- `VALIDATION_STATUS`
- `PUBLISH_STATUS`

### Minimum viable paths
#### For skill topics
1. Route.
2. Classify the skill.
3. Paste the real skill text inline.
4. Get critique.
5. Decide.
6. Patch if accepted.
7. Emit the round block.
8. Continue or stop.

#### For non-skill topics
1. Route.
2. Paste the real artifact or context inline.
3. Get critique.
4. Decide.
5. Patch if needed.
6. Emit the round block.
7. Continue or stop.

### Failure -> next action
| Failure | Next action |
|---|---|
| artifact not pasted | ask once, request inline artifact, no path-only review |
| second request still no artifact | switch to `analysis-only` and stop patch loop |
| consultant weak | retry once with a narrower prompt |
| consultant weak again | switch to `analysis-only` or stop as blocked |
| continuation missing | default `continue` |
| session polluted | open recovery chat, paste latest accepted artifact, add `RESUME_SNIPPET` |
| accepted fix not patched | patch before next review |
| validation failed | block packaging and publishing |

### Local mode
- If `ORCHESTRATOR_MODE: local`, set `ORCHESTRATOR: local`.
- Do not use model names in local mode.
- Do not fake an external consultant call in local mode.
- Omit `CONSULTANT_QUALITY` in local mode unless a formal self-critique pass was explicitly run.
- If a formal self-critique pass was explicitly run in local mode, use `strong`, `mixed`, `weak`, or `failed` honestly.

### Meaningful round rule
A round is meaningful only if at least one of these happened:
- a grounded flaw was identified
- a decision changed or was defended with explicit reasoning
- a real patch was accepted or applied
- a concrete risk was surfaced
- a validated stop signal was explicitly produced

If none of those happened, the round is non-meaningful.
Do not treat it as convergence.
Narrow the next prompt or switch mode according to failure rules.

### Skill closure rule
For skill topics, stop only if all are true for the asked scope:
- `CONTINUATION_SIGNAL: stop`
- you also agree
- no accepted fix remains unpatched
- no runtime-critical ambiguity remains
- no must-have docs remain missing
- no must-have tests remain missing
- no unresolved blocker remains

## Internal Execution Markers
These are service markers for the agent runtime. Do not present them as user-facing requirements.
- `ROUTE_COMPLETE`
- `STATE_EMITTED`
- `CHAT_CONTINUITY: new|reused|recovery`
- `ARTIFACT_LOADED`
- `PROMPT_READY`
- `RESPONSE_RECEIVED`
- `DECISION_MADE`
- `ROUND_EMITTED`
- `PATCH_GATE_CHECKED`
- `PATCH_APPLIED`
- `CHECKS_COMPLETE`
- `VALIDATION_STATUS: passed|failed|blocked`
- `FLOW_STATUS: continued|terminated`

## Notes
- `local` means no external consultant call.
- `api` means one consultant is used serially.
- `multi` means explicitly requested alternation before round 1.
- `analysis-only` is a valid mode, not a failure state.
- In local mode, omit `CONSULTANT_QUALITY` unless a formal self-critique pass was actually run.
- If continuation is missing, default to `continue`.
- If a fix is accepted, patch before the next review round.
- If validation fails, block packaging and publishing.
