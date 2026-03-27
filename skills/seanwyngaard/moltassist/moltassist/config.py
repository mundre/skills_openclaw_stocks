"""MoltAssist configuration management."""

import json
import os
from pathlib import Path

URGENCY_LEVELS = ("low", "medium", "high", "critical")

CATEGORIES = (
    "email", "calendar", "health", "weather", "dev",
    "finance", "compliance", "travel", "staff", "social", "system", "custom",
)

DEFAULT_CATEGORY = {
    "enabled": False,
    "urgency_threshold": "medium",
    "llm_enrich": False,
    "cooldown_minutes": 20,
}

DEFAULT_CONFIG = {
    "version": "0.1.0",
    "categories": {
        "email":      {"enabled": True,  "urgency_threshold": "medium", "llm_enrich": True,  "cooldown_minutes": 20},
        "calendar":   {"enabled": True,  "urgency_threshold": "medium", "llm_enrich": True,  "cooldown_minutes": 20},

        "health":     {"enabled": False, "urgency_threshold": "medium", "llm_enrich": True,  "cooldown_minutes": 20},
        "weather":    {"enabled": True,  "urgency_threshold": "low",    "llm_enrich": False, "cooldown_minutes": 60},
        "dev":        {"enabled": False, "urgency_threshold": "medium", "llm_enrich": True,  "cooldown_minutes": 20},
        "finance":    {"enabled": False, "urgency_threshold": "medium", "llm_enrich": True,  "cooldown_minutes": 20},
        "compliance": {"enabled": False, "urgency_threshold": "high",   "llm_enrich": False, "cooldown_minutes": 60},
        "travel":     {"enabled": False, "urgency_threshold": "medium", "llm_enrich": True,  "cooldown_minutes": 20},
        "staff":      {"enabled": False, "urgency_threshold": "medium", "llm_enrich": False, "cooldown_minutes": 20},
        "social":     {"enabled": False, "urgency_threshold": "low",    "llm_enrich": False, "cooldown_minutes": 20},
        "system":     {"enabled": True,  "urgency_threshold": "high",   "llm_enrich": False, "cooldown_minutes": 10},
        "custom":     {"enabled": False, "urgency_threshold": "medium", "llm_enrich": False, "cooldown_minutes": 20},
    },
    "delivery": {
        "default_channel": "telegram",
        "urgency_routing": {
            "critical": "telegram",
            "high":     "telegram",
            "medium":   "telegram",
            "low":      "telegram",
        },
        "channels": {
            "telegram": {"active": True, "chat_id": ""},
            "whatsapp": {"active": False, "target": ""},
            "discord":  {"active": False, "target": ""},
        },
    },
    "schedule": {
        "quiet_hours": {"start": "23:00", "end": "08:00"},
        "timezone": "UTC",
        "morning_digest": True,
        "rate_limits": {
            "per_category_per_hour": 3,
            "global_per_hour": 10,
        },
        "polling": {

            "calendar": {"interval_minutes": 10,   "enabled": True},
            "email":    {"interval_minutes": 15,   "enabled": True},
            "weather":  {"interval_minutes": 60,   "enabled": False},
            "health":   {"interval_minutes": 60,   "enabled": False},
            "github":   {"interval_minutes": 30,   "enabled": False},
            "finance":  {"interval_minutes": 1440, "enabled": False},
        },
    },
    "urgency_threshold": "medium",
    "llm_mode": "none",
}


def _get_config_path() -> Path:
    workspace = os.environ.get("OPENCLAW_WORKSPACE") or os.path.expanduser("~/.openclaw/workspace")
    return Path(workspace) / "moltassist" / "config.json"


def load_config(path: str | Path | None = None) -> dict:
    """Load config from JSON file, merging with defaults for any missing keys."""
    config_path = Path(path) if path else _get_config_path()

    if not config_path.exists():
        return json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy

    with open(config_path, "r") as f:
        user_config = json.load(f)

    # Merge defaults -- user values take priority
    merged = json.loads(json.dumps(DEFAULT_CONFIG))
    _deep_merge(merged, user_config)
    return merged


def save_config(config: dict, path: str | Path | None = None) -> None:
    """Write config dict to JSON file."""
    config_path = Path(path) if path else _get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def validate_config(config: dict) -> None:
    """Raise ValueError if config structure is invalid."""
    if not isinstance(config, dict):
        raise ValueError("Config must be a dict")

    if "categories" not in config:
        raise ValueError("Config missing 'categories'")

    if not isinstance(config["categories"], dict):
        raise ValueError("'categories' must be a dict")

    for cat_name, cat_cfg in config["categories"].items():
        if not isinstance(cat_cfg, dict):
            raise ValueError(f"Category '{cat_name}' must be a dict")
        if "enabled" in cat_cfg and not isinstance(cat_cfg["enabled"], bool):
            raise ValueError(f"Category '{cat_name}': 'enabled' must be bool")
        if "urgency_threshold" in cat_cfg:
            if cat_cfg["urgency_threshold"] not in URGENCY_LEVELS:
                raise ValueError(
                    f"Category '{cat_name}': invalid urgency_threshold "
                    f"'{cat_cfg['urgency_threshold']}'"
                )

    if "delivery" in config:
        delivery = config["delivery"]
        if not isinstance(delivery, dict):
            raise ValueError("'delivery' must be a dict")
        if "urgency_routing" in delivery:
            for urg, channel in delivery["urgency_routing"].items():
                if urg not in URGENCY_LEVELS:
                    raise ValueError(f"Invalid urgency level in routing: '{urg}'")

    if "schedule" in config:
        schedule = config["schedule"]
        if not isinstance(schedule, dict):
            raise ValueError("'schedule' must be a dict")
        if "rate_limits" in schedule:
            rl = schedule["rate_limits"]
            if not isinstance(rl, dict):
                raise ValueError("'rate_limits' must be a dict")
            for key in ("per_category_per_hour", "global_per_hour"):
                if key in rl and (not isinstance(rl[key], int) or rl[key] < 1):
                    raise ValueError(f"'{key}' must be a positive integer")

    if "urgency_threshold" in config:
        if config["urgency_threshold"] not in URGENCY_LEVELS:
            raise ValueError(f"Invalid global urgency_threshold: '{config['urgency_threshold']}'")


def get_category_config(category: str, config: dict | None = None) -> dict:
    """Return settings for a specific category, with defaults applied."""
    if config is None:
        config = load_config()
    cats = config.get("categories", {})
    if category in cats:
        merged = dict(DEFAULT_CATEGORY)
        merged.update(cats[category])
        return merged
    return dict(DEFAULT_CATEGORY)


def _deep_merge(base: dict, override: dict) -> None:
    """Recursively merge override into base (mutates base)."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
