---
name: ad-creative-testing
description: Design structured A/B test hypotheses for ad creatives, hooks, landing pages, and audience segments with clear success metrics and test duration logic.
---

# Ad Creative Testing

Running paid ads without a structured testing framework is expensive guesswork. Ad Creative Testing turns your intuitions into falsifiable hypotheses, pairs each test with the right success metric, calculates how long you need to run before making a confident decision, and sequences experiments so learning compounds across campaigns rather than restarting from zero every time your results look flat.

## Use when

- You have two or three video ad concepts and want to know which single variable to isolate first — hook, voiceover style, CTA overlay, or product hero shot — so you get clean, actionable learning from your TikTok or Meta ad spend rather than noisy results from too many simultaneous changes.
- Your ROAS has plateaued over the past two to four weeks and you suspect creative fatigue but cannot tell whether to test new hooks, new audience segments, or new landing page copy first, and you want a prioritized testing roadmap that matches your budget constraints.
- You are launching a new product category and want to run thumb-stop hook tests across three distinct audience profiles — for example deal-seekers, brand loyalists, and first-time category buyers — before committing full-scale budget to any single creative approach.
- Your agency or in-house performance team is running A/B tests but consistently making go-or-no-go decisions too early — before reaching statistical significance — and you need a framework document to align everyone on minimum spend requirements, required sample size, and non-negotiable decision rules.

## What this skill does

Ad Creative Testing takes your current ad situation — existing creatives, recent performance data, available test budget, and campaign objective — and produces a complete, ready-to-run testing plan. The skill identifies which single variable to isolate and why, writes the A and B hypothesis in falsifiable form that any team member can evaluate, specifies the primary success metric (CTR, CVR, CPA, ROAS, or thumb-stop rate) alongside secondary guardrail metrics, and defines the minimum detectable effect size that would actually be worth acting on given your business economics. It then calculates the minimum impressions or spend required to reach statistical confidence at your chosen threshold — typically 90% or 95% — sets a hard decision date to prevent indefinite testing, and defines explicit rules for what to do with each possible outcome. The output also includes a test sequencing plan so you know immediately what to test next once the current experiment concludes, keeping learning momentum going.

## Inputs required

- **current_creatives** (required): A description of your existing ads — format type, hook style, visual approach, CTA language, and duration — for example "15-second UGC unboxing video, hook: I found the best skincare product on TikTok, CTA: Shop now in bio".
- **recent_performance** (required): Key metrics from your most recent campaign period — CTR, CVR, CPA or ROAS, impressions, and total spend — even rough estimates are useful to calibrate the minimum detectable effect size and budget recommendations.
- **test_objective** (required): The specific outcome you are trying to improve — for example "increase thumb-stop rate from 28% to 35%", "reduce CPA by 15% without sacrificing volume", or "improve landing page add-to-cart rate".
- **available_budget** (optional): Your weekly or monthly test budget; helps calculate whether your spending level can support the statistical power required to reach a conclusive result, and flags if the budget is too small for the test design.

## Output format

The output is a structured testing brief with five clearly labeled sections. Section one is the Test Hypothesis written in the standard form: If we change X to Y, we expect this metric to change by this amount because of this reason. Section two is Variables and Controls — what is being tested, what remains identical across all variants, and why those specific controls matter to data integrity. Section three is Success Metrics and Decision Rules — the primary KPI with its target threshold, two to three secondary KPIs to monitor for unintended side effects, and the exact performance gap that determines a statistically valid winner. Section four is Sample Size and Duration — minimum impressions, spend, or days required to reach significance at 90% confidence with a hard cut-off date that the team commits to in advance. Section five is Next Test Sequence — two to three follow-on experiments to run regardless of the current outcome, designed so that each test builds on the last and learning accumulates progressively across campaigns.

## Scope

- Designed for: ecommerce operators, performance marketers, brand teams, media buyers, growth teams
- Platform context: TikTok Ads, Meta Ads, Amazon DSP, Shopify-connected ad channels
- Language: English

## Limitations

- Statistical recommendations assume you can split traffic cleanly between variants; platforms with small audience pools or limited delivery volume may not support true A/B isolation at the confidence levels recommended.
- This skill generates the testing framework, hypothesis, and decision criteria — it does not produce the creative assets themselves; use a content creation or script writing skill for the actual video or copy production.
- Real-world test results can be materially affected by seasonality, platform algorithm shifts, and auction dynamics that no testing framework can predict or control for in advance.