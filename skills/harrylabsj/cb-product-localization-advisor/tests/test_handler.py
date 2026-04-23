#!/usr/bin/env python3
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from handler import handle

CASES = [
    {'name': 'test_electronics_de_jp', 'input': 'how should I adapt my electronics products for Germany and Japan market',
     'checks': [lambda p: 'regulatory_adaptations' in p, lambda p: len(p['regulatory_adaptations'])>=2,
                lambda p: 'cultural_adaptations' in p, lambda p: 'competitive_analysis_framework' in p,
                lambda p: 'localization_implementation_plan' in p, lambda p: 'disclaimer' in p]},
    {'name': 'test_apparel_fr_au', 'input': 'help me localize apparel for France and Australia',
     'checks': [lambda p: 'regulatory_adaptations' in p, lambda p: 'cultural_adaptations' in p,
                lambda p: 'localization_implementation_plan' in p, lambda p: 'disclaimer' in p]},
    {'name': 'test_beauty_uk_us', 'input': 'product changes needed for selling beauty products in UK and US',
     'checks': [lambda p: 'regulatory_adaptations' in p, lambda p: 'competitive_analysis_framework' in p,
                lambda p: 'disclaimer' in p]},
    {'name': 'test_empty', 'input': '',
     'checks': [lambda p: isinstance(p,dict), lambda p: 'skill' in p, lambda p: 'disclaimer' in p]},
]

if __name__ == '__main__':
    print('cb-product-localization-advisor tests')
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
