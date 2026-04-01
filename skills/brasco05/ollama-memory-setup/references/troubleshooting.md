# Troubleshooting

## memory_search still returns `disabled: true` after setup

1. Check Ollama is running: `curl http://localhost:11434/api/tags`
2. Check model is loaded: `ollama list` — should show `nomic-embed-text`
3. Restart OpenClaw: `openclaw gateway restart`
4. Start a fresh session (`/new`) — memory index syncs on session start

## Ollama not responding on port 11434

```bash
# macOS
brew services restart ollama

# Linux
pkill ollama; ollama serve &
```

## `openclaw config set` command not found

Use the gateway tool instead:
```
openclaw config set agents.defaults.memorySearch.provider ollama
```

Or edit `~/.openclaw/openclaw.json` manually and add:
```json
"memorySearch": {
  "enabled": true,
  "provider": "ollama",
  "model": "nomic-embed-text",
  "remote": { "baseUrl": "http://localhost:11434" }
}
```

## Slow first response after setup

Normal — Ollama loads the model into memory on first use (~5-10 seconds). Subsequent queries are fast.

## macOS: Ollama stops after reboot

Enable auto-start:
```bash
brew services start ollama
```

## Linux: Ollama stops after reboot

Create a systemd service:
```bash
sudo systemctl enable ollama
sudo systemctl start ollama
```
