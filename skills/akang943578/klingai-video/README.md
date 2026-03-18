# klingai-video

Kling video generation (single skill): text-to-video, image-to-video, Omni, multi-shot. Script picks the API by parameters.

## Usage

```bash
node scripts/kling_video.mjs --prompt "description" --output_dir ./output
node scripts/kling_video.mjs --image ./photo.jpg --prompt "motion" --output_dir ./output
node scripts/kling_video.mjs --task_id <id> --download
```

## Docs

- [SKILL.md](SKILL.md) — Usage and parameters
- [reference.md](reference.md) — API reference
