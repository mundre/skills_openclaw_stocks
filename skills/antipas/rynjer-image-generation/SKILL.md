---
name: rynjer-image-generation
version: 0.1.0
summary: Agent-first image generation with prompt rewrite, cost estimate, live execution, and polling.
---

# Rynjer Image Generation for Agents

Agent-first image generation with prompt rewrite, cost estimate, live execution, and polling.

## Why install this

Use this skill when an agent needs a usable image with a low-friction path from:

**task → prompt → cost → image**

This skill is best for agents that care about:
- predictable cost before generation
- fast execution without manual model hunting
- workflow-ready outputs for real tasks
- a practical path from trial to production API usage

## Start here

Recommended first run:
1. `rewrite_image_prompt`
2. `estimate_image_cost`
3. `generate_image`
4. `poll_image_result` if the task is still pending

## Best for

- landing-page images
- product and ecommerce visuals
- blog and article covers
- ad and social creatives
- workflow-driven image tasks

## What it does

### Rewrite image prompts
Turn rough requests into stronger prompts for commercial and workflow-oriented image generation.

Typical inputs:
- `goal`
- `raw_prompt`
- `use_case`
- `tone` (optional)
- `audience` (optional)

### Estimate image cost
Estimate credits before execution so the agent can make budget-aware decisions.

Typical inputs:
- `use_case`
- `count`
- `resolution`
- `aspect_ratio`
- `quality_mode`
- `price_version` (optional)

### Generate images
Generate usable images for business and workflow-driven tasks.

Typical inputs:
- `prompt`
- `use_case`
- `aspect_ratio`
- `resolution` (optional)
- `quality_mode`
- `count`
- `scene` (optional)
- `request_id` (optional)
- `auto_poll` (optional)

### Poll image results
Poll a previously submitted generation request until completion.

Typical input:
- `request_id`

## Why this is credible

This is an early-access image-only v1, but it is not mock-only shelfware.
The live flow has been verified across:

- register
- owner bind UI
- API key creation
- cost estimate
- generate
- poll

One real product constraint also verified in practice:
- owner-granted scopes in the bind flow constrain later API key creation scopes

## Positioning

This is not a generic creative playground.
It is an agent-facing image generation entry point focused on:

- low-friction execution
- predictable cost
- default routing over manual model-picking
- repeatable workflow use

## Pricing boundary

Recommended v1 boundary:
- **Free:** prompt rewrite, routing help, cost estimate
- **Paid:** image generation via Rynjer credits or API access

## Good fit

Use this skill when an agent needs a usable image quickly for:
- landing pages
- product pages
- blogs
- social posts
- ads

## Not a good fit

This v1 is not designed for:
- video generation
- music generation
- complex asset management
- multi-step studio pipelines
- large-scale brand systems

## Reality check

This package should be treated as:
- soft launch
- early-access
- image-only v1

It is suitable for real usage, but the clearest path is still the recommended happy path above.
