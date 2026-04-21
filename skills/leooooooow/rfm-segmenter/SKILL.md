---
name: rfm-segmenter
description: Segment your customer base by Recency, Frequency, and Monetary value to identify VIPs, at-risk churners, and dormant buyers, then generate targeted re-engagement strategies for each segment.
---

# RFM Segmenter

Most ecommerce brands treat their entire customer list the same way, sending identical promotions to someone who bought yesterday and someone who has not purchased in a year. RFM Segmenter applies the proven Recency-Frequency-Monetary framework to divide your customer base into actionable segments — VIP loyalists, promising newcomers, at-risk churners, hibernating buyers, and lost customers — then generates specific re-engagement strategies and messaging recommendations for each group so you spend marketing dollars where they actually move the needle.

## Use when

- You have a customer purchase export (from Shopify, Amazon, WooCommerce, or any ecommerce platform) and want to understand which customers are your most valuable and which are slipping away
- You are planning an email or SMS campaign and need to segment your audience beyond basic demographics into behavior-based groups with different messaging strategies
- Your retention rate is declining and you want to identify exactly which customer cohort is churning and design a targeted win-back approach for that specific group
- You need to justify marketing budget allocation by showing which customer segments generate the most revenue and which segments have the highest recovery potential

## What this skill does

This skill takes your customer transaction data and applies RFM scoring methodology to classify every customer into distinct behavioral segments. It calculates three scores for each customer: Recency (how recently they purchased), Frequency (how often they purchase), and Monetary value (how much they spend). Each dimension is scored on a 1-5 scale, and customers are grouped into named segments such as Champions (high across all three), Loyal Customers (high frequency and monetary, moderate recency), At-Risk (previously high value but recency declining), Hibernating (low recency, formerly active), and Lost (low across all dimensions). For each segment, the skill generates tailored marketing strategies including recommended channels, messaging tone, offer types, and campaign timing. It also calculates segment sizes and revenue contribution to help you prioritize where to focus.

## Inputs required

- **Customer transaction data** (required): A summary or export of customer purchase history including customer identifier, date of most recent purchase, total number of orders, and total spend. Example: "Customer ID, Last Purchase Date, Order Count, Total Spend — or paste a CSV sample and I will work with your column names"
- **Analysis time frame** (required): The lookback period for the RFM analysis. Example: "Last 12 months" or "January 2025 through March 2026"
- **Business context** (required): Your product category, average order value, and typical repurchase cycle so segment thresholds are calibrated correctly. Example: "Skincare products, $35 AOV, customers typically reorder every 60-90 days"
- **Current marketing channels** (optional): Which channels you actively use (email, SMS, paid social, direct mail) so strategy recommendations are limited to channels you can actually execute. Example: "Klaviyo for email, Attentive for SMS, Meta Ads for retargeting"

## Output format

The output is a comprehensive RFM segmentation report with five sections. First, a **Scoring Methodology** explanation showing how the 1-5 RFM scores were assigned based on your specific data distribution and repurchase cycle, so you understand exactly where the segment boundaries fall. Second, a **Segment Summary Table** listing each named segment (Champions, Loyal, Potential Loyalists, At-Risk, Needs Attention, About to Sleep, Hibernating, Lost) with the RFM score ranges that define it, the number of customers in each group, their percentage of total customers, and their percentage of total revenue. Third, a **Segment Deep Dive** for each group covering behavioral profile, estimated lifetime value trajectory, churn probability, and what distinguishes this group from adjacent segments. Fourth, a **Re-Engagement Strategy Matrix** with segment-specific recommendations including campaign type (welcome series, VIP exclusives, win-back offers, sunset flows), recommended channel, messaging tone and example subject lines, offer type and discount depth, and optimal send timing. Fifth, a **Priority Action Plan** that ranks the three highest-impact segments to target first based on revenue recovery potential and effort required, with specific next steps you can execute immediately.

## Scope

- Designed for: ecommerce operators, retention marketers, CRM managers, and DTC brand teams
- Platform context: Shopify, WooCommerce, Amazon, BigCommerce, and any ecommerce platform that exports transaction data
- Language: English

## Limitations

- Does not connect to your ecommerce platform or CRM directly; you need to provide transaction data as a CSV paste, summary, or file upload
- RFM scoring uses standard quintile-based methodology and may need manual threshold adjustments for businesses with unusual purchase cycles such as luxury goods or annual subscription products
- Strategy recommendations are marketing best practices, not personalized predictions; actual campaign performance depends on execution quality, creative, and offer strength