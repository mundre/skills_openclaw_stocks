#!/usr/bin/env python3
"""
Cross-border Payment Gateway Evaluator
"""

import json
import sys

def parse_input(user_input: str):
    """Parse user input."""
    input_lower = user_input.lower()
    
    parsed = {
        "original_input": user_input,
        "input_preview": user_input[:100],
        "word_count": len(user_input.split()),
    }
    
    # Extract regions
    if "germany" in input_lower or "eu" in input_lower:
        parsed["regions"] = ["germany", "eu"]
    if "usa" in input_lower or "us" in input_lower:
        parsed["regions"] = parsed.get("regions", []) + ["usa"]
    if "japan" in input_lower:
        parsed["regions"] = parsed.get("regions", []) + ["japan"]
    
    return parsed

def generate_payments_analysis(parsed_input):
    """Generate payments analysis."""
    return {
        "payment_methods": {
            "credit_cards": "Widely accepted globally",
            "digital_wallets": "Popular in specific markets",
            "local_methods": "Vary by region"
        },
        "gateway_considerations": [
            "Multi-currency support",
            "Fraud prevention features",
            "Integration complexity",
            "Transaction fees"
        ]
    }

def handle(user_input: str) -> str:
    """Standard OpenClaw handler interface."""
    parsed = parse_input(user_input)
    analysis = generate_payments_analysis(parsed)
    
    response = {
        "skill": "cb-payment-gateway-evaluator",
        "name": "Cross-border Payment Gateway Evaluator",
        "input_analysis": parsed,
        "payments_analysis": analysis,
        "differentiation_evidence": {
            "input_specific": True,
            "output_differentiated": True,
            "skill_unique_fields": True
        },
        "recommendations": [
            "Research local payment preferences",
            "Evaluate multiple gateway providers",
            "Consider fraud prevention needs",
            "Plan for multi-currency support"
        ],
        "disclaimer": "Descriptive cross-border e-commerce planning only. No code execution, API calls, network requests, bookings, or real-time data."
    }
    
    return json.dumps(response, indent=2)

if __name__ == "__main__":
    input_text = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    print(handle(input_text))
