#!/usr/bin/env python3
"""
Tests for Cultural Marketing Adaptation Framework
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handler import handle

def test_json_output():
    """Test that handler returns valid JSON."""
    result = handle("test input for cultural marketing")
    
    # Parse JSON
    parsed = json.loads(result)
    
    # Check required fields
    assert "skill" in parsed, "Missing skill field"
    assert parsed["skill"] == "cb-cultural-marketing-framework", f"Wrong skill identifier: {parsed['skill']}"
    assert "input_analysis" in parsed, "Missing input_analysis field"
    assert "disclaimer" in parsed, "Missing disclaimer field"
    assert "cultural_analysis_framework" in parsed, "Missing cultural_analysis_framework field"
    assert "message_adaptation_framework" in parsed, "Missing message_adaptation_framework field"
    
    print("✓ JSON test passed")
    return True

def test_disclaimer():
    """Test that disclaimer is present and appropriate."""
    result = handle("test")
    parsed = json.loads(result)
    
    disclaimer = parsed.get("disclaimer", "")
    assert disclaimer, "Disclaimer is empty"
    assert "descriptive" in disclaimer.lower(), "Disclaimer should mention descriptive nature"
    assert "no code execution" in disclaimer.lower() or "no professional advice" in disclaimer.lower(), "Disclaimer should include safety boundaries"
    
    print("✓ Disclaimer test passed")
    return True

def test_input_differentiation():
    """Test that different inputs produce different outputs."""
    result1 = handle("marketing for Japan")
    result2 = handle("marketing for Germany")
    
    parsed1 = json.loads(result1)
    parsed2 = json.loads(result2)
    
    # They should not be identical
    assert json.dumps(parsed1, sort_keys=True) != json.dumps(parsed2, sort_keys=True), "Different inputs should produce different outputs"
    
    print("✓ Input differentiation test passed")
    return True

def test_marketing_specific():
    """Test marketing-specific functionality."""
    result = handle("cultural marketing adaptation for luxury fashion")
    parsed = json.loads(result)
    
    # Check for marketing-specific fields
    assert "cultural_analysis_framework" in parsed, "Missing cultural_analysis_framework field"
    assert "message_adaptation_framework" in parsed, "Missing message_adaptation_framework field"
    
    # Check that cultural analysis has expected structure
    cultural_analysis = parsed["cultural_analysis_framework"]
    assert isinstance(cultural_analysis, dict), "cultural_analysis_framework should be a dictionary"
    
    # Check that message adaptation has expected structure
    message_adaptation = parsed["message_adaptation_framework"]
    assert isinstance(message_adaptation, dict), "message_adaptation_framework should be a dictionary"
    
    print("✓ Marketing-specific test passed")
    return True

def test_differentiation_evidence():
    """Test that differentiation evidence is provided."""
    result = handle("cultural marketing test")
    parsed = json.loads(result)
    
    # Check for differentiation evidence
    assert "differentiation_evidence" in parsed, "Missing differentiation_evidence field"
    evidence = parsed["differentiation_evidence"]
    
    # Should have some evidence fields
    assert len(evidence) > 0, "Differentiation evidence should not be empty"
    
    print("✓ Differentiation evidence test passed")
    return True

def run_all_tests():
    """Run all tests."""
    print("\\nRunning tests for cb-cultural-marketing-framework...")
    print("-" * 40)
    
    tests = [
        test_json_output,
        test_disclaimer,
        test_input_differentiation,
        test_marketing_specific,
        test_differentiation_evidence
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {str(e)}")
    
    print(f"\\n{passed}/{len(tests)} tests passed")
    return passed == len(tests)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
