# Bird

Use `bird` CLI to read/search X (Twitter) and post tweets/replies from your OpenClaw agent.

## Installation

Add this skill to your OpenClaw workspace:

```bash
cp -r . ~/.openclaw/workspace/skills/bird/
```

## Usage

### Reading
- `bird whoami` — Check authenticated user
- `bird read <url-or-id>` — Read a tweet
- `bird thread <url-or-id>` — Read a full thread
- `bird search "query" -n 5` — Search tweets

### Posting (confirm with user first)
- `bird tweet "text"` — Post a tweet
- `bird reply <id-or-url> "text"` — Reply to a tweet

### Auth Sources
- Browser cookies (default: Firefox/Chrome)
- Sweetistics API: set `SWEETISTICS_API_KEY` or use `--engine sweetistics`
- Check sources: `bird check`

## License

MIT — see [LICENSE](./LICENSE)
