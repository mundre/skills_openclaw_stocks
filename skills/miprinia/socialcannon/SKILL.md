---
name: socialcannon
description: >
  Publish, schedule, and manage social media posts across Twitter/X, Facebook,
  Instagram, LinkedIn, TikTok, and YouTube. Content calendar with gap analysis,
  A/B testing, engagement inbox, AI content repurposing, optimal timing
  suggestions, auto-scheduling, and UTM tracking.
version: 1.2.0
metadata:
  openclaw:
    requires:
      env:
        - SOCIALCANNON_CLIENT_ID
        - SOCIALCANNON_CLIENT_SECRET
      bins:
        - curl
    primaryEnv: SOCIALCANNON_CLIENT_ID
    emoji: "\U0001F4E3"
    homepage: https://socialcannon.app
---

# SocialCannon

Social media publishing API. Publish to Twitter/X, Facebook, Instagram, LinkedIn, TikTok, and YouTube from one API with scheduling, analytics, A/B testing, and AI-powered features.

**Base URL:** `https://socialcannon.app`

## Getting Started

Before making API calls, you need credentials and at least one connected social account.

### 1. Get your API credentials

Sign up at [socialcannon.app](https://socialcannon.app) and create an account. Your **Client ID** and **Client Secret** are available on the dashboard Settings page. These are the values for `SOCIALCANNON_CLIENT_ID` and `SOCIALCANNON_CLIENT_SECRET`.

### 2. Connect social accounts

Social accounts are connected via OAuth in the browser. Open the connect URL for each platform you want to use — you'll authorize SocialCannon and get redirected back:

| Platform | Connect URL |
|----------|-------------|
| Twitter/X | `https://socialcannon.app/api/connect/twitter?client_id=YOUR_CLIENT_ID` |
| Facebook | `https://socialcannon.app/api/connect/facebook?client_id=YOUR_CLIENT_ID` |
| Instagram | `https://socialcannon.app/api/connect/instagram?client_id=YOUR_CLIENT_ID` |
| LinkedIn | `https://socialcannon.app/api/connect/linkedin?client_id=YOUR_CLIENT_ID` |
| TikTok | `https://socialcannon.app/api/connect/tiktok?client_id=YOUR_CLIENT_ID` |
| YouTube | `https://socialcannon.app/api/connect/youtube?client_id=YOUR_CLIENT_ID` |

You can also connect accounts from the dashboard at **Settings → Accounts**. Instagram uses Facebook's OAuth flow — make sure you select the Facebook Page linked to your Instagram Business account.

### 3. Get an API token and start posting

Once you have credentials and at least one connected account, authenticate and create your first post:

```bash
# Get a token
TOKEN=$(curl -s -X POST https://socialcannon.app/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d "{\"grant_type\": \"client_credentials\", \"client_id\": \"$SOCIALCANNON_CLIENT_ID\", \"client_secret\": \"$SOCIALCANNON_CLIENT_SECRET\"}" \
  | jq -r '.data.access_token')

# List your connected accounts
curl -s https://socialcannon.app/api/v1/accounts \
  -H "Authorization: Bearer $TOKEN" | jq '.data'

# Publish a post (replace <account_id> with an ID from the list above)
curl -X POST https://socialcannon.app/api/v1/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"accountId": "<account_id>", "content": "Hello from SocialCannon!"}'
```

## Authentication

All requests require a JWT Bearer token. Get one by exchanging your client credentials:

```bash
curl -X POST https://socialcannon.app/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d "{
    \"grant_type\": \"client_credentials\",
    \"client_id\": \"$SOCIALCANNON_CLIENT_ID\",
    \"client_secret\": \"$SOCIALCANNON_CLIENT_SECRET\"
  }"
```

Response:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "scope": "posts:read posts:write ..."
  }
}
```

Use `response.data.access_token` as a Bearer token in all subsequent requests. Tokens expire after 1 hour — request a new one when you get a 401.

**All requests below require this header:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Response Format

**IMPORTANT: ALL responses are wrapped in a standard envelope.** This includes the token endpoint.

- Success: `{ "success": true, "data": { ... } }`
- Error: `{ "success": false, "error": "message", "code": "ERROR_CODE" }`

When extracting data from any response, always read from `response.data`, not from the response root. For example, to get the access token: `response.data.access_token`, not `response.access_token`.

## Accounts

Accounts represent social media profiles connected via OAuth (see Getting Started above). You need at least one connected account before you can create posts.

### List connected accounts

```bash
curl https://socialcannon.app/api/v1/accounts \
  -H "Authorization: Bearer $TOKEN"
