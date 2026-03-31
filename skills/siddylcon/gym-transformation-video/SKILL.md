---
name: gym-transformation-video
version: 1.0.4
displayName: "Gym Transformation Video Maker"
description: >
  Describe your transformation and NemoVideo builds the video. Three-month weight loss, 6-month muscle gain, body recomposition — turn your before-after photos and progress data into an inspiring gym journey video that motivates and converts.

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

> ✂️ Ready to gym transformation video! Just send me a video or describe your project.

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
   curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

Let the user know briefly: "Setting things up… ready!" then proceed with their request.


# Gym Transformation Video Maker — Document Before-After Fitness Journey Content

Describe your transformation and NemoVideo builds the video. Three-month weight loss, 6-month muscle gain, body recomposition — turn your before-after photos and progress data into an inspiring gym journey video that motivates and converts.

## When to Use This Skill

Use this skill for fitness transformation content:
- Create before-after body transformation reveal videos
- Document weight loss journeys with weekly progress photos
- Show muscle-building timelines with measurement and strength gains
- Build motivational fitness content around a specific challenge or goal
- Create "what I did differently" breakdown videos after hitting a milestone
- Produce gym anniversary content (1 year of lifting, 100 days of running)

## How to Describe Your Transformation

Be specific about starting point, end point, timeline, and key changes.

**Examples of good prompts:**
- "12-week fat loss transformation: started at 195lb 28% body fat, finished at 172lb 19% — show before photo, weekly progress, final reveal, key changes (diet, training split). Motivational, not before-after shock value."
- "6-month beginner gains: went from 140lb skinny to 162lb — tracked bench from 95lb to 185lb, squat from 135lb to 225lb. Show the progress photos and strength numbers."
- "90-day body recomposition: same weight (155lb) but visible muscle definition gained, lost 3 inches off waist — show comparison photos, diet approach (high protein), training routine"

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `transformation_type` | Journey focus | `"fat_loss"`, `"muscle_gain"`, `"recomposition"`, `"strength"`, `"endurance"` |
| `timeline_weeks` | Duration of journey | `12`, `16`, `24`, `52` |
| `metrics` | Key numbers to show | `{"start_weight": 195, "end_weight": 172, "start_bf": 28, "end_bf": 19}` |
| `reveal_style` | Video structure | `"side_by_side"`, `"sequential"`, `"overlay"`, `"timeline_scroll"` |
| `include_stats` | Show numbers on screen | `true` |
| `tone` | Emotional framing | `"motivational"`, `"educational"`, `"personal"` |
| `platform` | Target platform | `"instagram"`, `"tiktok"`, `"youtube"` |

## Workflow

1. Describe your starting state, ending state, and timeline
2. NemoVideo structures the narrative arc (before → process → after)
3. Progress metrics, timeline markers, and key milestones overlaid automatically
4. Export with motivational framing tailored to your platform

## API Usage

### Fat Loss Transformation Reveal

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "gym-transformation-video",
    "input": {
      "prompt": "12-week transformation: 195lb to 172lb, lost 23lb and went from 28% to 19% body fat. Trained 4x/week (upper/lower split), tracked calories at 500 deficit. Show before photo, weekly progress montage, final reveal with side-by-side comparison.",
      "transformation_type": "fat_loss",
      "timeline_weeks": 12,
      "metrics": {"start_weight": 195, "end_weight": 172, "start_bf": 28, "end_bf": 19},
      "reveal_style": "side_by_side",
      "include_stats": true,
      "tone": "motivational",
      "platform": "instagram",
      "hashtags": ["TransformationTuesday", "FitnessJourney", "WeightLoss", "GymMotivation"]
    }
  }'
```

**Response:**
```json
{
  "job_id": "transform_def456",
  "status": "processing",
  "estimated_seconds": 100,
  "poll_url": "https://mega-api-prod.nemovideo.ai/v1/jobs/transform_def456"
}
```

### Muscle Building Progress Timeline

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "gym-transformation-video",
    "input": {
      "prompt": "6-month beginner muscle building: started at 140lb skinny fat, ended at 162lb with visible muscle. Bench went from 95lb to 185lb, squat from 135lb to 225lb. Show monthly progress photos with strength numbers overlaid. Educational tone — explain what worked (progressive overload, protein intake).",
      "transformation_type": "muscle_gain",
      "timeline_weeks": 24,
      "metrics": {"start_weight": 140, "end_weight": 162},
      "reveal_style": "timeline_scroll",
      "include_stats": true,
      "tone": "educational",
      "platform": "youtube",
      "voiceover": true
    }
  }'
```

## Tips for Best Results

- **Include real numbers**: "lost 23lb" beats "lost a lot of weight" — specific metrics make transformations credible
- **Describe the process too**: What you ate, how you trained — the method is as compelling as the result
- **Choose tone carefully**: "motivational" uses upbeat music and dramatic reveals; "educational" focuses on what worked and why
- **Timeline markers matter**: Monthly photo updates create better pacing than just before-after
- **Avoid shock value framing**: Frame around achievement, not appearance criticism

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| Instagram | 1080×1920 | 30–60s |
| TikTok | 1080×1920 | 30–90s |
| YouTube | 1920×1080 | 60–300s |

## Related Skills

- `workout-video-creator` — Document the training that drove the transformation
- `hiit-workout-video` — Show the specific workouts in your fat loss program
- `running-video-maker` — Endurance transformation content
- `tiktok-content-maker` — General short-form fitness content

## Common Questions

**Can I upload my own progress photos?**
Yes — pass image URLs in the `images` array. NemoVideo incorporates your actual before-after photos with consistent framing.

**How do I show strength gains alongside physique changes?**
Include lift numbers in the prompt and set `include_stats: true` — NemoVideo overlays your PR progression alongside the visual transformation.

**What's the difference between reveal_style options?**
`side_by_side` shows before and after simultaneously. `sequential` transitions from before to after. `timeline_scroll` shows monthly progression chronologically.
