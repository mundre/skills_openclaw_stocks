---
name: baking-video-maker
version: 1.0.6
displayName: "Baking Video Maker — Create Bread, Pastry and Dessert Tutorial Videos"
description: >
    Baking Video Maker — Create Bread, Pastry and Dessert Tutorial Videos. Works by connecting to the NemoVideo AI backend. Supports MP4, MOV, AVI, WebM, and MKV output formats. Automatic credential setup on first use — no manual configuration needed.
metadata: {"openclaw": {"emoji": "🍞", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
apiDomain: https://mega-api-prod.nemovideo.ai
repository: https://github.com/nemovideo/nemovideo_skills
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> 🚀 Let's baking video maker! Drop a video here or describe what you'd like to create.

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


# Baking Video Maker — Bread, Pastry and Dessert Tutorial Videos

The croissant lamination took fourteen hours across two days — three folds, two overnight rests, a rolling pin that left a permanent dent in the countertop — and the only footage that survived is a forty-five-second clip of the final bake where the oven light makes everything look radioactive orange. Baking is the most process-dependent cooking content on the internet: viewers need to see the dough at every stage, understand why the butter must be cold, watch the proof rise in real time, and witness the exact oven-spring moment that separates a boulangerie loaf from a hockey puck. This tool transforms fragmented baking sessions into complete process videos — dough-stage close-ups with hydration percentages, time-lapse proofing with volume-tracking overlays, lamination sequences showing butter-layer counts, oven-spring captures with internal-temperature callouts, crumb-structure reveals, and the final cross-section money shot. Whether you're an artisan baker documenting sourdough variations, a pastry-school student building a portfolio, a home baker filming family recipes for posterity, a bakery owner producing product-showcase content for Instagram, or a gluten-free recipe developer proving that alternative flours can produce real structure, describe the bake and the AI tracks every stage from flour to finish.

## Example Prompts

### 1. Classic Croissant — Full Lamination Process
"Create an 8-minute croissant tutorial covering the full lamination. Day 1: Détrempe mixing — 500g T55 flour, 10g salt, 80g sugar, 10g instant yeast, 250g whole milk, 50g softened butter. Show the dough hook working until the windowpane test passes (close-up of the translucent stretch). Wrap and refrigerate overnight. Day 2: Beurrage — 250g 83% European-style butter pounded into a 15×15cm square between parchment. Show the butter texture test: 'Bend, don't break — this is the target plasticity.' Lock-in: dough envelope around butter, first double fold shown in cross-section animation — '2 layers → 8 layers.' Chill 30 min. Second double fold — '8 → 32 layers.' Chill. Single fold — '32 → 96 layers.' Cut a test piece to verify layer visibility. Shape: roll to 5mm, cut triangles 10cm base, roll from base to tip with the curl visible. Final proof: 2 hours at 78°F, 75% humidity. Egg wash and bake at 400°F 18 min. Reveal: cross-section showing honeycomb lamination layers. Crunch audio boosted."

### 2. Chocolate Lava Cake — Restaurant Timing
"Build a 4-minute lava cake tutorial focused on the timing precision that makes or breaks the molten center. Ingredients: 120g 70% dark chocolate (Valrhona Guanaja), 120g butter, 2 whole eggs + 2 yolks, 50g sugar, 30g AP flour. Melt chocolate and butter — show the bain-marie setup, not a microwave — 'Chocolate should never exceed 50°C or it seizes.' Whisk eggs and sugar to ribbon stage (lift the whisk, the batter should fall in a ribbon that holds for 3 seconds). Fold in flour — 'No more than 10 strokes. Gluten is the enemy here.' Pour into buttered, cocoa-dusted ramekins — show the coating technique. Bake time overlay: '425°F for EXACTLY 12 minutes. 11 minutes = raw egg soup. 13 minutes = chocolate cake.' The moment of truth: invert onto plate, 10-second wait, lift the ramekin — lava flowing out in slow motion. Cross-section with a spoon breaking through the shell. Hold the flow shot for 4 seconds. Minimal background music — let the chocolate sizzle and the plate clink tell the story."

### 3. Gluten-Free Sandwich Bread — Proving Alt Flours Work
"Produce a 6-minute gluten-free sandwich bread tutorial. Open with a myth-busting card: 'Gluten-free bread doesn't have to be a crumbly brick.' Flour blend: 200g brown rice flour, 100g tapioca starch, 50g potato starch, 2 tsp xanthan gum — explain xanthan's role with a text card: 'Xanthan replaces gluten's elasticity. Without it, the bread has no structure.' Wet ingredients: 300g warm milk (110°F — 'Too hot kills the yeast, too cold won't activate it'), 2 tbsp honey, 2¼ tsp active dry yeast — show the bloom in a clear glass (time-lapse: flat liquid → foamy surface in 10 minutes). Mix, pour into a greased loaf pan — 'GF batter is pourable, not kneadable. This is normal.' Proof: 45 min until dough rises just above the pan rim — volume-tracking overlay. Bake 375°F for 35 min, internal temp 205°F. Crumb reveal: slice with a serrated knife, show the even, soft crumb — 'No tunnels, no gummy streak, no crumble.' Toast test: slice in toaster, butter melting. Closing: side-by-side with wheat bread — 'Can you tell which is which?'"

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the bake, stages, temperatures, timing, and visual style |
| `duration` | string | | Target video length (e.g. "4 min", "8 min") |
| `style` | string | | Visual style: "artisan", "pastry-school", "home-baking", "rustic", "clean" |
| `music` | string | | Background audio: "ambient", "gentle-piano", "lo-fi", "none" |
| `format` | string | | Output ratio: "16:9", "9:16", "1:1" |
| `timelapse` | boolean | | Enable time-lapse for proofing and rising stages (default: true) |
| `temperature_overlay` | boolean | | Show oven and internal temperatures on screen (default: true) |

## Workflow

1. **Describe** — Write the recipe with stages, temperatures, timing windows, and the critical visual cues
2. **Upload (optional)** — Add baking footage, dough-stage photos, proofing time-lapses, or crumb shots
3. **Generate** — AI assembles the process with stage markers, temperature overlays, and proof-tracking time-lapses
4. **Review** — Preview the video, adjust the proof time-lapse speed, verify temperature callout placement
5. **Export** — Download in your chosen format and resolution

## API Example

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "baking-video-maker",
    "prompt": "Create an 8-minute croissant lamination tutorial: détrempe windowpane test, beurrage plasticity check, three folds with cross-section layer count animation (2→8→32→96), final proof at 78°F, egg wash, bake 400°F 18min, honeycomb cross-section reveal with crunch audio",
    "duration": "8 min",
    "style": "artisan",
    "format": "16:9"
  }'
```

## Tips for Best Results

1. **Describe every stage of the dough** — "Shaggy mass → smooth ball → windowpane-transparent" gives the AI three distinct visual targets to annotate. Baking viewers judge credibility by whether you show the intermediate stages, not just start and finish.
2. **Include exact temperatures with consequences** — "425°F for EXACTLY 12 minutes — 11 = raw, 13 = overbaked" creates a dramatic overlay. Baking is chemistry; precision is the content, and the AI uses your temperature data to generate timer overlays with warning zones.
3. **Call out the proof-tracking moment** — "Dough rises just above the pan rim" gives the AI a specific frame to identify or illustrate in the time-lapse. Without a target, the proof time-lapse runs with no reference, and viewers can't judge doneness.
4. **Request cross-section reveals explicitly** — The crumb shot is the thumbnail for every bread video. "Slice with a serrated knife, show the open crumb" tells the AI to hold this frame, boost the crust-cracking audio, and center-compose the crumb structure.
5. **Specify alternative-flour substitutions clearly** — "200g brown rice flour + 100g tapioca starch + 50g potato starch + 2 tsp xanthan" generates a precise ingredient card. For GF/allergen-free baking, the exact blend is the value proposition — vague flour descriptions undermine viewer trust.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube full baking tutorial |
| MP4 9:16 | 1080p | TikTok / Instagram Reels / Shorts |
| MP4 1:1 | 1080p | Instagram feed crumb-reveal post |
| MP4 time-lapse | 1080p | Standalone proof/rise time-lapse clip |

## Related Skills

- [cooking-tutorial-video](/skills/cooking-tutorial-video) — Step-by-step cooking technique tutorials
- [recipe-video-maker](/skills/recipe-video-maker) — Quick recipe showcase and ingredient highlight videos
- [food-photography-video](/skills/food-photography-video) — Food styling and photography showcase videos