```

Returns all connected social accounts with their platform, username, and status. Use the account `id` field when creating posts. Filter by platform with `?platform=twitter`.

### Get a single account

```bash
curl https://socialcannon.app/api/v1/accounts/<account_id> \
  -H "Authorization: Bearer $TOKEN"
```

### Disconnect an account

```bash
curl -X DELETE https://socialcannon.app/api/v1/accounts/<account_id> \
  -H "Authorization: Bearer $TOKEN"
```

## Posts

### Create a post

Publish immediately (omit `scheduledAt`) or schedule for later:

```bash
curl -X POST https://socialcannon.app/api/v1/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "<account_id>",
    "content": "Your post text here",
    "mediaUrls": ["https://example.com/image.jpg"],
    "scheduledAt": "2026-04-15T10:00:00Z",
    "platformOptions": {
      "autoUtm": true
    }
  }'
```

Fields:
- `accountId` (required) — ID from the accounts list
- `content` (required) — post text
- `mediaUrls` (optional) — array of public image/video URLs
- `scheduledAt` (optional) — ISO 8601 datetime, `"optimal"` (auto-pick best time based on engagement data, Pro), or omit for immediate publish
- `platformOptions.autoUtm` (optional) — auto-tag URLs with UTM parameters
- `platformOptions.mediaType` (optional) — controls content type:
  - `"reel"` — Facebook/Instagram Reel (vertical 9:16 video)
  - `"story"` — Facebook/Instagram/TikTok Story (24h ephemeral)
  - `"short"` — YouTube Short (vertical video ≤60s)
  - `"community"` — YouTube Community post (text/image)

### List posts

```bash
curl "https://socialcannon.app/api/v1/posts?status=published&platform=twitter&limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

Query params: `status` (draft/scheduled/published/failed), `platform`, `accountId`, `limit`, `cursor`

### Get a single post

```bash
curl https://socialcannon.app/api/v1/posts/<post_id> \
  -H "Authorization: Bearer $TOKEN"
```

### Update a draft or scheduled post

```bash
curl -X PATCH https://socialcannon.app/api/v1/posts/<post_id> \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Updated text",
    "scheduledAt": "2026-04-16T14:00:00Z",
    "platformOptions": { "autoUtm": true }
  }'
```

Fields: `content`, `scheduledAt`, `platformOptions` — all optional.

### Delete a post

```bash
curl -X DELETE https://socialcannon.app/api/v1/posts/<post_id> \
  -H "Authorization: Bearer $TOKEN"
```

If the post is published, this also attempts to delete it from the social platform.

### Retry a failed post

```bash
curl -X POST https://socialcannon.app/api/v1/posts/<post_id>/retry \
  -H "Authorization: Bearer $TOKEN"
```

Resets the failed post and attempts to publish immediately. No body needed. If it fails again, the post returns to `failed` status with the new error.

## Threads & Carousels

Create multi-part threads (Twitter reply chains, Instagram carousels, LinkedIn multi-segment posts):

```bash
curl -X POST https://socialcannon.app/api/v1/posts/thread \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "<account_id>",
    "items": [
      { "content": "Thread part 1 — the hook" },
      { "content": "Thread part 2 — the detail" },
      { "content": "Thread part 3 — the CTA", "mediaUrls": ["https://..."] }
    ],
    "scheduledAt": "2026-04-15T10:00:00Z",
    "platformOptions": { "autoUtm": true }
  }'
```

