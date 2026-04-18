# Search Playbook

Use this file when `agent-travel` needs to turn local context into a safe search plan.

Default behavior:

- `search_mode = medium`
- `tool_preference = all-available`
- `thread_scope = active_conversation_only`
- `active_thread_window = 72h`

Use every search surface the host exposes unless the user narrowed the search.

## Problem Fingerprint

Build the smallest fingerprint that still distinguishes the issue:

- `system`: host agent and relevant subsystem
- `version`: product, library, or runtime version
- `symptom`: what is failing
- `error_fragment`: 5-20 words from the most stable error text
- `attempted_fixes`: short list of what already failed
- `constraints`: platform, policy, budget, or safety limits
- `goal`: what would count as a useful hint on the next task

Do not include secrets, full file contents, customer data, or long private paths.

## Query Templates

Start with one of these and tighten only when needed:

1. Exact error plus version:
   - `"exact error fragment" product version`
2. Symptom plus component:
   - `product component symptom version`
3. Regression after upgrade:
   - `product version old_version new_version regression symptom`
4. Config mismatch:
   - `product config_key symptom version`
5. Official page discovery:
   - `site:official.domain product symptom`

Use the exact error only when it is stable and non-sensitive.
Use version labels whenever the toolchain moves quickly.
Add the user's wording plus one community alias when the product has strong jargon drift.

## Search Coverage Matrix

Meet this minimum surface coverage before keeping advice:

- `low`: official docs plus 1 of search engine, forum, or official discussion
- `medium`: official docs plus any 2 of official discussion, search engine, forum, social
- `high`: official docs, official discussion, plus any 3 of search engine, forum, social, release notes

If the host exposes more tools, prefer breadth before depth on the first pass.

## Source Order

Search in this order:

1. Official documentation
2. Official release notes or changelogs
3. Official issue trackers or discussions
4. Search engines for broader discovery
5. Maintained forum threads, Q&A posts, and blog posts with version details
6. Social media or chat-community summaries for recent workaround signals
7. Aggregated answers only when they link back to primary sources

Drop pages that read like copied AI output without citations.

For host-specific travel, include the relevant official surfaces:

- OpenClaw docs and discussions
- Hermes docs and discussions
- Claude Code docs and discussions
- Codex docs and discussions

For every kept suggestion, official documentation or official maintainer guidance is mandatory.

## Distillation Frame

For every kept suggestion, write these three fields before keeping it:

- `solves_point`: name the concrete blocker, decision, or confusion inside the active thread
- `new_idea`: name the additional path or framing that external search added for this user
- `fit_reason`: name why the suggestion fits the current constraints, versions, and toolchain

Drop any suggestion that cannot answer all three precisely.

## Relevance Gate

Keep a candidate only when it matches at least 4 of these 5 axes:

1. Host or product family
2. Version or release neighborhood
3. Symptom or blocker
4. Constraint pattern
5. Desired next outcome

When two candidates disagree, prefer the one with tighter version match and tighter constraint match.

## Hard Answer Guard

Every kept suggestion must also define:

- `version_scope`: the versions, releases, or freshness window where it should hold
- `do_not_apply_when`: the clearest mismatch condition that should block reuse

If either field would be vague, the suggestion is too weak to keep.

## Tool Policy

Use all available search and fetch capabilities by default:

- built-in web search
- site-specific search
- issue and discussion search
- forum or community search
- social search
- direct page fetch or reader tools

If the host only exposes one search path, use it plus direct page fetches.
If the user specifies a narrower tool preference, obey it and record the preference in the suggestion block.

## Coverage Checklist

Before storing any suggestion, confirm that this pass covered:

- 1 official document page
- 1 official discussion, issue, or maintainer answer when available
- 1 broad web discovery source
- 1 community forum, Q&A, or blog source when available
- 1 social source when recency matters

`low` budget may stop after official docs plus 1 community surface.
`medium` budget should cover official docs plus at least 2 community surfaces.
`high` budget should cover official docs, official discussions, search engines, forums, and social signals unless a category is unavailable.

## Evidence Grading

- High: official doc plus official release note, or official doc plus matching maintainer fix, or official doc plus 2 independent community confirmations
- Medium: official doc plus community confirmation, or official maintainer answer plus forum confirmation, or official release note plus matching community report
- Low: single forum answer, blog post without versions, copied snippets without provenance

Only store medium or high.

## Redaction Rules

Apply all of these before web search:

- replace tokens and IDs with placeholders
- collapse private paths to a generic component name
- keep pasted code under 120 characters
- strip internal hostnames and customer names
- convert stack traces into a short error fragment plus top frame

## Distillation Rules

Every kept hint should answer four questions:

1. When does this apply?
2. What is the likely change or fix?
3. What manual check confirms it?
4. Why is it worth trying next time?

Keep the final hint short enough to fit in a small advisory block.

Also answer these two filters before keeping it:

5. Does it directly serve the active conversation?
6. Does it fit the current user's constraint, stack, and likely next step?
