---
name: documentary-video-maker
version: 1.2.3
displayName: "Documentary Video Maker — Create Professional Documentaries and Docu-Style Content"
description: >
  Create professional documentaries and docu-style content with AI — produce complete documentary projects from raw interview footage, archival material, B-roll, and narration scripts. NemoVideo handles every stage of documentary production: structure multi-source interviews into coherent narrative arcs, weave different speaker perspectives by theme, layer B-roll over talking-head segments to maintain visual variety, apply Ken Burns motion to archival photos and documents, generate cinematic AI narration with NPR-quality voiceover, score with mood-adaptive music that follows the emotional arc, create title sequences and chapter transitions, add speaker identification lower thirds, color grade for cinematic depth, and export broadcast-ready documentary content for YouTube festivals streaming platforms and corporate distribution. Documentary maker AI, interview documentary creator, brand story video, historical documentary maker, event documentary, docu-style video AI, narrative film maker, investigative documentary tool, oral history video creator.
metadata: {"openclaw": {"emoji": "🎥", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
apiDomain: https://mega-api-prod.nemovideo.ai
---

# Documentary Video Maker — Real Stories. Cinematic Production. From Any Source Material.

Documentary is storytelling that changes minds. A 10-minute brand documentary creates deeper trust than a year of advertising. A 30-minute oral history preserves voices that would otherwise be lost. A 60-minute investigative piece can shift public opinion and policy. The documentary format commands sustained attention and emotional investment because viewers understand that what they are watching is real — real people, real events, real consequences. This authenticity creates an engagement depth that fiction and advertising cannot replicate. The production barrier is what keeps most documentary projects as ideas rather than finished films. A documentary requires: multiple interviews (planning, scheduling, recording, transcribing), narrative structure (finding the story within hours of raw material), B-roll acquisition (footage that visually illustrates what interview subjects describe), archival research (photos, documents, footage that provides historical context), narration writing and recording (the connective tissue between interview segments), music scoring (the emotional layer that guides the viewer's feelings), and post-production assembly (the most time-intensive stage: weaving all elements into a coherent film). Professional documentary production costs $10,000-150,000+ depending on length and scope. Even a modest 15-minute documentary requires 40-100 hours of post-production at $50-150/hour. NemoVideo transforms raw documentary materials — interviews, photos, B-roll, narration — into structured, scored, polished documentary content. The AI understands narrative architecture: it identifies thematic connections across interviews, structures revelations for maximum impact, and assembles the visual and audio layers that give documentary its power.

## Use Cases

1. **Brand Origin Documentary — The Founding Story (8-20 min)** — Every company has an origin story worth telling. The problem the founders identified, the garage/dorm room/kitchen table where it started, the early failures that nearly ended everything, the breakthrough that changed the trajectory, and the vision that drives the future. NemoVideo: takes founder and early employee interviews (phone recordings, Zoom calls, any quality), identifies the narrative beats within each interview (problem recognition, early struggle, pivot moment, growth acceleration, future vision), weaves multiple interviews by theme (not by person — cutting between speakers who describe different facets of the same moment), layers archival photos with Ken Burns motion (early office photos, first product prototypes, team photos from each era), adds AI narration bridges that connect interview segments ("What the founders didn't know was that 3,000 miles away, the same frustration was sparking a very different solution..."), scores with a music arc that mirrors the emotional journey (contemplative opening, tension through struggles, triumphant at the breakthrough, inspiring at the vision), and produces a documentary that makes investors, recruits, and customers feel the company's humanity behind the product.

2. **Oral History Project — Preserving Voices and Stories (15-60 min)** — A family oral history, community archive, veteran interview project, or cultural preservation effort where recorded interviews are the primary source material. NemoVideo: treats each interview with archival respect (enhancing audio clarity without altering the speaker's voice character), structures long interviews into thematic chapters (childhood, career, pivotal moments, reflections), intercuts archival materials that illustrate the stories being told (family photos appearing as a grandmother describes her wedding, newspaper clippings appearing as a veteran describes a battle), adds contextual overlays (dates, locations, historical events) that orient the viewer in time, generates narration that provides historical context without overshadowing the primary voices ("It was 1963. The world was about to change, and Margaret was standing at the center of it."), and produces a historical document that preserves not just facts but the emotional texture of lived experience.

3. **Event Documentary — Capturing What It Felt Like (15-45 min)** — A conference, festival, milestone celebration, or community event. Multiple cameras, multiple locations, dozens of attendee interviews, performances, keynotes, and ambient atmosphere footage. NemoVideo: organizes footage chronologically and by location, selects the strongest 8-15 seconds from each attendee interview (the moment of genuine enthusiasm, insight, or emotion), structures as an experiential narrative (arrival anticipation → event unfolding → peak moments → reflection and farewell), intercuts wide establishing shots (showing the scale and atmosphere) with intimate moments (individual reactions, backstage preparation, spontaneous conversations), layers the actual ambient audio from the event (applause, music, crowd energy) with a documentary music bed, and creates an event film that communicates the experience more powerfully than being there — because the documentary compresses the best of every moment into a continuous emotional journey.

4. **Investigative / Issue Documentary — Building an Argument (10-30 min)** — A nonprofit, journalist, or advocacy organization has interviews, data, and evidence that build a case: environmental impact, social justice issue, corporate accountability, public health concern. NemoVideo: structures the evidence as a progressive revelation (establishing the status quo → introducing the anomaly → building evidence → reaching the conclusion), intercuts expert interviews with affected person testimonials (credibility + emotion), visualizes data as animated infographics within the documentary (statistics becoming visible and visceral rather than abstract), adds archival footage and documents as evidence layers, uses narration to build the logical chain without editorializing (presenting facts and letting the viewer reach the conclusion), and scores with music that creates appropriate gravity without manipulation. Documentary as evidence-based storytelling.

5. **Mini-Doc Series — Episodic Documentary Content (5-10 min each)** — A brand, media company, or creator produces recurring documentary content: weekly mini-docs, monthly deep dives, or a multi-part series exploring a topic. NemoVideo: maintains visual and structural consistency across episodes (same title sequence, same lower-third design, same narration voice, same music bed style), adapts content to each episode's specific story while maintaining series identity, creates episode-specific elements (episode number, topic title, guest introductions), produces social teaser clips for each episode (30-60 second highlights for TikTok/Reels), and builds a documentary library that grows more valuable with each episode as viewers discover the series.

## How It Works

### Step 1 — Upload All Source Materials
Interviews (any format, any quality), archival photos and documents, B-roll footage, existing narration recordings, data/statistics, and any supplementary visual material. The more sources, the richer the documentary.

### Step 2 — Define Documentary Structure
Chronological, thematic, character-driven, issue-based, or experiential. Specify: target duration, narrative arc, and which voices/sources are primary vs. supporting.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "documentary-video-maker",
    "prompt": "Create a 15-minute brand origin documentary for a climate tech startup. Sources: 40-min founder interview (phone), 25-min CTO interview (Zoom), 20-min early investor interview (phone), 30 archival photos (2019-2025), 8 min current office and lab B-roll, company pitch deck slides. Structure: 5 chapters — (1) The Wake-Up Call: founder describes the climate data that changed everything (2 min, contemplative), (2) The Garage Days: early team building in a literal garage, failed prototypes, running out of money (3 min, tension), (3) The Breakthrough: the technology that worked, first successful test (3 min, rising triumph), (4) Scaling Up: growth from 3 to 200 people, first major contracts, impact metrics (4 min, confident energy), (5) What Comes Next: vision for the decade ahead (3 min, inspiring). Weave all three interviews by theme. Ken Burns on all photos. AI narration bridges between chapters — warm, authoritative, NPR documentary style. Music arc matching emotional trajectory. Cinematic color grade. Chapter title cards. Lower thirds for all speakers. Export 16:9 1080p + 60-second trailer.",
    "documentary_type": "brand-origin",
    "target_duration": "15:00",
    "chapters": [
      {"title": "The Wake-Up Call", "duration": "2:00", "mood": "contemplative"},
      {"title": "The Garage Days", "duration": "3:00", "mood": "tension-struggle"},
      {"title": "The Breakthrough", "duration": "3:00", "mood": "rising-triumph"},
      {"title": "Scaling Up", "duration": "4:00", "mood": "confident-energy"},
      {"title": "What Comes Next", "duration": "3:00", "mood": "inspiring"}
    ],
    "narration": {"generate": true, "voice": "warm-authoritative-npr"},
    "music": "emotional-arc-matched",
    "color_grade": "cinematic",
    "ken_burns": true,
    "lower_thirds": true,
    "formats": {"film": "16:9", "trailer": {"duration": 60}}
  }'
```

### Step 4 — Review Narrative Flow
Watch the complete documentary. Check: narrative builds logically, interview weaving feels natural (not jarring between speakers), narration bridges connect without over-explaining, music supports without overwhelming, archival photos appear at contextually relevant moments. Iterate on structure and re-render.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Documentary description and structure |
| `documentary_type` | string | | "brand-origin", "oral-history", "event", "investigative", "mini-doc-series" |
| `target_duration` | string | | Target total length |
| `chapters` | array | | [{title, duration, mood, primary_sources}] |
| `narration` | object | | {generate, voice, style, script} |
| `music` | string | | "emotional-arc-matched", "ambient-minimal", "cinematic" |
| `color_grade` | string | | "cinematic", "warm-nostalgic", "clean-modern", "atmospheric" |
| `ken_burns` | boolean | | Apply to archival photos |
| `lower_thirds` | boolean | | Speaker identification graphics |
| `data_viz` | array | | [{type, data, at}] animated statistics |
| `series` | object | | {name, episode, template} for episodic |
| `formats` | object | | {film, trailer, social_clips} |

## Output Example

```json
{
  "job_id": "docmk-20260329-002",
  "status": "completed",
  "documentary_type": "brand-origin",
  "total_duration": "15:22",
  "chapters": 5,
  "interviews_woven": 3,
  "archival_photos": 30,
  "narration_bridges": 6,
  "outputs": {
    "documentary": {"file": "climate-tech-origin-16x9.mp4", "resolution": "1920x1080"},
    "trailer": {"file": "climate-tech-trailer-60s.mp4", "duration": "0:58"}
  }
}
```

## Tips

1. **Weave interviews by theme, never by person** — Playing one person's complete interview, then the next person's complete interview, creates a lecture. Cutting between speakers discussing the same topic creates a conversation. The weaving of perspectives is what transforms interviews into documentary storytelling.
2. **Narration bridges are the invisible architecture of documentary** — Without narration, the documentary relies entirely on interview subjects to carry the narrative. Narration bridges create context ("It was 2021. The pandemic had changed everything."), build suspense ("What happened next would surprise everyone — including the founders."), and connect disparate interviews into a unified story.
3. **Music arc is the emotional spine** — Viewers are often unaware of documentary music, but it shapes their entire emotional experience. Contemplative music during the setup makes them reflective. Tension music during struggles makes them anxious. Triumphant music during the breakthrough makes them elated. The music teaches the viewer how to feel at every moment.
4. **Ken Burns motion is the difference between documentary and slideshow** — A static photo on screen is a slide. The same photo with slow zoom into a face, or gentle pan across a group, is cinema. The subtle motion creates visual engagement that holds attention and creates the illusion that the viewer is exploring the photo.
5. **B-roll over interview audio is the visual language of documentary** — Showing a talking head for more than 20-30 seconds becomes visually monotonous. Professional documentaries establish who is speaking (5-10 seconds of face), then cut to relevant B-roll while the voice continues. This visual variety sustains attention for documentary-length content.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / streaming / screening |
| MP4 9:16 | 1080x1920 | TikTok / Reels (trailer/clips) |
| MP4 1:1 | 1080x1080 | Instagram / LinkedIn |

## Related Skills

- [ai-video-highlight-maker](/skills/ai-video-highlight-maker) — Documentary highlight extraction
- [ai-video-caption-generator](/skills/ai-video-caption-generator) — Documentary captions
- [ai-video-text-overlay](/skills/ai-video-text-overlay) — Title cards and lower thirds
- [ai-video-intro-maker](/skills/ai-video-intro-maker) — Documentary title sequences
