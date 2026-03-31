---
name: food-vlog-maker
version: 1.0.4
displayName: "Food Vlog Maker"
description: >
  Describe your food experience and NemoVideo creates the video. Restaurant visits and honest reviews, market exploration content, food travel destinations, street food discovery, farmers market hauls, tasting menus, food city guides — narrate what you ate, what made it extraordinary or disappointing, the specific details that capture why food in a place is worth seeking out, and get food vlog co...

  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM.
homepage: https://nemovideo.com
apiDomain: https://mega-api-prod.nemovideo.ai
repository: https://github.com/nemovideo/nemovideo_skills
license: MIT-0
metadata:
  requires:
    env: ["NEMO_TOKEN"]
    configPaths:
      - "~/.config/nemovideo/"
  primaryEnv: NEMO_TOKEN
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> 🎨 Hey! I'm ready to help you food vlog maker. Send me a video file or just tell me what you need!

**Try saying:**
- "edit my video"
- "add effects to this clip"
- "help me create a short video"

**IMPORTANT**: Always greet the user proactively on first contact. Let them know you're setting up while connecting. Always greet the user proactively on first contact.

### Auto-Setup

When the user first interacts, set up the connection:

1. **Check token**: If `NEMO_TOKEN` env var is set, use it. Otherwise:
2. **Read or generate Client-ID**:
   - Read `~/.config/nemovideo/client_id` if it exists
   - Otherwise generate a UUID, save it to `~/.config/nemovideo/client_id`
