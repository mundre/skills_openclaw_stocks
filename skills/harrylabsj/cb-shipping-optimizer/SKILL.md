---
name: International Shipping Optimizer
slug: cb-shipping-optimizer
description: Cost-effective international shipping strategy and carrier optimization framework
category: cross-border-ecommerce
type: descriptive
language: en
author: Harry (code agent)
version: 1.0.0
---

# International Shipping Optimizer

## Overview

Cost-effective international shipping strategy and carrier optimization framework. Evaluates carriers across speed, cost, reliability, tracking, and customs handling. Provides lane-specific recommendations, customs clearance guidance, and cost optimization strategies. Pure descriptive skill. No code execution, API calls, or network access.

## Trigger Keywords

Use this skill when the user mentions or asks about:
- shipping options for US, Germany, UK, Japan, Australia, France, Brazil, India, Canada, Netherlands
- reduce international shipping costs
- best carrier for China to US or Europe
- international shipping strategy and logistics planning
- customs and duties for specific countries
- DHL vs FedEx vs UPS comparison
- ePacket vs EMS vs SF Express
- sea freight vs air freight
- de minimis thresholds
- duty-free allowances by country

### Primary Triggers
- "best shipping options from China to US and Germany for 2kg package"
- "how to reduce international shipping costs for apparel"
- "shipping strategy for multiple international markets"
- "DHL vs FedEx vs UPS for China to Europe"
- "sea freight from China to US"
- "customs duty for electronics shipped to Japan"
- "de minimis threshold for Brazil"

## Supported Lanes

**Origin:** China (mainland)

**Destinations:** US, Germany, UK, Japan, Australia, France, Brazil, India, Canada, Netherlands

## Supported Carriers

1. **DHL Express** — Fast, global, excellent customs handling, premium pricing
2. **FedEx International** — Fast, reliable, strong tracking, slightly cheaper than DHL
3. **UPS Worldwide** — Fast, excellent for US, good bulk rates, strong tracking
4. **TNT Express** — Strong in Europe, good value, acquired by FedEx
5. **EMS / ePacket** — Economy, China Post backed, long transit, low cost
6. **SF Express** — Best for China-Hong Kong-Macao, competitive in Asia-Pacific
7. **Aramex** — Strong in Middle East and Africa, good for cross-border e-commerce
8. **Sea Freight** — Slow (4-8 weeks), lowest cost per kg, best for large/bulk shipments

## Workflow

1. **Receive input** — Parse origin, destination markets, package weight, value, delivery preference, tracking needs
2. **Evaluate carriers** — Score carriers across speed, cost, reliability, tracking, customs handling
3. **Lane recommendations** — Generate carrier recommendations per origin-destination lane
4. **Customs framework** — Provide duty rates, documentation requirements, clearance tips per market
5. **Cost optimization** — List strategies with saving potential and implementation guidance

## Input Format

Accepts natural language or structured JSON describing:
- origin country (default: China)
- destination markets (list of country names or codes)
- package weight (kg)
- declared value (USD)
- delivery time preference: fast | balanced | economy
- tracking needed: true | false
- insurance needed: true | false
- categories of goods: electronics | apparel | cosmetics | home goods | mixed

## Output Structure

Returns JSON with these top-level fields:
- input_analysis: parsed summary of user input
- carrier_evaluation_matrix: scored carriers with speed, cost, reliability, tracking, customs, best use cases
- lane_recommendations: carrier recommendations per origin-destination pair
- customs_clearance_framework: duty rates, documentation, clearance tips per market
- cost_optimization_strategies: 5+ strategies with saving potential and implementation
- disclaimer: safety disclaimer

### Scoring System

Each carrier is scored 1-10 on:
- speed_score: transit time performance (10 = fastest, 1 = slowest)
- cost_per_kg: value score (10 = cheapest per kg, 1 = most expensive)
- reliability: delivery success rate (10 = highest)
- tracking_quality: tracking granularity and accuracy (10 = best)
- customs_handling: ease of customs clearance (10 = smoothest)
- overall_score: weighted average

## Safety and Disclaimer

Descriptive guidance only. Not professional legal, regulatory, or business advice. Shipping costs, carrier availability, and regulations change frequently. Always verify current information with carriers and customs authorities before making shipping decisions.

## Examples

### Example 1: Electronics from China to US and Germany
Input: "best shipping options for electronics from China to US and Germany 2kg package value $200"
Output: Carrier comparison matrix (DHL, FedEx, UPS, EMS), lane-specific recommendations, customs duty guidance (de minimis $800 for US, $150 for Germany), cost optimization strategies.

### Example 2: Apparel to UK, Japan, Australia
Input: "how to reduce international shipping costs for apparel to UK Japan Australia"
Output: Economy carrier recommendations, consolidated shipping strategy, regional warehouse considerations, dimensional weight optimization, 5+ cost reduction tactics.

### Example 3: Heavy Package to Brazil
Input: "shipping 15kg home goods from China to Brazil, value $500, need insurance"
Output: Sea freight vs air freight comparison, carriers suited for heavy shipments, Brazil customs duty guidance (60%+ for home goods), insurance recommendations, consolidation strategies.

### Example 4: Fast Delivery to Canada and Netherlands
Input: "urgent 1kg document from China to Canada and Netherlands, fastest option"
Output: Top express carriers ranked by speed (DHL, FedEx, UPS), lane-by-lane timing, cost comparison for urgent delivery.

## Acceptance Criteria

- Evaluates at least 8 carriers with numerical scoring
- Provides lane-specific recommendations for at least 2 destination markets
- Includes customs clearance framework with documentation requirements for at least 5 countries
- Lists at least 5 cost optimization strategies with saving potential
- Returns valid JSON with all documented fields present
- Contains complete safety disclaimer in every output
- Includes input_analysis summarizing parsed input
- Pure descriptive — no code execution, API calls, network access
