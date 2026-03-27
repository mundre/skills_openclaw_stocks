"""MoltAssist platform-aware formatting -- Telegram MarkdownV2, WhatsApp plain."""

EMOJI_MAP = {
    "email":      "",
    "calendar":   "",

    "health":     "",
    "deals":      "",
    "travel":     "",
    "finance":    "",
    "dev":        "",
    "system":     "",
    "weather":    "",
    "social":     "",
    "compliance": "",
    "custom":     "",
    "staff":      "",
}

URGENCY_EMOJI = {
    "critical": "",
    "high":     "",
    "medium":   "",
    "low":      "",
}

# Telegram MarkdownV2 special characters that must be escaped
_MD2_SPECIAL = r"_*[]()~`>#+-=|{}.!"


def escape_md2(text: str) -> str:
    """Escape all Telegram MarkdownV2 special characters."""
    return "".join(f"\\{c}" if c in _MD2_SPECIAL else c for c in text)


def format_for_telegram(
    message: str,
    urgency: str,
    category: str,
    action_hint: str | None = None,
) -> str:
    """Format a notification for Telegram using MarkdownV2."""
    emoji = EMOJI_MAP.get(category, "")
    urg_emoji = URGENCY_EMOJI.get(urgency, "")

    escaped_msg = escape_md2(message)
    escaped_cat = escape_md2(category.title())

    header = f"{emoji} *{escaped_cat}* {urg_emoji}"
    body = escaped_msg

    parts = [header, body]
    if action_hint:
        parts.append(f"-> _{escape_md2(action_hint)}_")

    return "\n".join(parts)


def format_for_whatsapp(
    message: str,
    urgency: str,
    category: str,
    action_hint: str | None = None,
) -> str:
    """Format a notification for WhatsApp -- plain text, no markdown."""
    emoji = EMOJI_MAP.get(category, "")
    urg_emoji = URGENCY_EMOJI.get(urgency, "")

    header = f"{emoji} {category.title()} {urg_emoji}"
    parts = [header, message]
    if action_hint:
        parts.append(f"-> {action_hint}")

    return "\n".join(parts)
