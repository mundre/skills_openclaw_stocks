# Failure Handling
#tags: skills review

## Runtime failure table
| Failure | Next action |
|---|---|
| artifact not pasted | ask once, request inline artifact, no path-only review |
| artifact represented only by paths, filenames, `FILE:` labels without body text, shell snippets, literal placeholders like `$(cat ...)`, hidden-local assertions, or chopped fragments that do not cover the exact claim under review | treat as `artifact not pasted`; repaste the actual text inline before continuing |
| second request still no artifact | switch to `analysis-only` and stop patch loop |
| self opinion is vague | tighten `SELF_POSITION` before asking the consultant |
| consultant slow after successful submit | if the prompt was successfully submitted and no explicit failure signal appears, keep waiting; do not narrow, downgrade, or declare the round weak only because a long prompt is thinking slowly |
| consultant weak | retry once with the narrowing template |
| consultant weak again | switch to `analysis-only` or stop as blocked |
| consultant critique too generic because artifact payload was too thin | resend with a larger artifact payload before judging consultant quality |
| self and consultant sharply diverge | force explicit `SYNTHESIS`, list one keep and one reject, and do not patch until divergence is resolved |
| consultant contradicts self without evidence | prefer self baseline unless the consultant gives stronger concrete reasoning |
| consultant seems to miss an issue from a non-pasted section, local check, local code path, non-pasted validator/test result, or context that only the other consultant saw | verify visibility before blaming the consultant |
| both self and consultant are vague | narrow scope immediately or switch to `analysis-only` |
| synthesis attributes review to non-pasted material | mark the round invalid and rebuild with proper artifact payload |
| continuation missing | mark `CONTINUATION_SIGNAL: missing`, default `continue` |
| session polluted or context-degraded | first try to resume the intended persistent same-topic chat; if it is unusable because it is broken, polluted, or the consultant is clearly degrading under context load, open a recovery chat, paste latest accepted artifact, add `RESUME_SNIPPET`, and rebuild from the latest `STATE_SNAPSHOT` |
| consultant/orchestrator launch path keeps triggering approval cards or repeated authorization prompts for otherwise allowed work | do not claim safeguards can be disabled globally; switch once to a launch path that keeps the same safety boundary but avoids the prompt-triggering transport, preferably direct stdin or file redirection when supported, then resume the same round and log the transport change honestly |
| current-date-optimized, trend-aware, state-of-the-art, latest-practice-aligned, or materially improved against current external practice is being claimed without live inspection of relevant public internet evidence even though an allowed internet-capable consultant/orchestrator is available and the task materially benefits from that check | set `VALIDATIONSTATUS: blocked`, emit `BLOCKEDSTATE: current-date-trend-not-grounded`, inspect the missing live public evidence when allowed, or narrow the claim explicitly to `offline-only-provisional-not-verified-against-current-public-trends` |
| an in-scope current-date-sensitive task enters consultant-bearing review without satisfying the mandatory round-1 / round-2 internet-assisted minimum floor even though an allowed internet-capable consultant/orchestrator is available | keep current-date-strength claims blocked until round 1 names the strongest seam from live external evidence against the real artifact and round 2 challenges that finding against local truth boundaries and constraints, or narrow the claim explicitly to offline-only/provisional |
| accepted fix not patched | patch before next review |
| validation failed | block packaging and publishing, retain the failed diff, and revert to the last passed artifact |

## Current-date trend grounding blocked state
If strong current-date optimization, latest-practice, state-of-the-art, trend-aware, or materially-improved-against-current-external-practice claims are being made for a skill, code artifact, workflow, tool, runtime component, memory system, orchestrator, or program without live public internet inspection even though an allowed internet-capable consultant/orchestrator is available and the task materially benefits from that check:
- set `VALIDATIONSTATUS: blocked`
- emit `BLOCKEDSTATE: current-date-trend-not-grounded`
- inspect the missing live public evidence when allowed
- preserve all already-binding local-only, privacy, hardware, runtime, budget, latency, safety, and user-defined constraints while translating that evidence into the strongest compatible solution
- if live inspection is unavailable, disallowed, too weak, or too indirect, narrow the claim explicitly to `offline-only-provisional-not-verified-against-current-public-trends`
- do not import cloud-first, hosted, or external-API designs into a local-only artifact merely because that trend is fashionable
- if the task is in-scope current-date-sensitive work, do not exit the blocked state until the round-1 / round-2 internet-assisted minimum floor is satisfied or the claim is honestly narrowed
- the minimum floor means: round 1 names the strongest seam from live external evidence against the real artifact; round 2 challenges that finding against local truth boundaries, runtime limits, weak-model safety, and operator constraints

## Shallow consultant response
If the consultant only praises the artifact, gives generic advice, or ignores the real text, do not count the round as meaningful.
- name the missing weakness
- request keep / rewrite / add / delete / test
- continue in the same session

