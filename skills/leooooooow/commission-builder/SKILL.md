---
name: commission-builder
description: Design profitable affiliate and influencer commission structures by working backwards from margin, AOV, and conversion rate assumptions.
---

# Commission Builder

Designing an affiliate or influencer commission structure without anchoring it to your actual unit economics is one of the fastest ways to erode margin. Commission Builder helps ecommerce operators and brand teams work backwards from gross margin, average order value (AOV), and expected conversion rates to arrive at commission tiers that are attractive to partners while protecting profitability.

## Use when

- You are launching a TikTok Shop affiliate program and need to determine the maximum commission percentage you can offer creators without going below a target gross margin threshold, and you want to model multiple tiers (micro, mid, macro) simultaneously.
- You are negotiating a flat-fee + performance bonus deal with a KOL or brand ambassador and need to calculate the break-even sales volume at each bonus tier given your product COGS and current average order value.
- You are auditing an existing Shopify or Amazon Associates affiliate program and suspect certain commission rates are eating into margin because they were set arbitrarily rather than derived from unit economics.
- You want to design a tiered commission ladder for a Shopee or Lazada affiliate campaign where commission rates increase at defined GMV milestones, and you need to stress-test those thresholds against pessimistic and optimistic conversion rate scenarios.

## What this skill does

Commission Builder takes your product economics — COGS, selling price, platform fees, and any additional fulfillment costs — and computes the contribution margin available to fund partner commissions before you set a single rate. It then models one or more commission structures (flat percentage, tiered GMV, hybrid flat + bonus) and outputs a side-by-side comparison showing projected margin retention, partner earnings at different sales volumes, and the minimum conversion rate required for each scenario to remain profitable. It flags structures that breach your margin floor and suggests adjustments, so you can negotiate with partners from a position of financial clarity rather than guesswork.

## Inputs required

- **Selling price** (required): The final consumer-facing price per unit on the target platform, e.g., "$49.99 on TikTok Shop."
- **COGS per unit** (required): Total landed cost per unit including manufacturing, freight, and any import duties, e.g., "$12.00."
- **Platform fee / take rate** (required): The percentage the platform deducts from each sale, e.g., "8% for TikTok Shop" or "15% referral fee for Amazon."
- **Target gross margin floor** (required): The minimum gross margin percentage you want to protect after paying commission, e.g., "25%."
- **Commission structures to model** (required): One or more structures in plain language, e.g., "10% flat; or 8% up to $5K GMV then 12% above; or $2 flat fee + 6%."
- **Expected conversion rate range** (optional): Estimated low and high conversion rates from affiliate link clicks to purchases, e.g., "1%–3%." Providing this enables break-even volume calculations and sensitivity tables.
- **Additional variable costs** (optional): Any per-order costs not captured in COGS, such as return rate buffer, packaging inserts, or paid fulfillment surcharges. Including these gives a more accurate available-margin figure.

## Output format

The output is structured in four sections. First, a **Unit Economics Summary** table showing selling price, COGS, platform fee (in dollars), additional variable costs, and the resulting contribution margin in both dollars and percentage. Second, a **Commission Structure Comparison** table with one column per structure modeled, showing commission rate or amount, partner earnings per unit, net margin after commission, and whether the structure passes or fails your margin floor. Third, a **Break-Even Volume Table** (if conversion rate is provided) showing the number of affiliate-driven clicks needed to generate 100, 500, and 1,000 orders under each structure. Fourth, a **Recommendations** paragraph summarizing which structure(s) are viable, which should be avoided, and one or two negotiation levers (e.g., reducing COGS by $1 unlocks an additional 2% commission headroom).

## Scope

- Designed for: ecommerce operators, brand teams, affiliate program managers, TikTok Shop sellers
- Platform context: TikTok Shop, Amazon, Shopify, Shopee, Lazada, platform-agnostic
- Language: English

## Limitations

- This skill does not access live platform fee schedules; you must provide the current take rate manually, as these change periodically.
- Output is based on the inputs you provide and does not constitute financial or legal advice — consult an accountant before finalizing commission agreements with contracted influencers.
- The skill models up to four commission structures per session; highly complex multi-variable commission contracts (e.g., those with clawback clauses or attribution window logic) require manual adaptation of the outputs.
