---
name: postsyncer-social-media-assistant
version: 2.0.0
title: Social Media Assistant (via postsyncer.com)
description: Manages social media through PostSyncer using REST API calls. Use when scheduling, posting, or managing content across Instagram, TikTok, YouTube, X (Twitter), LinkedIn, Facebook, Threads, Bluesky, Pinterest, Telegram, Mastodon. Covers posts (create, list, update, delete), media via public URLs, comments (sync, reply, hide, delete), labels, and analytics. Accounts must be pre-connected in the PostSyncer app.
license: MIT
author: PostSyncer <support@postsyncer.com>
homepage: https://postsyncer.com/openclaw
keywords: [social-media, postsyncer, automation, scheduling, instagram, tiktok, youtube, twitter, linkedin, api]
metadata:
  openclaw:
    requires:
      env:
        - POSTSYNCER_API_TOKEN
    primaryEnv: POSTSYNCER_API_TOKEN
---

# PostSyncer Social Media Assistant

Autonomously manage social media through [PostSyncer](https://postsyncer.com) using the REST API.

## Setup

1. Create a PostSyncer account at [app.postsyncer.com](https://app.postsyncer.com)
2. [Connect social profiles](https://app.postsyncer.com/dashboard?action=accounts) (Instagram, TikTok, YouTube, X, LinkedIn, etc.)
3. Go to [**Settings → API Integrations**](https://app.postsyncer.com/dashboard?action=settings&section=api-integrations) and create a personal access token with abilities: `workspaces`, `accounts`, `posts`, `labels`
4. Add to `.env`: `POSTSYNCER_API_TOKEN=your_token`

## How to Make API Calls

All requests go to `https://postsyncer.com/api/v1` with the header:

```
Authorization: Bearer $POSTSYNCER_API_TOKEN
Content-Type: application/json
```

Use `web_fetch`, `curl`, or any HTTP tool available. Always read `$POSTSYNCER_API_TOKEN` from the environment.

---

## API Reference

### Discovery (Call First)

**List Workspaces** — `GET /api/v1/workspaces`

```bash
curl "https://postsyncer.com/api/v1/workspaces" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN"
```

Returns workspaces with `id`, `name`, `slug`, `timezone`.

**List Accounts** — `GET /api/v1/accounts`

```bash
curl "https://postsyncer.com/api/v1/accounts" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN"
```

Returns accounts with `id`, `platform`, `username`, `workspace_id`.

---

### Posts

**List Posts** — `GET /api/v1/posts`

```bash
curl "https://postsyncer.com/api/v1/posts?page=1&per_page=20&include_comments=false" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN"
```

Query params: `page`, `per_page` (max 100), `include_comments` (true/false).

**Get Post** — `GET /api/v1/posts/{id}`

```bash
curl "https://postsyncer.com/api/v1/posts/123" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN"
```

**Create Post** — `POST /api/v1/posts`

```bash
curl -X POST "https://postsyncer.com/api/v1/posts" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": 12,
    "schedule_type": "schedule",
    "content": [{"text": "Caption #hashtags", "media": ["https://example.com/image.jpg"]}],
    "accounts": [{"id": 136}, {"id": 95, "settings": {"board_id": 123}}],
    "schedule_for": {"date": "2026-03-26", "time": "14:30", "timezone": "America/New_York"},
    "labels": [5],
    "repeatable": false
  }'
```

- `schedule_type`: `publish_now` | `schedule` | `draft`
- `schedule_for`: Required when `schedule_type` is `schedule`. Date `YYYY-MM-DD`, time `HH:MM`
- `content`: Array of thread items. Each needs `text` and/or `media` (public HTTPS URLs)
- `accounts`: Array of `{id, settings?}`. Platform-specific options go in `settings`

**Update Post** — `PUT /api/v1/posts/{id}`

```bash
curl -X PUT "https://postsyncer.com/api/v1/posts/123" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": [{"text": "Updated caption"}], "schedule_for": {"date": "2026-03-27", "time": "10:00"}}'
```

Only posts that have not been published yet can be updated.

**Delete Post** — `DELETE /api/v1/posts/{id}` *(confirm with user first)*

```bash
curl -X DELETE "https://postsyncer.com/api/v1/posts/123" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN"
```

---

### Comments

**List Comments** — `GET /api/v1/comments`

```bash
curl -G "https://postsyncer.com/api/v1/comments" \
  --data-urlencode "post_id=123" \
  --data-urlencode "per_page=20" \
  --data-urlencode "include_replies=true" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN"
```

Query params: `post_id` (required), `per_page`, `page`, `include_replies`, `platform`.

**Get Comment** — `GET /api/v1/comments/{id}`

```bash
curl "https://postsyncer.com/api/v1/comments/456" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN"
```

**Create Comment / Reply** — `POST /api/v1/comments`

```bash
curl -X POST "https://postsyncer.com/api/v1/comments" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"post_id": 123, "content": "Reply text", "parent_comment_id": null, "media_urls": []}'
```

**Update Comment** — `PUT /api/v1/comments/{id}`

```bash
curl -X PUT "https://postsyncer.com/api/v1/comments/456" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Updated reply text"}'
```

**Hide Comment** — `POST /api/v1/comments/{id}/hide`

```bash
curl -X POST "https://postsyncer.com/api/v1/comments/456/hide" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN"
```

**Delete Comment** — `DELETE /api/v1/comments/{id}` *(confirm first)*

```bash
curl -X DELETE "https://postsyncer.com/api/v1/comments/456" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN"
```

**Sync Comments from Platforms** — `POST /api/v1/comments/sync`

```bash
curl -X POST "https://postsyncer.com/api/v1/comments/sync" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"post_id": 123}'
```

---

### Labels

**List Labels** — `GET /api/v1/labels`

```bash
curl "https://postsyncer.com/api/v1/labels" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN"
```

**Get Label** — `GET /api/v1/labels/{id}`

**Create Label** — `POST /api/v1/labels`

```bash
curl -X POST "https://postsyncer.com/api/v1/labels" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Campaign 2026", "color": "#3b82f6", "workspace_id": 12}'
```

**Update Label** — `PUT /api/v1/labels/{id}`

**Delete Label** — `DELETE /api/v1/labels/{id}` *(confirm first)*

---

### Analytics

All analytics endpoints require the `posts` API ability.

**All Workspaces** — `GET /api/v1/analytics`

```bash
curl "https://postsyncer.com/api/v1/analytics" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN"
```

**By Workspace** — `GET /api/v1/analytics/workspaces/{workspace_id}`

```bash
curl "https://postsyncer.com/api/v1/analytics/workspaces/12" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN"
```

**By Post** — `GET /api/v1/analytics/posts/{post_id}`

```bash
curl "https://postsyncer.com/api/v1/analytics/posts/123" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN"
```

**By Account** — `GET /api/v1/analytics/accounts/{account_id}`

```bash
curl "https://postsyncer.com/api/v1/analytics/accounts/136" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN"
```

**Sync Post Analytics** — `POST /api/v1/analytics/posts/{post_id}/sync`

```bash
curl -X POST "https://postsyncer.com/api/v1/analytics/posts/123/sync" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN"
```

Queues background jobs to refresh metrics. Does not return metrics directly — call GET after sync.

---

### Account Management

**Delete Account** — `DELETE /api/v1/accounts/{id}` *(destructive, confirm first)*

```bash
curl -X DELETE "https://postsyncer.com/api/v1/accounts/136" \
  -H "Authorization: Bearer $POSTSYNCER_API_TOKEN"
```

---

## Platform-Specific Settings

Pass per-platform options in `accounts[].settings` when creating/updating posts:

**Pinterest:** `{"board_id": 123456}`

**X/Twitter:**
```json
{"reply_settings": "everyone", "for_super_followers_only": false, "quote_tweet_id": null, "reply": {"in_reply_to_tweet_id": null}, "community_id": null, "share_with_followers": true}
```

**TikTok:**
```json
{"privacy_level": "PUBLIC_TO_EVERYONE", "disable_comment": false, "disable_duet": false, "disable_stitch": false, "post_mode": "DIRECT_POST"}
```

**Instagram:** `{"post_type": "POST"}` — options: `REELS`, `STORIES`, `POST`

**YouTube:**
```json
{"video_type": "video", "title": "My Video", "privacyStatus": "public", "notifySubscribers": true}
```

**LinkedIn:** `{"visibility": "PUBLIC"}` — options: `PUBLIC`, `CONNECTIONS`, `LOGGED_IN`

**Bluesky:** `{"website_card": {"uri": "https://...", "title": "...", "description": "..."}}`

**Telegram:** `{"disable_notification": false, "protect_content": false}`

---

## Common Workflows

### Schedule a Post to Multiple Platforms

1. `GET /api/v1/workspaces` → get `workspace_id`
2. `GET /api/v1/accounts` → get `id`s for target platforms
3. `POST /api/v1/posts` with `schedule_type: "schedule"` and `schedule_for`

### Reply to Comments

1. `GET /api/v1/posts` → find post `id`
2. `POST /api/v1/comments/sync` with `post_id`
3. `GET /api/v1/comments?post_id=123&include_replies=true`
4. `POST /api/v1/comments` with `post_id` and optional `parent_comment_id`

### Check Performance

1. `GET /api/v1/analytics/posts/{id}` for a specific post
2. If stale: `POST /api/v1/analytics/posts/{id}/sync`, then re-fetch

---

## Best Practices

- **Always start with** `GET /workspaces` and `GET /accounts` to discover IDs
- **New automations:** Use `schedule_type: "draft"` or confirm before `publish_now`
- **Destructive actions:** State what will happen, confirm before delete operations
- **Multi-network:** One post can target multiple accounts; check per-platform `status` in the response
- **Rate limits:** 60 requests/minute — don't call sync endpoints repeatedly
- **Hashtags:** Keep relevant and limited (3–5 per post)

---

## Error Handling

| Status | Meaning |
|--------|---------|
| `401` | Token missing or invalid |
| `403` | Token lacks required ability (e.g. `posts`) |
| `404` | Resource not found or no access |
| `422` | Validation error — check required fields and formats |
| `429` | Rate limited — wait before retrying |

---

## Links

- [API Documentation](https://docs.postsyncer.com/api-reference/introduction)
- [PostSyncer Dashboard](https://app.postsyncer.com)
- [API Authentication](https://docs.postsyncer.com/essentials/authentication)
