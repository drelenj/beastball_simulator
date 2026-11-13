"""Tests for EMERGENCE-1 metrics and read-out.  python -m pytest -q b1/emergence/test_metrics.py"""
import inspect
import json

import pytest

from b1.emergence.metrics import MetricsCollector
from b1.emergence.readout import aggregate, paired_summary, render, sign_test_p


def test_sign_test_known_values():
    assert sign_test_p(5, 0) == 0.0625
    assert sign_test_p(8, 2) == 0.109375
    assert sign_test_p(0, 0) == 1.0
    assert sign_test_p(3, 3) == 1.0
    assert sign_test_p(0, 6) == sign_test_p(6, 0) == 0.03125


def _row(seed, la, lb, sa, sb, status='final'):
    return {'seed': seed, 'period_s': 45, 'label_A': la, 'label_B': lb, 'score': {'A': sa, 'B': sb},
            'winner': 'A' if sa > sb else 'B' if sb > sa else None, 'status': status, 'trace_hash': 'x',
            'metrics': {'A': {'width': 30., 'pass_network': {'1>2': 2}, 'decisions_by_kind': {'pass': 1}},
                        'B': {'width': 50., 'pass_network': {'3>4': 1}, 'decisions_by_kind': {'carry': 2}}}}


def test_paired_summary_with_side_swap():
    rows = [_row(1, 'baseline', 'evo', 0, 3), _row(1, 'evo', 'baseline', 2, 3),     # evo +3 and -1 -> +2 (win)
            _row(2, 'baseline', 'evo', 4, 1), _row(2, 'evo', 'baseline', 1, 1),     # -3 and 0 -> loss
            _row(3, 'baseline', 'evo', 2, 3), _row(3, 'evo', 'baseline', 0, 1),     # +1 and -1 -> tie
            _row(4, 'baseline', 'evo', 0, 6),                                       # single side -> win
            _row(5, 'baseline', 'evo', 0, 9, status='crashed'),                     # ignored
            _row(6, 'evo', 'evo', 0, 9)]                                            # not this pairing
    ps = paired_summary(rows, 'baseline', 'evo')
    assert (ps['pairs'], ps['both_sides_pairs']) == (4, 3)
    assert (ps['b_pair_wins'], ps['pair_draws'], ps['b_pair_losses']) == (2, 1, 1)
    assert ps['mean_goal_diff_per_pair'] == round((2 - 3 + 0 + 6) / 4, 3)
    assert ps['sign_test_p'] == 1.0
    assert (ps['b_match_wins'], ps['match_draws'], ps['b_match_losses']) == (3, 1, 3)
    # reversing the labels reverses the result
    rev = paired_summary(rows, 'evo', 'baseline')
    assert (rev['b_pair_wins'], rev['b_pair_losses']) == (1, 2)


def test_aggregate_is_by_label_not_side_and_render_is_cautious():
    rows = [_row(1, 'baseline', 'evo', 0, 1), _row(1, 'evo', 'baseline', 1, 0)]
    means, net, kinds, n = aggregate(rows)
    assert means['baseline']['width'] == 40. and means['evo']['width'] == 40.     # each label played both sides
    assert n == {'baseline': 2, 'evo': 2}
    text = render(rows)
    assert 'no result difference beyond noise was shown' in text
    assert 'descriptive only; no significance tested for metrics' in text


def _hooks_present():
    from b1.matchport import run_match
    return {'on_decision', 'on_step'} <= set(inspect.signature(run_match).parameters)


def test_collector_does_not_change_the_match_and_output_is_json_safe():
    if not _hooks_present():
        pytest.skip('b1.matchport.run_match has no on_decision/on_step hooks yet')
    from b1.matchport import run_match
    base = run_match(1, None, 15000, False)[0]
    c = MetricsCollector()
    r, port = run_match(1, None, 15000, False, on_decision=c.on_decision, on_step=c.on_step)
    assert (r['trace_hash'], r['state_hash']) == (base['trace_hash'], base['state_hash'])
    m = c.finalize(port)
    assert set(m) == {'A', 'B', 'match'}
    assert json.loads(json.dumps(m)) == m
    assert m['match']['metric_errors'] == []
    assert m['match']['samples'] >= 10
    for t in ('A', 'B'):
        assert m[t]['width'] is not None and m[t]['width'] > 0
        assert sum(m[t]['decisions_by_kind'].values()) > 100
    assert abs(m['A']['possession_share'] + m['B']['possession_share'] + m['match']['possession_none_share'] - 1.) < .01


def test_collector_without_hooks_by_manual_drive():
    """Works even before the hooks land: finalize on a finished port with no samples."""
    from b1.matchport import run_match
    r, port = run_match(1, None, 8000, False)
    c = MetricsCollector()
    c.on_step(port)
    m = c.finalize(port)
    assert json.loads(json.dumps(m)) == m and m['match']['metric_errors'] == []
