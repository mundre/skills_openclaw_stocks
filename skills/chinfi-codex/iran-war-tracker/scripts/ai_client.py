#!/usr/bin/env python3
"""Minimal OpenAI-compatible model client with safe fallback."""

from __future__ import annotations

import json
import os
import urllib.request


def has_model_config() -> bool:
    return any(
        [
            os.environ.get("OPENCLAW_MODEL_ENDPOINT", "").strip(),
            os.environ.get("OPENAI_API_KEY", "").strip(),
            os.environ.get("LLM_API_KEY", "").strip() and os.environ.get("LLM_API_BASE", "").strip(),
            os.environ.get("OPENCLAW_SESSION", "").strip(),
        ]
    )


def call_ai(prompt: str, timeout: int = 120) -> str:
    endpoint = os.environ.get("OPENCLAW_MODEL_ENDPOINT", "").strip()
    if endpoint:
        return _call_http(prompt, endpoint, timeout)

    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    openai_base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
    if openai_key:
        return _call_openai_compatible(prompt, openai_base, openai_key, timeout)

    api_key = os.environ.get("LLM_API_KEY", "").strip()
    api_base = os.environ.get("LLM_API_BASE", "").strip()
    if api_key and api_base:
        return _call_openai_compatible(prompt, api_base, api_key, timeout)

    if os.environ.get("OPENCLAW_SESSION", "").strip():
        return f"[AI_ANALYSIS_REQUEST]\n{prompt}\n[END_AI_ANALYSIS_REQUEST]"

    return ""


def _call_http(prompt: str, endpoint: str, timeout: int) -> str:
    payload = json.dumps({"prompt": prompt, "max_tokens": 2200, "temperature": 0.4}).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "iran-war-tracker/2.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        if "choices" in data and data["choices"]:
            choice = data["choices"][0]
            return choice.get("text", choice.get("message", {}).get("content", ""))
        return data.get("response", data.get("content", ""))
    except Exception:
        return ""


def _call_openai_compatible(prompt: str, base_url: str, api_key: str, timeout: int) -> str:
    if not base_url.endswith("/v1"):
        base_url = base_url.rstrip("/") + "/v1"
    payload = json.dumps(
        {
            "model": os.environ.get("OPENAI_MODEL", os.environ.get("LLM_MODEL", "gpt-4o-mini")),
            "messages": [
                {"role": "system", "content": "你是严谨的地缘政治与市场分析助手。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.4,
            "max_tokens": 2200,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
    except Exception:
        return ""
    return ""
