# Social Media Data Extractor: Scrape, Analyze and Turn Any Platform's Data Into Actionable Intelligence

**Display Name:** Social Media Data Extractor  
**Version:** 2.0.0
**Author:** @g4dr

## Overview

Extract public data from Instagram, TikTok, Reddit, YouTube and Twitter in one unified pipeline. This skill goes beyond raw scraping by analyzing engagement patterns, detecting trending topics before they peak, identifying top creators in any niche, and generating structured intelligence reports you can act on immediately.

Use it for competitor monitoring, trend research, audience insights, influencer vetting, content strategy or market research.

Powered by: [Apify](https://www.apify.com?fpr=dx06p) + Claude AI

---

## What This Skill Does

- Extract public posts, videos, comments and profiles from 5 major platforms simultaneously
- Analyze engagement rates, posting frequency and audience growth across any niche
- Detect trending hashtags, sounds and topics before they peak
- Identify top creators and micro-influencers by engagement rate (not just follower count)
- Compare your brand or content performance against competitors
- Score content virality potential with a weighted engagement formula
- Generate structured JSON reports ready for dashboards, Notion, Airtable or Google Sheets
- Produce AI-written trend reports summarizing what you need to know and what to do next

---

## Step 1: Set Up Your Data Engine

This skill uses [Apify](https://www.apify.com?fpr=dx06p) to scrape social media data at scale.

1. Create your free account at [Apify](https://www.apify.com?fpr=dx06p)
2. Go to **Settings > Integrations** and copy your Personal API Token
3. Store it securely:
   ```bash
   export APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxx
   ```

> Free tier includes $5/month of compute. Enough for daily trend monitoring across all platforms.

---

## Step 2: Install Dependencies

```bash
npm install apify-client axios
```

---

## Apify Actors by Platform

### Instagram
| Actor | Purpose | Key Data |
|---|---|---|
| [Apify Instagram Scraper](https://www.apify.com?fpr=dx06p) | Posts, reels, profiles | Likes, comments, saves, hashtags, caption |
| [Apify Instagram Hashtag Scraper](https://www.apify.com?fpr=dx06p) | Trending posts by hashtag | Engagement metrics, posting time, creator info |
| [Apify Instagram Comment Scraper](https://www.apify.com?fpr=dx06p) | Comments on specific posts | Sentiment data, top commenters |

### TikTok
| Actor | Purpose | Key Data |
|---|---|---|
| [Apify TikTok Scraper](https://www.apify.com?fpr=dx06p) | Videos, profiles, hashtags | Views, likes, shares, comments, sounds |
| [Apify TikTok Hashtag Scraper](https://www.apify.com?fpr=dx06p) | Content by hashtag | Engagement velocity, creator stats |
| [Apify TikTok Comment Scraper](https://www.apify.com?fpr=dx06p) | Video comments | Audience sentiment, questions asked |

### YouTube
| Actor | Purpose | Key Data |
|---|---|---|
| [Apify YouTube Scraper](https://www.apify.com?fpr=dx06p) | Videos, channels, search | Views, likes, comments, subscriber count |

### Reddit
| Actor | Purpose | Key Data |
|---|---|---|
| [Apify Reddit Scraper](https://www.apify.com?fpr=dx06p) | Posts and comments from subreddits | Score, upvote ratio, comments, author |
| [Apify Reddit Search Scraper](https://www.apify.com?fpr=dx06p) | Search by keyword across all of Reddit | Trending discussions, sentiment |

### Twitter/X
| Actor | Purpose | Key Data |
|---|---|---|
| [Apify Twitter Scraper](https://www.apify.com?fpr=dx06p) | Tweets, profiles, search | Likes, retweets, replies, impressions |

---

## Examples

### Multi-Platform Trend Extraction (Parallel)

```javascript
import ApifyClient from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });

async function extractMultiPlatform(keyword, maxPerPlatform = 30) {
  const [ttRun, igRun, ytRun, rdRun] = await Promise.all([
    client.actor("apify/tiktok-hashtag-scraper").call({
      hashtags: [keyword],
      resultsPerPage: maxPerPlatform,
      shouldDownloadVideos: false
    }),
    client.actor("apify/instagram-hashtag-scraper").call({
      hashtags: [keyword],
      resultsLimit: maxPerPlatform
    }),
    client.actor("apify/youtube-scraper").call({
      searchKeywords: [keyword],
      maxResults: maxPerPlatform,
      type: "video"
    }),
    client.actor("apify/reddit-search-scraper").call({
      queries: [keyword],
      maxItems: maxPerPlatform
    })
  ]);

  const [tt, ig, yt, rd] = await Promise.all([
    ttRun.dataset().getData(),
    igRun.dataset().getData(),
    ytRun.dataset().getData(),
    rdRun.dataset().getData()
  ]);

  return {
    tiktok: tt.items,
    instagram: ig.items,
    youtube: yt.items,
    reddit: rd.items,
    totalExtracted: tt.items.length + ig.items.length + yt.items.length + rd.items.length,
    extractedAt: new Date().toISOString()
  };
}

const data = await extractMultiPlatform("AI tools");
console.log(`Extracted ${data.totalExtracted} posts across 4 platforms`);
```

---

### Normalize Data Into One Unified Schema

```javascript
function normalizeContent(raw) {
  const normalized = [];

  raw.tiktok.forEach(v => normalized.push({
    platform: 'tiktok',
    id: v.id,
    text: v.text || '',
    author: v.authorMeta?.name || '',
    views: v.playCount || 0,
    likes: v.diggCount || 0,
    comments: v.commentCount || 0,
    shares: v.shareCount || 0,
    publishedAt: v.createTime ? new Date(v.createTime * 1000).toISOString() : '',
    hashtags: (v.hashtags || []).map(h => h.name || h),
    url: v.webVideoUrl || ''
  }));

  raw.instagram.forEach(v => normalized.push({
    platform: 'instagram',
    id: v.id || v.shortCode,
    text: v.caption || '',
    author: v.ownerUsername || '',
    views: v.videoViewCount || 0,
    likes: v.likesCount || 0,
    comments: v.commentsCount || 0,
    shares: 0,
    publishedAt: v.timestamp || '',
    hashtags: v.hashtags || [],
    url: v.url || ''
  }));

  raw.youtube.forEach(v => normalized.push({
    platform: 'youtube',
    id: v.id,
    text: v.title || '',
    author: v.channelName || '',
    views: v.viewCount || 0,
    likes: v.likeCount || 0,
    comments: v.commentCount || 0,
    shares: 0,
    publishedAt: v.date || '',
    hashtags: [],
    url: v.url || ''
  }));

  raw.reddit.forEach(v => normalized.push({
    platform: 'reddit',
    id: v.id,
    text: v.title || '',
    author: v.author || '',
    views: 0,
    likes: v.score || 0,
    comments: v.numComments || 0,
    shares: 0,
    publishedAt: v.created || '',
    hashtags: [],
    url: v.url || ''
  }));

  return normalized;
}

const allContent = normalizeContent(data);
```

---

### Engagement Analysis and Scoring

```javascript
function analyzeEngagement(content) {
  // Calculate engagement rate per post
  const scored = content.map(post => {
    const totalEngagement = post.likes + post.comments + (post.shares * 2);
    const engagementRate = post.views > 0
      ? (totalEngagement / post.views) * 100
      : totalEngagement;

    return {
      ...post,
      totalEngagement,
      engagementRate: Math.round(engagementRate * 100) / 100,
      viralityScore: Math.min(100, Math.round(
        (Math.log10(Math.max(post.views, 1)) * 10) +
        (engagementRate * 5) +
        (post.shares * 0.5)
      ))
    };
  }).sort((a, b) => b.viralityScore - a.viralityScore);

  // Platform breakdown
  const platforms = {};
  scored.forEach(post => {
    if (!platforms[post.platform]) {
      platforms[post.platform] = { posts: 0, totalViews: 0, totalLikes: 0, totalComments: 0 };
    }
    platforms[post.platform].posts++;
    platforms[post.platform].totalViews += post.views;
    platforms[post.platform].totalLikes += post.likes;
    platforms[post.platform].totalComments += post.comments;
  });

  // Trending hashtags across platforms
  const hashtagMap = {};
  scored.forEach(post => {
    post.hashtags.forEach(tag => {
      const t = (tag || '').toLowerCase();
      if (!hashtagMap[t]) hashtagMap[t] = { count: 0, totalEngagement: 0 };
      hashtagMap[t].count++;
      hashtagMap[t].totalEngagement += post.totalEngagement;
    });
  });

  const trendingHashtags = Object.entries(hashtagMap)
    .sort((a, b) => b[1].totalEngagement - a[1].totalEngagement)
    .slice(0, 20)
    .map(([tag, data]) => ({ tag, ...data }));

  // Top creators by engagement rate
  const creatorMap = {};
  scored.forEach(post => {
    if (!post.author) return;
    if (!creatorMap[post.author]) {
      creatorMap[post.author] = { posts: 0, totalEngagement: 0, platform: post.platform };
    }
    creatorMap[post.author].posts++;
    creatorMap[post.author].totalEngagement += post.totalEngagement;
  });

  const topCreators = Object.entries(creatorMap)
    .sort((a, b) => b[1].totalEngagement - a[1].totalEngagement)
    .slice(0, 10)
    .map(([name, data]) => ({ name, ...data, avgEngagement: Math.round(data.totalEngagement / data.posts) }));

  return {
    scoredContent: scored,
    platformBreakdown: platforms,
    trendingHashtags,
    topCreators,
    topContent: scored.slice(0, 10)
  };
}

const analysis = analyzeEngagement(allContent);
console.log("Top 5 viral content:");
analysis.topContent.slice(0, 5).forEach((p, i) => {
  console.log(`${i + 1}. [${p.viralityScore}/100] ${p.platform}: ${p.text.substring(0, 60)}... (${p.views.toLocaleString()} views)`);
});
```

---

### Competitor Content Monitoring

```javascript
async function monitorCompetitor(username, platform = 'instagram') {
  let run;

  if (platform === 'instagram') {
    run = await client.actor("apify/instagram-scraper").call({
      directUrls: [`https://www.instagram.com/${username}/`],
      resultsLimit: 30,
      resultsType: "posts"
    });
  } else if (platform === 'tiktok') {
    run = await client.actor("apify/tiktok-scraper").call({
      profiles: [username],
      resultsPerPage: 30,
      shouldDownloadVideos: false
    });
  }

  const { items } = await run.dataset().getData();

  // Analyze their posting pattern
  const postTimes = items.map(p => {
    const date = new Date(p.timestamp || p.createTime * 1000);
    return { day: date.getDay(), hour: date.getHours() };
  });

  const bestDays = {};
  const bestHours = {};
  postTimes.forEach(t => {
    bestDays[t.day] = (bestDays[t.day] || 0) + 1;
    bestHours[t.hour] = (bestHours[t.hour] || 0) + 1;
  });

  return {
    username,
    platform,
    totalPosts: items.length,
    avgLikes: Math.round(items.reduce((s, p) => s + (p.likesCount || p.diggCount || 0), 0) / items.length),
    avgComments: Math.round(items.reduce((s, p) => s + (p.commentsCount || p.commentCount || 0), 0) / items.length),
    postingPattern: { bestDays, bestHours },
    topPost: items.sort((a, b) => (b.likesCount || b.diggCount || 0) - (a.likesCount || a.diggCount || 0))[0]
  };
}

const competitor = await monitorCompetitor("competitor_handle", "instagram");
console.log(`${competitor.username}: ${competitor.avgLikes} avg likes, ${competitor.totalPosts} recent posts`);
```

---

### Generate AI Trend Intelligence Report

```javascript
import axios from 'axios';

async function generateTrendReport(analysis, keyword) {
  const topContent = analysis.topContent.slice(0, 5).map(c =>
    `[${c.platform}] "${c.text.substring(0, 80)}" - ${c.views.toLocaleString()} views, ${c.engagementRate}% engagement`
  ).join('\n');

  const hashtags = analysis.trendingHashtags.slice(0, 10).map(h =>
    `#${h.tag} (used ${h.count}x, ${h.totalEngagement.toLocaleString()} total engagement)`
  ).join('\n');

  const creators = analysis.topCreators.slice(0, 5).map(c =>
    `@${c.name} (${c.platform}) - ${c.posts} posts, ${c.avgEngagement.toLocaleString()} avg engagement`
  ).join('\n');

  const prompt = `Write a concise trend intelligence report based on real social media data for the topic: "${keyword}".

DATA ANALYZED: ${analysis.scoredContent.length} posts across 4 platforms

TOP PERFORMING CONTENT:
${topContent}

TRENDING HASHTAGS:
${hashtags}

TOP CREATORS:
${creators}

PLATFORM BREAKDOWN:
${JSON.stringify(analysis.platformBreakdown, null, 2)}

REPORT STRUCTURE:
1. Executive Summary (3 sentences max)
2. Key Trend: What is the dominant narrative right now?
3. Platform Winner: Which platform has the highest engagement for this topic?
4. Content Opportunity: What type of content is underrepresented but high-demand?
5. Hashtag Strategy: Top 5 hashtags to use right now
6. Creator Watch: Who to monitor or collaborate with
7. Action Items: 3 specific things to do this week based on this data

Keep it sharp and actionable. No fluff.`;

  const { data } = await axios.post('https://api.anthropic.com/v1/messages', {
    model: "claude-sonnet-4-20250514",
    max_tokens: 1000,
    messages: [{ role: "user", content: prompt }]
  }, {
    headers: {
      'x-api-key': process.env.CLAUDE_API_KEY,
      'anthropic-version': '2023-06-01'
    }
  });

  return data.content[0].text;
}

const report = await generateTrendReport(analysis, "AI tools");
console.log(report);
```

---

### Export to Structured JSON for Dashboards

```javascript
import { writeFileSync } from 'fs';

function exportReport(analysis, keyword) {
  const report = {
    keyword,
    generatedAt: new Date().toISOString(),
    summary: {
      totalPostsAnalyzed: analysis.scoredContent.length,
      platformBreakdown: analysis.platformBreakdown,
      avgViralityScore: Math.round(
        analysis.scoredContent.reduce((s, c) => s + c.viralityScore, 0) / analysis.scoredContent.length
      )
    },
    topContent: analysis.topContent.slice(0, 20),
    trendingHashtags: analysis.trendingHashtags,
    topCreators: analysis.topCreators,
    rawData: analysis.scoredContent
  };

  const filename = `social-intel-${keyword.replace(/\s+/g, '-')}-${Date.now()}.json`;
  writeFileSync(filename, JSON.stringify(report, null, 2));
  console.log(`Report exported to ${filename}`);
  return filename;
}

exportReport(analysis, "AI tools");
```

---

## Normalized Output Schema

```json
{
  "platform": "tiktok",
  "id": "7302938471029384",
  "text": "This AI tool is insane #aitools #viral",
  "author": "techreviewer99",
  "views": 2300000,
  "likes": 142300,
  "comments": 4820,
  "shares": 9100,
  "engagementRate": 6.79,
  "viralityScore": 87,
  "hashtags": ["aitools", "viral"],
  "publishedAt": "2025-02-18T14:32:00Z",
  "url": "https://www.tiktok.com/@techreviewer99/video/7302938471029384"
}
```

---

## What Makes This Different

| Feature | Basic Scraper | This Skill |
|---|---|---|
| Platforms | 1 at a time | 4+ platforms in parallel |
| Data format | Raw JSON dump | Normalized schema across all platforms |
| Engagement analysis | None | Virality scoring 0 to 100 |
| Trend detection | None | Hashtag velocity + cross-platform signals |
| Creator analysis | None | Top creators ranked by real engagement rate |
| Competitor monitoring | None | Posting pattern + best performing content |
| Intelligence report | None | AI-generated actionable insights |

---

## Pro Tips

1. Run the same keyword weekly to track trend velocity over time
2. Compare hashtag engagement across platforms to find where your niche lives
3. Look for creators with high engagement rate but low follower count for affordable collaborations
4. Cross-reference Reddit discussions with TikTok trends to spot emerging topics early
5. Use the competitor monitoring to reverse-engineer posting schedules of successful accounts
6. Schedule recurring runs with [Apify Schedules](https://www.apify.com?fpr=dx06p) for automated daily monitoring

---

## Cost Estimate

| Action | Apify CU | Cost |
|---|---|---|
| 120 posts across 4 platforms | ~0.20 CU | ~$0.08 |
| Competitor profile analysis | ~0.05 CU | ~$0.02 |
| Full trend report (4 platforms + AI) | ~0.25 CU | ~$0.10 |
| Daily automated monitoring | ~7.5 CU/month | ~$3.00/month |

Scale with [Apify](https://www.apify.com?fpr=dx06p) as your monitoring needs grow.

---

## Error Handling

```javascript
try {
  const run = await client.actor("apify/tiktok-scraper").call(input);
  const dataset = await run.dataset().getData();
  return dataset.items;
} catch (error) {
  if (error.statusCode === 401) throw new Error("Invalid Apify token. Get yours at https://www.apify.com?fpr=dx06p");
  if (error.statusCode === 429) throw new Error("Rate limit hit. Reduce request frequency.");
  if (error.message.includes("timeout")) throw new Error("Actor timed out. Try a smaller batch.");
  throw error;
}
```

---

## Requirements

- An [Apify](https://www.apify.com?fpr=dx06p) account with API token
- Node.js 18+ with `apify-client` and `axios`
- Claude API key for trend report generation (optional but recommended)
- A dashboard or spreadsheet to receive data (Notion, Airtable, Google Sheets)
