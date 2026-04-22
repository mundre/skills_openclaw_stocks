"""Main pipeline entrypoint.

Usage:
    uv run --with httpx python scripts/run.py [--track ai|crypto|devtools] [--dry-run] [--verbose]

Exit codes:
    0  Success
    1  All sources failed (no data)
    2  Config/state error
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add scripts dir to path so local imports work
SCRIPTS_DIR = Path(__file__).parent
SKILL_DIR = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from state import load_state, save_state, get_current_track, advance_track, override_track, TRACKS
from sources import fetch_all, load_track_config
from synthesise import build_report

CONFIG_PATH = SKILL_DIR / "config.json"
MEMORY_DIR = Path.home() / ".openclaw" / "workspace" / "memory"
LATEST_PATH = MEMORY_DIR / "autoresearch-latest.md"
ARCHIVE_PATH = MEMORY_DIR / "autoresearch-archive.md"


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Autoresearch nightly pipeline — fetches from arXiv, GitHub, HN, and web.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--track",
        choices=TRACKS,
        default=None,
        help="Override track rotation (ai|crypto|devtools). Default: rotate from state.json.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Fetch + synthesise but don't write files or advance state.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Print debug info to stderr.",
    )
    return parser.parse_args()


def log(level: str, msg: str) -> None:
    """Log to stderr."""
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[autoresearch] {level:<5} {ts} {msg}", file=sys.stderr)


async def main() -> int:
    """Pipeline orchestrator."""
    args = parse_args()

    if args.verbose:
        log("INFO", "Verbose mode enabled")

    # ── 1. Validate config ────────────────────────────────────────────────────
    if not CONFIG_PATH.exists():
        print(f"ERROR: config.json not found at {CONFIG_PATH}", file=sys.stderr)
        return 2

    try:
        import json
        with open(CONFIG_PATH) as f:
            _config_check = json.load(f)
    except Exception as exc:
        print(f"ERROR: config.json invalid JSON: {exc}", file=sys.stderr)
        return 2

    # ── 2. Load state ─────────────────────────────────────────────────────────
    state = load_state()
    log("INFO", f"State loaded: track_index={state.current_track_index}, last_run={state.last_run}")

    # ── 3. Determine track ────────────────────────────────────────────────────
    if args.track:
        try:
            track_name = override_track(args.track)
            log("INFO", f"Track override: {track_name}")
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
    else:
        track_name = get_current_track(state)
        log("INFO", f"Track from rotation: {track_name}")

    # ── 4. Load track config ──────────────────────────────────────────────────
    try:
        track_config = load_track_config(track_name, CONFIG_PATH)
        log("INFO", f"Track config loaded: {track_config.display_name}")
    except Exception as exc:
        print(f"ERROR: failed to load track config: {exc}", file=sys.stderr)
        return 2

    # ── 5. Fetch all sources ──────────────────────────────────────────────────
    run_timestamp = datetime.now(timezone.utc).isoformat()
    log("INFO", f"Starting fetch for track '{track_name}' at {run_timestamp}")

    sources = await fetch_all(track_config, CONFIG_PATH)

    total_items = sum(len(v) for v in sources.values())
    log("INFO", f"Fetch complete: {total_items} total items "
        f"(arXiv={len(sources['arxiv'])}, GitHub={len(sources['github'])}, "
        f"HN={len(sources['hackernews'])}, web={len(sources['web'])})")

    # ── 6. Check all-empty ────────────────────────────────────────────────────
    if total_items == 0:
        log("ERROR", "All sources returned empty — pipeline failed")
        teaser = f"⚠️ **Nightly Research: {track_config.display_name}** — all sources failed. Check logs."
        print(teaser)
        return 1

    # ── 7. Build report + teaser ──────────────────────────────────────────────
    # Determine next track display name
    next_index = (TRACKS.index(track_name) + 1) % len(TRACKS)
    next_track_name = TRACKS[next_index]
    try:
        next_track_cfg = load_track_config(next_track_name, CONFIG_PATH)
        next_track_display = next_track_cfg.display_name
    except Exception:
        next_track_display = next_track_name

    log("INFO", "Building report…")
    try:
        full_report, teaser = build_report(
            track_display_name=track_config.display_name,
            track_name=track_name,
            sources=sources,
            run_timestamp=run_timestamp,
            next_track_display=next_track_display,
        )
    except Exception as exc:
        log("ERROR", f"Report build failed: {exc}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1

    log("INFO", f"Report built ({len(full_report)} chars)")

    # ── 8. Write outputs (unless --dry-run) ───────────────────────────────────
    if args.dry_run:
        log("INFO", "DRY RUN — skipping file writes and state advance")
        log("INFO", f"Would write to: {LATEST_PATH}")
        log("INFO", f"Would append to: {ARCHIVE_PATH}")
        # Print a preview of the report to stderr in verbose mode
        if args.verbose:
            print("\n--- DRY RUN REPORT PREVIEW ---", file=sys.stderr)
            print(full_report[:1000], file=sys.stderr)
            print("--- END PREVIEW ---\n", file=sys.stderr)
    else:
        # Ensure memory dir exists
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)

        # 8a. Write latest (overwrite)
        try:
            tmp_latest = LATEST_PATH.with_suffix(".md.tmp")
            tmp_latest.write_text(full_report, encoding="utf-8")
            os.rename(tmp_latest, LATEST_PATH)
            log("INFO", f"Wrote latest report to {LATEST_PATH}")
        except Exception as exc:
            log("ERROR", f"Failed to write latest report: {exc}")
            return 1

        # 8b. Append to archive
        try:
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            archive_separator = (
                f"\n\n---\n\n"
                f"<!-- autoresearch:{track_name}:{date_str} -->\n\n"
                f"{full_report}\n"
            )
            with open(ARCHIVE_PATH, "a", encoding="utf-8") as f:
                f.write(archive_separator)
            log("INFO", f"Appended to archive: {ARCHIVE_PATH}")
        except Exception as exc:
            log("ERROR", f"Failed to append to archive: {exc}")
            return 1

        # 8c. Advance state
        try:
            # Only advance if track was the natural rotation (not a --track override)
            if not args.track:
                new_state = advance_track(state)
            else:
                # On override: just update last_run timestamp, don't advance index
                import dataclasses
                new_state = dataclasses.replace(
                    state,
                    last_run=datetime.now(timezone.utc).isoformat(),
                )
            save_state(new_state)
            log("INFO", f"State advanced: next track index = {new_state.current_track_index}")
        except Exception as exc:
            log("ERROR", f"Failed to save state: {exc}")
            # Non-fatal: report was written, just state didn't advance

    # ── 9. Print teaser to stdout ─────────────────────────────────────────────
    print(teaser)

    # ── 10. Done ──────────────────────────────────────────────────────────────
    log("INFO", "Pipeline complete — exit 0")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
