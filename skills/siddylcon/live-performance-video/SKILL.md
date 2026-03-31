---
name: live-performance-video
version: 1.0.3
displayName: "Live Performance Video Maker"
description: >
  Describe your performance and NemoVideo creates the video. Theater shows, comedy nights, dance recitals, spoken word events, improv performances — narrate the show, the space, the moment that made it, and what the audience experienced, and get a performance video that documents your work for portfolio, promotion, and archiving.

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

> 🚀 Ready to live performance video! Just send me a video or describe your project.

**Try saying:**
- "edit my video"
- "help me create a short video"
- "add effects to this clip"

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


# Live Performance Video Maker — Create Stage and Venue Performance Documentation

Describe your performance and NemoVideo creates the video. Theater shows, comedy nights, dance recitals, spoken word events, improv performances — narrate the show, the space, the moment that made it, and what the audience experienced, and get a performance video that documents your work for portfolio, promotion, and archiving.

## When to Use This Skill

Use this skill for live performance documentation across all performing arts:
- Create theater production highlight and full-show documentation videos
- Film dance company and choreography documentation for portfolio and auditions
- Build comedy club performance videos for comedian press kits
- Document spoken word and poetry slam performance content
- Create improv and sketch comedy show highlight reels
- Produce circus, variety, and specialty performance documentation

## How to Describe Your Performance

Be specific about the art form, the venue, the piece performed, and the moments that define the show.

**Examples of good prompts:**
- "Contemporary dance piece 'Groundwater' by the Meridian Dance Company: 22 minutes, 5 dancers, exploring themes of environmental erasure. The piece uses water on the stage floor (actual water, 2 inches deep, the dancers work in it the whole time). Key moments: the opening where a single dancer enters before the lights are up (silhouette in black water), the central quintet where all five dancers move in synchronized slowness for 8 minutes, and the ending where they collectively push the water to the walls and stand on dry floor. For company portfolio and festival submissions."
- "Stand-up comedy set at a 150-cap room: 25-minute set, third night of a 5-night run. The comedian is Priya Nair, observational comedy about growing up between two cultures. The room was sold out, laughs came hard. Best moment: the bit about her grandmother learning to use an iPhone that went 4 minutes over expected because of the crowd response. Single camera, nothing fancy, for her press kit."
- "Shakespeare in the park: A Midsummer Night's Dream, outdoor stage, summer evening. 90 audience members in folding chairs, fairy lights strung through actual trees, the set is minimal (two benches and a lot of imagination). Show the magic of outdoor Shakespeare — the fireflies that showed up during Act 3, the kid in the front row who was completely lost in it, the Puck who played the whole thing like stand-up comedy."

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `performance_type` | Art form | `"theater"`, `"dance"`, `"comedy"`, `"spoken_word"`, `"improv"`, `"circus"` |
| `show_title` | Performance name | `"Groundwater"`, `"A Midsummer Night's Dream"` |
| `performer_name` | Artist or company | `"Meridian Dance Company"`, `"Priya Nair"` |
| `venue_type` | Performance space | `"black_box"`, `"outdoor"`, `"comedy_club"`, `"proscenium"` |
| `key_moments` | Highlight sequences | `["opening silhouette", "water quintet", "crowd response bit"]` |
| `show_audience` | Include audience reactions | `true` |
| `purpose` | How video will be used | `"portfolio"`, `"press_kit"`, `"social_media"`, `"archive"` |
| `tone` | Documentary approach | `"artistic"`, `"documentary"`, `"promotional"`, `"intimate"` |
| `duration_minutes` | Video length | `3`, `5`, `8`, `15` |
| `platform` | Distribution | `"vimeo"`, `"youtube"`, `"instagram"`, `"portfolio_site"` |

## Workflow

1. Describe the performance, venue, key moments, and intended use of the video
2. NemoVideo structures the documentation with appropriate framing for the art form
3. Show title, company/performer name, venue, and date overlaid automatically
4. Export in formats suited for portfolio, booking, and press use

## API Usage

