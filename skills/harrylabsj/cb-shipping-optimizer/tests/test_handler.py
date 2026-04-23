#!/usr/bin/env python3
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from handler import handle

CASES = [
    {'name': 'test_us_de', 'input': 'best shipping options for electronics from China to US and Germany 2kg package value 200',
     'checks': [lambda p: 'carrier_evaluation_matrix' in p, lambda p: len(p['carrier_evaluation_matrix'].get('carrier_evaluation',[]))>=5,
                lambda p: 'lane_recommendations' in p, lambda p: 'customs_clearance_framework' in p,
                lambda p: 'cost_optimization_strategies' in p, lambda p: 'disclaimer' in p]},
    {'name': 'test_uk_jp_au', 'input': 'how to reduce international shipping costs for apparel to UK Japan Australia 1kg',
     'checks': [lambda p: 'carrier_evaluation_matrix' in p, lambda p: 'lane_recommendations' in p,
                lambda p: 'cost_optimization_strategies' in p, lambda p: 'disclaimer' in p]},
    {'name': 'test_fast', 'input': 'fast delivery shipping strategy for electronics to France and Brazil 3kg fast',
     'checks': [lambda p: 'carrier_evaluation_matrix' in p, lambda p: 'customs_clearance_framework' in p,
                lambda p: 'disclaimer' in p]},
    {'name': 'test_empty', 'input': '',
     'checks': [lambda p: isinstance(p,dict), lambda p: 'skill' in p, lambda p: 'disclaimer' in p]},
]

if __name__ == '__main__':
    print('cb-shipping-optimizer tests')
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
