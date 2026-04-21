---
name: shipping-optimizer
description: Compare shipping strategies across carriers, zones, and fulfillment models to find the lowest-cost configuration that still meets customer delivery expectations and platform performance metrics.
---

# Shipping Optimizer

Shipping costs are one of the largest controllable expenses in ecommerce, yet most sellers pick a carrier and forget about it. Shipping Optimizer helps you systematically compare carrier rates, fulfillment models (FBA, FBM, 3PL, in-house), zone-based pricing, and dimensional weight rules to find the configuration that minimizes cost while still hitting the delivery speed your customers and marketplace algorithms expect.

## Use when

- You need to decide between FBA, FBM, third-party logistics, or self-fulfillment and want a side-by-side cost comparison for your actual SKU mix
- Your shipping costs have crept up and you want to audit whether your current carrier contracts and service levels are still competitive
- You are expanding into new geographic zones or international markets and need to model shipping cost impacts before committing inventory
- A marketplace like Amazon or TikTok Shop is penalizing your seller metrics because delivery times are too slow, and you need to find a faster option without blowing your margin

## What this skill does

This skill walks you through a structured shipping cost analysis. You provide your product dimensions, weights, current shipping volumes, origin warehouse locations, and target delivery windows. The skill then builds a comparison matrix across major carriers (UPS, FedEx, USPS, DHL, regional carriers) and fulfillment models, factoring in dimensional weight pricing, residential surcharges, fuel surcharges, zone-based rate tiers, and peak season adjustments. It calculates landed cost per unit for each scenario and highlights where you can save money or improve delivery speed. The output includes actionable recommendations ranked by estimated annual savings.

## Inputs required

- **Product catalog summary** (required): A list of your top SKUs with individual item weight (lbs or kg), box dimensions (L x W x H), and approximate monthly unit volume for each. Example: "SKU-A: 2 lbs, 10x8x4 in, 500 units/month"
- **Warehouse or fulfillment origin** (required): City and state (or country) where orders ship from. If you use multiple origins, list all of them. Example: "Los Angeles, CA and Dallas, TX"
- **Target delivery window** (required): The maximum acceptable delivery time your customers or marketplace requires. Example: "3 business days to continental US"
- **Current shipping method** (optional): Your existing carrier, service level, and approximate cost per shipment so the skill can benchmark against alternatives. Example: "UPS Ground, averaging $7.50 per package"
- **Marketplace requirements** (optional): Any platform-specific shipping performance metrics you must meet, such as Amazon Prime eligibility, TikTok Shop shipping SLA, or Shopify delivery promise badges

## Output format

The output is a structured shipping strategy report with five sections. First, a **Current State Summary** that recaps your existing setup and estimated annual shipping spend. Second, a **Carrier Comparison Matrix** presented as a table comparing 3-5 carrier and service level combinations across cost per unit, estimated transit days, dimensional weight impact, and surcharge exposure for your specific SKU mix. Third, a **Fulfillment Model Analysis** comparing FBA, 3PL, and self-ship options with per-unit cost breakdowns including storage fees, pick-and-pack fees, and shipping rates. Fourth, a **Zone Analysis** showing how costs change by delivery destination region and identifying zones where you overpay relative to alternatives. Fifth, an **Action Plan** with ranked recommendations, estimated annual savings for each change, implementation steps, and any trade-offs to consider such as loss of Prime badge or longer transit times.

## Scope

- Designed for: ecommerce operators, fulfillment managers, and DTC brand logistics teams
- Platform context: Amazon, Shopify, TikTok Shop, Walmart Marketplace, and platform-agnostic DTC stores
- Language: English

## Limitations

- Does not pull real-time carrier rate quotes; analysis is based on published rate structures and the information you provide about your negotiated rates
- Cannot access your actual carrier account dashboards or shipping history; you will need to supply volume and cost data manually
- Recommendations are estimates and should be validated with actual carrier quotes before switching providers