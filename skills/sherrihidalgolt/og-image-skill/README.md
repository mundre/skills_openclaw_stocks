# OG Image Generator

Generate stunning **open graph social media preview images** from a text description using AI. Get back a direct image URL instantly — no UI required.

Powered by the [Neta / talesofai](https://talesofai.cn) image generation API.

---

## Install

**Via npx skills:**
```bash
npx skills add SherriHidalgolt/og-image-skill
```

**Via ClawHub:**
```bash
clawhub install og-image-skill
```

---

## Usage

```bash
# Basic — uses the default prompt
node ogimage.js

# Custom prompt
node ogimage.js "dark tech blog banner, neon accents, minimal layout"

# Specify size
node ogimage.js "product launch card" --size square

# Use a reference image (by picture UUID)
node ogimage.js "similar style banner" --ref <picture_uuid>

# Pass token explicitly
node ogimage.js "my prompt" --token sk-xxxx
```

The script prints the image URL to stdout on success:
```
https://cdn.talesofai.cn/artifacts/....png
```

---

## Options

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--size` | `square`, `portrait`, `landscape`, `tall` | `landscape` | Output image dimensions |
| `--token` | string | — | API token (overrides env/file lookup) |
| `--ref` | picture UUID | — | Reference image UUID for style inheritance |

### Size dimensions

| Name | Width | Height |
|------|-------|--------|
| `square` | 1024 | 1024 |
| `portrait` | 832 | 1216 |
| `landscape` | 1216 | 832 |
| `tall` | 704 | 1408 |

---

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
node ogimage.js "your prompt"
```

Or pass it inline:
```bash
node ogimage.js "your prompt" --token your_token_here
```

> **API endpoint:** defaults to `api.talesofai.com` (Open Platform tokens).  
> China users: set `NETA_API_BASE_URL=https://api.talesofai.com` to use the China endpoint.


---

## Examples

```bash
# OG image for a blog post
node ogimage.js "technology article cover, dark gradient, bold white title text"

# Square social card
node ogimage.js "product announcement, vibrant colors, centered logo" --size square

# Tall Pinterest-style card
node ogimage.js "recipe card, warm tones, food photography style" --size tall
```

---

## Requirements

- Node.js 18+ (uses native `fetch` and top-level `await`)
- A valid `NETA_TOKEN` from [talesofai.cn](https://talesofai.cn)

---

Built with [Claude Code](https://claude.ai/claude-code) · Powered by [Neta](https://www.neta.art/) · [API Docs](https://www.neta.art/open/)