from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

API_ROOT = "https://ws.audioscrobbler.com/2.0/"
DEFAULT_CREDS_PATH = Path.home() / ".openclaw" / "lastfm-credentials.json"


class LastFMError(RuntimeError):
    pass


def load_credentials(explicit_path: Optional[str] = None) -> Dict[str, str]:
    creds: Dict[str, str] = {}

    env_key = os.getenv("LASTFM_API_KEY")
    env_secret = os.getenv("LASTFM_SHARED_SECRET")
    env_user = os.getenv("LASTFM_USERNAME")
    if env_key:
        creds["api_key"] = env_key
    if env_secret:
        creds["shared_secret"] = env_secret
    if env_user:
        creds["username"] = env_user

    path = Path(explicit_path) if explicit_path else DEFAULT_CREDS_PATH
    if path.exists():
        file_creds = json.loads(path.read_text(encoding="utf-8"))
        for key in ("api_key", "shared_secret", "username"):
            if file_creds.get(key) and key not in creds:
                creds[key] = str(file_creds[key])

    if not creds.get("api_key"):
        raise LastFMError(
            "Missing Last.fm API key. Set LASTFM_API_KEY or create ~/.openclaw/lastfm-credentials.json"
        )
    return creds


def lastfm_get(method: str, params: Optional[Dict[str, Any]] = None, api_key: Optional[str] = None) -> Dict[str, Any]:
    query: Dict[str, Any] = {
        "method": method,
        "api_key": api_key or load_credentials().get("api_key"),
        "format": "json",
    }
    if params:
        for key, value in params.items():
            if value is not None:
                query[key] = value

    url = API_ROOT + "?" + urllib.parse.urlencode(query)
    with urllib.request.urlopen(url) as response:
        payload = response.read().decode("utf-8")
    data = json.loads(payload)

    if "error" in data:
        raise LastFMError(f"Last.fm error {data['error']}: {data.get('message', 'Unknown error')}")
    return data


def ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def dump_json(data: Any) -> None:
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
