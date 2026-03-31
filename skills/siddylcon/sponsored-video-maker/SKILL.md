---
name: sponsored-video-maker
version: "1.0.0"
displayName: "Sponsored Video Maker — Create Professional Brand Sponsorship Content with AI"
description: >
  Create professional sponsored content and brand partnership videos with AI — produce sponsor integration segments, dedicated brand videos, product placement content, media kit pitch videos, and sponsor deliverable compilations. NemoVideo handles the complete sponsorship content workflow: script integration that feels natural (not salesy), product demonstration segments, branded overlay graphics, sponsor disclosure compliance, multi-format deliverables (long-form segment + Shorts + Stories), and performance-optimized CTA placement. Sponsored content creator, brand deal video maker, influencer partnership tool, sponsor integration, brand collaboration video, UGC creator tool.
metadata: {"openclaw": {"emoji": "🤝", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Sponsored Video Maker — Brand Deals That Feel Like Content, Not Commercials

The difference between a sponsored video that earns $500 and one that earns $5,000 is not audience size — it is deliverable quality. Brands pay premium rates for creators who produce sponsored content that looks and feels like organic content: natural product integration, genuine enthusiasm, production quality that matches or exceeds regular uploads, and deliverables across multiple formats (main video, Shorts, Stories, static posts). The creator who delivers a single awkward 60-second read gets the base rate. The creator who delivers a polished integration segment plus 3 Shorts clips plus an Instagram Story sequence plus analytics screenshots gets the premium package rate — often 3-5x the base. NemoVideo produces the full sponsorship deliverable package from a brand brief: the main integration segment (scripted naturally, produced at channel quality), dedicated brand content (product review or demonstration), companion Shorts and Stories (reformatted highlights), media kit updates (channel stats visualized), and performance reports (post-campaign analytics presented as shareable visuals). Every deliverable brands expect, produced at the quality level that commands premium rates.

## Use Cases

1. **Integrated Sponsor Segment — Natural Mid-Video Read (60-120s)** — A tech creator has a $2,000 sponsor deal for a VPN. The brand brief requires: product mention, 3 key features, discount code, and CTA. NemoVideo scripts the integration to match the creator's natural speaking style: opens with a personal use case ("I've been using [VPN] for 3 months while traveling..."), demonstrates 3 features through actual screen recordings, transitions naturally from and back to the main content, places the discount code as a persistent lower-third overlay (not just a verbal mention), and adds a branded but unobtrusive end card. The integration feels like a genuine recommendation, not an interruption.
2. **Dedicated Brand Video — Full Product Review (5-15 min)** — A beauty creator is paid $5,000 for a dedicated video about a skincare line. NemoVideo produces: hook optimized for non-fans ("I tested this for 30 days and here's what happened"), structured review (unboxing → first impression → daily use montage → 30-day results with before/after), product shots with branded lighting and color grade, honest tone (acknowledging one minor drawback builds credibility for the positive claims), multiple CTA placements at natural decision points, and a companion set of 3 Shorts clips for the brand's social channels. The dedicated video that justifies premium pricing.
3. **Media Kit Pitch — Channel Showcase for Brand Outreach (60-90s)** — A creator with 100K followers wants to proactively pitch brands. NemoVideo creates: a 90-second visual media kit (channel overview → audience demographics as animated infographics → engagement metrics as animated counters → content samples → previous brand partnerships → rate card → contact CTA), professional voiceover, branded music, and export as both video (for email pitches and website) and PDF (for formal proposals). The pitch video that gets responses from brand partnership managers.
4. **UGC Package — User-Generated Content for Brand Ads (multiple)** — A brand hires a creator to produce 5 UGC-style videos for their paid ad campaigns. NemoVideo produces: 5 variations of authentic-feeling product testimonials (different angles, different hooks, different messaging emphasis), each in 3 formats (9:16 for TikTok ads, 1:1 for Facebook ads, 16:9 for YouTube pre-roll), with and without captions, with and without branded end cards. 30 total deliverable files from 5 content concepts — the deliverable volume that makes UGC deals profitable for creators.
5. **Sponsor Deliverable Report — Post-Campaign Results (60s)** — After a sponsored video publishes, the brand wants performance data. NemoVideo creates: a 60-second results video (views animated counter, engagement rate chart, click-through stats, audience demographics reached, comment sentiment highlights), formatted as a polished report the brand can share internally. The deliverable that gets the creator re-hired for the next campaign.

## How It Works

### Step 1 — Input Brand Brief
The sponsor's requirements: product name, key messages, required disclosures, CTA (link/code), content format preferences, and deliverable list.

### Step 2 — Set Creator Style
Your channel's tone, editing style, audience expectations, and content format so the sponsored content matches your organic content quality.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "sponsored-video-maker",
    "prompt": "Create a 90-second sponsor integration segment for NordVPN in a tech review video. Style: natural conversational (not scripted-sounding). Key messages: (1) works on all devices, (2) 5,900+ servers in 60 countries, (3) Threat Protection blocks malware. Discount: nordvpn.com/creator — 70%% off + 4 months free. Integration approach: creator traveling and using hotel WiFi as the natural entry point. Show: phone app connecting to server, laptop speed test, Threat Protection blocking a sketchy site. Disclosure: #ad in first 3 seconds as text overlay. Also generate 2 Shorts clips (30s each) highlighting one feature each for brand social channels.",
    "brand": "NordVPN",
    "key_messages": ["all devices", "5900+ servers 60 countries", "Threat Protection malware block"],
    "cta": {"url": "nordvpn.com/creator", "offer": "70%% off + 4 months free"},
    "disclosure": "#ad",
    "creator_style": "conversational-tech",
    "deliverables": ["integration-segment", "shorts-clips"],
    "shorts_count": 2
  }'
```

### Step 4 — Review Deliverables
Verify: brand messaging is accurate, integration feels natural, disclosure is compliant, CTA is clear. Send deliverables to brand for approval. Publish.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Brand brief and integration concept |
| `brand` | string | | Brand/product name |
| `key_messages` | array | | Required talking points |
| `cta` | object | | {url, offer, code} |
| `disclosure` | string | | "#ad", "#sponsored", "Paid partnership" |
| `creator_style` | string | | "conversational", "professional", "energetic", "educational" |
| `deliverables` | array | | ["integration-segment", "dedicated-video", "shorts-clips", "stories", "media-kit", "ugc-package"] |
| `shorts_count` | integer | | Number of Shorts clips |
| `ugc_variations` | integer | | Number of UGC ad variations |
| `formats` | array | | ["16:9", "9:16", "1:1"] |

## Output Example

```json
{
  "job_id": "svm-20260328-001",
  "status": "completed",
  "brand": "NordVPN",
  "deliverables": {
    "integration_segment": {
      "file": "nordvpn-integration-90s.mp4",
      "duration": "1:28",
      "disclosure": "#ad overlay at 0:00-0:03",
      "cta_placements": 2
    },
    "shorts_clips": [
      {"file": "nordvpn-short-1-alldevices.mp4", "duration": "0:30", "feature": "all devices"},
      {"file": "nordvpn-short-2-protection.mp4", "duration": "0:28", "feature": "Threat Protection"}
    ]
  },
  "compliance": {
    "ftc_disclosure": "present",
    "brand_messages": "3/3 covered",
    "cta_visible": true
  }
}
```

## Tips

1. **Natural integration outperforms scripted reads by 3-5x in click-through** — When the sponsor mention feels like a genuine recommendation from personal experience, viewers click. When it feels like an ad break, viewers skip. Start every integration with a personal story, not a feature list.
2. **Multi-format deliverables justify 2-3x rate increases** — A creator who delivers one video segment gets the base rate. A creator who delivers the main segment + 3 Shorts + Stories + a results report gets premium packaging pricing. The additional effort is minimal with AI; the rate increase is substantial.
3. **Disclosure in the first 3 seconds builds trust** — Hiding the #ad disclosure or burying it at the end makes the audience feel deceived when they realize it is sponsored. Upfront disclosure paradoxically increases credibility — the viewer knows it is a paid promotion and still watches because the content is genuinely useful.
4. **UGC creation is the highest-margin sponsorship work** — Brands pay $200-1000 per UGC video for their ad campaigns. Creating 5 variations in one session with AI produces $1,000-5,000 in deliverables from minimal time investment. The brand gets authentic-feeling ad content; the creator gets high-margin work.
5. **Post-campaign reports get you re-hired** — Most creators deliver the video and disappear. Sending a polished performance report 7 days after publishing demonstrates professionalism and gives the brand shareable results for their internal team. This single deliverable is the #1 driver of repeat deals.

## Output Formats

| Format | Content | Use Case |
|--------|---------|----------|
| MP4 16:9 | Integration segment | YouTube main video |
| MP4 9:16 | Shorts / Stories | TikTok / Instagram |
| MP4 1:1 | Social clips | Instagram / Facebook ads |
| PDF | Media kit | Brand outreach |
| PNG | Thumbnail / overlay | Video elements |

## Related Skills

- [ai-video-monetization](/skills/ai-video-monetization) — Monetization strategy
- [affiliate-video-creator](/skills/affiliate-video-creator) — Affiliate content
- [video-ad-maker](/skills/video-ad-maker) — Video ads
