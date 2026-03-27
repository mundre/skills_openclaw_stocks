"""MoltAssist Channel Sync -- optional cross-instance context sharing.

What this solves:
  OpenClaw can run as multiple bot instances simultaneously -- a DM bot,
  a WhatsApp bot, multiple group chat bots. By default each instance is
  completely unaware of what the others know or have said.

  Channel Sync is an OPTIONAL feature users can enable. When active:
    - Each instance writes a summary of recent user activity to a shared file
    - Instances can read what happened in other channels (opt-in, summary only)
    - Proactive message cooldowns are global -- if one instance already reached
      out, others won't pile on in the same window

  Importantly: per-channel silence detection is NOT overridden.
    If a user wants their DM bot to reach out when it's been quiet on DM,
    that behaviour is preserved even if the user is active in a group chat.
    Global cooldowns only prevent *simultaneous* reach-outs from multiple
    instances -- they don't suppress a bot that legitimately hasn't heard
    from the user in its own channel.

  This is intentional: a DM bot missing you is a valid use case even if
  you're chatting in a group. The user controls which behaviour they want
  by configuring the bot's proactive check independently per channel.

Enabled via config: {"channel_sync": {"enabled": true}}

Architecture:
  Backed by a single JSON file: memory/moltassist-context.json
  No DB, no network. Rolling window of last 100 activity entries.
  Safe for single-user concurrent reads/writes (no critical transactions).

v0.6 scaffold -- interfaces are stable, integration with proactive check later.
"""

import json
import os
import time
from pathlib import Path


_MAX_ENTRIES = 100  # rolling window across all instances


def _get_context_path() -> Path:
    workspace = os.environ.get("OPENCLAW_WORKSPACE") or os.path.expanduser(
        "~/.openclaw/workspace"
    )
    return Path(workspace) / "moltassist" / "memory" / "moltassist-context.json"


def _read_store(path: Path) -> dict:
    """Read the context store. Returns {activities: [], cooldowns: {}}."""
    if not path.exists():
        return {"activities": [], "cooldowns": {}}
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"activities": [], "cooldowns": {}}
    if not isinstance(data, dict):
        return {"activities": [], "cooldowns": {}}
    data.setdefault("activities", [])
    data.setdefault("cooldowns", {})
    return data


def _write_store(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


class ContextStore:
    """Shared cross-channel context store backed by a JSON file.

    Optional feature -- only used when channel_sync is enabled in config.
    """

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else _get_context_path()

    # -------------------------------------------------------------------------
    # Activity tracking
    # -------------------------------------------------------------------------

    def record_activity(
        self,
        channel: str,
        summary: str,
        mood_hint: str | None = None,
        instance_id: str | None = None,
    ) -> None:
        """Record user activity from any channel instance.

        channel:     e.g. 'telegram_dm', 'whatsapp_dm', 'telegram_group_work',
                     'telegram_group_family' -- be specific so instances can
                     distinguish each other
        summary:     neutral one-line summary of what was discussed.
                     Summarise before storing -- do NOT store raw messages.
        mood_hint:   optional user mood/context hint ('focused', 'casual', etc.)
        instance_id: optional -- identifies which bot instance wrote this entry
        """
        store = _read_store(self.path)
        entry = {
            "channel": channel,
            "timestamp": time.time(),
            "summary": summary,
            "mood_hint": mood_hint,
            "instance_id": instance_id,
        }
        store["activities"].append(entry)
        store["activities"] = store["activities"][-_MAX_ENTRIES:]
        _write_store(store, self.path)

    def get_last_activity(self, channel: str | None = None) -> dict | None:
        """Return the most recent activity entry.

        If channel is specified: returns most recent for that channel only.
        If channel is None: returns most recent across ALL channels.

        Note on proactive reach-out:
          Use channel=your_channel for per-instance silence detection.
          Use channel=None only if you explicitly want global silence detection
          (e.g. to prevent a bot reaching out when user is already active elsewhere).
          The DM bot use case typically wants channel='telegram_dm' so it misses
          the user independently of group chat activity.
        """
        store = _read_store(self.path)
        activities = store.get("activities", [])
        if channel:
            activities = [a for a in activities if a.get("channel") == channel]
        if not activities:
            return None
        return max(activities, key=lambda e: e.get("timestamp", 0))

    def get_silence_window(self, channel: str | None = None) -> int:
        """Seconds since last activity.

        channel=None -> global (any channel). channel='x' -> that channel only.
        Returns 0 if no activity recorded yet.
        """
        last = self.get_last_activity(channel=channel)
        if last is None:
            return 0
        return int(time.time() - last.get("timestamp", 0))

    def get_recent_activities(
        self,
        limit: int = 10,
        exclude_channel: str | None = None,
    ) -> list[dict]:
        """Return recent activities, optionally excluding a specific channel.

        Useful for an instance to see what happened in other channels:
          ctx.get_recent_activities(exclude_channel='telegram_group_work')
        """
        store = _read_store(self.path)
        activities = store.get("activities", [])
        if exclude_channel:
            activities = [a for a in activities if a.get("channel") != exclude_channel]
        return sorted(activities, key=lambda e: e.get("timestamp", 0), reverse=True)[:limit]

    def get_recent_context(self, hours: float = 2) -> str:
        """Return a summary string of recent cross-channel activity.

        Useful for prepending to LLM enrichment prompts so the AI has
        awareness of what happened across all channels recently.

        Returns empty string if no activity in the window.
        """
        cutoff = time.time() - (hours * 3600)
        store = _read_store(self.path)
        activities = store.get("activities", [])
        recent = [
            a for a in activities
            if a.get("timestamp", 0) >= cutoff
        ]
        if not recent:
            return ""

        recent.sort(key=lambda e: e.get("timestamp", 0))

        lines = []
        for a in recent:
            channel = a.get("channel", "unknown")
            summary = a.get("summary", "")
            mood = a.get("mood_hint")
            mood_str = f" [{mood}]" if mood else ""
            lines.append(f"- {channel}: {summary}{mood_str}")

        return "Recent activity across channels:\n" + "\n".join(lines)

    # -------------------------------------------------------------------------
    # Global proactive cooldowns
    # -------------------------------------------------------------------------

    def set_cooldown(self, key: str, duration_seconds: int) -> None:
        """Set a shared cooldown that expires after duration_seconds.

        Used to prevent multiple bot instances reaching out simultaneously.
        One instance reaching out sets this cooldown; others check it before
        deciding whether to send their own proactive message.

        This does NOT affect per-channel silence detection -- it only prevents
        the same proactive message being sent by multiple instances at once.

        Example:
          ctx.set_cooldown("proactive_global", 3600)  # 1 hour
          # -> all other instances skip proactive reach-out for 60 minutes
        """
        store = _read_store(self.path)
        store["cooldowns"][key] = time.time() + duration_seconds
        _write_store(store, self.path)

    def is_on_cooldown(self, key: str) -> bool:
        """Return True if the cooldown key is active (not yet expired)."""
        store = _read_store(self.path)
        expires_at = store.get("cooldowns", {}).get(key)
        if expires_at is None:
            return False
        return time.time() < expires_at
