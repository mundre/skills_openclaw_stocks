#!/usr/bin/env python3
"""
Example: Query price and build a USDT → ETH swap transaction

Usage:
    python3 examples/swap_usdt_eth.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from zeroex_client import create_client


def main():
    # Create client from config
    client = create_client()

    # Query price
    print("💱 Querying price for 1000 USDT → ETH...\n")
    price = client.get_price("USDT", "ETH", 1000)

    print(f"   From: {price['from_amount']:,.2f} {price['from_token']}")
    print(f"   To:   {price['to_amount']:,.6f} {price['to_token']}")
    print(
        f"   Price: 1 {price['from_token']} = {price['price']:,.6f} {price['to_token']}"
    )
    print(f"   Min Buy: {price['min_buy_amount']:,.6f} {price['to_token']}")
    print(f"   Gas: ~{price['gas']:,}\n")

    # Get full quote with transaction data
    print("🛣️  Getting optimal route...\n")
    quote = client.get_quote(
        "USDT",
        "ETH",
        1000,
        taker="0x0000000000000000000000000000000000000001",  # Replace with your wallet
    )

    print(
        f"   Price: 1 {quote['from_token']} = {quote['price']:,.6f} {quote['to_token']}"
    )
    print(f"   Min Buy: {quote['min_buy_amount']:,.6f} {quote['to_token']}")
    print(f"   Route Sources:")
    for fill in quote.get("route", {}).get("fills", []):
        bps = int(fill.get("proportionBps", 0))
        if bps > 0:
            print(f"     • {fill.get('source', 'Unknown')}: {bps / 100:.1f}%")
    print()

    # Transaction data
    tx = quote["tx"]
    print("📦 Transaction Data (for review):")
    print(f"   To: {tx['to']}")
    print(f"   Data: {tx['data'][:64]}...")
    print(f"   Gas: {tx['gas']:,}")
    print()
    print("   ⚠️  Review above and sign with your wallet!")
    print()


if __name__ == "__main__":
    main()