### Dance Company Portfolio Video

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "live-performance-video",
    "input": {
      "prompt": "Contemporary dance documentation for festival application: piece titled 'Thresholds', 18 minutes, 3 dancers. The piece deals with the moment before a decision — every movement is either arriving or leaving, nothing in the middle. Key moments: the opening trio (all three dancers mirroring in canon), the central duet where two dancers catch and release in 6-minute improvised score, the ending where each dancer walks off stage in a different direction and the stage lights die one by one. The company needs this for Edinburgh Fringe application. Filmed at the company's residency black box, quality documentation not promo hype.",
      "performance_type": "dance",
      "show_title": "Thresholds",
      "performer_name": "Kinetic Meridian Dance Company",
      "venue_type": "black_box",
      "key_moments": ["opening trio canon", "central duet score", "individual exits"],
      "show_audience": false,
      "purpose": "portfolio",
      "tone": "artistic",
      "duration_minutes": 8,
      "platform": "vimeo",
      "hashtags": ["ContemporaryDance", "DanceVideo", "LivePerformance", "FestivalApplication"]
    }
  }'
```

**Response:**
```json
{
  "job_id": "performance_mno345",
  "status": "processing",
  "estimated_seconds": 115,
  "poll_url": "https://mega-api-prod.nemovideo.ai/v1/jobs/performance_mno345"
}
```

### Comedy Press Kit Video

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "live-performance-video",
    "input": {
      "prompt": "Stand-up comedy press kit video for Priya Nair: best 5 minutes from her recent 25-minute set. The bit about her grandmother and the iPhone is the centrepiece — 3 minutes of consecutive laughs, the crowd was completely with her. Also include the opening bit (quick laughs to establish her voice) and the button before intermission. 150-cap sold-out room, authentic laughs, real audience visible. For comedy club bookers and TV submissions.",
      "performance_type": "comedy",
      "performer_name": "Priya Nair",
      "venue_type": "comedy_club",
      "show_audience": true,
      "purpose": "press_kit",
      "tone": "promotional",
      "duration_minutes": 5,
      "platform": "youtube"
    }
  }'
```

## Tips for Best Results

- **Purpose shapes everything**: Portfolio for festival applications is different from social media clips — set `purpose` explicitly so the pacing, length, and framing are appropriate
- **The key moment is the portfolio's center**: One extraordinary moment (the water stage, the 4-minute crowd response bit, the fireflies in Act 3) is what makes the documentation memorable — describe it specifically
- **Audience reactions signal the art's impact**: Set `show_audience: true` for comedy and theater where the audience response IS the documentation — a silent audience shot during a standing ovation says what words can't
- **Art form dictates camera style**: Dance documentation is wide-shot with technique visible; comedy is tight on face and crowd; theater is scene-by-scene storytelling
- **Portfolio and promo are different products**: Portfolio for bookers should be uncut and representative; promo for social should be the peak 60 seconds — make both

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| Vimeo (portfolio) | 1920×1080 | 5–20 min |
| YouTube | 1920×1080 | 3–15 min |
| Instagram Reels | 1080×1920 | 60–90s |
| Press kit | 1920×1080 | 3–5 min |

## Related Skills

- `concert-video-maker` — Music-specific live performance
- `band-promo-video` — Musical artist promotional content
- `cover-song-video` — Performance content for covers
- `dance-performance-video` — Dedicated choreography documentation

## Common Questions

**What's the right video length for a festival application?**
3-8 minutes for most performing arts festivals. Edinburgh Fringe, for example, wants to see the work clearly — long enough to understand it, short enough to stay focused. Set `purpose: "portfolio"` and `duration_minutes: 5-8`.

**Should dance documentation show the full piece or highlights?**
For portfolio submissions, show key sections that represent the full aesthetic. For social media, take the most visually compelling 60-90 seconds. Describe both if you need both formats.

**Can I document multiple shows in one video?**
Yes — describe the shows in sequence and set `content_type: "highlight_reel"`. Useful for company annual reels or comedian year-in-review content.
