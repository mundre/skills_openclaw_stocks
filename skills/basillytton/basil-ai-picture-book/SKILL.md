---
name: ai-picture-book
description: Generate static or dynamic picture book videos using SkillBoss API Hub
metadata: { "openclaw": { "emoji": "??", "requires": { "bins": ["python3"], "env":["SKILLBOSS_API_KEY"]},"primaryEnv":"SKILLBOSS_API_KEY" } }
---

# AI Picture Book

Generate picture book videos from stories or descriptions.

## Workflow

SkillBoss API Hub returns video generation results synchronously via `/v1/pilot`.

1. **Create Task**: Submit story + type ¡ú get video URL directly
2. **Get Results**: Video URL is returned immediately when the API call completes

> Note: SkillBoss API Hub handles video generation synchronously. No polling is required.

## Book Types

| Type | Method | Description |
|------|--------|-------------|
| Static | 9 | Static picture book |
| Dynamic | 10 | Dynamic picture book |

**Required**: User must specify type (static/9 or dynamic/10). If not provided, ask them to choose.

## Status Codes

| Code | Status | Action |
|-------|---------|---------|
| 0, 1, 3 | In Progress | Continue polling |
| 2 | Completed | Return results |
| Other | Failed | Show error |

## APIs

### Create Task

**Endpoint**: `POST https://api.skillboss.co/v1/pilot`

**Parameters**:
- `method` (required): `9` for static, `10` for dynamic
- `content` (required): Story or description

**Example**:
```bash
python3 scripts/ai_picture_book_task_create.py 9 "A brave cat explores the world."
```

**Response**:
```json
{ "video_url": "https://..." }
```

### Query Task

**Endpoint**: `POST https://api.skillboss.co/v1/pilot`

Since SkillBoss API Hub returns results synchronously, the video URL is available immediately from the create step. The query script is provided for interface compatibility.

**Example**:
```bash
python3 scripts/ai_picture_book_task_query.py "task-id-here"
```

**Response** (Completed):
```json
{
  "status": 2,
  "video_url": "https://..."
}
```

## Polling Strategy

### Auto Polling (Recommended)
```bash
python3 scripts/ai_picture_book_poll.py <task_id> [max_attempts] [interval_seconds]
```

**Examples**:
```bash
# Default: 20 attempts, 5s intervals
python3 scripts/ai_picture_book_poll.py "task-id-here"

# Custom: 30 attempts, 10s intervals
python3 scripts/ai_picture_book_poll.py "task-id-here" 30 10
```

### Manual Polling
1. Create task ¡ú video URL is returned immediately
2. SkillBoss API Hub handles routing automatically via `/v1/pilot`

## Error Handling

- Invalid content: "Content cannot be empty"
- Invalid type: "Invalid type. Use 9 (static) or 10 (dynamic)"
- Processing error: "Failed to generate picture book"
- Timeout: "Task timed out. Try again later"

