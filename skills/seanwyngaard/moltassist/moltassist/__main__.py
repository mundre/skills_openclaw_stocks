"""MoltAssist CLI dispatcher.

Usage: python3 -m moltassist <command> [args...]

Commands:
  onboard                  Run the onboarding flow
  config                   Launch dashboard server on port 7430
  status                   Show enabled categories, channels, LLM mode
  log [category|urgency]   Show last 24h alerts (optionally filtered)
  snooze <cat> <duration>  Snooze a category (e.g. email 2h)
  snooze <cat> off         Clear snooze for a category
  test                     Fire a test notification through the full pipeline
  reload                   Reload config from disk
  uninstall                Remove scheduler, workspace files, and print removal steps
  scheduler install        Install launchd/cron system job
  scheduler uninstall      Remove system job
  scheduler status         Show scheduler status
  poll now <category>      Run a single poller immediately
"""

import sys
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path


def _get_workspace() -> Path:
    ws = os.environ.get("OPENCLAW_WORKSPACE") or os.path.expanduser("~/.openclaw/workspace")
    return Path(ws)


def _print_usage():
    print(__doc__.strip())


def cmd_onboard(args: list[str]) -> None:
    """Run the onboarding flow.

    NOTE: The full interactive onboarding is driven by the AI agent (via SKILL.md).
    This CLI command is a terminal fallback only.

    For the full experience with channel-native buttons, run /moltassist onboard
    from your Telegram/WhatsApp/Discord/iMessage chat -- the agent handles everything.
    """
    from moltassist.onboard import start_onboarding
    from moltassist.config import _get_config_path

    config_path = _get_config_path()
    if config_path.exists() and "--reset" not in args:
        print(
            "MoltAssist is already configured.\n\n"
            "Run: moltassist onboard --reset  to start fresh\n"
            "     moltassist status           to see current setup\n"
            "     moltassist config           to open the dashboard"
        )
        return

    result = start_onboarding()
    print(result["message"])
    if result.get("buttons"):
        print(f"\nOptions: {', '.join(result['buttons'])}")
    print(
        "\n  For the full interactive flow with channel buttons,\n"
        "   run /moltassist onboard from your Telegram/WhatsApp/Discord/iMessage chat.\n"
        "   The AI agent will guide you step by step on your channel."
    )


def cmd_config(args: list[str]) -> None:
    """Launch the dashboard server."""
    from moltassist.server import start_server

    workspace = _get_workspace()
    port = 7430
    print(f"Starting MoltAssist dashboard on http://localhost:{port}")
    print("The server will auto-close after 30 minutes of inactivity.")
    start_server(workspace=workspace, port=port)


def cmd_status(args: list[str]) -> None:
    """Show current config status."""
    from moltassist.config import load_config

    config = load_config()

    # Enabled categories
    categories = config.get("categories", {})
    enabled = [cat for cat, cfg in categories.items() if cfg.get("enabled")]
    disabled = [cat for cat, cfg in categories.items() if not cfg.get("enabled")]

    print(" MoltAssist Status\n")

    print(f" Enabled: {', '.join(enabled) if enabled else 'none'}")
    print(f"  Disabled: {', '.join(disabled) if disabled else 'none'}")

    # Snooze status
    snoozes = config.get("snooze", {})
    now = datetime.now(timezone.utc)
    active_snoozes = []
    for cat, snz in snoozes.items():
        until_str = snz.get("until", "")
        try:
            until = datetime.fromisoformat(until_str)
            if until.tzinfo is None:
                until = until.replace(tzinfo=timezone.utc)
            if until > now:
                remaining = until - now
                mins = int(remaining.total_seconds() / 60)
                active_snoozes.append(f"{cat} (snoozed for {mins}m)")
        except (ValueError, TypeError):
            pass

    if active_snoozes:
        print(f" Snoozed: {', '.join(active_snoozes)}")

    # Channels
    delivery = config.get("delivery", {})
    default_ch = delivery.get("default_channel", "telegram")
    channels = delivery.get("channels", {})
    active_channels = [ch for ch, cfg in channels.items() if cfg.get("active")]
    print(f"\n Default channel: {default_ch}")
    print(f"   Active channels: {', '.join(active_channels) if active_channels else 'none'}")

    # Urgency routing
    routing = delivery.get("urgency_routing", {})
    if routing:
        routing_str = ", ".join(f"{u}->{ch}" for u, ch in routing.items())
        print(f"   Routing: {routing_str}")

    # LLM mode
    llm_mode = config.get("llm_mode", "none")
    print(f"\n LLM mode: {llm_mode}")

    # Schedule
    schedule = config.get("schedule", {})
    qh = schedule.get("quiet_hours", {})
    print(f"\n Quiet hours: {qh.get('start', '?')}-{qh.get('end', '?')}")
    print(f" Timezone: {schedule.get('timezone', '?')}")

    # Polling
    polling = schedule.get("polling", {})
    if polling:
        print("\n Polling:")
        for cat, pcfg in sorted(polling.items()):
            status = "" if pcfg.get("enabled") else ""
            interval = pcfg.get("interval_minutes", "?")
            print(f"   {status} {cat}: every {interval}m")


