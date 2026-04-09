# Examples
#tags: skills review

## Example 1: initial activation for a skill rewrite
User request:
- `Rewrite this skill so weak models can execute it without stalling.`

Expected first-round state:
- `MODE: skill-rewrite`
- `SKILL_CLASS: workflow`
- `ORCHESTRATOR_MODE: api`
- `SESSION: dt-skill-name-yyyymmdd-api`

## Example 2: weak-model shortcut
User request:
- `Just do a quick structural audit of this skill.`

Expected shortcut path:
- emit `ROUTE_COMPLETE`
- emit `PROMPT_READY`
- emit the minimum round block
- emit `FLOW_STATUS: terminated`
- later recovery can start from the emitted `RESUME_SNIPPET`

## Example 3: same topic same chat
User request:
- `Continue reviewing the same skill.`

Expected behavior:
- round 2+ reuses the same chat or session for that topic
- emit `CHAT_CONTINUITY: reused`
- do not start a fresh chat unless continuity is broken

## Example 4: alternating multi-orchestrator
User request:
- `Use Qwen and DeepSeek alternately for 6 rounds on this skill.`

Expected behavior:
- `ORCHESTRATOR_MODE: multi`
- `MODE:` stays the semantic task mode that was routed for the topic, such as `skill-review`, `skill-hardening`, or `skill-publish-readiness`
- Round 1 uses orchestrator A in its own persistent chat
- Round 2 uses orchestrator B in its own persistent chat
- later rounds return to the same per-orchestrator chats
- every accepted fix is patched before the next round

## Example 5: patch-bearing round
- emit `PATCH_STATUS: applied`
- patch the real artifact
- emit `APPLY: done`
- emit `PATCH_MANIFEST`
- include `version_bump` when runtime behavior changed

## Example 6: publish-readiness close
- run validators
- run the minimal round-flow test
- package the skill
- set `PUBLISH_STATUS` to `Packaged` or `Published`
- if a blocker remains, set `PUBLISH_STATUS: Deferred`

## Example 7: local mode
- `ORCHESTRATOR_MODE: local`
- `ORCHESTRATOR: local`
- `CONSULTANT_QUALITY` omitted unless a formal self-critique pass was actually run
- no external consultant call is implied
