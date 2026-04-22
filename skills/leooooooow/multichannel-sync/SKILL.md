---
name: multichannel-sync
description: Plan inventory, pricing, and listing synchronization across multiple sales channels to prevent overselling, maintain consistent branding, and optimize channel-specific pricing without triggering marketplace policy violations.
---

# Multichannel Sync

Selling on Shopify plus Amazon plus TikTok Shop plus one or two regional marketplaces sounds great until two customers buy the last unit at the same time, or Amazon suppresses your Buy Box because a 10% TikTok flash sale violated their fair pricing policy. Multichannel Sync gives you a concrete playbook for keeping stock counts, prices, and listing data aligned across channels without breaking any individual platform's rules.

## Use when

- A seller says "I'm overselling on Amazon every time TikTok Shop runs a promotion — how do I set up inventory buffers and sync rules that stop this?"
- A brand is adding a third or fourth channel and needs a decision framework for whether to run them off a single inventory pool or split stock by channel.
- A founder asks "Amazon just warned me about fair pricing — can you audit my cross-channel pricing and tell me what to fix?"
- An operations lead is evaluating inventory and listing sync tools (ChannelAdvisor, Sellbrite, Linnworks, Zentail) and wants a requirements checklist before committing to one.

## What this skill does

Produces a multichannel synchronization plan covering three layers: inventory (which channels share a pool, which carry reserved buffers, how low-stock thresholds throttle listings before a stockout), pricing (which channel is the anchor price, what differential each secondary channel is allowed to deviate, and how promotions cascade without triggering marketplace parity penalties), and listing content (which fields must be identical, which should vary by platform for SEO or policy reasons, and how to propagate updates). It also outlines the reconciliation cadence, exception handling workflow, and the specific platform rules you must respect on each marketplace.

## Inputs required

- **Channel list** (required): every channel you sell on, including direct storefront, marketplaces, and any B2B portals, with monthly order volume for each.
- **Current inventory structure** (required): whether stock is centralized in one location, split by channel, or managed across multiple 3PLs; include safety stock and typical replenishment lead time.
- **Pricing strategy** (required): anchor price by SKU, any MAP or MSRP policies, and any known parity constraints from Amazon, Walmart, or other marketplaces.
- **SKU variation rules** (required): which products have parent-child or variant structures, and any channel-specific SKU or listing ID mappings you already use.
- **Integration stack** (optional): current OMS, ERP, or listing tool and any known sync frequency or reliability issues.
- **Promotion calendar** (optional): upcoming sitewide or channel-specific sales so the plan can pre-define safe discount ranges and buffer stock.
- **Category risk factors** (optional): perishables, hazmat, oversize, or other restrictions that affect where inventory can legally sit.

## Output format

A three-section sync playbook. Section one is an inventory sync matrix showing each channel's stock pool, buffer percentage, low-stock throttle threshold, and what happens when inventory drops below the safety line. Section two is a pricing matrix with anchor, allowed deviation, cascade rules for promotions, and a short explanation of each marketplace's parity or fair-pricing policy you must respect. Section three is a listing content playbook specifying which fields are shared, which vary, and the push order when something changes. A closing checklist lists the top oversell, price-parity, and listing-suppression risks with the monitoring alert each one needs.

## Scope

- Designed for: ecommerce operations leads, multi-channel sellers, and brand managers coordinating across marketplaces and direct storefronts.
- Platform context: Shopify, Amazon, Walmart, TikTok Shop, Shopee, Lazada, eBay. Additional marketplaces can be accommodated with generic rules.
- Language: English.

## Limitations

- Does not integrate directly with ERP, OMS, or channel APIs; the output is a plan you implement in your existing tooling.
- Marketplace rules change frequently — the plan reflects typical policy structures, but you should verify current terms with each platform.
- Does not replace legal review of MAP agreements, distributor contracts, or cross-border tax obligations.