Fields: `accountId` (required), `items` (required, min 2, max 25), `scheduledAt` (optional), `platformOptions` (optional). Instagram requires media on each item.

## Media Upload

Upload images/videos before creating posts. Max file size: 50MB. Accepted types: JPEG, PNG, GIF, WebP, MP4, QuickTime, WebM.

```bash
curl -X POST https://socialcannon.app/api/v1/media/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@photo.jpg"
```

Response: `{ "data": { "url": "https://...", "filename": "abc123.jpg", "contentType": "image/jpeg", "size": 102400 } }`

Use the returned `url` in the `mediaUrls` field when creating posts. Images are auto-optimized to JPEG.

## Content Calendar

### Get calendar view

See posts grouped by date with gap analysis:

```bash
curl "https://socialcannon.app/api/v1/calendar?startDate=2026-04-01&endDate=2026-04-30" \
  -H "Authorization: Bearer $TOKEN"
```

Returns `posts`, `summary` (totals by status/platform/day), and `gaps` (dates with no posts).

Query params: `startDate` (required), `endDate` (required), `accountId`, `platform`

### Find available slots

```bash
curl "https://socialcannon.app/api/v1/calendar/slots?startDate=2026-04-01&endDate=2026-04-07&slotDurationMinutes=60" \
  -H "Authorization: Bearer $TOKEN"
```

Query params: `startDate` (required), `endDate` (required, max 14-day range), `slotDurationMinutes` (optional, 30-1440, default 60).

Returns `{ slots[], totalSlots, availableSlots, occupiedSlots }`.

## Analytics

### Per-post analytics

Fetch live engagement metrics from the platform:

```bash
curl https://socialcannon.app/api/v1/posts/<post_id>/analytics \
  -H "Authorization: Bearer $TOKEN"
```

Returns: likes, comments, shares, impressions, reach, clicks, engagementRate, plus historical snapshots.

### Aggregate analytics

```bash
curl "https://socialcannon.app/api/v1/analytics/summary?startDate=2026-04-01&endDate=2026-04-30" \
  -H "Authorization: Bearer $TOKEN"
```

Returns totals across all posts for the date range.

### Bulk refresh analytics

```bash
curl -X POST https://socialcannon.app/api/v1/analytics/refresh \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "platform": "twitter", "limit": 20 }'
```

Fields: `postIds` (optional, array of up to 50 post IDs to refresh), `platform` (optional, filter), `limit` (optional, default 20, max 50). If `postIds` is provided, those specific posts are refreshed; otherwise recent published posts are refreshed.

## Engagements (Comment Inbox)

### List engagements

```bash
curl "https://socialcannon.app/api/v1/engagements?isRead=false&limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

Query params: `postId`, `isRead` (true/false), `limit`, `cursor`

### Fetch engagements for a post

```bash
curl "https://socialcannon.app/api/v1/posts/<post_id>/engagements?cursor=<next_cursor>" \
  -H "Authorization: Bearer $TOKEN"
```

Fetches fresh comments from the platform and stores them. Supports `cursor` for pagination.

### Mark as read

```bash
curl -X PATCH https://socialcannon.app/api/v1/engagements/<engagement_id> \
  -H "Authorization: Bearer $TOKEN"
```

Marks the engagement as read. No request body needed — the endpoint auto-marks on PATCH.

### Reply to an engagement

```bash
curl -X POST https://socialcannon.app/api/v1/engagements/<engagement_id>/reply \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "content": "Thanks for the feedback!" }'
```

Posts the reply directly on the social platform.

## AI Content Repurposing

Adapt content for multiple platforms using AI. Two modes available:

### Preview mode (default) — adapt and return variants for review:

```bash
curl -X POST https://socialcannon.app/api/v1/posts/repurpose \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sourceContent": "Your long-form content here...",
    "targetPlatforms": ["twitter", "facebook", "tiktok"],
    "mode": "preview",
    "tone": "professional"
  }'
