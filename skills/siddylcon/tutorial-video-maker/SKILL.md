---
name: tutorial-video-maker
version: 2.0.2
displayName: "Tutorial Video Maker — Create How-To Guides Step-by-Step Tutorials and Course Videos"
description: >
  Create how-to guides, step-by-step tutorials, and online course videos with AI — produce polished educational content with screen recordings, webcam overlay, step numbering, chapter navigation, zoom-to-detail callouts, code highlighting, annotation arrows, progress indicators, and professional narration. NemoVideo transforms raw tutorial recordings into structured learning experiences: clean up screen recordings with zoom-to-action focus, add step indicators and progress bars, create chapter markers for non-linear navigation, highlight key elements with animated callouts, layer clear narration, and export for YouTube Udemy Skillshare and course platforms. Tutorial video maker AI, how-to video creator, course video maker, step-by-step video, screen recording editor, educational video AI, training video maker, instructional video creator, online course video tool.
metadata: {"openclaw": {"emoji": "📚", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
apiDomain: https://mega-api-prod.nemovideo.ai
---

# Tutorial Video Maker — Teach Anything. Look Like You Have a Production Team.

Tutorial content is the backbone of YouTube. "How to" is the most searched phrase on YouTube after music. 86% of YouTube viewers say they use the platform to learn new things. The educational video market (online courses, tutorials, training) is projected at $350 billion by 2027. Whether teaching software, cooking, crafts, coding, fitness, music, or any skill — tutorial video is the delivery format that reaches the largest audience. The challenge is not knowing the subject — it is producing video that teaches effectively. Great tutorials require: clear visual structure (the viewer must always know what step they are on), zoom-to-detail at critical moments (showing exactly where to click, what to type, where to cut), progress indication (how far through the tutorial they are), chapter navigation (so they can skip to the step they need), clean audio (narration must be clear over any background), and pacing appropriate to difficulty (slow for complex steps, faster for simple ones). Professional tutorial production involves: screen recording with mouse highlighting ($100-300 software), webcam overlay compositing (picture-in-picture setup), post-production editing with zoom effects (2-4x real-time in editing hours), annotation graphics creation (arrows, circles, text callouts), and chapter structuring. NemoVideo automates the production layer entirely. Record your tutorial — screen recording, camera recording, or both — and NemoVideo produces structured educational content with every element that makes tutorials effective.

## Use Cases

1. **Software Tutorial — Screen Recording with Smart Zoom (5-30 min)** — A creator records a 20-minute Photoshop tutorial: full-screen capture with voiceover narration. The raw recording shows the entire monitor at all times — when the instructor clicks a small toolbar icon, it is invisible at the video's viewing resolution. NemoVideo: detects mouse activity and interface interactions, applies automatic zoom-to-action (when the cursor moves to a small element, the view smoothly zooms to 200-300% centered on that element, holds for the interaction, then smoothly zooms back to full screen), adds click highlighting (a subtle ripple effect on every mouse click so viewers see exactly what was clicked), displays keyboard shortcuts as overlays when pressed ("Cmd+T" appearing near the cursor), adds step numbering ("Step 3: Select the Lasso Tool"), creates chapter markers at each major step, and adds a progress bar showing position within the tutorial. A screen recording that teaches through directed attention rather than forcing the viewer to find the relevant pixel.

2. **Cooking/Craft Tutorial — Hands-On with Step Cards (10-30 min)** — A cooking instructor records a recipe tutorial on their phone. NemoVideo: adds step cards that appear at each new phase ("Step 4: Fold the egg whites into the batter — gently, do not deflate"), displays ingredient lists as overlays when relevant (showing the specific ingredients needed for each step), creates timing overlays for processes ("Bake at 375°F for 25 minutes" with a visible timer), adds zoom-in on critical technique moments (close-up on folding technique, knife cuts, decoration details), layers clear narration above cooking sounds, creates a recipe card summary at the end (all ingredients and steps displayed as a screenshottable reference), and adds chapter markers for each recipe phase (Prep, Cook, Assembly, Plating). A recipe video that viewers can actually follow step-by-step without pausing and rewinding constantly.

3. **Coding Tutorial — Code Display with Syntax Highlighting (10-45 min)** — A developer records a coding tutorial: screen recording of their IDE with voiceover explaining each code block. NemoVideo: enhances code readability (syntax highlighting optimized for video — larger font, high-contrast color scheme, dark background), adds line-by-line highlighting as each line is explained (the current line glows while the instructor discusses it), displays code output in a split-screen panel (code on left, output on right — viewers see cause and effect simultaneously), zooms to relevant code sections (when discussing a specific function, the view zooms to that function), adds error callouts when debugging (red highlight on the error line, green on the fix), and creates chapter markers by topic (Setup, Data Model, API Routes, Testing, Deployment). Code tutorials where viewers can read every character and follow every logical step.

4. **Course Module — Structured Lesson with Assessment (15-45 min)** — An instructor creates a lesson within a larger online course. NemoVideo: adds course branding (consistent header with course name, module number, lesson title), displays learning objectives at the beginning ("By the end of this lesson, you will be able to..."), adds knowledge check pauses (the video pauses with a question on screen, giving 10 seconds for the viewer to think before revealing the answer), inserts recap summaries at section transitions (key points listed as visual bullet points), adds a lesson summary at the end with links to the next lesson, and maintains pacing appropriate for learning (pauses after complex concepts, faster through review material). A lesson that follows instructional design best practices, not just content delivery.

5. **Quick How-To — Social Media Tutorial (30-90s)** — A creator produces short, punchy tutorials for TikTok and Instagram: "How to remove a background in Canva in 30 seconds" or "3 iPhone camera tricks you didn't know." NemoVideo: compresses the key steps into the target duration (removing all explanation beyond the essential), adds large step numbers visible at mobile size ("1" "2" "3" filling a quarter of the screen), uses fast zoom-to-action on every interface interaction (no wasted frames showing the full screen when the action is in one small area), adds text captions for every spoken instruction (most social viewing is muted), and creates a punchy intro hook in the first 2 seconds ("Stop doing THIS in Canva"). Short-form tutorial format that teaches and entertains in under a minute.

## How It Works

### Step 1 — Upload Tutorial Recording
Screen recording, camera recording, screen + webcam combo, or phone footage. Any format, any resolution.

### Step 2 — Define Tutorial Structure
Number of steps, key moments to zoom, chapter markers, and any overlays needed (step cards, ingredient lists, code display).

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "tutorial-video-maker",
    "prompt": "Create a polished 15-minute Figma tutorial from screen recording with voiceover. Auto-detect cursor movements and apply zoom-to-action: 250%% zoom on toolbar clicks, 200%% on panel interactions, smooth transitions between zoom levels. Add click highlighting (subtle ripple on every click). Display keyboard shortcuts as overlays when pressed. Step numbering: 8 major steps, display step card at each transition (Step 1: Create a new frame, etc.). Chapter markers matching steps. Progress bar showing tutorial completion percentage. Webcam overlay: small circle in lower-right showing the instructor. Add intro title card: Figma for Beginners — Auto Layout Explained. Export 16:9 for YouTube + extract the 3 most visual steps as 9:16 clips for TikTok.",
    "tutorial_type": "software-screen-recording",
    "smart_zoom": {
      "toolbar_clicks": "250%%",
      "panel_interactions": "200%%",
      "transition": "smooth"
    },
    "click_highlight": true,
    "keyboard_shortcuts": true,
    "steps": 8,
    "step_cards": true,
    "chapters": true,
    "progress_bar": true,
    "webcam_overlay": {"shape": "circle", "position": "lower-right", "size": "small"},
    "title_card": "Figma for Beginners — Auto Layout Explained",
    "formats": {"main": "16:9", "clips": "9:16"}
  }'
```

### Step 4 — Review Learning Flow
Watch as a learner would. Verify: zoom-to-action shows the right element at the right time, step numbering matches the actual instruction, chapters align with topic transitions, pacing allows comprehension of complex steps. Adjust and re-render.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Tutorial production requirements |
| `tutorial_type` | string | | "software-screen-recording", "hands-on", "coding", "course-module", "quick-howto" |
| `smart_zoom` | object | | {toolbar_clicks, panel_interactions, transition} auto zoom settings |
| `click_highlight` | boolean | | Visual ripple on mouse clicks |
| `keyboard_shortcuts` | boolean | | Display shortcut overlays |
| `steps` | int | | Number of major steps |
| `step_cards` | boolean | | Display step description cards |
| `chapters` | boolean | | Create chapter markers |
| `progress_bar` | boolean | | Show tutorial completion progress |
| `webcam_overlay` | object | | {shape, position, size} picture-in-picture |
| `code_display` | object | | {syntax_highlighting, line_highlight, split_output} |
| `knowledge_checks` | array | | [{question, answer, pause_duration}] |
| `formats` | object | | {main, clips} output formats |

## Output Example

```json
{
  "job_id": "tutmk-20260329-001",
  "status": "completed",
  "tutorial_type": "software-screen-recording",
  "duration": "14:52",
  "steps": 8,
  "zoom_events": 34,
  "click_highlights": 87,
  "shortcut_overlays": 12,
  "chapters": 8,
  "outputs": {
    "full_tutorial": {"file": "figma-autolayout-16x9.mp4", "resolution": "1920x1080"},
    "tiktok_clips": [
      {"file": "step3-autolayout-9x16.mp4", "duration": "0:42"},
      {"file": "step5-constraints-9x16.mp4", "duration": "0:38"},
      {"file": "step7-responsive-9x16.mp4", "duration": "0:45"}
    ]
  }
}
```

## Tips

1. **Zoom-to-action is the single most important feature in screen recording tutorials** — A full-screen recording at 1080p makes toolbar icons and menu items invisible at typical viewing sizes (phone, laptop in a browser tab). Automated zoom-to-action ensures the viewer sees exactly the relevant interface element at every interaction, eliminating the "where did they click?" frustration that causes tutorial abandonment.
2. **Step numbering creates a mental scaffold that prevents cognitive overload** — A viewer following a 15-step process without numbered steps loses track by step 6. Numbered step cards create structure: the viewer always knows where they are, how far they have come, and how many steps remain. This reduces anxiety and increases completion rates.
3. **Chapter markers respect the viewer's time** — Most tutorial viewers are not watching linearly — they are trying to solve a specific problem. Chapter markers let them jump to the relevant step immediately. A 20-minute tutorial with chapters serves both the full-watch learner and the "I just need step 7" problem-solver.
4. **Webcam overlay creates human connection in screen-only content** — A screen recording with voiceover is informative. A screen recording with a small webcam overlay showing the instructor's face is informative AND personal. The face creates trust, engagement, and the sense that a human is teaching you, not just narrating pixels.
5. **Short-form tutorial clips drive discovery for the full tutorial** — A 45-second TikTok showing one impressive technique drives viewers to the full YouTube tutorial. Social micro-tutorials are not the lesson — they are the advertisement for the lesson. Always extract short clips for social distribution.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / Udemy / Skillshare / course platform |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts (tip clips) |
| MP4 1:1 | 1080x1080 | Instagram / LinkedIn |

## Related Skills

- [ai-video-zoom](/skills/ai-video-zoom) — Zoom effects for emphasis
- [ai-video-caption-generator](/skills/ai-video-caption-generator) — Tutorial captions
- [ai-video-text-overlay](/skills/ai-video-text-overlay) — Step cards and annotations
- [ai-video-chapter-maker](/skills/ai-video-chapter-maker) — Auto chapter detection
