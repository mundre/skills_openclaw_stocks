#!/usr/bin/env python3
# Product Localization Advisor - handler.py
# Pure descriptive skill. No code execution, API calls, or network access.
import json, re

SKILL_INFO = {'name': 'Product Localization Advisor', 'slug': 'cb-product-localization-advisor', 'version': '1.0.0'}

REGULATORY_DB = {
    'Germany': {'certifications': ['CE marking', 'GS mark (voluntary)'], 'labels': ['German language required', 'Energy label (electronics)'],
                'product_safety': ['ProdSG compliance', 'ElektroG (WEEE)', 'BattG (batteries)'], 'packaging': ['Packaging Act (VerpackG)', 'Green Dot']},
    'France': {'certifications': ['CE marking', 'NF mark'], 'labels': ['French language required', 'French label requirements'],
               'product_safety': ['REACH', 'CLP (chemicals)'], 'packaging': ['French packaging regulations', 'Triman logo']},
    'Japan': {'certifications': ['PSE mark (electrical)', 'SG mark (general)', 'JIS mark'], 'labels': ['Japanese language required', 'JIS label'],
              'product_safety': ['Electrical Appliance Safety Act', 'Consumer Product Safety Act'], 'packaging': ['Japanese packaging standards', 'Recycling law']},
    'Australia': {'certifications': ['RCM mark', 'AS/NZS standards'], 'labels': ['English required', 'Country of origin labeling'],
                  'product_safety': ['ACL compliance', 'ACCC product safety bans'], 'packaging': ['Australian packaging covenant']},
    'UK': {'certifications': ['UKCA mark (replaces CE)', 'UK NI marking'], 'labels': ['English required', 'UK-specific labeling'],
           'product_safety': ['UK Product Safety Regulations', 'UK REACH'], 'packaging': ['UK Packaging Regulations']},
    'US': {'certifications': ['FCC (electronics)', 'UL (safety)', 'FDA (cosmetics/food)'], 'labels': ['English required', 'FTC labeling'],
           'product_safety': ['CPSIA (children)', 'FDA regulations'], 'packaging': ['US packaging regulations']},
}

CULTURAL_DB = {
    'Germany': {'priorities': ['Quality over convenience', 'Environmental consciousness', 'Privacy'],
                'adaptations': ['Detailed technical specs', 'Strong warranty terms', 'Cash/card payment preference'],
                'marketing': ['Direct and factual', 'Build trust through reviews', 'German influencer marketing']},
    'France': {'priorities': ['Design and aesthetics', 'Brand heritage', 'Quality of life'],
               'adaptations': ['Elegant packaging', 'French language customer service', 'French payment methods'],
               'marketing': ['Emotional storytelling', 'Cultural references', 'French brand ambassadors']},
    'Japan': {'priorities': ['Omotenashi (hospitality)', 'Attention to detail', 'Trust and reliability'],
              'adaptations': ['Elaborate packaging', 'Detailed instructions', 'Multiple payment options (Konbini, PayPay)'],
              'marketing': ['Kawaii aesthetic', 'Line/Instagram social', 'Celebrity endorsements']},
    'Australia': {'priorities': ['Value for money', 'Convenience', 'Practicality'],
                  'adaptations': ['Simple straightforward packaging', 'Clear return policy', 'Afterpay/zip'],
                  'marketing': ['Humorous and casual', 'Sports and outdoor', 'Facebook/Instagram focus']},
    'UK': {'priorities': ['Value consciousness', 'Brand loyalty', 'Convenience'],
           'adaptations': ['Clear pricing', 'Klarna/Clearpay', 'Royal Mail delivery preference'],
           'marketing': ['British humor', 'Quality messaging', 'Celebrity partnerships']},
    'US': {'priorities': ['Convenience', 'Speed', 'Value deals'],
           'adaptations': ['Free returns', 'Amazon Prime compatibility', 'BNPL options'],
           'marketing': ['Direct and benefit-driven', 'Social proof heavy', 'Influencer heavy']},
}

def _parse_input(user_input):
    inp = user_input.lower()
    p = {'original_input': user_input[:100], 'word_count': len(user_input.split())}
    found = [m for m in REGULATORY_DB if m.lower() in inp]
    p['target_markets'] = found[:5] if found else list(REGULATORY_DB.keys())[:3]
    cats = []
    for cat, terms in [('electronics',['electronics','electronic','tech','gadget']),('apparel',['apparel','clothing','fashion','wear']),
                       ('beauty',['beauty','cosmetics','skincare','makeup']),('home',['home','furniture','decor'])]:
        if any(t in inp for t in terms): cats.append(cat)
    p['product_categories'] = cats or ['general_merchandise']
    if 'compliance' in inp: p['localization_goals'] = 'regulatory_compliance'
    elif 'cultural' in inp: p['localization_goals'] = 'cultural_appropriateness'
    elif 'competit' in inp: p['localization_goals'] = 'competitive_positioning'
    else: p['localization_goals'] = 'full_localization'
    return p

def _regulatory(markets, categories):
    result = {}
    for m in markets:
        if m not in REGULATORY_DB: continue
        r = REGULATORY_DB[m]
        result[m] = {'market': m, 'required_certifications': r['certifications'], 'labeling_requirements': r['labels'],
                     'product_safety_requirements': r['product_safety'], 'packaging_requirements': r['packaging']}
    return result

def _cultural(markets):
    result = {}
    for m in markets:
        if m not in CULTURAL_DB: continue
        c = CULTURAL_DB[m]
        result[m] = {'cultural_priorities': c['priorities'], 'recommended_adaptations': c['adaptations'],
                     'marketing_approach': c['marketing']}
    return result

def _competitive(markets):
    return {m: {'differentiation': ['Superior quality vs local brands', 'Competitive pricing', 'Unique product features'],
                'positioning': ['Premium international brand', 'Value alternative to local incumbents', 'Niche specialist']}
            for m in markets}

def _impl_plan():
    return {'implementation_plan': [
        {'phase': 'Phase 1 (Month 1-2)', 'actions': ['Obtain required certifications per market', 'Translate all content to local languages', 'Design market-compliant packaging']},
        {'phase': 'Phase 2 (Month 2-4)', 'actions': ['Implement cultural adaptations', 'Set up local customer service', 'Adapt pricing for market expectations']},
        {'phase': 'Phase 3 (Month 4-6)', 'actions': ['Launch in first market', 'Gather feedback and iterate', 'Prepare expansion to additional markets']}]}

def handle(user_input):
    parsed = _parse_input(user_input)
    return json.dumps({
        'skill': SKILL_INFO['slug'], 'name': SKILL_INFO['name'],
        'input_analysis': parsed,
        'regulatory_adaptations': _regulatory(parsed['target_markets'], parsed['product_categories']),
        'cultural_adaptations': _cultural(parsed['target_markets']),
        'competitive_analysis_framework': _competitive(parsed['target_markets']),
        'localization_implementation_plan': _impl_plan(),
        'disclaimer': 'Descriptive guidance only. Not professional legal, regulatory, or business advice. Verify with qualified professionals.',
    }, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    for t in ['how should I adapt my electronics products for Germany and Japan market',
              'help me localize apparel products for France and Australia',
              'what product changes needed for selling beauty products in UK and US']:
        p = json.loads(handle(t))
        assert 'regulatory_adaptations' in p and 'cultural_adaptations' in p
        assert 'competitive_analysis_framework' in p
        print('  PASS: ' + t[:50])
    print('All self-tests passed!')
