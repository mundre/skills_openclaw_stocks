---
name: dual-thinking
description: Second-opinion consultation plus automatic skill-engineering escalation for reviews, rewrites, hardening, weak-model optimization, packaging, testing, and publish readiness.
---

# Dual Thinking Method — v7.3.1

**Purpose:** consult a second model, then escalate skill topics into structured, patch-bearing skill engineering instead of generic advice when the topic is a skill or skill-adjacent artifact.

## Deterministic Router

Evaluate router conditions in order. The first matching semantic condition sets `MODE`.

If the user explicitly asked for alternating orchestrators before round 1, set `ORCHESTRATOR_MODE: multi`, keep one persistent session per orchestrator, and continue routing to set `MODE`.
If the user explicitly asked for findings only, set `MODE: analysis-only` and do not patch.
If the topic is a skill or skill-adjacent artifact and the requested outcome is a concrete rewrite, set `MODE: skill-rewrite`.
If the topic is a skill or skill-adjacent artifact and the requested outcome is runtime, safety, weak-model, or operability tightening, set `MODE: skill-hardening`.
If the topic is a skill or skill-adjacent artifact and the requested outcome is packaging, release gating, sharing, or publication, set `MODE: skill-publish-readiness`.
If the topic is a skill or skill-adjacent artifact and the requested outcome is weak-model clarity specifically, set `MODE: weak-model-optimization`.
If the topic is a skill or skill-adjacent artifact, set `MODE: skill-review`.
If the user wants an artifact changed, set `MODE: artifact-improvement`.
If the user wants an artifact assessed, set `MODE: artifact-review`.
Otherwise set `MODE: general-decision-review`.

If multiple intents overlap, keep the first-match semantic mode already encountered. Do not blend modes.

## Runtime Contract

Read `references/runtime-contract.md` when you need the visible round block, enum values, or marker split. Purpose: keep runtime output cheap and machine-checkable.

### External Required Output
These are the visible runtime rules.

#### Quick enum block
Use these values exactly.
- `MODE`: `general-decision-review` | `artifact-review` | `artifact-improvement` | `skill-review` | `skill-rewrite` | `skill-hardening` | `skill-publish-readiness` | `weak-model-optimization` | `analysis-only`
- `SKILL_CLASS`: `memory` | `continuity` | `network` | `orchestrator` | `tooling` | `workflow` | `infra` | `hybrid` | `na`
- `ORCHESTRATOR_MODE`: `local` | `api` | `multi`
- `PATCH_STATUS`: `none` | `proposed` | `applied` | `re-reviewed` | `deferred`
- `CONSULTANT_QUALITY`: `strong` | `mixed` | `weak` | `failed`
- `CONTINUATION_SIGNAL`: `continue` | `stop` | `missing` | `ambiguous`

#### Minimum viable path
##### For skill topics
1. Route.
2. Classify the skill.
3. Paste the real skill text inline.
4. Get critique.
5. Decide.
6. Patch if accepted.
7. Emit the round block.
8. Continue or stop.

##### For non-skill topics
1. Route.
2. Paste the real artifact or context inline.
3. Get critique.
4. Decide.
5. Patch if needed.
6. Emit the round block.
7. Continue or stop.

#### Local mode rule
If `ORCHESTRATOR_MODE: local`, set `ORCHESTRATOR: local`.
Do not use model names in local mode.
Do not imitate an external consultant call in local mode.
Omit `CONSULTANT_QUALITY` in local mode unless a formal self-critique pass was explicitly run.
If a formal self-critique pass was explicitly run, use `strong`, `mixed`, `weak`, or `failed` honestly.

#### Failure -> next action
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

#### Meaningful round rule
A round counts as meaningful only if at least one of these happened:
- a grounded flaw was identified
- a decision changed or was defended with explicit reasoning
- a real patch was accepted or applied
- a concrete risk was surfaced
- a validated stop signal was explicitly produced

