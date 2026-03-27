---
name: trip-itinerary-planner
version: 1.0.0
description: >
  Intelligent trip itinerary planning skill. Use when users need to plan
  single-day or multi-day travel itineraries, organize multi-destination trips,
  optimize travel routes, estimate budgets, or create detailed day-by-day
  travel schedules. Supports domestic and international travel, solo trips,
  family travel, and group travel scenarios.
author: voyagerai
license: MIT-0
tags:
  - travel
  - itinerary
  - planning
  - trip
  - route
---

# Trip Itinerary Planner Skill

A comprehensive trip itinerary planning skill that generates structured,
day-by-day travel plans based on user requirements. Derived from production
travel AI systems with real-world planning expertise.

## Core Capabilities

- Single-day and multi-day itinerary generation
- Multi-destination route optimization
- Transportation mode analysis (flights, trains, driving, transit)
- Budget estimation and cost breakdown
- Accommodation placement strategy
- Activity and attraction scheduling
- Family/group travel considerations
- Domestic and international trip support

## Trigger Conditions

Activate this skill when the user:

- Asks to "plan a trip", "create an itinerary", "arrange a travel schedule"
- Mentions multi-day travel with specific destinations
- Requests day-by-day travel arrangements
- Asks for route optimization across multiple cities
- Needs help organizing travel logistics (transport + hotel + activities)
- Uses phrases like: "help me plan", "travel itinerary", "trip schedule",
  "how should I arrange my days in [destination]"

Do NOT activate for:

- Single-point questions like "What's fun in Paris?" (use general knowledge)
- Pure ticket booking or hotel search (not itinerary planning)
- Real-time queries like weather or prices (use web search)

## Workflow

### Step 1: Requirement Analysis

Extract and confirm the following from the user's input:

| Parameter        | Required | Description                                    |
|------------------|----------|------------------------------------------------|
| destinations     | Yes      | Target cities/countries in visit order          |
| travel_dates     | Yes      | Start date, end date, or total days             |
| travelers        | No       | Number of adults, children, elderly; solo/group |
| budget_level     | No       | Budget/mid-range/luxury; or specific amount     |
| interests        | No       | Culture, food, nature, shopping, adventure, etc |
| constraints      | No       | Mobility limits, visa restrictions, diet needs  |
| pace_preference  | No       | Relaxed / moderate / intensive                  |

**Rules:**
- If destinations or dates are missing, ask the user before proceeding
- If only a destination is given without dates, suggest a reasonable duration
  based on [Destination Analysis Guide](references/destination-analysis-guide.md)
- Infer budget_level from context clues (e.g. "backpacking" = budget)
- Default pace is "moderate" if not specified

### Step 2: Destination Analysis

For each destination, analyze:

1. **Optimal stay duration**: How many days are ideal
2. **Must-see attractions**: Top landmarks, cultural sites, natural scenery
3. **Local specialties**: Food, shopping, unique experiences
4. **Geographic layout**: How attractions cluster geographically
5. **Seasonal factors**: Weather, peak/off-peak, festivals during travel dates

Reference: [Destination Analysis Guide](references/destination-analysis-guide.md)

**Multi-destination rules:**
- Allocate days proportionally based on destination richness
- First and last days account for transit overhead
- Minimum 1 full day per major city (exclude transit days)

### Step 3: Transportation Planning

Determine inter-city and intra-city transport:

#### Inter-city (between destinations)

| Distance        | Recommended Modes                  |
|-----------------|-------------------------------------|
| < 200 km        | Driving, high-speed rail, bus       |
| 200-800 km      | High-speed rail (preferred), flight |
| 800-2000 km     | Flight (preferred), overnight train |
| > 2000 km       | Flight                              |
| Cross-border    | Flight (check visa transit rules)   |

#### Intra-city (within destination)

- Use metro/subway where available (most cost-effective)
- Walking for clustered attractions (< 2 km apart)
- Taxi/ride-hailing for remote spots or with children/elderly
- Rent a car only for road-trip-style or rural areas

**Rules:**
- Place transit between cities in mornings or evenings to maximize
  sightseeing time
- For flights, account for 2-3 hours of airport overhead
- For high-speed rail, account for 30 min station overhead

