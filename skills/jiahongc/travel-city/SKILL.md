---
name: travel-city
version: 1.0.0
description: |
  Given a city name (+ optional season/month + optional origin city), return a
  comprehensive travel briefing. Use when asked to research a city for travel,
  plan a trip, or get destination info.
  Examples: "/travel-city Taipei", "/travel-city Tokyo in March",
  "/travel-city Barcelona from New York"
allowed-tools:
  - WebSearch
  - WebFetch
  - AskUserQuestion
metadata:
  openclaw:
    emoji: "🌍"
---

# /travel-city — City Travel Briefing

You are an expert travel researcher. Given a city, produce a comprehensive,
well-sourced travel briefing using live web research.

---

## Step 1: Parse Inputs

Extract these parameters from the user's message:

| Parameter       | Required | Pattern                                    |
|-----------------|----------|--------------------------------------------|
| `city`          | Yes      | City name (e.g., "Taipei", "Tokyo")        |
| `season_month`  | No       | "in summer", "in March", "in December"     |
| `travel_from`   | No       | "from New York", "from JFK", "from LA"     |

If `city` is missing or ambiguous, use AskUserQuestion to clarify.

---

## Step 1.5: Set Expectations

Before starting any search, output a brief status message so the user knows what to expect:

> Researching {city} travel information — this involves multiple searches and will take about 1-2 minutes. Hang tight...

This message must appear **before the first search call**.

---

## Step 2: Research via Live Search

Use **live web search** as the primary research method for all research. Target **~45 seconds total** for the research phase.
Run up to **8 queries** max. Prioritize the most impactful queries first.

Use the environment's built-in `WebSearch` / `WebFetch` tools or another live search method available to the user.

Do not rely on stale model knowledge when live search is available. Only proceed with partially verified information when a live search method is unavailable or clearly failing, and disclose that in the final confidence section.

### Search Strategy — Parallel First

**Maximize parallelism to reduce total wait time.** Batch searches into 2-3 parallel groups using multiple simultaneous search tool calls:

**Batch 1 (simultaneous):**
- City overview
- Weather/climate
- Attractions

**Batch 2 (simultaneous):**
- Food/cuisine
- Events/festivals
- Flight prices (if travel_from provided)

**Batch 3 (simultaneous):**
- Points/miles (if travel_from provided)
- Safety advisory

No artificial delays between batches. Only pause if you hit a **429** rate limit (wait 8-15 seconds, retry once).

### Query Plan (run in priority order, skip lower-priority if budget exhausted)

1. `"{city}" travel guide overview` — city basics, intro
2. `"{city}" travel safety advisory {current_year}` — safety, advisories
3. `"{city}" weather climate best time to visit` — seasonal info
4. `"{city}" top attractions things to do` — sightseeing
5. `"{city}" food must try dishes cuisine` — food scene
6. `"{city}" festivals events {current_year}` — events calendar
7. `flights from {travel_from} to {city} price` — only if travel_from provided
8. `"{city}" points miles award flights from {travel_from}` — only if travel_from provided

### Source Priority

**Prefer these sources** (official, authoritative):
- travel.state.gov, gov.uk/foreign-travel-advice — travel advisories
- Official tourism board sites (visitjapan.jp, etc.)
- cdc.gov/travel — health advisories

**Secondary** (reputable travel content):
- lonelyplanet.com, thepointsguy.com, skyscanner.com, google.com/travel
- numbeo.com (cost of living), xe.com (currency), rome2rio.com (transit)

**Tertiary** (use only when primary/secondary lack coverage):
- tripadvisor.com

**Never use**: Reddit, X/Twitter, Facebook, Instagram, TikTok, Quora, Medium, personal blogs

---

## Step 3: Compile Briefing

Write the briefing using **all** of the following sections in order.
If `travel_from` is NOT provided, skip section 10.
If `season_month` IS provided, tailor sections 3, 6, and 10 to that time window.

---

### Output Format

Use these exact section headings with emojis. Use numbered lists for ranked/ordered
content. Use bullet lists for unordered content. Keep paragraphs to 2-3 sentences.

---

## 🌍 City Overview

- Population, country, language(s), currency, timezone
- Brief intro — what the city is known for, its character and vibe
- Format population as: `9.7 million` or `850,000`
- Format timezone as: `UTC+9 (JST)`

## 📰 Recent History

- Notable events from the last ~10 years
- Political or economic changes that affect travelers
- Major infrastructure changes (new airports, transit lines, etc.)

## 🗓️ Best Time to Visit

- Climate by season with temperature ranges
- Peak vs. off-season timing and pricing impact
- Weather considerations and natural disaster risks
- If `season_month` provided: focus on that specific window
- Format temperatures as: `85°F (29°C)` (Fahrenheit first)

## 🏘️ Top Neighborhoods & Nearby Cities

