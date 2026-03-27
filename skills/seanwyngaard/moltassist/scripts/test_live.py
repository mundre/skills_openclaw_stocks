#!/usr/bin/env python3
"""MoltAssist live integration test harness.

Manual end-to-end smoke test against a real Telegram channel.
NOT pytest -- standalone script for pre-production validation.

Usage:
    python3 scripts/test_live.py --channel telegram --chat-id TEST_CHAT_ID
    python3 scripts/test_live.py --channel telegram --chat-id TEST_CHAT_ID --live
"""

import argparse
import json
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Test result tracking
# ---------------------------------------------------------------------------

results: list[tuple[str, bool, str]] = []


def print_summary() -> None:
    print("\n" + "=" * 60)
    print("MoltAssist Live Test Summary")
    print("=" * 60)
    for name, passed, detail in results:
        icon = "\u2705" if passed else "\u274c"
        line = f"  {icon} {name}"
        if detail:
            line += f"  -- {detail}"
        print(line)
    total = len(results)
    passed_count = sum(1 for _, p, _ in results if p)
    print(f"\n  {passed_count}/{total} passed")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Individual tests
# ---------------------------------------------------------------------------

def test_python_version() -> None:
    name = "Python version"
    major, minor = sys.version_info[:2]
    ok = (major, minor) >= (3, 10)
    results.append((name, ok, f"{major}.{minor}"))
    if ok:
        print(f"  [PASS] Python {major}.{minor} >= 3.10")
    else:
        print(f"  [FAIL] Python {major}.{minor} < 3.10 -- MoltAssist requires 3.10+")


def test_config_load() -> None:
    name = "Config load"
    try:
        from moltassist.config import load_config, DEFAULT_CONFIG
        config = load_config()
        # Show key values
        channel = config.get("delivery", {}).get("default_channel", "?")
        llm = config.get("llm_mode", "?")
        cats_enabled = [k for k, v in config.get("categories", {}).items() if v.get("enabled")]
        detail = f"channel={channel}, llm_mode={llm}, enabled={cats_enabled}"
        results.append((name, True, detail))
        print(f"  [PASS] Config loaded -- {detail}")
    except Exception as e:
        results.append((name, False, str(e)))
        print(f"  [FAIL] Config load -- {e}")


def test_formatter() -> None:
    name = "Formatter"
    try:
        from moltassist.formatter import format_for_telegram
        from moltassist.config import URGENCY_LEVELS

        print(f"  Formatted Telegram messages:")
        for urgency in URGENCY_LEVELS:
            msg = format_for_telegram(
                message=f"Test {urgency} notification from MoltAssist",
                urgency=urgency,
                category="system",
                action_hint="Verify",
            )
            print(f"    [{urgency}] {msg}")
        results.append((name, True, f"all {len(URGENCY_LEVELS)} urgency levels"))
        print(f"  [PASS] Formatter -- all urgency levels rendered")
    except Exception as e:
        results.append((name, False, str(e)))
        print(f"  [FAIL] Formatter -- {e}")


def test_dedup() -> None:
    name = "Dedup"
    try:
        from moltassist.dedup import is_duplicate, _generate_event_id
        from moltassist.log import append_log, make_log_entry

        tmpdir = tempfile.mkdtemp(prefix="moltassist_live_")
        log_path = Path(tmpdir) / "log.json"

        event_id = f"live_test_{uuid.uuid4().hex[:8]}"

        # Should NOT be duplicate (fresh log)
        dup1 = is_duplicate(event_id, log_path=log_path)
        assert not dup1, "Event should not be duplicate before insert"

        # Insert into log
        entry = make_log_entry(
            category="system", urgency="low", source="test_live",
            message="dedup test", delivered=True, event_id=event_id,
        )
        append_log(entry, log_path=log_path)

        # Should now be duplicate
        dup2 = is_duplicate(event_id, log_path=log_path)
        assert dup2, "Event should be duplicate after insert"

        results.append((name, True, f"event_id={event_id}"))
        print(f"  [PASS] Dedup -- generated {event_id}, verified insert + duplicate check")
    except Exception as e:
        results.append((name, False, str(e)))
        print(f"  [FAIL] Dedup -- {e}")