def cmd_log(args: list[str]) -> None:
    """Show recent alerts from the log."""
    from moltassist.config import URGENCY_LEVELS
    from moltassist.log import query_log, format_log_summary

    category = None
    urgency = None

    if args:
        arg = args[0].lower()
        if arg in URGENCY_LEVELS:
            urgency = arg
        else:
            category = arg

    entries = query_log(category=category, urgency=urgency, hours=24)
    print(format_log_summary(entries))


def cmd_snooze(args: list[str]) -> None:
    """Snooze or unsnooze a category."""
    from moltassist.config import load_config, save_config, CATEGORIES

    if len(args) < 2:
        print("Usage: moltassist snooze <category> <duration|off>")
        print(f"Categories: {', '.join(CATEGORIES)}")
        print("Duration examples: 30m, 1h, 2h, 6h, 1d")
        return

    category = args[0].lower()
    duration_str = args[1].lower()

    config = load_config()

    if "snooze" not in config:
        config["snooze"] = {}

    if duration_str == "off":
        if category in config["snooze"]:
            del config["snooze"][category]
            save_config(config)
            print(f" Snooze cleared for {category}")
        else:
            print(f"  {category} wasn't snoozed")
        return

    # Parse duration
    delta = _parse_duration(duration_str)
    if delta is None:
        print(f" Invalid duration: {duration_str}")
        print("Examples: 30m, 1h, 2h, 6h, 1d")
        return

    until = datetime.now(timezone.utc) + delta
    config["snooze"][category] = {"until": until.isoformat()}
    save_config(config)

    local_until = until.astimezone()
    print(f" {category} snoozed until {local_until.strftime('%H:%M')} ({duration_str})")


def _parse_duration(s: str) -> timedelta | None:
    """Parse a human duration like 30m, 2h, 1d into a timedelta."""
    s = s.strip().lower()
    try:
        if s.endswith("m"):
            return timedelta(minutes=int(s[:-1]))
        elif s.endswith("h"):
            return timedelta(hours=int(s[:-1]))
        elif s.endswith("d"):
            return timedelta(days=int(s[:-1]))
        else:
            # Try as minutes
            return timedelta(minutes=int(s))
    except (ValueError, TypeError):
        return None


def cmd_test(args: list[str]) -> None:
    """Fire a test notification through the full pipeline."""
    from moltassist.core import notify

    result = notify(
        message="MoltAssist test notification",
        urgency="high",
        category="system",
        source="moltassist_test",
        dry_run=False,
    )

    if result.get("sent"):
        print(f" Test notification sent via {result.get('channel', '?')}")
    elif result.get("queued"):
        print(" Test notification queued (quiet hours active)")
    elif result.get("error"):
        print(f" Test failed: {result['error']}")
    else:
        print(f"  Result: {result}")


def cmd_uninstall(args: list[str]) -> None:
    """Full uninstall -- scheduler, workspace files, and skill."""
    import shutil

    print("Uninstalling MoltAssist...\n")

    # Step 1 -- Scheduler
    from moltassist.scheduler import Scheduler
    scheduler = Scheduler()
    if scheduler.job_is_installed():
        success = scheduler.uninstall_system_job()
        print(" Scheduler removed" if success else "  Scheduler removal failed -- remove manually")
    else:
        print(" Scheduler not installed -- skipping")

    # Step 2 -- Workspace files
    workspace = _get_workspace()
    files_to_remove = [
        workspace / "moltassist" / "memory" / "moltassist-log.json",
        workspace / "moltassist" / "memory" / "moltassist-queue.json",
        workspace / "moltassist" / "memory" / "moltassist-context.json",
        workspace / "moltassist" / "memory" / "moltassist-build-state.json",
        workspace / "memory" / "moltassist-schedule-state.json",
        workspace / "memory" / "moltassist-poll.log",
        workspace / "moltassist" / "config.json",
    ]
    removed = []
    for f in files_to_remove:
        if f.exists():
            f.unlink()
            removed.append(f.name)

    custom_pollers = workspace / "moltassist" / "custom_pollers"
    if custom_pollers.exists():
        shutil.rmtree(custom_pollers)
        removed.append("custom_pollers/")

    if removed:
        print(f" Workspace files removed: {', '.join(removed)}")
    else:
        print(" No workspace files found -- already clean")

    # Step 3 -- Skill
    print("\n Python package: run `uv tool uninstall moltassist` to remove the binary")
    print(" Skill: run `clawhub uninstall moltassist` to remove from OpenClaw\n")
    print("MoltAssist fully uninstalled. Your OpenClaw config and channels are untouched.")


