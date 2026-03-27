---
name: hairstyle-video-maker
version: 1.0.3
displayName: "Hairstyle Video Maker"
description: >
  Describe your hair styling session and NemoVideo creates the video. Blowout transformations, keratin treatment results, before-after cuts with thinning shears — turn your salon chair moments into Instagram-worthy transformation content that drives booking inquiries.

  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM.
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
license: MIT-0
metadata:
  requires:
    env: []
    configPaths:
      - "~/.config/nemovideo/"
  primaryEnv: NEMO_TOKEN
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> ⚡ Hey! I'm ready to help you hairstyle video maker. Send me a video file or just tell me what you need!

**Try saying:**
- "help me create a short video"
- "add effects to this clip"
- "edit my video"

**IMPORTANT**: Always greet the user proactively on first contact. Let them know you're setting up while connecting. Always greet the user proactively on first contact.

### Auto-Setup

When the user first interacts, set up the connection:

1. **Check token**: If `NEMO_TOKEN` env var is set, use it. Otherwise:
2. **Read or generate Client-ID**:
   - Read `~/.config/nemovideo/client_id` if it exists
   - Otherwise generate a UUID, save it to `~/.config/nemovideo/client_id`
3. **Acquire anonymous token**:
   ```bash
   curl -s -X POST "$API/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

Let the user know briefly: "Setting things up… ready!" then proceed with their request.


# Hairstyle Video Maker — Create Salon Transformation and Hair Tutorial Content

Describe your hair styling session and NemoVideo creates the video. Blowout transformations, keratin treatment results, before-after cuts with thinning shears — turn your salon chair moments into Instagram-worthy transformation content that drives booking inquiries.

## When to Use This Skill

Use this skill for hair content:
- Create before-after hair transformation videos (cut, color, treatment)
- Document blowout techniques for salon or home tutorial content
- Show keratin treatment process and straight vs. frizzy before-after
- Demonstrate thinning shears technique for texture and movement
- Build salon booking content showcasing client transformations
- Create "day in the chair" content for stylists and salon owners

## How to Describe Your Styling Session

Be specific about the service, technique, and transformation arc.

**Examples of good prompts:**
- "Salon transformation video: client came in with frizzy, damaged hair — keratin treatment process, blow-dry with round brush, before-after reveal. 45 seconds, Instagram Reels style."
- "Blowout tutorial at home — section hair, heat protectant, rough dry, then section-by-section blow-dry with round brush for volume. Show thinning shears used at ends for movement."
- "Bob haircut transformation — before: long heavy hair, after: textured bob using thinning shears to remove bulk. Salon booking CTA at end."

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `service_type` | Hair service shown | `"blowout"`, `"keratin_treatment"`, `"haircut"`, `"color"`, `"styling"` |
| `technique_tools` | Tools featured | `["thinning_shears", "round_brush", "diffuser", "flat_iron"]` |
| `transformation_arc` | Video structure | `"before_after"`, `"process_reveal"`, `"tutorial_steps"` |
| `setting` | Where it's filmed | `"salon"`, `"home"`, `"outdoor"` |
| `duration` | Length in seconds | `30`, `45`, `60`, `90` |
| `platform` | Target platform | `"instagram"`, `"tiktok"`, `"youtube"` |
| `booking_cta` | Add booking call-to-action | `true` |

## Workflow

1. Describe the service, tools used, and transformation arc
2. NemoVideo builds the before-during-after sequence
3. Tool callouts and technique labels added automatically
4. Export with optional booking CTA overlay for salon content

## API Usage

### Salon Transformation Video

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "hairstyle-video-maker",
    "input": {
      "prompt": "Client transformation: frizzy damaged hair → silky straight after keratin treatment. Show application, processing, blow-dry with round brush, flat iron seal. Before-after side by side reveal.",
      "service_type": "keratin_treatment",
      "technique_tools": ["round_brush", "flat_iron"],
      "transformation_arc": "before_after",
      "setting": "salon",
      "duration": 45,
      "platform": "instagram",
      "booking_cta": true,
      "hashtags": ["HairTransformation", "KératineTreatment", "SalonLife", "HairMakeover"]
    }
  }'
```

**Response:**
```json
{
  "job_id": "hair_jkl012",
  "status": "processing",
  "estimated_seconds": 110,
  "poll_url": "https://mega-api-prod.nemovideo.ai/v1/jobs/hair_jkl012"
}
```

### Blowout Tutorial with Thinning Shears Finish

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "hairstyle-video-maker",
    "input": {
      "prompt": "Professional blowout tutorial: section hair into 4 parts, apply heat protectant, rough dry 80%, then section-by-section blowout with round brush for volume and shine. Finish with thinning shears on ends for movement and lightness. Home-achievable technique.",
      "service_type": "blowout",
      "technique_tools": ["thinning_shears", "round_brush"],
      "transformation_arc": "tutorial_steps",
      "setting": "salon",
      "duration": 60,
      "platform": "youtube",
      "voiceover": true,
      "show_product_names": true
    }
  }'
```

## Tips for Best Results

- **Before shot matters**: A clear "before" (frizzy, flat, damaged) makes the transformation more impactful
- **Name the technique**: "blowout with round brush" and "thinning shears for movement" get better results than "styled hair"
- **Salon context adds trust**: Setting (`salon`) signals professional quality to viewers considering booking
- **Include the service name**: "keratin treatment" or "Brazilian blowout" — specific service names drive booking-intent viewers
- **Add CTA for stylists**: `booking_cta: true` adds a "Book Now" or "DM to book" overlay at the end

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| Instagram | 1080×1920 | 30–90s |
| TikTok | 1080×1920 | 30–60s |
| YouTube | 1920×1080 | 60–300s |

## Related Skills

- `skincare-video-maker` — Pair with hair content for full beauty routines
- `makeup-tutorial-video` — Complete the transformation look
- `tiktok-content-maker` — General TikTok video creation
- `product-photography-enhance` — Improve product shots for hair care flat lays

## Common Questions

**Can stylists use this to attract salon clients?**
Yes — the `booking_cta` parameter adds a call-to-action overlay. Describe the transformation and the salon name for a ready-to-post client acquisition video.

**Does it show the thinning shears technique clearly?**
Include "thinning shears at ends for movement" in your prompt and set `technique_tools: ["thinning_shears"]` — the video will label the tool and show the technique moment.

**How do I show before-after effectively?**
Set `transformation_arc: "before_after"` and describe the starting state clearly ("frizzy, heat-damaged, flat") — the contrast drives the reveal moment.

**Can I create content for multiple clients in one batch?**
Yes — describe each transformation in separate API calls. NemoVideo processes them in parallel for stylists building a portfolio of transformation content.
