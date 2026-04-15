#!/usr/bin/env python3
import json
import os
import re
from typing import Any, Dict, List, Sequence


def _load_skill_meta(slug):
    path = os.path.join(os.path.dirname(__file__), 'SKILL.md')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    meta = re.search(r'^---$(.*?)^---$', content, re.DOTALL | re.MULTILINE)
    return meta.group(1).strip() if meta else ''


def _normalize_inputs(inputs: Any) -> str:
    if inputs is None:
        return ''
    if isinstance(inputs, str):
        return inputs.strip()
    if isinstance(inputs, dict):
        parts = []
        for key, value in inputs.items():
            if value in (None, '', [], {}, ()):  # type: ignore[comparison-overlap]
                continue
            if isinstance(value, (list, tuple, set)):
                rendered = ', '.join(str(item) for item in value)
            else:
                rendered = str(value)
            parts.append(f"{key}: {rendered}")
        return ' | '.join(parts)
    if isinstance(inputs, (list, tuple, set)):
        return ' | '.join(str(item) for item in inputs)
    try:
        return json.dumps(inputs, ensure_ascii=False, sort_keys=True)
    except TypeError:
        return str(inputs)


def _coerce_dict(inputs: Any) -> Dict[str, Any]:
    return inputs if isinstance(inputs, dict) else {}


def _pick_text(data: Dict[str, Any], keys: Sequence[str], default: str = '') -> str:
    for key in keys:
        value = data.get(key)
        if value is None:
            continue
        if isinstance(value, (list, tuple, set)):
            text = ', '.join(str(item).strip() for item in value if str(item).strip())
        else:
            text = str(value).strip()
        if text:
            return text
    return default


def _detect_one(text: str, rules: Dict[str, Sequence[str]], default: str) -> str:
    lower = text.lower()
    for label, keywords in rules.items():
        if any(keyword in lower for keyword in keywords):
            return label
    return default


DAY_ALIASES = {
    'Monday': ['monday', 'mon'],
    'Tuesday': ['tuesday', 'tue'],
    'Wednesday': ['wednesday', 'wed'],
    'Thursday': ['thursday', 'thu'],
    'Friday': ['friday', 'fri'],
}

DIET_RULES = {
    'Vegetarian': ['vegetarian', 'meatless', 'veggie', 'plant-based'],
    'High-protein': ['high protein', 'protein', 'training', 'gym meals'],
}

BUDGET_RULES = {
    'Tight': ['tight budget', 'cheap', 'budget', 'save money', 'low cost'],
    'Flexible': ['flexible', 'splurge', 'treat', 'special dinner'],
}

ARC_TEMPLATES = {
    'Mixed': {
        'comfort': 'Sheet-pan chicken, potatoes, and one green vegetable',
        'light': 'Quick rice bowls with eggs or tuna, cucumbers, and a bright sauce',
        'protein': 'Fast stir-fry with protein, vegetables, and rice',
        'soup': 'Big pot noodle soup with extra vegetables for leftovers',
        'experimental': 'Fun Friday tacos or wraps with one fresh topping',
        'weekend': 'One slower family meal plus a leftover remix lunch',
        'simple': '15-minute noodles, eggs on toast, or rotisserie chicken wraps',
        'backup': 'Eggs, toast, and fruit or a freezer dumpling night',
        'produce': 'Leafy greens, cucumbers, onions, potatoes, carrots, herbs',
        'protein_list': 'Chicken, eggs, tofu, tuna, yogurt',
        'pantry': 'Rice, noodles, canned beans, broth, tortillas, sauces',
    },
    'Vegetarian': {
        'comfort': 'Roasted vegetable grain bowls with tahini or yogurt sauce',
        'light': 'Chopped salad with beans, feta, and toasted seeds',
        'protein': 'Tofu or lentil stir-fry with rice and crunchy vegetables',
        'soup': 'Miso noodle soup with tofu, mushrooms, and greens',
        'experimental': 'Crispy mushroom tacos or paneer wraps with slaw',
        'weekend': 'One slower vegetarian feast plus a leftover grain-bowl remix',
        'simple': '15-minute tofu noodles, bean quesadillas, or tomato eggs',
        'backup': 'Bean quesadillas, soup from the freezer, or peanut noodles',
        'produce': 'Greens, mushrooms, tomatoes, cucumbers, carrots, herbs',
        'protein_list': 'Tofu, beans, lentils, eggs, yogurt, paneer',
        'pantry': 'Rice, noodles, canned beans, lentils, tortillas, broth',
    },
    'High-protein': {
        'comfort': 'Sheet-pan chicken with potatoes and a yogurt-herb sauce',
        'light': 'Salmon or chicken rice bowls with crisp vegetables',
        'protein': 'Turkey, tofu, or beef stir-fry with rice and greens',
        'soup': 'High-protein noodle soup with chicken and extra eggs',
        'experimental': 'Skewers, tacos, or lettuce wraps with a bold sauce',
        'weekend': 'One protein-forward grill or roast plus smart leftovers',
        'simple': 'Greek yogurt bowls, rotisserie chicken wraps, or egg fried rice',
        'backup': 'Rotisserie chicken, frozen edamame, and microwaved rice',
        'produce': 'Greens, peppers, cucumbers, onions, potatoes, fruit',
        'protein_list': 'Chicken, eggs, Greek yogurt, tofu, salmon, turkey',
        'pantry': 'Rice, oats, noodles, beans, broth, tortillas, seasonings',
    },
}


