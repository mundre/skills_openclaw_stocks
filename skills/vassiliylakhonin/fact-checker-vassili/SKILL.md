---
name: fact-checker
description: Evidence-first claim verification for AI-agent workflows. Use when a user asks to fact-check, verify truthfulness, assess misinformation, validate statistics, compare conflicting sources, or decide whether a claim is reliable enough for decision-making.
---

# Fact Checker

Give verdict first, then short evidence bullets.

## Best for

- Verifying claims before publishing
- Checking stats, quotes, and causal statements
- Resolving source conflicts with confidence rating
- Fast misinformation triage in chats/docs

## Not for

- Pure opinions or value judgments without testable facts
- Legal/medical/financial final advice without qualified experts
- Claims with zero accessible evidence (mark `UNVERIFIABLE`)

## 60-second preflight

```bash
# 1) Rewrite claim as one testable sentence
# 2) Split into atomic sub-claims if needed
# 3) Define what would prove vs disprove it
```

Minimum evidence rule:
- Use at least 2 independent sources for strong verdicts.
- Prefer primary sources and official data.

## Core workflow

### 1) Define claim
- Normalize to one factual sentence.
- If mixed, split into atomic claims.

### 2) Collect evidence
- Prioritize: primary docs/data -> official institutions -> peer-reviewed -> reputable reporting.
- Record date and possible staleness.
- Apply freshness gate by default: for fast-moving topics, prefer sources from last 30 days; if older, add stale-risk note.

### 3) Adversarial pass
- Find strongest counter-evidence.
- Check: cherry-pick, denominator mismatch, timeframe mismatch, quote out of context, correlation vs causation.

### 4) Rate claim
Use exactly one:
- `TRUE`
- `MOSTLY TRUE`
- `MIXED`
- `MOSTLY FALSE`
- `FALSE`
- `UNVERIFIABLE`

Add confidence:
- `high`
- `medium`
- `low`

If claim has multiple parts, score atomic sub-claims first, then roll up to final verdict.

### 5) Report
Include:
- key supporting evidence
- key caveat/counter-evidence
- corrected claim (if misleading)
- explicit unknowns

## Eval gate (required for major updates)

Before major release/promoted usage, run `references/eval-harness.md` and check pass/fail gates.
Do not claim readiness if source hygiene or overconfidence gates fail.

## Courtroom mode (optional, v1.2)

Use for controversial or high-stakes claims where source conflict is material.

Trigger conditions:
- 2+ credible sources directly disagree
- claim has policy/legal/medical/financial impact
- adversarial misinformation risk is high

Protocol:
1. Prosecution: build strongest case **for** the claim.
2. Defense: build strongest case **against** the claim.
3. Judge: compare evidence quality, freshness, and directness.
4. Final verdict: single rating + confidence, plus why one side wins.

Rules:
- Both sides must cite evidence.
- Do not allow rhetoric without sources.
- If evidence tie persists, return `MIXED` or `UNVERIFIABLE`.

## Output template

```markdown
## Claim
[Exact claim]

## Verdict
[TRUE|MOSTLY TRUE|MIXED|MOSTLY FALSE|FALSE|UNVERIFIABLE]

## Confidence
[high|medium|low]

## Why
- [Top supporting evidence]
- [Top counter-evidence or caveat]

## Corrected version
[Only if needed]

## Unknowns
- [What remains unverified]

## Atomic scores (only if claim was split)
- A1: [sub-claim] -> [rating, confidence]
- A2: [sub-claim] -> [rating, confidence]

## Provenance notes
- Included sources: [why these were selected]
- Excluded sources: [why excluded: low quality/stale/non-independent]

## Courtroom summary (only if courtroom mode is on)
- Prosecution: [best evidence for claim]
- Defense: [best evidence against claim]
- Judge rationale: [why final verdict stands]

## Sources
1. [Title, publisher/author, date, URL, credibility note]
2. [...]
```

## Failure recovery playbook

- No reliable sources found -> return `UNVERIFIABLE` and request specific missing evidence.
- Sources conflict -> downgrade confidence and explain conflict clearly.
- Claim too broad -> split into atomic claims and rate separately.
- Outdated evidence -> add freshness caveat and avoid high-confidence verdict.

## Guardrails

- Never fabricate citations.
- Never cite a source not inspected.
- For high-stakes domains, avoid definitive wording when evidence is weak.
- If uncertainty remains, say it directly.
- Use `references/source-quality.md` when source quality/conflicts decide the verdict.
- Use `references/eval-harness.md` to validate quality before major rollout.

## Author

Vassiliy Lakhonin