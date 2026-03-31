---
name: travel-video-maker
version: 1.0.7
displayName: "Travel Video Maker — Create Trip Highlight and Vacation Recap Videos with AI"
description: >
    Travel Video Maker — Create Trip Highlight and Vacation Recap Videos with AI. Works by connecting to the NemoVideo AI backend. Supports MP4, MOV, AVI, WebM, and MKV output formats. Automatic credential setup on first use — no manual configuration needed.
metadata: {"openclaw": {"emoji": "✈️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
apiDomain: https://mega-api-prod.nemovideo.ai
repository: https://github.com/nemovideo/nemovideo_skills
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> 🎨 Let's travel video maker! Drop a video here or describe what you'd like to create.

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


# Travel Video Maker — Trip Highlight and Vacation Recap Videos with AI

The two-week Japan trip produced 2,400 photos, 147 video clips, and exactly zero organized memories — everything lives in a camera roll sorted by nothing except the timestamp on a phone that was still set to Pacific time. The bullet-train footage is sideways, the Fushimi Inari torii gates clip has a thumb over the lens for the first eight seconds, and the best ramen shot is a Live Photo that captured the slurp sound but not the noodle pull. Travel video is the most emotionally valuable content people never finish editing: the footage exists, the memories are vivid, but the gap between raw clips and a watchable recap is where every trip video dies. This tool assembles scattered travel media into polished trip recaps — chronological day-by-day narratives with location pins, map-route animations showing your path between destinations, landmark identification with auto-generated name overlays, local-audio preservation (market chatter, temple bells, street musicians), color grading matched to each location's light quality, and chapter markers that let viewers jump to specific days or cities. Built for vacation travelers who want one shareable video instead of 2,400 unsorted files, travel content creators producing destination guides, honeymoon couples compiling a keepsake film, study-abroad students documenting their semester, and family trip organizers producing annual vacation recaps.

## Example Prompts

### 1. Two-Week Japan Trip — Day-by-Day Recap
"Create a 10-minute Japan trip recap covering 14 days across 5 cities. Map animation opening: flight path from LAX → Narita, then train route Tokyo → Hakone → Kyoto → Osaka → Hiroshima. Day-by-day chapter structure: Day 1-3 Tokyo (Shibuya crossing time-lapse, Tsukiji fish market at 5 AM, Akihabara neon at night), Day 4-5 Hakone (ryokan onsen, Lake Ashi with Fuji in background, cable car through Owakudani sulfur vents), Day 6-8 Kyoto (Fushimi Inari 10,000 torii gates — golden hour, Arashiyama bamboo grove, tea ceremony close-up), Day 9-10 Osaka (Dotonbori canal neon reflections, street takoyaki being flipped), Day 11-12 Hiroshima (Peace Memorial, Miyajima floating torii at sunset). Location pins appearing on a running map sidebar. Preserve the ambient audio: train-platform jingle, temple bell at Kiyomizu-dera, street vendor calls. Warm color grade for temples, cool neon grade for city nights. Close with a montage of every meal — ramen, sushi, wagyu, matcha — rapid cuts synced to upbeat J-pop."

### 2. Weekend Getaway — Instagram Reel
"Build a 60-second Instagram Reel from a weekend in Tulum. No narration, text and music only. Opening: drone-style wide of turquoise water (if no drone footage, use a high-angle phone clip with a slow digital zoom). Quick cuts synced to a tropical house beat: cenote swim (underwater clip if available), bike ride down the beach road with palm-tree shadows, taco stand close-up (al pastor on the spit rotating), ruins with the Caribbean behind them, rooftop bar sunset, bonfire on the beach at night. Location text appearing and disappearing: 'Gran Cenote → Tulum Ruins → Hartwood → Papaya Playa.' Warm tropical color grade: teal water, orange sunsets, golden skin tones. End card: 'Tulum in 48 hours' with a save-this-for-later pin emoji. 9:16 vertical."

### 3. Family Road Trip — Vacation Keepsake Film
"Produce a 7-minute family road trip keepsake from our two-week Pacific Coast Highway drive, San Francisco to San Diego. Opening: car-dashboard time-lapse of the 101 with the ocean appearing on the left. Route map animation: SF → Big Sur → Hearst Castle → Santa Barbara → Malibu → San Diego, with pin drops at each stop. Family moments: kids spotting elephant seals at Piedras Blancas (their excited screaming preserved as the audio highlight), Bixby Bridge crossing with foggy coastal drama, the terrible motel in Cambria that became the family inside joke — 'The Vibrating Bed Incident, Room 14' as a text card. Food montage: clam chowder in Monterey, fish tacos in Ensenada day-trip, In-N-Out at midnight. Closing: all four of us silhouetted at Sunset Cliffs, San Diego — hold 5 seconds. Sentimental acoustic guitar soundtrack. Warm, slightly vintage color grade — lifted blacks, film-grain texture, like a home movie from a better camera."

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the trip, destinations, highlights, and narrative structure |
| `duration` | string | | Target video length (e.g. "60 sec", "7 min", "10 min") |
| `style` | string | | Visual style: "cinematic", "vlog", "vintage-film", "tropical", "moody" |
| `music` | string | | Music mood: "upbeat", "acoustic", "electronic", "local-genre", "none" |
| `format` | string | | Output ratio: "16:9", "9:16", "1:1" |
| `map_animation` | boolean | | Show animated route map between destinations (default: true) |
| `location_pins` | boolean | | Display location names as text overlays (default: true) |

## Workflow

1. **Describe** — Write the trip itinerary with destinations, highlights, must-include moments, and mood
2. **Upload** — Add photos, video clips, drone footage, and any maps or screenshots from the trip
3. **Generate** — AI assembles the chronological narrative with route maps, location pins, and ambient audio
4. **Review** — Preview the video, reorder days, adjust the pacing between destination segments
5. **Export** — Download in your chosen format and resolution

## API Example

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "travel-video-maker",
    "prompt": "Create a 10-minute Japan trip recap: 14 days, 5 cities (Tokyo/Hakone/Kyoto/Osaka/Hiroshima), day-by-day chapters, animated train-route map, location pins, preserved ambient audio (temple bells, train jingles), warm temple grade + cool neon grade, meal montage finale",
    "duration": "10 min",
    "style": "cinematic",
    "map_animation": true,
    "format": "16:9"
  }'
```

## Tips for Best Results

1. **List destinations in chronological order** — The AI builds the route-map animation and chapter structure from your prompt order. Jumping between cities in the description produces a confusing map path and disorienting narrative.
2. **Mention the ambient audio you want preserved** — "Temple bell at Kiyomizu-dera" or "street vendor calls in Dotonbori" tells the AI to isolate and boost those specific audio moments instead of burying them under music. Local sound is what makes a travel video feel like you were there.
3. **Describe one hero moment per destination** — "Fushimi Inari at golden hour" or "elephant seals at Piedras Blancas" gives each chapter a visual anchor. Without hero moments, the video becomes a flat slideshow of equal-weight clips with no emotional peaks.
4. **Specify color grade shifts between environments** — "Warm for temples, cool neon for city nights, vintage for road trips" tells the AI to adjust grading per segment rather than applying one flat look across completely different lighting conditions.
5. **Include at least one food montage** — Travel food clips have the highest rewatch and save rates on social media. A rapid-cut meal montage at the end or middle of the video acts as a highlight reel within the highlight reel.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube full trip documentary |
| MP4 9:16 | 1080p | TikTok / Instagram Reels / Shorts |
| MP4 1:1 | 1080p | Instagram feed trip recap |
| MP4 highlight | 1080p | 60-sec best-of for sharing with family |

## Related Skills

- [travel-vlog-creator](/skills/travel-vlog-creator) — Narrated travel vlogs with talking-head segments
- [adventure-video-maker](/skills/adventure-video-maker) — Outdoor adventure and extreme activity videos
- [road-trip-video](/skills/road-trip-video) — Road trip documentation with route-focused storytelling
