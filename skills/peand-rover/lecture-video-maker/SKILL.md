---
name: lecture-video-maker
version: 1.0.4
displayName: "Lecture Video Maker"
description: >
  Describe your lecture and NemoVideo creates the video. University courses, professional training sessions, conference talks — combine your slides, whiteboard, and camera into a polished lecture recording ready for your LMS, YouTube, or institution's course platform.

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

> 📹 Hey! I'm ready to help you lecture video maker. Send me a video file or just tell me what you need!

**Try saying:**
- "add effects to this clip"
- "help me create a short video"
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


# Lecture Video Maker — Record and Produce Academic and Course Lecture Content

Describe your lecture and NemoVideo creates the video. University courses, professional training sessions, conference talks — combine your slides, whiteboard, and camera into a polished lecture recording ready for your LMS, YouTube, or institution's course platform.

## When to Use This Skill

Use this skill for academic and formal instruction content:
- Record university and college course lectures with slide synchronization
- Create professional development and corporate training sessions
- Produce conference presentation recordings with speaker and slides
- Build online course content for platforms like Coursera, edX, or Teachable
- Document workshop and seminar recordings for institutional archives
- Create continuing education content for professional certification courses

## How to Describe Your Lecture

Be specific about the subject, structure, and key concepts covered.

**Examples of good prompts:**
- "Introduction to Macroeconomics lecture, 45 minutes: cover GDP measurement (expenditure approach), unemployment types (frictional, structural, cyclical), inflation and CPI. Include slides with graphs, show speaker camera, chapter markers for each topic."
- "Corporate onboarding training: company values and culture (15 min), benefits overview (10 min), IT setup and tools walkthrough (15 min), Q&A format. Professional tone, new employee audience."
- "Machine learning fundamentals course lecture: supervised vs unsupervised learning, overfitting and regularization, train/test split and cross-validation. Assume basic Python and statistics knowledge, intermediate audience."

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `lecture_format` | Recording style | `"slides_only"`, `"talking_head"`, `"picture_in_picture"`, `"screen_share"` |
| `subject` | Topic area | `"economics"`, `"computer_science"`, `"medicine"`, `"law"`, `"management"` |
| `duration_minutes` | Lecture length | `20`, `30`, `45`, `60`, `90` |
| `audience_level` | Viewer background | `"undergraduate"`, `"graduate"`, `"professional"`, `"executive"` |
| `chapter_markers` | Section navigation | `true` |
| `show_timestamps` | Time display | `true` |
| `closed_captions` | Accessibility | `true` |
| `platform` | Target LMS/platform | `"coursera"`, `"canvas"`, `"youtube"`, `"zoom_recording"` |

## Workflow

1. Describe the subject, lecture structure, and key concepts
2. NemoVideo sequences slides, speaker video, and board content
3. Chapter markers, timestamps, and captions added automatically
4. Export in formats compatible with your LMS or course platform

## API Usage

### University Course Lecture

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "lecture-video-maker",
    "input": {
      "prompt": "Organic Chemistry lecture on reaction mechanisms, 45 minutes: nucleophilic substitution (SN1 and SN2 reactions) with energy diagrams, stereochemistry implications, leaving group ability, solvent effects. Use molecular diagrams, arrow-pushing notation, worked examples for each mechanism type. Undergraduate chemistry audience.",
      "lecture_format": "picture_in_picture",
      "subject": "chemistry",
      "duration_minutes": 45,
      "audience_level": "undergraduate",
      "chapter_markers": true,
      "show_timestamps": true,
      "closed_captions": true,
      "platform": "canvas"
    }
  }'
```

**Response:**
```json
{
  "job_id": "lecture_jkl012",
  "status": "processing",
  "estimated_seconds": 180,
  "poll_url": "https://mega-api-prod.nemovideo.ai/v1/jobs/lecture_jkl012"
}
```

### Corporate Training Session

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "lecture-video-maker",
    "input": {
      "prompt": "Cybersecurity awareness training for non-technical employees: phishing email recognition (3 real-world examples), password security best practices, VPN usage policy, what to do if you click a suspicious link. Conversational professional tone, scenario-based learning, 30 minutes with quiz checkpoints.",
      "lecture_format": "talking_head",
      "subject": "cybersecurity",
      "duration_minutes": 30,
      "audience_level": "professional",
      "chapter_markers": true,
      "closed_captions": true,
      "platform": "coursera"
    }
  }'
```

## Tips for Best Results

- **Structure by learning objectives**: "After this lecture, students will understand X, Y, Z" — state the objectives and NemoVideo organizes the content accordingly
- **Name the specific concepts**: "SN1 vs SN2 mechanisms" beats "organic chemistry reaction" — specificity creates better diagram generation and chapter labeling
- **Duration shapes delivery**: 20-minute micro-lectures work well for online courses; 45-60 minutes for traditional university format
- **Accessibility matters**: Set `closed_captions: true` for institutional content — most LMS platforms require captions for compliance
- **Chapter markers for navigation**: Students rewatch specific sections; `chapter_markers: true` makes your lecture searchable and referenceable

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| Canvas / Blackboard | 1920×1080 | 20–90 min |
| Coursera / edX | 1920×1080 | 10–20 min segments |
| YouTube | 1920×1080 | any length |
| Zoom Recording | 1920×1080 | any length |

## Related Skills

- `tutorial-video-creator` — Shorter, more informal how-to content
- `whiteboard-animation-video` — Animated concept explanations to embed in lectures
- `coding-tutorial-video` — CS course coding demonstrations
- `language-learning-video` — Language instruction course content

## Common Questions

**Can I upload my existing PowerPoint slides?**
Yes — pass the slide file URL in `slides_url` and NemoVideo synchronizes them with your narration, adding transitions and zoom-ins on key diagrams.

**What's the best format for blended learning?**
Use 10-15 minute micro-lecture segments (`platform: "coursera"`) rather than one long recording. Students engage more with shorter units and you can update individual segments without re-recording the whole lecture.

**Does it add closed captions automatically?**
Set `closed_captions: true` and captions are generated and embedded. Export includes a separate VTT file for LMS upload.