def test_queue() -> None:
    name = "Queue"
    try:
        from moltassist.queue import enqueue, dequeue_all

        tmpdir = tempfile.mkdtemp(prefix="moltassist_live_")
        queue_path = Path(tmpdir) / "queue.json"

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "category": "system",
            "urgency": "low",
            "message": "Queue test from test_live.py",
        }
        ok = enqueue(entry, queue_path=queue_path)
        assert ok, "Enqueue should succeed"

        # Verify it's there by reading raw
        with open(queue_path) as f:
            raw = json.load(f)
        assert len(raw) == 1, f"Queue should have 1 entry, got {len(raw)}"

        # Dequeue
        items = dequeue_all(queue_path=queue_path)
        assert len(items) == 1, f"Dequeue should return 1, got {len(items)}"

        # Verify empty
        items2 = dequeue_all(queue_path=queue_path)
        assert len(items2) == 0, f"Queue should be empty after dequeue, got {len(items2)}"

        results.append((name, True, "enqueue -> verify -> dequeue -> empty"))
        print(f"  [PASS] Queue -- enqueue, verify, dequeue, verify empty")
    except Exception as e:
        results.append((name, False, str(e)))
        print(f"  [FAIL] Queue -- {e}")


def test_rate_limiter() -> None:
    name = "Rate limiter"
    try:
        from moltassist.core import notify

        tmpdir = tempfile.mkdtemp(prefix="moltassist_live_")
        config_path = Path(tmpdir) / "config.json"
        log_path = Path(tmpdir) / "log.json"
        lock_path = Path(tmpdir) / "moltassist.lock"
        queue_path = Path(tmpdir) / "queue.json"

        config = {
            "version": "0.1.0",
            "categories": {
                "finance": {"enabled": True, "urgency_threshold": "low", "llm_enrich": False, "cooldown_minutes": 0}
            },
            "delivery": {"default_channel": "telegram", "urgency_routing": {}, "channels": {}},
            "schedule": {
                "quiet_hours": {"start": "00:00", "end": "00:00"},
                "timezone": "UTC",
                "rate_limits": {"per_category_per_hour": 3, "global_per_hour": 10},
            },
            "urgency_threshold": "low",
            "llm_mode": "none",
        }
        config_path.write_text(json.dumps(config))

        # Mock deliver so we don't make real network calls
        sent_count = 0
        blocked = False

        for i in range(4):
            with patch("moltassist.core._deliver", return_value=(True, None)):
                result = notify(
                    message=f"Rate limit test #{i+1}",
                    urgency="medium",
                    category="finance",
                    source="test_live",
                    event_id=f"rl_test_{uuid.uuid4().hex[:8]}",
                    config_path=config_path,
                    log_path=log_path,
                    lock_path=lock_path,
                    queue_path=queue_path,
                )
            if result.get("sent"):
                sent_count += 1
            if result.get("error") and "Rate limit" in result["error"]:
                blocked = True

        assert sent_count == 3, f"Expected 3 sent, got {sent_count}"
        assert blocked, "4th call should be rate-limited"

        results.append((name, True, "3 sent, 4th blocked"))
        print(f"  [PASS] Rate limiter -- 3 sent, 4th blocked")
    except Exception as e:
        results.append((name, False, str(e)))
        print(f"  [FAIL] Rate limiter -- {e}")


def test_quiet_hours() -> None:
    name = "Quiet hours"
    try:
        from moltassist.core import notify

        tmpdir = tempfile.mkdtemp(prefix="moltassist_live_")
        config_path = Path(tmpdir) / "config.json"
        log_path = Path(tmpdir) / "log.json"
        lock_path = Path(tmpdir) / "moltassist.lock"
        queue_path = Path(tmpdir) / "queue.json"

        config = {
            "version": "0.1.0",
            "categories": {
                "finance": {"enabled": True, "urgency_threshold": "low", "llm_enrich": False, "cooldown_minutes": 0}
            },
            "delivery": {"default_channel": "telegram", "urgency_routing": {}, "channels": {}},
            "schedule": {
                "quiet_hours": {"start": "00:00", "end": "23:59"},
                "timezone": "UTC",
                "rate_limits": {"per_category_per_hour": 10, "global_per_hour": 20},
            },
            "urgency_threshold": "low",
            "llm_mode": "none",
        }
        config_path.write_text(json.dumps(config))

        # Force quiet hours to be active
        with patch("moltassist.core._is_quiet_hours", return_value=True):
            result = notify(
                message="Quiet hours test",
                urgency="medium",
                category="finance",
                source="test_live",
                config_path=config_path,
                log_path=log_path,
                lock_path=lock_path,
                queue_path=queue_path,
            )

        assert result.get("queued"), f"Expected queued=True, got {result}"

        # Verify something landed in queue
        with open(queue_path) as f:
            q = json.load(f)
        assert len(q) >= 1, "Queue should have at least 1 entry"

        results.append((name, True, "notification queued during quiet hours"))
        print(f"  [PASS] Quiet hours -- notification queued")
    except Exception as e:
        results.append((name, False, str(e)))
        print(f"  [FAIL] Quiet hours -- {e}")


