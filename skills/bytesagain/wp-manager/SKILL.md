---
version: "3.0.4"
name: wp-manager
description: "Manage WordPress sites from terminal. Use when checking site health, listing posts and pages, searching content, or running security scans."
author: BytesAgain
homepage: https://bytesagain.com
source: https://github.com/bytesagain/ai-skills
---

# wp-manager

WordPress site management CLI — check site health, list posts and pages, search content, inspect sitemap, generate robots.txt templates, and run security scans. Connects to your WordPress site via its REST API.

## Commands

### `status`

Check site health — response time, SSL certificate status, and HTTP headers.

```bash
scripts/script.sh status
```

### `info`

Show site metadata — name, description, URL, WordPress version, timezone.

```bash
scripts/script.sh info
```

### `list-posts`

List recent blog posts with title, date, and status. Optional count argument.

```bash
scripts/script.sh list-posts 10
```

### `list-pages`

List published pages with title and URL. Optional count argument.

```bash
scripts/script.sh list-pages 20
```

### `search`

Search posts and pages by keyword.

```bash
scripts/script.sh search "tutorial"
```

### `sitemap`

Fetch and display the site's XML sitemap structure and URL count.

```bash
scripts/script.sh sitemap
```

### `robots`

Generate a robots.txt template based on WordPress best practices.

```bash
scripts/script.sh robots
```

### `performance`

Show performance tips — caching headers, GZIP status, image optimization hints.

```bash
scripts/script.sh performance
```

### `security-scan`

Run a security checklist — exposed files, default credentials, header analysis.

```bash
scripts/script.sh security-scan
```

### `help`

```bash
scripts/script.sh help
```

## Examples

```bash
# Daily site check workflow
scripts/script.sh status
scripts/script.sh info
scripts/script.sh list-posts 5
scripts/script.sh security-scan
```

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `WP_URL` | No | WordPress site URL (default: `https://bytesagain.com`) |
| `WP_MANAGER_DIR` | No | Data directory (default: `~/.local/share/wp-manager/`) |

## Data Storage

Session data cached in `~/.local/share/wp-manager/`.

## Requirements

- bash 4.0+
- curl (for WordPress REST API calls)

---

*Powered by BytesAgain | bytesagain.com | hello@bytesagain.com*