def _extract_busy_nights(data: Dict[str, Any], raw: str) -> List[str]:
    explicit = data.get('busy_nights')
    if isinstance(explicit, (list, tuple, set)):
        return [str(item).strip().title() for item in explicit if str(item).strip()]
    if isinstance(explicit, str) and explicit.strip():
        return [chunk.strip().title() for chunk in explicit.split(',') if chunk.strip()]

    lower = raw.lower()
    found = []
    for day, aliases in DAY_ALIASES.items():
        if any(re.search(rf'\b{alias}\b', lower) for alias in aliases):
            found.append(day)
    return found or ['Wednesday', 'Thursday']


def _build_meal_board(diet: str, busy_nights: List[str]) -> Dict[str, str]:
    template = ARC_TEMPLATES[diet]
    roles = {
        'Monday': 'comfort',
        'Tuesday': 'light',
        'Wednesday': 'protein',
        'Thursday': 'soup',
        'Friday': 'experimental',
    }
    board = {}
    for day, role in roles.items():
        if day in busy_nights:
            board[day] = template['simple']
        else:
            board[day] = template[role]
    board['Weekend'] = template['weekend']
    return board


def handle(inputs):
    meta = _load_skill_meta('skill')
    data = _coerce_dict(inputs)
    raw = _normalize_inputs(inputs)

    diet = _detect_one(f"{_pick_text(data, ['dietary_notes', 'diet', 'dietary_preferences'])} {raw}", DIET_RULES, 'Mixed')
    budget = _pick_text(data, ['budget_notes', 'budget'], _detect_one(raw, BUDGET_RULES, 'Moderate'))
    busy_nights = _extract_busy_nights(data, raw)
    eaters = _pick_text(data, ['eaters', 'household'])
    dietary_notes = _pick_text(data, ['dietary_notes', 'diet', 'dietary_preferences'], diet)
    if eaters:
        dietary_notes = f'{dietary_notes}; eaters: {eaters}'

    board = _build_meal_board(diet, busy_nights)
    template = ARC_TEMPLATES[diet]
    prep_ahead = 'Cook one grain, wash produce, and mix one sauce early in the week so busy nights stay light.'
    leftover_plan = 'Make extra on Monday or Thursday and fold it into bowls, wraps, or soup the next day.'
    if diet == 'High-protein':
        prep_ahead = 'Cook one protein base, one grain, and a yogurt sauce before the hardest night.'
        leftover_plan = 'Turn extra protein into wraps, fried rice, or salad bowls instead of starting from zero.'
    elif diet == 'Vegetarian':
        prep_ahead = 'Wash greens, roast one tray of vegetables, and cook lentils or tofu ahead.'
        leftover_plan = 'Use leftover grains, roasted vegetables, and beans for bowls or quesadillas.'

    return f"""# Weekly Feast Plan
## Week Constraints
- Busy nights: {', '.join(busy_nights)}
- Budget notes: {budget}
- Dietary notes: {dietary_notes}

## Meal Board
- Monday: {board['Monday']}
- Tuesday: {board['Tuesday']}
- Wednesday: {board['Wednesday']}
- Thursday: {board['Thursday']}
- Friday: {board['Friday']}
- Weekend: {board['Weekend']}

## Prep and Leftovers
- Prep ahead: {prep_ahead}
- Leftover plan: {leftover_plan}
- Backup meal: {template['backup']}

## Shopping Clusters
- Produce: {template['produce']}
- Protein: {template['protein_list']}
- Pantry: {template['pantry']}
"""
