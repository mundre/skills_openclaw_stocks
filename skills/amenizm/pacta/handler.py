"""Pacta skill handler.

This module bridges ClawHub skill commands to the Pacta Python SDK.
Defaults are loaded from pacta_enabled.json (bundled) and can be overridden with env vars.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, Tuple
from urllib.parse import quote

# Import from bundled copies in the skill directory
sys.path.insert(0, os.path.dirname(__file__))

from pacta_client import PactaClient, PactaClientConfig  # noqa: E402

SKILL_DIR = Path(__file__).resolve().parent
MANIFEST_PATH = SKILL_DIR / "pacta_enabled.json"
CHECKSUMS_PATH = SKILL_DIR / "checksums.json"


def _verify_integrity() -> None:
    """Verify bundled skill files have not been tampered with.

    Reads checksums.json and compares SHA-256 hashes against the actual files.
    Raises RuntimeError if any file has been modified post-install.
    """
    if not CHECKSUMS_PATH.exists():
        return  # No checksums file — skip (e.g., development mode)

    expected = json.loads(CHECKSUMS_PATH.read_text())
    for filename, expected_hash in expected.items():
        filepath = SKILL_DIR / filename
        if not filepath.exists():
            raise RuntimeError(
                f"Pacta skill integrity check failed: {filename} is missing. "
                f"The skill bundle may be corrupted. Reinstall with: openclaw skills install pacta"
            )
        actual_hash = hashlib.sha256(filepath.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise RuntimeError(
                f"Pacta skill integrity check failed: {filename} has been modified. "
                f"Expected SHA-256: {expected_hash}, got: {actual_hash}. "
                f"The skill bundle may have been tampered with. Reinstall with: openclaw skills install pacta"
            )


_verify_integrity()


def _clean_manifest_string(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    cleaned = value.strip()
    if not cleaned:
        return ""
    if "TODO" in cleaned.upper():
        return ""
    return cleaned


def _load_manifest() -> Dict[str, Any]:
    if not MANIFEST_PATH.exists():
        return {}
    return json.loads(MANIFEST_PATH.read_text())


def _manifest_defaults(manifest: Dict[str, Any]) -> Dict[str, Any]:
    defaults = manifest.get("defaults", {})
    fees = manifest.get("fees", {})
    tokens = manifest.get("tokens", {})
    default_symbol = str(defaults.get("token_symbol", "USDC")).upper()
    normalized_tokens = {}

    for symbol, config in tokens.items():
        if not isinstance(config, dict):
            continue
        address = _clean_manifest_string(config.get("address"))
        if not address:
            continue
        normalized_tokens[str(symbol).upper()] = {
            "symbol": str(symbol).upper(),
            "address": address,
            "decimals": config.get("decimals"),
        }

    return {
        "rpc_url": _clean_manifest_string(manifest.get("rpc_url")) or "https://mainnet.base.org",
        "subgraph_url": _clean_manifest_string(manifest.get("subgraph_url")),
        "core_address": _clean_manifest_string(manifest.get("core_address")),
        "default_token_symbol": default_symbol,
        "default_token": normalized_tokens.get(default_symbol, {}),
        "tokens_by_symbol": normalized_tokens,
        "accept_in_hours": defaults.get("accept_window_hours", 24),
        "delivery_in_hours": defaults.get("delivery_window_hours", 72),
        "review_in_hours": defaults.get("review_window_hours", 48),
        "protocol_fee_bps": fees.get("protocol_fee_bps"),
        "keeper_bounty_bps": fees.get("keeper_bounty_bps"),
        "protocol_fee_recipient": fees.get("protocol_fee_recipient"),
    }


def _client_config() -> Tuple[PactaClientConfig, Dict[str, Any]]:
    manifest = _load_manifest()
    defaults = _manifest_defaults(manifest)
    config = PactaClientConfig(
        rpc_url=os.getenv("PACTA_RPC_URL", defaults["rpc_url"]),
        subgraph_url=os.getenv("PACTA_SUBGRAPH_URL", defaults["subgraph_url"]),
        core_address=os.getenv("PACTA_CORE_ADDRESS", defaults["core_address"]),
        private_key=os.getenv("PACTA_PRIVATE_KEY", ""),
        chain_id=int(manifest.get("chain_id", 8453)),
        start_block=int(os.getenv("PACTA_START_BLOCK", manifest.get("start_block", 0) or 0)),
    )
    return config, defaults


def get_client() -> Tuple[PactaClient, Dict[str, Any]]:
    config, defaults = _client_config()
    return PactaClient(config), defaults


def _deadline_bundle(params: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, int]:
    now = int(time.time())
    accept_deadline = int(
        params.get("accept_deadline")
        or now + int(params.get("accept_in_hours", defaults["accept_in_hours"])) * 3600
    )
    delivery_deadline = int(
        params.get("delivery_deadline")
        or accept_deadline + int(params.get("delivery_in_hours", defaults["delivery_in_hours"])) * 3600
    )
    review_deadline = int(
        params.get("review_deadline")
        or delivery_deadline + int(params.get("review_in_hours", defaults["review_in_hours"])) * 3600
    )
    return {
        "accept_deadline": accept_deadline,
        "delivery_deadline": delivery_deadline,
        "review_deadline": review_deadline,
    }


def _resolve_token(params: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
    tokens_by_symbol = defaults.get("tokens_by_symbol", {})
    token_symbol = str(params.get("token_symbol", "")).upper().strip()
    token_value = str(params.get("token", "")).strip()

    if token_symbol:
        token_config = tokens_by_symbol.get(token_symbol)
        if not token_config:
            raise RuntimeError(f"Unknown token_symbol: {token_symbol}")
        return token_config

    if token_value:
        if token_value.upper() in tokens_by_symbol:
            return tokens_by_symbol[token_value.upper()]
        return {"symbol": "", "address": token_value, "decimals": None}

    default_token = defaults.get("default_token", {})
    if default_token.get("address"):
        return default_token

    raise RuntimeError("Token not provided and no default token is configured")


def _resolve_amount(params: Dict[str, Any], token_config: Dict[str, Any]) -> int:
    amount = params.get("amount")
    amount_decimal = params.get("amount_decimal")

    if amount is not None:
        return int(str(amount))

    if amount_decimal is None:
        raise RuntimeError("Provide either amount (base units) or amount_decimal")

    decimals = token_config.get("decimals")
    if decimals is None:
        raise RuntimeError("amount_decimal requires a known token decimals value")

    try:
        scaled = Decimal(str(amount_decimal)) * (Decimal(10) ** int(decimals))
    except (InvalidOperation, ValueError) as exc:
        raise RuntimeError(f"Invalid amount_decimal: {amount_decimal}") from exc

    if scaled <= 0:
        raise RuntimeError("amount_decimal must be greater than zero")

    if scaled != scaled.to_integral_value():
        raise RuntimeError(f"amount_decimal has more precision than the token supports ({decimals} decimals)")

    return int(scaled)


def _format_amount_decimal(amount: int, token_config: Dict[str, Any]) -> str | None:
    decimals = token_config.get("decimals")
    if decimals is None:
        return None

    scaled = Decimal(amount) / (Decimal(10) ** int(decimals))
    return format(scaled.normalize(), "f")


def _parse_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y"}:
        return True
    if normalized in {"0", "false", "no", "n"}:
        return False
    raise RuntimeError(f"Invalid boolean value: {value}")


def _resolve_metadata_uri(params: Dict[str, Any]) -> str:
    metadata_uri = str(params.get("metadata_uri", "")).strip()
    if metadata_uri:
        return metadata_uri

    metadata_text = params.get("metadata_text")
    if metadata_text is None:
        raise RuntimeError("Provide metadata_uri or metadata_text")

    return f"data:text/plain;charset=utf-8,{quote(str(metadata_text), safe='')}"


def handle_approve_token(params: Dict[str, Any]) -> Dict[str, Any]:
    client, defaults = get_client()
    token_config = _resolve_token(params, defaults)
    amount = _resolve_amount(params, token_config)
    tx_hash = client.approve_token(token=token_config["address"], amount=amount)
    return {
        "status": "approved",
        "tx_hash": tx_hash,
        "token": token_config["address"],
        "token_symbol": token_config.get("symbol") or None,
        "amount": str(amount),
    }


def handle_post_agreement(params: Dict[str, Any]) -> Dict[str, Any]:
    client, defaults = get_client()
    deadlines = _deadline_bundle(params, defaults)
    token_config = _resolve_token(params, defaults)
    amount = _resolve_amount(params, token_config)
    metadata_uri = _resolve_metadata_uri(params)
    tx_hash = client.post_agreement(
        provider=params.get("provider"),
        token=token_config["address"],
        amount=amount,
        metadata_uri=metadata_uri,
        metadata_hash=params.get("metadata_hash"),
        accept_deadline=deadlines["accept_deadline"],
        delivery_deadline=deadlines["delivery_deadline"],
        review_deadline=deadlines["review_deadline"],
    )
    return {
        "status": "agreement_posted",
        "tx_hash": tx_hash,
        "token": token_config["address"],
        "token_symbol": token_config.get("symbol") or None,
        "amount": str(amount),
        "metadata_uri": metadata_uri,
        **deadlines,
    }


def handle_browse_agreements(params: Dict[str, Any]) -> Dict[str, Any]:
    client, defaults = get_client()
    token = params.get("token")
    if token or params.get("token_symbol"):
        token = _resolve_token(params, defaults)["address"]
    agreements = client.browse_agreements(
        status=params.get("status"),
        token=token,
        requester=params.get("requester"),
        provider=params.get("provider"),
        limit=int(params.get("limit", 20)),
    )
    return {"status": "ok", "count": len(agreements), "agreements": agreements}


def handle_get_agreement(params: Dict[str, Any]) -> Dict[str, Any]:
    client, _ = get_client()
    agreement = client.get_agreement_status(int(params["agreement_id"]))
    return {"status": "ok", "agreement": agreement}


def handle_accept_agreement(params: Dict[str, Any]) -> Dict[str, Any]:
    client, _ = get_client()
    tx_hash = client.accept_agreement(int(params["agreement_id"]))
    return {"status": "accepted", "tx_hash": tx_hash}


def handle_cancel_agreement(params: Dict[str, Any]) -> Dict[str, Any]:
    client, _ = get_client()
    tx_hash = client.cancel_agreement(int(params["agreement_id"]))
    return {"status": "cancelled", "tx_hash": tx_hash}


def handle_deliver_agreement(params: Dict[str, Any]) -> Dict[str, Any]:
    client, _ = get_client()
    tx_hash = client.deliver_agreement(
        int(params["agreement_id"]),
        params["delivery_uri"],
        params.get("delivery_hash"),
    )
    return {"status": "delivered", "tx_hash": tx_hash}


def handle_confirm_agreement(params: Dict[str, Any]) -> Dict[str, Any]:
    client, _ = get_client()
    tx_hash = client.confirm_agreement(int(params["agreement_id"]))
    return {"status": "confirmed", "tx_hash": tx_hash}


def handle_challenge_agreement(params: Dict[str, Any]) -> Dict[str, Any]:
    client, _ = get_client()
    tx_hash = client.challenge_agreement(int(params["agreement_id"]))
    return {"status": "challenged", "tx_hash": tx_hash}


def handle_finalize_agreement(params: Dict[str, Any]) -> Dict[str, Any]:
    client, _ = get_client()
    tx_hash = client.finalize_agreement(int(params["agreement_id"]))
    return {"status": "finalized", "tx_hash": tx_hash}


def handle_participant_profile(params: Dict[str, Any]) -> Dict[str, Any]:
    client, _ = get_client()
    profile = client.get_participant_profile(params.get("address"))
    return {"status": "ok", "participant": profile}


def handle_protocol_stats(params: Dict[str, Any]) -> Dict[str, Any]:
    client, _ = get_client()
    stats = client.get_protocol_stats()
    return {"status": "ok", "stats": stats}


def handle_get_core_config(params: Dict[str, Any]) -> Dict[str, Any]:
    client, defaults = get_client()
    if client.core is None:
        raise RuntimeError("No PactaCore configured. Set PACTA_CORE_ADDRESS or update pacta_enabled.json.")
    return {
        "status": "ok",
        "core_address": client.config.core_address,
        "start_block": client.config.start_block,
        "protocol_fee_recipient": client.core.functions.protocolFeeRecipient().call(),
        "protocol_fee_bps": client.core.functions.protocolFeeBps().call(),
        "keeper_bounty_bps": client.core.functions.keeperBountyBps().call(),
        "minimum_amount_for_protocol_fee": client.core.functions.minimumAmountForProtocolFee().call(),
        "minimum_amount_for_keeper_bounty": client.core.functions.minimumAmountForKeeperBounty().call(),
        "default_token_symbol": defaults.get("default_token_symbol"),
        "default_token": defaults.get("default_token"),
    }


def handle_quote_economics(params: Dict[str, Any]) -> Dict[str, Any]:
    client, defaults = get_client()
    token_config = _resolve_token(params, defaults)
    amount = _resolve_amount(params, token_config)
    scenario = str(params.get("scenario", "CONFIRMATION")).upper()
    third_party_executor = _parse_bool(params.get("third_party_executor"), True)

    quote_params: Dict[str, Any] = {
        "amount": amount,
        "scenario": scenario,
        "third_party_executor": third_party_executor,
    }

    quote = client.quote_economics(**quote_params)

    response: Dict[str, Any] = {
        "status": "ok",
        "token": token_config["address"],
        "token_symbol": token_config.get("symbol") or None,
        "decimals": token_config.get("decimals"),
        "quote": quote,
    }

    if token_config.get("decimals") is not None:
        response["quote_decimal"] = {
            "amount": _format_amount_decimal(int(quote["amount"]), token_config),
            "requesterAmount": _format_amount_decimal(int(quote["requesterAmount"]), token_config),
            "providerAmount": _format_amount_decimal(int(quote["providerAmount"]), token_config),
            "protocolFeeAmount": _format_amount_decimal(int(quote["protocolFeeAmount"]), token_config),
            "keeperAmount": _format_amount_decimal(int(quote["keeperAmount"]), token_config),
            "minimumAmountForProtocolFee": _format_amount_decimal(
                int(quote["minimumAmountForProtocolFee"]), token_config
            ),
            "minimumAmountForKeeperBounty": _format_amount_decimal(
                int(quote["minimumAmountForKeeperBounty"]), token_config
            ),
        }

    return response


COMMANDS = {
    "approve_token": handle_approve_token,
    "post_agreement": handle_post_agreement,
    "browse_agreements": handle_browse_agreements,
    "get_agreement": handle_get_agreement,
    "accept_agreement": handle_accept_agreement,
    "cancel_agreement": handle_cancel_agreement,
    "deliver_agreement": handle_deliver_agreement,
    "confirm_agreement": handle_confirm_agreement,
    "challenge_agreement": handle_challenge_agreement,
    "finalize_agreement": handle_finalize_agreement,
    "participant_profile": handle_participant_profile,
    "protocol_stats": handle_protocol_stats,
    "get_core_config": handle_get_core_config,
    "quote_economics": handle_quote_economics,
}


def handle(command: str, params: Dict[str, Any]) -> Dict[str, Any]:
    if command not in COMMANDS:
        return {"error": f"Unknown command: {command}", "available": sorted(COMMANDS.keys())}
    try:
        return COMMANDS[command](params)
    except Exception as exc:  # pragma: no cover
        return {"error": str(exc), "command": command}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python handler.py <command> '<json_params>'")
        print(f"Commands: {', '.join(sorted(COMMANDS.keys()))}")
        sys.exit(1)

    command = sys.argv[1]
    params = json.loads(sys.argv[2])
    print(json.dumps(handle(command, params), indent=2))
