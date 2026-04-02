---
name: wechat-article-to-obsidian
description: "Save WeChat public account articles (微信公众号文章) as clean Markdown notes in Obsidian. Use this skill whenever the user shares a mp.weixin.qq.com link and wants to save it to Obsidian, or mentions '微信文章', '公众号文章', '保存微信', '导入微信文章到Obsidian', 'save wechat article', 'clip wechat'. Also triggers when the user wants to batch-save multiple WeChat article URLs to their Obsidian vault. Zero external dependencies — just curl and Node.js."
---

# WeChat Article → Obsidian

Save WeChat MP articles (微信公众号) as clean Markdown notes in Obsidian. No browser, no CDP, no plugins needed.

## How it works

WeChat articles are server-side rendered — the full content is in the HTML, just CSS-hidden. A `curl` with browser UA fetches it, a Node.js script converts it to clean Markdown (with images, merged section headings, promotional tails stripped), and the result goes into the user's Obsidian vault via the `obsidian` CLI.

## Dependencies

- **curl** (pre-installed on macOS/Linux)
- **Node.js** >= 18
- **obsidian CLI** (for writing to vault — if not available, fall back to direct file write)

## First-time setup

On first use, check `<skill-path>/config.json`. If `obsidian_vault` or `default_path` is empty, ask the user:

1. "What is your Obsidian vault name?" — this is the vault name used with `obsidian` CLI (e.g., `vault=MyVault`)
2. "Where should I save WeChat articles by default?" — a path inside the vault (e.g., `notes/wechat`, `articles/wechat`)

Then write the answers to `<skill-path>/config.json`:

```json
{
  "obsidian_vault": "MyVault",
  "default_path": "notes/wechat"
}
```

This only needs to happen once. After that, the skill uses the saved config automatically.

## Configuration

### Natural language override (per-request)

The user can override the default path anytime:
- "把这篇文章存到 reading/tech 目录"
- "save this under articles/ai/"
- "导入到 Obsidian 的 inbox 文件夹"

Parse the target path from the user's message and use it instead of `default_path`.

### Config file (persistent default)

`<skill-path>/config.json`:

- `obsidian_vault`: the vault name for `obsidian` CLI
- `default_path`: where to save articles when the user doesn't specify a path

## Workflow

### Single article

```bash
SKILL_PATH="<skill-path>"

# Step 1: Fetch HTML
bash "$SKILL_PATH/scripts/fetch.sh" "URL" /tmp/wx_article.html

# Step 2: Get metadata (to determine filename)
node "$SKILL_PATH/scripts/parse.mjs" /tmp/wx_article.html --json

# Step 3: Parse to Markdown
node "$SKILL_PATH/scripts/parse.mjs" /tmp/wx_article.html > /tmp/wx_article.md

# Step 4: Read the parsed output, then save to Obsidian
obsidian create path="<target_path>/<filename>.md" content="<markdown_content>" vault=<vault_name>
```

The filename should be derived from the article title, keeping it readable: strip special characters, keep Chinese characters. Example: `从Claude Code源码看AI Agent工程架构.md`

### Batch save (multiple URLs)

For 2+ URLs, process them sequentially. For 4+ URLs, consider using subagents in parallel (each with its own temp file).

```bash
# Per URL:
bash "$SKILL_PATH/scripts/fetch.sh" "$url" "/tmp/wx_${i}.html"
node "$SKILL_PATH/scripts/parse.mjs" "/tmp/wx_${i}.html" > "/tmp/wx_${i}.md"
# Then save each to Obsidian
```

## Output format

The parser produces clean Markdown with YAML frontmatter:

```yaml
---
title: "Article Title"
author: "公众号名称"
publish_date: "2026-03-31 19:45:08"
saved_date: "2026-03-31"
source: "wechat"
url: "https://mp.weixin.qq.com/s/..."
---
```

The parser automatically:
- Preserves all article images (WeChat CDN URLs)
- Removes WeChat decoration text (THUMB, STOPPING)
- Merges "PART.XX" + title into proper `## PART.XX Title` headings
- Strips promotional tails (关注/点赞/在看, author bios, QR codes)
- Preserves bold, italic, code blocks, blockquotes, lists, links

## Post-processing by Claude

After the parser runs, review the output and apply any remaining cleanup:

1. If the user specified tags, add them to the frontmatter
2. Verify the filename is clean and descriptive
3. Confirm save location with the user if ambiguous

## Troubleshooting

### curl returns empty or verification page

WeChat may rate-limit. Wait 30 seconds and retry. If persistent, the article may require login — inform the user.

### Empty content / no #js_content

Some special article types (mini-programs, video-only) aren't supported. Inform the user.

### obsidian CLI not available

Fall back to direct file write using the Write tool to the vault's disk path.