If none of those happened, the round is non-meaningful.
Do not treat it as convergence.
Narrow the next prompt or switch mode according to failure rules.

#### Skill-task closure checklist
For skill topics, stop only if all are true for the asked scope:
- `CONTINUATION_SIGNAL: stop`
- I also agree
- no accepted fix remains unpatched
- no runtime-critical ambiguity remains for the asked scope
- no must-have docs remain missing for the asked scope
- no must-have tests remain missing for the asked scope
- no unresolved blocker remains for the asked scope

### Internal Execution Markers
These markers are service markers. They are not required user-visible output.
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

## Required Modes
Keep these modes available and route with the Deterministic Router. Read `references/modes.md` when you need the full mode table and mode-specific entry rules. Purpose: map task types.

## Skill Review Checklist

If the topic is a skill, always check the 12 review angles defined in `references/skill-review-mode.md`.

If a skill fix is accepted, the next round must include a real patch in the real artifact, not only a suggestion list.

## Patch State

Emit patch state when patch work exists, an accepted fix is still pending, or a patch blocker must be logged.
If no patch work exists, `PATCH_STATUS: none` is enough and `PATCH_MANIFEST` may be omitted.

```text
DRY_RUN: <ready|not-needed|blocked>
APPLY: <done|deferred|not-needed>
PATCH_MANIFEST:
- target: <file or section>
  change: <one-line description>
  status: <proposed|applied|re-reviewed|rejected>
  version_bump: <none|patch|minor|major>
```

## Round Output Contract

Every round ends with the shared block in `references/round-output-contract.md`.
For weak models, emit the minimum required round block first. Add extended fields only when they help.

## Publish Scope and Gate

Publish, release, and package gates are required only in `skill-publish-readiness`.
In `skill-review`, `skill-rewrite`, `skill-hardening`, and `weak-model-optimization`, run publish checks only if the user asked for shipping, distribution, packaging, or readiness.
Keep `PUBLISH_STATUS` even when publish scope is not requested.
If publish scope is not requested, `PUBLISH_STATUS` may be `Draft`, `Reviewed`, `Hardened`, or `Deferred`.
If `VALIDATION_STATUS: failed`, block packaging and publishing.

For `skill-publish-readiness`, require all of these before `PUBLISH_STATUS: Packaged`:
- validator passes
- weak-model validator passes
- package contents are explicit
- version string is explicit and matches the latest applied patch intent
- no unresolved must-have docs remain for the asked scope
- no unresolved must-have tests remain for the asked scope
- `TEST_STATUS: verified`, unless the user explicitly accepted deferral for the current scope

The heading version string (for example `v7.3.1`) is the authoritative source of truth for validation and packaging. Do not require a frontmatter version key.

When a patch changes runtime behavior, record a `version_bump` value in `PATCH_MANIFEST` and keep the visible version string aligned with the latest applied change.
Packaging means bundling `SKILL.md`, `references/`, and any required test or eval artifacts into one import-ready archive.

**Test status transitions:**
- `missing` -> no test artifact exists yet for the current asked scope.
- `planned` -> a concrete test or eval path has been specified but not yet updated and run.
- `updated` -> the relevant test or eval artifact was added or modified for the latest accepted patch.
- `verified` -> the relevant tests or evals were run successfully against the current artifact.

## Weak-Model Shortcut

If you cannot safely manage the full package flow, use this fallback.
Treat the current path as weak-model constrained if either of these is true:
- after two attempts, the consultant response still does not contain a usable `DECISION` field and a concrete non-empty `NEXT_ACTION`
- the consultant repeats generic praise after the real artifact was pasted inline
- the consultant cannot keep the mode, session, or next-action state stable across one round

