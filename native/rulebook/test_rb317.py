from dataclasses import replace

import pytest

from native import cognition as C, cognition_rb3 as R
from native.roster import rb3_control_rosters
from native.run import run_match
from .config import RulebookConfigV3
from .handoff_block import block_impedance
from .port import RulebookPort


def fixture(enabled=True):
    rosters = rb3_control_rosters()
    cfg = RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A', 'B')),
                           rb3_handoff_block_enabled=enabled)
    return RulebookPort(1, cfg, rosters=rosters), rosters


def live():
    port, _ = fixture()
    s = port.m.s
    s.phase, s.now, s.restart, s.owner = port.types.Phase.LIVE, 60000, None, 'A'
    port.m.e.hunt_cleared = True
    for p in s.players.values():
        if p.role != 'archer':
            p.x, p.y = 80., 90.
            p.target = (p.x, p.y)
    giver, receiver, defender = (s.players[pid] for pid in ('A:0', 'A:1', 'B:0'))
    giver.x, giver.y = 50., 50.
    receiver.x, receiver.y = 50. + giver.a.reach + receiver.a.reach, 50.
    s.ball = port.types.Ball(mode=port.types.BallMode.CONTROLLED, carrier=giver.id,
                             x=giver.x, y=giver.y, z=giver.hand_height,
                             control_time=s.now, scoring=True)
    port.m.e.possession.pp = port.m.e.possession.tc = 'A'
    return port, giver, receiver, defender


def command(port, actor, kind, target, aim=None):
    now = port.m.s.now
    return port.submit(C.ActionIntent(f'{actor.id}/{kind}/{now}', 'forced', actor.id, kind,
                                      target.id, aim, None, None, now))


def handoff(port, giver, receiver):
    cmd = command(port, giver, 'handoff', receiver)['command']
    assert cmd.release_ms - port.m.s.now == 150
    port.m.s.now = cmd.release_ms - 1
    port.ball_motor()
    assert port.m.s.ball.carrier == giver.id
    port.m.s.now += 1
    port.ball_motor()
    return port.outcomes[-1].status


def test_handoff_at_reach_changes_the_carrier_without_flight_or_pass():
    p, giver, receiver, _ = live()
    assert handoff(p, giver, receiver) == 'handoff_complete'
    assert p.m.s.ball.carrier == receiver.id
    assert p.m.s.ball.mode == p.types.BallMode.CONTROLLED
    assert p.m.e.possession.tc == 'A'
    assert not [event for event in p.m.e.log if event['event'] == 'release']
    assert [event['event'] for event in p.m.e.log if event['event'].startswith('handoff_')] == [
        'handoff_start', 'handoff_complete']


def test_execution_rechecks_reach_and_does_not_drop_the_ball_for_a_missing_receiver():
    p, giver, receiver, _ = live()
    cmd = command(p, giver, 'handoff', receiver)['command']
    receiver.x += .2
    p.m.s.now = cmd.release_ms
    p.ball_motor()
    assert p.outcomes[-1].status == 'rejected_out_of_reach'
    assert p.m.s.ball.carrier == giver.id


def test_large_hand_speed_mismatch_fumbles_at_the_exchange_point():
    p, giver, receiver, _ = live()
    giver.vx, receiver.vx = -44.704, 44.704
    receiver.a.catching = .4
    assert handoff(p, giver, receiver) == 'handoff_fumble'
    ball = p.m.s.ball
    assert ball.carrier is None and ball.mode == p.types.BallMode.LOOSE
    assert ball.x == pytest.approx((giver.x + receiver.x) / 2)
    assert p.m.e.possession.pp == 'A' and p.m.e.possession.tc is None


def test_no_handoff_during_snap_hold():
    p, giver, receiver, _ = live()
    p.m.e.rb310_hold = {'active': True}
    assert command(p, giver, 'handoff', receiver)['reason'] == 'snap_hold'


def aligned_block():
    p, giver, blocker, target = live()
    giver.x, giver.y = 30., 60.
    target.x, target.y = 50., 50.
    blocker.x, blocker.y = 50. + blocker.radius + target.radius, 50.
    target.target = (70., 50.)
    return p, blocker, target


@pytest.mark.parametrize('guard,reason', [('hold', 'snap_hold'), ('frozen', 'frozen_obstacle'),
                                          ('thaw', 'immune_contact'), ('carrier', 'carrier')])
