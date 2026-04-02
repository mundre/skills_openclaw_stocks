---
name: dribbble-pinterest-search
description: Choose public search tags for Dribbble and Pinterest, run public search flows without login, and extract normalized result fields such as title, high-resolution image, author, source URL, and publish/update time when available. Use when Codex needs to collect design inspiration from Dribbble or Pinterest, design a keyword taxonomy for B-end/data-visualization themes, or explain how to get public search result fields from these two platforms.
---

# Dribbble Pinterest Search

Use English tags, not Chinese keywords, for public design search on Dribbble and Pinterest. Treat search pages as candidate discovery and detail pages as field enrichment.

Keep the workflow public-only:

- Do not require cookies, sessions, or login-only APIs.
- Prefer browser automation for both platforms.
- Use detail pages only when search results do not expose a reliable high-resolution image, author, or publish/update time.

## Workflow

1. Choose a category and tag set.
   - For B-end/data-visualization use cases, load [references/tag-taxonomy.md](references/tag-taxonomy.md).
   - Prefer Dribbble for dashboard, scene, motion, and high-quality UI shots.
   - Prefer Pinterest for color, infographic, isometric, and reference-heavy categories.

2. Build the public search URL.
   - Dribbble: `https://dribbble.com/search/<urlencoded-tag>`
   - Pinterest: `https://www.pinterest.com/search/pins/?q=<urlencoded-tag>&rs=typed`

3. Collect candidate cards from the search page.
   - Dribbble: find `a[href*="/shots/"]`, then keep only links matching `/shots/<numeric-id>`.
   - Pinterest: find `a[href*="/pin/"]`, then keep only links matching `/pin/<numeric-id>/`.

4. Normalize search-card fields first.
   - Always capture at least: `title`, `platform`, `source_url`, `cover_image_url`, `keyword/tag`.
   - If search-card author or time is weak, leave it empty and enrich from the detail page.

5. Enrich from the detail page when needed.
   - Use detail pages for high-resolution cover images.
   - Use detail pages for `author_name`.
   - Use detail pages for `publish_time` or `updated_time` only when the public page exposes it reliably.

6. Return a normalized public-only record.
   - Keep unstable fields nullable.
   - Record which tag matched.
   - Do not fabricate publish times or authors.

## Extraction Rules

Use these field priorities:

- `title`: search-card text first, then detail-page meta/title.
- `cover_image_url`: prefer highest `srcset` candidate or detail-page `og:image`.
- `author_name`: prefer detail-page author metadata or title pattern.
- `publish_time`: prefer detail-page `og:updated_time`, `createdAt`, `datePublished`, or equivalent. Leave `null` when unavailable.
- `summary`: use normalized title or public description snippet.

Platform-specific details live in:

- [references/platform-methods.md](references/platform-methods.md)
- [references/tag-taxonomy.md](references/tag-taxonomy.md)

## Guardrails

- Stay within public pages and public metadata.
- Expect DOM changes and anti-bot behavior; selectors are heuristics, not guarantees.
- Treat Dribbble publish time as unstable on public pages.
- Treat Pinterest `og:updated_time` as the best public timestamp unless richer relay data is needed.
- Prefer English tags even for Chinese design topics.

## Output Shape

Normalize results into a shape close to:

```json
{
  "title": "",
  "platform": "dribbble|pinterest",
  "source_url": "",
  "cover_image_url": "",
  "author_name": "",
  "publish_time": null,
  "keyword": "",
  "category": "",
  "matched_tags": []
}
```
