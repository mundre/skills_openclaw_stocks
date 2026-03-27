---
name: unboxing-video-maker
version: "1.0.0"
displayName: "Unboxing Video Maker — Create Unboxing and First Impressions Videos"
description: >
  Unboxing Video Maker — Create Unboxing and First Impressions Videos.
metadata: {"openclaw": {"emoji": "📦", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Unboxing Video Maker — Unboxing and First Impressions Videos

The package arrived twenty minutes ago, it's sitting on a desk with good lighting, and the camera is rolling — but the person holding the box knife is about to make every mistake the format allows: ripping the seal too fast for the slow-motion replay, blocking the product reveal with their own hand, spending ninety seconds on the shipping label nobody cares about, and completely forgetting to show the charger brick that half the comments will ask about. Unboxing videos are the most deceptively simple format on YouTube — the concept is "open box, show thing" — but the channels that turn unboxings into millions of views understand that the format is really about anticipation engineering, reveal pacing, and the specific brand of material ASMR that makes viewers feel like they're opening the box themselves. This tool transforms raw unboxing footage into polished first-impressions videos — slow-motion seal breaks with satisfying audio emphasis, overhead content layouts where every accessory is labeled as it appears, product reveal moments with rack-focus and dramatic lighting shifts, first-power-on sequences with genuine reaction captures, size and weight comparisons against familiar reference objects, and the honest first-impression commentary that viewers trust more than a review published three weeks later. Built for tech YouTubers filming daily unboxings, lifestyle creators showcasing subscription boxes, sneakerheads documenting limited-edition releases, collectors revealing rare items, brand ambassadors creating sponsored unboxing content, and anyone who understands that the moment before the box opens is worth more than every spec sheet combined.

## Example Prompts

### 1. Premium Tech Unboxing — Flagship Phone
"Create a 6-minute flagship phone unboxing. Pre-open (0-20 sec): sealed box on a dark wood desk, overhead angle, hands entering frame — slow push-in as I describe what's supposedly inside. 'They're calling this their most ambitious phone ever. The internet has opinions. Let's see what $1,199 actually gets you.' Seal break: slow-motion pull of the tab, satisfying adhesive-peel ASMR (boost that audio), lid lift with magnetic resistance. First reveal: the phone face-down in its cradle — hold for 2 seconds before lifting. The pause is the content. Lift and flip: first look at the screen, peel the protective film (slow-mo, this is a main-character moment), power button press — boot animation on screen, reaction in real time. Box contents: overhead flat-lay, each item pulled out and placed in a grid — phone, cable (USB-C to USB-C, no brick), SIM tool, documentation, sticker. Label each item with animated text as it lands. Call out what's missing: 'No charger. No case. No headphones. $1,199.' First impressions hands-on (3-5 min): weight in hand ('227g — I feel it'), button click test (mute switch, volume, power — rate the click), color under different lighting (walk to window, show how the titanium shifts), camera bump height with a coin comparison. First photo: point it at something interesting, show the result full-screen for 3 seconds. Display: swipe through home screens to show 120Hz, pull up a colorful image to show the OLED contrast. Closing: phone back on desk — 'First impression: the hardware is $1,199. Whether the software is... that's the review.' Subscribe card."

### 2. Sneaker Unboxing — Limited Release
"Build a 4-minute sneaker unboxing for a limited-edition collaboration release. Atmosphere matters — this is a collector moment. Opening shot: shipping box on a clean white surface, order confirmation visible on phone next to it (blur the personal info). 'Got the W on these. 47,000 people tried. Let's see if they were worth the 6 AM alarm.' Outer box: cut the tape (satisfying knife sounds), reveal the branded shoe box — pause on the special-edition packaging art, rotate to show all sides. Box details: collaboration logo close-up, limited-edition numbering if present, tissue paper color (these details matter to sneakerheads). The reveal: lift the lid, tissue paper fold-back in slow-mo, first glimpse — hold the angle for 3 seconds before reaching in. In-hand: rotate slowly, show every angle — medial side, lateral side, heel tab, tongue label, outsole pattern. Macro shots: stitching quality close-up, material texture (is the leather tumbled or smooth?), collaboration details (special insole print, heel embroidery, custom lace tips). On-feet: lace up in real time, standing shot, walking shot, jeans-and-sneaker outfit check, the profile silhouette that matters on Instagram. Comparison: next to the general-release version — highlight every difference. Storage: back in the box, tissue paper replaced, on the shelf next to the collection. Closing: 'Resale is at $380. Am I keeping or selling? Keeping. Obviously.' Clean, minimal aesthetic — white surface, directional lighting, no clutter, sneaker as the star."

### 3. Subscription Box — Monthly Surprise
"Produce a 5-minute subscription box unboxing — a premium coffee subscription. The format: I don't know what's inside (genuine blind unboxing). Opening: the box on a kitchen counter, subscription card visible — '$45/month for "the world's best single-origin beans." Month 3. The first two months were excellent. Let's see if they can keep it up.' Box open: pull out items one by one, genuine first reactions. Item 1: bag of beans — read the label aloud (origin, roast date, tasting notes), smell test reaction (close the eyes, be honest — 'Ethiopian Yirgacheffe... fruity, bright, I'm getting blueberry from the smell alone'). Show the roast date — 'Roasted 4 days ago. That's what $45 buys you: freshness.' Item 2: second bag — different origin (Guatemalan? Colombian?), contrast with the first bag. Item 3: the extras — brewing guide card, sticker, discount code for gear. Read the guide: 'They recommend a V60 pour-over, 15:1 ratio, 94°C. Let's try it.' Brew sequence (90 sec): grind the beans (show the grind size), pour-over process time-lapse, first sip reaction. Honest take: 'The Ethiopian is exceptional. The Guatemalan is good, not $22.50-per-bag good.' Value breakdown: animated overlay — cost per cup calculation, comparison to specialty shop prices. Rating: animated scorecard — Bean Quality, Freshness, Value, Variety, Extras. Overall: 7.8/10. 'Month 3: still worth it.' Warm kitchen aesthetic — natural light, wood surfaces, close-up steam shots on the brew, cozy morning vibe."

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the product, unboxing flow, reveal moments, and first impressions |
| `duration` | string | | Target video length (e.g. "4 min", "6 min") |
| `style` | string | | Unboxing style: "tech-premium", "sneaker-collector", "subscription-blind", "luxury-asmr", "quick-shorts" |
| `music` | string | | Background audio: "ambient-chill", "hype-beat", "asmr-minimal", "none" |
| `format` | string | | Output ratio: "16:9", "9:16", "1:1" |
| `asmr_audio` | boolean | | Enhance tactile sounds — tape cuts, seal peels, material textures (default: true) |
| `labels` | boolean | | Add animated text labels to box contents in overhead layout (default: true) |

## Workflow

1. **Describe** — Outline the product, reveal sequence, key moments, and first-impression talking points
2. **Upload** — Add your raw unboxing footage, overhead shots, detail close-ups, and reactions
3. **Generate** — AI edits with reveal pacing, slow-motion emphasis, content labels, and ASMR audio
4. **Review** — Preview the edit, adjust the reveal timing and first-impression commentary cuts
5. **Export** — Download in your chosen format and resolution

## API Example

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "unboxing-video-maker",
    "prompt": "Create a 6-minute flagship phone unboxing: slow-mo seal break, magnetic lid lift, film peel moment, overhead flat-lay of all contents with labels, first power-on reaction, hands-on weight and button tests, first photo test, 120Hz scrolling demo, closing first impression",
    "duration": "6 min",
    "style": "tech-premium",
    "asmr_audio": true,
    "labels": true,
    "music": "ambient-chill",
    "format": "16:9"
  }'
