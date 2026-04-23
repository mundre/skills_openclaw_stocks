# ═══════════════════════════════════════════════════
# SkillPay Billing Integration
# Pay-per-call: $0.01 USDT per analysis run
# ═══════════════════════════════════════════════════
import os
import requests

BILLING_API_URL = "https://skillpay.me"
BILLING_API_KEY = os.environ.get("SKILL_BILLING_API_KEY", "")
SKILL_ID = os.environ.get("SKILL_BILLING_SKILL_ID", "tax-invoice-validator")
HEADERS = {"X-API-Key": BILLING_API_KEY, "Content-Type": "application/json"}


def check_balance(user_id: str) -> float:
    """Check user's USDT balance."""
    if not BILLING_API_KEY:
        return float("inf")  # Dev mode: no billing
    resp = requests.get(
        f"{BILLING_API_URL}/api/v1/billing/balance",
        params={"user_id": user_id},
        headers=HEADERS,
        timeout=10,
    )
    return resp.json().get("balance", 0.0)


def charge_user(user_id: str, amount: float = 0.01) -> dict:
    """Charge user per call. Returns dict with ok status and balance."""
    if not BILLING_API_KEY:
        return {"ok": True, "balance": 999.0}  # Dev mode
    resp = requests.post(
        f"{BILLING_API_URL}/api/v1/billing/charge",
        headers=HEADERS,
        json={"user_id": user_id, "skill_id": SKILL_ID, "amount": amount},
        timeout=10,
    )
    data = resp.json()
    if data.get("success"):
        return {"ok": True, "balance": data.get("balance", 0.0)}
    return {
        "ok": False,
        "balance": data.get("balance", 0.0),
        "payment_url": data.get("payment_url"),
    }


def get_payment_link(user_id: str, amount: float = 10.0) -> str:
    """Generate payment link for user to top up."""
    if not BILLING_API_KEY:
        return ""
    resp = requests.post(
        f"{BILLING_API_URL}/api/v1/billing/payment-link",
        headers=HEADERS,
        json={"user_id": user_id, "amount": amount},
        timeout=10,
    )
    return resp.json().get("payment_url", "")
