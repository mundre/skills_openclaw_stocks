#!/usr/bin/env python3
"""Run a stage-1 local execution lease for agent-compute-mesh."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job_path", help="Path to a stage-1 job spec JSON file")
    parser.add_argument(
        "--runtime-root",
        default=".runtime/leases",
        help="Directory where lease artifacts are written",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable output")
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("top-level JSON must be an object")
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def require(job: dict[str, Any], keys: list[str]) -> None:
    missing = [key for key in keys if key not in job]
    if missing:
        raise ValueError(f"missing required keys: {', '.join(missing)}")


def sanitize_name(value: str) -> str:
    out = []
    for char in value.lower():
        out.append(char if char.isalnum() else "-")
    return "".join(out).strip("-") or "item"


def materialize_input_texts(
    facet: dict[str, Any],
    sandbox_inbox: Path,
    max_items: int,
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for index, item in enumerate(facet.get("input_texts", [])[:max_items], start=1):
        if not isinstance(item, dict):
            raise ValueError("input_texts items must be objects")
        label = str(item.get("label") or f"text-{index}")
        source_type = str(item.get("source_type") or "text")
        text = str(item.get("text") or "")
        if not text:
            continue
        filename = f"{index:02d}-{sanitize_name(label)}.txt"
        sandbox_path = sandbox_inbox / filename
        sandbox_path.write_text(text, encoding="utf-8")
        evidence.append(
            {
                "evidence_id": f"evi_{index:03d}",
                "label": label,
                "source_type": source_type,
                "sha256": sha256_text(text),
                "excerpt": text[:280],
                "sandbox_path": str(sandbox_path.relative_to(sandbox_inbox.parent).as_posix()),
            }
        )
    return evidence


def materialize_input_files(
    facet: dict[str, Any],
    sandbox_inbox: Path,
    job_dir: Path,
    starting_index: int,
    max_items: int,
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    raw_items = facet.get("input_files", [])
    for offset, item in enumerate(raw_items[:max_items], start=0):
        label = f"file-{starting_index + offset}"
        source_type = "file"
        rel_path = ""
        if isinstance(item, str):
            rel_path = item
        elif isinstance(item, dict):
            rel_path = str(item.get("path") or "")
            label = str(item.get("label") or label)
            source_type = str(item.get("source_type") or source_type)
        if not rel_path:
            continue
        source_path = (job_dir / rel_path).resolve() if not Path(rel_path).is_absolute() else Path(rel_path)
        if not source_path.exists():
            raise ValueError(f"input file does not exist: {source_path}")
        filename = f"{starting_index + offset:02d}-{sanitize_name(label)}{source_path.suffix or '.txt'}"
        sandbox_path = sandbox_inbox / filename
        shutil.copy2(source_path, sandbox_path)
        raw = sandbox_path.read_bytes()
        excerpt = raw[:280].decode("utf-8", errors="replace")
        evidence.append(
            {
                "evidence_id": f"evi_{starting_index + offset:03d}",
                "label": label,
                "source_type": source_type,
                "sha256": sha256_bytes(raw),
                "excerpt": excerpt,
                "sandbox_path": str(sandbox_path.relative_to(sandbox_inbox.parent).as_posix()),
            }
        )
    return evidence


def run_evidence_scan(
    job: dict[str, Any],
    facet: dict[str, Any],
    sandbox_dir: Path,
    job_dir: Path,
    context: dict[str, Any],
) -> dict[str, Any]:
    inbox = sandbox_dir / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    max_items = int(job.get("search_budget", {}).get("max_evidence_items", 4))
    evidence = materialize_input_texts(facet, inbox, max_items)
    remaining = max(max_items - len(evidence), 0)
    evidence.extend(materialize_input_files(facet, inbox, job_dir, len(evidence) + 1, remaining))
    context["evidence"].extend(evidence)
    return {
        "facet_id": facet["facet_id"],
        "facet_type": facet["facet_type"],
        "status": "completed",
        "evidence_count": len(evidence),
    }


def build_suggestion(job: dict[str, Any], facet: dict[str, Any], context: dict[str, Any]) -> str:
    evidence = context["evidence"]
    evidence_lines = []
    for item in evidence[:3]:
        evidence_lines.append(f"- {item['label']}: {item['excerpt']}")
    acceptance = job.get("acceptance_contract", {})
    manual_merge = acceptance.get("manual_merge_check", [])
    do_not_apply = acceptance.get("do_not_apply_when", [])
    instruction_line = str(facet.get("instructions") or "").strip()
    lines = [
        f"Problem: {job['problem_statement']}",
        f"Host: {job['host_family']} {job['version_band']}",
    ]
    if instruction_line:
        lines.append(f"Execution note: {instruction_line}")
    lines.append("Suggested path:")
    lines.append("- Keep the work inside a fresh local execution lease and review receipts before reuse.")
    lines.append("- Use the evidence package to confirm version fit and acceptance rules before carrying the result forward.")
    lines.append("Evidence snapshot:")
    lines.extend(evidence_lines or ["- No evidence was collected."])
    if manual_merge:
        lines.append("Manual merge check:")
        lines.extend(f"- {item}" for item in manual_merge)
    if do_not_apply:
        lines.append("Do not apply when:")
        lines.extend(f"- {item}" for item in do_not_apply)
    return "\n".join(lines)


def run_advice_synthesis(
    job: dict[str, Any],
    facet: dict[str, Any],
    sandbox_dir: Path,
    context: dict[str, Any],
) -> dict[str, Any]:
    outbox = sandbox_dir / "outbox"
    outbox.mkdir(parents=True, exist_ok=True)
    suggestion = build_suggestion(job, facet, context)
    summary_path = outbox / "suggestion.txt"
    summary_path.write_text(suggestion, encoding="utf-8")
    context["result_text"] = suggestion
    return {
        "facet_id": facet["facet_id"],
        "facet_type": facet["facet_type"],
        "status": "completed",
        "output_path": str(summary_path.relative_to(sandbox_dir).as_posix()),
    }


def build_result_bundle(
    job: dict[str, Any],
    lease_id: str,
    facet_results: list[dict[str, Any]],
    context: dict[str, Any],
) -> dict[str, Any]:
    acceptance = job.get("acceptance_contract", {})
    result_text = context.get("result_text") or "No synthesis output was generated."
    return {
        "job_id": job["job_id"],
        "lease_id": lease_id,
        "task_summary": job["problem_statement"],
        "facet_results": facet_results,
        "result": result_text,
        "confidence": "stage1-local",
        "manual_merge_check": acceptance.get("manual_merge_check", []),
        "do_not_apply_when": acceptance.get("do_not_apply_when", []),
        "expected_evidence_types": acceptance.get("expected_evidence_types", []),
        "result_visibility": acceptance.get("result_visibility", "local-review"),
        "evidence": context["evidence"],
        "local_accept_required": bool(job.get("local_accept_required", True)),
        "official_recheck_required": bool(job.get("official_recheck_required", True)),
        "acceptance_status": "pending",
    }


def main() -> int:
    args = parse_args()
    job_path = Path(args.job_path).resolve()
    runtime_root = Path(args.runtime_root).resolve()
    job = load_json(job_path)
    require(
        job,
        [
            "job_id",
            "problem_statement",
            "host_family",
            "version_band",
            "privacy_tier",
            "deadline_at",
            "local_accept_required",
            "official_recheck_required",
            "facet_plan",
        ],
    )

    started_monotonic = time.monotonic()
    created_at = utc_now()
    lease_id = f"lease_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:8]}"
    thread_id = f"thr_{uuid.uuid4().hex[:10]}"
    sandbox_id = f"sbx_{uuid.uuid4().hex[:10]}"
    lease_root = runtime_root / lease_id
    sandbox_dir = lease_root / "sandbox"
    artifacts_dir = lease_root / "artifacts"
    sandbox_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    context: dict[str, Any] = {"evidence": [], "result_text": ""}
    facet_results: list[dict[str, Any]] = []
    tool_scope: set[str] = set()
    exit_reason = "completed"

    try:
        for facet in job["facet_plan"]:
            if not isinstance(facet, dict):
                raise ValueError("facet_plan entries must be objects")
            facet_type = facet.get("facet_type")
            tool_scope.update(str(item) for item in facet.get("tool_scope", []))
            if facet_type == "evidence-scan":
                facet_results.append(run_evidence_scan(job, facet, sandbox_dir, job_path.parent, context))
            elif facet_type == "advice-synthesis":
                facet_results.append(run_advice_synthesis(job, facet, sandbox_dir, context))
            else:
                raise ValueError(f"unsupported facet_type: {facet_type}")
    except Exception as exc:  # noqa: BLE001
        exit_reason = "failed"
        error_bundle = {
            "job_id": job["job_id"],
            "lease_id": lease_id,
            "task_summary": job["problem_statement"],
            "error": str(exc),
            "facet_results": facet_results,
            "local_accept_required": bool(job.get("local_accept_required", True)),
            "official_recheck_required": bool(job.get("official_recheck_required", True)),
            "acceptance_status": "pending",
        }
        write_json(artifacts_dir / "result_bundle.json", error_bundle)
        destroyed_at = utc_now()
        budget_digest = sha256_text(json.dumps(job.get("search_budget", {}), ensure_ascii=False, sort_keys=True))
        image_hash = sha256_bytes(Path(__file__).read_bytes())
        sandbox_receipt = {
            "job_id": job["job_id"],
            "lease_id": lease_id,
            "thread_id": thread_id,
            "sandbox_id": sandbox_id,
            "created_at": created_at,
            "destroyed_at": destroyed_at,
            "image_hash": image_hash,
            "budget_digest": budget_digest,
            "tool_scope": sorted(tool_scope),
            "exit_reason": exit_reason,
        }
        write_json(artifacts_dir / "sandbox_receipt.json", sandbox_receipt)
        write_json(
            artifacts_dir / "acceptance.json",
            {
                "job_id": job["job_id"],
                "lease_id": lease_id,
                "status": "pending",
                "local_accept_required": bool(job.get("local_accept_required", True)),
            },
        )
        print(str(exc), file=sys.stderr)
        return 1

    destroyed_at = utc_now()
    budget_digest = sha256_text(json.dumps(job.get("search_budget", {}), ensure_ascii=False, sort_keys=True))
    image_hash = sha256_bytes(Path(__file__).read_bytes())
    runtime_seconds = round(time.monotonic() - started_monotonic, 4)
    result_bundle = build_result_bundle(job, lease_id, facet_results, context)
    billing_receipt = {
        "job_id": job["job_id"],
        "lease_id": lease_id,
        "ledger_id": f"ledger_{lease_id}",
        "meter_digest": sha256_text(f"{lease_id}:{runtime_seconds}:{len(context['evidence'])}"),
        "estimated_cost": round(runtime_seconds * 0.05 + len(context["evidence"]) * 0.1, 4),
        "solver_amount": round(runtime_seconds * 0.05 + len(context["evidence"]) * 0.1, 4),
        "runtime_seconds": runtime_seconds,
        "evidence_count": len(context["evidence"]),
    }
    sandbox_receipt = {
        "job_id": job["job_id"],
        "lease_id": lease_id,
        "thread_id": thread_id,
        "sandbox_id": sandbox_id,
        "created_at": created_at,
        "destroyed_at": destroyed_at,
        "image_hash": image_hash,
        "budget_digest": budget_digest,
        "tool_scope": sorted(tool_scope),
        "exit_reason": exit_reason,
    }
    acceptance = {
        "job_id": job["job_id"],
        "lease_id": lease_id,
        "status": "pending",
        "local_accept_required": bool(job.get("local_accept_required", True)),
        "official_recheck_required": bool(job.get("official_recheck_required", True)),
        "review_required": True,
    }

    write_json(lease_root / "job_spec.normalized.json", job)
    write_json(artifacts_dir / "result_bundle.json", result_bundle)
    write_json(artifacts_dir / "sandbox_receipt.json", sandbox_receipt)
    write_json(artifacts_dir / "billing_receipt.json", billing_receipt)
    write_json(artifacts_dir / "acceptance.json", acceptance)

    output = {
        "lease_id": lease_id,
        "job_id": job["job_id"],
        "lease_root": str(lease_root),
        "artifacts_dir": str(artifacts_dir),
        "result_bundle": str(artifacts_dir / "result_bundle.json"),
        "sandbox_receipt": str(artifacts_dir / "sandbox_receipt.json"),
        "billing_receipt": str(artifacts_dir / "billing_receipt.json"),
        "acceptance": str(artifacts_dir / "acceptance.json"),
    }

    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"lease_id={lease_id}")
        print(f"lease_root={lease_root}")
        print(f"result_bundle={artifacts_dir / 'result_bundle.json'}")
        print(f"sandbox_receipt={artifacts_dir / 'sandbox_receipt.json'}")
        print(f"billing_receipt={artifacts_dir / 'billing_receipt.json'}")
        print(f"acceptance={artifacts_dir / 'acceptance.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