## Slow consultant after successful submit
If a long consultant prompt was successfully submitted and the consultant is still thinking:
- do not treat slow thinking by itself as a weak response
- do not narrow the prompt only because the wait feels long
- do not start recovery unless an explicit failure signal appears or continuity is clearly broken
- prefer patient waiting over premature prompt shortening when the original long prompt is materially needed for accurate review

## Weak self position
If the self pass is vague, decorative, or not clearly grounded in the loaded artifact:
- stop before asking the consultant
- tighten the self verdict, weakness, and smallest strong fix
- only continue to consultant prompting after the self pass is concrete enough to challenge or refine

## Artifact not reviewed
If the consultant reacted to a path, summary, filename, `FILE:` label without body text, shell snippet, literal placeholder such as `$(cat ...)`, or any non-pasted local claim instead of the pasted artifact:
- stop the round
- ask once for the real artifact inline
- do not do path-only review or summary-only review when exact claims depend on text not yet pasted
- do not treat unresolved shell substitutions or file labels as pasted artifact text
- rerun the same topic session after the artifact is pasted
- if the second request still does not produce the artifact, switch to `analysis-only` and stop the patch loop

Clarification:
- if the missing issue lives in a section that was never pasted, do not blame the consultant first
- if the missing issue was visible only in the other consultant's chat, repaste it here before judging consultant quality
- repaste the relevant artifact text before judging consultant quality

## Missing continuation signal
If the consultant does not explicitly say whether another round is worth it:
- mark `CONTINUATION_SIGNAL: missing`
- continue by default

## Continuity broken
If round 2+ accidentally opened a new chat for the same topic:
- do not continue in the wrong chat by default
- try to return to the intended same-topic chat or session first
- if recovery to the intended chat is impossible, or the intended chat is visibly polluted or context-degraded, mark `CHAT_CONTINUITY: recovery`
- paste the latest accepted patch and `RESUME_SNIPPET` into the recovery chat before continuing
- if a reused session repeats stale pre-patch critique after the accepted artifact has changed, loses task identity, or starts producing nonsense against the visible prior rounds in that same chat, treat that as session pollution / context degradation and recover or narrow explicitly instead of counting the round as meaningful

Clarification:
- in `multi`, continuity is session-specific
- do not assume another orchestrator already saw the accepted artifact unless that text was pasted into that orchestrator session
- reusing consultant A's chat preserves only A-context; it does not make that context visible to consultant B
- if the launch transport is what keeps surfacing approval cards, prefer swapping transport to direct stdin or file redirection when supported rather than claiming any global safeguard removal

## Divergence handling
If self and consultant disagree sharply:
- do not patch immediately
- emit explicit `SYNTHESIS`
- keep at least one strong point from the winning side
- reject at least one weaker point with a reason
- only patch after the divergence is concretely resolved or the scope is narrowed

If the consultant contradicts the self pass without evidence:
- prefer the self baseline
- ask whether the consultant has stronger concrete reasoning or direct artifact evidence
- do not switch decisions just because the consultant sounded confident

If both sides are weak:
- narrow the scope immediately
- or switch to `analysis-only`
- do not fake convergence from two vague positions

## Patch blocked
If a fix is accepted but cannot be applied safely:
- emit `DRY_RUN: blocked`
- emit `APPLY: deferred`
- explain the blocker in `PATCH_MANIFEST`
- do not pretend the round is converged

## Diagnostic actions
- `CONSULTANT_QUALITY: weak` -> rerun once with the narrowing template and cite the exact weak point or section.
- `CONSULTANT_QUALITY: mixed` -> keep the good parts, reject the vague parts, and patch only accepted fixes.
- `CONTINUATION_SIGNAL: ambiguous` -> continue and ask for an explicit stop or continue judgment next round.
- `CONTINUATION_SIGNAL: missing` -> continue by default and log the missing signal.

## Narrowing template

### Narrow consultant template — normal consultant-bearing rounds
`Focus strictly on <section>. Name exactly 1 structural weakness. Give the smallest strong fix. Return only: consultant_verdict, strongest_finding, weakest_or_vague_finding, proposed_fix, confidence. No praise. No preamble.`

### Narrow synthesis fallback — only when the caller explicitly requests decision-ready compaction
`Focus strictly on <section>. Given the current SELF_POSITION and the consultant critique, output only: relation, decision, next_action. No praise. No preamble.`

Rules:
- In consultant-bearing rounds, narrowing should default to consultant-position output, not direct final decision output.
- Decision-style narrowing is allowed only at synthesis time, not as the consultant's default role.

## Safety stop
Stop only when all of these are true:
- the consultant explicitly says another round is not worth it
- you agree
- no accepted but unpatched fix remains
- no must-have docs or tests remain for the asked scope
- no unresolved blocker remains for the asked scope
