#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from handler import handle


def test_busy_nights_and_high_protein_context_render_meal_board():
    output = handle('We have busy Tuesday and Thursday nights and want high protein dinners this week')
    assert '# Weekly Feast Plan' in output
    assert '- Busy nights: Tuesday, Thursday' in output
    assert 'Greek yogurt' in output or 'Chicken' in output


def test_dict_input_preserves_budget_and_dietary_notes():
    output = handle({
        'busy_nights': ['Tuesday', 'Thursday'],
        'dietary_notes': 'Vegetarian',
        'budget_notes': 'Keep it moderate'
    })
    assert '- Budget notes: Keep it moderate' in output
    assert '- Dietary notes: Vegetarian' in output
    assert 'Tofu' in output or 'beans' in output.lower()


def test_output_contains_backup_and_shopping_clusters():
    output = handle('Need easy dinners for a family with a chaotic Wednesday')
    assert '- Backup meal:' in output
    assert '## Shopping Clusters' in output


if __name__ == '__main__':
    for name, fn in list(globals().items()):
        if name.startswith('test_') and callable(fn):
            fn()
    print('All tests passed.')
