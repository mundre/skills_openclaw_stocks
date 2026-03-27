"""MoltAssist scheduler -- manages polling intervals and system job installation."""

import json
import os
import platform
import subprocess
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


# Default paths (overridable for testing)
_WORKSPACE = os.environ.get("OPENCLAW_WORKSPACE") or os.path.expanduser("~/.openclaw/workspace")
_DEFAULT_CONFIG_PATH = Path(_WORKSPACE) / "moltassist" / "config.json"
_DEFAULT_STATE_PATH = Path(_WORKSPACE) / "memory" / "moltassist-schedule-state.json"

PLIST_LABEL = "ai.moltassist.poll"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / f"{PLIST_LABEL}.plist"
CRONTAB_MARKER = "# moltassist-poll"


class Scheduler:
    """Reads polling config, tracks per-category lastRun, installs system jobs."""

    def __init__(
        self,
        config_path: Path | None = None,
        state_path: Path | None = None,
    ):
        self.config_path = config_path or _DEFAULT_CONFIG_PATH
        self.state_path = state_path or _DEFAULT_STATE_PATH

    # ---- Config / state helpers ----

    def _load_config(self) -> dict:
        if not self.config_path.exists():
            return {}
        with open(self.config_path) as f:
            return json.load(f)

    def _load_state(self) -> dict:
        if not self.state_path.exists():
            return {}
        try:
            with open(self.state_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_state(self, state: dict) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_path, "w") as f:
            json.dump(state, f, indent=2)

    def _get_schedule_config(self) -> dict:
        """Return the 'schedule' -> 'polling' section from config, or empty dict."""
        config = self._load_config()
        return config.get("schedule", {}).get("polling", {})

    # ---- Core scheduling logic ----

    def should_run(self, category: str) -> bool:
        """True if enough time has elapsed since last run for this category."""
        polling = self._get_schedule_config()
        cat_cfg = polling.get(category, {})

        if not cat_cfg.get("enabled", False):
            return False

        interval = cat_cfg.get("interval_minutes", 0)
        if interval == 0:
            # "Manual only" -- never auto-poll
            return False

        state = self._load_state()
        last_run_ts = state.get("lastRun", {}).get(category)

        if last_run_ts is None:
            # First run -- always due
            return True

        elapsed = time.time() - last_run_ts
        return elapsed >= (interval * 60)

    def mark_run(self, category: str) -> None:
        """Update lastRun timestamp for this category."""
        state = self._load_state()
        if "lastRun" not in state:
            state["lastRun"] = {}
        state["lastRun"][category] = time.time()
        self._save_state(state)

    def get_due_categories(self) -> list[str]:
        """Return list of enabled categories whose interval has elapsed."""
        polling = self._get_schedule_config()
        due = []
        for category in polling:
            if self.should_run(category):
                due.append(category)
        return due

    # ---- Digest scheduling ----

    def should_run_digest(self) -> bool:
        """True if the morning digest should fire now.

        Conditions:
        1. schedule.morning_digest is true in config
        2. Current time is within 5 minutes after quiet_hours.end
        3. Haven't already run today
        4. There are items in the queue
        """
        config = self._load_config()
        schedule = config.get("schedule", {})

        if not schedule.get("morning_digest", False):
            return False

        tz_name = schedule.get("timezone", "UTC")
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            tz = ZoneInfo("UTC")

        # Check if we already ran today
        state = self._load_state()
        last_digest = state.get("lastDigest")
        if last_digest:
            today = datetime.now(tz=tz).strftime("%Y-%m-%d")
            if last_digest == today:
                return False

        # Check if we're within the digest window (quiet_hours.end  5 min)
        qh = schedule.get("quiet_hours", {})
        end_str = qh.get("end", "08:00")
        try:
            end_time = datetime.strptime(end_str, "%H:%M").time()
        except ValueError:
            return False

        now = datetime.now(tz=tz)
        end_dt = now.replace(
            hour=end_time.hour, minute=end_time.minute, second=0, microsecond=0,
        )
        diff_seconds = (now - end_dt).total_seconds()

        # Fire if we're 0-5 minutes past quiet_hours.end
        if not (0 <= diff_seconds <= 300):
            return False

        # Check if queue has items
        try:
            from moltassist.queue import _get_queue_path, _read_queue
            queue_path = _get_queue_path()
            entries = _read_queue(queue_path)
            if not entries:
                return False
        except Exception:
            return False

        return True

    def mark_digest_run(self) -> None:
        """Record that today's digest has been sent."""
        config = self._load_config()
        tz_name = config.get("schedule", {}).get("timezone", "UTC")
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            tz = ZoneInfo("UTC")
        state = self._load_state()
        state["lastDigest"] = datetime.now(tz=tz).strftime("%Y-%m-%d")
        self._save_state(state)

    def run_digest(self) -> bool:
        """Execute the morning digest if due. Returns True if digest was sent."""
        if not self.should_run_digest():
            return False

        try:
            # Import here to avoid circular imports
            import sys
            from pathlib import Path as P
            scripts_dir = P(__file__).resolve().parent.parent / "scripts"
            sys.path.insert(0, str(scripts_dir.parent))
            from scripts.digest import run_digest as _run_digest
            _run_digest()
            self.mark_digest_run()
            return True
        except Exception:
            return False

    # ---- System job management ----

    def install_system_job(self, workspace: Path) -> bool:
        """Install a launchd plist (macOS) or crontab entry (Linux).

        The job runs: /opt/homebrew/bin/python3 -m moltassist.poll --workspace <path>
        every 1 minute.
        Returns True on success.
        """
        system = platform.system()
        if system == "Darwin":
            return self._install_launchd(workspace)
        elif system == "Linux":
            return self._install_crontab(workspace)
        return False

    def uninstall_system_job(self) -> bool:
        """Remove the launchd plist or crontab entry."""
        system = platform.system()
        if system == "Darwin":
            return self._uninstall_launchd()
        elif system == "Linux":
            return self._uninstall_crontab()
        return False

    def job_is_installed(self) -> bool:
        """Check if the system job is currently installed."""
        system = platform.system()
        if system == "Darwin":
            return PLIST_PATH.exists()
        elif system == "Linux":
            return self._crontab_entry_exists()
        return False

    # ---- macOS launchd ----

    def _install_launchd(self, workspace: Path) -> bool:
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>{PLIST_LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/opt/homebrew/bin/python3</string>
    <string>-m</string>
    <string>moltassist.poll</string>
    <string>--workspace</string>
    <string>{workspace}</string>
  </array>
  <key>StartInterval</key>
  <integer>60</integer>
  <key>StandardOutPath</key>
  <string>{workspace / "memory" / "moltassist-poll.log"}</string>
  <key>StandardErrorPath</key>
  <string>{workspace / "memory" / "moltassist-poll.log"}</string>
  <key>WorkingDirectory</key>
  <string>{workspace}</string>
</dict>
</plist>
"""
        try:
            PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
            PLIST_PATH.write_text(plist_content)

            # Load the plist
            subprocess.run(
                ["launchctl", "load", str(PLIST_PATH)],
                timeout=10,
                capture_output=True,
            )
            return True
        except Exception:
            return False

    def _uninstall_launchd(self) -> bool:
        try:
            if PLIST_PATH.exists():
                subprocess.run(
                    ["launchctl", "unload", str(PLIST_PATH)],
                    timeout=10,
                    capture_output=True,
                )
                PLIST_PATH.unlink()
            return True
        except Exception:
            return False

    # ---- Linux crontab ----

    def _get_crontab_lines(self) -> list[str]:
        try:
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode != 0:
                return []
            return result.stdout.splitlines()
        except Exception:
            return []

    def _crontab_entry_exists(self) -> bool:
        lines = self._get_crontab_lines()
        return any(CRONTAB_MARKER in line for line in lines)

    def _install_crontab(self, workspace: Path) -> bool:
        cron_cmd = (
            f"* * * * * /opt/homebrew/bin/python3 -m moltassist.poll "
            f"--workspace {workspace} {CRONTAB_MARKER}"
        )
        try:
            lines = self._get_crontab_lines()
            # Remove any existing moltassist entry
            lines = [l for l in lines if CRONTAB_MARKER not in l]
            lines.append(cron_cmd)
            new_crontab = "\n".join(lines) + "\n"

            proc = subprocess.run(
                ["crontab", "-"],
                input=new_crontab, text=True,
                capture_output=True, timeout=10,
            )
            return proc.returncode == 0
        except Exception:
            return False

    def _uninstall_crontab(self) -> bool:
        try:
            lines = self._get_crontab_lines()
            lines = [l for l in lines if CRONTAB_MARKER not in l]
            new_crontab = "\n".join(lines) + "\n" if lines else ""

            proc = subprocess.run(
                ["crontab", "-"],
                input=new_crontab, text=True,
                capture_output=True, timeout=10,
            )
            return proc.returncode == 0
        except Exception:
            return False
