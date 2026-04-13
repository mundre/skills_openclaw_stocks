#!/usr/bin/env python3
"""Prepare and launch the ClawArena local watcher."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


CLAW_DIR = Path.home() / ".clawarena"
TOKEN_PATH = CLAW_DIR / "token"
AGENT_ID_PATH = CLAW_DIR / "agent_id"
DELIVERY_CONFIG_PATH = CLAW_DIR / "openclaw_delivery.json"
WATCHER_PID_PATH = CLAW_DIR / "watcher.pid"
WATCHER_LOG_PATH = CLAW_DIR / "watcher.log"


def atomic_write(path: Path, content: str, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content)
    tmp_path.replace(path)
    if mode is not None:
        path.chmod(mode)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    return {}


def process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def require_runtime_credentials() -> dict[str, str]:
    missing: list[str] = []
    values: dict[str, str] = {}
    for key, path in {"token": TOKEN_PATH, "agent_id": AGENT_ID_PATH}.items():
        if not path.exists():
            missing.append(str(path))
            continue
        value = path.read_text().strip()
        if not value:
            missing.append(str(path))
            continue
        values[key] = value
    if missing:
        raise SystemExit(
            "ClawArena watcher setup requires a provisioned fighter first. "
            "Save ~/.clawarena/token and ~/.clawarena/agent_id before running setup. "
            f"Missing or empty: {', '.join(missing)}"
        )
    return values


def stop_existing_watcher() -> None:
    if not WATCHER_PID_PATH.exists():
        return
    try:
        pid = int(WATCHER_PID_PATH.read_text().strip())
    except ValueError:
        WATCHER_PID_PATH.unlink(missing_ok=True)
        return
    if process_alive(pid):
        os.kill(pid, signal.SIGTERM)
        for _ in range(20):
            if not process_alive(pid):
                break
            time.sleep(0.2)
    WATCHER_PID_PATH.unlink(missing_ok=True)


def write_delivery_config(args: argparse.Namespace) -> dict[str, Any]:
    existing = read_json(DELIVERY_CONFIG_PATH)
    channel = args.channel or existing.get("channel")
    target = args.to or existing.get("to")
    reply_account = args.reply_account or existing.get("reply_account")
    if not channel or not target:
        raise SystemExit(
            "channel and to are required on first setup; reruns can reuse the saved config."
        )
    config = {
        "channel": channel,
        "to": target,
    }
    if reply_account:
        config["reply_account"] = reply_account
    atomic_write(
        DELIVERY_CONFIG_PATH,
        json.dumps(config, indent=2, sort_keys=True) + "\n",
        0o600,
    )
    return config


def start_watcher(skill_root: Path) -> int:
    WATCHER_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    watcher_path = skill_root / "watcher.py"
    with WATCHER_LOG_PATH.open("ab") as log_file:
        proc = subprocess.Popen(  # noqa: S603
            [sys.executable, str(watcher_path)],
            stdout=log_file,
            stderr=log_file,
            cwd=str(skill_root),
            start_new_session=True,
        )
    WATCHER_PID_PATH.write_text(f"{proc.pid}\n")
    return proc.pid


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Set up the ClawArena local watcher")
    parser.add_argument("--channel", help="Active OpenClaw channel for delivery, e.g. telegram")
    parser.add_argument("--to", help="Active chat target, e.g. a Telegram numeric chat id")
    parser.add_argument(
        "--reply-account",
        help="Optional OpenClaw account id for outbound delivery",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_root = Path(__file__).resolve().parent
    credentials = require_runtime_credentials()
    config = write_delivery_config(args)
    stop_existing_watcher()
    pid = start_watcher(skill_root)
    print(
        json.dumps(
            {
                "watcher_started": True,
                "pid": pid,
                "agent_id": credentials["agent_id"],
                "channel": config["channel"],
                "to": config["to"],
                "reply_account": config.get("reply_account"),
                "watcher_script": str(skill_root / "watcher.py"),
                "log_file": str(WATCHER_LOG_PATH),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
