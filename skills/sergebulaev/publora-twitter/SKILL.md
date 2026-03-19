---
name: publora-twitter
description: >
  Post or schedule content to X (Twitter) using the Publora API. Use this skill
  when the user wants to tweet, schedule a tweet, or post a thread to X/Twitter
  via Publora.
---

# Publora — X / Twitter

X/Twitter platform skill for the Publora API. For auth, core scheduling, media upload, and workspace/webhook docs, see the `publora` core skill.

**Base URL:** `https://api.publora.com/api/v1`  
**Header:** `x-publora-key: sk_YOUR_KEY`  
**Platform ID format:** `twitter-{userId}`

## Platform Limits (API)

> ⚠️ API limits differ from native app. Design against these.

| Property | API Limit | Notes |
|----------|-----------|-------|
| Text | **280 characters** | 25,000 with Premium account |
| Images | Up to **4** × 5 MB | JPEG, PNG, GIF, WebP |
| Video | **2 min (120s)** / 512 MB | ⚠️ Native allows 2:20 — API is stricter |
| Video format | MP4, MOV | — |
| Threading | ✅ Auto-split with `---` | — |
| Text only | ✅ Yes | — |

**Common errors:**
- `This user is not allowed to post a video longer than 2 minutes` — trim video to under 120s

## Post a Tweet

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Just shipped a new feature! 🚀 #buildinpublic',
    platforms: ['twitter-123456789']
  })
});
```

## Post a Thread

Separate tweets with `---` on its own line:

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: '1/ Here is everything I learned building in public this year.\n\n---\n\n2/ First lesson: ship early, learn fast. Don\'t wait for perfect.\n\n---\n\n3/ Second lesson: your audience is your best product team. Listen to them.',
    platforms: ['twitter-123456789']
  })
});
```

Each `---` separator creates a new tweet in the thread, linked automatically.

## Schedule a Tweet

```javascript
body: JSON.stringify({
  content: 'Scheduled announcement: our product launches tomorrow! 🎉',
  platforms: ['twitter-123456789'],
  scheduledTime: '2026-03-20T14:00:00.000Z'
})
```

## Tweet with Image

Upload image via the 3-step media workflow (see `publora` core skill), then the image attaches to the post automatically via `postGroupId`.

## Platform Quirks

- **API video limit is 2 min** — not 2:20 like the native app. Videos over 120s will fail.
- **PNG images** are supported unlike Instagram
- **Threads**: auto-splitting via `---` separator works reliably on Twitter
- **Premium accounts** get 25,000 character limit — Publora will use the extended limit if your account is Premium
- **GIF posts** count as a video, not an image — different size/count rules apply