```

## Tips for Best Results

1. **Pause before the reveal** — The moment before the box opens is worth more than the product inside. "Hold for 2 seconds before lifting" in your prompt tells the AI to insert a deliberate pause that builds anticipation. Rushing the reveal kills the format's core emotion.
2. **Boost the tactile audio** — Tape ripping, seal peeling, magnetic lid clicks, protective-film removal — these sounds trigger the satisfying ASMR response that keeps viewers watching. The AI enhances tactile frequencies when asmr_audio is enabled.
3. **Show what's missing** — "No charger. No case. $1,199" is content. Viewers want to know what's NOT in the box as much as what is. Include explicit callouts of missing items and the AI adds labeled empty spaces in the overhead layout.
4. **Use overhead flat-lay for box contents** — Items placed in a grid with animated labels is the visual language of unboxing. It's scannable, shareable as a screenshot, and lets viewers assess value at a glance. The AI generates labeled grid layouts from your content list.
5. **Give genuine first reactions, not polished takes** — "I'm getting blueberry from the smell alone" with closed eyes is authentic; "This features premium aromatic notes" is a press release. The AI preserves your natural reaction timing and even adds subtle zoom on reaction moments.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube unboxing / website product reveal |
| MP4 9:16 | 1080p | TikTok / YouTube Shorts / Instagram Reels |
| MP4 1:1 | 1080p | Instagram post / Twitter/X product reveal |
| GIF | 720p | Product reveal loop / Reddit unboxing post |

## Related Skills

- [tech-review-video](/skills/tech-review-video) — Tech review and comparison videos
- [product-demo-video](/skills/product-demo-video) — Product walkthrough and feature demo videos
- [brand-video-maker](/skills/brand-video-maker) — Brand story and company identity videos