- Notable neighborhoods/districts — **2-3 sentences each** covering vibe, key activities, and who it's best for
- Each neighborhood/district name must be a [named hyperlink](https://www.google.com/maps/search/...) to Google Maps
- Day-trip cities within 1-2 hours (also with Google Maps links)
- Where to stay for different traveler types (budget, luxury, nightlife, culture)

## 🎯 Things to Do

- Top 10-15 attractions, experiences, and landmarks (numbered list)
- Mix of iconic must-sees and lesser-known gems
- Each attraction name must be a [named hyperlink](https://www.google.com/maps/search/...) to Google Maps
- Include approximate visit duration and cost where known
- Format prices in both local currency and USD: `¥1,500 (~$10 USD)`

## 🎉 Popular Events

- Major festivals, holidays, and recurring events
- If `season_month` provided: highlight events in that window
- Include dates/months when events typically occur
- Note which events require advance booking

## 🍜 Food & Dining

- Must-try dishes (numbered list, 8-12 items)
- Food culture overview — meal times, dining customs
- Price ranges by category: street food, casual, mid-range, fine dining
- Tipping norms
- Format prices in both local currency and USD

## 🎌 Cultural Norms

- Essential etiquette and customs
- Dress codes (temples, restaurants, business)
- Do's and don'ts
- Communication tips (common phrases, language barriers)
- Religious or social sensitivities

## 🛡️ Safety & Security

- General crime overview and safety level
- Common scams and tourist traps to watch for
- Current travel advisories (cite travel.state.gov or equivalent)
- Health considerations (vaccines, water safety, air quality)
- Emergency numbers

## ✈️ Getting There

**Only include this section if `travel_from` is provided.**

- Direct flight routes and major airlines serving them
- Airport info (name, code, distance to city center)
- Flight duration
- Approximate cash pricing (economy, round trip): `$800–$1,200 RT`
- Points/miles estimates with program names: `60k–80k United MileagePlus miles RT`
- Transfer partner options: `transferable from Chase UR, Amex MR`
- Best booking strategies and when to book
- Airport-to-city transportation options

## 🚇 Getting Around

- Public transit overview (metro, bus, rail) with fare info
- Ride-hailing apps available (Uber, local alternatives)
- Walkability assessment
- Tourist passes or transit cards worth buying
- Intercity transportation if relevant

## 📋 Confidence Notes

Flag data freshness and uncertainty:

- **Confirmed**: Items verified from official/primary sources during this research
- **Unconfirmed**: Items from training data not verified by live search (mark with `(unconfirmed)`)
- **Conflicting**: Items where sources disagreed — note the discrepancy
- **Stale data flags**: Note any data that may change rapidly (prices, exchange rates, political situations)
- Include the date of research: `Research conducted: {today's date}`
- Include: `Live search queries used: {count}/8`
- If a fallback live search method was used, name it explicitly

## 🔗 Sources

List key sources used during research. Use `Name — URL` format (plain text with full URL).
Group by category. Example:

- **Official:** GO TOKYO Official Travel Guide — https://www.gotokyo.org/en/
- **Official:** U.S. State Dept Japan Advisory — https://travel.state.gov/...
- **Travel guides:** Lonely Planet Tokyo — https://www.lonelyplanet.com/...
- **Points/Miles:** The Points Guy — https://thepointsguy.com/...
- **Flights:** Expedia JFK→NRT — https://www.expedia.com/...

Only include sources that were actually consulted. Keep to ~8-12 links max.

---

## Formatting Rules

- **Emoji section headings**: Every H2 uses a relevant emoji prefix
- **Numbered lists**: For ranked/ordered items (top attractions, must-try dishes)
- **Bullet lists**: For unordered items (cultural norms, safety tips)
- **Bold key terms** on first mention: **Shinkansen** (bullet train)
- **Italics for foreign words**: *izakaya* (casual bar)
- **Prices**: Always dual currency — `¥1,500 (~$10 USD)`
- **Temperatures**: Fahrenheit first — `85°F (29°C)`
- **Distances**: Miles first with km — `15 miles (24 km)`
- **Flight durations**: `14h 30m`
- **Flight prices**: Ranges with RT — `$800–$1,200 RT`
- **Points/miles**: Program name + amount — `60k–80k United MileagePlus miles RT`
- **Time-sensitive data**: Mark with `(as of Month YYYY)`
- **Paragraphs**: 2-3 sentences max
- **Google Maps links**: For every named location (neighborhoods, attractions, restaurants, airports, stations), use a Markdown named hyperlink on the place name itself: `[Sensō-ji Temple](https://www.google.com/maps/search/Sensoji+Temple+Tokyo+Japan)`. Use `+` for spaces in the URL. Do NOT put bare URLs at the end of sentences.
- **No trailing summary**: End with Sources section, not a recap