```

Returns `{ "variants": [{ "platform", "content", "validation", "characterCount" }], "allValid" }`.

### Post mode — adapt and publish in one call:

```bash
curl -X POST https://socialcannon.app/api/v1/posts/repurpose \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sourceContent": "Your content here...",
    "targetPlatforms": ["twitter", "facebook"],
    "mode": "post",
    "accountIds": { "twitter": "acc_123", "facebook": "acc_456" },
    "mediaUrls": { "twitter": ["https://example.com/video.mp4"] },
    "appendContent": { "twitter": "Links or extra text for Twitter only" },
    "appendToAll": "Text appended to all platforms"
  }'
```

Returns `{ "results": [{ "platform", "success", "postUrl?", "error?" }] }`.

All content is humanized automatically to remove AI writing patterns. Trusted clients bypass tier limits.

## A/B Testing (Pro)

### Create a test

```bash
curl -X POST https://socialcannon.app/api/v1/ab-tests \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "<account_id>",
    "name": "CTA test",
    "variants": [
      { "content": "Check out our new feature!", "mediaUrls": ["https://..."] },
      { "content": "You won'\''t believe this new feature..." }
    ],
    "metric": "engagementRate",
    "minDurationHours": 24,
    "scheduledAt": "2026-04-20T10:00:00Z"
  }'
```

**Publish behavior matches `POST /api/v1/posts`:**
- **Omit `scheduledAt`** → all variants publish **immediately** to the platform via the social adapter
- **Provide `scheduledAt`** → all variants are **scheduled** for that time (must be within 30 days; cron publishes them hourly)

Each variant is a separate post record. Auto-completes after `minDurationHours` and the winner is determined by the chosen metric. Per-variant `mediaUrls` is optional.

**Partial failure semantics:** if ANY variant fails to publish during immediate mode, the endpoint returns **HTTP 502** and the failed variants are marked with `status: 'failed'`. The A/B test record is still created, but the winner comparison at completion only considers successfully published variants. Inspect each variant's post status before relying on test results.

### Get test results

```bash
curl https://socialcannon.app/api/v1/ab-tests/<test_id> \
  -H "Authorization: Bearer $TOKEN"
```

Returns per-variant metrics, current winner, and confidence score.

### List tests

```bash
curl "https://socialcannon.app/api/v1/ab-tests?status=active" \
  -H "Authorization: Bearer $TOKEN"
```

### Force-complete a test

```bash
curl -X POST https://socialcannon.app/api/v1/ab-tests/<test_id>/complete \
  -H "Authorization: Bearer $TOKEN"
```

## Timing Suggestions (Pro)

### Get recommended posting times

```bash
curl "https://socialcannon.app/api/v1/accounts/<account_id>/timing?timezone=UTC-5" \
  -H "Authorization: Bearer $TOKEN"
```

Returns top 5 time slots ranked by average engagement rate with confidence scores.

### Find the single best available slot

Combines engagement data with calendar availability:

```bash
curl "https://socialcannon.app/api/v1/timing/optimal-slot?accountId=<account_id>&timezone=UTC-5" \
  -H "Authorization: Bearer $TOKEN"
```

Returns the next open slot ranked by historical performance.

### Auto-schedule multiple posts

Distribute posts across optimal time slots for the next 7 days:

```bash
curl -X POST https://socialcannon.app/api/v1/posts/auto-schedule \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "<account_id>",
    "posts": [
      { "content": "Post 1 text" },
      { "content": "Post 2 text", "mediaUrls": ["https://..."] },
      { "content": "Post 3 text" }
    ],
    "timezone": "UTC-5"
  }'
