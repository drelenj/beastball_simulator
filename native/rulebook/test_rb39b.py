"""RB-3.9b PROVISIONAL (native-rb/3): pass release speed by distance (B-1) and lead by the real
flight time at that speed (E-1)."""
from dataclasses import replace
from math import hypot
import pytest
from native import cognition as C
from native.throw_speed import release_speed, flight_time, FLIGHT_TIME_S, MIN_SPEED_MPS, cap_for
from .test_rb36 import rb3
from .test_rb34 import live


@pytest.mark.parametrize('d', [2., 5., 8., 12., 20., 30., 60.])
def test_release_speed_by_distance(d):
    v = release_speed(d, 120.)
    assert v == round(min(cap_for(120.), max(MIN_SPEED_MPS, d / FLIGHT_TIME_S)), 3)
    assert MIN_SPEED_MPS <= v <= 60.


def test_short_passes_are_slower_and_capped_by_max_throw():
    assert release_speed(5., 120.) < release_speed(10., 120.) < release_speed(20., 120.) <= 60.
    assert release_speed(30., 40.) == 20.            # cap = min(80, 0.5 x max throw)
    assert release_speed(5., 120.) < 58.             # was: every pass at min(80, 0.5 x max)


@pytest.mark.parametrize('vel', [(0., 0.), (6., 0.), (0., -7.), (-5., 5.)])
def test_lead_equals_flight_time_at_the_chosen_speed(vel):
    aim, tf, speed = C.rb3_lead(40., 50., (52., 55.), vel, 120.)
    d = hypot(aim[0] - 40., aim[1] - 50.)
    assert speed == release_speed(d, 120.) and abs(tf - flight_time(d, speed)) < 1e-3
    assert abs(aim[0] - (52. + vel[0] * tf)) < 1e-3 and abs(aim[1] - (55. + vel[1] * tf)) < 1e-3


def test_play_window_pass_speeds_follow_distance():
    from native.run import run_match
    r, port = run_match(1, rb3().config, max_steps=2500, port_factory=lambda *x, **k: rb3())
    speeds = [i.speed for i in port.intents if i.kind == 'pass']
    assert speeds and len(set(speeds)) > 3 and min(speeds) >= MIN_SPEED_MPS
    assert sorted(speeds)[len(speeds) // 2] < 58.    # median was 58 m/s for every pass
    rel = [rw for rw in port.m.e.log if rw['event'] == 'release' and rw['data']['kind'] == 'pass']
    assert rel and all(abs(sum(c * c for c in rw['data']['velocity']) ** .5) <= 61. for rw in rel)
