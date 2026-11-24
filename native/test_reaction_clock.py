from math import ceil

import pytest

from .run import reaction_deadline


@pytest.mark.parametrize('interval', [440, 460, 480, 500, 520, 540, 560, 483.4])
def test_decision_deadline_carries_fraction_and_tick_overshoot(interval):
    deadline = tick = 0
    for _ in range(10_000):
        deadline = reaction_deadline(tick, deadline, interval)
        tick = 100 * ceil((deadline - 1e-6) / 100)
    assert deadline == pytest.approx(10_000 * interval)
    assert abs(tick / 10_000 - interval) <= .01


def test_frozen_actor_does_not_receive_backlogged_decisions():
    assert reaction_deadline(10_000, 100, 500) == 10_500
    assert reaction_deadline(1_600, None, 500) == 2_100
