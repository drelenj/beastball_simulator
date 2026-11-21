from dataclasses import asdict

import pytest

from native.cognition import ActionIntent
from .scoring_audit import catch_case, lab


def test_control_separates_arm_reach_from_standing_reach():
    port, player = lab('field')
    assert player.a.height == 2.39
    assert player.a.reach == pytest.approx(.529 * 2.39)
    assert player.a.standing_reach_m == 3.05
    assert port.m.c4c_reach(player) == pytest.approx(.9 * .529 * 2.39)


@pytest.mark.parametrize('kind', ['pass', 'shoot'])
@pytest.mark.parametrize('handling,delay', [(.48, 278), (.70, 250), (.86, 230)])
def test_readback_matches_the_actual_unrestrained_release(kind, handling, delay):
    port, player = lab('field')
    state = port.m.s
    player.a.ball_handling = handling
    player.x, player.y, player.target = 45., 50., (45., 50.)
    state.ball = port.types.Ball(mode=port.types.BallMode.CONTROLLED, carrier=player.id,
                                x=45., y=50., z=player.hand_height, control_time=state.now)
    state.owner = player.team
    port.capture(state.now)
    state.now += port.config.latency_ms
    view, belief = port.view(player.id, state.now)
    assert view.own_release_ms == view.pass_release_ms == delay
    rebuilt, _ = port.view_from_json({'view': asdict(view), 'belief': asdict(belief)})
    assert rebuilt.own_release_ms == rebuilt.pass_release_ms == delay

    intent = ActionIntent('audit/release', 'audit/decision', player.id, kind,
                          None, (65., 50.), None, None, state.now, speed=30.)
    start = state.now
    admission = port.submit(intent)
    assert admission['status'] == 'accepted'
    assert admission['command'].release_ms == start + view.own_release_ms
    for _ in range(10):
        port.step()
        releases = [event for event in port.m.e.log if event['event'] == 'release']
        if releases:
            break
    assert len(releases) == 1
    assert releases[0]['t_ms'] == start + delay


@pytest.mark.parametrize('speed', [22., 58.])
def test_primed_field_hands_cannot_reach_two_or_three_metres(speed):
    assert catch_case('field', speed, 1., hands=True)
    assert not catch_case('field', speed, 2., hands=True)
    assert not catch_case('field', speed, 3., hands=True)
