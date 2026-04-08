#!/usr/bin/env python3
"""
Parse OpenAI ChatGPT export file (conversations.json) into a normalized list of chats.

Output format (one JSON object per chat, newline‑delimited):
{
  "id": "chat_...",
  "title": "Chat title",
  "date": "YYYY-MM-DD",
  "messages": [
    { "role": "user" | "assistant" | "system", "content": "text...", "timestamp": "ISO" }
  ]
}
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def parse(file_path: str):
    with open(file_path, 'r') as f:
        data = json.load(f)  # expects top‑level list

    for conv in data:
        chat_id = conv.get("id")
        title = conv.get("title", "Untitled")
        # Prefer create_time, but some exports use update_time
        create_ts = conv.get("create_time") or conv.get("update_time") or 0
        try:
            dt = datetime.fromtimestamp(float(create_ts))
        except Exception:
            dt = datetime.now()
        date_str = dt.strftime("%Y-%m-%d")

        messages = []
        for msg in conv.get("messages", []):
            # role is user/assistant/system; content can be string or {parts: [...]}
            role = msg.get("role")
            raw_content = msg.get("content")
            if isinstance(raw_content, dict):
                parts = raw_content.get("parts", [])
                content = "\n".join(parts)
            else:
                content = raw_content or ""
            # timestamp per message
            msg_ts = msg.get("create_time") or conv.get("create_time") or 0
            try:
                msg_iso = datetime.fromtimestamp(float(msg_ts)).isoformat()
            except Exception:
                msg_iso = dt.isoformat()
            messages.append({
                "role": role,
                "content": content.strip(),
                "timestamp": msg_iso
            })

        yield {
            "id": chat_id,
            "title": title,
            "date": date_str,
            "messages": messages
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: parse_openai.py <conversations.json>", file=sys.stderr)
        sys.exit(1)
    for chat in parse(sys.argv[1]):
        print(json.dumps(chat, ensure_ascii=False))