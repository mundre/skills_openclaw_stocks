"""MoltAssist LLM enrichment -- calls OpenClaw's existing LLM via subprocess."""

import subprocess


def enrich(
    message: str,
    category: str,
    action_hint: str | None = None,
    timeout: int = 10,
    context_prefix: str | None = None,
) -> str:
    """Add one sentence of context to a message using OpenClaw's LLM.

    Calls: openclaw agent --local -m <prompt>
    On any failure, timeout, or empty response: returns original message unchanged.

    context_prefix: optional cross-channel activity summary (from Channel Sync)
                    prepended to the prompt for cross-channel awareness.
    """
    # IMPORTANT: Keep system prompt neutral -- no persona, no relationship context.
    # Passing character context ("e.g. persona prompts") causes LLM safety
    # filters to refuse generation after certain conversation patterns.
    # Plain functional instruction only.
    prompt = (
        f"You are a notification assistant. Add one brief factual sentence of context "
        f"to this {category} notification. No preamble, no sign-off. "
        f"Return only the enriched notification text.\n\n"
    )
    if context_prefix:
        prompt += f"{context_prefix}\n\n"
    prompt += f"Notification: {message}"
    if action_hint:
        prompt += f"\nSuggested action: {action_hint}"

    try:
        result = subprocess.run(
            ["openclaw", "agent", "--local", "-m", prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            return message

        output = result.stdout.strip()
        if not output:
            return message

        # Take first line only -- no multi-line responses
        first_line = output.split("\n")[0].strip()
        return first_line if first_line else message

    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return message


def detect_llm_mode() -> str:
    """Detect which LLM mode is available via OpenClaw.

    Returns:
        'none'  -- Mode A: no LLM available (openclaw not installed or no model configured)
        'cloud' -- Mode B: cloud LLM configured via OpenClaw
        'mixed' -- Mode C: mixed (local + cloud) -- detected if model string contains 'local' or 'lmstudio'

    Checks by running: openclaw config get agents.defaults.model
    """
    try:
        result = subprocess.run(
            ["openclaw", "config", "get", "agents.defaults.model"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return "none"

        model = result.stdout.strip()
        if not model:
            return "none"

        # Mode C: mixed -- if the model string hints at local routing
        model_lower = model.lower()
        if any(hint in model_lower for hint in ("local", "lmstudio", "ollama", "lm-studio")):
            return "mixed"

        # Mode B: cloud LLM configured
        return "cloud"

    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return "none"


def is_enrichment_available() -> bool:
    """Return True if any LLM enrichment mode is available."""
    return detect_llm_mode() != "none"
