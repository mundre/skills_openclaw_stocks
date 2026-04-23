---
skill: cb-cultural-marketing-framework
name: Cultural Marketing Adaptation Framework
type: descriptive
version: 1.0.0
description: Marketing message and campaign adaptation for cultural contexts
author: Golden Bean (OpenClaw)
created: 2026-04-22
category: marketing
language: en
tags: ["marketing", "localization", "culture", "adaptation", "international"]
outputs: json
requires_api: false
safety_boundary: Descriptive cross-border e-commerce planning only. No code execution, API calls, network requests, bookings, or real-time data. Does not provide professional advice. Verify information with official sources and qualified professionals.
---

# Cultural Marketing Adaptation Framework

## Overview

Cultural Marketing Adaptation Framework (Marketing message and campaign adaptation for cultural contexts). This skill provides a structured approach to adapting marketing strategies for international audiences. It analyzes cultural differences in communication styles, visual preferences, and value systems to generate culturally appropriate marketing recommendations.

The framework covers cultural analysis, message adaptation, channel-specific strategies, and implementation planning. It helps businesses avoid cultural missteps and create resonant marketing campaigns across different markets.

## Trigger Keywords

- "cultural marketing adaptation"
- "cross-cultural marketing framework"
- "localize marketing for culture"
- "cultural advertising adaptation"
- "international marketing localization"
- "culture-specific campaign planning"

## Workflow

1. **Input Analysis**: Parse user input to extract target culture, brand positioning, product category, and marketing channels
2. **Cultural Analysis**: Apply culture-specific communication and value system frameworks
3. **Message Adaptation**: Generate adapted messaging with cultural rationale
4. **Channel Strategy**: Develop channel-specific adaptation recommendations
5. **Output Delivery**: Return comprehensive JSON with analysis and recommendations

## Output Modules

### Cultural Analysis Framework
- Communication style analysis for target culture
- Visual preference assessment and design recommendations
- Value system alignment and key cultural principles
- Cultural taboos and sensitivities to avoid
- Brand positioning adjustments for cultural fit

### Message Adaptation Framework
- Original to adapted message transformations with rationale
- Slogan and tagline cultural adaptation
- Tone and voice adjustment recommendations
- Visual and imagery adaptation guidance
- Call-to-action cultural optimization

### Channel-Specific Adaptations
- Social media platform preferences by market
- Content style and posting frequency recommendations
- Engagement and community management strategies
- Influencer and partnership considerations
- Email marketing cultural adaptation

### Implementation Plan
- Phase 1: Cultural research and analysis
- Phase 2: Message and visual adaptation
- Phase 3: Testing and refinement
- Phase 4: Launch and monitoring

## Safety & Limitations

### Safety Boundaries
- **No Professional Advice**: Provides informational frameworks only. Does not replace professional marketing consultants.
- **No Real-Time Data**: Based on general cultural frameworks, not current market research.
- **No Campaign Execution**: No actual campaign creation or management capabilities.
- **No Code Execution**: Pure descriptive implementation. No shell commands or network requests.
- **Descriptive Only**: Provides planning frameworks and guidance only.

### Limitations
- Cultural generalizations may not apply to all segments within a culture
- Individual preferences vary within cultural groups
- Cultural norms evolve over time
- Requires verification with local market research
- Does not replace local marketing expertise

## Example Prompts

### Level 1: Basic Inquiry
"How to adapt my marketing for Japanese consumers?"

### Level 2: Specific Scenario
"Premium fashion brand marketing adaptation for German market"

### Level 3: Complex Planning
"Multi-market campaign adaptation for France, Germany, and Japan with different brand positions"

### Level 4: Detailed Case
"US sustainable tech company adapting social media and email marketing for Chinese consumers"

## Acceptance Criteria

### Functional Requirements
- Returns valid JSON structure from handle() function
- Includes input_analysis field with parsed input information
- Contains proper disclaimer with safety boundaries
- Provides culture-specific analysis and message adaptation
- Differentiated from other cross-border e-commerce skills

### Quality Requirements
- Clear and structured output
- Comprehensive framework coverage
- Actionable implementation guidance
- Proper safety boundaries enforced
- Input differentiation verified through tests

## Integration

### Complementary Skills
- Works with cb-product-localization-advisor for holistic market entry
- Integrates with cb-customer-service-localizer for consistent cultural approach
- Supports cb-market-entry-strategist for market selection

### Input/Output Flow
- Accepts natural language input via handle() function
- Returns structured JSON for system integration
- Can be chained with related skills for multi-faceted analysis

## Version History

### v1.0.0 (2026-04-22)
- Initial release
- Cultural analysis framework for major markets
- Message adaptation with rationale
- Channel-specific adaptation recommendations
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
- Marketing-specific functionality test
- Differentiation evidence test
