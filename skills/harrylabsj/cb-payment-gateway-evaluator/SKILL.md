---
skill: cb-payment-gateway-evaluator
name: Cross-border Payment Gateway Evaluator
type: descriptive
version: 1.0.0
description: Payment method selection and gateway evaluation for international markets
author: Golden Bean (OpenClaw)
created: 2026-04-22
category: payments
language: en
tags: ["payment", "gateway", "international", "fraud", "compliance"]
outputs: json
requires_api: false
safety_boundary: Descriptive cross-border e-commerce planning only. No code execution, API calls, network requests, bookings, or real-time data. Does not provide professional advice. Verify information with official sources and qualified professionals.
---

# Cross-border Payment Gateway Evaluator

## Overview

Cross-border Payment Gateway Evaluator (Payment method selection and gateway evaluation for international markets). This skill provides a structured framework for evaluating and selecting payment gateways for cross-border e-commerce operations. It covers payment method preferences by market, gateway feature comparison, cost analysis, and fraud risk assessment.

The framework helps businesses choose the right payment infrastructure for their target markets, considering local payment preferences, regulatory requirements, and operational costs.

## Trigger Keywords

- "payment gateway evaluation"
- "cross-border payment methods"
- "international payment gateway"
- "multi-currency payment processing"
- "payment method localization"
- "global payment infrastructure"

## Workflow

1. **Input Analysis**: Parse user input to extract target markets, transaction volumes, and business requirements
2. **Payment Analysis**: Generate market-specific payment method analysis
3. **Gateway Evaluation**: Compare gateway features, costs, and capabilities
4. **Fraud Assessment**: Evaluate fraud risks and mitigation strategies
5. **Output Delivery**: Return comprehensive JSON with analysis and recommendations

## Output Modules

### Payment Method Analysis
- Local payment method preferences by market
- Credit card penetration and alternative payment adoption
- Digital wallet and mobile payment trends
- Buy-now-pay-later and installment options
- Bank transfer and direct debit availability

### Gateway Evaluation Framework
- Gateway feature comparison across providers
- Integration complexity and technical requirements
- Transaction fee structures and hidden costs
- Currency support and conversion fees
- Settlement timelines and payout options

### Fraud Risk Assessment
- Fraud rate benchmarks by market and industry
- Chargeback prevention and management
- 3D Secure and authentication requirements
- Address verification and CVV requirements
- Machine learning fraud detection options

### Compliance & Security
- PCI DSS compliance requirements
- Data localization and privacy regulations
- Anti-money laundering considerations
- Know-your-customer requirements
- Cross-border data transfer rules

## Safety & Limitations

### Safety Boundaries
- **No Professional Advice**: Provides informational frameworks only. Does not replace financial or legal professionals.
- **No Real-Time Data**: Based on general frameworks, not current gateway pricing or features.
- **No Transactions**: No payment processing or gateway integration capabilities.
- **No Code Execution**: Pure descriptive implementation. No shell commands or network requests.
- **Descriptive Only**: Provides planning frameworks and guidance only.

### Limitations
- Gateway features and pricing change frequently
- Payment method preferences vary significantly by market
- Regulatory requirements for payments are evolving
- Integration complexity varies by platform
- Fraud patterns change over time

## Example Prompts

### Level 1: Basic Inquiry
"What payment gateways work best for international e-commerce?"

### Level 2: Specific Scenario
"Payment gateway evaluation for European market expansion"

### Level 3: Complex Planning
"Multi-market payment strategy for US, EU, and Asia with subscription billing"

### Level 4: Detailed Case
"US e-commerce platform expanding to Germany, France, and Japan with k monthly transaction volume"

## Acceptance Criteria

### Functional Requirements
- Returns valid JSON structure from handle() function
- Includes input_analysis field with parsed input information
- Contains proper disclaimer with safety boundaries
- Provides payment-specific analysis and gateway evaluation
- Differentiated from other cross-border e-commerce skills

### Quality Requirements
- Clear and structured output
- Comprehensive framework coverage
- Actionable implementation guidance
- Proper safety boundaries enforced
- Input differentiation verified through tests

## Integration

### Complementary Skills
- Works with cb-multi-currency-pricing for pricing strategy integration
- Integrates with cb-compliance-framework for regulatory considerations
- Supports cb-market-entry-strategist for market-specific payment planning

### Input/Output Flow
- Accepts natural language input via handle() function
- Returns structured JSON for system integration
- Can be chained with related skills for multi-faceted analysis

## Version History

### v1.0.0 (2026-04-22)
- Initial release
- Payment method analysis by market
- Gateway evaluation framework
- Fraud risk assessment
- Compliance and security considerations
- Input parsing and parameter extraction
- JSON output with input_analysis and disclaimer
- Safety boundaries and limitations documentation
- Test coverage with 5 tests per skill

## Technical Details

### Handler Interface


### Dependencies
- None (pure Python standard library only)

### File Structure
- handler.py: Main handler implementation
- tests/test_handler.py: Unit tests (5 tests)
- SKILL.md: This documentation file
- skill.json: Skill metadata and configuration
- ACCEPTANCE.md: Acceptance criteria documentation
- .claw/identity.json: Identity and authorship information

### Test Coverage
- JSON output validation test
- Disclaimer presence and content test
- Input differentiation test
- Payments-specific functionality test
- Differentiation evidence test
