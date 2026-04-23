#!/usr/bin/env python3
# Cross-border Market Entry Strategist - handler.py
# Pure descriptive skill. No code execution, API calls, or network access.
import json, re

SKILL_INFO = {'name': 'Cross-border Market Entry Strategist', 'slug': 'cb-market-entry-strategist', 'version': '1.0.0'}

MARKETS = {
    'Germany': {'score': 82, 'strengths': ['High purchasing power','Excellent logistics','Digital maturity'], 'risks': ['Strict regulatory','Language barrier','High competition'], 'complexity': 'Medium-High'},
    'Japan': {'score': 78, 'strengths': ['Very high purchasing power','Quality-focused consumers','Strong logistics'], 'risks': ['Strict regulatory','Language barrier','Cultural complexity'], 'complexity': 'High'},
    'Australia': {'score': 75, 'strengths': ['High purchasing power','English-speaking','Strong digital adoption'], 'risks': ['Distance','Small market','Seasonal opposite'], 'complexity': 'Low-Medium'},
    'France': {'score': 74, 'strengths': ['Large market','EU access','High digital adoption'], 'risks': ['Strict regulatory','Language barrier','High competition'], 'complexity': 'Medium'},
    'UK': {'score': 76, 'strengths': ['Large English-speaking market','Excellent logistics','High digital adoption'], 'risks': ['Post-Brexit complexity','High competition','Market saturation'], 'complexity': 'Medium'},
    'Canada': {'score': 77, 'strengths': ['High purchasing power','English/French','US adjacency'], 'risks': ['US competition','Regional diversity','Bilingual requirements'], 'complexity': 'Low-Medium'},
    'Netherlands': {'score': 79, 'strengths': ['EU logistics hub','Excellent English','High digital adoption'], 'risks': ['Small market','EU regulatory','Price sensitivity'], 'complexity': 'Low-Medium'},
    'South Korea': {'score': 73, 'strengths': ['Very high purchasing power','Mobile-first','Excellent logistics'], 'risks': ['Strong local brands','High competition','Cultural complexity'], 'complexity': 'High'},
    'Brazil': {'score': 65, 'strengths': ['Large market','Growing middle class','E-commerce growth'], 'risks': ['Complex tax system','Logistics challenges','Currency volatility'], 'complexity': 'High'},
    'India': {'score': 68, 'strengths': ['Very large market','Rapidly growing','English-speaking'], 'risks': ['Complex regulatory','Logistics challenges','Price sensitivity'], 'complexity': 'High'},
}

def _parse_input(user_input):
    inp = user_input.lower()
    p = {'original_input': user_input[:100], 'word_count': len(user_input.split())}
    found = [m for m in MARKETS if m.lower() in inp]
    p['target_markets'] = found[:5] if found else list(MARKETS.keys())[:5]
    cats = []
    for cat, terms in [('electronics',['electronics','electronic','tech']),
                        ('apparel',['apparel','clothing','fashion']),
                        ('home_goods',['home','furniture','decor']),
                        ('beauty',['beauty','cosmetics','skincare']),
                        ('food',['food','grocery'])]:
        if any(t in inp for t in terms): cats.append(cat)
    p['product_categories'] = cats or ['general_merchandise']
    m = re.search(r'\$\d+', user_input)
    p['budget_usd'] = int(m.group(1)) if m else 50000
    tm = re.search(r'(\d+)\s*(month|year)', inp)
    if tm:
        v = int(tm.group(1)); u = tm.group(2)
        p['timeline_months'] = v if u=='month' else v*12
    else:
        p['timeline_months'] = 6
    return p

def _score_market(market, data, budget, timeline):
    score = data['score'] + (5 if budget > 100000 else 0) + (5 if timeline >= 12 else 0)
    return {'market': market, 'overall_score': min(98, score), 'strengths': data['strengths'], 'risks': data['risks'], 'entry_complexity': data['complexity']}

