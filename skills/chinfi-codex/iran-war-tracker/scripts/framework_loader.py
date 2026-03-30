#!/usr/bin/env python3
"""Load the analysis framework with remote-first fallback."""

from __future__ import annotations

from pathlib import Path

import requests

from config import FRAMEWORK_CANDIDATES, FRAMEWORK_GIST_URL, FRAMEWORK_MAX_CHARS, FRAMEWORK_REMOTE_TIMEOUT, skill_root
from normalize import normalize_text


def load_framework(session: requests.Session) -> dict[str, str]:
    remote = load_remote_framework(session)
    if remote["content"]:
        return remote
    return load_local_framework(remote.get("error", ""))


def load_remote_framework(session: requests.Session) -> dict[str, str]:
    try:
        response = session.get(FRAMEWORK_GIST_URL, timeout=FRAMEWORK_REMOTE_TIMEOUT)
        response.raise_for_status()
        text = response.text.strip()
        return {
            "name": Path(FRAMEWORK_GIST_URL).name or "remote-framework.md",
            "source": "gist",
            "content": text[:FRAMEWORK_MAX_CHARS],
            "error": "",
        }
    except Exception as exc:
        return {
            "name": "",
            "source": "gist",
            "content": "",
            "error": normalize_text(exc),
        }


def load_local_framework(remote_error: str = "") -> dict[str, str]:
    root = skill_root()
    for candidate in FRAMEWORK_CANDIDATES:
        path = root / candidate
        if path.exists():
            text = path.read_text(encoding="utf-8")
            return {
                "name": path.name,
                "source": "local",
                "content": text[:FRAMEWORK_MAX_CHARS],
                "error": remote_error,
            }
    return {
        "name": "",
        "source": "missing",
        "content": "",
        "error": remote_error or "framework not found",
    }
