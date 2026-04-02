"""
Pacta Metadata Schema v1.0 — construction, hashing, and verification utilities.

Task metadata is the 'language of commerce' between autonomous agents.
The schema defines what the work is; the smart contract handles settlement.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from eth_utils import keccak


# ---------------------------------------------------------------------------
# Canonical JSON
# ---------------------------------------------------------------------------

def canonicalize(obj: Any) -> str:
    """Produce deterministic JSON for hashing.

    Keys are sorted recursively, no trailing whitespace, no BOM.
    Two payloads with identical logical content always produce the same string.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash_bytes(data: bytes) -> str:
    """Keccak256 hash of raw bytes, returned as a 0x-prefixed hex string."""
    return "0x" + keccak(data).hex()


def hash_payload(obj: Dict[str, Any]) -> str:
    """Keccak256 hash of the canonical JSON representation of a metadata or delivery payload."""
    return _hash_bytes(canonicalize(obj).encode("utf-8"))


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------

def build_task_metadata(
    task_type: str,
    description: str,
    requirements: Optional[List[str]] = None,
    input_uri: Optional[str] = None,
    input_hash: Optional[str] = None,
    output_format: Optional[str] = None,
    delivery_method: Optional[str] = None,
) -> Tuple[Dict[str, Any], str, str]:
    """Build a v1 task metadata envelope.

    Returns (metadata_dict, keccak256_hash, canonical_json_string).
    The hash is ready to pass as ``metadataHash`` to ``createAgreement``.
    """
    if not task_type:
        raise ValueError("task_type is required")
    if not description:
        raise ValueError("description is required")

    task: Dict[str, Any] = {
        "type": task_type,
        "description": description,
    }

    if requirements:
        task["requirements"] = requirements

    if input_uri and input_hash:
        task["input"] = {"uri": input_uri, "hash": input_hash}

    if output_format or delivery_method:
        output: Dict[str, Any] = {}
        if output_format:
            output["format"] = output_format
        if delivery_method:
            output["deliveryMethod"] = delivery_method
        task["output"] = output

    metadata: Dict[str, Any] = {"pacta": "1.0", "task": task}
    canonical = canonicalize(metadata)
    h = _hash_bytes(canonical.encode("utf-8"))
    return metadata, h, canonical


def build_delivery_payload(
    delivery_type: str,
    summary: str,
    artifacts: List[Dict[str, Any]],
) -> Tuple[Dict[str, Any], str, str]:
    """Build a v1 delivery payload envelope.

    Returns (payload_dict, keccak256_hash, canonical_json_string).
    The hash is ready to pass as ``deliveryHash`` to ``deliverAgreement``.
    """
    if not delivery_type:
        raise ValueError("delivery_type is required")
    if not summary:
        raise ValueError("summary is required")
    if not artifacts:
        raise ValueError("at least one artifact is required")

    payload: Dict[str, Any] = {
        "pacta": "1.0",
        "delivery": {
            "type": delivery_type,
            "summary": summary,
            "artifacts": artifacts,
        },
    }

    canonical = canonicalize(payload)
    h = _hash_bytes(canonical.encode("utf-8"))
    return payload, h, canonical


# ---------------------------------------------------------------------------
# Hashing helpers
# ---------------------------------------------------------------------------

def hash_content(content: bytes) -> str:
    """Keccak256 hash of raw content bytes.

    Use this to compute ``task.input.hash`` or ``delivery.artifacts[].hash``
    from actual file content.
    """
    return _hash_bytes(content)


def hash_content_string(content: str) -> str:
    """Keccak256 hash of a UTF-8 string."""
    return _hash_bytes(content.encode("utf-8"))


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_task_metadata(json_string: str, expected_hash: str) -> bool:
    """Verify that a task metadata JSON string matches an expected on-chain hash."""
    h = _hash_bytes(json_string.encode("utf-8"))
    return h.lower() == expected_hash.lower()


def verify_delivery_payload(json_string: str, expected_hash: str) -> bool:
    """Verify that a delivery payload JSON string matches an expected on-chain hash."""
    h = _hash_bytes(json_string.encode("utf-8"))
    return h.lower() == expected_hash.lower()


def verify_content(content: bytes, expected_hash: str) -> bool:
    """Verify that content bytes match an expected hash."""
    return hash_content(content).lower() == expected_hash.lower()


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_task_metadata(json_string: str) -> Optional[Dict[str, Any]]:
    """Parse and validate a task metadata JSON string.

    Returns None if the JSON is not valid Pacta v1 task metadata.
    """
    try:
        obj = json.loads(json_string)
        if obj.get("pacta") != "1.0":
            return None
        task = obj.get("task")
        if not task or not task.get("type") or not task.get("description"):
            return None
        return obj
    except (json.JSONDecodeError, TypeError, AttributeError):
        return None


def parse_delivery_payload(json_string: str) -> Optional[Dict[str, Any]]:
    """Parse and validate a delivery payload JSON string.

    Returns None if the JSON is not valid Pacta v1 delivery payload.
    """
    try:
        obj = json.loads(json_string)
        if obj.get("pacta") != "1.0":
            return None
        delivery = obj.get("delivery")
        if not delivery or not delivery.get("type") or not delivery.get("summary"):
            return None
        artifacts = delivery.get("artifacts")
        if not isinstance(artifacts, list) or len(artifacts) == 0:
            return None
        return obj
    except (json.JSONDecodeError, TypeError, AttributeError):
        return None