def test_block_admission_protections(guard, reason):
    p, blocker, target = aligned_block()
    if guard == 'hold':
        p.m.e.rb310_hold = {'active': True}
    elif guard == 'frozen':
        target.freeze_until = p.m.s.now + 200
    elif guard == 'thaw':
        target.freeze_until = p.m.s.now - 200
    elif guard == 'carrier':
        p.m.s.ball.carrier = target.id
    assert command(p, blocker, 'block', target, (60., 50.))['reason'] == reason
    p.rb317.update_blocks()
    assert not p.rb317.engaged


def test_legal_contact_slows_positive_propulsion_but_allows_escape():
    p, blocker, target = aligned_block()
    assert command(p, blocker, 'block', target, (60., 50.))['status'] == 'accepted'
    p.rb317.update_blocks()
    assert (blocker.id, target.id) in p.rb317.engaged
    # Stub only the ordinary propulsion solver to isolate the wrapper's
    # effect from avoidance, collisions and changes in the contact normal.
    p.rb317.drive = lambda q, dt, live, car: setattr(q, 'vx', q.vx + (1 if q.target[0] > q.x else -1))
    p.rb317.drive_with_blocks(target, .1, True, None)
    assert target.vx == pytest.approx(.5)
    assert not p.m.c3_holds
    target.target = (30., 50.)
    target.vx = 0.
    p.rb317.drive_with_blocks(target, .1, True, None)
    assert target.vx == -1.
    p.m.s.live_ms += 50
    p.rb317.update_blocks()
    assert p.m.e.log[-1]['event'] == 'block_shed'
    assert p.m.e.log[-1]['data']['duration_ms'] == 50


def test_lighter_and_weaker_target_is_slowed_more():
    _, blocker, target = aligned_block()
    base = block_impedance(blocker, target, 1.)
    target.a.mass *= 2
    assert block_impedance(blocker, target, 1.) < base
    heavier = block_impedance(blocker, target, 1.)
    target.a.strength *= 1.2
    assert block_impedance(blocker, target, 1.) < heavier
    assert block_impedance(blocker, target, 0.) == 0.


def test_enabled_window_replays_deterministically():
    p, rosters = fixture()
    a, _ = run_match(1, p.config, max_steps=600, rosters=rosters, port_factory=RulebookPort)
    b, _ = run_match(1, p.config, max_steps=600, rosters=rosters, port_factory=RulebookPort)
    assert (a['trace_hash'], a['state_hash']) == (b['trace_hash'], b['state_hash'])


def test_flag_off_omits_the_key_from_the_baseline_record():
    p, _ = fixture(False)
    assert 'rb3_handoff_block_enabled' not in p.config.record()
    assert not hasattr(p, 'rb317')


def test_belief_based_minimal_hooks():
    p, giver, receiver, target = live()
    p.capture(p.m.s.now)
    p.m.s.now += p.config.latency_ms
    view, belief = p.view(giver.id, p.m.s.now)
    teammate = C.Track(receiver.id, 'A', 'field', giver.x + view.attack_sign, giver.y,
                       4. * view.attack_sign, 0., view.delivered_ms)
    assert any(o[:2] == ('handoff', receiver.id) for o in R.carrier_options(view, [teammate], None))
    off = replace(view, rb3_handoff_block_enabled=False)
    assert not any(o[0] == 'handoff' for o in R.carrier_options(off, [teammate], None))
    ball_carrier = C.Track(giver.id, 'A', 'field', giver.x, giver.y, 0., 0., view.delivered_ms)
    closing = C.Track(target.id, 'B', 'field', giver.x + 5., giver.y, -3., 0., view.delivered_ms)
    view = replace(view, athlete=receiver.id, holds_ball=False, x=giver.x + 2. * view.attack_sign, y=giver.y)   # RB-3.19 B2: the blocker is ahead of the carrier
    belief = replace(belief, tracks=(ball_carrier, closing))
    intent = C.ActionIntent('forced', 'forced', receiver.id, 'support', None,
                             (40., 40.), None, None, view.delivered_ms)
    record = {'believed_carrier': [giver.id, 'A']}
    chosen, _ = R.choose_block(view, belief, intent, record)
    assert (chosen.kind, chosen.target, chosen.aim) == ('block', target.id, (giver.x, giver.y))
