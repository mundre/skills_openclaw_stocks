---
name: exit-intent
description: Design exit-intent popup strategies for ecommerce sites including trigger rules, offer types, copy variants, and A/B testing plans that recover leaving visitors without annoying engaged shoppers.
---

# Exit Intent

This skill designs end-to-end exit-intent popup strategies for ecommerce stores — deciding when to fire, what to offer, what copy and creative to show, and how to measure lift — so that recovery offers catch abandoning visitors without interrupting the ones who are still shopping or ready to check out.

## Use when

- The user runs a Shopify, WooCommerce, BigCommerce, or custom ecommerce storefront and is seeing desktop bounce rates above 55% or abandoning cart rates climbing week over week.
- The user asks for help writing exit popup copy, picking an incentive (discount vs free shipping vs sample), or deciding whether a popup should appear on product, cart, or checkout pages.
- The user wants a structured A/B testing plan for exit-intent variants (trigger sensitivity, offer size, headline tone, visual layout) with a clear primary metric and guardrails.
- The user is concerned that popups are hurting SEO Core Web Vitals, harming mobile UX, or creating a brand perception problem, and wants rules for when not to fire.

## What this skill does

Analyzes the store type, traffic composition (paid vs organic, new vs returning), and conversion funnel stage to recommend a layered exit-intent strategy. Produces trigger logic (mouse leave threshold, scroll depth gate, time on page minimum, page-type filters, frequency caps per visitor), offer tiering (soft ask like newsletter vs hard ask like 10% off vs urgency-based like countdown), and at least three headline and CTA copy variants mapped to customer intent. Recommends suppression rules for returning buyers, logged-in accounts, and checkout pages. Includes an A/B test plan with sample size math and statistical stopping rules.

## Inputs required

- **Store URL or platform** (required): Platform matters because trigger implementation differs between Shopify apps, Klaviyo flows, Privy, OptinMonster, or custom JS.
- **Primary goal** (required): Email capture, first-order discount redemption, cart recovery, or survey collection — each pulls the design in a different direction.
- **Average order value and gross margin** (required): Dictates how generous the incentive can be without destroying contribution margin.
- **Monthly unique visitors and current conversion rate** (optional): Improves A/B sample-size recommendations and lift expectations.
- **Brand voice examples or past popup copy** (optional): Helps match tone so recovery offers sound native rather than generic.

## Output format

Four sections. (1) Strategy summary — one paragraph explaining the recommended approach and why it fits the store. (2) Trigger configuration table — trigger type, threshold, page filters, frequency cap, suppression rules, and a short rationale for each row. (3) Offer and creative matrix — three to five variants, each with headline, subheadline, CTA button text, offer value, and intended audience segment. (4) A/B test plan — primary metric, minimum detectable effect, required sample size per variant, estimated test duration, and guardrail metrics (bounce rate, checkout completion, unsubscribe rate) to monitor.

## Scope

- Designed for: ecommerce operators, growth marketers, CRO specialists, and DTC brand teams
- Platform context: platform-agnostic, with implementation notes for Shopify, WooCommerce, Klaviyo, and OptinMonster
- Language: English

## Limitations

- Does not pull live analytics data — recommendations are based on the numbers you provide.
- Does not generate the actual popup code or design files; output is a strategy specification that your developer, designer, or popup platform can implement.
- Sample-size math assumes roughly normal conversion distributions; very low-volume stores may need longer test windows than the estimate suggests.
