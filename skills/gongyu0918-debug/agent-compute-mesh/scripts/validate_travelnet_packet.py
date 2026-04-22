#!/usr/bin/env python3
"""Validate example travelnet packet JSON."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


AGENT_ID_RE = re.compile(r"^agt_[a-z0-9]{6,64}$")
PACKET_TYPES = {"JOIN_ANNOUNCE", "WORK_ASK_HEADER", "WORK_RESULT", "WORK_SETTLEMENT"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Path to a travelnet packet JSON file")
    return parser.parse_args()


def fail(errors: list[str]) -> int:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1


def parse_iso(value: str) -> None:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    datetime.fromisoformat(value)


def require_fields(packet: dict[str, object], required: set[str], errors: list[str]) -> None:
    missing = sorted(required - set(packet))
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")


def require_positive_number(packet: dict[str, object], key: str, errors: list[str]) -> float | None:
    value = packet.get(key)
    if not isinstance(value, (int, float)):
        errors.append(f"{key} must be a number")
        return None
    if value < 0:
        errors.append(f"{key} must be non-negative")
        return None
    return float(value)


def require_agent_id(value: object, key: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not AGENT_ID_RE.match(value):
        errors.append(f"{key} must match {AGENT_ID_RE.pattern}")


def require_str_list(value: object, key: str, errors: list[str], allow_empty: bool = False) -> None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        errors.append(f"{key} must be a list of strings")
        return
    if not allow_empty and not value:
        errors.append(f"{key} must not be empty")


def require_str(value: object, key: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value:
        errors.append(f"{key} must be a non-empty string")


def parse_iso_or_error(value: object, key: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str):
        errors.append(f"{key} must be a string")
        return None
    try:
        raw = value[:-1] + "+00:00" if value.endswith("Z") else value
        return datetime.fromisoformat(raw)
    except ValueError as exc:
        errors.append(f"{key} is not valid ISO-8601: {exc}")
        return None


def require_object(value: object, key: str, errors: list[str]) -> dict[str, object] | None:
    if not isinstance(value, dict):
        errors.append(f"{key} must be an object")
        return None
    return value


def validate_sandbox_receipt(receipt: dict[str, object], errors: list[str]) -> None:
    require_fields(
        receipt,
        {
            "lease_id",
            "thread_id",
            "sandbox_id",
            "created_at",
            "destroyed_at",
            "image_hash",
            "budget_digest",
            "tool_scope",
            "exit_reason",
        },
        errors,
    )
    for key in ("lease_id", "thread_id", "sandbox_id", "image_hash", "budget_digest", "exit_reason"):
        require_str(receipt.get(key), f"sandbox_receipt.{key}", errors)
    require_str_list(receipt.get("tool_scope"), "sandbox_receipt.tool_scope", errors)
    created_at = parse_iso_or_error(receipt.get("created_at"), "sandbox_receipt.created_at", errors)
    destroyed_at = parse_iso_or_error(receipt.get("destroyed_at"), "sandbox_receipt.destroyed_at", errors)
    if created_at and destroyed_at and destroyed_at < created_at:
        errors.append("sandbox_receipt.destroyed_at must be later than or equal to sandbox_receipt.created_at")


def validate_billing_receipt(receipt: dict[str, object], errors: list[str]) -> None:
    require_fields(receipt, {"ledger_id", "meter_digest", "estimated_cost", "solver_amount"}, errors)
    require_str(receipt.get("ledger_id"), "billing_receipt.ledger_id", errors)
    require_str(receipt.get("meter_digest"), "billing_receipt.meter_digest", errors)
    require_positive_number(receipt, "estimated_cost", errors)
    require_positive_number(receipt, "solver_amount", errors)


def validate_join(packet: dict[str, object], errors: list[str]) -> None:
    require_fields(
        packet,
        {
            "packet_type",
            "packet_version",
            "from_agent_id",
            "timestamp",
            "signature",
            "compute_class",
            "model_band",
            "bond_amount",
            "operator_id",
            "warm_start_requested",
            "public_channels",
        },
        errors,
    )
    require_agent_id(packet.get("from_agent_id"), "from_agent_id", errors)
    require_positive_number(packet, "bond_amount", errors)
    require_str(packet.get("operator_id"), "operator_id", errors)
    if not isinstance(packet.get("warm_start_requested"), bool):
        errors.append("warm_start_requested must be boolean")
    require_str_list(packet.get("public_channels"), "public_channels", errors)


def validate_header(packet: dict[str, object], errors: list[str]) -> None:
    require_fields(
        packet,
        {
            "packet_type",
            "packet_version",
            "job_id",
            "from_agent_id",
            "timestamp",
            "signature",
            "host_family",
            "version_band",
            "symptom_tags",
            "constraint_tags",
            "reward_lock",
            "deadline_at",
            "privacy_tier",
            "fingerprint_cid",
            "local_accept_required",
            "official_recheck_required",
        },
        errors,
    )
    require_agent_id(packet.get("from_agent_id"), "from_agent_id", errors)
    require_str_list(packet.get("symptom_tags"), "symptom_tags", errors)
    require_str_list(packet.get("constraint_tags"), "constraint_tags", errors, allow_empty=True)
    require_positive_number(packet, "reward_lock", errors)
    if packet.get("privacy_tier") != "P0":
        errors.append("WORK_ASK_HEADER privacy_tier must be P0")
    if not isinstance(packet.get("fingerprint_cid"), str):
        errors.append("fingerprint_cid must be a string")
    if packet.get("local_accept_required") is not True:
        errors.append("local_accept_required must be true")
    if packet.get("official_recheck_required") is not True:
        errors.append("official_recheck_required must be true")


def validate_result(packet: dict[str, object], errors: list[str]) -> None:
    require_fields(
        packet,
        {
            "packet_type",
            "packet_version",
            "job_id",
            "from_agent_id",
            "timestamp",
            "signature",
            "facet_id",
            "result_bundle_cid",
            "evidence_count",
            "advisory_only",
            "official_recheck_required",
            "local_accept_required",
            "sandbox_receipt",
            "billing_receipt",
        },
        errors,
    )
    require_agent_id(packet.get("from_agent_id"), "from_agent_id", errors)
    require_positive_number(packet, "evidence_count", errors)
    if packet.get("advisory_only") is not True:
        errors.append("advisory_only must be true")
    if packet.get("official_recheck_required") is not True:
        errors.append("official_recheck_required must be true")
    if packet.get("local_accept_required") is not True:
        errors.append("local_accept_required must be true")
    sandbox_receipt = require_object(packet.get("sandbox_receipt"), "sandbox_receipt", errors)
    if sandbox_receipt is not None:
        validate_sandbox_receipt(sandbox_receipt, errors)
    billing_receipt = require_object(packet.get("billing_receipt"), "billing_receipt", errors)
    if billing_receipt is not None:
        validate_billing_receipt(billing_receipt, errors)


def validate_settlement(packet: dict[str, object], errors: list[str]) -> None:
    require_fields(
        packet,
        {
            "packet_type",
            "packet_version",
            "job_id",
            "settlement_id",
            "payer_agent_id",
            "solver_agent_id",
            "validator_agent_ids",
            "relay_agent_ids",
            "timestamp",
            "signature",
            "solver_amount",
            "validator_fee",
            "relay_fee",
            "treasury_refill",
            "burn_amount",
            "total_debit",
            "receipt_cid",
        },
        errors,
    )
    require_agent_id(packet.get("payer_agent_id"), "payer_agent_id", errors)
    require_agent_id(packet.get("solver_agent_id"), "solver_agent_id", errors)
    require_str_list(packet.get("validator_agent_ids"), "validator_agent_ids", errors, allow_empty=True)
    require_str_list(packet.get("relay_agent_ids"), "relay_agent_ids", errors, allow_empty=True)

    solver_amount = require_positive_number(packet, "solver_amount", errors) or 0.0
    validator_fee = require_positive_number(packet, "validator_fee", errors) or 0.0
    relay_fee = require_positive_number(packet, "relay_fee", errors) or 0.0
    treasury_refill = require_positive_number(packet, "treasury_refill", errors) or 0.0
    burn_amount = require_positive_number(packet, "burn_amount", errors) or 0.0
    total_debit = require_positive_number(packet, "total_debit", errors) or 0.0

    expected_total = solver_amount + validator_fee + relay_fee + treasury_refill + burn_amount
    if abs(total_debit - expected_total) > 1e-9:
        errors.append(
            "total_debit must equal solver_amount + validator_fee + relay_fee + treasury_refill + burn_amount"
        )


def main() -> int:
    args = parse_args()
    path = Path(args.path)
    if not path.exists():
        return fail([f"file not found: {path}"])

    try:
        packet = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return fail([f"invalid JSON: {exc}"])

    if not isinstance(packet, dict):
        return fail(["top-level JSON value must be an object"])

    errors: list[str] = []

    packet_type = packet.get("packet_type")
    if packet_type not in PACKET_TYPES:
        errors.append(f"packet_type must be one of: {', '.join(sorted(PACKET_TYPES))}")

    for key in ("packet_version", "timestamp", "signature"):
        if key not in packet:
            errors.append(f"missing field: {key}")

    timestamp = packet.get("timestamp")
    if isinstance(timestamp, str):
        try:
            parse_iso(timestamp)
        except ValueError as exc:
            errors.append(f"timestamp is not valid ISO-8601: {exc}")
    else:
        errors.append("timestamp must be a string")

    signature = packet.get("signature")
    if not isinstance(signature, str) or len(signature) < 16:
        errors.append("signature must be a non-empty string")

    if packet_type == "JOIN_ANNOUNCE":
        validate_join(packet, errors)
    elif packet_type == "WORK_ASK_HEADER":
        validate_header(packet, errors)
    elif packet_type == "WORK_RESULT":
        validate_result(packet, errors)
    elif packet_type == "WORK_SETTLEMENT":
        validate_settlement(packet, errors)

    if errors:
        return fail(errors)

    print(f"OK: validated {packet_type} packet in {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
