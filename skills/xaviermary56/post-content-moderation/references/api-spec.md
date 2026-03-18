# API Spec

Use this reference when the user wants a backend-facing API contract for post moderation, comment moderation, callback integration, and fully automatic review.

## 1. Pending post pull API

Business side returns a list of posts waiting for moderation.

### Response example

```json
{
  "code": 0,
  "message": "ok",
  "data": [
    {
      "id": 10001,
      "title": "副业分享",
      "content": "最近发现一个不错的项目",
      "imgs": [
        "https://cdn.example.com/post/10001-1.jpg"
      ],
      "videos": [
        "https://cdn.example.com/post/10001-1.mp4"
      ],
      "other": 0,
      "created_at": "2026-03-18 18:00:00"
    }
  ]
}
```

### Field definition

| Field | Type | Required | Description |
|---|---|---:|---|
| code | int | yes | `0` means success |
| message | string | yes | response message |
| data | array | yes | pending moderation list |
| data[].id | int/string | yes | unique post id |
| data[].title | string | no | post title |
| data[].content | string | no | post body |
| data[].imgs | array | no | image url list |
| data[].videos | array | no | video url list |
| data[].other | int/string/object | no | business extension field |
| data[].created_at | string | no | creation time |

### Validation rules

- `id` is mandatory
- at least one of `title`, `content`, `imgs`, `videos` should exist
- media URLs should be directly readable by the moderation service or use signed URLs

## 2. Moderation callback API

Moderation service calls the business callback after a decision is made.

### Request example

```json
{
  "id": 10001,
  "audit_status": "reject",
  "is_pass": 0,
  "risk_level": "high",
  "reason": "第1张图片右下角存在微信联系方式",
  "hit_rules": ["contact_info"],
  "hit_fields": ["images"],
  "hit_positions": ["image_1_bottom_right"],
  "action": "replace_image",
  "model_name": "grok-4-1-fast",
  "audit_mode": "auto",
  "audit_time": "2026-03-18 18:30:00",
  "trace_id": "audit-post-10001-20260318183000"
}
```

### Field definition

| Field | Type | Required | Description |
|---|---|---:|---|
| id | int/string | yes | post id |
| audit_status | string | yes | `pass` / `reject` / `review` |
| is_pass | int | yes | `1` pass, `0` reject |
| risk_level | string | yes | `low` / `medium` / `high` |
| reason | string | yes | core reason |
| hit_rules | array | no | matched rules |
| hit_fields | array | no | matched fields |
| hit_positions | array | no | matched positions |
| action | string | no | suggested action |
| model_name | string | no | model used |
| audit_mode | string | no | `auto` / `manual_review_enabled` |
| audit_time | string | yes | decision time |
| trace_id | string | no | trace id |

### Recommended response

```json
{
  "code": 0,
  "message": "callback accepted"
}
```

## 3. Minimal callback mode

If the business side only wants the simplest result:

### Request example

```json
{
  "id": 10001,
  "is_pass": 0,
  "reason": "存在广告或联系方式"
}
```

This mode is easy to integrate, but loses detailed audit evidence.

## 4. Comment moderation API

This API is for comment text and short text moderation.

### Request example

```json
{
  "id": 90001,
  "text": "加V了解一下 abc123456"
}
```

### Response example

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": 90001,
    "audit_status": "reject",
    "is_pass": 0,
    "risk_level": "high",
    "reason": "评论中存在联系方式和引流话术",
    "hit_rules": ["contact_info", "advertising"],
    "action": "reject"
  }
}
```

### Comment field definition

| Field | Type | Required | Description |
|---|---|---:|---|
| id | int/string | yes | comment id |
| text | string | yes | comment content |
| audit_status | string | yes | `pass` / `reject` |
| is_pass | int | yes | `1` pass, `0` reject |
| risk_level | string | yes | `low` / `medium` / `high` |
| reason | string | yes | rejection reason or pass reason |
| hit_rules | array | no | matched rule list |
| action | string | no | `publish` / `reject` |

## 5. Automatic audit policy

Use this when the user wants no human intervention.

### Strict full-auto mode

- clear clean content -> `pass`
- clear ad/contact content -> `reject`
- ambiguous but risky content -> `reject`
- media unreadable -> `reject`
- model request failed -> `reject`
- model returned invalid JSON -> `reject`

### Balanced mode

- clear clean content -> `pass`
- clear ad/contact content -> `reject`
- ambiguous or partially unreadable content -> `review`
- upstream/model/media temporary failure -> `review`

### Comment policy

- normal discussion -> `pass`
- any ad/contact signal -> `reject`
- uncertain disguised contact intent:
  - strict full-auto -> `reject`
  - balanced mode -> `review`

## 6. Error code spec

Recommended common error codes:

| Code | Meaning | Suggested handling |
|---:|---|---|
| 0 | success | normal processing |
| 4001 | invalid parameters | fix request and retry |
| 4002 | missing id | reject request |
| 4003 | empty content | reject request |
| 4004 | invalid media url | reject request or mark failed |
| 5001 | model request failed | strict mode reject; balanced mode manual review |
| 5002 | media download failed | strict mode reject; balanced mode manual review |
| 5003 | model returned invalid JSON | retry once or fail closed |
| 5004 | callback failed | retry callback with backoff |
| 5005 | callback timeout | retry callback with backoff |

### Error response example

```json
{
  "code": 5002,
  "message": "media download failed",
  "data": {
    "id": 10001
  }
}
```

## 7. Action enum suggestion

Recommended `action` values:

- `publish`
- `reject`
- `replace_image`
- `replace_video`
- `trim_video`
- `rewrite_text`
- `block_comment`
- `review`

## 8. Suggested implementation flow

### Posts

1. pull pending posts
2. validate request fields
3. fetch title/content/images/videos
4. call model with strict moderation prompt
5. parse JSON result
6. normalize the result fields
7. map result to business callback contract
8. callback business system
9. retry callback if needed

### Comments

1. receive `id + text`
2. call model with comment-only moderation prompt
3. normalize the result fields
4. return structured result immediately

## 9. Security and reliability notes

- never hardcode API keys in source code or docs
- use environment variables such as `XAI_API_KEY`
- keep model `temperature = 0`
- enforce JSON-only output
- add timeout and connect timeout
- log `id`, `trace_id`, result, reason, and callback status
- if using strict full-auto mode, fail closed on upstream/model/media errors
- if callback is important, retry and keep a dead-letter record

## 10. Prompt contract suggestion

Recommended system contract:

```text
You are a strict moderation assistant. Review title, content, images, and videos. Block ads and contact information. Respect whitelist rules. Return JSON only. In full-auto mode, reject ambiguous risky content instead of asking for manual review.
```

Recommended user payload shape:

```json
{
  "id": 10001,
  "title": "xx",
  "content": "xxx",
  "imgs": ["https://..."],
  "videos": ["https://..."],
  "whitelist": [],
  "custom_rules": [],
  "output": "json"
}
```
