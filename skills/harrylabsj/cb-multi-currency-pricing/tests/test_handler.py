#!/usr/bin/env python3
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from handler import handle

CASES = [
    {'name': 'test_de_jp_au', 'input': 'multi-currency pricing for my electronics product at 100 for Germany Japan and Australia',
     'checks': [lambda p: 'multi_currency_pricing' in p, lambda p: len(p['multi_currency_pricing'].get('prices',[]))>=3,
                lambda p: 'pricing_strategy_framework' in p, lambda p: 'currency_risk_management' in p,
                lambda p: 'competitive_positioning' in p, lambda p: 'disclaimer' in p]},
    {'name': 'test_competitive', 'input': 'help me price my apparel at 50 for UK Canada and Brazil competitive pricing',
     'checks': [lambda p: 'multi_currency_pricing' in p, lambda p: 'pricing_strategy_framework' in p,
                lambda p: 'currency_risk_management' in p, lambda p: 'disclaimer' in p]},
    {'name': 'test_premium', 'input': 'premium pricing strategy for 200 dollar electronics for France and India',
     'checks': [lambda p: 'multi_currency_pricing' in p, lambda p: 'competitive_positioning' in p,
                lambda p: 'disclaimer' in p]},
    {'name': 'test_empty', 'input': '',
     'checks': [lambda p: isinstance(p,dict), lambda p: 'skill' in p, lambda p: 'disclaimer' in p]},
]

if __name__ == '__main__':
    print('cb-multi-currency-pricing tests')
    print('='*50)
    passed = 0
    for tc in CASES:
        try: p = json.loads(handle(tc['input']))
        except Exception as e: print('  FAIL ' + tc['name'] + ': ' + str(e)); continue
        failed = [c.__name__ for c in tc['checks'] if not c(p)]
        if failed: print('  FAIL ' + tc['name'] + ': ' + str(failed))
        else: print('  PASS ' + tc['name']); passed += 1
    print(f'\n{passed}/{len(CASES)} tests passed.')
    if passed == len(CASES): print('All tests passed!')
    else: sys.exit(1)
