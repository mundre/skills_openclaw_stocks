---
name: paper-framework-figure-studio-pro
description: Multi-round co-designer for reviewer-friendly paper framework diagrams and method overview figures for top-tier CS papers.
version: 1.1.0
author: OpenAI
tags:
  - scientific-figures
  - framework-diagram
  - paper-writing
  - visual-communication
  - computer-science
  - research-workflow
---

# Paper Framework Figure Studio Pro

## Purpose
Turn a paper deep-reading report, method description, model overview, or figure idea into a **publication-ready framework diagram** through a **multi-round, human-in-the-loop workflow**.

This skill is optimized for:
- **main framework figures**
- **method overview diagrams**
- **problem-setting + why-ours figures**
- **one-page integrated paper figures**
- **mechanism explanation diagrams**

## When to Use
Use this skill when:
- you already have a paper deep-reading report, method summary, or model description;
- you need a **framework figure** rather than a simple plot;
- you want to compare multiple figure styles before committing;
- you want the assistant to generate **multiple candidate diagrams each round**, then refine based on your choice;
- you want a figure tuned for **reviewer communication efficiency**, not just aesthetics.

## When Not to Use
Do not use this skill when:
- you only need a line chart / bar chart from numeric data;
- you only want a one-shot image with no iteration;
- you already have a finalized vector figure and only need tiny cosmetic edits.

## Core Design Principles
1. **Framework-first**: prioritize the main paper framework diagram before decorative variants.
2. **Reviewer efficiency**: optimize for fast comprehension of problem, method, novelty, and comparison.
3. **Style follows function**: choose figure family based on paper type and reviewer familiarity.
4. **Iterative convergence**: narrow from figure family -> substyle -> layout -> density -> local elements.
5. **Low-cost choices**: each round should produce only a small set of strong options.

## Workflow
### Phase 0 — Parse the Paper
Extract:
- problem setting
- method pipeline
- key novelty
- comparison point vs baseline
- which figure types are needed

Compress the input into a **figure-oriented visual summary**.

### Phase 1 — Choose a Figure Family
Propose 3–4 families such as:
- Academic-safe framework overview
- Modern modular / card layout
- Mechanism-explanation framework
- Design-forward scientific illustration

Generate **2–4 candidate framework figures** and ask the user to choose one direction.

### Phase 2 — Choose a Substyle
Within the selected family, refine into substyles, for example:
- classic overview
- minimalist concept-first
- modular magnetic-tile
- stepwise mechanism
- result-snapshot explanation

Generate **2–4 candidates** and ask the user to choose.

### Phase 3 — Choose Layout and Density
Refine:
- A4 portrait vs landscape
- low / medium / high density
- equations: none / light / medium
- intermediate result snapshots: none / light / strong
- comparison block: simple / moderate / rich

Generate **2–3 candidates** and ask the user to choose.

### Phase 4 — Refine Local Elements
Refine:
- icon language
- card strength
- arrow style
- comparison block style
- result-snapshot style
- palette strength

Generate **2–3 candidates** and ask the user to choose.

### Phase 5 — Finalize
Generate **1–3 final framework diagrams**.

After generating the final figure, **always ask**:

> Do you also want me to prepare the supporting figure text, such as:
> 1. short in-figure labels,
> 2. a polished figure caption,
> 3. panel-by-panel explanation text,
> 4. slide-friendly annotation text?

If the user says yes, produce the requested text in a style consistent with the selected figure.

## Required Response Structure Each Round
Every round should follow this structure:
1. **Current understanding**
2. **Round goal**
3. **Candidate directions**
4. **Image generation**
5. **Low-cost choice prompt**
6. **State update summary**

## Candidate Direction Format
For each candidate, provide:
- a short name
- one-line positioning
- strengths
- risks
- ideal reviewer / paper fit

## State to Maintain
Maintain a running state with:
- paper title / domain / venue target
- core problem
- core method
- core novelty
- chosen figure type
- selected family
- selected substyle
- selected layout
- density level
- liked elements
- disliked elements
- generation history
- next refinement target

## Image Generation Policy
- Prefer the current environment's **latest official image generation capability**.
- In ChatGPT web, use the image creation flow available in the current environment.
- In API / Codex / Trae-like environments, prefer the newest available official image model.
- During exploration rounds, maximize **style difference** across candidates.
- During refinement rounds, keep the selected direction stable and vary only targeted elements.

## Professional Figure Guidance
### Always optimize for:
- hierarchy
- legibility
- semantic color consistency
- panel alignment
- visual economy
- method faithfulness
- reviewer comprehension speed

### Avoid:
- over-decoration
- excessive tiny text
- inconsistent icon language
- ambiguous arrows
- mixing too many independent stories in one figure
- visual novelty that obscures the scientific message

## Output Expectations
At the end, provide:
- the final recommended framework diagram(s)
- a suggested figure title
- a concise figure caption draft
- optional in-figure wording / annotations when requested

## Safety
This skill is instruction-focused and primarily operates on user-provided paper content and figure design choices. It should not request secrets or unrelated private data.

## Version History
### 1.1.0
- Renamed to focus explicitly on **paper framework diagrams**
- Added mandatory final prompt asking whether to generate supporting figure text / caption / annotations
- Tightened workflow around framework-figure-first selection
- Improved publish-ready packaging for OpenClaw / ClawHub

### 1.0.0
- Initial multi-round scientific diagram co-design workflow
