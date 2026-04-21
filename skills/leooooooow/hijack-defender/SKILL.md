---
name: hijack-defender
description: Create a monitoring and response plan for Amazon listing hijacking, including detection triggers, Brand Registry escalation steps, and counterfeit removal procedures via Project Zero and Transparency.
---

# Hijack Defender

Listing hijacking on Amazon — where unauthorized sellers attach themselves to your ASIN and sell counterfeit or grey-market products — erodes your brand, tanks your reviews, and steals your Buy Box. Hijack Defender builds a complete monitoring and rapid-response playbook so you can detect hijackers early, remove them through the correct Amazon enforcement channels, and put preventive measures in place to stop it from happening again.

## Use when

- You discover an unknown seller has appeared on one of your Amazon ASINs and is winning the Buy Box with a suspiciously low price or shipping counterfeit units
- You want to build a proactive hijack monitoring system before a problem occurs, especially if you sell high-demand products in categories prone to counterfeiting
- You are enrolled in Amazon Brand Registry and need a step-by-step escalation workflow for filing IP complaints, using Project Zero self-service removal, or enrolling ASINs in the Transparency program
- Your customer reviews have suddenly started mentioning quality issues or wrong items received, which may indicate a hijacker is fulfilling orders with inferior products under your listing

## What this skill does

This skill generates a comprehensive anti-hijacking playbook tailored to your brand and catalog. It covers three phases: detection, response, and prevention. For detection, it defines what monitoring signals to watch (new seller appearances, Buy Box loss, review sentiment shifts, pricing anomalies) and how to set up alerts. For response, it produces step-by-step escalation procedures through Amazon Brand Registry Report a Violation tool, Project Zero counterfeit removal, and Transparency program enrollment. For prevention, it recommends long-term protective measures including unique product identifiers, packaging authentication, and legal cease-and-desist templates. The playbook is specific to your ASINs, brand registry status, and the type of hijacking you are experiencing or want to prevent.

## Inputs required

- **Brand name and ASIN list** (required): Your brand name as registered in Amazon Brand Registry and the ASINs you want to protect or that are currently being hijacked. Example: "Brand: AquaPure, ASINs: B08XYZ1234, B09ABC5678"
- **Brand Registry status** (required): Whether you are enrolled in Amazon Brand Registry (and which tier), Project Zero, or Transparency. Example: "Brand Registry 2.0 enrolled, not yet on Project Zero or Transparency"
- **Current hijacking situation** (optional): Details about any active hijacking incident — the unauthorized seller name, what they are selling, pricing differences, and any customer complaints. Example: "Seller 'BestDeals99' appeared on B08XYZ1234 two days ago, priced $5 below our MAP, and three customers reported receiving a different product"
- **Product category and price range** (optional): Helps tailor the risk assessment and prevention recommendations. Example: "Health supplements, $25-45 per unit"

## Output format

The output is a structured Hijack Defense Playbook divided into four major sections. First, a **Risk Assessment** that evaluates your current exposure based on product category, price point, and existing protections, assigning a risk level (high, medium, low) to each ASIN. Second, a **Detection Protocol** with specific monitoring steps including how to set up automated alerts for new seller appearances on your ASINs, Buy Box monitoring cadence, and review sentiment tripwires, with recommended free and paid tools for each. Third, a **Response Escalation Ladder** with exact step-by-step instructions for each enforcement channel — starting with a direct seller warning, then Brand Registry Report a Violation filing (with field-by-field guidance), Project Zero self-service takedown procedures, Transparency enrollment steps, and when to escalate to Amazon Seller Support or pursue legal action. Fourth, a **Prevention Checklist** covering Transparency barcode enrollment, unique packaging markers, MAP policy enforcement, authorized reseller agreements, and ongoing monitoring cadence to keep your listings clean long-term.

## Scope

- Designed for: Amazon private label sellers, brand owners, and brand protection managers
- Platform context: Amazon (US, EU, and other Amazon marketplaces with Brand Registry support)
- Language: English

## Limitations

- Cannot file Brand Registry complaints, Project Zero removals, or Transparency enrollments on your behalf; the playbook provides instructions you execute in Seller Central
- Does not provide legal advice; cease-and-desist templates are starting points and should be reviewed by an attorney before sending
- Detection recommendations rely on tools and manual checks; this skill does not connect to live Amazon data or monitor your listings in real time