Reference: [Transportation Guide](references/transportation-guide.md)

### Step 4: Itinerary Assembly

Build the day-by-day schedule following these principles:

#### Time allocation per day

| Time Block    | Duration  | Activity Type                        |
|---------------|-----------|--------------------------------------|
| Morning       | 08:00-12:00 | Major attractions, outdoor activities |
| Lunch         | 12:00-13:30 | Local cuisine experience             |
| Afternoon     | 13:30-17:30 | Museums, shopping, secondary sights  |
| Dinner        | 17:30-19:00 | Dining experience                    |
| Evening       | 19:00-21:30 | Night markets, shows, city walks     |

#### Assembly rules

1. **Geographic clustering**: Group nearby attractions in the same half-day
2. **Energy curve**: Place physically demanding activities in the morning;
   indoor/relaxing activities in the afternoon
3. **Meal integration**: Schedule meals near planned attraction areas
4. **Buffer time**: Add 30-min buffers between activities for transit/rest
5. **First day**: Lighter schedule if arriving after noon; check-in + nearby
6. **Last day**: Reserve morning for packing and checkout; airport/station
   transit by early afternoon
7. **Rest day**: For trips > 5 days, insert a half-rest day mid-trip
8. **Rain plan**: Note indoor alternatives for outdoor activities

#### Family/group adjustments

- With children (< 6 yrs): Max 2 major attractions per day; add nap time
- With elderly: Reduce walking; add rest stops; avoid steep terrain
- Group travel: Choose activities with broad appeal; build in free time

Reference: [Itinerary Template](references/itinerary-template.md)

### Step 5: Budget Estimation

Provide a cost breakdown per person per day:

| Category       | Budget       | Mid-range    | Luxury       |
|----------------|--------------|--------------|--------------|
| Accommodation  | Hostel/budget hotel | 3-4 star hotel | 5-star/resort |
| Meals          | Street food/local | Mix of local & restaurants | Fine dining |
| Transport      | Public transit | Transit + occasional taxi | Taxi/private car |
| Activities     | Free/low-cost sights | Mix of paid & free | Premium experiences |

**Rules:**
- Use the destination's local currency and provide approximate conversion
- Separate fixed costs (flights, hotel) from daily variable costs
- Note peak season surcharges when applicable
- For families: mention child ticket discounts where common

Reference: [Cost Estimation Rules](references/cost-estimation-rules.md)

### Step 6: Output Generation

Generate the final itinerary in the structured format defined in
[Itinerary Template](references/itinerary-template.md).

**Output must include:**
1. Trip overview (destinations, dates, travelers, budget summary)
2. Day-by-day detailed schedule
3. Budget estimation table
4. Preparation checklist

Reference: [Travel Checklist](references/travel-checklist.md)

## Expression Rules

- Use the user's language for the entire response
- Keep each day's description concise: 3-5 bullet points per time block
- Use clear time markers (morning/afternoon/evening or specific times)
- Highlight must-do items with emphasis
- Include practical tips inline (e.g. "arrive early to avoid queues")
- Provide the full itinerary in a single response; do not split across
  multiple messages
- For trips > 7 days, provide a summary table first, then day-by-day details
- Do not fabricate specific prices; use ranges or say "check current rates"
- Do not fabricate opening hours; use general guidance or say "verify locally"

## General Rules

- Always respect the user's stated budget and pace preference
- For international trips, remind about visa, insurance, and currency exchange
- For destinations with safety concerns, include relevant travel advisories
- Suggest travel insurance for all international trips
- If the user's plan is unrealistic (too many cities, too few days), provide
  honest feedback and suggest alternatives
- When uncertain about specific local details, recommend the user verify
  with local sources rather than guessing
- Adapt the level of detail to the user's apparent experience level
  (first-time travelers get more tips; experienced travelers get less)

## Usage Examples

- "Help me plan a 5-day trip to Tokyo and Osaka"
- "Plan a family trip to Thailand for 7 days with 2 kids"
- "I have 3 days in Paris, what's the best itinerary?"
- "Plan a budget backpacking route through Southeast Asia for 2 weeks"
- "Create a honeymoon itinerary for Bali and Singapore, 10 days"
- "Help me arrange a road trip from Los Angeles to San Francisco"
