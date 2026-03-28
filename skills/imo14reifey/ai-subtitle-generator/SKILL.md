---
name: ai-subtitle-generator
version: "1.0.0"
displayName: "AI Subtitle Generator — Auto Generate Subtitles and Captions for Any Video"
description: >
  Generate subtitles and captions for any video using AI — automatic speech recognition in 50+ languages, word-level timing, speaker identification, multiple caption styles, and export as burned-in video or standalone subtitle files. NemoVideo watches your video, transcribes every word with precise timing, and produces: word-by-word animated captions for social media, sentence-level subtitles for YouTube, speaker-labeled captions for interviews and podcasts, translated subtitles for multilingual reach, and styled burned-in captions that match your brand. Subtitle generator online, auto caption video, AI captions free, video subtitle maker, speech to text video, add subtitles to video automatically.
metadata: {"openclaw": {"emoji": "💬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# AI Subtitle Generator — Captions That Make Every Video Accessible and Engaging

Subtitles are no longer optional. On Facebook, 85% of video is watched without sound. On Instagram, 80%. On LinkedIn, 79%. On TikTok, even though sound is the default, 40% of users browse with sound off in public spaces. A video without captions loses the majority of its potential audience before the first word is heard. Beyond accessibility, captions measurably improve performance: videos with captions get 12% longer watch time on YouTube, 16% higher reach on Facebook, and 15% more shares across all platforms. The data is clear — captions are the single easiest improvement any creator can make to any video. The barrier has been production time. Manual captioning takes 5-10x the video length: a 10-minute video requires 50-100 minutes of transcription, timing, and formatting. Professional captioning services charge $1-3 per minute. Auto-generated captions from platforms (YouTube, TikTok) are 80-85% accurate — close enough to be dangerous, because viewers notice every error and associate caption mistakes with low production quality. NemoVideo generates captions with 98%+ accuracy using AI speech recognition trained on diverse accents, speaking styles, and audio conditions. Every word is timed to the millisecond, speakers are identified automatically, and captions are styled for the target platform — from minimal YouTube subtitles to bold animated TikTok captions.

## Use Cases

1. **YouTube Video — Clean Professional Subtitles (any length)** — A 15-minute tutorial needs subtitles for accessibility and SEO. NemoVideo generates: 98%+ accurate transcription, sentence-level timing (each caption holds for 2-4 seconds matching natural speech rhythm), proper punctuation and capitalization, speaker identification for multi-person content, chapter-aligned caption breaks (new caption line at topic transitions), and export as both SRT file (for YouTube's closed caption system) and burned-in version (white text, semi-transparent dark background). YouTube indexes subtitle text for search — proper captions improve discoverability for every word spoken in the video.
2. **TikTok/Reels — Word-by-Word Animated Captions (15-60s)** — A creator needs the trending caption style for a 45-second Reel. NemoVideo produces: word-by-word highlight animation (each word appears and highlights as spoken), large centered text (readable on mobile at arm's length), bold font with color accent on the active word (white text, yellow or green highlight), dark pill background for readability over any visual, and precise timing that matches the speaker's rhythm — not generic 0.5-second intervals. The caption style that TikTok and Reels audiences expect and that drives sound-off retention.
3. **Podcast/Interview — Speaker-Labeled Captions (30-90 min)** — A 60-minute two-person podcast needs captions that identify who is speaking. NemoVideo: detects two distinct speakers using voice analysis, labels each caption with the speaker's name ("Host:" / "Dr. Chen:"), assigns different colors per speaker (host in blue, guest in green), handles overlapping speech (prioritizes the primary speaker), and times captions to speaker turns. The viewer always knows who is saying what — essential for interview and podcast content where visual distinction is limited.
4. **Multilingual — Translated Subtitles (any length, 50+ languages)** — A company's product demo video in English needs subtitles in Spanish, French, German, Japanese, and Portuguese. NemoVideo: transcribes the English audio, translates to all 5 target languages with natural phrasing (not word-for-word machine translation), adjusts caption timing for each language (German sentences are longer than English, Japanese reads faster), generates separate SRT files per language, and optionally burns in dual-language captions (English + one other language). One video becomes accessible to a global audience.
5. **Batch Captioning — Full Content Library (multiple videos)** — A course creator has 20 lecture videos without captions. NemoVideo batch-processes all 20: consistent caption style across the series (same font, size, position, timing), speaker identification maintained per lecturer, technical terminology handled correctly (the AI learns from the first few videos' vocabulary), and exports as both SRT files and burned-in versions. An entire content library made accessible in one batch.

## How It Works

### Step 1 — Upload Video
Any video with spoken audio. Any language. Any accent. Any audio quality (NemoVideo handles background noise, echo, and low-quality microphones).

### Step 2 — Choose Caption Style
Select: subtitle format (SRT, VTT, burned-in), caption style (sentence, word-by-word, speaker-labeled), visual design (font, colors, position), and language options.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-subtitle-generator",
    "prompt": "Generate subtitles for a 12-minute YouTube tutorial. Language: English. Style: word-by-word highlight for a burned-in social version (white text, #FFD700 yellow highlight, dark pill background, centered bottom third) AND sentence-level SRT for YouTube closed captions. Speaker: single speaker. Also generate Spanish and French translated SRT files.",
    "source_language": "en",
    "caption_styles": [
      {"type": "burned-in", "style": "word-highlight", "text": "#FFFFFF", "highlight": "#FFD700", "bg": "pill-dark", "position": "bottom-center"},
      {"type": "srt", "style": "sentence"}
    ],
    "translations": ["es", "fr"],
    "speaker_detection": true
  }'
```

### Step 4 — Review and Apply
Preview: caption accuracy, timing sync, visual placement. Edit any misrecognized words. Export or upload SRT to YouTube.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Video description and caption requirements |
| `source_language` | string | | "en", "es", "fr", "de", "ja", "ko", "zh", "ar", "auto" |
| `caption_styles` | array | | [{type, style, text, highlight, bg, position}] |
| `translations` | array | | Target languages for translated subtitles |
| `speaker_detection` | boolean | | Identify and label speakers (default: true) |
| `speaker_names` | array | | ["Host", "Guest"] — custom speaker labels |
| `vocabulary` | array | | Technical terms, brand names, jargon for accuracy |
| `max_chars_per_line` | integer | | Characters per caption line (default: 42) |
| `batch` | array | | Multiple videos for batch captioning |

## Output Example

```json
{
  "job_id": "asg-20260328-001",
  "status": "completed",
  "source_duration": "12:08",
  "source_language": "en",
  "accuracy": "98.4%%",
  "outputs": {
    "burned_in": {
      "file": "tutorial-captioned.mp4",
      "style": "word-highlight (white + #FFD700)",
      "words_captioned": 1842
    },
    "srt_english": {
      "file": "tutorial-en.srt",
      "lines": 286,
      "style": "sentence-level"
    },
    "srt_spanish": {
      "file": "tutorial-es.srt",
      "lines": 292
    },
    "srt_french": {
      "file": "tutorial-fr.srt",
      "lines": 288
    }
  },
  "speakers_detected": 1
}
```

## Tips

1. **Word-by-word captions are mandatory for short-form social video** — TikTok, Reels, and Shorts audiences expect animated word-by-word highlighting. Sentence-level subtitles on short-form content feel like an afterthought. Match the caption style to the platform.
2. **98% accuracy means 2 errors per 100 words — still review** — In a 10-minute video (~1,500 words), expect ~30 potential errors. Most are minor (capitalization, punctuation), but name misspellings and technical terms need manual review. Use the vocabulary parameter to pre-teach unusual words.
3. **Translated subtitles multiply audience by 5-10x** — An English video with Spanish, French, German, and Japanese subtitles is accessible to 3 billion+ additional speakers. The translation cost is negligible compared to the audience expansion.
4. **Speaker labels transform multi-person content** — Without labels, the viewer must figure out who said what from context. With color-coded speaker labels, the conversation becomes instantly parseable. Essential for podcasts, interviews, and panel discussions.
5. **Caption position matters: bottom-center for landscape, top-third for vertical** — On landscape (16:9) video, captions sit at the bottom where viewers expect them. On vertical (9:16) video, captions in the upper third avoid being hidden by platform UI elements (like, comment, share buttons).

## Output Formats

| Format | Content | Use Case |
|--------|---------|----------|
| SRT | Timed subtitle file | YouTube / Vimeo upload |
| VTT | Web subtitle file | HTML5 video player |
| MP4 | Video with burned-in captions | Social media / direct share |
| TXT | Plain transcript | Blog / show notes |
| JSON | Structured transcript with timing | API integration |

## Related Skills

- [auto-caption-video](/skills/auto-caption-video) — Auto captioning
- [animated-video-maker](/skills/animated-video-maker) — Animated videos
- [gaming-video-editor](/skills/gaming-video-editor) — Gaming video editing
