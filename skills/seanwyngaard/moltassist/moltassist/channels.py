"""MoltAssist delivery channels -- delegates to OpenClaw CLI for all delivery."""

import json
import subprocess
import time


def _run_openclaw(args: list[str], retries: int = 3) -> tuple[bool, str | None]:
    """Run an openclaw CLI command with exponential backoff retries.

    Returns (success, error_or_none).
    """
    last_error: str | None = None

    for attempt in range(1, retries + 1):
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return (True, None)
            last_error = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
        except FileNotFoundError:
            return (False, "openclaw CLI not found -- is OpenClaw installed?")
        except subprocess.TimeoutExpired:
            last_error = "openclaw command timed out"
        except Exception as e:
            last_error = str(e)

        if attempt < retries:
            time.sleep(2 ** attempt)  # exponential backoff: 2s, 4s

    return (False, f"Failed after {retries} attempts: {last_error}")


def get_channel_config() -> dict:
    """Detect which channels OpenClaw has configured.

    Returns a dict with channel availability info. For backward compatibility
    with core.py, includes 'bot_token' and 'chat_id' keys when Telegram is
    available (set to 'openclaw-managed' since OpenClaw owns the credentials).
    """
    try:
        result = subprocess.run(
            ["openclaw", "channels", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            try:
                channels_data = json.loads(result.stdout.strip())
                config: dict = {"channels": channels_data}
                # Backward compat: if telegram is in the list, populate
                # dummy credentials so core.py's _deliver() checks pass
                channel_names = []
                if isinstance(channels_data, list):
                    channel_names = [
                        c.get("name", c) if isinstance(c, dict) else str(c)
                        for c in channels_data
                    ]
                elif isinstance(channels_data, dict):
                    channel_names = list(channels_data.keys())

                if any("telegram" in n.lower() for n in channel_names):
                    config["bot_token"] = "openclaw-managed"
                    config["chat_id"] = "openclaw-managed"
                return config
            except (json.JSONDecodeError, TypeError):
                pass
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass

    # Fallback: assume OpenClaw is installed and telegram is available
    # (the actual send will fail with a clear error if it's not)
    return {"bot_token": "openclaw-managed", "chat_id": "openclaw-managed"}


def deliver_telegram(
    message: str,
    chat_id: str,
    bot_token: str = "",
    retries: int = 3,
    buttons: list | None = None,
) -> tuple[bool, str | None]:
    """Send a message via Telegram through OpenClaw CLI.

    The bot_token parameter is accepted for backward compatibility but ignored --
    OpenClaw manages its own credentials. The chat_id is passed as --target.

    Retries up to `retries` times with exponential backoff.
    Returns (success, error_or_none).
    """
    args = [
        "openclaw", "message", "send",
        "--channel", "telegram",
        "--target", str(chat_id),
        "-m", message,
    ]

    if buttons:
        args.extend(["--buttons", json.dumps(buttons)])

    return _run_openclaw(args, retries=retries)


def deliver_whatsapp(
    message: str,
    target: str | None = None,
    retries: int = 3,
    **kwargs,
) -> tuple[bool, str | None]:
    """Send a message via WhatsApp through OpenClaw CLI.

    Returns (success, error_or_none).
    """
    args = [
        "openclaw", "message", "send",
        "--channel", "whatsapp",
        "-m", message,
    ]

    if target:
        args.extend(["--target", str(target)])

    return _run_openclaw(args, retries=retries)


def deliver(
    message: str,
    channel: str = "telegram",
    target: str | None = None,
    retries: int = 3,
    buttons: list | None = None,
) -> tuple[bool, str | None]:
    """Convenience function: send a message via any OpenClaw channel.

    Args:
        message: The message text to send.
        channel: Channel name (telegram, whatsapp, discord, signal, etc).
        target: Target chat/user ID. Required for most channels.
        retries: Number of retry attempts with exponential backoff.
        buttons: Optional inline keyboard buttons (channel-dependent).

    Returns (success, error_or_none).
    """
    args = [
        "openclaw", "message", "send",
        "--channel", channel,
        "-m", message,
    ]

    if target:
        args.extend(["--target", str(target)])

    if buttons:
        args.extend(["--buttons", json.dumps(buttons)])

    return _run_openclaw(args, retries=retries)
