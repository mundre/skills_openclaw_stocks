#!/usr/bin/env python3
"""Offline ablation for agent-travel suggestion structure.

This script uses a few real local Codex session files as anchors, then compares:
1. legacy suggestion shape without explicit rationale fields
2. current suggestion shape with solves_point/new_idea/fit_reason

The goal is to estimate whether the new structure improves next-turn usability.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any


@dataclass(frozen=True)
class Case:
    case_id: str
    label: str
    session_path: Path
    summary: str
    blocker_keywords: tuple[str, ...]
    constraint_keywords: tuple[str, ...]
    legacy: dict[str, Any]
    enhanced: dict[str, Any]


ROOT = Path(__file__).resolve().parents[1]
SESSION_ROOT = Path.home() / ".codex"


CASES: tuple[Case, ...] = (
    Case(
        case_id="travel_design",
        label="Agent travel skill design",
        session_path=SESSION_ROOT
        / "sessions/2026/04/19/rollout-2026-04-19T03-08-50-019da1fe-e5c0-7560-ad2c-a7d384eb9d11.jsonl",
        summary=(
            "Design a lightweight agent-travel skill for OpenClaw and Hermes that "
            "uses heartbeat or idle windows to search official docs plus community "
            "sources, cross-validates each suggestion, and brings back advisory-only hints."
        ),
        blocker_keywords=("agent-travel", "heartbeat", "openclaw", "hermes", "advisory"),
        constraint_keywords=("official", "cross-validate", "active thread", "lightweight"),
        legacy={
            "title": "Keep travel results advisory",
            "applies_when": "Background research is needed for a still-active agent problem.",
            "hint": (
                "Search official docs first, then community threads, and store a few "
                "advisory-only hints for the next task."
            ),
            "confidence": "medium",
            "manual_check": (
                "Confirm the host still supports heartbeat or idle travel and that each "
                "stored hint has official grounding plus one community confirmation."
            ),
            "evidence": [
                "official: https://docs.openclaw.ai/gateway/heartbeat",
                "official: https://hermes-agent.nousresearch.com/docs/developer-guide/creating-skills/",
                "community: https://github.com/NousResearch/hermes-agent",
            ],
        },
        enhanced={
            "title": "Keep travel results advisory",
            "applies_when": "Background research is needed for a still-active agent problem.",
            "hint": (
                "Search official docs first, then community threads, and store a few "
                "advisory-only hints for the next task."
            ),
            "confidence": "medium",
            "manual_check": (
                "Confirm the host still supports heartbeat or idle travel and that each "
                "stored hint has official grounding plus one community confirmation."
            ),
            "solves_point": (
                "The active thread needs a safe way to learn OpenClaw and Hermes "
                "community practice during heartbeat without contaminating core instructions."
            ),
            "new_idea": (
                "Persist travel output in an isolated advisory channel so the next turn can "
                "reuse validated hints without auto-applying them."
            ),
            "fit_reason": (
                "This matches the user's lightweight cross-agent design because it keeps "
                "search broad, keeps suggestions advisory, and keeps official cross-checking mandatory."
            ),
            "version_scope": (
                "Use for current OpenClaw and Hermes skill workflows where heartbeat or idle wakeups can launch web research."
            ),
            "do_not_apply_when": (
                "Do not reuse when the host forbids network access or the thread asks for automatic action instead of advisory hints."
            ),
            "evidence": [
                "official: https://docs.openclaw.ai/gateway/heartbeat",
                "official: https://hermes-agent.nousresearch.com/docs/developer-guide/creating-skills/",
                "community: https://github.com/NousResearch/hermes-agent",
            ],
        },
    ),
    Case(
        case_id="history_compression",
        label="Thread handoff summary compression",
        session_path=SESSION_ROOT
        / "archived_sessions/rollout-2026-04-18T15-20-18-019d9f76-3aa9-7da3-8c01-93f59d7160f5.jsonl",
        summary=(
            "Compress a long Codex thread into a strict four-part handoff summary with "
            "Goal, Done, Current Status, and Next Step, preserving key paths and constraints."
        ),
        blocker_keywords=("history", "summary", "goal", "next step", "handoff"),
        constraint_keywords=("four-part", "strict format", "paths", "handoff"),
        legacy={
            "title": "Use a fixed handoff summary",
            "applies_when": "The thread is long and a human needs a fast handoff.",
            "hint": (
                "Compress the thread into four short sections, preserve key paths and "
                "configuration names, and call out missing information."
            ),
            "confidence": "high",
            "manual_check": (
                "Confirm the output keeps the requested four sections and that key paths "
                "or identifiers still appear verbatim."
            ),
            "evidence": [
                "official_discussion: https://developers.openai.com/codex/skills",
                "community: https://github.com/openai/codex/issues/5957",
            ],
        },
        enhanced={
            "title": "Use a fixed handoff summary",
            "applies_when": "The thread is long and a human needs a fast handoff.",
            "hint": (
                "Compress the thread into four short sections, preserve key paths and "
                "configuration names, and call out missing information."
            ),
            "confidence": "high",
            "manual_check": (
                "Confirm the output keeps the requested four sections and that key paths "
                "or identifiers still appear verbatim."
            ),
            "solves_point": (
                "The thread needs a handoff summary that a human can scan quickly without "
                "losing the exact Goal, Current Status, and Next Step structure."
            ),
            "new_idea": (
                "Treat the compression output as a fixed operator handoff artifact instead "
                "of a free-form recap so the next reader can resume immediately."
            ),
            "fit_reason": (
                "This fits the user's constraint because the thread already defines a strict "
                "four-part summary format and values exact paths, identifiers, and missing-info flags."
            ),
            "version_scope": (
                "Use when a long Codex thread needs a human handoff and the four-part summary contract still applies."
            ),
            "do_not_apply_when": (
                "Do not reuse when the handoff consumer expects a full transcript, a machine-readable export, or a different section order."
            ),
            "evidence": [
                "official_discussion: https://developers.openai.com/codex/skills",
                "community: https://github.com/openai/codex/issues/5957",
            ],
        },
    ),
    Case(
        case_id="telegram_control",
        label="Control Codex from Telegram or phone",
        session_path=SESSION_ROOT
        / "sessions/2026/04/16/rollout-2026-04-16T17-41-03-019d95aa-5d25-7dd0-b5f9-399df9459743.jsonl",
        summary=(
            "Find a workable way to control Codex from Telegram or a phone while keeping "
            "the coding loop on the desktop side."
        ),
        blocker_keywords=("telegram", "phone", "codex", "desktop", "bridge"),
        constraint_keywords=("control", "mobile", "desktop side", "community"),
        legacy={
            "title": "Keep the execution loop on desktop",
            "applies_when": "The user wants mobile control without moving the coding agent off the desktop.",
            "hint": (
                "Use a chat bridge for control and keep the actual coding session on the desktop "
                "side so file access and tooling stay stable."
            ),
            "confidence": "medium",
            "manual_check": (
                "Confirm the bridge can forward commands and status updates while the desktop "
                "session retains workspace and tool access."
            ),
            "evidence": [
                "official_discussion: https://developers.openai.com/codex/skills",
                "community: https://github.com/openai/codex/issues/4110",
            ],
        },
        enhanced={
            "title": "Keep the execution loop on desktop",
            "applies_when": "The user wants mobile control without moving the coding agent off the desktop.",
            "hint": (
                "Use a chat bridge for control and keep the actual coding session on the desktop "
                "side so file access and tooling stay stable."
            ),
            "confidence": "medium",
            "manual_check": (
                "Confirm the bridge can forward commands and status updates while the desktop "
                "session retains workspace and tool access."
            ),
            "solves_point": (
                "The thread is choosing how to control Codex from Telegram or a phone without "
                "breaking the desktop coding environment."
            ),
            "new_idea": (
                "Split control from execution so Telegram acts as a command surface and the "
                "desktop remains the only place that runs code and owns the workspace."
            ),
            "fit_reason": (
                "This fits the user's mobile-control goal because it preserves the stable "
                "desktop toolchain while still enabling lightweight remote commands."
            ),
            "version_scope": (
                "Use when Codex still runs in a desktop or workstation environment and mobile access acts as a control layer."
            ),
            "do_not_apply_when": (
                "Do not reuse when the user needs full mobile-native coding, direct workspace access from the phone, or a first-party mobile app."
            ),
            "evidence": [
                "official_discussion: https://developers.openai.com/codex/skills",
                "community: https://github.com/openai/codex/issues/4110",
            ],
        },
    ),
    Case(
        case_id="openclaw_primary_agent",
        label="OpenClaw primary agent and slower heartbeat",
        session_path=SESSION_ROOT
        / "sessions/2026/04/17/rollout-2026-04-17T05-29-02-019d9832-8a49-78e3-8710-b09c468e4593.jsonl",
        summary=(
            "Configure OpenClaw to keep one primary agent active, slow the heartbeat, route "
            "cron tasks to that primary worker, and keep a second agent dormant until explicit parallel work is needed."
        ),
        blocker_keywords=("openclaw", "agent", "heartbeat", "cron", "memory", "talk-normal"),
        constraint_keywords=("primary", "secondary", "slow", "parallel", "community"),
        legacy={
            "title": "Keep one primary OpenClaw worker",
            "applies_when": "The workspace wants one stable agent and a dormant parallel worker.",
            "hint": (
                "Route regular cron work to the primary worker, slow the heartbeat, and "
                "activate the secondary worker only for explicit parallel tasks."
            ),
            "confidence": "medium",
            "manual_check": (
                "Confirm only one agent is active by default, heartbeat frequency is reduced, "
                "and shared workspace rules remain stable."
            ),
            "evidence": [
                "official: https://docs.openclaw.ai/gateway/heartbeat",
                "community: https://github.com/hexiecs/talk-normal",
            ],
        },
        enhanced={
            "title": "Keep one primary OpenClaw worker",
            "applies_when": "The workspace wants one stable agent and a dormant parallel worker.",
            "hint": (
                "Route regular cron work to the primary worker, slow the heartbeat, and "
                "activate the secondary worker only for explicit parallel tasks."
            ),
            "confidence": "medium",
            "manual_check": (
                "Confirm only one agent is active by default, heartbeat frequency is reduced, "
                "and shared workspace rules remain stable."
            ),
            "solves_point": (
                "The current thread needs a stable OpenClaw layout with one primary agent, a slower heartbeat, "
                "and a second worker reserved for explicit parallel work."
            ),
            "new_idea": (
                "Treat the secondary agent as a cold standby path while community prompt, soul, "
                "memory, and talk-normal tuning all stay attached to the primary worker."
            ),
            "fit_reason": (
                "This matches the user's operations-heavy setup because cron traffic, context hygiene, "
                "and drift control are easier to keep consistent when one primary agent owns the workflow."
            ),
            "version_scope": (
                "Use when the workspace still wants one always-on primary OpenClaw worker and heartbeat remains configurable."
            ),
            "do_not_apply_when": (
                "Do not reuse when the workload now needs permanent parallel agents or when heartbeat latency must stay aggressive."
            ),
            "evidence": [
                "official: https://docs.openclaw.ai/gateway/heartbeat",
                "community: https://github.com/hexiecs/talk-normal",
            ],
        },
    ),
)


TEXT_FIELDS = (
    "title",
    "applies_when",
    "hint",
    "manual_check",
    "solves_point",
    "new_idea",
    "fit_reason",
    "version_scope",
    "do_not_apply_when",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "assets/historical_codex_ablation_report.json",
        help="Where to write the JSON report",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def combined_text(payload: dict[str, Any]) -> str:
    return " ".join(str(payload.get(field, "")) for field in TEXT_FIELDS).lower()


def keyword_ratio(keywords: tuple[str, ...], text: str) -> tuple[float, list[str]]:
    matched = [keyword for keyword in keywords if keyword.lower() in text]
    if not keywords:
        return 1.0, []
    return len(matched) / len(keywords), matched


def official_grounding(payload: dict[str, Any]) -> float:
    evidence = [str(item).lower() for item in payload.get("evidence", [])]
    has_official = any(
        item.startswith("official:") or item.startswith("official_discussion:")
        for item in evidence
    )
    has_community = any(
        item.startswith("community:") or item.startswith("social:")
        for item in evidence
    )
    return 1.0 if has_official and has_community else 0.0


def rationale_presence(payload: dict[str, Any]) -> dict[str, float]:
    return {
        "solves_point": 1.0 if str(payload.get("solves_point", "")).strip() else 0.0,
        "new_idea": 1.0 if str(payload.get("new_idea", "")).strip() else 0.0,
        "fit_reason": 1.0 if str(payload.get("fit_reason", "")).strip() else 0.0,
        "version_scope": 1.0 if str(payload.get("version_scope", "")).strip() else 0.0,
        "do_not_apply_when": 1.0 if str(payload.get("do_not_apply_when", "")).strip() else 0.0,
    }


def score_case(case: Case, payload: dict[str, Any], session_text: str) -> dict[str, Any]:
    text = combined_text(payload)
    blocker_score, blocker_hits = keyword_ratio(case.blocker_keywords, text)
    constraint_score, constraint_hits = keyword_ratio(case.constraint_keywords, text)
    source_score, source_hits = keyword_ratio(case.blocker_keywords, session_text.lower())
    rationale = rationale_presence(payload)
    rationale_score = mean(rationale.values())
    grounding_score = official_grounding(payload)

    total = (
        blocker_score * 0.30
        + constraint_score * 0.20
        + rationale["solves_point"] * 0.10
        + rationale["new_idea"] * 0.10
        + rationale["fit_reason"] * 0.10
        + rationale["version_scope"] * 0.05
        + rationale["do_not_apply_when"] * 0.05
        + grounding_score * 0.10
    )

    return {
        "source_grounding_score": round(source_score, 4),
        "source_grounding_hits": source_hits,
        "thread_focus_score": round(blocker_score, 4),
        "thread_focus_hits": blocker_hits,
        "constraint_fit_score": round(constraint_score, 4),
        "constraint_fit_hits": constraint_hits,
        "rationale_visibility": rationale,
        "rationale_score": round(rationale_score, 4),
        "official_grounding_score": round(grounding_score, 4),
        "total_score": round(total, 4),
    }


def evaluate_case(case: Case) -> dict[str, Any]:
    if not case.session_path.exists():
        raise FileNotFoundError(f"missing session file: {case.session_path}")

    session_text = read_text(case.session_path)
    legacy_scores = score_case(case, case.legacy, session_text)
    enhanced_scores = score_case(case, case.enhanced, session_text)

    return {
        "case_id": case.case_id,
        "label": case.label,
        "source_session": f".codex/{case.session_path.relative_to(SESSION_ROOT).as_posix()}",
        "summary": case.summary,
        "legacy": {
            "suggestion": case.legacy,
            "scores": legacy_scores,
        },
        "enhanced": {
            "suggestion": case.enhanced,
            "scores": enhanced_scores,
        },
        "uplift": {
            "thread_focus": round(
                enhanced_scores["thread_focus_score"] - legacy_scores["thread_focus_score"], 4
            ),
            "constraint_fit": round(
                enhanced_scores["constraint_fit_score"] - legacy_scores["constraint_fit_score"], 4
            ),
            "rationale_score": round(
                enhanced_scores["rationale_score"] - legacy_scores["rationale_score"], 4
            ),
            "total_score": round(
                enhanced_scores["total_score"] - legacy_scores["total_score"], 4
            ),
        },
    }


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    legacy_scores = [case["legacy"]["scores"]["total_score"] for case in results]
    enhanced_scores = [case["enhanced"]["scores"]["total_score"] for case in results]

    return {
        "cases": len(results),
        "legacy_average": round(mean(legacy_scores), 4),
        "enhanced_average": round(mean(enhanced_scores), 4),
        "average_uplift": round(mean(enhanced - legacy for legacy, enhanced in zip(legacy_scores, enhanced_scores)), 4),
        "all_cases_improved": all(enhanced > legacy for legacy, enhanced in zip(legacy_scores, enhanced_scores)),
    }


def main() -> int:
    args = parse_args()
    results = [evaluate_case(case) for case in CASES]
    report = {
        "kind": "agent-travel-historical-codex-ablation",
        "note": (
            "Offline structural ablation against real local Codex session anchors. "
            "This measures how much explicit rationale fields improve next-turn readability "
            "and retrieval fit. It does not simulate live web search latency."
        ),
        "summary": summarize(results),
        "results": results,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {args.output}")
    print(
        "Average total score:",
        f"legacy={report['summary']['legacy_average']}",
        f"enhanced={report['summary']['enhanced_average']}",
        f"uplift={report['summary']['average_uplift']}",
    )
    print(f"All cases improved: {report['summary']['all_cases_improved']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
