# Output Schema Reference

## Envelope Structure

### Success Envelope (stdout)

```json
{
  "success": true,
  "task_id": "<string>",
  "results_num": "<int>",
  "ai_overview_count": "<int>",
  "ai_overview": [ ... ],
  "organic_results": [ ... ],
  "screenshot": "<string>"
}
```

### Error Envelope (stderr)

```json
{
  "success": false,
  "error": {
    "code": "<string>",
    "api_code": "<int>",
    "message": "<string>",
    "hint": "<string>"
  }
}
```

## Success Fields

| Field | Type | Guaranteed | Description |
|-------|------|------------|-------------|
| `success` | boolean | Yes | Always `true` |
| `task_id` | string | Yes | Unique Pangolinfo task identifier |
| `results_num` | int | Yes | Number of organic results (0 if none) |
| `ai_overview_count` | int | Yes | Number of AI overview blocks (0 if none) |
| `ai_overview` | array | No | Present only if AI overviews exist |
| `organic_results` | array | No | Present only if organic results exist |
| `screenshot` | string | No | Screenshot URL; present only if `--screenshot` was used |

### `ai_overview[]` Item

| Field | Type | Description |
|-------|------|-------------|
| `content` | string[] | AI-generated text paragraphs |
| `references` | array | Source references (may be empty) |

### `ai_overview[].references[]` Item

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Source page title |
| `url` | string | Source page URL |
| `domain` | string | Source domain name |

### `organic_results[]` Item

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Result page title |
| `url` | string | Result page URL |
| `text` | string | Result snippet text (may be null) |

## Error Fields

| Field | Type | Guaranteed | Description |
|-------|------|------------|-------------|
| `success` | boolean | Yes | Always `false` |
| `error.code` | string | Yes | Machine-readable error code |
| `error.api_code` | int | No | Pangolinfo API error code (when applicable) |
| `error.message` | string | Yes | Human-readable description |
| `error.hint` | string | No | Suggested resolution |

## Auth-Only Output (stdout)

```json
{
  "success": true,
  "message": "Authentication successful",
  "api_key_preview": "eyJh...ab1c"
}
```

## Raw Mode

When using `--raw`, the unprocessed Pangolinfo API response is output. The envelope structure above does **not** apply.
