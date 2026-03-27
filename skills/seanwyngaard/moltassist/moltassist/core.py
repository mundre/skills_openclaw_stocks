"""MoltAssist core -- lockfile and the full notify() pipeline."""

import os
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from moltassist.config import load_config, get_category_config, URGENCY_LEVELS
from moltassist.log import append_log, make_log_entry, query_log
from moltassist.dedup import is_duplicate, _generate_event_id
from moltassist.formatter import format_for_telegram, format_for_whatsapp
from moltassist.channels import deliver_telegram, deliver_whatsapp
from moltassist.queue import enqueue
from moltassist import llm as llm_module
from moltassist.context import ContextStore

LOCKFILE_PATH = Path(
    os.environ.get(
        "MOLTASSIST_LOCKFILE",
        os.path.join(
            os.environ.get("OPENCLAW_WORKSPACE", str(Path.home() / ".openclaw" / "workspace")),
            "memory",
            "moltassist.lock",
        ),
    )
)


# --- Lockfile ---

class Lock:
    """Context manager for single-instance lockfile."""

    def __init__(self, path: Path | None = None):
        self.path = path or LOCKFILE_PATH

    def __enter__(self):
        acquire_lock(self.path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        release_lock(self.path)
        return False


def acquire_lock(path: Path | None = None) -> None:
    """Create lockfile. Raises RuntimeError if it already exists."""
    lock = path or LOCKFILE_PATH
    if lock.exists():
        raise RuntimeError(f"MoltAssist lock already held: {lock}")
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(str(os.getpid()))


def release_lock(path: Path | None = None) -> None:
    """Remove lockfile."""
    lock = path or LOCKFILE_PATH
    if lock.exists():
        lock.unlink()


# --- Pipeline helpers ---

def _urgency_rank(urgency: str) -> int:
    """Return numeric rank for urgency level (0=low, 3=critical)."""
    try:
        return URGENCY_LEVELS.index(urgency)
    except ValueError:
        return 0


def _is_quiet_hours(config: dict) -> bool:
    """Check if current time falls within quiet hours."""
    schedule = config.get("schedule", {})
    qh = schedule.get("quiet_hours", {})
    start_str = qh.get("start", "23:00")
    end_str = qh.get("end", "08:00")
    tz_name = schedule.get("timezone", "UTC")

    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("UTC")

    try:
        now = datetime.now(tz=tz)
        start = datetime.strptime(start_str, "%H:%M").time()
        end = datetime.strptime(end_str, "%H:%M").time()
    except ValueError:
        return False

    current = now.time()
    if start > end:
        # Crosses midnight: e.g., 23:00 to 08:00
        return current >= start or current < end
    else:
        return start <= current < end


def _check_rate_limit(category: str, config: dict, log_path=None) -> bool:
    """Return True if rate limit is exceeded for this category."""
    schedule = config.get("schedule", {})
    rl = schedule.get("rate_limits", {})
    max_per_cat = rl.get("per_category_per_hour", 3)

    recent = query_log(category=category, hours=1, log_path=log_path)
    delivered = [e for e in recent if e.get("delivered")]
    return len(delivered) >= max_per_cat


def _pick_channel(urgency: str, config: dict) -> str:
    """Pick delivery channel based on urgency routing config."""
    delivery = config.get("delivery", {})
    routing = delivery.get("urgency_routing", {})
    return routing.get(urgency, delivery.get("default_channel", "telegram"))


def _format_message(message: str, urgency: str, category: str,
                    action_hint: str | None, channel: str) -> str:
    """Format message for the target channel."""
    if channel == "whatsapp":
        return format_for_whatsapp(message, urgency, category, action_hint)
    # Default: Telegram
    return format_for_telegram(message, urgency, category, action_hint)


def _deliver(formatted: str, channel: str, channel_config: dict,
             buttons: list[list[dict]] | None = None) -> tuple[bool, str | None]:
    """Send via the chosen channel. Returns (success, error)."""
    if channel == "telegram":
        # Prefer chat_id from MoltAssist delivery config; fall back to channel_config
        chat_id = (
            channel_config.get("delivery", {})
                         .get("channels", {})
                         .get("telegram", {})
                         .get("chat_id", "")
            or channel_config.get("chat_id", "")
        )
        if not chat_id:
            return (False, "Telegram chat_id not configured. Run 'moltassist config set delivery.channels.telegram.chat_id <your_chat_id>'")
        return deliver_telegram(formatted, chat_id, buttons=buttons)
    elif channel == "whatsapp":
        target = (
            channel_config.get("delivery", {})
                         .get("channels", {})
                         .get("whatsapp", {})
                         .get("target", "")
            or channel_config.get("target", "")
        )
        return deliver_whatsapp(formatted, target=target or None)
    return (False, f"Unknown channel: {channel}")


# --- Main pipeline ---

def notify(
    message: str,
    urgency: str = "medium",
    category: str = "custom",
    source: str = "unknown",
    action_hint: str | None = None,
    llm_hint: bool = False,
    event_id: str | None = None,
    dry_run: bool = False,
    buttons: list[list[dict]] | None = None,
    config_path=None,
    log_path=None,
    lock_path=None,
    queue_path=None,
) -> dict:
    """Run the full notification pipeline.

    Returns dict: {sent, channel, queued, dry_run, error, buttons_sent}
    """
    result = {"sent": False, "channel": None, "queued": False,
              "dry_run": dry_run, "error": None, "buttons_sent": False}

    # Step 1: Config load -- category enabled? Urgency threshold met?
    config = load_config(path=config_path)
    cat_config = get_category_config(category, config)

    if not cat_config.get("enabled", False):
        result["error"] = f"Category '{category}' is disabled"
        return result

    # Step 1.5: Snooze check -- skip if category is snoozed (unless critical)
    if urgency != "critical":
        snoozes = config.get("snooze", {})
        snooze_entry = snoozes.get(category)
        if snooze_entry:
            until_str = snooze_entry.get("until", "")
            try:
                until = datetime.fromisoformat(until_str)
                if until.tzinfo is None:
                    until = until.replace(tzinfo=timezone.utc)
                if until > datetime.now(timezone.utc):
                    result["error"] = f"Category '{category}' is snoozed until {until_str}"
                    return result
            except (ValueError, TypeError):
                pass  # Invalid snooze entry -- ignore it

    global_threshold = config.get("urgency_threshold", "medium")
    cat_threshold = cat_config.get("urgency_threshold", global_threshold)
    if _urgency_rank(urgency) < _urgency_rank(cat_threshold):
        result["error"] = f"Urgency '{urgency}' below threshold '{cat_threshold}'"
        return result

    # Step 2: Acquire lockfile
    lock = lock_path or LOCKFILE_PATH
    try:
        acquire_lock(lock)
    except RuntimeError as e:
        result["error"] = str(e)
        return result

    try:
        # Step 3: Quiet hours -- queue if inside window (unless critical)
        if _is_quiet_hours(config) and urgency != "critical":
            now = datetime.now(timezone.utc)
            entry = {
                "timestamp": now.isoformat(),
                "category": category,
                "urgency": urgency,
                "source": source,
                "message": message,
                "action_hint": action_hint,
                "event_id": event_id,
                "llm_hint": llm_hint,
            }
            enqueue(entry, queue_path=queue_path)
            result["queued"] = True
            return result

        # Step 4: Rate limiter
        if _check_rate_limit(category, config, log_path=log_path):
            result["error"] = f"Rate limit exceeded for category '{category}'"
            return result

        # Step 5: Dedup check
        if event_id is None:
            ts_hour = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H")
            event_id = _generate_event_id(message, category, ts_hour)

        if is_duplicate(event_id, log_path=log_path):
            result["sent"] = False
            result["error"] = "duplicate"
            return result

        # Step 6: LLM enrichment -- enrich() returns str, falls back to original on failure
        enriched_message = message
        llm_enriched = False
        if llm_hint and config.get("llm_mode", "none") != "none":
            try:
                # Optionally prepend cross-channel context for LLM awareness
                context_prefix = ""
                channel_sync = config.get("channel_sync", {})
                if channel_sync.get("enabled", False):
                    try:
                        ctx = ContextStore()
                        context_prefix = ctx.get_recent_context(hours=2)
                    except Exception:
                        pass

                result_text = llm_module.enrich(
                    message, category,
                    action_hint=action_hint,
                    context_prefix=context_prefix if context_prefix else None,
                )
                if result_text and result_text != message:
                    enriched_message = result_text
                    llm_enriched = True
            except Exception:
                # Timeout or failure -- use raw message
                pass

        # Step 7: Channel router
        channel = _pick_channel(urgency, config)
        result["channel"] = channel

        # Step 8: Format for platform
        formatted = _format_message(enriched_message, urgency, category, action_hint, channel)

        # Step 9: Send (or dry run)
        if dry_run:
            log_entry = make_log_entry(
                category=category, urgency=urgency, source=source,
                message=enriched_message, delivered=False,
                channel_used=channel, llm_enriched=llm_enriched,
                event_id=event_id,
            )
            append_log(log_entry, log_path=log_path)
            result["sent"] = False
            return result

        success, error = _deliver(formatted, channel, config, buttons=buttons)

        if success:
            result["buttons_sent"] = buttons is not None and len(buttons) > 0
            # Step 11: Log success
            log_entry = make_log_entry(
                category=category, urgency=urgency, source=source,
                message=enriched_message, delivered=True,
                channel_used=channel, llm_enriched=llm_enriched,
                event_id=event_id,
            )
            append_log(log_entry, log_path=log_path)
            result["sent"] = True

            # Channel Sync: record activity for cross-channel awareness
            channel_sync = config.get("channel_sync", {})
            if channel_sync.get("enabled", False):
                try:
                    ctx = ContextStore()
                    ctx.record_activity(
                        channel=channel,
                        summary=f"[{category}/{urgency}] {message[:120]}",
                    )
                except Exception:
                    pass  # Channel sync is best-effort, never block delivery
        else:
            # Step 10: Log failure.
            # IMPORTANT: Clear the queue on permanent send failure.
            # A stuck queue is worse than a missed message -- if we leave a failed
            # item in the queue, every subsequent check skips ("queue has a message")
            # and nothing gets delivered for hours. Clear it, log the failure, move on.
            from moltassist.queue import dequeue_all as _clear_queue
            _clear_queue(queue_path=queue_path)

            log_entry = make_log_entry(
                category=category, urgency=urgency, source=source,
                message=enriched_message, delivered=False,
                channel_used=channel, llm_enriched=llm_enriched,
                event_id=event_id, error=error,
            )
            append_log(log_entry, log_path=log_path)
            result["error"] = error

    finally:
        # Step 12: Release lockfile
        release_lock(lock)

    return result
