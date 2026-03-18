# Kling API reference (video)

This skill maps to three endpoints; the script chooses by parameters.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /v1/videos/text2video | Text-to-video |
| GET  | /v1/videos/text2video/{task_id} | Query text-to-video task |
| POST | /v1/videos/image2video | Image-to-video |
| GET  | /v1/videos/image2video/{task_id} | Query image-to-video task |
| POST | /v1/videos/omni-video | Omni / multi-shot |
| GET  | /v1/videos/omni-video/{task_id} | Query Omni task |

## Request body (text-to-video)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| model_name | string | yes | kling-v3 |
| prompt | string | yes | Video description |
| negative_prompt | string | no | Negative prompt |
| duration | string | no | "3"-"15" |
| mode | string | no | pro / std |
| aspect_ratio | string | no | 16:9 / 9:16 / 1:1 |
| sound | string | no | on / off |

## Request body (image-to-video)

Same as text-to-video plus: image (required), image_tail (optional).

## Request body (Omni)

Supports multi_shot, multi_prompt, image_list, element_list, video_list, etc. See Kling 3.0 API docs for details.

## Response

Submit returns `task_id`. Query success: `task_result.videos[0].url` is the video URL. Refer to latest Kling docs.
