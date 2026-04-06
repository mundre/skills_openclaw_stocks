---
name: awareness-campaign-video
version: "1.1.0"
displayName: "Awareness Campaign Video — Create Social Impact and Cause Marketing Videos with AI"
description: >
  Create social impact, cause marketing, and awareness campaign videos with AI — produce emotionally compelling videos for nonprofits, NGOs, social enterprises, advocacy groups, and brands with purpose-driven messaging. NemoVideo builds complete campaign video: combine personal stories with data visualization, layer testimonials from affected communities with expert commentary, add urgent call-to-action overlays, score with music that balances gravity and hope, create shareable social clips that spread the message, and export for fundraising pages social media email campaigns and event presentations. Awareness campaign video maker, cause marketing video, nonprofit video creator, social impact video AI, advocacy video maker, fundraising video tool, charity video creator, PSA video maker, social cause video.
metadata: {"openclaw": {"emoji": "📢", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Awareness Campaign Video — Make People Care. Then Make Them Act.

Awareness campaigns succeed or fail on emotional connection. Data alone does not change behavior — "1 in 4 adults experience mental health challenges" is a statistic that informs. A 90-second video of a real person describing their experience while their family watches with tears is a story that transforms. The most successful awareness campaigns in history (Ice Bucket Challenge, #MeToo, Kony 2012, Dove Real Beauty) all centered on video that made abstract issues personal, visible, and emotionally undeniable. The production challenge for nonprofits and advocacy organizations is acute. Budgets are constrained — every dollar spent on video production is a dollar not spent on the mission. Staff are stretched thin — the communications director also manages social media, email, events, and press. Professional video production ($5,000-50,000 per campaign video) is often the first line item cut from already-tight budgets. Yet the organizations with the most important messages to share are the least equipped to produce the videos that would spread those messages. NemoVideo enables mission-driven organizations to produce broadcast-quality campaign video from the resources they already have: phone-recorded testimonials from the people they serve, data from their impact reports, photos from their programs, and the passion of their team. Upload raw materials and NemoVideo produces an emotionally compelling, professionally structured campaign video that moves viewers from awareness to understanding to action.

## Use Cases

1. **Personal Story Campaign — Testimonial-Driven Awareness (60-180s)** — A mental health organization wants to reduce stigma by sharing real stories. Three people recorded phone testimonials about their experience. NemoVideo: structures the testimonials into a narrative arc (isolation → reaching out → recovery → advocacy), intercuts the three stories by theme (not one after another — weaving creates the message that this experience is universal), applies sensitive color grading (warm but not cheerful — acknowledging the gravity while communicating hope), adds statistical context overlays at key moments ("1 in 4 adults will experience a mental health condition this year" appearing as a speaker describes feeling alone), layers a music score that balances emotional gravity with forward momentum (not sad — determined), adds the organization's branding and CTA ("You are not alone. Text HOME to 741741"), and produces a video that makes stigma feel like the barrier it is and help feel as accessible as it should be.

2. **Data-Driven Impact Video — Statistics That Move (60-120s)** — An environmental organization needs to communicate climate data in a way that creates urgency rather than numbness. NemoVideo: transforms raw statistics into animated data visualizations that create visceral impact (a temperature chart that visually accelerates, a glacier timelapse that shows 50 years of retreat in 10 seconds, a counter showing species lost per day ticking in real time), pairs each data visualization with a corresponding real-world image (the temperature chart dissolves into footage of drought, the glacier chart dissolves into footage of flooding), adds narration that connects abstract numbers to human experience ("That number means 3 million families lost their homes last year"), scores with music that creates urgency without despair (the balance between "this is dire" and "action is possible"), and ends with a concrete action CTA ("Donate / Sign / Share / Contact your representative"). Data that moves people because it connects statistics to human lives.

3. **Fundraising Campaign Video — Donate Button Conversion (90-120s)** — A nonprofit's annual fundraising campaign needs a video for the donation page, email campaign, and social media. NemoVideo: opens with a specific, relatable story (one person or family whose life was changed by the organization — not abstract mission statement), shows the problem they faced (empathy-building), shows the organization's intervention (credibility-building), shows the outcome (hope-building), connects the individual story to the broader need ("Maria's story is just one of 50,000 families we serve"), adds impact metrics as animated graphics ("$25 provides school supplies for one child for a year"), and closes with a direct, urgent CTA with the donate mechanism visible on screen. The fundraising video structure proven to maximize conversion: specific story → broader context → concrete ask → easy action.

4. **Advocacy Campaign — Issue Mobilization (2-5 min)** — A policy advocacy organization needs to mobilize public support for legislation. NemoVideo: structures as a persuasion narrative (the issue explained simply → who is affected → what the proposed solution is → what the viewer can do), intercuts expert voices with affected community voices (credibility + emotion), visualizes the policy proposal as clear, simple graphics (not legalese — visual representation of what changes and who benefits), adds geographic data (map showing affected communities, districts of key legislators), creates urgency through timeline overlays ("The vote is in 30 days"), and produces both a full-length video for engaged supporters and 30-second social clips for broad distribution. Advocacy content that turns complex policy into clear citizen action.

5. **Awareness Day Content — Calendar-Driven Campaign (15-60s each)** — An organization needs content for awareness days and months: World Mental Health Day, Breast Cancer Awareness Month, Earth Day, Pride Month, International Women's Day. NemoVideo: creates day-specific social content (shareable 30-60 second videos optimized for each platform), incorporates the awareness day's visual identity (official colors, symbols, hashtags), features relevant stories or data tied to the specific observance, adds the organization's unique perspective and contribution to the cause, and produces a batch of platform-specific content (9:16 for TikTok/Reels, 1:1 for feed, 16:9 for YouTube). Calendar-driven awareness content that keeps the organization visible and relevant throughout the year.

## How It Works

### Step 1 — Upload Campaign Materials
Personal story recordings, impact data, program photos, community footage, expert interviews, or any combination. Raw phone recordings are expected and welcomed.

### Step 2 — Choose Campaign Type
Personal story, data-driven impact, fundraising, advocacy, or awareness day content. Define the desired audience action.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "awareness-campaign-video",
    "prompt": "Create a 90-second fundraising video for a food bank annual campaign. Sources: 3-minute phone testimonial from a mother describing how the food bank helped her family during unemployment, 10 photos of volunteers and food distribution, impact data (2.4 million meals served last year, 15,000 families supported, $1 = 4 meals). Structure: open with the mother story (specific, personal — 30s), expand to the broader need (data visualization — 20s), show the solution in action (volunteer photos with Ken Burns — 15s), concrete ask (what donations accomplish — 15s), CTA (donate now + website — 10s). Music: warm, community-feeling, hopeful but grounded. Color grade: warm documentary. Lower third for the mother. Animated stat graphics. Export 16:9 for donation page, 9:16 for Instagram fundraising story, 1:1 for Facebook post.",
    "campaign_type": "fundraising",
    "target_duration": "90s",
    "structure": ["personal-story", "data-expansion", "solution-action", "concrete-ask", "cta"],
    "impact_data": {
      "meals_served": "2.4 million",
      "families": "15,000",
      "dollar_impact": "$1 = 4 meals"
    },
    "music": "warm-hopeful-community",
    "color_grade": "warm-documentary",
    "cta": {"text": "Donate Now", "url": "foodbank.org/give"},
    "formats": ["16:9", "9:16", "1:1"]
  }'
```

### Step 4 — Review Emotional Calibration
Watch as a potential donor would. Check: the personal story creates genuine empathy (not pity — empathy), the data creates urgency (not overwhelm), the CTA feels like a natural next step (not a guilt-trip). The emotional calibration — balancing gravity with hope, urgency with agency — is what separates effective campaign video from manipulative or depressing content.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Campaign video description |
| `campaign_type` | string | | "personal-story", "data-driven", "fundraising", "advocacy", "awareness-day" |
| `target_duration` | string | | Target video length |
| `structure` | array | | Narrative structure sequence |
| `impact_data` | object | | Key statistics for visualization |
| `cta` | object | | {text, url, action} call to action |
| `music` | string | | Emotional tone for scoring |
| `color_grade` | string | | "warm-documentary", "urgent", "hopeful-bright" |
| `advocacy` | object | | {issue, legislation, action, deadline} |
| `awareness_day` | object | | {name, date, colors, hashtag} |
| `formats` | array | | ["16:9", "9:16", "1:1"] |
| `batch` | boolean | | Multiple awareness day videos |

## Output Example

```json
{
  "job_id": "awcmp-20260329-001",
  "status": "completed",
  "campaign_type": "fundraising",
  "duration": "1:28",
  "emotional_arc": "empathy → urgency → hope → action",
  "data_visualizations": 3,
  "outputs": {
    "donation_page": {"file": "foodbank-campaign-16x9.mp4", "resolution": "1920x1080"},
    "instagram": {"file": "foodbank-campaign-9x16.mp4", "resolution": "1080x1920"},
    "facebook": {"file": "foodbank-campaign-1x1.mp4", "resolution": "1080x1080"}
  }
}
```

## Tips

1. **One specific story outperforms a thousand statistics** — "Maria, a single mother of three, lost her job in January. For two months, the food bank was the only thing between her family and hunger." This creates more donor action than "We served 2.4 million meals last year." Use the specific story as the emotional entry point, then expand with data.
2. **Hope must outweigh gravity in fundraising video** — A video that only shows suffering creates compassion fatigue, not donations. The emotional arc must move from problem (gravity) through solution (hope) to action (agency). The viewer must end feeling empowered to help, not helpless in the face of need.
3. **"$1 = 4 meals" is the donation catalyst** — Concrete impact ratios (what a specific donation amount accomplishes) convert more donors than abstract asks. Animated stat graphics showing "$25 provides school supplies for one child for a year" give the donor a mental image of their specific impact.
4. **Social clips drive awareness; the full video drives action** — A 30-second clip on TikTok reaches people who have never heard of the cause. The full 90-second video on the donation page converts people who are already interested. Both are necessary; they serve different funnel stages.
5. **Music calibration is the difference between effective and manipulative** — Sad piano over suffering footage feels manipulative. Warm, determined music over the same footage feels respectful. The music communicates whether the organization sees its community as victims to pity or people to stand alongside.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p | Website / YouTube / presentation / email |
| MP4 9:16 | 1080x1920 | Instagram Stories / TikTok / Reels |
| MP4 1:1 | 1080x1080 | Facebook / Instagram Feed / LinkedIn |

## Related Skills

- [ai-video-caption-generator](/skills/ai-video-caption-generator) — Campaign captions
- [ai-video-text-overlay](/skills/ai-video-text-overlay) — Impact stat graphics
- [ai-video-thumbnail-maker](/skills/ai-video-thumbnail-maker) — Campaign thumbnails
- [ai-video-outro-maker](/skills/ai-video-outro-maker) — CTA end screens

## Frequently Asked Questions

**Can I create campaign videos in multiple languages?** — Yes. NemoVideo generates AI voiceover narration and translates text overlays into 50+ languages. Multi-language versions of the same campaign reach global audiences and diaspora communities. Subtitle translations are also available for maintaining the original speaker's voice while reaching new language audiences.

**Is there a nonprofit discount?** — NemoVideo's AI-powered production makes professional campaign video accessible at a fraction of traditional production costs. The savings come from the technology itself — no agency fees, no production crew, no weeks of post-production. Every organization, regardless of budget, can produce broadcast-quality awareness content.
