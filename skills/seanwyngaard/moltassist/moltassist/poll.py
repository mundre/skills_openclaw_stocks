"""MoltAssist poller -- entry point for the system job.

Usage: python3 -m moltassist.poll --workspace /path/to/workspace

Called every minute by launchd/cron. Checks which categories are due,
runs the appropriate poller, marks them as run, and exits.
"""

import argparse
import json
import logging
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from moltassist.scheduler import Scheduler

log = logging.getLogger("moltassist.poll")


# ---- State helpers ----

def _load_poll_state(state_path: Path) -> dict:
    if not state_path.exists():
        return {}
    try:
        with open(state_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_poll_state(state: dict, state_path: Path) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)


def _load_config(config_path: Path) -> dict:
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        return json.load(f)


def _notify(message: str, urgency: str = "medium", category: str = "system",
            source: str = "poll", event_id: str | None = None,
            config_path: Path | None = None, log_path: Path | None = None) -> None:
    """Call MoltAssist notify(). Fails silently -- pollers must never crash the scheduler."""
    try:
        from moltassist.core import notify
        kwargs: dict = dict(
            message=message,
            urgency=urgency,
            category=category,
            source=source,
        )
        if event_id:
            kwargs["event_id"] = event_id
        if config_path:
            kwargs["config_path"] = config_path
        if log_path:
            kwargs["log_path"] = log_path
        notify(**kwargs)
    except Exception:
        pass


# ---- Pollers ----


