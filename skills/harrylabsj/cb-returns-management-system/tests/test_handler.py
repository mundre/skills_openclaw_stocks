#!/usr/bin/env python3
"""
Tests for International Returns Management System
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handler import handle

def test_json():
    """Test JSON output."""
    result = handle("test")
    parsed = json.loads(result)
    assert "skill" in parsed
    assert parsed["skill"] == "cb-returns-management-system"
    print(f"✓ JSON test passed")

def test_disclaimer():
    """Test disclaimer."""
    result = handle("test")
    parsed = json.loads(result)
    assert "disclaimer" in parsed
    assert parsed["disclaimer"]
    print(f"✓ Disclaimer test passed")

def test_input_analysis():
    """Test input analysis."""
    result = handle("test input")
    parsed = json.loads(result)
    assert "input_analysis" in parsed
    print(f"✓ Input analysis test passed")

def test_returns_specific():
    """Test returns-specific field."""
    result = handle("test")
    parsed = json.loads(result)
    assert "returns_analysis" in parsed
    print(f"✓ returns-specific test passed")

def test_differentiation():
    """Test input differentiation."""
    result1 = handle("test one")
    result2 = handle("test two different")
    parsed1 = json.loads(result1)
    parsed2 = json.loads(result2)
    assert json.dumps(parsed1) != json.dumps(parsed2)
    print(f"✓ Differentiation test passed")

if __name__ == "__main__":
    print(f"Testing cb-returns-management-system...")
    tests = [test_json, test_disclaimer, test_input_analysis, test_returns_specific, test_differentiation]
    passed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: {e}")
    
    print(f"\n{passed}/{len(tests)} tests passed")
    sys.exit(0 if passed == len(tests) else 1)
