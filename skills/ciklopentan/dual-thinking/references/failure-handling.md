# Failure Handling
#tags: skills review

## Runtime failure table
| Failure | Next action |
|---|---|
| artifact not pasted | ask once, request inline artifact, no path-only review |
| second request still no artifact | switch to `analysis-only` and stop patch loop |
| consultant weak | retry once with a narrower prompt |
| consultant weak again | switch to `analysis-only` or stop as blocked |
| continuation missing | mark `CONTINUATION_SIGNAL: missing`, default `continue` |
| session polluted | open recovery chat, paste latest accepted artifact, add `RESUME_SNIPPET` |
| accepted fix not patched | patch before next review |
| validation failed | block packaging and publishing |

## Shallow consultant response
If the consultant only praises the artifact, gives generic advice, or ignores the real text, do not count the round as meaningful.
- name the missing weakness
- request keep / rewrite / add / delete / test
- continue in the same session

## Artifact not reviewed
If the consultant reacted to a path, summary, or filename instead of the pasted artifact:
- stop the round
- ask once for the real artifact inline
- do not do path-only review
- rerun the same topic session after the artifact is pasted
- if the second request still does not produce the artifact, switch to `analysis-only` and stop the patch loop

## Missing continuation signal
If the consultant does not explicitly say whether another round is worth it:
- mark `CONTINUATION_SIGNAL: missing`
- continue by default

## Continuity broken
If round 2+ accidentally opened a new chat for the same topic:
- do not continue in the wrong chat by default
- try to return to the intended same-topic chat or session
- if recovery to the intended chat is impossible, mark `CHAT_CONTINUITY: recovery`
- paste the latest accepted patch and `RESUME_SNIPPET` into the recovery chat before continuing

## Patch blocked
If a fix is accepted but cannot be applied safely:
- emit `DRY_RUN: blocked`
- emit `APPLY: deferred`
- explain the blocker in `PATCH_MANIFEST`
- do not pretend the round is converged

## Diagnostic actions
- `CONSULTANT_QUALITY: weak` -> rerun once with a narrower question and cite exact weak points.
- `CONSULTANT_QUALITY: mixed` -> keep the good parts, reject the vague parts, and patch only accepted fixes.
- `CONTINUATION_SIGNAL: ambiguous` -> continue and ask for an explicit stop or continue judgment next round.
- `CONTINUATION_SIGNAL: missing` -> continue by default and log the missing signal.

## Safety stop
Stop only when all of these are true:
- the consultant explicitly says another round is not worth it
- you agree
- no accepted but unpatched fix remains
- no must-have docs or tests remain for the asked scope
- no unresolved blocker remains for the asked scope
