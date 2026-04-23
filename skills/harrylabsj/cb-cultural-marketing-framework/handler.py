#!/usr/bin/env python3
"""
Cultural Marketing Adaptation Framework - Differentiated Implementation
"""

import json
import re
import sys

def parse_marketing_input(user_input: str):
    """Parse marketing-specific input with cultural nuance extraction."""
    input_lower = user_input.lower()
    
    parsed = {
        "original_input": user_input,
        "input_preview": user_input[:100] + ("..." if len(user_input) > 100 else ""),
        "word_count": len(user_input.split()),
        "target_culture": None,
        "brand_positioning": None,
        "product_category": None,
        "marketing_channels": [],
        "campaign_objective": None
    }
    
    # Extract target culture
    culture_keywords = {
        "japanese": ["japan", "japanese"],
        "chinese": ["china", "chinese"],
        "german": ["germany", "german"],
        "french": ["france", "french"],
        "british": ["uk", "britain", "british"],
        "american": ["usa", "us", "america", "american"],
        "korean": ["korea", "korean"]
    }
    
    for culture, keywords in culture_keywords.items():
        for keyword in keywords:
            if keyword in input_lower:
                parsed["target_culture"] = culture
                break
        if parsed["target_culture"]:
            break
    
    # Extract brand positioning
    if "premium" in input_lower or "luxury" in input_lower:
        parsed["brand_positioning"] = "premium"
    elif "budget" in input_lower or "affordable" in input_lower:
        parsed["brand_positioning"] = "budget"
    elif "sustainable" in input_lower or "eco" in input_lower:
        parsed["brand_positioning"] = "sustainable"
    
    # Extract product category
    if "fashion" in input_lower:
        parsed["product_category"] = "fashion"
    elif "tech" in input_lower:
        parsed["product_category"] = "technology"
    elif "food" in input_lower:
        parsed["product_category"] = "food"
    
    # Extract marketing channels
    if "social" in input_lower:
        parsed["marketing_channels"].append("social_media")
    if "email" in input_lower:
        parsed["marketing_channels"].append("email_marketing")
    if "search" in input_lower:
        parsed["marketing_channels"].append("search_ads")
    
    return parsed

def generate_cultural_analysis(parsed_input):
    """Generate culture-specific analysis."""
    culture = parsed_input.get("target_culture", "general")
    positioning = parsed_input.get("brand_positioning", "general")
    
    analysis = {}
    
    if culture == "japanese":
        analysis = {
            "communication_style": "Indirect, relationship-focused",
            "key_values": ["Harmony", "Quality", "Attention to detail"],
            "visual_preferences": ["Minimalist", "Clean", "Precise"],
            "cultural_considerations": [
                "Avoid direct confrontation",
                "Emphasize craftsmanship",
                "Use respectful language"
            ]
        }
    elif culture == "german":
        analysis = {
            "communication_style": "Direct, factual, structured",
            "key_values": ["Precision", "Quality", "Efficiency"],
            "visual_preferences": ["Functional", "Clean", "Minimalist"],
            "cultural_considerations": [
                "Provide detailed specifications",
                "Avoid exaggeration",
                "Respect formal titles"
            ]
        }
    elif culture == "french":
        analysis = {
            "communication_style": "Eloquent, aesthetic-focused",
            "key_values": ["Elegance", "Artistry", "Heritage"],
            "visual_preferences": ["Sophisticated", "Artistic", "Elegant"],
            "cultural_considerations": [
                "Use sophisticated language",
                "Incorporate cultural references",
                "Value intellectual discussion"
            ]
        }
    else:
        analysis = {
            "communication_style": "Research required for specific culture",
            "key_values": ["Cultural research needed"],
            "visual_preferences": ["Adapt to local aesthetics"],
            "cultural_considerations": ["Conduct local market research"]
        }
    
    # Adjust for brand positioning
    if positioning == "premium":
        analysis["positioning_adjustment"] = "Emphasize exclusivity and craftsmanship"
    elif positioning == "sustainable":
        analysis["positioning_adjustment"] = "Focus on environmental and ethical values"
    
    return analysis

def generate_message_adaptations(parsed_input, cultural_analysis):
    """Generate message adaptations."""
    culture = parsed_input.get("target_culture", "general")
    
    adaptations = {
        "original_message": "High-quality product at competitive price",
        "adapted_message": "",
        "rationale": "",
        "channel_adaptations": {}
    }
    
    if culture == "japanese":
        adaptations["adapted_message"] = "Meticulously crafted product offering exceptional value and lasting quality"
        adaptations["rationale"] = "Shift from direct price mention to emphasis on craftsmanship and lasting value"
    elif culture == "german":
        adaptations["adapted_message"] = "Precision-engineered product offering optimal performance at competitive pricing"
        adaptations["rationale"] = "Emphasize engineering and performance with factual price reference"
    else:
        adaptations["adapted_message"] = "Quality product offering good value"
        adaptations["rationale"] = "General adaptation - refine based on specific culture"
    
    # Channel adaptations
    channels = parsed_input.get("marketing_channels", ["social_media"])
    for channel in channels:
        if channel == "social_media":
            adaptations["channel_adaptations"]["social_media"] = {
                "content_style": "Visual-focused with minimal text",
                "engagement_approach": "Community building and relationship focus"
            }
        elif channel == "email_marketing":
            adaptations["channel_adaptations"]["email_marketing"] = {
                "subject_line_style": "Clear and direct",
                "content_structure": "Structured with clear benefits"
            }
    
    return adaptations

def handle(user_input: str) -> str:
    """Standard OpenClaw handler interface."""
    parsed_input = parse_marketing_input(user_input)
    cultural_analysis = generate_cultural_analysis(parsed_input)
    message_adaptations = generate_message_adaptations(parsed_input, cultural_analysis)
    
    response = {
        "skill": "cb-cultural-marketing-framework",
        "name": "Cultural Marketing Adaptation Framework",
        "input_analysis": parsed_input,
        "cultural_analysis_framework": cultural_analysis,
        "message_adaptation_framework": message_adaptations,
        "implementation_plan": {
            "phase_1": "Cultural research and analysis",
            "phase_2": "Message and visual adaptation",
            "phase_3": "Testing and refinement",
            "phase_4": "Launch and monitoring"
        },
        "differentiation_evidence": {
            "culture_specific": parsed_input.get("target_culture") is not None,
            "positioning_specific": parsed_input.get("brand_positioning") is not None,
            "product_category_specific": parsed_input.get("product_category") is not None,
            "channel_specific": len(parsed_input.get("marketing_channels", [])) > 0
        },
        "recommendations": [
            "Conduct in-depth cultural research before adaptation",
            "Test adapted messaging with local focus groups",
            "Work with cultural consultants for nuanced adaptation",
            "Monitor campaign performance and adjust as needed"
        ],
        "disclaimer": "Descriptive cross-border e-commerce planning only. No code execution, API calls, network requests, bookings, or real-time data. Does not provide professional marketing advice."
    }
    
    return json.dumps(response, indent=2)

if __name__ == "__main__":
    input_text = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    print(handle(input_text))