```

Max 20 posts per request. Each post gets a unique slot. Returns `{ scheduled: [...], unscheduled: [...], summary: {...} }`.

## UTM Link Tracking

Generate UTM-tagged URLs:

```bash
curl -X POST https://socialcannon.app/api/v1/links/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/product",
    "platform": "twitter",
    "campaign": "spring-launch",
    "content": "hero-cta",
    "postId": "<post_id>",
    "save": true
  }'
```

Fields: `url` (required), `platform` (optional — sets `utm_source`), `campaign` (optional — `utm_campaign`), `content` (optional — `utm_content`), `term` (optional — `utm_term`), `postId` (optional — link to a post), `save` (optional, default true — persist to tracked_links).

### List tracked links

```bash
curl "https://socialcannon.app/api/v1/links?postId=<post_id>&platform=twitter&limit=20&cursor=<cursor>" \
  -H "Authorization: Bearer $TOKEN"
```

Query params: `postId`, `platform`, `limit`, `cursor` — all optional.

## Platforms

List supported platforms and their capabilities (public, no auth required):

```bash
curl https://socialcannon.app/api/v1/platforms
```

## Platform-Specific Notes

### Twitter/X
- 280 char limit. Up to 4 images. Threads via reply chains.

### Facebook
- 63,206 char limit. Supports native scheduling. Page-level tokens.
- **Reels**: Set `platformOptions.mediaType` to `"reel"`. Video must be MP4/MOV, vertical (9:16). Without this, videos post as regular video posts.
- **Stories**: Set `platformOptions.mediaType` to `"story"`. Supports one image or video. Ephemeral (24h).

```bash
curl -X POST https://socialcannon.app/api/v1/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "<account_id>",
    "content": "Check out this tutorial!",
    "mediaUrls": ["https://example.com/video.mp4"],
    "platformOptions": {
      "mediaType": "reel"
    }
  }'
```

### Instagram
- Requires media (no text-only). Max 10 carousel items. No API deletion.
- **Stories**: Set `platformOptions.mediaType` to `"story"`. One image or video.
- **Reels**: Set `platformOptions.mediaType` to `"reel"`. Vertical 9:16 video.

### LinkedIn
- 3,000 char limit. Visibility: PUBLIC or CONNECTIONS. 2-step image upload.

### TikTok
- Requires media — no text-only posts. Supports video, photo carousel (up to 35 images), and Stories.
- **Stories**: Set `platformOptions.mediaType` to `"story"`. One video. Ephemeral (24h).
- Video publish uses async poll model. No API deletion support.

### YouTube
- Supports regular videos, Shorts, and Community posts. Native scheduling support.
- **Shorts**: Set `platformOptions.mediaType` to `"short"`. Vertical video ≤60s.
- **Community posts**: Set `platformOptions.mediaType` to `"community"`. Text/image post to channel's Community tab.
- Scheduled videos are uploaded as private with a `publishAt` timestamp.

## Rate Limits

- Free tier: 60 requests/minute
- Pro tier: 300 requests/minute
- Returns `429` with `Retry-After` header when exceeded

## Support

If you run into issues with the API, account connections, or integration setup, contact **support@socialcannon.app**.

## Tips for Agents

1. Always list accounts first to get valid `accountId` values before creating posts.
2. Use the calendar endpoint to check for gaps before suggesting new posts.
3. For Instagram and TikTok, always include at least one media URL — text-only posts will fail.
4. Use `autoUtm: true` in `platformOptions` to automatically tag URLs in posts.
5. Check analytics after 24+ hours for meaningful engagement data.
6. When repurposing content, review the returned `validation` field — if `valid` is false, adjust the content before publishing.
7. Use `scheduledAt: "optimal"` to let SocialCannon pick the best posting time automatically (Pro).
8. For batch scheduling, use the auto-schedule endpoint instead of creating posts one by one.
9. For YouTube, set `mediaType` to `"short"` for Shorts or `"community"` for Community tab posts.
