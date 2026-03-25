# FeedTo Skill

OpenClaw skill for [FeedTo.ai](https://feedto.ai) — auto-pull and process feeds with AI.

## Install

```bash
clawhub install feedto
```

## Setup

1. Sign up at [feedto.ai](https://feedto.ai)
2. Copy your API key from [Settings](https://feedto.ai/settings)
3. The skill will prompt for your key on first run, or set it manually in `openclaw.json`:

```json
{
  "skills": {
    "feedto": {
      "config": {
        "FEEDTO_API_KEY": "your-api-key"
      }
    }
  }
}
```

## How it works

Every minute, the skill:
1. Polls FeedTo for pending feeds
2. Relays each feed's content verbatim to the user
3. Marks processed feeds as read

Use the [FeedTo Chrome Extension](https://feedto.ai/setup) to feed content from any webpage.

## Links

- Web app: [feedto.ai](https://feedto.ai)
- Web app repo: [isopenclaw/feedto](https://github.com/isopenclaw/feedto)
- ClawHub: [clawhub.com/skills/feedto](https://clawhub.com/skills/feedto)
