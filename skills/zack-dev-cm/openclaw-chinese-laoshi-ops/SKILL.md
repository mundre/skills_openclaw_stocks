---
name: openclaw-chinese-laoshi-ops
description: Use when extracting Chinese lesson videos into raw transcripts, lesson JSON, learner docs, and Drive exports while enforcing pilot-first and prepublish leak gates.
homepage: https://github.com/zack-dev-cm/openclaw-agent-chinese-laoshi
user-invocable: true
metadata: {"openclaw":{"homepage":"https://github.com/zack-dev-cm/openclaw-agent-chinese-laoshi","skillKey":"openclaw-chinese-laoshi-ops","requires":{"bins":["python3","node"]}}}
---

# OpenClaw Chinese Laoshi Ops

Use this skill when working in the OpenClaw Chinese Laoshi repo or another repo
that exposes the same lesson schema, pipeline stages, and publication gate.

## Use This Skill When

- the task is to extract text from long-form Chinese lesson videos or subtitle drops
- the user wants lesson summaries, conspects, vocabulary, grammar, drills, or tests
- the user wants Markdown and JSON lesson assets exported to Drive
- the user wants to package or publish the workflow without leaking local paths,
  known Drive IDs, or secret-shaped text

## Quick Start

1. Validate the repo state before editing content.
   - `node scripts/check-lessons.mjs`
   - `python3 scripts/check_raw_transcripts.py`
2. Move only one lesson at a time beyond scaffold state.
   - Transcript drop lane:
     `python3 scripts/process_transcript_drop.py --lesson 1 --input /absolute/path/to/lesson-01.srt`
   - Whisper lane:
     `python3 scripts/transcribe_lesson_with_whisper.py --lesson 1 --smotrim-video-id <video_id>`
3. Build learner-facing artifacts only after extraction exists.
   - `python3 scripts/build_lesson_from_transcript.py --lesson 1`
   - `bash scripts/refresh_artifacts.sh`
4. Run the public release gate before any publish step.
   - `python3 scripts/check_publication_bundle.py`

If the repo-local scripts are absent, keep the same stages anyway: extract,
ground, review, render, export, publish. Do not skip directly from video to
polished lesson prose.

## Core Rules

- Raw lesson media stays in Drive or another operator-controlled store.
- Lesson 01 is the pilot gate. Do not scale real content to lessons 02-16 until
  lesson 01 is approved.
- Keep uncertainty visible. Missing Hanzi, pinyin, or translation should be
  marked, not guessed.
- The tutor is Petrov-inspired, not Petrov impersonation.
- Treat all public publication surfaces as hostile to private details. ClawHub
  and GitHub publication should assume anyone can read `SKILL.md`.

## Workflow

### 1. Extract

- Prefer a transcript or subtitle drop when available.
- If the source is video-only, transcribe into the raw transcript layer first.
- Keep timestamps, speaker-role placeholders, and uncertainty notes.

### 2. Ground

- Convert raw transcript segments into the lesson schema.
- Add summaries, conspects, vocabulary, grammar, pronunciation, drills, and
  tests only when the source supports them.
- Keep source traceability visible.

### 3. Review

- Check lesson quality against the pilot-first and editorial gates.
- Reject unsupported content, weak answer keys, and synthetic filler.
- Treat speaker labeling, Hanzi, pinyin, and translation drift as correctness
  problems, not style nits.

### 4. Render And Export

- Rebuild learner-facing Markdown after lesson JSON changes.
- Sync JSON and Markdown exports to Drive only after the repo copy passes checks.
- Keep exports small; raw media should not enter the repo or the public skill.

### 5. Publish

- The public bundle must pass the release gate before GitHub or ClawHub.
- The gate should fail closed on placeholders, local absolute paths, `localhost`
  URLs, websocket/debug endpoints, secret-like strings, and known lesson file
  IDs.

## Do Not

- Do not guess missing Chinese text or smooth weak source material into fake fluency.
- Do not move lessons 02-16 past scaffold state before the lesson 01 pilot clears.
- Do not publish local paths, private emails, mounted Drive paths, or browser
  session details.
- Do not let the public skill and the bundled plugin copy drift apart.

## References

- `references/pipeline.md`
  - current lesson pipeline, state transitions, and repo command surfaces
- `references/release-gates.md`
  - public publication checklist and leak/slop/bleed blockers
