import pytest

from native.roster import rb3_control_rosters
from native.run import run_match
from .config import RulebookConfigV3
from .port import RulebookPort
from .test_rb317 import command


def fixture(moves=True, handoffs=False, radius=3.):
    rosters = rb3_control_rosters()
    cfg = RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A', 'B')),
                           rb3_carrier_moves_enabled=moves, rb3_handoff_block_enabled=handoffs,
                           carry_release_radius_m=radius)
    p = RulebookPort(1, cfg, rosters=rosters)
    s = p.m.s
    s.now, s.phase, s.restart, s.owner = 60000, p.types.Phase.LIVE, None, 'A'
    c, d = s.players['A:0'], s.players['B:0']
    for q in s.players.values():
        if q.role != 'archer':
            q.x, q.y, q.target = 70., 80., (70., 80.)
    c.x, c.y, c.facing = 50., 50., (s.attack_sign('A'), 0.)
    d.x, d.y, d.facing = c.x + s.attack_sign('A') * (c.radius + d.radius), 50., (-s.attack_sign('A'), 0.)
    s.ball = p.types.Ball(mode=p.types.BallMode.CONTROLLED, carrier=c.id, control_time=s.now,
                          last_touch='A', scoring=True)
    p.m.e.hunt_cleared = True
    p.m.e.possession.pp = p.m.e.possession.tc = 'A'
    p.m.e.follow_carrier()
    return p, rosters, c, d


@pytest.mark.parametrize('distance,points,carry', [(2.5, 5, True), (3., 2, False), (3.5, 2, False)])
def test_release_carry_radius(distance, points, carry):
    p, _, c, _ = fixture(moves=False)
    s, e = p.m.s, p.m.e
    sign, goal = s.attack_sign('A'), s.attack_goal('A')
    c.x = goal - sign * (distance + .35 + .35 * c.a.reach)
    assert e.release(c.id, (sign * 4., 0., 0.), 'shot')
    s.ball.x = goal + sign * (s.ball.radius + .001)
    assert e.goal('B', 50., 1.)
    result = next(x['data'] for x in e.log if x['event'] == 'goal')
    assert result['points'] == points and result.get('release_carry', False) == carry
    assert e.rb_bands['A']['carry_goals'] == int(carry)
    assert e.rb_bands['A']['under10_attempts'] == int(not carry)


def test_stretch_scores_while_ball_stays_in_hand():
    p, _, c, _ = fixture()
    m, s, e = p.m, p.m.s, p.m.e
    goal = s.attack_goal('A')
    c.x = goal - s.attack_sign('A') * 1.
    e.follow_carrier()
    assert not m.advance_ball(200, {})
    assert command(p, c, 'stretch', s.players['B:0'], (goal, 50.))['status'] == 'accepted'
    event, = [x for x in m.advance_ball(200, {}) if x.kind == 'goal']
    s.now += event.at
    e.dispatch(event)
    assert s.score['A'] == 5
    assert [r['event'] for r in e.log if r['event'].startswith('stretch_')] == ['stretch_start', 'stretch_goal']


def grip_step(p, carrier, defender, elapsed=.1):
    m = p.m
    m.native_wrap_authorized = lambda *args: True
    return m.c3_holds_kick([carrier, defender], carrier, [(defender, 3.)],
                           {defender.id: True}, elapsed, 0., m.s.now)


@pytest.mark.parametrize('stretch,expected', [(False, False), (True, True)])
def test_stretch_exposes_the_ball_in_paired_strip_scenario(stretch, expected):
    p, _, c, d = fixture()
    s = p.m.s
    goal = s.attack_goal('A')
    c.x = goal - s.attack_sign('A') * 1.5
    d.x = c.x + s.attack_sign('A') * .5
    if stretch:
        assert command(p, c, 'stretch', d, (goal, 50.))['status'] == 'accepted'
    s.now += 200
    class ContactRng:
        def random(self):
            return .01  # Above ordinary 100 ms hazard, below full stretch hazard.
    p.m.rng['contact'] = ContactRng()
    _, event = grip_step(p, c, d)
    assert bool(event and event[0] == 'strip') == expected


def test_stiff_arm_delays_the_actual_c3_grip():
    p, _, c, d = fixture()
    key = d.id, c.id
    p.m.c3_no_strip = True
    grip_step(p, c, d)
    assert p.m.c3_holds[key]['g'] > 0
    q, _, actor, target = fixture()
    q.m.c3_no_strip = True
    assert command(q, actor, 'stiff_arm', target)['status'] == 'accepted'
    q.rb318.update()
    grip_step(q, actor, target)
    assert key not in q.m.c3_holds
    assert (actor.id, target.id) not in q.m.c3_holds
    q.m.s.now += 300
    grip_step(q, actor, target)
    assert key in q.m.c3_holds


@pytest.mark.parametrize('heavy,outcome', [(False, 'truck_broken'), (True, 'truck_stopped')])
def test_truck_is_resolved_by_real_c3_impulse(heavy, outcome):
    p, _, c, d = fixture()
    m, s = p.m, p.m.s
    sign = s.attack_sign('A')
    c.vx, d.vx = 4. * sign, -2. * sign
    d.a.mass, d.a.strength = (600., .95) if heavy else (140., .45)
    d.x = c.x + sign * (c.radius + d.radius)
    assert command(p, c, 'truck', d, (d.x, d.y))['status'] == 'accepted'
    key = d.id, c.id
    m.c3_no_strip = True
    grip_step(p, c, d, elapsed=.01)
    assert key in m.c3_holds
    m.c3_contact_kick([(c, d, c.radius + d.radius)], [c, d], c, 0., s.now, 1e-6,
                      m.assume['contact_restitution'], 1.)
    assert any(ev['event'] == outcome for ev in m.e.log)
    if not heavy:
        assert 0 < sign * c.vx < 4.
        assert c.posture == 'upright' and key not in m.c3_holds
    else:
        assert key in m.c3_holds
    assert (c.id, d.id) not in m.c3_holds


@pytest.mark.parametrize('kind', ['stretch', 'stiff_arm', 'truck'])
def test_moves_are_rejected_during_snap_hold(kind):
    p, _, c, d = fixture()
    p.m.e.rb310_hold = {'active': True}
    assert command(p, c, kind, d)['reason'] == 'snap_hold'


def test_own_zone_handoff_completes_then_gets_pass_restart():
    p, _, c, _ = fixture(handoffs=True)
    s, e = p.m.s, p.m.e
    receiver = s.players['A:1']
    sign = s.attack_sign('A')
    c.x = s.ends['A'] + sign * 20.5
    receiver.x, receiver.y = s.ends['A'] + sign * 19., 50.
    e.follow_carrier()
    cmd = command(p, c, 'handoff', receiver)['command']
    s.now = cmd.release_ms
    p.ball_motor()
    assert any(r['event'] == 'handoff_complete' and r['carrier'] == receiver.id for r in e.log)
    assert s.restart.team == 'B' and s.restart.reason == 'ZR-T'
    assert not any(r['event'] == 'release' for r in e.log)


def test_enabled_window_is_deterministic():
    p, rosters, *_ = fixture(handoffs=True)
    a, _ = run_match(1, p.config, max_steps=500, rosters=rosters, port_factory=RulebookPort)
    b, _ = run_match(1, p.config, max_steps=500, rosters=rosters, port_factory=RulebookPort)
    assert (a['trace_hash'], a['state_hash']) == (b['trace_hash'], b['state_hash'])