1. Preserve the routed `MODE`. Output marker: `ROUTE_COMPLETE`.
2. Paste the real artifact inline and ask for 3 structural weaknesses plus the smallest fix for each. Output marker: `PROMPT_READY`.
3. Emit a simplified round block with `ROUND`, `MODE`, `DECISION`, `NEXT_ACTION`, and `RESUME_SNIPPET`. Output marker: `FLOW_STATUS: terminated`.
4. If the user later wants the full flow back, resume by pasting the last `RESUME_SNIPPET` and the latest accepted artifact into a normal round and routing again. Output marker: `RESUME_READY`.

## Execution

1. Route the topic with the Deterministic Router. Internal marker: `ROUTE_COMPLETE`.
2. Emit the minimum round state needed for the current round. Internal marker: `STATE_EMITTED`.
3. Decide chat continuity for the round. Reuse the same chat for the same topic unless explicit recovery is required. Internal marker: `CHAT_CONTINUITY: new|reused|recovery`.
4. Paste the real artifact inline. Internal marker: `ARTIFACT_LOADED`.
5. Generate the round prompt. Internal marker: `PROMPT_READY`.
6. Obtain critique using the resolved `ORCHESTRATOR_MODE` in the current topic chat. Internal marker: `RESPONSE_RECEIVED`.
7. Compare findings and set `DECISION`, `CONSULTANT_QUALITY`, and `NEXT_ACTION`. Internal marker: `DECISION_MADE`.
8. Emit the round block. Internal marker: `ROUND_EMITTED`.
9. Check whether patching is required. Internal marker: `PATCH_GATE_CHECKED`.
10. If patching is required, emit `DRY_RUN: ready`, patch the real artifact, emit `APPLY: done`, and emit `PATCH_MANIFEST`. Internal marker: `PATCH_APPLIED`.
11. Run the skill checklist, class checklist, and mode-specific checks when the topic is a skill. Internal marker: `CHECKS_COMPLETE`.
12. Validate the round block against `references/validator-schema.md`. Ensure that even in fallback or weak-model-constrained rounds, `DECISION` and `NEXT_ACTION` are present and non-empty. Internal marker: `VALIDATION_STATUS: passed|failed|blocked`.
13. Decide whether the flow continues. Internal marker: `FLOW_STATUS: continued|terminated`.

## Maintenance & Release Gates

- `CONSULTANT_QUALITY: mixed` means the response contained at least one structurally sound actionable finding, but also included vague, hallucinated, or only partially aligned points. Keep the good parts, reject the bad parts, and do not retry automatically if the actionable path is already clear.
- `analysis-only` is a valid operating mode, not a failure state.
- In `local` mode, omit `CONSULTANT_QUALITY` unless a formal self-critique pass was actually run.
- `MAX_ROUNDS`: default `5` unless the user explicitly wants more.
- Retry a `CONSULTANT_QUALITY: weak` response only once with a narrower prompt.
- If the second response is still weak, switch to `analysis-only` or stop with a blocker.
- Package only after `VALIDATION_STATUS: passed`.
- Treat `VALIDATION_STATUS: passed` as a required precondition for `PUBLISH_STATUS: Packaged` or `PUBLISH_STATUS: Published`.
- Publish only if the user asked for distribution and the publish gate has been satisfied.

Read `references/skill-review-mode.md` when the topic is a skill. Purpose: enforce skill-architecture review.
Read `references/skill-classes.md` when the skill belongs to a known class. Purpose: load the correct checklist.
Read `references/round-output-contract.md` when you need the exact round fields. Purpose: emit a machine-checkable round block.
Read `references/failure-handling.md` when the consultant is shallow, vague, or misses the artifact. Purpose: force a corrective round.
Read `references/patch-discipline.md` when a real fix was accepted. Purpose: patch before the next round.
Read `references/convergence-rules.md` when deciding whether to stop. Purpose: test stop conditions.
Read `references/weak-model-guide.md` when weak models may struggle. Purpose: flatten the path.
Read `references/validator-schema.md` when validation needs a minimal contract. Purpose: check round-block structure.
Read `references/examples.md` when you need prompt or output examples. Purpose: copy a safe pattern.
