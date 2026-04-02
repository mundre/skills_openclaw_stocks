# Platform Methods

## Dribbble

### Search URL

`https://dribbble.com/search/<urlencoded-tag>`

### Search-page collection

- Use a real browser.
- Query `a[href*="/shots/"]`.
- Keep only anchors whose `href` matches `/shots/<numeric-id>`.
- For `title`, prefer:
  - `img.alt`
  - overlay shot title text
  - anchor text after whitespace cleanup
- For `cover_image_url`, prefer:
  - highest `srcset` candidate from the card image
  - or upgrade `resize=` query params to a larger variant such as `1600x1200`

### Detail-page enrichment

Use the detail page when the search card does not expose a reliable author or high-resolution image.

Recommended browser loading pattern:

1. `goto(url, wait_until="domcontentloaded")`
2. `wait_for_load_state("networkidle")`
3. then read meta and title

Field rules:

- `author_name`
  - Parse from page title pattern: `<shot title> by <author> on Dribbble`
  - Fallback: parse `meta[name="description"]` text after `designed by `
- `cover_image_url`
  - Prefer `meta[property="og:image"]`
- `publish_time`
  - Public pages are unstable here
  - Try `article:published_time`, `datePublished`, `uploadDate`, or `dateCreated` if present
  - If not found, leave `null`

### Practical notes

- Raw HTTP often returns an empty shell page; browser rendering is safer.
- Author extraction is reliable enough from the detail-page title.
- Publish time is not consistently available on public pages.

## Pinterest

### Search URL

`https://www.pinterest.com/search/pins/?q=<urlencoded-tag>&rs=typed`

### Search-page collection

- Use a real browser.
- Query `a[href*="/pin/"]`.
- Keep only anchors whose `href` matches `/pin/<numeric-id>/`.
- For `title`, prefer:
  - `img.alt`
  - `aria-label`
  - cleaned anchor text
- For `cover_image_url`, the search page may only expose `236x` or `474x` images.

### Detail-page enrichment

Use the detail page for high-resolution cover, author, and timestamp.

Preferred public fields:

- `cover_image_url`
  - `meta[property="og:image"]`
  - Fallback: upgrade `236x` or `474x` image URLs to `736x`
- `author_name`
  - `meta[property="pinterestapp:pinner"]`, using the final path segment as username
  - If needed, parse relay JSON and prefer `originPinner.fullName`, `originPinner.username`, or `pinner.username`
- `publish_time`
  - `meta[property="og:updated_time"]`
  - Fallback: relay JSON `createdAt`

### Rich relay data

Public Pinterest detail pages often contain relay payloads with useful fields such as:

- `richMetadata.title`
- `createdAt`
- `imageLargeUrl`
- `images_736x`
- `images_orig`
- `originPinner.fullName`
- `pinner.username`

Use them when meta tags are insufficient.

### Practical notes

- Pinterest public detail pages are much richer than search cards.
- `og:updated_time` is usually good enough as a public timestamp.
- High-resolution images are easy to recover from `og:image` or size-upgraded URLs.
