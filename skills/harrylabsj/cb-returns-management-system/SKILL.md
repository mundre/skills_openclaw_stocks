---
skill: cb-returns-management-system
name: International Returns Management System
type: descriptive
version: 1.0.0
description: Cost-effective international returns and reverse logistics
author: Golden Bean (OpenClaw)
created: 2026-04-22
category: returns
language: en
tags: ["returns", "logistics", "reverse", "international", "customer-service"]
outputs: json
requires_api: false
safety_boundary: Descriptive cross-border e-commerce planning only. No code execution, API calls, network requests, bookings, or real-time data. Does not provide professional advice. Verify information with official sources and qualified professionals.
---

# International Returns Management System

## Overview

International Returns Management System (Cost-effective international returns and reverse logistics). This skill provides a structured framework for planning and managing cross-border returns processes. It covers reverse logistics optimization, cost analysis, customer experience management, and regulatory compliance for international returns.

The framework helps businesses balance customer satisfaction with operational efficiency in international returns management, considering regional differences in consumer protection laws and logistics infrastructure.

## Trigger Keywords

- "international returns management"
- "cross-border reverse logistics"
- "returns cost optimization"
- "global returns policy"
- "international customer returns"
- "reverse logistics framework"

## Workflow

1. **Input Analysis**: Parse user input to extract target markets, product types, and business parameters
2. **Returns Framework**: Generate returns management framework with cost analysis
3. **Logistics Planning**: Develop reverse logistics strategy for target markets
4. **Customer Experience**: Design customer-friendly returns process
5. **Output Delivery**: Return comprehensive JSON with analysis and recommendations

## Output Modules

### Returns Cost Analysis
- Return rate estimation by market and product category
- Shipping and handling cost breakdown
- Restocking and refurbishment cost analysis
- Disposal and liquidation cost considerations
- Cost optimization strategies

### Reverse Logistics Framework
- Return shipping carrier selection and routing
- Customs and duty considerations for returns
- Warehouse and inspection hub placement
- Inventory management for returned goods
- Return consolidation strategies

### Customer Experience Optimization
- Return policy design for international markets
- Customer communication and tracking
- Refund processing and timeline management
- Exchange and store credit alternatives
- Customer satisfaction measurement

### Regulatory Compliance
- Consumer protection laws by market
- Return window requirements by jurisdiction
- Labeling and documentation requirements
- Environmental regulations for returns processing
- Data privacy considerations

## Safety & Limitations

### Safety Boundaries
- **No Professional Advice**: Provides informational frameworks only. Does not replace logistics or legal professionals.
- **No Real-Time Data**: Based on general frameworks, not current carrier rates or regulations.
- **No Transactions**: No booking, shipping label generation, or refund processing.
- **No Code Execution**: Pure descriptive implementation. No shell commands or network requests.
- **Descriptive Only**: Provides planning frameworks and guidance only.

### Limitations
- Shipping costs and carrier options vary by region and change frequently
- Customs regulations for returns differ significantly by country
- Product-specific factors may alter return handling requirements
- Consumer protection laws are subject to change
- Infrastructure quality varies by market

## Example Prompts

### Level 1: Basic Inquiry
"How to manage international returns for my e-commerce business?"

### Level 2: Specific Scenario
"Returns management for fashion products in EU markets"

### Level 3: Complex Planning
"Multi-market returns optimization for electronics in US, EU, and Asia"

### Level 4: Detailed Case
"US-based fashion retailer managing returns from France, Germany, and UK with <10% return rate target"

## Acceptance Criteria

### Functional Requirements
- Returns valid JSON structure from handle() function
- Includes input_analysis field with parsed input information
- Contains proper disclaimer with safety boundaries
- Provides returns-specific cost analysis and logistics framework
- Differentiated from other cross-border e-commerce skills

### Quality Requirements
- Clear and structured output
- Comprehensive framework coverage
- Actionable implementation guidance
- Proper safety boundaries enforced
- Input differentiation verified through tests

## Integration

### Complementary Skills
- Works with cb-shipping-optimizer for outbound logistics integration
- Integrates with cb-customer-service-localizer for returns communication
- Supports cb-compliance-framework for regulatory considerations

### Input/Output Flow
- Accepts natural language input via handle() function
- Returns structured JSON for system integration
- Can be chained with related skills for multi-faceted analysis

## Version History

### v1.0.0 (2026-04-22)
- Initial release
- Returns cost analysis framework
- Reverse logistics planning
- Customer experience optimization
- Regulatory compliance considerations
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
- Returns-specific functionality test
- Differentiation evidence test
