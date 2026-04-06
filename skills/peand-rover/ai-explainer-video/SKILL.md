---
name: ai-explainer-video
version: "1.0.0"
displayName: "AI Explainer Video — Create Animated Explainer Videos for Products and Services"
description: >
  Create animated explainer videos with AI — produce whiteboard animations, motion graphics, character-driven narratives, and infographic videos that explain products, services, processes, and concepts in 60-120 seconds. NemoVideo generates complete explainer videos from a product description: problem-solution narrative structure, professional animation matched to brand style, voiceover narration, background music, and platform-ready export. The 90-second video that converts landing page visitors into customers. Explainer video maker, animated explainer, product explainer video, whiteboard animation maker, motion graphics explainer, SaaS explainer video, startup explainer video.
metadata: {"openclaw": {"emoji": "💡", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# AI Explainer Video — 90 Seconds to Make Anyone Understand Your Product

An explainer video answers one question: "What does this do and why should I care?" Answering that question in 90 seconds with animation, narration, and music is the most effective way to convert a confused visitor into an interested prospect. Landing pages with explainer videos convert 20% higher than those without. Explainer videos on product pages increase time-on-page by 2.6x. Sales teams that send explainer videos in outreach get 3x higher response rates. The format works because it combines three communication channels simultaneously: visual (animation shows abstract concepts as concrete images), auditory (narration explains in plain language), and emotional (music and pacing create engagement). Text alone uses one channel. Images use one. Video uses all three. The traditional explainer video production process: write a script (1-2 weeks), storyboard (1 week), illustration/design (2-3 weeks), animation (2-4 weeks), voiceover recording (3-5 days), music and sound design (3-5 days), revisions (1-2 weeks). Total: 8-12 weeks and $5,000-25,000. NemoVideo produces explainer videos from a product description. Describe what your product does, who it is for, and what problem it solves — the AI generates: a problem-solution script, storyboarded animation, professional voiceover, background music, and polished export.

## Use Cases

1. **SaaS Product — Homepage Explainer (60-90s)** — A project management tool needs a homepage video that converts visitors who land from ads. NemoVideo produces: Hook (5s) — "Your team wastes 12 hours per week on status meetings" (animated clock draining, team looking frustrated), Problem (15s) — tasks scattered across email, chat, spreadsheets; nobody knows what anyone is working on (animated chaos), Solution (10s) — introduce the product as the single source of truth (chaos transforms to clean dashboard), Features (30s) — 3 key features demonstrated through animation (task boards, automated updates, team analytics), Social Proof (10s) — "Trusted by 10,000 teams" (animated counter + logo ticker), CTA (10s) — "Start your free trial in 30 seconds" (button animation). The 90-second video that sits above the fold and converts cold traffic.

2. **Startup — Investor Pitch Explainer (60-120s)** — A startup needs to explain a complex product to investors who have 2 minutes of attention. NemoVideo creates: Market problem (20s) — the pain point with market size data (animated statistics showing scale), Current solutions (15s) — why existing approaches fail (animated comparison showing gaps), The product (25s) — how it works differently (simplified animation of the core mechanism), Traction (15s) — key metrics animated (users, revenue, growth rate), Vision (15s) — where this goes at scale (expanding market visualization). The explainer that replaces 10 slides of a pitch deck with one memorable video.

3. **Complex Service — Process Explanation (90-180s)** — An insurance company needs to explain how their claims process works. NemoVideo: animates the entire workflow step by step (file claim → assessment → approval → payment), uses character animation to show the customer's experience at each stage, highlights the speed advantage over competitors (timeline comparison animation), addresses common concerns ("What if my claim is denied?" — animation showing the appeal process), and ends with reassurance and CTA. The complex multi-step process becomes a simple visual story.

4. **Education — Concept Explainer (2-5 min)** — A teacher needs to explain supply and demand to economics students. NemoVideo generates: the concept of demand (animated buyers entering a market, price-quantity relationship visualized), the concept of supply (animated producers increasing output as price rises), equilibrium (the two curves meeting — the "aha" visual moment), disruption examples (what happens when supply drops: animation of shortage, price spike, consumer behavior change), and real-world application (current news example animated). Abstract economic theory becomes visual, intuitive, and memorable.

5. **App Onboarding — Feature Walkthrough (60-90s)** — A mobile app has low activation rates because users do not discover key features. NemoVideo creates: an animated app walkthrough showing the 5 actions that lead to an "aha moment" (the actions correlated with long-term retention), each step animated within a phone device frame (realistic touch gestures, screen transitions), narrated with encouraging instructional tone ("Tap here to see your personalized dashboard"), and delivered as both an in-app video and an email onboarding sequence. The onboarding video that turns downloads into active users.

## How It Works

### Step 1 — Describe Your Product or Concept
What it does, who it is for, what problem it solves, and what makes it different. Include any brand guidelines (colors, tone, existing visual language).

### Step 2 — Choose Animation Style
Modern flat design, whiteboard sketch, 3D isometric, character-driven, kinetic typography, infographic motion, or mixed.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-explainer-video",
    "prompt": "Create a 90-second explainer video for an AI writing assistant SaaS. Target: content marketers who spend 4+ hours per article. Structure: (1) Hook — content marketers drowning in deadlines (5s), (2) Problem — writing is slow, editing is slower, research is slowest (20s), (3) Solution — AI assistant that researches, drafts, and edits (10s), (4) Feature 1: AI research — finds sources in seconds (15s), (5) Feature 2: Draft generation — first draft in minutes (15s), (6) Feature 3: Style matching — learns your brand voice (10s), (7) Social proof — 5,000 marketers, 10M articles (5s), (8) CTA — start free, no credit card (10s). Animation: modern flat with character. Voice: friendly confident female. Music: upbeat tech at -18dB. Brand: #7C3AED purple, #FFFFFF white.",
    "animation_style": "modern-flat-character",
    "voice": "friendly-confident-female",
    "music": {"style": "upbeat-tech", "volume": "-18dB"},
    "brand_colors": ["#7C3AED", "#FFFFFF"],
    "duration": 90,
    "formats": ["16:9", "9:16"]
  }'
```

### Step 4 — Review and Deploy
Preview: animation quality, narration pacing, message clarity. Does a first-time viewer understand the product in 90 seconds? Deploy to homepage, ads, sales outreach, and social media.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Product description and video structure |
| `animation_style` | string | | "modern-flat", "whiteboard", "3d-isometric", "character-driven", "kinetic-typography", "infographic" |
| `voice` | string | | "friendly-female", "authoritative-male", "energetic", "warm-narrator" |
| `music` | object | | {style, volume} |
| `brand_colors` | array | | Hex codes |
| `duration` | integer | | 60, 90, 120, or custom seconds |
| `formats` | array | | ["16:9", "9:16", "1:1"] |
| `script` | string | | Custom script (optional — AI generates if not provided) |
| `characters` | boolean | | Include animated characters |
| `captions` | object | | {style, text, bg} |

## Output Example

```json
{
  "job_id": "aev-20260328-001",
  "status": "completed",
  "duration": "1:28",
  "animation_style": "modern-flat with character",
  "scenes": 8,
  "production": {
    "voice": "friendly-confident-female",
    "music": "upbeat-tech at -18dB",
    "brand_colors": ["#7C3AED", "#FFFFFF"]
  },
  "outputs": {
    "landscape": {"file": "ai-writer-explainer-16x9.mp4", "resolution": "1920x1080"},
    "vertical": {"file": "ai-writer-explainer-9x16.mp4", "resolution": "1080x1920"}
  }
}
```

## Tips

1. **The problem section is more important than the solution section** — If the viewer does not feel the pain, the solution is irrelevant. Spend 20-30% of the video making the problem visceral and relatable. The viewer should think "that's exactly my situation" before the product is even mentioned.
2. **One concept per scene, maximum 3 features** — Explainer videos that try to show every feature become confusing infomercials. Pick the 3 features that matter most to the target audience. Everything else goes on the features page.
3. **90 seconds is the ideal length for most explainer videos** — Under 60 seconds: not enough time to build problem-solution narrative. Over 120 seconds: attention drops significantly. 90 seconds gives enough time for hook + problem + solution + 3 features + CTA.
4. **Character animation creates empathy that abstract shapes cannot** — A frustrated character the viewer identifies with creates emotional engagement. Geometric shapes moving on screen communicate information but not feeling. For products that solve human problems, use character animation.
5. **The CTA must be specific and low-friction** — "Learn more" is vague. "Start your free trial — no credit card, 30 seconds to set up" is specific and removes friction. The CTA should make the next step feel effortless.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | Homepage / YouTube / presentation |
| MP4 9:16 | 1080x1920 | Social media ads / Reels |
| MP4 1:1 | 1080x1080 | Instagram / LinkedIn / Facebook |
| GIF | 720p | Email / landing page preview |

## Related Skills

- [ai-testimonial-video](/skills/ai-testimonial-video) — Testimonial videos
- [ai-promo-video-maker](/skills/ai-promo-video-maker) — Promo videos
- [ai-commercial-video](/skills/ai-commercial-video) — Commercial videos
