---
name: surgical-contributor
description: Deliver small, high-signal contributions by finding and fixing one real pain point with the narrowest safe change, adding regression protection, and writing a maintainer-friendly PR summary. Use for bug fixes, workflow paper cuts, state/caching correctness issues, startup/config/platform edge cases, and UI-backend behavior drift where low review burden and low merge risk matter.
---

# Surgical Contributor

## Overview

Execute a disciplined contribution loop: reproduce, isolate, patch minimally, protect against regressions, and self-review before presenting results. Optimize for mergeability, trust, and behavior stability over feature scope.

## Contribution Doctrine

Apply this doctrine in every run:

- Regression-first
- Minimal-diff
- Maintainer-friendly

Refuse these by default unless explicitly requested:

- Broad refactors
- Speculative architecture shifts
- Opportunistic style rewrites
- Feature expansion beyond the bug or paper cut

## Operating Modes

Choose exactly one mode at the start of work:

1. Bugfix mode
Reproduce a correctness issue, isolate root cause, apply narrow patch, add regression protection.
2. Paper-cut mode
Fix high-frequency UX friction in hot paths (navigation, shortcuts, defaults, wording, startup flow) with minimal behavioral surface area.
3. Refactor-under-permission mode
Perform cleanup only when explicitly requested; keep each change independently safe and reviewable.
4. Review-my-own-PR mode
Run an explicit maintainer-style critique before final output.
This is a standalone review mode (no code changes), not a second execution mode alongside Bugfix/Paper-cut flows.

### Non-code repository fallback

This fallback is not a separate mode.
If no executable code or reproducible runtime bug exists, treat the repository as a specification system and fix exactly one deterministic weakness (ambiguity, missing constraint, contradiction, scope leak, or unenforceable rule) with the smallest reviewable docs patch.

## Standard Workflow

### 1. Find one pain point

Scan current code and nearby tests for one concrete issue that is:

- Reproducible now
- Small enough for a focused patch
- Valuable to daily usage, correctness, or reliability

Prefer high-leverage targets:

- Stale index logic
- Undo/redo correctness
- Selection or batch state drift
- Cache invalidation mistakes
- Edge-case crashes
- Startup/config/platform breakage
- UI-backend contract mismatches
- Hot-path UX friction

### 2. Write a tiny change plan before editing

Document five items in plain language:

- Observed behavior
- Expected behavior
- Suspected root cause
- Safest seam to modify
- Risk surface

### 3. Reproduce first

Create a minimal repro with one of:

- Existing automated test
- New focused test
- Small harness script
- Manual repro recipe when GUI constraints block automation

Avoid fixing before proving the failure.

### 4. Implement the narrowest safe fix

Constrain edits to the smallest practical set of files and lines.

Rules:

- Do not mix unrelated cleanup into the patch
- Preserve behavior outside the defect scope
- Prefer local guards, condition fixes, and invariant restoration over broad rewrites
- Keep naming and style aligned with surrounding code

### 5. Add regression protection

Add one durable protection artifact:

- Automated test (preferred)
- Focused test helper/harness
- Manual verification protocol with exact steps and expected results when automation is not feasible

Tie assertions directly to the reproduced failure and fixed behavior.

### 6. Run self-review before finalizing

Perform this checklist and resolve any "no" answers:

- Is non-bug behavior preserved?
- Are stale indices or invalid references still possible?
- Can cache/state desync still occur?
- Are undo/redo semantics still consistent?
- Are keyboard/UI interaction flows intact?
- Is platform behavior safe on Windows/macOS/Linux (as relevant)?
- Is naming clear and consistent with repo conventions?
- Is there a smaller patch that would work equally well?

### 7. Produce maintainer-language PR summary

Use this exact heading structure:

```markdown
## What broke
<one short paragraph>

## Root cause
<one short paragraph>

## Why this fix is minimal
<scope boundary + why no broader change>

## What I tested
<tests run, harness checks, or manual steps>

## What I intentionally did not change
<explicit non-goals to reduce review ambiguity>
```

Keep the summary scannable in about 20 seconds.

## Stack-Specific Focus

When working in UI-heavy codebases, prioritize bugs where small state mistakes have outsized UX impact. Read [references/risk-map.md](references/risk-map.md) when selecting targets or doing self-review.

## Output Contract

Return results in this order:

1. Change plan (5 bullets)
2. Reproduction evidence
3. Minimal patch summary
4. Regression protection summary
5. Self-review findings
6. PR summary with required headings
