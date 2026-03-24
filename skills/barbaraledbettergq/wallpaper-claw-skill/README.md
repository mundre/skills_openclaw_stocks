# AI Wallpaper Generator

Generate stunning AI-powered wallpaper images from a text description in seconds. Powered by the Neta talesofai API, this skill returns a direct image URL you can use anywhere.

---

## Install

**Via npx skills:**
```bash
npx skills add BarbaraLedbettergq/wallpaper-claw-skill
```

**Via ClawHub:**
```bash
clawhub install wallpaper-claw-skill
```

---

## Usage

```bash
# Use the default prompt
node wallpaperclaw.js

# Custom prompt
node wallpaperclaw.js "misty mountain range at golden hour"

# Specify size
node wallpaperclaw.js "cyberpunk city at night" --size landscape

# Use a reference image UUID
node wallpaperclaw.js "same style, different scene" --ref <picture_uuid>

# Pass token directly
node wallpaperclaw.js "aurora borealis over a frozen lake" --token YOUR_TOKEN
```

The script prints a single image URL to stdout on success.

---

## Options

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--size` | `square`, `portrait`, `landscape`, `tall` | `landscape` | Output image dimensions |
| `--style` | `anime`, `cinematic`, `realistic` | `cinematic` | Visual style (passed in prompt) |
| `--ref` | `<picture_uuid>` | — | Reference image UUID for style inheritance |
| `--token` | `<token>` | — | Override token resolution |

### Size reference

| Name | Dimensions |
|------|------------|
| `square` | 1024 × 1024 |
| `portrait` | 832 × 1216 |
| `landscape` | 1216 × 832 |
| `tall` | 704 × 1408 |

---

## Token setup

The script resolves your `NETA_TOKEN` in this order:

1. `--token` CLI flag
2. `NETA_TOKEN` environment variable
3. `~/.openclaw/workspace/.env` — line matching `NETA_TOKEN=...`
4. `~/developer/clawhouse/.env` — line matching `NETA_TOKEN=...`

**Recommended:** add your token to `~/.openclaw/workspace/.env`:
```
NETA_TOKEN=your_token_here
```

---

## Example output

```
https://cdn.talesofai.cn/artifacts/abc123.jpg
```

## About Neta

[Neta](https://www.neta.art/) (by TalesofAI) is an AI image and video generation platform with a powerful open API. It uses a **credit-based system (AP — Action Points)** where each image generation costs a small number of credits. Subscriptions are available for heavier usage.

### Register & Get Token

| Region | Sign up | Get API token |
|--------|---------|---------------|
| Global | [neta.art](https://www.neta.art/) | [neta.art/open](https://www.neta.art/open/) |
| China  | [nieta.art](https://app.nieta.art/) | [nieta.art/security](https://app.nieta.art/security) |

New accounts receive free credits to get started. No credit card required to try.

### Pricing

Neta uses a pay-per-generation credit model. View current plans on the [pricing page](https://www.neta.art/pricing).

- **Free tier:** limited credits on signup — enough to test
- **Subscription:** monthly AP allowance via Stripe
- **Credit packs:** one-time top-up as needed

### Set up your token

```bash
# Step 1 — get your token:
#   Global: https://www.neta.art/open/
#   China:  https://app.nieta.art/security

# Step 2 — set it
export NETA_TOKEN=your_token_here

# Step 3 — run
node wallpaperclaw.js "your prompt"
```

Or pass it inline:
```bash
node wallpaperclaw.js "your prompt" --token your_token_here
```

> **API endpoint:** defaults to `api.talesofai.cn` (works with all token types).  
> Override with `NETA_API_URL=https://api.talesofai.cn` if using a global Open Platform token.


---

Built with [Claude Code](https://claude.ai/claude-code) · Powered by [Neta](https://www.neta.art/) · [API Docs](https://www.neta.art/open/)