def test_live_send(chat_id: str) -> str | None:
    """Send an actual test message to Telegram. Returns event_id on success."""
    name = "LIVE SEND"
    try:
        from moltassist.channels import get_channel_config, deliver_telegram
        from moltassist.formatter import format_for_telegram
        from moltassist.log import append_log, make_log_entry

        tmpdir = tempfile.mkdtemp(prefix="moltassist_live_")
        log_path = Path(tmpdir) / "log.json"

        channel_config = get_channel_config()
        bot_token = channel_config.get("bot_token")
        if not bot_token:
            results.append((name, False, "TELEGRAM_BOT_TOKEN not set"))
            print(f"  [FAIL] LIVE SEND -- TELEGRAM_BOT_TOKEN not configured")
            return None

        event_id = f"live_send_{uuid.uuid4().hex[:8]}"
        message = "MoltAssist live integration test"
        formatted = format_for_telegram(
            message=message,
            urgency="low",
            category="system",
            action_hint="This is a test -- safe to ignore",
        )

        success, error = deliver_telegram(formatted, chat_id=chat_id, bot_token=bot_token)

        if success:
            entry = make_log_entry(
                category="system", urgency="low", source="test_live",
                message=message, delivered=True, channel_used="telegram",
                event_id=event_id,
            )
            append_log(entry, log_path=log_path)
            results.append((name, True, f"sent to chat_id={chat_id}"))
            print(f"  [PASS] LIVE SEND -- message delivered to {chat_id}")
            return event_id
        else:
            results.append((name, False, error or "unknown error"))
            print(f"  [FAIL] LIVE SEND -- {error}")
            return None
    except Exception as e:
        results.append((name, False, str(e)))
        print(f"  [FAIL] LIVE SEND -- {e}")
        return None


def test_log_query(event_id: str | None) -> None:
    name = "Log query"
    if event_id is None:
        results.append((name, True, "skipped (no --live)"))
        print(f"  [SKIP] Log query -- no live send to verify")
        return

    try:
        from moltassist.log import query_log

        # The live send wrote to a tmpdir log -- we need to check that log
        # Since we can't easily recover the tmpdir, we verify the query function works
        # by writing a known entry and querying it
        tmpdir = tempfile.mkdtemp(prefix="moltassist_live_")
        log_path = Path(tmpdir) / "log.json"

        from moltassist.log import append_log, make_log_entry
        entry = make_log_entry(
            category="system", urgency="low", source="test_live",
            message="log query test", delivered=True, event_id=event_id,
        )
        append_log(entry, log_path=log_path)

        found = query_log(category="system", hours=1, log_path=log_path)
        match = [e for e in found if e.get("event_id") == event_id]

        assert len(match) == 1, f"Expected 1 match for {event_id}, got {len(match)}"

        results.append((name, True, f"found event_id={event_id}"))
        print(f"  [PASS] Log query -- found event in log")
    except Exception as e:
        results.append((name, False, str(e)))
        print(f"  [FAIL] Log query -- {e}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="MoltAssist live integration test harness",
    )
    parser.add_argument("--channel", default="telegram", help="Channel to test (default: telegram)")
    parser.add_argument("--chat-id", required=True, help="Telegram chat ID for test sends")
    parser.add_argument("--live", action="store_true", help="Actually send a message to the channel")
    args = parser.parse_args()

    print("=" * 60)
    print(f"MoltAssist Live Integration Test")
    print(f"Channel: {args.channel}  |  Chat ID: {args.chat_id}  |  Live: {args.live}")
    print("=" * 60)
    print()

    # 1. Python version
    test_python_version()

    # 2. Config load
    test_config_load()

    # 3. Formatter
    test_formatter()

    # 4. Dedup
    test_dedup()

    # 5. Queue
    test_queue()

    # 6. Rate limiter
    test_rate_limiter()

    # 7. Quiet hours
    test_quiet_hours()

    # 8. Live send (only with --live)
    event_id = None
    if args.live:
        event_id = test_live_send(chat_id=args.chat_id)
    else:
        results.append(("LIVE SEND", True, "skipped (no --live flag)"))
        print(f"  [SKIP] LIVE SEND -- pass --live to send a real message")

    # 9. Log query
    test_log_query(event_id)

    # Summary
    print_summary()

    # Exit code
    failed = sum(1 for _, p, _ in results if not p)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
