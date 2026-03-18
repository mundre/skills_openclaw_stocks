# API Integration

Use this reference when the user wants to wire the moderation skill into pull APIs, callback APIs, comment APIs, or a fully automatic review workflow.

## Recommended architecture

Use a simple four-step flow:

1. 拉取未审核帖子数据
2. 调用大模型审核标题/正文/图片/视频
3. 生成结构化审核结果
4. 回调业务审核结果接口

For comments, use a lighter flow:

1. 接收评论 `id + text`
2. 调用审核
3. 立即返回通过/拒绝结果

## Pull interface for pending posts

Recommended input shape:

```json
[
  {
    "id": 10001,
    "title": "xx",
    "imgs": [
      "https://cdn.example.com/a.jpg"
    ],
    "videos": [
      "https://cdn.example.com/a.mp4"
    ],
    "content": "xxx",
    "other": 0
  }
]
```

### Field notes

- `id`: required; unique post id
- `title`: optional but should be provided when available
- `imgs`: array of image URLs
- `videos`: array of video URLs
- `content`: main post body
- `other`: business extension field such as source/type/flags

## Callback interface for audit result

Recommended callback payload:

```json
{
  "id": 10001,
  "audit_status": "pass|reject|review",
  "is_pass": 1,
  "risk_level": "low|medium|high",
  "reason": "图片右下角存在微信联系方式",
  "hit_rules": ["contact_info"],
  "hit_fields": ["images"],
  "hit_positions": ["image_1_bottom_right"],
  "action": "replace_image",
  "audit_time": "2026-03-18 18:30:00"
}
```

### Minimal callback fields

If the business side only needs the minimum fields, return:

```json
{
  "id": 10001,
  "is_pass": 0,
  "reason": "存在广告或联系方式"
}
```

## Comment moderation interface

Recommended comment input:

```json
{
  "id": 90001,
  "text": "加V了解一下 abc123456"
}
```

Recommended comment output:

```json
{
  "id": 90001,
  "audit_status": "reject",
  "is_pass": 0,
  "risk_level": "high",
  "reason": "评论中存在联系方式和引流话术",
  "hit_rules": ["contact_info", "advertising"]
}
```

## Automatic audit rule

If the user wants fully automatic moderation with no human action, use this policy:

- `pass` → 自动通过
- `reject` → 自动拦截
- do not use `review` unless the business explicitly keeps a manual-review lane

If the user requires zero manual operations, convert ambiguous cases into a conservative result:
- high-confidence violation → `reject`
- high-confidence clean content → `pass`
- ambiguous but risky content → `reject`

This is stricter, but matches "自动审核不需要人工操作".

## Prompting pattern for model call

When sending data to the model, include:
- moderation policy summary
- whitelist rules
- custom business rules
- post fields: title, content, imgs, videos
- required output schema

Recommended result schema:

```json
{
  "id": 10001,
  "audit_status": "pass|reject",
  "is_pass": 1,
  "risk_level": "low|medium|high",
  "reason": "string",
  "hit_rules": ["advertising", "contact_info"],
  "hit_fields": ["title", "content", "images", "videos"],
  "hit_positions": ["title", "image_1", "video_end_card"],
  "action": "publish|reject|replace_image|trim_video"
}
```

## Example x.ai request shape

Do not hardcode real keys in code or docs. Use environment variables.

```bash
curl https://api.x.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-4-1-fast",
    "temperature": 0,
    "stream": false,
    "messages": [
      {
        "role": "system",
        "content": "You are a strict moderation assistant. Block ads and contact information. Return JSON only."
      },
      {
        "role": "user",
        "content": "请审核以下帖子并返回 JSON：标题: xx；正文: xxx；图片: [https://...]; 视频: [https://...]"
      }
    ]
  }'
```

## Reliability recommendations

- set request timeout and connect timeout
- use retries only for network/transient failures, not content failures
- keep `temperature` at `0`
- enforce JSON-only output
- log raw request id, post id, result, and reason
- if image/video cannot be fetched, fail closed when full automation is required

## Suggested business mapping

### Posts

- `is_pass = 1` => 发布成功 or move to published state
- `is_pass = 0` => 拦截 and store reason

### Comments

- `is_pass = 1` => comment visible
- `is_pass = 0` => comment hidden/rejected immediately

## Suggested error handling

If model call fails:
- full-auto strict mode: reject and record `审核服务失败，已自动拦截`
- balanced mode: send to manual review

If media download fails:
- full-auto strict mode: reject and record `媒体读取失败，无法完成审核`
- balanced mode: send to manual review
