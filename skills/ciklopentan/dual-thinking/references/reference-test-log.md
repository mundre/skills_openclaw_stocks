# Reference Test Log
#tags: skills review

Validation run: 2026-04-14T16:55:00+08:00
Validated version: `v8.5.15`
Prior frozen line: `v8.5.9 reference-release`
Frozen current baseline: `v8.5.9 reference-release`
Current line state: `reference-candidate`

| Scenario | Setup | Expected behavior | Observed behavior | Pass/Fail | Notes | Blocker |
|---|---|---|---|---|---|---|
| `local-basic` | `ORCHESTRATOR_MODE: local`; no external consultant | self+synthesis preserved; terminal round block | validation pack passed; terminal block semantics remain coherent | PASS | no local-path regression | none |
| `api-divergence` | consultant-bearing single external consultation | synthesis remains final owner after consultant input | inline contract still preserves synthesis-owned decision path after the accepted clarifications | PASS | synthesis ownership preserved | none |
| `multi-recovery` | alternating orchestrators across rounds with accepted-state recovery | later rounds return to same per-orchestrator chats; recovery resumes from accepted state when needed | stale Qwen repeat and stalled Qwen follow-up were both handled honestly as non-meaningful and recovered from the latest accepted state | PASS | recovery contract behaved as intended | none |
| `weak-shortcut-honesty` | compact consultant-bearing path | compact path remains truthful and non-duplicative | no drift introduced by the accepted fixes | PASS | shortcut boundary preserved | none |
| `publish-readiness-gate` | publish-gated release work | support-surface sync completes before promotion/publication | current line keeps publish sequencing subordinate to validation and accepted-state gates | PASS | publish sequencing preserved | none |
| `self-review-dual-thinking` | self-review lens remains active for `dual-thinking` itself | no fake convergence; real cuts or explicit stop only | full 8-round rerun on top of `v8.5.9` accepted three narrow continuity/recovery/publish-honesty clarifications, rejected stale or stalled non-meaningful rounds honestly, then converged without cosmetic churn | PASS | self-review stayed honest | none |
| `freeze-compatibility` | full rerun against frozen `v8.5.9` baseline | accepted fixes stay within clarification/recovery-hardening scope without architecture expansion | observed: accepted fixes remained narrow, architecture stayed unchanged, final line stayed within frozen-line bugfix/clarification scope | PASS | freeze honesty preserved | none |
| `current-date-trend-grounding` | allowed internet-capable consultant/orchestrator available for a materially current-date-sensitive artifact claim | strong current-date claims require live relevant public evidence or an honest narrowed state | support/evidence/test surfaces require `BLOCKEDSTATE: current-date-trend-not-grounded`, constrained-local interpretation, self-evolution live-public-evidence coverage, and the new round-1 / round-2 internet-assisted minimum floor | PASS | strengthened trend-grounding ratchet preserved inline authority | none |
| `consultant-context-isolation-stability` | consultant-bearing `api`/`multi` rounds with session reuse and narrowed later payloads | consultant visibility remains limited to explicitly visible text only | no regression introduced by the accepted clarifications; isolation law remains intact | PASS | isolation preserved | none |
| `subordinate-runtime-shadow-recovery` | subordinate section or `references/` text drifts behind the inline contract | runtime resolution must snap back to `Runtime Core Lock` | current line still resolves runtime authority to the inline contract without reintroducing subordinate-runtime drift | PASS | authority boundary preserved | none |
| `validation-failure-loop-closure` | a real patch fails validation and rolls back | failed patch loop closes for that scope unless materially different evidence appears | rollback contract remained intact and final validation pack passed | PASS | rollback semantics preserved | none |
| `user-declared-round-commitment` | user declares a fixed multi-round plan before execution | declared plan remains binding until completed or lawfully interrupted | runtime law kept the declared 8-round plan binding and all 8 rounds completed before release work | PASS | round commitment preserved | none |
| `multi-cycle-no-intercycle-reply` | user declares more than one cycle before execution | no user-facing progress reply is emitted between cycles during normal execution | no inter-cycle violation introduced | PASS | inter-cycle silence preserved | none |
| `no-idle-after-completed-step` | declared plan remains unfinished and a completed step already resolved `NEXT_ACTION` | execution continues immediately into the known next step | no unlawful idle pauses introduced; execution continued directly into the next required step | PASS | anti-idle rule preserved | none |

## Convergence summary
- support/reference/test surfaces were synchronized to the strengthened `v8.5.15` inline contract without changing the public three-step runtime architecture
- subordinate files now explicitly support the `Current-date Internet Trend Grounding Lock`, its stability lock, its anti-patterns, and the new round-1 / round-2 internet-assisted minimum floor
- subordinate recovery/evidence/test surfaces now cover `BLOCKEDSTATE: current-date-trend-not-grounded` and the matching current-date trend-grounding branch
- subordinate self-evolution support now covers live public trend, architecture, implementation, benchmark, and maintainer evidence when allowed and materially relevant
- the new anti-ritual boundary is explicit: after the mandatory floor is satisfied, repeated broad web-search is no longer implied for purely local bug, test, contract, or consistency work
- targeted sync validation passed for the updated support surfaces
