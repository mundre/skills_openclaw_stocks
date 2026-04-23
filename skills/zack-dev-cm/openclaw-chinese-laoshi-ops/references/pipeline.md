# Pipeline Reference

Use this reference when the task is operational rather than editorial.

## Durable layers

1. `data/raw_transcripts`
   - timestamped source segments with uncertainty notes
2. `data/lessons`
   - normalized lesson JSON with summaries, conspects, vocabulary, grammar,
     pronunciation, drills, and tests
3. `docs/lessons`
   - learner-facing Markdown derived from lesson JSON
4. `exports/drive`
   - compact export bundles for syncing JSON and Markdown to Drive

## Preferred command path

- Transcript drop:
  - `python3 scripts/process_transcript_drop.py --lesson <n> --input <file>`
- Whisper transcription:
  - `python3 scripts/transcribe_lesson_with_whisper.py --lesson <n> --smotrim-video-id <video_id>`
- Lesson build:
  - `python3 scripts/build_lesson_from_transcript.py --lesson <n>`
- Course refresh:
  - `bash scripts/refresh_artifacts.sh`
- Drive sync:
  - `python3 scripts/build_drive_exports.py`
  - `python3 scripts/sync_drive_mount_exports.py`

## Quality rule

- Extraction is allowed to be ugly.
- Editorial review is allowed to be slow.
- Publication is not allowed to leak.