def _phased_strategy(timeline, budget):
    if timeline >= 12:
        phases = [
            {'phase': 'Phase 1 (0-3 mo)', 'action': 'Market research, regulatory review, local counsel engagement', 'budget_pct': '15%'},
            {'phase': 'Phase 2 (3-6 mo)', 'action': 'Test via marketplace with limited SKUs; validate logistics', 'budget_pct': '25%'},
            {'phase': 'Phase 3 (6-12 mo)', 'action': 'Dedicated storefront with localized content; local marketing', 'budget_pct': '40%'},
            {'phase': 'Phase 12+ mo', 'action': 'Full localization investment; brand building; consider local entity', 'budget_pct': '20%'},
        ]
    elif timeline >= 6:
        phases = [
            {'phase': 'Phase 1 (0-2 mo)', 'action': 'Compliance setup, VAT registration, legal counsel', 'budget_pct': '20%'},
            {'phase': 'Phase 2 (2-4 mo)', 'action': 'Marketplace listing with core SKU range', 'budget_pct': '35%'},
            {'phase': 'Phase 3 (4-6 mo)', 'action': 'Evaluate performance; plan dedicated storefront expansion', 'budget_pct': '45%'},
        ]
    else:
        phases = [
            {'phase': 'Phase 1 (0-1 mo)', 'action': 'Quick regulatory check, marketplace listing', 'budget_pct': '30%'},
            {'phase': 'Phase 2 (1-3 mo)', 'action': 'Pilot launch; collect feedback; iterate quickly', 'budget_pct': '70%'},
        ]
    return {'phased_approach': phases}

def _checklist(markets):
    base = ['Conduct market-specific regulatory compliance review','Engage local legal counsel for entity/registration requirements','Register for VAT/tax obligations in target markets','Set up local payment processor accounts','Configure shipping carrier accounts with international coverage','Establish local language customer service capability','Translate and localize all customer-facing content','Implement GDPR/data protection compliance for EU markets','Set up international returns process and policy','Configure pricing engine for local currency display','Establish local marketing and advertising accounts','Define KPI framework for market performance monitoring','Create contingency plans for regulatory changes']
    extras = {'Germany': ['Register German VAT (StNr)', 'Create Impressum per TMG', 'Add German 14-day withdrawal rights'],'Japan': ['Register with METI if required', 'Configure Konbini/Rakuten Pay', 'Ensure PSC product safety mark'],'UK': ['Post-Brexit customs compliance', 'UK VAT registration', 'UK return address setup'],'Australia': ['Australian Business Number (ABN) for GST', 'Import duty classification', 'Create AU return address']}
    for market in markets:
        for item in extras.get(market, []):
            if item not in base: base.append(item)
    return base

def _risks():
    return {
        'regulatory_risks': [{'risk': 'Unexpected regulatory requirements', 'mitigation': 'Engage local legal counsel before launch'},{'risk': 'VAT/tax compliance penalties', 'mitigation': 'Work with international tax advisor; automate tax calc'}],
        'operational_risks': [{'risk': 'Shipping delays and customs issues', 'mitigation': 'Use established carriers with customs brokerage'},{'risk': 'Local fulfillment challenges', 'mitigation': 'Start with marketplace fulfillment before dedicated setup'}],
        'market_risks': [{'risk': 'Cultural misalignment', 'mitigation': 'Invest in cultural research; small tests before full rollout'},{'risk': 'Currency volatility', 'mitigation': 'Set dynamic currency conversion rules; quarterly pricing review'}],
    }

def handle(user_input):
    parsed = _parse_input(user_input)
    scored = [_score_market(m, MARKETS[m], parsed['budget_usd'], parsed['timeline_months']) for m in parsed['target_markets']]
    scored.sort(key=lambda x: x['overall_score'], reverse=True)
    response = {
        'skill': SKILL_INFO['slug'],
        'name': SKILL_INFO['name'],
        'input_analysis': parsed,
        'market_analysis': {'evaluated_markets': scored},
        'entry_strategy_framework': _phased_strategy(parsed['timeline_months'], parsed['budget_usd']),
        'implementation_checklist': _checklist(parsed['target_markets']),
        'risk_mitigation_framework': _risks(),
        'disclaimer': 'Descriptive guidance only. Not professional legal, tax, financial, or business advice. Verify with qualified professionals.',
    }
    return json.dumps(response, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    for t in ['I sell electronics and want to expand to Germany and Japan within 6 months',
              'help me evaluate Australia Canada Netherlands for cross-border expansion budget',
              'which markets should I enter next for my apparel brand']:
        p = json.loads(handle(t))
        assert 'disclaimer' in p and 'market_analysis' in p
        print('  PASS: ' + t[:50])
    print('All self-tests passed!')
