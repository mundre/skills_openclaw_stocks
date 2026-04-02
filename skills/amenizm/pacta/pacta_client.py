"""
Pacta Python SDK.

Pacta v1 is an immutable escrow and settlement protocol for agent-to-agent
agreements. Writes go directly to PactaCore on Base. Reads use the subgraph
when available, with full onchain fallback for survival-critical discovery.
"""

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import requests
from eth_utils import keccak
from web3 import Web3

from pacta_metadata import (
    build_task_metadata,
    build_delivery_payload,
    hash_content,
    hash_content_string,
    hash_payload,
    canonicalize,
    verify_task_metadata,
    verify_delivery_payload,
    verify_content,
    parse_task_metadata,
    parse_delivery_payload,
)


AGREEMENT_STATUSES = [
    "NONE",
    "OPEN",
    "ACTIVE",
    "DELIVERED",
    "SETTLED",
    "REFUNDED",
    "CANCELLED",
]


def _clean_config_value(value: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        return ""
    if "TODO" in cleaned.upper():
        return ""
    return cleaned


def _sanitize_graphql_string(value: str) -> str:
    import re
    return re.sub(r'[^\x20-\x7E]', '', str(value).replace('\\', '').replace('"', ''))


@dataclass
class PactaClientConfig:
    rpc_url: str = "https://mainnet.base.org"
    subgraph_url: str = ""
    core_address: str = ""
    private_key: str = ""
    chain_id: int = 8453
    start_block: int = 0


PACTA_CORE_FUNCTION_ABI = json.loads(
    '[{"inputs":[{"type":"address","name":"provider"},{"type":"address","name":"token"},{"type":"uint256","name":"amount"},{"type":"bytes32","name":"metadataHash"},{"type":"string","name":"metadataURI"},{"type":"uint64","name":"acceptDeadline"},{"type":"uint64","name":"deliveryDeadline"},{"type":"uint64","name":"reviewDeadline"}],"name":"createAgreement","outputs":[{"type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"type":"uint256","name":"agreementId"}],"name":"acceptAgreement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"type":"uint256","name":"agreementId"}],"name":"cancelAgreement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"type":"uint256","name":"agreementId"},{"type":"bytes32","name":"deliveryHash"},{"type":"string","name":"deliveryURI"}],"name":"deliverAgreement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"type":"uint256","name":"agreementId"}],"name":"confirmAgreement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"type":"uint256","name":"agreementId"}],"name":"challengeAgreement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"type":"uint256","name":"agreementId"}],"name":"finalizeAgreement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"nextAgreementId","outputs":[{"type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"type":"uint256","name":"agreementId"}],"name":"getAgreement","outputs":[{"components":[{"type":"address","name":"requester"},{"type":"address","name":"provider"},{"type":"address","name":"token"},{"type":"uint256","name":"amount"},{"type":"bytes32","name":"metadataHash"},{"type":"bytes32","name":"deliveryHash"},{"type":"uint64","name":"createdAt"},{"type":"uint64","name":"acceptDeadline"},{"type":"uint64","name":"deliveryDeadline"},{"type":"uint64","name":"reviewDeadline"},{"type":"uint8","name":"status"}],"type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"protocolFeeRecipient","outputs":[{"type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"protocolFeeBps","outputs":[{"type":"uint16"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"keeperBountyBps","outputs":[{"type":"uint16"}],"stateMutability":"view","type":"function"},{"inputs":[{"type":"uint256","name":"amount"}],"name":"quoteProtocolFee","outputs":[{"type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"type":"uint256","name":"amount"}],"name":"quoteKeeperBounty","outputs":[{"type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"type":"uint256","name":"amount"}],"name":"quoteConfirmation","outputs":[{"type":"uint256","name":"providerAmount"},{"type":"uint256","name":"protocolFeeAmount"}],"stateMutability":"view","type":"function"},{"inputs":[{"type":"uint256","name":"amount"},{"type":"bool","name":"thirdPartyExecutor"}],"name":"quoteOptimisticFinalize","outputs":[{"type":"uint256","name":"providerAmount"},{"type":"uint256","name":"protocolFeeAmount"},{"type":"uint256","name":"keeperAmount"}],"stateMutability":"view","type":"function"},{"inputs":[{"type":"uint256","name":"amount"},{"type":"bool","name":"thirdPartyExecutor"}],"name":"quoteRefund","outputs":[{"type":"uint256","name":"requesterAmount"},{"type":"uint256","name":"keeperAmount"}],"stateMutability":"view","type":"function"},{"inputs":[{"type":"uint256","name":"amount"}],"name":"quoteChallenge","outputs":[{"type":"uint256","name":"requesterAmount"},{"type":"uint256","name":"providerAmount"},{"type":"uint256","name":"protocolFeeAmount"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"minimumAmountForProtocolFee","outputs":[{"type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"minimumAmountForKeeperBounty","outputs":[{"type":"uint256"}],"stateMutability":"view","type":"function"}]'
)

PACTA_CORE_EVENT_ABI = json.loads(
    '[{"anonymous":false,"inputs":[{"indexed":true,"name":"agreementId","type":"uint256"},{"indexed":true,"name":"requester","type":"address"},{"indexed":true,"name":"providerHint","type":"address"},{"indexed":false,"name":"token","type":"address"},{"indexed":false,"name":"amount","type":"uint256"},{"indexed":false,"name":"metadataHash","type":"bytes32"},{"indexed":false,"name":"metadataURI","type":"string"},{"indexed":false,"name":"acceptDeadline","type":"uint64"},{"indexed":false,"name":"deliveryDeadline","type":"uint64"},{"indexed":false,"name":"reviewDeadline","type":"uint64"}],"name":"AgreementCreated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"agreementId","type":"uint256"},{"indexed":true,"name":"provider","type":"address"}],"name":"AgreementAccepted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"agreementId","type":"uint256"},{"indexed":false,"name":"requesterAmount","type":"uint256"}],"name":"AgreementCancelled","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"agreementId","type":"uint256"},{"indexed":false,"name":"deliveryHash","type":"bytes32"},{"indexed":false,"name":"deliveryURI","type":"string"}],"name":"AgreementDelivered","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"agreementId","type":"uint256"},{"indexed":true,"name":"challenger","type":"address"},{"indexed":false,"name":"requesterAmount","type":"uint256"},{"indexed":false,"name":"providerAmount","type":"uint256"},{"indexed":false,"name":"protocolFeeAmount","type":"uint256"}],"name":"AgreementChallenged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"agreementId","type":"uint256"},{"indexed":false,"name":"providerAmount","type":"uint256"},{"indexed":false,"name":"protocolFeeAmount","type":"uint256"},{"indexed":true,"name":"executor","type":"address"}],"name":"AgreementSettled","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"agreementId","type":"uint256"},{"indexed":false,"name":"requesterAmount","type":"uint256"},{"indexed":true,"name":"executor","type":"address"},{"indexed":false,"name":"reason","type":"string"}],"name":"AgreementRefunded","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"agreementId","type":"uint256"},{"indexed":true,"name":"token","type":"address"},{"indexed":false,"name":"amount","type":"uint256"}],"name":"ProtocolFeePaid","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"agreementId","type":"uint256"},{"indexed":true,"name":"keeper","type":"address"},{"indexed":true,"name":"token","type":"address"},{"indexed":false,"name":"amount","type":"uint256"},{"indexed":false,"name":"action","type":"string"}],"name":"KeeperPaid","type":"event"}]'
)

PACTA_CORE_ABI = PACTA_CORE_FUNCTION_ABI + PACTA_CORE_EVENT_ABI

ERC20_ABI = json.loads(
    '[{"inputs":[{"type":"address"},{"type":"uint256"}],"name":"approve","outputs":[{"type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"type":"address"},{"type":"address"}],"name":"allowance","outputs":[{"type":"uint256"}],"stateMutability":"view","type":"function"}]'
)


class PactaClient:
    def __init__(self, config: Optional[PactaClientConfig] = None):
        if config is None:
            config = PactaClientConfig(
                rpc_url=os.getenv("PACTA_RPC_URL", PactaClientConfig.rpc_url),
                subgraph_url=_clean_config_value(os.getenv("PACTA_SUBGRAPH_URL", "")),
                core_address=_clean_config_value(os.getenv("PACTA_CORE_ADDRESS", "")),
                private_key=os.getenv("PACTA_PRIVATE_KEY", ""),
                start_block=int(os.getenv("PACTA_START_BLOCK", "0")),
            )
        else:
            config.subgraph_url = _clean_config_value(config.subgraph_url)
            config.core_address = _clean_config_value(config.core_address)

        self.config = config
        self.w3 = Web3(Web3.HTTPProvider(config.rpc_url))
        self._session = requests.Session()

        if config.private_key:
            self.account = self.w3.eth.account.from_key(config.private_key)
        else:
            self.account = None

        self.core = None
        if config.core_address:
            self.core = self.w3.eth.contract(
                address=Web3.to_checksum_address(config.core_address),
                abi=PACTA_CORE_ABI,
            )

    @property
    def address(self) -> str:
        if self.account is None:
            raise RuntimeError("No wallet configured")
        return self.account.address

    def _require_account(self) -> None:
        if self.account is None:
            raise RuntimeError("No wallet configured")

    def _require_core(self) -> None:
        if self.core is None:
            raise RuntimeError("No PactaCore configured")

    def hash_pointer(self, pointer: str) -> str:
        return "0x" + keccak(text=pointer).hex()

    def approve_token(self, token: str, amount: int) -> str:
        self._require_account()
        self._require_core()
        erc20 = self.w3.eth.contract(address=Web3.to_checksum_address(token), abi=ERC20_ABI)
        tx = erc20.functions.approve(
            Web3.to_checksum_address(self.config.core_address), amount
        ).build_transaction({"from": self.account.address})
        return self._sign_and_send(tx)

    def get_allowance(self, token: str, owner: Optional[str] = None) -> int:
        self._require_core()
        erc20 = self.w3.eth.contract(address=Web3.to_checksum_address(token), abi=ERC20_ABI)
        return erc20.functions.allowance(
            Web3.to_checksum_address(owner or self.address),
            Web3.to_checksum_address(self.config.core_address),
        ).call()

    def post_agreement(
        self,
        token: str,
        amount: int,
        metadata_uri: str,
        accept_deadline: int,
        delivery_deadline: int,
        review_deadline: int,
        provider: Optional[str] = None,
        metadata_hash: Optional[str] = None,
    ) -> str:
        self._require_account()
        self._require_core()

        tx = self.core.functions.createAgreement(
            Web3.to_checksum_address(provider) if provider else "0x" + "0" * 40,
            Web3.to_checksum_address(token),
            amount,
            metadata_hash or self.hash_pointer(metadata_uri),
            metadata_uri,
            accept_deadline,
            delivery_deadline,
            review_deadline,
        ).build_transaction({"from": self.account.address})
        return self._sign_and_send(tx)

    def accept_agreement(self, agreement_id: int) -> str:
        self._require_account()
        self._require_core()
        tx = self.core.functions.acceptAgreement(agreement_id).build_transaction(
            {"from": self.account.address}
        )
        return self._sign_and_send(tx)

    def cancel_agreement(self, agreement_id: int) -> str:
        self._require_account()
        self._require_core()
        tx = self.core.functions.cancelAgreement(agreement_id).build_transaction(
            {"from": self.account.address}
        )
        return self._sign_and_send(tx)

    def deliver_agreement(
        self, agreement_id: int, delivery_uri: str, delivery_hash: Optional[str] = None
    ) -> str:
        self._require_account()
        self._require_core()
        tx = self.core.functions.deliverAgreement(
            agreement_id,
            delivery_hash or self.hash_pointer(delivery_uri),
            delivery_uri,
        ).build_transaction({"from": self.account.address})
        return self._sign_and_send(tx)

    def confirm_agreement(self, agreement_id: int) -> str:
        self._require_account()
        self._require_core()
        tx = self.core.functions.confirmAgreement(agreement_id).build_transaction(
            {"from": self.account.address}
        )
        return self._sign_and_send(tx)

    def challenge_agreement(self, agreement_id: int) -> str:
        self._require_account()
        self._require_core()
        tx = self.core.functions.challengeAgreement(agreement_id).build_transaction(
            {"from": self.account.address}
        )
        return self._sign_and_send(tx)

    def finalize_agreement(self, agreement_id: int) -> str:
        self._require_account()
        self._require_core()
        tx = self.core.functions.finalizeAgreement(
            agreement_id
        ).build_transaction({"from": self.account.address})
        return self._sign_and_send(tx)

    def sweep_stale(self, dry_run: bool = False) -> List[Dict[str, Any]]:
        """Discover and finalize stale agreements for keeper bounties.

        Any agent can call this opportunistically to earn keeper bounties while
        keeping the protocol healthy. Skips agreements where the signer is a
        principal (requester or provider) since principals don't earn bounties.

        Returns a list of result dicts for each processed agreement.
        """
        import time

        self._require_account()
        self._require_core()

        now = int(time.time())
        signer = self.account.address.lower()
        next_id = self.get_next_agreement_id()
        results: List[Dict[str, Any]] = []

        for agreement_id in range(next_id):
            try:
                agreement = self.get_agreement_onchain(agreement_id)
            except Exception:
                continue

            status = str(agreement.get("status", "")).upper()
            if status not in {"OPEN", "ACTIVE", "DELIVERED"}:
                continue

            requester = str(agreement.get("requester", "")).lower()
            provider_val = agreement.get("provider")
            provider = str(provider_val.get("id", "")).lower() if isinstance(provider_val, dict) else str(provider_val or "").lower()

            if signer in {requester, provider}:
                continue

            action = None
            if status == "OPEN" and now > int(agreement.get("acceptDeadline", 0) or 0):
                action = "accept_expired"
            elif status == "ACTIVE" and now > int(agreement.get("deliveryDeadline", 0) or 0):
                action = "delivery_expired"
            elif status == "DELIVERED" and now > int(agreement.get("reviewDeadline", 0) or 0):
                action = "review_expired"

            if action is None:
                continue

            if dry_run:
                results.append({
                    "agreementId": agreement_id,
                    "action": action,
                    "result": "dry_run",
                })
                continue

            try:
                tx_hash = self.finalize_agreement(agreement_id)
                results.append({
                    "agreementId": agreement_id,
                    "action": action,
                    "result": "finalized",
                    "txHash": tx_hash,
                })
            except Exception as exc:
                results.append({
                    "agreementId": agreement_id,
                    "action": action,
                    "result": "error",
                    "error": str(exc),
                })

        return results

    def post_agreement_with_metadata(
        self,
        token: str,
        amount: int,
        metadata_uri: str,
        accept_deadline: int,
        delivery_deadline: int,
        review_deadline: int,
        task_type: str,
        task_description: str,
        task_requirements: Optional[List[str]] = None,
        input_uri: Optional[str] = None,
        input_hash: Optional[str] = None,
        output_format: Optional[str] = None,
        delivery_method: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build task metadata, hash it, and post an agreement in one call.

        Returns a dict with tx_hash, metadata, metadata_hash, and metadata_json.
        The caller is responsible for uploading the JSON to metadata_uri.
        """
        metadata, metadata_hash, metadata_json = build_task_metadata(
            task_type=task_type,
            description=task_description,
            requirements=task_requirements,
            input_uri=input_uri,
            input_hash=input_hash,
            output_format=output_format,
            delivery_method=delivery_method,
        )

        tx_hash = self.post_agreement(
            token=token,
            amount=amount,
            metadata_uri=metadata_uri,
            accept_deadline=accept_deadline,
            delivery_deadline=delivery_deadline,
            review_deadline=review_deadline,
            provider=provider,
            metadata_hash=metadata_hash,
        )

        return {
            "tx_hash": tx_hash,
            "metadata": metadata,
            "metadata_hash": metadata_hash,
            "metadata_json": metadata_json,
        }

    def deliver_agreement_with_metadata(
        self,
        agreement_id: int,
        delivery_uri: str,
        delivery_type: str,
        summary: str,
        artifacts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Build a delivery payload, hash it, and deliver an agreement in one call.

        Returns a dict with tx_hash, payload, delivery_hash, and delivery_json.
        The caller is responsible for uploading the JSON to delivery_uri.
        """
        payload, delivery_hash, delivery_json = build_delivery_payload(
            delivery_type=delivery_type,
            summary=summary,
            artifacts=artifacts,
        )

        tx_hash = self.deliver_agreement(
            agreement_id=agreement_id,
            delivery_uri=delivery_uri,
            delivery_hash=delivery_hash,
        )

        return {
            "tx_hash": tx_hash,
            "payload": payload,
            "delivery_hash": delivery_hash,
            "delivery_json": delivery_json,
        }

    def fetch_and_verify_metadata(
        self, metadata_uri: str, expected_hash: str
    ) -> Dict[str, Any]:
        """Fetch task metadata from a URI, parse it, and verify against an on-chain hash."""
        resp = self._session.get(metadata_uri)
        resp.raise_for_status()
        json_string = resp.text
        valid = verify_task_metadata(json_string, expected_hash)
        metadata = parse_task_metadata(json_string) if valid else None
        return {"valid": valid, "metadata": metadata, "json": json_string}

    def fetch_and_verify_delivery(
        self, delivery_uri: str, expected_hash: str
    ) -> Dict[str, Any]:
        """Fetch delivery payload from a URI, parse it, and verify against an on-chain hash."""
        resp = self._session.get(delivery_uri)
        resp.raise_for_status()
        json_string = resp.text
        valid = verify_delivery_payload(json_string, expected_hash)
        payload = parse_delivery_payload(json_string) if valid else None
        return {"valid": valid, "payload": payload, "json": json_string}

    def get_agreement_onchain(self, agreement_id: int) -> Dict[str, Any]:
        self._require_core()
        result = self.core.functions.getAgreement(agreement_id).call()
        return {
            "id": str(agreement_id),
            "agreementId": str(agreement_id),
            "requester": result[0],
            "provider": result[1],
            "token": result[2],
            "amount": str(result[3]),
            "metadataHash": ("0x" + result[4].hex()) if hasattr(result[4], "hex") else result[4],
            "deliveryHash": ("0x" + result[5].hex()) if hasattr(result[5], "hex") else result[5],
            "createdAt": str(result[6]),
            "acceptDeadline": str(result[7]),
            "deliveryDeadline": str(result[8]),
            "reviewDeadline": str(result[9]),
            "status": AGREEMENT_STATUSES[result[10]],
        }

    def get_next_agreement_id(self) -> int:
        self._require_core()
        return self.core.functions.nextAgreementId().call()

    def get_core_config(self) -> Dict[str, Any]:
        self._require_core()
        return {
            "coreAddress": self.config.core_address,
            "startBlock": self.config.start_block,
            "protocolFeeRecipient": self.core.functions.protocolFeeRecipient().call(),
            "protocolFeeBps": self.core.functions.protocolFeeBps().call(),
            "keeperBountyBps": self.core.functions.keeperBountyBps().call(),
            "minimumAmountForProtocolFee": self.core.functions.minimumAmountForProtocolFee().call(),
            "minimumAmountForKeeperBounty": self.core.functions.minimumAmountForKeeperBounty().call(),
        }

    def quote_economics(
        self,
        amount: int,
        scenario: str = "CONFIRMATION",
        third_party_executor: bool = True,
    ) -> Dict[str, Any]:
        self._require_core()
        scenario = scenario.upper()
        minimum_protocol_amount = self.core.functions.minimumAmountForProtocolFee().call()
        minimum_keeper_amount = self.core.functions.minimumAmountForKeeperBounty().call()

        if scenario == "CONFIRMATION":
            provider_net, protocol_fee = self.core.functions.quoteConfirmation(amount).call()
            return {
                "scenario": scenario,
                "amount": amount,
                "requesterAmount": 0,
                "providerAmount": provider_net,
                "protocolFeeAmount": protocol_fee,
                "keeperAmount": 0,
                "thirdPartyExecutor": False,
                "minimumAmountForProtocolFee": minimum_protocol_amount,
                "minimumAmountForKeeperBounty": minimum_keeper_amount,
            }

        if scenario == "OPTIMISTIC_FINALIZE":
            provider_net, protocol_fee, keeper_amount = (
                self.core.functions.quoteOptimisticFinalize(amount, third_party_executor).call()
            )
            return {
                "scenario": scenario,
                "amount": amount,
                "requesterAmount": 0,
                "providerAmount": provider_net,
                "protocolFeeAmount": protocol_fee,
                "keeperAmount": keeper_amount,
                "thirdPartyExecutor": third_party_executor,
                "minimumAmountForProtocolFee": minimum_protocol_amount,
                "minimumAmountForKeeperBounty": minimum_keeper_amount,
            }

        if scenario == "REFUND":
            requester_net, keeper_amount = self.core.functions.quoteRefund(
                amount, third_party_executor
            ).call()
            return {
                "scenario": scenario,
                "amount": amount,
                "requesterAmount": requester_net,
                "providerAmount": 0,
                "protocolFeeAmount": 0,
                "keeperAmount": keeper_amount,
                "thirdPartyExecutor": third_party_executor,
                "minimumAmountForProtocolFee": minimum_protocol_amount,
                "minimumAmountForKeeperBounty": minimum_keeper_amount,
            }

        if scenario == "CHALLENGE":
            requester_net, provider_net, protocol_fee = self.core.functions.quoteChallenge(
                amount
            ).call()
            return {
                "scenario": scenario,
                "amount": amount,
                "requesterAmount": requester_net,
                "providerAmount": provider_net,
                "protocolFeeAmount": protocol_fee,
                "keeperAmount": 0,
                "thirdPartyExecutor": False,
                "minimumAmountForProtocolFee": minimum_protocol_amount,
                "minimumAmountForKeeperBounty": minimum_keeper_amount,
            }

        raise ValueError(f"Unknown quote scenario: {scenario}")

    def get_participant_profile(self, address: Optional[str] = None) -> Dict[str, Any]:
        participant = (address or self.address).lower()
        try:
            data = self._graph_query(
                f"""{{
                  participant(id: "{_sanitize_graphql_string(participant)}") {{
                    id requestedCount providedCount settledCount challengedCount refundedCount cancelledCount totalVolumeAsProvider totalVolumeAsRequester lastSeenAt
                  }}
                }}"""
            )
            if data.get("participant"):
                return data["participant"]
        except Exception:
            pass
        agreements = self._browse_agreements_onchain(limit=None)
        challenged_ids = set()
        for event in self._event_logs("AgreementChallenged"):
            challenged_ids.add(int(event["args"]["agreementId"]))
        requested_count = 0
        provided_count = 0
        settled_count = 0
        challenged_count = 0
        refunded_count = 0
        cancelled_count = 0
        last_seen_at = 0

        for agreement in agreements:
            agreement_requester = self._participant_id(agreement.get("requester"))
            agreement_provider = self._participant_id(agreement.get("provider"))
            updated_at = int(str(agreement.get("updatedAt") or agreement.get("createdAt") or "0"))
            agreement_id = int(str(agreement.get("agreementId") or agreement.get("id") or "0"))
            was_challenged = agreement_id in challenged_ids

            if agreement_requester == participant:
                requested_count += 1
                last_seen_at = max(last_seen_at, updated_at)
                if agreement.get("status") == "SETTLED":
                    settled_count += 1
                if agreement.get("status") == "CANCELLED":
                    cancelled_count += 1
                if agreement.get("status") == "REFUNDED":
                    refunded_count += 1
                if was_challenged:
                    challenged_count += 1

            if agreement_provider == participant:
                provided_count += 1
                last_seen_at = max(last_seen_at, updated_at)
                if agreement.get("status") == "SETTLED":
                    settled_count += 1
                if agreement.get("status") == "REFUNDED":
                    refunded_count += 1
                if agreement.get("status") == "CANCELLED":
                    cancelled_count += 1
                if was_challenged:
                    challenged_count += 1

        return {
            "id": participant,
            "requestedCount": str(requested_count),
            "providedCount": str(provided_count),
            "settledCount": str(settled_count),
            "challengedCount": str(challenged_count),
            "refundedCount": str(refunded_count),
            "cancelledCount": str(cancelled_count),
            "lastSeenAt": str(last_seen_at),
        }

    def discover_providers(
        self,
        min_trust_score: float = 0.5,
        min_settled_count: int = 0,
        min_volume: int = 0,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Discover and rank providers by trust score and volume."""
        if self.config.subgraph_url:
            try:
                query = """{
                  participants(first: 100, orderBy: settledCount, orderDirection: desc, where: { providedCount_gt: "0" }) {
                    id requestedCount providedCount settledCount challengedCount refundedCount cancelledCount totalVolumeAsProvider totalVolumeAsRequester lastSeenAt
                  }
                }"""
                resp = self._graph_query(query)
                participants = resp.get("participants", [])
                ranked = []
                for p in participants:
                    settled = int(p.get("settledCount", 0))
                    challenged = int(p.get("challengedCount", 0))
                    refunded = int(p.get("refundedCount", 0))
                    total = settled + challenged + refunded
                    trust = settled / total if total > 0 else 0.0
                    p["trustScore"] = round(trust, 3)
                    p["totalOutcomes"] = total
                    p["settledCount"] = str(settled)
                    if trust >= min_trust_score and settled >= min_settled_count and int(p.get("totalVolumeAsProvider", 0)) >= min_volume:
                        ranked.append(p)
                ranked.sort(key=lambda x: (-x["trustScore"], -int(x["settledCount"])))
                return ranked[:limit]
            except Exception:
                pass

        # Onchain fallback
        agreements = self.browse_agreements(limit=1000)
        challenged_ids = set()
        for event in self._event_logs("AgreementChallenged"):
            challenged_ids.add(int(event["args"]["agreementId"]))
        provider_map: Dict[str, Dict[str, Any]] = {}
        for agreement in agreements:
            pid = self._participant_id(agreement.get("provider"))
            if not pid:
                continue
            if pid not in provider_map:
                provider_map[pid] = {"id": pid, "providedCount": 0, "settledCount": 0, "challengedCount": 0, "refundedCount": 0, "totalVolumeAsProvider": 0, "lastSeenAt": "0"}
            p = provider_map[pid]
            p["providedCount"] += 1
            updated_at = int(str(agreement.get("updatedAt") or agreement.get("createdAt") or "0"))
            if updated_at > int(p["lastSeenAt"]):
                p["lastSeenAt"] = str(updated_at)
            agreement_id = int(str(agreement.get("agreementId") or agreement.get("id") or "0"))
            status = agreement.get("status")
            if status == "SETTLED":
                p["settledCount"] += 1
                p["totalVolumeAsProvider"] += int(agreement.get("providerAmount") or 0)
            elif status == "REFUNDED":
                p["refundedCount"] += 1
            if agreement_id in challenged_ids:
                p["challengedCount"] += 1

        ranked = []
        for p in provider_map.values():
            total = p["settledCount"] + p["challengedCount"] + p["refundedCount"]
            trust = p["settledCount"] / total if total > 0 else 0.0
            p["trustScore"] = round(trust, 3)
            p["totalOutcomes"] = total
            p["totalVolumeAsProvider"] = str(p["totalVolumeAsProvider"])
            if trust >= min_trust_score and p["settledCount"] >= min_settled_count and int(p["totalVolumeAsProvider"]) >= min_volume:
                ranked.append(p)
        ranked.sort(key=lambda x: (-x["trustScore"], -x["settledCount"]))
        return ranked[:limit]

    def browse_agreements(
        self,
        status: Optional[str] = None,
        token: Optional[str] = None,
        requester: Optional[str] = None,
        provider: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        where_parts = []
        if status:
            where_parts.append(f'status: "{_sanitize_graphql_string(status)}"')
        if token:
            where_parts.append(f'token: "{_sanitize_graphql_string(token.lower())}"')
        if requester:
            where_parts.append(f'requester: "{_sanitize_graphql_string(requester.lower())}"')
        if provider:
            where_parts.append(f'provider: "{_sanitize_graphql_string(provider.lower())}"')
        where = f"where: {{{', '.join(where_parts)}}}" if where_parts else ""
        sanitized_limit = max(1, min(1000, int(limit)))
        try:
            data = self._graph_query(
                f"""{{
                  agreements(first: {sanitized_limit}, orderBy: createdAt, orderDirection: desc, {where}) {{
                    id agreementId token amount metadataHash metadataUri deliveryHash deliveryUri
                    acceptDeadline deliveryDeadline reviewDeadline status
                    requesterAmount providerAmount protocolFeeAmount createdAt updatedAt
                    requester {{ id }}
                    provider {{ id }}
                  }}
                }}"""
            )
            return data["agreements"]
        except Exception:
            return self._browse_agreements_onchain(
                status=status,
                token=token,
                requester=requester,
                provider=provider,
                limit=limit,
            )

    def _browse_agreements_onchain(
        self,
        status: Optional[str] = None,
        token: Optional[str] = None,
        requester: Optional[str] = None,
        provider: Optional[str] = None,
        limit: Optional[int] = 20,
    ) -> List[Dict[str, Any]]:
        self._require_core()
        created_events = self._event_logs("AgreementCreated")
        created_events = list(reversed(created_events))
        delivery_events = self._event_logs("AgreementDelivered")
        settled_events = self._event_logs("AgreementSettled")
        refunded_events = self._event_logs("AgreementRefunded")

        delivery_map: Dict[int, Dict[str, Any]] = {}
        for event in delivery_events:
            args = event["args"]
            delivery_map[int(args["agreementId"])] = {
                "deliveryHash": ("0x" + args["deliveryHash"].hex())
                if hasattr(args["deliveryHash"], "hex")
                else args["deliveryHash"],
                "deliveryUri": args["deliveryURI"],
            }

        settled_map: Dict[int, Dict[str, Any]] = {}
        for event in settled_events:
            args = event["args"]
            settled_map[int(args["agreementId"])] = {
                "providerAmount": str(args["providerAmount"]),
                "protocolFeeAmount": str(args["protocolFeeAmount"]),
                "executor": str(args["executor"]),
            }

        refunded_map: Dict[int, Dict[str, Any]] = {}
        for event in refunded_events:
            args = event["args"]
            refunded_map[int(args["agreementId"])] = {
                "requesterAmount": str(args["requesterAmount"]),
                "terminalReason": args["reason"],
            }

        results: List[Dict[str, Any]] = []
        for event in created_events:
            args = event["args"]
            agreement_id = int(args["agreementId"])
            agreement = self.get_agreement_onchain(agreement_id)
            agreement["requester"] = str(agreement["requester"]).lower()
            agreement["provider"] = self._normalize_optional_address(agreement.get("provider"))
            agreement["token"] = str(agreement["token"]).lower()
            agreement["metadataUri"] = args["metadataURI"]
            agreement["updatedAt"] = agreement["createdAt"]
            agreement["requester"] = {"id": agreement["requester"]}
            agreement["provider"] = (
                {"id": agreement["provider"]} if agreement["provider"] else None
            )

            if agreement_id in delivery_map:
                agreement.update(delivery_map[agreement_id])
            if agreement_id in settled_map:
                agreement.update(settled_map[agreement_id])
            if agreement_id in refunded_map:
                agreement.update(refunded_map[agreement_id])

            if not self._matches_agreement_filters(
                agreement,
                status=status,
                token=token,
                requester=requester,
                provider=provider,
            ):
                continue

            results.append(agreement)
            if limit is not None and len(results) >= limit:
                break

        return results

    def get_agreement_status(self, agreement_id: int) -> Dict[str, Any]:
        try:
            data = self._graph_query(
                f"""{{
                  agreement(id: "{_sanitize_graphql_string(agreement_id)}") {{
                    id agreementId token amount metadataHash metadataUri deliveryHash deliveryUri
                    acceptDeadline deliveryDeadline reviewDeadline status
                    requesterAmount providerAmount protocolFeeAmount createdAt updatedAt
                    requester {{ id }}
                    provider {{ id }}
                  }}
                }}"""
            )
            if data.get("agreement"):
                return data["agreement"]
        except Exception:
            pass
        return self.get_agreement_onchain(agreement_id)

    def get_protocol_stats(self) -> Dict[str, Any]:
        try:
            data = self._graph_query(
                """{
                  protocolStat(id: "global") {
                    totalAgreements
                    totalEscrowedVolume
                    totalVolume
                    totalRefundedVolume
                    totalProtocolFees
                    totalKeeperPayouts
                    openAgreements
                    activeAgreements
                    deliveredAgreements
                    challengedAgreements
                    settledAgreements
                    refundedAgreements
                    cancelledAgreements
                  }
                }"""
            )
            return data["protocolStat"]
        except Exception:
            pass

        agreements = self._browse_agreements_onchain(limit=None)
        stats = {
            "totalAgreements": 0,
            "totalEscrowedVolume": 0,
            "totalVolume": 0,
            "totalRefundedVolume": 0,
            "totalProtocolFees": 0,
            "totalKeeperPayouts": 0,
            "openAgreements": 0,
            "activeAgreements": 0,
            "deliveredAgreements": 0,
            "challengedAgreements": 0,
            "settledAgreements": 0,
            "refundedAgreements": 0,
            "cancelledAgreements": 0,
        }

        for agreement in agreements:
            amount = int(agreement.get("amount", "0"))
            status = str(agreement.get("status", "")).upper()
            stats["totalAgreements"] += 1
            stats["totalEscrowedVolume"] += amount
            if status == "SETTLED":
                stats["totalVolume"] += amount
            if status == "REFUNDED":
                stats["totalRefundedVolume"] += int(agreement.get("requesterAmount", "0"))
            status_key = f"{status.lower()}Agreements"
            if status_key in stats:
                stats[status_key] += 1

        for event in self._event_logs("ProtocolFeePaid"):
            stats["totalProtocolFees"] += int(event["args"]["amount"])
        for event in self._event_logs("KeeperPaid"):
            stats["totalKeeperPayouts"] += int(event["args"]["amount"])

        return {key: str(value) for key, value in stats.items()}

    def discover_pacta(self, base_url: str) -> Dict[str, Any]:
        url = base_url.rstrip("/") + "/pacta_enabled.json"
        resp = self._session.get(url)
        resp.raise_for_status()
        return resp.json()

    def _sign_and_send(self, tx: Dict[str, Any]) -> str:
        # Chain ID safety check: verify the RPC is actually Base mainnet
        rpc_chain_id = self.w3.eth.chain_id
        if rpc_chain_id != self.config.chain_id:
            raise RuntimeError(
                f"Chain ID mismatch: RPC reports {rpc_chain_id}, expected {self.config.chain_id}. "
                f"Refusing to sign. This may indicate a malicious or misconfigured RPC endpoint."
            )

        tx["nonce"] = self.w3.eth.get_transaction_count(self.account.address)
        tx["chainId"] = self.config.chain_id
        if "gas" not in tx:
            tx["gas"] = self.w3.eth.estimate_gas(tx)
        if "gasPrice" not in tx:
            tx["maxFeePerGas"] = self.w3.eth.gas_price * 2
            tx["maxPriorityFeePerGas"] = self.w3.to_wei("0.001", "gwei")

        signed = self.w3.eth.account.sign_transaction(tx, self.config.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        return tx_hash.hex()

    def _graph_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.config.subgraph_url:
            raise RuntimeError("No subgraph URL configured. Set PACTA_SUBGRAPH_URL.")
        resp = self._session.post(
            self.config.subgraph_url,
            json={"query": query, "variables": variables or {}},
        )
        resp.raise_for_status()
        data = resp.json()
        if "errors" in data:
            raise RuntimeError(f"Subgraph error: {data['errors'][0]['message']}")
        return data["data"]

    def _event_logs(self, event_name: str) -> List[Dict[str, Any]]:
        self._require_core()
        event = getattr(self.core.events, event_name)
        start = self.config.start_block
        latest = self.w3.eth.block_number
        block_range = 50_000

        if latest - start <= block_range:
            return event.get_logs(from_block=start, to_block="latest")

        all_logs: List[Dict[str, Any]] = []
        current = start
        while current <= latest:
            end = min(current + block_range - 1, latest)
            chunk = event.get_logs(from_block=current, to_block=end)
            all_logs.extend(chunk)
            current = end + 1
        return all_logs

    def _participant_id(self, participant: Any) -> str:
        if isinstance(participant, dict):
            return str(participant.get("id", "")).lower()
        return self._normalize_optional_address(participant)

    def _normalize_optional_address(self, value: Any) -> str:
        normalized = str(value or "").lower()
        if normalized in {"", "0x0000000000000000000000000000000000000000"}:
            return ""
        return normalized

    def _matches_agreement_filters(
        self,
        agreement: Dict[str, Any],
        status: Optional[str] = None,
        token: Optional[str] = None,
        requester: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> bool:
        if status and str(agreement.get("status", "")).upper() != status.upper():
            return False
        if token and self._normalize_optional_address(agreement.get("token")) != token.lower():
            return False
        if requester and self._participant_id(agreement.get("requester")) != requester.lower():
            return False
        if provider and self._participant_id(agreement.get("provider")) != provider.lower():
            return False
        return True
