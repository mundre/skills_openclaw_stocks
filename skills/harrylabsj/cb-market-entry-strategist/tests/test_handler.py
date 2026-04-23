#!/usr/bin/env python3
# test_handler.py for cb-market-entry-strategist
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from handler import handle

CASES = [
    {"name": "test_valid", "input": "I sell electronics and want to expand to Germany and Japan within 6 months budget 100k dollars",
     "checks": [lambda p: "market_analysis" in p, lambda p: len(p["market_analysis"].get("evaluated_markets",[]))>=2,
                lambda p: "entry_strategy_framework" in p, lambda p: "implementation_checklist" in p,
                lambda p: "risk_mitigation_framework" in p, lambda p: "disclaimer" in p, lambda p: "input_analysis" in p]},
    {"name": "test_multi", "input": "help me evaluate Australia Canada Netherlands Brazil for cross-border expansion",
     "checks": [lambda p: "market_analysis" in p, lambda p: len(p["market_analysis"].get("evaluated_markets",[]))>=3,
                lambda p: "entry_strategy_framework" in p, lambda p: "disclaimer" in p]},
    {"name": "test_general", "input": "which markets should I expand to next for my online store selling electronics",
     "checks": [lambda p: "market_analysis" in p, lambda p: "implementation_checklist" in p,
                lambda p: "input_analysis" in p, lambda p: "disclaimer" in p]},
    {"name": "test_empty", "input": "",
     "checks": [lambda p: isinstance(p,dict), lambda p: "skill" in p, lambda p: "disclaimer" in p]},
    {"name": "test_small", "input": "I have 5k budget want to test one market for my clothing brand in 3 months",
     "checks": [lambda p: "market_analysis" in p, lambda p: "entry_strategy_framework" in p,
                lambda p: "implementation_checklist" in p, lambda p: "disclaimer" in p]},
]

if __name__ == "__main__":
    print("cb-market-entry-strategist tests")
    print("="*50)
    passed = 0
    for tc in CASES:
        try: p = json.loads(handle(tc["input"]))
        except Exception as e: print("  FAIL " + tc["name"] + ": " + str(e)); continue
        failed = [c.__name__ for c in tc["checks"] if not c(p)]
        if failed: print("  FAIL " + tc["name"] + ": " + str(failed))
        else: print("  PASS " + tc["name"]); passed += 1
    print("")
    print(str(passed) + "/" + str(len(CASES)) + " tests passed.")
    if passed == len(CASES): print("All tests passed!")
    else: sys.exit(1)
