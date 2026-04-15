---
name: upsell-mapper
description: Map product relationships and purchase sequence patterns to identify the best cross-sell triggers at checkout, post-purchase, and in creator content.
---

# Upsell Mapper

Most ecommerce brands sprinkle cross-sell widgets across the funnel without evidence that the pairings actually convert. This skill turns raw order data and content placements into a concrete upsell map that tells you which SKU should be offered after which, at which funnel stage, with which angle, so every cross-sell slot on your storefront and creator content has a tested reason to exist.

## Use when

- A Shopify, TikTok Shop, or Amazon seller asks "what should I put in my post-purchase upsell slot?" or "which products sell best together after X bestseller?"
- A brand team wants to restructure the checkout add-on widget, bundle suggestions, or "frequently bought together" module on product detail pages
- A creator or affiliate team needs a shot list of companion products to weave into TikTok Live, UGC scripts, or email flows after a hero SKU sells
- An operator is planning a loyalty or replenishment program and needs a logical product adjacency graph to build the reorder sequence

## What this skill does

Takes a list of SKUs, order line-item data, and optional review or return notes, then builds a directional affinity graph: for each source product, it ranks the top candidate follow-up products by attach rate, gross margin contribution, average time between purchases, and return correlation. It then groups these into three placement-specific playbooks — checkout add-ons, post-purchase one-click offers, and creator content pairings — because each slot rewards a different kind of upsell (impulse, convenience, demonstration).

## Inputs required

- **SKU list with categories, prices, margins** (required): CSV or pasted table covering at least the top 50 active SKUs
- **Order history sample** (required): order ID, line items, quantities, purchase date — 3 to 12 months is ideal
- **Current upsell placements** (required): which slots exist today (PDP, cart, checkout, post-purchase, email, creator content)
- **Return or refund notes** (optional): helps downweight high-return pairings
- **Creator content inventory** (optional): so pairings can be mapped to specific video formats or hooks

## Output format

A three-part deliverable. First, the affinity matrix: a ranked table of source SKU, recommended follow-up SKU, attach rate, incremental margin per thousand orders, and confidence note. Second, placement-specific playbooks: for checkout, post-purchase, and creator content, a shortlist of the top five pairings with the recommended copy angle for each slot. Third, a prioritized rollout plan: which pairings to test first based on traffic volume, implementation effort, and expected margin uplift over a four-week test window.

## Scope

- Designed for: ecommerce operators, DTC brands, TikTok Shop sellers, and marketplace sellers with at least a few months of order history
- Platform context: platform-agnostic, with specific placement notes for Shopify, Amazon, and TikTok Shop
- Language: English

## Limitations

- Does not connect to live ecommerce APIs; works from exported data you paste in
- Statistical confidence suffers with fewer than ~500 orders per source SKU; the output will flag low-data pairings
- Does not replace merchandising judgment for brand-sensitive pairings or seasonal considerations
