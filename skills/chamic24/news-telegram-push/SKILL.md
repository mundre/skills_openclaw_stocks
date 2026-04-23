---
name: news-telegram-push
version: 2.0.0
description: Curate and send twice-daily English Telegram news pushes covering FX/CFD, crypto, prediction markets, retail trading app technology, financial news, and global political news, with strict deduplication and trusted-source filtering.

News Telegram Push

Objective
Curate and push high-signal English news updates twice daily at 7:00 AM and 7:00 PM for Telegram.

Coverage
Select the top 10 stories for each category:
- Industry News (FX / CFD) - 10 items
- Crypto - 10 items
- Prediction Markets - 10 items
- Retail Trading App Technology - 10 items
- Financial News - 10 items
- Global Political News - 10 items

Output format
For each push, output exactly 10 items PER CATEGORY (30 items total) in English.

Format:
[Morning Brief | 07:00]
[Category] Headline

Source: xxx

Read more: xxx

[Category] Headline

Source: xxx

Read more: xxx

...

[Category] Headline

Source: xxx

Read more: xxx

End with:

Tap any link to read the full story.

Selection rules
Prioritize relevance, market impact, policy significance, freshness, source credibility, and reader interest.
Balance the three categories where possible.
Avoid repeating the same event across multiple categories in the same push.
Avoid repeating the same story between the 7:00 AM and 7:00 PM pushes.
If a previously pushed story ranks highly again, skip it unless there is a materially new development.

Deduplication rules
Treat two articles as duplicates if they describe the same core event without a meaningful update.

Compare:
- core event
- company / asset / government involved
- timing
- whether the later report adds genuinely new information

If duplicate:
- keep only the strongest source
- prefer original reporting or primary source material

News Sources and Tools
Use tavily or firecrawl for news fetching (not web_fetch). These handle JS-heavy news sites.
- tavily: AI-powered news search with clean extraction
- firecrawl: Converts dynamic JS sites to clean markdown
- DuckDuckGo: For general web search
- browser: Fallback for sites that need full browser automation

Use high-credibility sources only.

Major financial media:
- Reuters
- Bloomberg
- Financial Times
- Wall Street Journal
- CNBC
- MarketWatch
- Barron's

Industry / trade media:
- Finance Magnates
- FX News Group
- The Block
- CoinDesk
- Cointelegraph (selectively)
- Decrypt (selectively)

Primary sources:
- official company blogs
- official newsroom pages
- official exchange / regulator / court / central bank websites
- official CEO / founder blogs or announcements when directly relevant

For crypto and prediction markets, prefer official announcements over commentary whenever possible.

Exclusions
Do not use:
- AI-generated news sites
- spammy aggregators
- SEO farms
- anonymous repost blogs
- rewritten articles without original reporting
- rumor-only posts
- shallow or sensational content

Inclusion filter
Prefer meaningful developments:
- regulation, licensing, compliance
- macro and central bank moves
- sanctions, trade policy, elections, war, ceasefire
- acquisitions, launches, shutdowns
- funding, earnings, institutional adoption
- trading app technology and infrastructure changes
- broker, exchange, custody, payment, KYC, onboarding, API, execution developments

Avoid:
- trivial opinion pieces
- generic market recaps
- low-signal commentary
- speculative clickbait
- generic AI-generated prediction content

Ranking logic
Rank by:
- importance to target audience
- freshness
- source credibility
- non-duplication
- likely reader interest
- broader market impact

Additional enforcement rules
Select exactly 10 items PER CATEGORY per push (30 items total).

Select top 10 from each category:
- Industry News: 10 items
- Crypto: 10 items
- Prediction Markets: 10 items
- Retail Trading App Technology: 10 items
- Financial News: 10 items
- Global Political News: 10 items

If one category has insufficient high-quality items, reallocate to the other categories, but still avoid duplication.

Never include more than 2 items about the same company in one push.
Never include more than 2 items about the same country-specific political event in one push.
Never include more than 1 pure price-move headline unless the move is caused by a major confirmed event.

For Crypto and Prediction Markets, prefer official announcements over commentary whenever possible.
For FX/CFD and Retail Trading App Technology, prefer regulatory, licensing, infrastructure, product, and platform news over promotional content.

If an official source and a media source cover the same event, prefer the official source for company announcements and the media source for broader analysis.

Final rule
Only output the final Telegram-ready list.

Do not output internal reasoning.