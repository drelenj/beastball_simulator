import pytest

from .scoring_audit import keeper_case, lab, new_flight, speeds
from b1.emergence_intents import KeeperIntent
from types import SimpleNamespace


@pytest.mark.parametrize('carrying', [False, True])
def test_unopposed_run_reaches_mapped_speed(carrying):
    run = speeds(carrying)
    assert run['speeds'] == pytest.approx([8.75, 17.5, 26.25, 31.2928])
    assert run['cap'] == pytest.approx(run['maximum'])


@pytest.mark.parametrize('awareness', [.5, .7, .9])
def test_a_forced_early_save_cannot_launch_at_a_short_corner_shot(awareness):
    result = keeper_case(awareness, 2.4, .4, force_intent=True)
    assert result['outcome'] == 'goal'
    assert not result['launched']
    assert result['displaced_y_m'] == 0


@pytest.mark.parametrize('moving', [False, True])
def test_keeper_admission_waits_and_uses_matching_body_parameters(monkeypatch, moving):
    from native import port as native_port

    port, keeper = lab('keeper')
    state = port.m.s
    keeper.vy = 2. if moving else 0.
    tick = state.now
    new_flight(port, (12., 50., 1.5), (-25., 0., 0.))
    course = ((0., 12., 50., 1.5), (.4, 2., 50., 1.5), (.48, 0., 50., 1.5))
    intent = KeeperIntent('test', keeper.id, 'save', tick, 'forced', course=course)
    port.keeper_intents[keeper.id] = SimpleNamespace(auxiliary=intent)
    keeper.native_keeper_course_ms = tick
    calls = []

    def inspect(intent, body, **kwargs):
        calls.append((intent, kwargs))
        return SimpleNamespace(kind='rejected')

    monkeypatch.setattr(native_port, 'plan_keeper_motor', inspect)
    port.keeper_motor({})
    reaction = 176 + 100 * moving
    state.now = tick + reaction - 1
    port.keeper_motor({})
    assert calls == []
    state.now += 1
    port.keeper_motor({})
    offered, kwargs = calls.pop()
    assert offered.course[0][0] == pytest.approx(.4 - reaction / 1000)
    assert kwargs['reach_factor'] == pytest.approx(.9)
    assert kwargs['extension_fraction'] == .3
    assert kwargs['pushoff_fraction'] == .4
    assert kwargs['launch_min_s'] == .1
    assert kwargs['dive_hand_fraction'] == .3
    assert kwargs['match_lean']
    state.ball.version += 1
    state.ball.course_time = state.now
    state.now += 400
    port.keeper_motor({})
    assert calls == []


def test_keeper_reaction_restarts_when_restart_reuses_ball_version():
    port, keeper = lab('keeper')
    state = port.m.s
    first = new_flight(port, (12., 50., 1.5), (-25., 0., 0.))
    port.keeper_motor({})
    state.now += 300
    second = new_flight(port, (20., 50., 1.5), (-25., 0., 0.))
    assert second.version == first.version
    port.keeper_motor({})
    _, started, ready = keeper.native_keeper_flight
    assert started == state.now
    assert ready - started == pytest.approx(176)