def poll_calendar(config: dict, state_path: Path, **kwargs) -> None:
    """Check calendar for upcoming events via openclaw/gog subprocess."""
    try:
        result = subprocess.run(
            ["openclaw", "run", "gog", "calendar", "list", "--today", "--all"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return
        output = result.stdout.strip()
    except Exception:
        return

    if not output:
        return

    state = _load_poll_state(state_path)
    if "calendar_notified" not in state:
        state["calendar_notified"] = []

    tz_name = config.get("schedule", {}).get("timezone", "UTC")
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("UTC")
    now = datetime.now(tz=tz)

    for line in output.splitlines():
        # Parse lines looking for time indicators
        # Expected format varies, but look for events starting in 10-20 min
        line = line.strip()
        if not line:
            continue

        # Try to extract event time and title
        # Typical format: "14:30 - Meeting Title" or similar
        parts = line.split(" - ", 1)
        if len(parts) < 2:
            parts = line.split("\t", 1)
        if len(parts) < 2:
            continue

        time_str = parts[0].strip()
        title = parts[1].strip()

        try:
            event_time = datetime.strptime(time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )
        except ValueError:
            continue

        minutes_until = (event_time - now).total_seconds() / 60

        if 0 < minutes_until <= 20:
            # Generate dedup key from title + date
            event_id = f"cal_{title[:30]}_{now.strftime('%Y-%m-%d')}"

            if event_id in state["calendar_notified"]:
                continue  # Already notified

            _notify(
                message=f"{title} in {int(minutes_until)} min",
                urgency="medium",
                category="calendar",
                source="poll_calendar",
                event_id=event_id,
                config_path=kwargs.get("config_path"),
                log_path=kwargs.get("log_path"),
            )

            state["calendar_notified"].append(event_id)

    # Keep only today's dedup entries
    today_prefix = f"cal_"
    today_suffix = now.strftime("%Y-%m-%d")
    state["calendar_notified"] = [
        eid for eid in state["calendar_notified"]
        if eid.endswith(today_suffix)
    ]

    _save_poll_state(state, state_path)


def poll_email(config: dict, state_path: Path, **kwargs) -> None:
    """Check for unread emails via gog subprocess."""
    try:
        result = subprocess.run(
            ["openclaw", "run", "gog", "gmail", "list", "is:unread", "--limit", "10"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return
        output = result.stdout.strip()
    except Exception:
        return

    if not output:
        return

    state = _load_poll_state(state_path)
    if "email_notified" not in state:
        state["email_notified"] = []

    polling_cfg = config.get("schedule", {}).get("polling", {}).get("email", {})
    whitelist = polling_cfg.get("whitelist", [])

    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue

        # Try to extract sender and subject from line
        # Format varies -- look for "From: sender - Subject: subject" or tab-separated
        sender = ""
        subject = line
        message_id = ""

        if " - " in line:
            parts = line.split(" - ", 2)
            if len(parts) >= 2:
                sender = parts[0].strip()
                subject = parts[1].strip()
                if len(parts) >= 3:
                    message_id = parts[2].strip()
        elif "\t" in line:
            parts = line.split("\t")
            if len(parts) >= 2:
                sender = parts[0].strip()
                subject = parts[1].strip()
                if len(parts) >= 3:
                    message_id = parts[2].strip()

        # Generate dedup ID
        if not message_id:
            message_id = f"email_{sender[:20]}_{subject[:20]}_{int(time.time() // 3600)}"

        if message_id in state["email_notified"]:
            continue

        # Check whitelist (if set)
        if whitelist:
            sender_lower = sender.lower()
            if not any(w.lower() in sender_lower for w in whitelist):
                continue

        # Determine urgency based on sender priority
        urgency = "medium"
        priority_senders = polling_cfg.get("priority_senders", [])
        if any(p.lower() in sender.lower() for p in priority_senders):
            urgency = "high"

        msg = f"{sender}: {subject}" if sender else subject

        _notify(
            message=msg,
            urgency=urgency,
            category="email",
            source="poll_email",
            event_id=message_id,
            config_path=kwargs.get("config_path"),
            log_path=kwargs.get("log_path"),
        )

        state["email_notified"].append(message_id)

    # Keep only last 200 dedup entries to avoid unbounded growth
    state["email_notified"] = state["email_notified"][-200:]
    _save_poll_state(state, state_path)


def poll_weather(config: dict, state_path: Path, **kwargs) -> None:
    """Check weather via weather skill subprocess."""
    try:
        result = subprocess.run(
            ["openclaw", "run", "weather", "forecast", "--hours", "6"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return
        output = result.stdout.strip()
    except Exception:
        return

    if not output:
        return

    # Check for rain/storms
    weather_lower = output.lower()
    has_bad_weather = any(
        term in weather_lower
        for term in ["rain", "storm", "thunder", "hail", "snow", "sleet"]
    )

    if not has_bad_weather:
        return

    state = _load_poll_state(state_path)
    tz_name = config.get("schedule", {}).get("timezone", "UTC")
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("UTC")
    today = datetime.now(tz=tz).strftime("%Y-%m-%d")
    weather_key = f"weather_{today}"

    if state.get("weather_notified") == weather_key:
        return  # Already notified today

    # Try to cross-reference with calendar for outdoor events
    calendar_note = ""
    try:
        cal_result = subprocess.run(
            ["openclaw", "run", "gog", "calendar", "list", "--today", "--all"],
            capture_output=True, text=True, timeout=10,
        )
        if cal_result.returncode == 0 and cal_result.stdout.strip():
            cal_lower = cal_result.stdout.lower()
            outdoor_terms = ["outdoor", "park", "garden", "bbq", "picnic", "hike",
                             "run", "walk", "golf", "tennis", "swim"]
            for term in outdoor_terms:
                if term in cal_lower:
                    calendar_note = " -- you have an outdoor event today"
                    break
    except Exception:
        pass

    # Extract first line of weather info as summary
    summary = output.splitlines()[0][:100] if output else "Bad weather expected"

    _notify(
        message=f"{summary}{calendar_note}",
        urgency="medium",
        category="weather",
        source="poll_weather",
        event_id=weather_key,
        config_path=kwargs.get("config_path"),
        log_path=kwargs.get("log_path"),
    )

    state["weather_notified"] = weather_key
    _save_poll_state(state, state_path)


# ---- Poller registry ----

POLLERS = {
    "calendar": poll_calendar,
    "email": poll_email,
    "weather": poll_weather,
}


# ---- Main entry point ----

def main(workspace: Path | None = None) -> None:
    """Entry point called by the system job every minute."""
    if workspace is None:
        workspace = Path.cwd()

    config_path = workspace / "moltassist" / "config.json"
    state_path = workspace / "memory" / "moltassist-schedule-state.json"
    log_path = workspace / "memory" / "moltassist-log.json"

    scheduler = Scheduler(config_path=config_path, state_path=state_path)
    config = scheduler._load_config()

    due = scheduler.get_due_categories()
    if not due:
        return

    for category in due:
        poller = POLLERS.get(category)
        if poller is None:
            # No built-in or custom poller for this category -- skip
            scheduler.mark_run(category)
            continue

        try:
            poller(
                config,
                state_path,
                config_path=config_path,
                log_path=log_path,
            )
        except Exception:
            # Poller errors must never crash the scheduler
            pass

        scheduler.mark_run(category)


def run_single(category: str, workspace: Path | None = None) -> None:
    """Run a single poller immediately (for testing / manual trigger)."""
    if workspace is None:
        workspace = Path.cwd()

    config_path = workspace / "moltassist" / "config.json"
    state_path = workspace / "memory" / "moltassist-schedule-state.json"
    log_path = workspace / "memory" / "moltassist-log.json"

    config = {}
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)

    poller = POLLERS.get(category)
    if poller is None:
        print(f"No poller for category: {category}")
        return

    poller(config, state_path, config_path=config_path, log_path=log_path)
    print(f"Polled: {category}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MoltAssist poller")
    parser.add_argument("--workspace", type=Path, default=None,
                        help="Path to OpenClaw workspace")
    parser.add_argument("--category", type=str, default=None,
                        help="Run a single category poller (for testing)")
    args = parser.parse_args()

    if args.category:
        run_single(args.category, workspace=args.workspace)
    else:
        main(workspace=args.workspace)