3. **Acquire anonymous token**:
   ```bash
   curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

Let the user know briefly: "Setting things up… ready!" then proceed with their request.


# Food Vlog Maker — Create Food Discovery, Restaurant, and Culinary Journey Videos

Describe your food experience and NemoVideo creates the video. Restaurant visits and honest reviews, market exploration content, food travel destinations, street food discovery, farmers market hauls, tasting menus, food city guides — narrate what you ate, what made it extraordinary or disappointing, the specific details that capture why food in a place is worth seeking out, and get food vlog content for the audience that plans trips around meals.

## When to Use This Skill

- Create restaurant visit and honest review vlog content
- Film street food and market discovery documentation
- Build food travel city guide content
- Document tasting menu and special dining experience content
- Create farmers market and seasonal ingredient haul content
- Produce food neighborhood and culinary district walking tour content

## How to Describe Your Food Vlog

Be specific about the location, the specific dishes, the tastes and textures, the context that makes the food meaningful, and the honest assessment.

**Examples of good prompts:**
- "Tokyo ramen tour — 5 bowls in 3 days, one clear winner: The format: eat ramen at the places that have waited 40 years to be good, not the ones that went viral last month. Bowl 1: Fuunji, Shinjuku (tsukemen — thick, concentrated tare, noodles dipped not submerged, order medium noodles not small). Bowl 2: Ichiran, Shibuya (the solo booth ramen — intentionally designed so you eat alone without social pressure, the broth is the product of 60 years of single-focus refinement). Bowl 3: Fuji Ramen (a counter with 6 seats in Golden Gai, old man has been making the same shoyu broth since 1975, no reservation, queue at opening). Bowl 4: a convenience store instant cup at 2am after a long night (context is everything — this was actually good). Bowl 5: the winner and why. The specific things that separate Tokyo ramen from everywhere else: water (Tokyo's soft water creates a different broth character), the concentration of specialization (a shop that has only made tonkotsu for 30 years is different from a shop with 15 ramen varieties)."
- "The 3-Michelin-star tasting menu I saved 18 months for — was it worth it: The restaurant: Eleven Madison Park, NYC. The reservation: 11 months out. The cost: $365/person, wine pairing brings it to $600+. The experience: 9 courses over 3.5 hours. What I expected: flawless execution and innovative flavor combinations. What I got: that, but also a level of hospitality that changes how you think about service (the table captain memorized every dietary preference mentioned during booking and adapted two courses). The specific course that justified the price: the beet dish with bone marrow and truffle — three ingredients that individually seem incompatible but create a flavor the table hadn't experienced before. Was it worth it? Yes, once. Not because the food was 10x better than a $65 meal, but because it showed what the ceiling of hospitality looks like."
- "My neighborhood food market — the vendors who changed how I cook: Not a travel video — the market 12 minutes from my apartment that I visit every Saturday morning and the vendors who have educated me over 2 years. The egg vendor who explained why his eggs have orange yolks (chicken diet and outdoor living). The cheese maker who cuts wheels to order and lets you taste before you buy. The Korean grandmother who sells banchan and whose kimchi is made with ingredients she describes in Korean (her daughter translates). The moment markets become interesting: when you know the vendors and they know what you'll ask for."

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `content_type` | Video type | `"restaurant_review"`, `"food_travel"`, `"market_tour"`, `"tasting_menu"`, `"neighborhood_guide"` |
| `location` | Where | `"Tokyo"`, `"NYC"`, `"local neighborhood market"` |
| `foods_featured` | What was eaten | `["tsukemen"`, `"tasting menu"`, `"kimchi from scratch"]` |
| `key_highlight` | Best moment | `"Fuji Ramen counter in Golden Gai"`, `"beet with bone marrow"` |
| `honest_assessment` | Real verdict | `"worth it once"`, `"one clear winner"` |
| `price_context` | Cost information | `"$365/person"`, `"$8 bowl"` |
| `tone` | Content energy | `"discovery"`, `"review"`, `"nostalgic"`, `"analytical"` |
| `duration_minutes` | Video length | `8`, `12`, `20` |
| `platform` | Distribution | `"youtube"`, `"instagram"`, `"tiktok"` |

## Workflow

1. Describe the food experience, the specific dishes, and the honest assessment
2. NemoVideo structures the food vlog with location markers and dish callouts
3. Restaurant names, dish names, prices, and tasting notes added automatically
4. Export with food vlog pacing suited to the discovery or review format

## API Usage

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "food-vlog-maker",
    "input": {
      "prompt": "The best cheap eats in Bangkok — everything under $3, nothing tourist-facing: The premise: Bangkok street food at prices Thais actually pay (not the tourist-price cart near the Grand Palace). The rule: look for the line of workers eating at 11:30am, that is the quality signal. The finds: Som Tum cart near Silom BTS — green papaya salad with fermented crab, illegal level of heat, $1.20. Khao Man Gai restaurant on a back soi — poached chicken over rice with ginger broth, $1.50, the condensed milk in the dipping sauce is the specific secret. The boat noodles shop that has been on the same corner since 1982 — beef broth with blood, $0.80 a cup, order four. The pad Thai at the tourist spots: $6 and fine. The pad Thai at the correct wok cart behind the temple: $1.80 and genuinely better because it is cooked to order in a wok that has 40 years of seasoning. Why Bangkok cheap food is the world standard: ingredient freshness (everything bought that morning), specialization (the woman who makes only khao man gai), and competition.",
      "content_type": "food_travel",
      "location": "Bangkok, Thailand",
      "foods_featured": ["som tum with fermented crab", "khao man gai", "boat noodles", "pad Thai"],
      "honest_assessment": "tourist-price is fine, local-price is genuinely better",
      "price_context": "under $3 per dish",
      "tone": "discovery",
      "duration_minutes": 12,
      "platform": "youtube",
      "hashtags": ["FoodVlog", "BangkokFood", "StreetFood", "FoodTravel", "BudgetFood"]
    }
  }'
```

## Tips for Best Results

- **The honest negative is what distinguishes real food content from promotion**: "Was it worth it? Yes, once. Not because the food was 10x better" or "the tourist-price cart is fine" — the qualified assessment is more credible than universal enthusiasm
- **Specific dish details create the vicarious experience**: "Thick concentrated tare, noodles dipped not submerged — order medium not small" — the specific ordering instruction is what makes food content useful for trip planning
- **The context that makes the food meaningful**: "The old man has been making the same shoyu broth since 1975" or "the woman who makes only khao man gai" — the specificity of dedication and specialization is what elevates a dish beyond its ingredients
- **Price context is essential for travel food content**: "$365/person vs $1.80 pad Thai from the correct cart" — the price reference helps viewers understand what kind of experience to expect
- **The quality signal for food travel**: "Line of workers eating at 11:30am" — the practical heuristic for finding quality food that viewers can apply on their own trips is the most saved content

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| YouTube | 1920×1080 | 10–20 min |
| Instagram Reels | 1080×1920 | 60–90s |
| TikTok | 1080×1920 | 60–180s |

## Related Skills

- `cooking-video-maker` — Home cooking technique content
- `recipe-video-maker` — Recipe recreation content
- `travel-vlog-maker` — Travel and destination content
