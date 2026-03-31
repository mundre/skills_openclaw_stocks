---
name: minecraft-video-maker
version: 1.0.3
displayName: "Minecraft Video Maker"
description: >
  Describe your Minecraft project and NemoVideo creates the video. Survival world progress, mega builds, redstone contraptions, speedruns, hardcore deaths — narrate your world and get Minecraft content for YouTube and TikTok that speaks the language of 300 million active players.

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

> 🎵 Let's minecraft video maker! Drop a video here or describe what you'd like to create.

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


# Minecraft Video Maker — Create Survival, Build, and Adventure Content for Minecraft

Describe your Minecraft project and NemoVideo creates the video. Survival world progress, mega builds, redstone contraptions, speedruns, hardcore deaths — narrate your world and get Minecraft content for YouTube and TikTok that speaks the language of 300 million active players.

## When to Use This Skill

Use this skill for Minecraft content creation:
- Create survival world update videos showing progression over weeks or months
- Film mega build timelapse content with architectural commentary
- Build "how I built this" tutorial content for your redstone or building projects
- Document hardcore world survival milestones and near-death moments
- Create Minecraft challenge content (100 days, speedrun attempts, specific rules)
- Produce server tour and multiplayer adventure content

## How to Describe Your Minecraft Content

Be specific about the game mode, your project, the scale, and the most interesting moments.

**Examples of good prompts:**
- "Survival world year 1 recap: started in a plains biome with a really bad seed (spawned near a woodland mansion with no village nearby). Show the progression: dirt hut on Day 1, first stone house by Day 7, discovered a mineshaft under the house on Day 12, built my first iron farm at the mesa biome 3000 blocks away, ended year 1 with a 1:1 scale reproduction of Notre Dame Cathedral using the woodland mansion as a base. This took 4 months real time, I'm actually proud of it."
- "Hardcore mode death at Day 847: I survived 847 days, had a fully automated base, a beacon network, and a dragon egg trophy. Died because a creeper blew up my floor and I fell into the void while trying to fix it. The mundane death after surviving everything. Show the base I built, the void fall, the death screen."
- "Speedrun attempt breakdown: All Achievements run, current world record is 22:47. My personal best is 29:14. Break down the optimal route (nether route, stronghold find, End fight), show where I gain and lose time compared to the world record pace. Educational commentary."

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `content_type` | Video category | `"survival_update"`, `"build_timelapse"`, `"hardcore"`, `"tutorial"`, `"speedrun"`, `"100_days"` |
| `game_mode` | Minecraft mode | `"survival"`, `"hardcore"`, `"creative"`, `"adventure"` |
| `project_focus` | What's featured | `"Notre Dame Cathedral build"`, `"iron farm"`, `"speedrun route"` |
| `scale` | Project size | `"small"`, `"medium"`, `"mega"` |
| `show_coordinates` | XYZ overlay | `false` |
| `show_day_counter` | Day number overlay | `true` |
| `timelapse_ratio` | Build compression | `"10x"`, `"50x"`, `"100x"` |
| `tone` | Content vibe | `"documentary"`, `"tutorial"`, `"funny"`, `"emotional"` |
| `duration_minutes` | Video length | `5`, `8`, `12`, `20` |
| `platform` | Target platform | `"youtube"`, `"tiktok"`, `"instagram"` |

## Workflow

1. Describe your world, project, key moments, and what makes it worth watching
2. NemoVideo structures the Minecraft narrative with appropriate pacing for the content type
3. Day counter, inventory shots, build progress markers, and death screens added automatically
4. Export with Minecraft-appropriate music and pacing

## API Usage

### Survival World Update Video

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "minecraft-video-maker",
    "input": {
      "prompt": "Survival world update, Days 200-350: This update covers my underground city project. The concept: build a fully functional city 60 blocks underground in a natural cave system. Show the cave system discovery (enormous, multiple biomes inside), the urban planning phase (I spent 2 real hours just placing markers before building anything), the market district (8 villager shops, all trades optimized), the residential area (12 player houses each with different architectural styles), and the centerpiece: a underground tree that I grew in the cave using bone meal and artificial light. Day counter visible. Cinematic, no commentary, just the builds and the progress.",
      "content_type": "survival_update",
      "game_mode": "survival",
      "project_focus": "underground city in natural cave system",
      "scale": "mega",
      "show_day_counter": true,
      "timelapse_ratio": "50x",
      "tone": "documentary",
      "duration_minutes": 10,
      "platform": "youtube",
      "hashtags": ["Minecraft", "MinecraftBuilds", "SurvivalMinecraft", "MinecraftTutorial", "UndergroundCity"]
    }
  }'
```

**Response:**
```json
{
  "job_id": "minecraft_mno345",
  "status": "processing",
  "estimated_seconds": 120,
  "poll_url": "https://mega-api-prod.nemovideo.ai/v1/jobs/minecraft_mno345"
}
```

### Hardcore Death Video

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "minecraft-video-maker",
    "input": {
      "prompt": "Hardcore death video, Day 1,247: I died falling off my own nether highway because I misclicked a block I was placing. 1,247 days. Full netherite gear. Dragon egg on my shelf. Three beacons. Show the base in its final form (everything I built over 1,247 days), then the fatal moment in slow motion, then the death screen. The tone should match: this was a mundane death after surviving everything. End with the stats screen. No music during the death — just silence.",
      "content_type": "hardcore",
      "game_mode": "hardcore",
      "tone": "emotional",
      "show_day_counter": true,
      "duration_minutes": 8,
      "platform": "youtube"
    }
  }'
```

## Tips for Best Results

- **Day counter is essential for survival content**: Set `show_day_counter: true` — it provides the timeline that makes progress feel meaningful and gives viewers a reference for scale
- **Hardcore deaths have their own genre**: The more mundane the death after a long run, the more impact the content has — describe both the achievement (how long you survived, what you built) and the death (how routine it was)
- **Build timelapse needs ratio**: Specify `timelapse_ratio` — "50x" for a week-long build, "100x" for a month-long project — so viewers understand the real time investment
- **Minecraft builds need context**: "I built Notre Dame using the woodland mansion as a base" or "underground city in a natural cave" — the concept is what makes builds worth watching, not just the finished structure
- **The 100 Days format has its own structure**: Introduction (spawn and first 24 hours), midpoint (established base, first major challenge), and finale (what was accomplished by Day 100) — mention all three if using this format

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| YouTube | 1920×1080 | 8–30 min |
| TikTok | 1080×1920 | 60–180s |
| YouTube Shorts | 1080×1920 | up to 60s |
| Instagram Reels | 1080×1920 | 60–90s |

## Related Skills

- `gaming-highlight-video` — General gaming highlights
- `tutorial-video-creator` — Educational Minecraft technique content
- `adventure-video-maker` — Minecraft exploration and adventure content

## Common Questions

**Can I create 100 Days content with this skill?**
Yes — set `content_type: "100_days"` and describe your Day 1, key milestones, and Day 100 state. The 100 Days format has a specific narrative structure (survival setup → mid-game development → end-game achievement) that NemoVideo applies automatically.

**How do I show build timelapse?**
Set `content_type: "build_timelapse"` and `timelapse_ratio` to match how long the build took. Describe what you built, the building sequence, and the final result — NemoVideo compresses the footage with the day counter and build progress visible.

**Can I create Minecraft tutorial content?**
Set `content_type: "tutorial"` and describe the specific technique, farm design, or building method you're teaching. Tutorial content with narrated steps and overhead shots of the finished design performs well in the Minecraft community.
