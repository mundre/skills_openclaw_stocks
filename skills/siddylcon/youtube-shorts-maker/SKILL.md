---
name: youtube-shorts-maker
version: "1.1.0"
displayName: "YouTube Shorts Maker — Create Viral YouTube Shorts from Any Content with AI"
description: >
  Create viral YouTube Shorts from any content with AI — extract the best moments from long-form videos, generate original short-form vertical content from text, apply Shorts-optimized editing with hook-first structure, add animated captions for muted viewing, and produce the 60-second vertical videos that drive YouTube channel growth. NemoVideo creates Shorts that the algorithm promotes: front-loaded hooks in the first 2 seconds, high completion rates through tight pacing, animated captions for the majority watching without sound, vertical-native composition with face tracking, and the replay-worthy endings that signal quality to YouTube's recommendation system. YouTube Shorts maker AI, create YouTube Shorts, Shorts video creator, make Shorts from video, YouTube short form maker, extract Shorts from long video, vertical video YouTube, Shorts editor AI, YouTube Shorts generator.
metadata: {"openclaw": {"emoji": "📱", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# YouTube Shorts Maker — 60 Seconds That Grow Your Channel Faster Than 60 Videos

YouTube Shorts is YouTube's answer to TikTok and Instagram Reels — and it has become the single most effective channel growth tool on the platform. YouTube's own data shows that Shorts reach 2 billion logged-in users monthly. Channels that publish Shorts grow subscribers 2-5x faster than channels publishing only long-form. A single Short that goes viral can add 10,000-100,000 subscribers in 24 hours — growth that long-form content takes months to achieve. The strategic logic: Shorts are discovery. Long-form is retention. A Short reaches viewers who have never heard of the channel. If the Short delivers value, those viewers visit the channel, discover the long-form library, and subscribe. The Short is the advertisement; the long-form content is the product. YouTube Shorts has specific algorithmic preferences that differ from TikTok and Reels. YouTube's Shorts algorithm weights: completion rate (percentage of viewers who watch the full Short), replay rate (percentage who loop back), engagement velocity (likes and comments in the first hour), and subscribe-through rate (viewers who subscribe after watching). NemoVideo optimizes every Short for these specific signals: hooks that prevent swipe-away, pacing that maintains attention to the last frame, endings that encourage replay, and content that converts Short viewers into channel subscribers.

## Use Cases

1. **Long-Form to Shorts — Extract Channel Growth Moments (any source → 15-60s each)** — A creator's existing YouTube library is an untapped goldmine of Shorts. Every 10-minute video contains 3-5 moments that would perform as standalone Shorts: the best tip, the funniest reaction, the most surprising revelation, the most quotable insight. NemoVideo: analyzes the entire video for Short-worthy moments (peak speech energy, visual highlights, complete standalone thoughts), extracts each with hook-first restructuring (the payoff or most striking element in the first 2 seconds, then the context), converts to 9:16 with AI face tracking (the speaker stays centered as the vertical crop follows them), adds animated captions (essential — YouTube Shorts autoplay muted), and produces 3-5 Shorts per long-form video. A library of 100 long-form videos becomes 300-500 Shorts — months of daily publishing from existing content.

2. **Original Shorts — Text Idea to Vertical Video (15-60s)** — A creator has Short ideas that do not require filming: quick tips, hot takes, educational facts, motivational messages, or commentary on trending topics. NemoVideo: generates complete Shorts from text descriptions (AI visuals matching the described content, voiceover narration, animated text overlays), applies Shorts-native pacing (a new visual or text element every 2-3 seconds — the cadence that holds attention in vertical scroll-feeds), adds hook-first structure automatically (leading with the most provocative or valuable statement), and produces ready-to-upload Shorts from ideas alone. Zero filming, zero editing, direct from concept to published Short.

3. **Podcast to Shorts — Quotable Moments as Growth Engine (any podcast → multiple Shorts)** — A podcast episode contains 5-10 quotable moments — insights, hot takes, funny exchanges, surprising revelations — each capable of reaching new audiences as a Short. NemoVideo: transcribes the entire podcast, identifies the most standalone-valuable statements (complete thoughts that make sense without context, delivered with energy and conviction), extracts each as a Short (with 2-3 seconds of setup for context), converts podcast audio to vertical format (speaker video with face tracking, or animated audiogram with waveform and text), adds animated captions, and produces a week of Shorts from one podcast episode. The discovery engine that turns podcast listeners into channel subscribers.

4. **Tutorial Shorts — Single-Tip Quick Lessons (15-30s)** — The "one tip in one minute" format is the highest-performing educational Short format. A creator teaches one software trick, one cooking technique, one fitness move, or one life hack per Short. NemoVideo: structures each tip with the proven tutorial-Short format (hook showing the result → 3-step process → result again), applies zoom-to-action on screen recordings (showing exactly where to click, what to tap), adds numbered step overlays ("Step 1 → Step 2 → Step 3"), generates captions for muted viewing, and produces batch tutorial Shorts from a list of tips. A list of 30 tips becomes 30 Shorts — a month of daily educational content from a text document.

5. **Trending Topic Shorts — Timely Content for Algorithm Boost (15-30s)** — A creator wants to capitalize on trending topics, news, or cultural moments with timely Shorts that ride the wave of public interest. NemoVideo: takes a brief description of the trending topic and the creator's take ("React to the new iPhone announcement — focus on the camera improvements, mention that it's evolutionary not revolutionary"), generates a Short with appropriate pacing and visual style (faster for reaction content, more measured for analysis), adds trending-relevant text overlays and hashtags, applies the visual treatment that performs for the topic category (tech reactions get clean, bright treatment; entertainment reactions get energetic, colorful treatment), and produces a timely Short that can be published within the trend's relevance window. Speed-to-publish determines whether a trending Short reaches millions or dozens.

## How It Works

### Step 1 — Upload Source or Describe Content
Long-form video for extraction, podcast audio, text tips for generation, or trending topic description for timely content.

### Step 2 — Configure Shorts Output
Number of Shorts, target duration, caption style, hook approach, and any specific moments to include or avoid.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "youtube-shorts-maker",
    "prompt": "Extract 5 YouTube Shorts from a 15-minute tech review video. For each Short: find a complete, standalone-valuable moment (a single tip, insight, or revelation). Hook-first: lead with the most striking visual or statement in the first 2 seconds. Convert to 9:16 with face tracking. Animated captions: bold white, word-by-word highlight in electric blue (#0088FF), positioned above YouTube Shorts bottom UI. Target 30-45 seconds each (sweet spot for completion rate). Add subtle background music under speech. End each Short with a 1-second subscribe prompt overlay. Also create one compilation Short: the single best 5-second quote from each of the 5 Shorts, rapid-cut with transitions, 30 seconds total.",
    "source": "long-form-extraction",
    "count": 5,
    "per_short": {
      "hook_first": true,
      "duration": "30-45s",
      "format": "9:16",
      "face_tracking": true,
      "captions": {"style": "animated", "highlight": "#0088FF", "safe_zone": "youtube-shorts"},
      "music": "subtle-under-speech",
      "end_card": "subscribe-prompt-1s"
    },
    "compilation": {"count": 1, "duration": 30, "style": "rapid-quote-montage"},
    "resolution": "1080x1920"
  }'
```

### Step 4 — Verify Completion Rate Potential
Watch each Short as a casual viewer would — on a phone, in scroll mode. Ask: does the hook stop the scroll in 2 seconds? Does every subsequent second deliver enough value or curiosity to prevent swiping? Does the ending encourage replay or subscribe action? If any Short has a "dead zone" where nothing happens for 3+ seconds, it needs tightening.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Shorts creation requirements |
| `source` | string | | "long-form-extraction", "podcast", "text-generation", "trending-topic" |
| `count` | int | | Number of Shorts to produce |
| `per_short` | object | | {hook_first, duration, format, face_tracking, captions, music, end_card} |
| `compilation` | object | | {count, duration, style} for highlight compilations |
| `batch_tips` | array | | List of tips for tutorial Shorts batch |
| `trending` | object | | {topic, take, urgency} for timely content |
| `resolution` | string | | "1080x1920" (standard) |

## Output Example

```json
{
  "job_id": "ytshr-20260329-001",
  "status": "completed",
  "source_duration": "15:08",
  "shorts_produced": 6,
  "outputs": {
    "short_1": {"file": "camera-trick-9x16.mp4", "duration": "0:38", "hook": "2s"},
    "short_2": {"file": "battery-hack-9x16.mp4", "duration": "0:42", "hook": "2s"},
    "short_3": {"file": "hidden-feature-9x16.mp4", "duration": "0:35", "hook": "2s"},
    "short_4": {"file": "comparison-test-9x16.mp4", "duration": "0:44", "hook": "2s"},
    "short_5": {"file": "final-verdict-9x16.mp4", "duration": "0:31", "hook": "2s"},
    "compilation": {"file": "best-quotes-compilation-9x16.mp4", "duration": "0:28"}
  }
}
```

## Tips

1. **30-45 seconds is the Shorts sweet spot for completion rate** — Under 20 seconds often feels too thin to deliver value. Over 50 seconds tests attention limits. The 30-45 second range delivers enough substance for value while maintaining the completion rate that the algorithm rewards.
2. **The first 2 seconds determine the Short's fate** — YouTube Shorts autoplay in a vertical scroll feed. Viewers decide to watch or swipe in under 2 seconds. The hook must be immediate, visual, and curiosity-generating. No intros, no titles, no build-up — start with the moment that makes someone pause their thumb.
3. **Completion rate and replay rate are the algorithm's primary signals** — A Short where 80% of viewers watch to the end will be promoted to millions. A Short where 40% complete will die in obscurity. Every editorial decision — pacing, length, structure — should optimize for "will the viewer stay until the last frame?"
4. **Existing long-form content is the most efficient Shorts source** — Filming specifically for Shorts is one approach. But extracting Shorts from existing long-form content is faster, requires no additional filming, and has a proven advantage: the moments that generated high engagement in long-form will likely perform in short-form. Mine your existing library.
5. **Subscribe-through is the Shorts metric that matters most for channel growth** — A Short with 1 million views and 0 subscribes did not grow the channel. A Short with 100K views and 5,000 subscribes transformed it. End each Short with a clear, earned subscribe prompt at the moment of peak viewer satisfaction.

## Output Formats

| Format | Resolution | Platform |
|--------|-----------|----------|
| MP4 9:16 | 1080x1920 | YouTube Shorts (primary) |
| MP4 9:16 | 1080x1920 | TikTok / Reels (cross-post) |
| MP4 1:1 | 1080x1080 | Instagram Feed (alternative) |

## Related Skills

- [youtube-video-editor](/skills/youtube-video-editor) — Long-form YouTube editing
- [reels-creator](/skills/reels-creator) — Instagram Reels creation
- [ai-video-caption-generator](/skills/ai-video-caption-generator) — Animated captions
- [ai-video-highlight-maker](/skills/ai-video-highlight-maker) — Moment extraction