def cmd_reload(args: list[str]) -> None:
    """Reload config from disk."""
    from moltassist.config import load_config, validate_config

    try:
        config = load_config()
        validate_config(config)
        cats = config.get("categories", {})
        enabled = sum(1 for c in cats.values() if c.get("enabled"))
        print(f" Config reloaded -- {enabled} categories enabled, {len(cats)} total")
    except Exception as e:
        print(f" Config error: {e}")


def cmd_scheduler(args: list[str]) -> None:
    """Manage the system scheduler."""
    from moltassist.scheduler import Scheduler

    if not args:
        print("Usage: moltassist scheduler <install|uninstall|status>")
        return

    subcmd = args[0].lower()
    scheduler = Scheduler()
    workspace = _get_workspace()

    if subcmd == "install":
        success = scheduler.install_system_job(workspace)
        if success:
            print(" Scheduler installed -- MoltAssist will poll automatically")
        else:
            print(" Scheduler install failed")

    elif subcmd == "uninstall":
        success = scheduler.uninstall_system_job()
        if success:
            print(" Scheduler uninstalled")
        else:
            print(" Scheduler uninstall failed")

    elif subcmd == "status":
        installed = scheduler.job_is_installed()
        print(f" Scheduler: {'installed' if installed else 'not installed'}")

        # Show last run per category
        state = scheduler._load_state()
        last_runs = state.get("lastRun", {})
        if last_runs:
            print("\nLast run times:")
            for cat, ts in sorted(last_runs.items()):
                try:
                    dt = datetime.fromtimestamp(ts)
                    ago = datetime.now() - dt
                    mins = int(ago.total_seconds() / 60)
                    print(f"  {cat}: {dt.strftime('%H:%M:%S')} ({mins}m ago)")
                except (ValueError, TypeError, OSError):
                    print(f"  {cat}: {ts}")
        else:
            print("\nNo poll runs recorded yet.")

    else:
        print(f"Unknown scheduler command: {subcmd}")
        print("Usage: moltassist scheduler <install|uninstall|status>")


def cmd_poll_now(args: list[str]) -> None:
    """Run a single poller immediately."""
    from moltassist.poll import run_single, POLLERS

    if not args:
        print("Usage: moltassist poll now <category>")
        print(f"Available pollers: {', '.join(POLLERS.keys())}")
        return

    category = args[0].lower()
    workspace = _get_workspace()
    run_single(category, workspace=workspace)


def main():
    args = sys.argv[1:]

    # Auto-redirect to onboarding if config doesn't exist yet
    from moltassist.config import _get_config_path
    config_path = _get_config_path()
    if not config_path.exists() and (not args or args[0].lower() not in ("onboard", "uninstall")):
        print("MoltAssist isn't configured yet. Starting onboarding...\n")
        cmd_onboard([])
        return

    if not args:
        _print_usage()
        return

    command = args[0].lower()
    rest = args[1:]

    dispatch = {
        "onboard": cmd_onboard,
        "config": cmd_config,
        "status": cmd_status,
        "log": cmd_log,
        "snooze": cmd_snooze,
        "test": cmd_test,
        "reload": cmd_reload,
        "uninstall": cmd_uninstall,
        "scheduler": cmd_scheduler,
    }

    # Handle "poll now <cat>" as a special two-word command
    if command == "poll" and rest and rest[0].lower() == "now":
        cmd_poll_now(rest[1:])
        return

    handler = dispatch.get(command)
    if handler:
        handler(rest)
    else:
        print(f"Unknown command: {command}\n")
        _print_usage()


if __name__ == "__main__":
    main()
