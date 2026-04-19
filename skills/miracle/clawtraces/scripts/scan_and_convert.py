# FILE_META
# INPUT:  OpenClaw session .jsonl files
# OUTPUT: {session_id}.trajectory.json + .stats.json + candidates.json
# POS:    skill scripts — Step 2, core pipeline, depends on all lib modules
# MISSION: Scan local sessions, filter by quality, convert to Anthropic trajectory format.

#!/usr/bin/env python3
"""Scan local OpenClaw sessions, filter, convert to trajectory format.

Merged scan + convert pipeline (V2). Outputs trajectory files (OpenAI format)
and a candidates list for agent semantic quality review.

Usage:
    python scan_and_convert.py [--sessions-dir PATH] [--output-dir PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))

from lib.session_index import find_openclaw_sessions_dirs, get_qualifying_sessions
from lib.dag import parse_jsonl, extract_conversation_chain, extract_richest_segment, count_turns, get_model_from_nodes, detect_file_encoding
from lib.converter import convert_to_trajectory
from lib.metadata_stripper import strip_metadata_prefix, is_system_startup_message
from lib.system_prompt_builder import extract_session_metadata, build_system_prompt
from lib.cache_trace import get_cache_trace_path, build_session_system_prompt_index
from lib.quality_checker import check_quality, extract_user_messages_for_review
from lib.paths import get_default_output_dir
from convert_to_openai import convert_trajectory as convert_to_openai_format

MIN_TURNS = 5
DEFAULT_OUTPUT_DIR = get_default_output_dir()
MANIFEST_FILENAME = "manifest.json"

# Limits for user_messages in candidates.json (semantic review only)
REVIEW_MAX_MESSAGES = 5    # keep first N user messages
REVIEW_MAX_CHARS = 300     # truncate each message to N chars


def _load_manifest(output_dir: str) -> dict:
    """Load manifest to check already-submitted and rejected sessions."""
    manifest_path = os.path.join(output_dir, MANIFEST_FILENAME)
    if os.path.isfile(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"submitted": {}, "rejected": {}}


def _save_manifest(output_dir: str, manifest: dict):
    """Save manifest (atomic write via tmp+rename)."""
    manifest_path = os.path.join(output_dir, MANIFEST_FILENAME)
    tmp_path = manifest_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, manifest_path)


def _get_skip_session_ids(output_dir: str) -> set[str]:
    """Get set of session IDs to skip (already submitted or rejected)."""
    manifest = _load_manifest(output_dir)
    submitted = manifest.get("submitted", {})
    rejected = manifest.get("rejected", {})
    # submitted keys are like "session_id.trajectory.json"
    ids = {k.replace(".trajectory.json", "") for k in submitted}
    # rejected keys are session_id directly
    ids.update(rejected.keys())
    return ids


def _extract_user_texts_and_tools(messages: list[dict]) -> tuple[list[str], list[str]]:
    """Extract user message texts and tool names from conversation chain."""
    user_texts = []
    tool_names = []

    for node in messages:
        if node.get("type") == "compaction":
            continue
        msg = node.get("message", {})
        role = msg.get("role")
        content = msg.get("content", [])

        if role == "user":
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text = block.get("text", "")
                    if not is_system_startup_message(text):
                        user_texts.append(strip_metadata_prefix(text))

        elif role == "assistant":
            for block in content:
                if isinstance(block, dict) and block.get("type") == "toolCall":
                    tool_names.append(block.get("name", ""))

    return user_texts, tool_names


def _extract_session_stats(nodes: list[dict], messages: list[dict]) -> dict:
    """Extract session-level stats from source data for upload alongside trajectory.

    These stats are NOT part of the trajectory training data — they are
    operational metrics sent as a separate field during upload.

    Counters (token_input/output, cache_*, tool_use_count, tool_names) are
    accumulated across the **entire file** (not just the selected segment),
    so the stats reflect total real interaction in the session even when
    compaction has collapsed many earlier turns out of the trajectory chain.
    `messages` is still used to derive `segment_*` diagnostic fields.
    """
    # Timestamps: first and last node
    started_at = nodes[0].get("timestamp") if nodes else None
    ended_at = nodes[-1].get("timestamp") if nodes else None

    token_input = 0
    token_output = 0
    cache_read = 0
    cache_write = 0
    tool_use_count = 0
    tool_name_set: set[str] = set()
    compaction_count = 0
    full_user_messages = 0

    for node in nodes:
        ntype = node.get("type")
        if ntype == "compaction":
            if node.get("summary"):
                compaction_count += 1
            continue
        if ntype != "message":
            continue
        msg = node.get("message", {})
        role = msg.get("role")

        if role == "assistant":
            usage = msg.get("usage", {})
            token_input += usage.get("input", 0)
            token_output += usage.get("output", 0)
            cache_read += usage.get("cacheRead", 0)
            cache_write += usage.get("cacheWrite", 0)
            for block in msg.get("content", []):
                if isinstance(block, dict) and block.get("type") == "toolCall":
                    tool_use_count += 1
                    name = block.get("name", "")
                    if name:
                        tool_name_set.add(name)
        elif role == "user":
            for block in msg.get("content", []):
                if isinstance(block, dict) and block.get("type") == "text":
                    raw = block.get("text", "")
                    if is_system_startup_message(raw):
                        continue
                    if strip_metadata_prefix(raw):
                        full_user_messages += 1

    # Segment-level diagnostic counters (reflect only the chosen trajectory chain)
    segment_turns = 0
    segment_user_messages = 0
    for node in messages:
        if node.get("type") == "compaction":
            continue
        msg = node.get("message", {})
        role = msg.get("role")
        if role == "assistant":
            segment_turns += 1
        elif role == "user":
            for block in msg.get("content", []):
                if isinstance(block, dict) and block.get("type") == "text":
                    raw = block.get("text", "")
                    if is_system_startup_message(raw):
                        continue
                    if strip_metadata_prefix(raw):
                        segment_user_messages += 1

    return {
        "started_at": started_at,
        "ended_at": ended_at,
        "token_input": token_input,
        "token_output": token_output,
        "cache_read": cache_read,
        "cache_write": cache_write,
        "tool_use_count": tool_use_count,
        "tool_names": sorted(tool_name_set),
        "compaction_count": compaction_count,
        "full_user_messages": full_user_messages,
        "segment_turns": segment_turns,
        "segment_user_messages": segment_user_messages,
    }


def _compute_prefix_hash(messages: list[dict], n: int = 5) -> str:
    """Compute hash of first N user messages for prefix deduplication.

    Strips metadata prefixes before hashing so that the same message
    sent via different channels (TUI vs Telegram) produces the same hash.
    """
    user_texts = []
    for node in messages:
        if node.get("type") == "compaction":
            continue
        msg = node.get("message", {})
        if msg.get("role") == "user":
            content = msg.get("content", [])
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    raw = block.get("text", "")
                    if not is_system_startup_message(raw):
                        user_texts.append(strip_metadata_prefix(raw))
                    break
        if len(user_texts) >= n:
            break

    combined = "\n---\n".join(user_texts)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()[:16]


def _topic_from_messages(messages: list[dict], max_len: int = 80) -> str:
    """Extract topic from already-parsed message nodes."""
    for node in messages:
        if node.get("type") != "message":
            continue
        msg = node.get("message", {})
        if msg.get("role") != "user":
            continue
        for block in msg.get("content", []):
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "")
                if is_system_startup_message(text):
                    break
                text = strip_metadata_prefix(text)
                if text:
                    text = " ".join(text.split())
                    return text[:max_len] + "..." if len(text) > max_len else text
                break
    return ""


def _infer_domain(tool_names: list[str], user_texts: list[str]) -> str:
    """Infer domain from tool usage patterns and user message keywords."""
    tool_set = set(t.lower() for t in tool_names)
    combined_text = " ".join(user_texts[:3]).lower()

    code_tools = {"edit", "write", "grep", "find", "apply_patch"}
    web_tools = {"web_search", "web_fetch"}
    msg_tools = {"message"}
    media_tools = {"image", "image_generate", "tts", "pdf"}
    session_tools = {"sessions_spawn", "sessions_send", "subagents"}
    cron_tools = {"cron"}
    monitor_keywords = {"monitor", "监控", "告警", "health", "status check"}

    has_code = bool(tool_set & code_tools)
    has_web = bool(tool_set & web_tools)
    has_browser = "browser" in tool_set
    has_msg = bool(tool_set & msg_tools)
    has_media = bool(tool_set & media_tools)
    has_sessions = bool(tool_set & session_tools)
    has_cron = bool(tool_set & cron_tools)

    if has_msg and not has_code:
        return "communication"
    if has_media and not has_code:
        return "media_processing"
    if has_cron or has_sessions:
        return "automation"
    if any(kw in combined_text for kw in monitor_keywords):
        return "monitoring"
    if has_web and not has_code:
        return "research"
    if has_code:
        return "development"
    if has_browser:
        return "research"
    return "development"


def _infer_title(user_texts: list[str], max_len: int = 30) -> str:
    """Generate heuristic title from first substantive user message."""
    for text in user_texts:
        text = " ".join(text.split())
        if len(text) > max_len:
            # Try to cut at word boundary (English-friendly), else hard cut (Chinese)
            cut = text[:max_len].rfind(" ")
            if cut > max_len // 2:
                return text[:cut] + "..."
            return text[:max_len] + "..."
        if text:
            return text
    return "untitled"


def _get_session_created_time(session_info: dict) -> float:
    """Get session creation time for sorting. Uses file mtime as fallback."""
    file_path = session_info.get("file_path", "")
    try:
        return os.path.getmtime(file_path)
    except OSError:
        return 0.0


def _find_latest_session_ids(all_sessions: list[dict]) -> set[str]:
    """Find the latest session ID per agent to skip.

    Each agent may have an active session, so we skip the most recent
    session from each agent rather than only one globally.
    """
    if not all_sessions:
        return set()

    # Group by agent_id
    by_agent: dict[str, list[dict]] = {}
    for s in all_sessions:
        agent = s.get("agent_id", "unknown")
        if agent not in by_agent:
            by_agent[agent] = []
        by_agent[agent].append(s)

    latest_ids = set()
    for agent, sessions in by_agent.items():
        # Only consider non-reset sessions as potentially active
        active_sessions = [s for s in sessions if ".reset." not in s.get("file_path", "")]
        if not active_sessions:
            continue
        latest = max(active_sessions, key=_get_session_created_time)
        sid = latest.get("session_id")
        if sid:
            latest_ids.add(sid)

    return latest_ids


def _filter_by_since(sessions: list[dict], since: float) -> list[dict]:
    """Filter sessions to only include those modified after the given timestamp."""
    return [s for s in sessions if _get_session_created_time(s) >= since]


def _extract_first_user_message(file_path: str, max_lines: int = 100) -> str:
    """Extract the first user message text from a .jsonl file (lightweight).

    Scans up to max_lines to find the first substantive user message,
    strips metadata prefixes, and truncates to 80 chars for display.
    """
    try:
        with open(file_path, "r", encoding=detect_file_encoding(file_path), errors="replace") as f:
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    node = json.loads(line)
                    if node.get("type") != "message":
                        continue
                    msg = node.get("message", {})
                    if msg.get("role") != "user":
                        continue
                    for block in msg.get("content", []):
                        if isinstance(block, dict) and block.get("type") == "text":
                            text = block.get("text", "")
                            if is_system_startup_message(text):
                                break
                            text = strip_metadata_prefix(text)
                            if text:
                                # Truncate and collapse whitespace
                                text = " ".join(text.split())
                                if len(text) > 80:
                                    text = text[:80] + "..."
                                return text
                            break
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue
    except OSError:
        pass
    return ""


def _count_turns_and_detect_compaction(file_path: str) -> tuple[int, bool]:
    """Count assistant turns and detect compaction nodes in one pass.

    Returns (turns, has_compaction).

    `turns` is the raw total count of assistant messages in the file (matches
    the previous display behavior, reflecting total real interaction including
    pre-compaction messages). `has_compaction` is True if the file contains a
    compaction node with a non-empty summary.
    """
    count = 0
    has_compaction = False
    try:
        with open(file_path, "r", encoding=detect_file_encoding(file_path), errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    node = json.loads(line)
                    ntype = node.get("type")
                    if ntype == "compaction":
                        if node.get("summary"):
                            has_compaction = True
                        continue
                    if ntype != "message":
                        continue
                    if node.get("message", {}).get("role") == "assistant":
                        count += 1
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue
    except OSError:
        pass
    return count, has_compaction


def _extract_topic_preview(file_path: str, max_msgs: int = 3, max_lines: int = 300) -> str:
    """Extract a multi-message topic preview from a .jsonl session file.

    Collects up to max_msgs substantive user messages, each truncated to 15 chars,
    joined with " → " to form a conversation flow preview like:
      "配置 Nginx 反代.. → 加 SSL 证书 → 测试 HTTPS"

    Returns "(无对话消息)" if no substantive user messages found.
    """
    snippets: list[str] = []
    try:
        with open(file_path, "r", encoding=detect_file_encoding(file_path), errors="replace") as f:
            for i, line in enumerate(f):
                if i >= max_lines or len(snippets) >= max_msgs:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    node = json.loads(line)
                    if node.get("type") != "message":
                        continue
                    msg = node.get("message", {})
                    if msg.get("role") != "user":
                        continue
                    for block in msg.get("content", []):
                        if isinstance(block, dict) and block.get("type") == "text":
                            text = block.get("text", "")
                            if is_system_startup_message(text):
                                break
                            text = strip_metadata_prefix(text)
                            if not text:
                                break
                            text = " ".join(text.split())
                            # Skip very short messages (likely confirmations, codes, etc.)
                            if len(text) <= 4:
                                break
                            if len(text) > 15:
                                text = text[:15] + ".."
                            snippets.append(text)
                            break
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue
    except OSError:
        pass

    if not snippets:
        return "(无对话消息)"
    return " → ".join(snippets)


def _extract_session_times(file_path: str) -> tuple[str, str]:
    """Extract start and end timestamps from a .jsonl session file.

    Start: timestamp of the first node (usually type=session).
    End: timestamp of the last node (seek to file tail for efficiency).

    Returns (started_at, ended_at) as raw ISO-8601 strings.
    """
    started_at = ""
    ended_at = ""

    try:
        # Start time: first node with timestamp
        with open(file_path, "r", encoding=detect_file_encoding(file_path), errors="replace") as f:
            for i, line in enumerate(f):
                if i >= 10:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    node = json.loads(line)
                    ts = node.get("timestamp")
                    if ts:
                        started_at = ts
                        break
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue

        # End time: last node with timestamp (read tail of file)
        with open(file_path, "rb") as f:
            f.seek(0, 2)
            file_size = f.tell()
            seek_pos = max(0, file_size - 8192)
            f.seek(seek_pos)
            tail = f.read().decode("utf-8", errors="replace")

            for line in reversed(tail.strip().split("\n")):
                line = line.strip()
                if not line:
                    continue
                try:
                    node = json.loads(line)
                    ts = node.get("timestamp")
                    if ts:
                        ended_at = ts
                        break
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue
    except OSError:
        pass

    return started_at, ended_at


def _format_timestamp(iso_ts: str) -> str:
    """Format ISO-8601 timestamp to 'YYYY-MM-DD HH:MM:SS'."""
    if not iso_ts:
        return ""
    try:
        dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, AttributeError):
        return iso_ts[:19] if len(iso_ts) >= 19 else iso_ts


def list_qualifying_sessions(
    sessions_dirs: list[str],
    output_dir: str,
    limit: int | None = None,
    since: float | None = None,
) -> list[dict]:
    """List all sessions (except submitted) with status markers.

    Shows rejected, model-mismatched, and active sessions with status
    flags so users can see why sessions are not auto-processed.

    Returns summary dicts sorted by session start time (newest first).
    """
    # Get ALL sessions including non-whitelisted models
    all_sessions = []
    for sessions_dir in sessions_dirs:
        sessions = get_qualifying_sessions(sessions_dir, include_all_models=True)
        all_sessions.extend(sessions)

    if not all_sessions:
        return []

    # Identify latest sessions (may still be active)
    latest_sids = _find_latest_session_ids(all_sessions)

    # Load manifest for submitted and rejected info
    manifest = _load_manifest(output_dir)
    submitted_ids = {k.replace(".trajectory.json", "") for k in manifest.get("submitted", {})}
    rejected_map = manifest.get("rejected", {})

    # Only skip submitted sessions
    all_sessions = [s for s in all_sessions if s["session_id"] not in submitted_ids]

    # Filter by date
    if since:
        all_sessions = _filter_by_since(all_sessions, since)

    # Sort by mtime for limit pre-filter
    all_sessions.sort(key=_get_session_created_time, reverse=True)

    # Apply limit
    if limit and limit > 0:
        all_sessions = all_sessions[:limit]

    result = []
    for s in all_sessions:
        file_path = s["file_path"]
        try:
            fsize = os.path.getsize(file_path)
        except OSError:
            continue

        started_at, ended_at = _extract_session_times(file_path)
        topic = _extract_topic_preview(file_path)
        turns, has_compaction = _count_turns_and_detect_compaction(file_path)

        # Determine status (single value, by priority: model > cron > rejected > active)
        sid = s["session_id"]
        if not s.get("model_allowed", True):
            status = "model_mismatch"
        elif topic.startswith("[cron:"):
            status = "cron_task"
        elif sid in rejected_map:
            status = "rejected"
        elif sid in latest_sids:
            status = "active"
        else:
            status = None

        result.append({
            "session_id": sid,
            "agent_id": s.get("agent_id", ""),
            "model": s["model"],
            "started_at": _format_timestamp(started_at),
            "ended_at": _format_timestamp(ended_at),
            "file_size_kb": round(fsize / 1024),
            "turns": turns,
            "has_compaction": has_compaction,
            "topic": topic,
            "status": status,
            "_sort_key": started_at,
        })

    # Sort by started_at descending (newest first)
    result.sort(key=lambda x: x.get("_sort_key", ""), reverse=True)

    # Add index and remove internal sort key
    for item in result:
        item.pop("_sort_key", None)
    result = [{"index": i + 1, **item} for i, item in enumerate(result)]

    return result


def scan_and_convert(
    sessions_dirs: list[str],
    output_dir: str,
    session_ids: list[str] | None = None,
    limit: int | None = None,
    since: float | None = None,
) -> tuple[list[dict], dict]:
    """Scan sessions, filter, convert, and output trajectory files.

    Args:
        session_ids: If provided, only process these specific sessions
            (skip latest/submitted filters — user explicitly chose them).
        limit: If provided, only process the N most recent sessions.
        since: If provided, only process sessions modified after this timestamp.

    Returns (candidates, filter_report):
        - candidates: list of candidate dicts for agent semantic review
        - filter_report: dict with total_found, total_scanned, pre_filter, passed,
          filtered_count, and filtered (list of per-session filter records)
    """
    # Pre-filter counters
    skipped_active = 0
    skipped_processed = 0
    skipped_date = 0
    skipped_limit = 0

    # Collect all qualifying sessions across all agents
    all_qualifying = []
    for sessions_dir in sessions_dirs:
        qualifying = get_qualifying_sessions(sessions_dir)
        all_qualifying.extend(qualifying)

    total_found = len(all_qualifying)
    empty_report = {
        "total_found": total_found, "total_scanned": 0,
        "pre_filter": {"skipped_active": 0, "skipped_processed": 0, "skipped_date": 0, "skipped_limit": 0},
        "passed": 0, "filtered_count": 0, "filtered": [],
    }

    if not all_qualifying:
        print("No qualifying sessions found (model filter).", file=sys.stderr)
        return [], empty_report

    if session_ids:
        # Explicit selection: only filter by requested IDs, skip auto-filters
        requested = set(session_ids)
        all_qualifying = [s for s in all_qualifying if s["session_id"] in requested]
        found = {s["session_id"] for s in all_qualifying}
        missing = requested - found
        if missing:
            print(f"Warning: session(s) not found or not qualifying: {', '.join(missing)}", file=sys.stderr)
        if not all_qualifying:
            print("No matching sessions to process.", file=sys.stderr)
            return [], empty_report
    else:
        # Auto mode: apply all filters
        # Skip the latest session per agent (might still be active)
        latest_sids = _find_latest_session_ids(all_qualifying)
        if latest_sids:
            before = len(all_qualifying)
            all_qualifying = [s for s in all_qualifying if s["session_id"] not in latest_sids]
            skipped_active = before - len(all_qualifying)
            if skipped_active:
                print(f"Skipped {skipped_active} latest session(s) (may still be active): {', '.join(latest_sids)}", file=sys.stderr)

        # Skip already-submitted and rejected sessions
        skip_ids = _get_skip_session_ids(output_dir)
        if skip_ids:
            before = len(all_qualifying)
            all_qualifying = [s for s in all_qualifying if s["session_id"] not in skip_ids]
            skipped_processed = before - len(all_qualifying)
            if skipped_processed:
                print(f"Skipped {skipped_processed} already-processed session(s) (submitted or rejected).", file=sys.stderr)

        if not all_qualifying:
            print("No new sessions to process.", file=sys.stderr)
            empty_report["total_found"] = total_found
            empty_report["pre_filter"] = {
                "skipped_active": skipped_active, "skipped_processed": skipped_processed,
                "skipped_date": 0, "skipped_limit": 0,
            }
            return [], empty_report

    # Filter by date (applies to both explicit and auto modes)
    if since and not session_ids:
        before = len(all_qualifying)
        all_qualifying = _filter_by_since(all_qualifying, since)
        skipped_date = before - len(all_qualifying)
        if skipped_date:
            print(f"Filtered out {skipped_date} session(s) older than cutoff date.", file=sys.stderr)

    # Apply limit: sort by time (newest first), take top N
    if limit and limit > 0 and not session_ids:
        all_qualifying.sort(key=_get_session_created_time, reverse=True)
        if len(all_qualifying) > limit:
            skipped_limit = len(all_qualifying) - limit
            print(f"Limiting to {limit} most recent session(s) out of {len(all_qualifying)}.", file=sys.stderr)
            all_qualifying = all_qualifying[:limit]

    # Build cache-trace system prompt index.
    # Only index sessions we are about to process — cache-trace.jsonl accumulates
    # system prompts for every OpenClaw session ever, and on long-running hosts
    # can reach GB scale. Building an index of everything would OOM on 2GB VMs.
    cache_trace_path = get_cache_trace_path()
    target_ids = {s["session_id"] for s in all_qualifying}
    system_prompt_index = build_session_system_prompt_index(
        cache_trace_path, target_session_ids=target_ids
    )
    if system_prompt_index:
        print(f"Loaded system prompts for {len(system_prompt_index)} session(s) from cache-trace.", file=sys.stderr)

    total_scanned = len(all_qualifying)

    # Process each session
    candidates = []
    filter_records: list[dict] = []
    prefix_groups: dict[str, list[dict]] = {}

    for session_info in all_qualifying:
        file_path = session_info["file_path"]
        session_id = session_info["session_id"]

        try:
            nodes = parse_jsonl(file_path)

            # If the file contains compaction nodes, switch to richest-segment
            # extraction: slice the session by compaction boundaries and pick the
            # single segment with the most user content as the trajectory chain.
            # This avoids the pathological case where a 10+ compaction session
            # collapses to a one-line tail ("继续" / "完成的很好") and fails both
            # the quality gate and downstream training value.
            file_has_compaction = any(
                n.get("type") == "compaction" and n.get("summary") for n in nodes
            )
            if file_has_compaction:
                selected_chain, prior_compaction = extract_richest_segment(nodes)
                messages = ([prior_compaction] if prior_compaction else []) + selected_chain
            else:
                messages = extract_conversation_chain(nodes)

            if not messages:
                filter_records.append({
                    "session_id": session_id,
                    "topic": _extract_first_user_message(file_path),
                    "reason": "empty_conversation",
                    "detail": "no messages after parsing",
                })
                continue

            # Turn count filter (operates on the selected trajectory chain).
            # `segment_turns` is used as the MIN_TURNS gate to protect against
            # empty-shell sessions. `full_file_turns` is used for stats and
            # prefix dedup so multi-compaction sessions aren't under-weighted.
            segment_turns_val = count_turns(messages)
            turns = segment_turns_val  # kept for legacy local refs in this block
            full_file_turns = sum(
                1 for n in nodes
                if n.get("type") == "message"
                and n.get("message", {}).get("role") == "assistant"
            )
            # Sessions with a compaction node are long-by-definition: OpenClaw
            # only compacts when context fills up. Even after picking the richest
            # segment, we keep the MIN_TURNS bypass as a safety net for sessions
            # whose richest segment happens to be short.
            has_compaction = any(
                m.get("type") == "compaction" and m.get("summary")
                for m in messages
            )
            effective_min = 0 if has_compaction else MIN_TURNS
            if turns <= effective_min:
                detail = f"{turns} turns (min {effective_min + 1})"
                if has_compaction:
                    detail += " [compacted]"
                filter_records.append({
                    "session_id": session_id,
                    "topic": _topic_from_messages(messages),
                    "reason": "turns_too_low",
                    "detail": detail,
                })
                continue

            # Extract user texts for review
            user_texts, tool_names = _extract_user_texts_and_tools(messages)

            # Numeric quality check
            quality_ok, quality_reason = check_quality(messages)
            if not quality_ok:
                filter_records.append({
                    "session_id": session_id,
                    "topic": _topic_from_messages(messages),
                    "reason": "quality_check",
                    "detail": quality_reason,
                })
                print(f"  Quality skip ({quality_reason}): {session_id}", file=sys.stderr)
                continue

            # Get system prompt: prefer cache-trace, fallback depends on mode
            real_system_prompt = system_prompt_index.get(session_id)
            session_meta = extract_session_metadata(nodes)
            if real_system_prompt:
                system_prompt_source = "cache_trace"
            elif session_ids:
                # Explicit mode: user chose this session, allow reconstruction fallback
                real_system_prompt = build_system_prompt(
                    tool_names=session_meta.get("tool_names", []),
                    cwd=session_meta.get("cwd", ""),
                    model=session_meta.get("model", ""),
                    thinking_level=session_meta.get("thinking_level", "off"),
                    timestamp=session_meta.get("timestamp", ""),
                )
                system_prompt_source = "reconstructed"
                print(f"  Reconstructed system prompt (no cache-trace): {session_id}", file=sys.stderr)
            else:
                # Auto mode: skip sessions without cache-trace (pre-cache-trace historical sessions)
                filter_records.append({
                    "session_id": session_id,
                    "topic": _topic_from_messages(messages),
                    "reason": "no_cache_trace",
                    "detail": "no system prompt available",
                })
                print(f"  Skipped (no cache-trace): {session_id}", file=sys.stderr)
                continue

            # Convert to trajectory
            trajectory = convert_to_trajectory(
                messages,
                session_meta=session_meta,
                real_system_prompt=real_system_prompt,
            )

            if trajectory.get("_discarded"):
                filter_records.append({
                    "session_id": session_id,
                    "topic": _topic_from_messages(messages),
                    "reason": "conversion_error",
                    "detail": trajectory["_discarded"],
                })
                print(f"  Skipped ({trajectory['_discarded']}): {session_id}", file=sys.stderr)
                continue

            if not trajectory["messages"]:
                filter_records.append({
                    "session_id": session_id,
                    "topic": _topic_from_messages(messages),
                    "reason": "conversion_error",
                    "detail": "empty after conversion",
                })
                print(f"  Skipped (empty after conversion): {session_id}", file=sys.stderr)
                continue

            model = get_model_from_nodes(nodes) or session_info.get("model", "unknown")

            # Extract session stats (separate from trajectory)
            stats = _extract_session_stats(nodes, messages)
            stats["system_prompt_source"] = system_prompt_source
            stats["cwd"] = session_meta.get("cwd", "")
            stats["agent_id"] = session_info.get("agent_id", "")
            stats["model"] = model
            stats["provider"] = session_meta.get("provider", "unknown")
            stats["thinking"] = session_meta.get("thinking_level", "off")
            # `turns` reflects the total assistant messages across the whole
            # file (all compaction eras included), so admin stats / prefix
            # dedup / user rankings see the real interaction volume. The
            # trajectory chain's own turn count is kept as `segment_turns` in
            # _extract_session_stats for diagnosis.
            stats["turns"] = full_file_turns
            stats["has_compaction"] = file_has_compaction
            # Heuristic domain/title — agent review (step 3) can upgrade these
            stats["domain"] = _infer_domain(tool_names, user_texts)
            stats["title"] = _infer_title(user_texts)
            stats["review_status"] = "heuristic"

            # Convert to OpenAI format (final output format)
            openai_traj = convert_to_openai_format(trajectory, stats)

            # Calculate reasoning stats from OpenAI format
            _pure_text = 0
            _rc_with_tc = 0
            _rc_pure = 0
            for _m in openai_traj.get("messages", []):
                if _m.get("role") != "assistant":
                    continue
                _has_tc = len(_m.get("tool_calls", [])) > 0
                _has_rc = isinstance(_m.get("reasoning_content", ""), str) and _m.get("reasoning_content", "").strip() != ""
                if _has_tc:
                    if _has_rc:
                        _rc_with_tc += 1
                else:
                    _pure_text += 1
                    if _has_rc:
                        _rc_pure += 1
            stats["effective_asst"] = _pure_text + _rc_with_tc
            stats["reasoning_asst"] = _rc_pure + _rc_with_tc

            # Write trajectory file (OpenAI format)
            output_filename = f"{session_id}.trajectory.json"
            output_path = os.path.join(output_dir, output_filename)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(openai_traj, f, ensure_ascii=False, indent=2)

            # Write stats file alongside trajectory
            stats_filename = f"{session_id}.stats.json"
            stats_path = os.path.join(output_dir, stats_filename)
            with open(stats_path, "w", encoding="utf-8") as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)

            # Extract user messages for semantic review (stripped + truncated)
            review_messages = []
            for msg in trajectory["messages"]:
                if msg.get("role") != "user":
                    continue
                content = msg.get("content")
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    # Handle merged messages (list of content blocks)
                    text_parts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text_parts.append(block.get("text", ""))
                    text = "\n".join(text_parts)
                else:
                    continue
                text = strip_metadata_prefix(text)
                if not text:
                    continue
                if len(text) > REVIEW_MAX_CHARS:
                    text = text[:REVIEW_MAX_CHARS] + "..."
                review_messages.append(text)
                if len(review_messages) >= REVIEW_MAX_MESSAGES:
                    break

            # Prefix hash for dedup
            prefix_hash = _compute_prefix_hash(messages)

            candidate = {
                "session_id": session_id,
                "turns": full_file_turns,
                "domain": stats["domain"],
                "model": model,
                "output_path": output_path,
                "message_count": len(trajectory["messages"]),
                "tool_count": len(trajectory["tools"]),
                "system_prompt_source": system_prompt_source,
                "user_messages": review_messages,
                "_prefix_hash": prefix_hash,
            }

            # Group by prefix hash for dedup
            if prefix_hash not in prefix_groups:
                prefix_groups[prefix_hash] = []
            prefix_groups[prefix_hash].append(candidate)

        except Exception as e:
            print(f"  Error processing {file_path}: {e}", file=sys.stderr)
            continue

    # Prefix dedup: keep longest per group
    dedup_rejections: list[tuple[str, str]] = []
    for prefix_hash, group in prefix_groups.items():
        best = max(group, key=lambda x: x["turns"])
        candidates.append(best)

        if len(group) > 1:
            dropped = len(group) - 1
            print(f"  Prefix dedup: kept {best['session_id']} ({best['turns']} turns), dropped {dropped}", file=sys.stderr)

            # Clean up trajectory and stats files of dropped candidates
            for c in group:
                if c["session_id"] != best["session_id"]:
                    filter_records.append({
                        "session_id": c["session_id"],
                        "topic": "",
                        "reason": "prefix_dedup",
                        "detail": f"duplicate of {best['session_id']}",
                    })
                    dedup_rejections.append((c["session_id"], f"prefix_dedup:{best['session_id']}"))
                    for path in (
                        c["output_path"],
                        c["output_path"].replace(".trajectory.json", ".stats.json"),
                    ):
                        try:
                            os.remove(path)
                        except OSError:
                            pass

    # Record dedup rejections in manifest to prevent re-processing
    if dedup_rejections:
        manifest = _load_manifest(output_dir)
        manifest.setdefault("rejected", {})
        now = datetime.now(timezone.utc).isoformat()
        for sid, reason in dedup_rejections:
            manifest["rejected"][sid] = {"rejected_at": now, "reason": reason}
        _save_manifest(output_dir, manifest)

    # Remove internal fields from output
    for c in candidates:
        c.pop("_prefix_hash", None)

    filter_report = {
        "total_found": total_found,
        "total_scanned": total_scanned,
        "pre_filter": {
            "skipped_active": skipped_active,
            "skipped_processed": skipped_processed,
            "skipped_date": skipped_date,
            "skipped_limit": skipped_limit,
        },
        "passed": len(candidates),
        "filtered_count": len(filter_records),
        "filtered": filter_records,
    }

    return candidates, filter_report


def main():
    parser = argparse.ArgumentParser(description="Scan and convert OpenClaw sessions to trajectories")
    parser.add_argument("--sessions-dir", help="Override sessions directory path")
    parser.add_argument("--output-dir", "-o", default=DEFAULT_OUTPUT_DIR, help="Output directory")
    parser.add_argument("--list-only", action="store_true", help="List qualifying sessions without processing")
    parser.add_argument("--page", type=int, default=1, help="Page number for --list-only (default: 1)")
    parser.add_argument("--page-size", type=int, default=10, help="Items per page for --list-only (default: 10)")
    parser.add_argument("--sessions", nargs="+", metavar="ID", help="Only process these specific session IDs")
    parser.add_argument("--limit", type=int, metavar="N", help="Only process the N most recent sessions")
    parser.add_argument("--since", metavar="DATE", help="Only process sessions modified after DATE (YYYY-MM-DD)")
    args = parser.parse_args()

    # Parse --since into a timestamp
    since_ts = None
    if args.since:
        try:
            since_ts = datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            print(f"Error: --since must be in YYYY-MM-DD format, got '{args.since}'", file=sys.stderr)
            sys.exit(1)

    # Create output dir
    os.makedirs(args.output_dir, exist_ok=True)

    if args.sessions_dir:
        sessions_dirs = [args.sessions_dir]
    else:
        sessions_dirs = find_openclaw_sessions_dirs()

    if not sessions_dirs:
        print("No OpenClaw sessions directories found.", file=sys.stderr)
        sys.exit(1)

    # List-only mode: paginated output, exit
    if args.list_only:
        all_sessions = list_qualifying_sessions(sessions_dirs, args.output_dir, since=since_ts)
        total = len(all_sessions)

        page_size = args.page_size
        page = args.page
        start = (page - 1) * page_size
        page_items = all_sessions[start:start + page_size]

        output = {
            "items": page_items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": start + page_size < total,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print(f"Scanning {len(sessions_dirs)} agent(s)...", file=sys.stderr)
    candidates, filter_report = scan_and_convert(sessions_dirs, args.output_dir, session_ids=args.sessions, limit=args.limit, since=since_ts)
    print(f"\nGenerated {len(candidates)} candidate trajectory(ies).", file=sys.stderr)

    if filter_report["filtered_count"]:
        print(f"Filtered out {filter_report['filtered_count']} session(s) during processing:", file=sys.stderr)
        # Group by reason and show details
        from collections import defaultdict
        reason_groups: dict[str, list[dict]] = defaultdict(list)
        for rec in filter_report["filtered"]:
            reason_groups[rec["reason"]].append(rec)
        for reason, recs in reason_groups.items():
            print(f"  - {reason}: {len(recs)}", file=sys.stderr)
            for rec in recs:
                sid = rec["session_id"]
                short_sid = f"{sid[:8]}..{sid[-4:]}" if len(sid) > 12 else sid
                print(f"    · {rec.get('detail', '')}: {short_sid}", file=sys.stderr)

    # Write full candidates (with user_messages) to file for agent review
    output_path = os.path.join(args.output_dir, "candidates.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)
    print(f"\nCandidates written to {output_path}", file=sys.stderr)

    # Print structured output to stdout (summary + filter_report)
    summary = []
    for c in candidates:
        summary.append({
            "session_id": c["session_id"],
            "turns": c["turns"],
            "domain": c["domain"],
            "model": c["model"],
            "message_count": c["message_count"],
            "tool_count": c["tool_count"],
            "system_prompt_source": c["system_prompt_source"],
        })
    print(json.dumps({
        "candidates": summary,
        "filter_report": filter_report,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
