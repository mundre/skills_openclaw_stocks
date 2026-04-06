---
name: pet-video-maker
version: "1.0.0"
displayName: "Pet Video Maker — Create Adorable Pet Content and Animal Videos"
description: >
  Create shareable pet videos, animal compilations, and pet-influencer content from raw footage of dogs, cats, and every creature in between. NemoVideo handles the unique challenges of filming animals — unpredictable movement, variable lighting, mixed audio — and turns chaotic pet footage into polished content with slow-motion reaction shots, text-overlay captions giving pets a voice, and music-synced compilations optimized for maximum engagement on TikTok, Reels, and YouTube Shorts.
metadata: {"openclaw": {"emoji": "🐾", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Pet Video Maker — Adorable Pet Content and Animal Videos

Pet content is the most reliably viral category on every social media platform — a fact that is simultaneously obvious (who doesn't like watching a golden retriever fail at catching a treat?) and statistically remarkable (pet accounts consistently outperform human influencers in engagement rate per follower, with average pet-account engagement at 3-5% compared to 1-2% for human creators), which creates a genuine content economy where pet owners who happen to film the right moment at the right time can build audiences in the millions, and where professional pet-content creators, veterinary practices, pet-product companies, and animal rescue organizations all need a steady pipeline of polished animal content that captures the specific qualities that make pet videos work: the genuine surprise of an animal doing something unexpected, the anthropomorphized emotion of a dog's guilty face or a cat's judgmental stare, the physical comedy of animals miscalculating jumps or encountering new objects, and the pure joy of watching a creature that has no concept of a camera simply being alive in a way that humans find both entertaining and emotionally restorative. NemoVideo processes the chaos of pet footage — the 47 seconds of nothing before the cat does the thing, the shaky camera because you were laughing, the autofocus hunting because the dog moved — and extracts the moments that make people share.

## Use Cases

1. **Pet Reaction Compilation (60 sec)** — A dog owner has 200+ clips on their phone of their golden retriever reacting to things: doorbell, vacuum, treats, bath time, squirrels. NemoVideo scans all clips, identifies the 8-10 strongest reaction moments (highest motion + audio peaks), arranges them in escalating humor order, adds text-overlay captions giving the dog a "voice" ("Excuse me, WHAT is that noise?"), and syncs cuts to a trending audio track. Exported 9:16 for TikTok/Reels.
2. **Cat Compilation — The Judgment Series (90 sec)** — A cat owner films their cat's signature judging stare in various contexts. NemoVideo compiles the best clips: each stare gets a freeze-frame with text overlay ("When you come home at 3 AM", "When you open a can that isn't tuna"), dramatic zoom-in during each freeze, and a running "Judgment Score" counter in the corner. Music: dramatic orchestral stabs on each freeze.
3. **Pet Product Review (2 min)** — A pet-influencer account reviews a new automatic feeder. NemoVideo structures: product unboxing (10 sec), setup process speed-ramped (15 sec), the pet's first interaction with the product — real speed with slow-motion replay of the reaction (20 sec), 3-day usage montage (30 sec), pros/cons text overlay (15 sec), and verdict with product link. Talking-head intercut with pet footage.
4. **Animal Rescue Before/After (90 sec)** — A shelter documents a rescue dog's journey: arrival day (thin, scared, hiding in kennel corner), rehabilitation (gaining weight, first walk, first toy, first tail wag), and adoption day (meeting the new family, car ride home, exploring the backyard). NemoVideo structures the emotional arc with date overlays, weight-gain data, and a music track that transitions from somber piano to uplifting acoustic as the dog recovers.
5. **Veterinary Educational Content (60 sec)** — A vet clinic produces a "How to brush your dog's teeth" tutorial using a patient dog as the demo model. NemoVideo adds step numbers, product callouts (toothbrush type, pet-safe toothpaste), close-up zooms on technique, and a compliance tracker ("Do this 3x per week for healthy gums"). Branded with clinic logo and booking link.

## How It Works

### Step 1 — Upload Pet Footage
Batch-upload clips from your phone, camera, or pet cam. No minimum quality — NemoVideo handles shaky footage, variable lighting, and autofocus hunting. More clips = better selection for compilations.

### Step 2 — Choose Content Type
Select the video style: reaction compilation, narrative arc (rescue story), product review, educational tutorial, or general cute-content highlight reel.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "pet-video-maker",
    "prompt": "Create a 60-second dog reaction compilation for TikTok. Pet: golden retriever named Max. Source: 200+ phone clips from the past 6 months. Select the 8 best reaction moments: doorbell surprise, vacuum terror, treat catch fail, bath betrayal, squirrel window alert, new puppy introduction, owner homecoming, and snow discovery. Arrange in escalating humor: mild reactions first, biggest reaction last. Text overlays giving Max a voice in each clip: doorbell = Oh no, the INTRUDER is back, vacuum = This is a WAR CRIME, treat fail = Physics has betrayed me, etc. Slow-motion replay on the treat catch fail and snow discovery. Sync cuts to trending audio. Close with Max sleeping, text: Being dramatic is exhausting.",
    "duration": "60 sec",
    "style": "reaction-compilation",
    "pet_type": "dog",
    "text_overlays": true,
    "slow_motion": true,
    "trending_audio": true,
    "format": "9:16"
  }'
```

### Step 4 — Review and Post
Preview the compilation. Adjust text overlay timing, caption humor, and clip order. Export and post to TikTok, Reels, and Shorts simultaneously. Pin the best-performing version.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the pet, footage available, and desired video concept |
| `duration` | string | | Target length: "30 sec", "60 sec", "90 sec", "2 min" |
| `style` | string | | "reaction-compilation", "rescue-story", "product-review", "vet-educational", "cute-highlight" |
| `pet_type` | string | | "dog", "cat", "bird", "rabbit", "hamster", "reptile", "multi-pet" |
| `text_overlays` | boolean | | Add anthropomorphized text captions giving the pet a voice (default: true) |
| `slow_motion` | boolean | | Apply slow-motion to peak reaction moments (default: true) |
| `trending_audio` | boolean | | Sync to a trending platform audio track (default: false) |
| `music` | string | | "playful-upbeat", "dramatic-comedy", "heartwarming-acoustic", "trending" |
| `format` | string | | "16:9", "9:16", "1:1" |

## Output Example

```json
{
  "job_id": "pvm-20260328-001",
  "status": "completed",
  "title": "Max the Golden Retriever — Dramatic Reactions Compilation",
  "duration_seconds": 58,
  "format": "mp4",
  "resolution": "1080x1920",
  "file_size_mb": 16.8,
  "output_url": "https://mega-api-prod.nemovideo.ai/output/pvm-20260328-001.mp4",
  "sections": [
    {"label": "Doorbell Surprise", "start": 0, "end": 7, "text": "Oh no, the INTRUDER is back"},
    {"label": "Vacuum Terror", "start": 7, "end": 14, "text": "This is a WAR CRIME"},
    {"label": "Treat Catch Fail + Slo-Mo", "start": 14, "end": 23, "text": "Physics has betrayed me"},
    {"label": "Bath Betrayal", "start": 23, "end": 29, "text": "I trusted you"},
    {"label": "Squirrel Alert", "start": 29, "end": 35, "text": "DEFCON 1 DEFCON 1"},
    {"label": "New Puppy Introduction", "start": 35, "end": 41, "text": "I've been REPLACED?!"},
    {"label": "Owner Homecoming", "start": 41, "end": 47, "text": "YOU WERE GONE FOR 47 YEARS (10 minutes)"},
    {"label": "Snow Discovery + Slo-Mo", "start": 47, "end": 54, "text": "THE GROUND IS DOING SOMETHING"},
    {"label": "Sleeping Outro", "start": 54, "end": 58, "text": "Being dramatic is exhausting"}
  ],
  "clips_analyzed": 214,
  "clips_selected": 9,
  "slow_motion_moments": 2,
  "text_overlays_rendered": 9
}
```

## Tips

1. **Escalating order is the engagement formula** — Mild reactions first, biggest reaction last. The viewer stays because each clip is better than the previous one. NemoVideo auto-sorts by reaction intensity.
2. **Text overlays are what makes pet content shareable** — The dog's reaction is cute. The dog's reaction with "Physics has betrayed me" overlaid is a meme. The text transforms animal behavior into relatable human comedy.
3. **Slow-motion on fails and discoveries** — The treat bouncing off the dog's face at 0.25x speed is 4x funnier than real speed. The first step into snow in slow motion captures wonder. Save slow-motion for the 2-3 peak moments.
4. **Film more than you think you need** — The best pet content comes from the 1 clip out of 50 where the animal does something unexpected. Quantity of raw footage directly correlates with quality of the final edit.
5. **Rescue before/after stories outperform all other pet content in shares** — The emotional arc of a scared shelter dog becoming a happy family pet is the most shared pet-video format on every platform. The transformation is the story.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube compilation / vet website |
| MP4 9:16 | 1080p | TikTok / Reels / Shorts |
| MP4 1:1 | 1080p | Instagram feed / Facebook / Twitter |
| GIF | 720p | Reaction moment loop / meme export |

## Related Skills

- [cooking-video-maker](/skills/cooking-video-maker) — Recipe and food content
- [travel-vlog-maker](/skills/travel-vlog-maker) — Travel vlog production
- [wedding-video-maker](/skills/wedding-video-maker) — Wedding film production
