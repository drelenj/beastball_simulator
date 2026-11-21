"""RB-3.19 PROVISIONAL, native-rb/3: Part A (keep the ball in play) and Part B (handoff / block / carrier-move tactics)."""
from dataclasses import replace
from math import hypot
import pytest
from native import cognition as C
from native import cognition_rb3 as R
from native import cognition_v3 as V
from .test_rb36 import rb3, defender_view, T
from .test_rb34 import live
from .test_rb312 import carrier_scene, opts
from .test_rb314 import scene as scene314


# ---------------------------------------------------------------- A1 toss speed and lane
def toss_view(rb, opp=None, mates=((50., 13.),)):
    p = rb3(); s, e, a, t = live(p); v, b = defender_view(p, 'A:0')
    tr = tuple(T(f'A:{i + 1}', 'A', x, y, v.delivered_ms) for i, (x, y) in enumerate(mates))
    if opp: tr += (T('B:0', 'B', opp[0], opp[1], v.delivered_ms),)
    v = replace(v, x=50., y=1., tracks=tr, rb319=rb, holds_ball=False, signals=replace(v.signals, phase='dead'),
                restart=('r', 'toss', 'A', 50., 1., 50., 1., 'A:0', None, None, v.delivered_ms - 9000, True))
    return v, replace(b, tracks=tr, own_feedback=(), last_ball=None)


def test_a1_toss_to_a_target_12_m_away_uses_distance_speed_not_the_old_fixed_speed():
    v, b = toss_view('A1'); i, _ = V.restart_decide(v, b)
    assert i.kind == 'restart_pass' and abs(i.speed - 30.) < 1e-6
    v0, b0 = toss_view(''); i0, _ = V.restart_decide(v0, b0)                 # control: the old fixed speed
    assert i0.speed > 45.


def test_a1_toss_with_no_safe_target_throws_to_space_at_distance_speed():
    v, b = toss_view('A1', opp=(50., 8.))                                     # a defender standing in the lane (and within reach of the taker)
    i, r = V.restart_decide(v, b)
    assert r['path'] == 'restart_taker_space_placeholder' and abs(i.speed - 8. / .4) < 1e-6 and i.target is None
    v0, b0 = toss_view('', opp=(50., 8.)); i0, r0 = V.restart_decide(v0, b0)   # control: the old rule still throws at the covered teammate
    assert i0.target == 'A:1'


def toss_flight(speed):
    p = rb3(); s, e, a, t = live(p); T_ = p.types; s.restart = None; e.rb_period_start_open = False
    for i, q in enumerate(q for q in s.players.values() if q.role != 'archer'):
        q.x, q.y = 5. + (i % 6) * 2, 5. + (i // 6) * 1.5; q.vx = q.vy = 0.; q.target = (q.x, q.y); p.move[q.id] = (q.x, q.y)
    ans = p.geom.launch_for((50., 1., 1.6), (50., 13., 1.6), speed, 9.81, .015)
    s.owner = 'A'; e.possession.pp = 'A'; e.possession.tc = 'A'; e.rb.possession = 'A'
    s.ball = T_.Ball(mode=T_.BallMode.PASS, x=50., y=1., z=1.6, carrier=None, control_time=0, scoring=True, last_touch='A', vx=ans[0][0], vy=ans[0][1], vz=ans[0][2])
    n0 = len(e.log); e.native_sync()
    for k in range(400):
        p.step()
        if any(x['event'] == 'boundary' for x in e.log[n0:]): return 'out'
        n0 = len(e.log)
    return 'in'


def test_a1_a_missed_toss_stays_in_the_field_at_distance_speed_and_leaves_at_the_old_speed():
    assert toss_flight(30.) == 'in' and toss_flight(50.3) == 'out'


# ---------------------------------------------------------------- A2 boundary awareness
def test_a2_carry_and_escape_aims_stay_2_m_inside_every_line_and_the_goal_mouth_is_exempt():
    for rb, ok in (('A2', True), ('', False)):
        v, tr, _ = carrier_scene(me=(50., 3.), opps=[(58., 3.)], mates=[])
        tr = tuple(replace(t, vx=-9.) if t.team == 'B' else t for t in tr)
        v = replace(v, tracks=tr, rb319=rb)
        aims = [r[2] for r in opts(v, tr, aim=(65., 0.6)) if r[0] == 'carry']
        assert aims and (all(2. <= a[1] <= 98. and 2. <= a[0] <= 98. for a in aims) is ok)
    assert R.keep_in(v, (100., 50.)) == (100., 50.) and R.keep_in(v, (100., 60.)) == (98., 60.)   # goal mouth exempt, end line elsewhere not
    assert R.keep_in(v, (99., 0.)) == (98., 2.)


def test_a2_applies_to_a_truck_aim_through_adjust():
    v, tr, _ = carrier_scene(me=(50., 3.), opps=[(51., 0.5)], mates=[])
    v = replace(v, tracks=tr, rb319='A2')
    pp = rb3(); s, e, a, t = live(pp); v0, b0 = defender_view(pp, 'A:0')
    i = C.ActionIntent('i', 'd', v.athlete, 'truck', 'B:0', (51., 0.5), None, None, v.delivered_ms)
    assert R.keep_in(v, i.aim)[1] == 2.


# ---------------------------------------------------------------- A3 missed-ball pursuit
def pursuit_view(me, rb, mates):
    p = rb3(); s, e, a, t = live(p); v, b = defender_view(p, 'A:0')
    tr = (T(C.BALL, 'ball', 60., 50., v.delivered_ms),) + tuple(T(f'A:{i + 1}', 'A', x, y, v.delivered_ms) for i, (x, y) in enumerate(mates))
    tr = tuple(replace(t_, vx=30., vy=0.) if t_.entity == C.BALL else t_ for t_ in tr)
    sig = replace(v.signals, phase='live', passive_team='A', ball_status='loose')
    v = replace(v, x=me[0], y=me[1], tracks=tr, rb319=rb, holds_ball=False, signals=sig, restart=None, pending_command_id=None)
    b = replace(b, tracks=tr, own_feedback=(), last_ball=None)
    intent = C.ActionIntent('i', 'd', v.athlete, 'scan', None, (v.x, v.y), None, None, v.delivered_ms)
    return v, b, intent


def test_a3_the_two_nearest_teammates_pursue_a_loose_ball_heading_out_and_the_third_does_not():
    mates = [(80., 52.), (75., 40.), (20., 90.)]                              # three teammates besides me at (30, 30)
    got = {}
    for name, me in (('near', (70., 50.)), ('second', (66., 44.)), ('far', (30., 30.))):
        v, b, i = pursuit_view(me, 'A3', mates[:2] if name != 'far' else mates)
        i2, rec = R.missed_ball_pursuit(v, b, i, {})
        got[name] = i2.kind
    assert got['near'] == 'pursue' and got['far'] == 'scan'
    v, b, i = pursuit_view((70., 50.), '', mates[:2])                          # control: step disabled
    assert R.missed_ball_pursuit(v, b, i, {})[0].kind == 'scan'
    v, b, i = pursuit_view((70., 50.), 'A3', mates[:2]); v = replace(v, signals=replace(v.signals, passive_team='B'))
    assert R.missed_ball_pursuit(v, b, i, {})[0].kind == 'scan'                # a loose ball of the other team's possession is not this rule


# ---------------------------------------------------------------- A4 pass depth safety
def test_a4_a_corner_pass_that_would_exit_within_one_second_beyond_the_receiver_is_not_chosen():
    mates = [(94., 80.), (80., 40.)]
    for rb, offered in (('A4', False), ('', True)):
        v, tr, _ = carrier_scene(me=(70., 62.), opps=[(70., 90.)], mates=mates, held_ms=2000)
        v = replace(v, rb319=rb)
        got = {r[1] for r in opts(v, tr) if r[0] == 'pass'}
        assert ('A:1' in got) is offered
    assert R.pass_exit_s(v, T('A:1', 'A', 94., 80., 0), 40.) < R.PASS_EXIT_MIN_S
    assert R.pass_exit_s(v, T('A:2', 'A', 80., 40., 0), 40.) > 0


# ---------------------------------------------------------------- Part B
def tactics_scene(me=(50., 50.), opps=(), mates=(), oppvel=(0., 0.), matevel=(0., 0.), heights=None, **kw):
    v, tr, _ = carrier_scene(me=me, opps=opps, mates=mates, **kw)
    tr = tuple(replace(t, vx=oppvel[0], vy=oppvel[1]) if t.team == 'B' else replace(t, vx=matevel[0], vy=matevel[1]) for t in tr)
    heights = heights or {}
    br = tuple((t.entity, 3.05) for t in tr)
    bh = tuple((t.entity, heights.get(t.entity, 2.39)) for t in tr)
    return replace(v, tracks=tr, rb3_handoff_block_enabled=True, rb3_carrier_moves_enabled=True, body_reach=br, body_height=bh), tr


def handoffs(v, tr): return [r for r in opts(v, tr) if r[0] == 'handoff']


def test_b1_handoff_to_a_faster_teammate_unpressured_and_not_to_a_slower_one():
    v, tr = tactics_scene(opps=[(50., 90.)], mates=[(53., 52.)], matevel=(6., 0.))              # 6 m/s faster toward the goal
    assert [r[1] for r in handoffs(v, tr)] == ['A:1']
    vs, trs = tactics_scene(opps=[(50., 90.)], mates=[(53., 52.)], matevel=(1., 0.))             # control: only 1 m/s faster
    assert not handoffs(vs, trs)
    vb, trb = tactics_scene(opps=[(50., 90.)], mates=[(47., 52.)], matevel=(6., 0.))             # control: faster but BACKWARD while unpressured
    assert not handoffs(vb, trb)


def test_b1_pressured_carrier_may_hand_off_even_backward_and_the_receiver_must_be_within_reach():
    # RB-3.20b: the backward receiver must also be clearly freer (least time-to-contact >= mine + 0.5 s)
    v, tr = tactics_scene(opps=[(50., 57.)], oppvel=(0., -6.), mates=[(48., 47.)])
    assert R.is_pressured(v, [t for t in tr if t.team == 'B']) and [r[1] for r in handoffs(v, tr)] == ['A:1']
    vf, trf = tactics_scene(opps=[(50., 57.)], oppvel=(0., -6.), mates=[(40., 45.)])            # control: 10 m away, out of reach
    assert not handoffs(vf, trf)


def block_view(carrier_xy, me_xy, defenders, rb=True):
    p = rb3(); s, e, a, t = live(p); v, b = defender_view(p, 'A:0')
    tr = (T('A:9', 'A', carrier_xy[0], carrier_xy[1], v.delivered_ms),) + tuple(
        replace(T(f'B:{i}', 'B', x, y, v.delivered_ms), vx=vx, vy=vy) for i, (x, y, vx, vy) in enumerate(defenders))
    sig = replace(v.signals, phase='live', passive_team='A')
    v = replace(v, x=me_xy[0], y=me_xy[1], tracks=tr, holds_ball=False, signals=sig, restart=None, pending_command_id=None,
                rb3_handoff_block_enabled=rb, body_reach=tuple((t_.entity, 3.05) for t_ in tr))
    b = replace(b, tracks=tr, own_feedback=(), last_ball=None)
    return v, b, C.ActionIntent('i', 'd', v.athlete, 'support', None, (v.x, v.y), None, None, v.delivered_ms), {'believed_carrier': ['A:9', 'A']}


def test_b2_a_block_engages_the_closing_defender_and_not_a_far_one():
    v, b, i, rec = block_view((50., 50.), (54., 50.), [(60., 50., -9., 0.)])
    out = R.choose_block(v, b, i, rec)[0]; assert out.kind == 'block' and out.target == 'B:0'
    v, b, i, rec = block_view((50., 50.), (54., 50.), [(64., 50., -9., 0.)])                   # 14 m from the carrier: not blocked
    assert R.choose_block(v, b, i, rec)[0].kind == 'support'
    v, b, i, rec = block_view((50., 50.), (46., 50.), [(60., 50., -9., 0.)])                   # I am BEHIND the carrier: not a blocker
    assert R.choose_block(v, b, i, rec)[0].kind == 'support'
    v, b, i, rec = block_view((50., 50.), (54., 50.), [(60., 50., -9., 0.)], rb=False)         # control: tactics off
    assert R.choose_block(v, b, i, rec)[0].kind == 'support'


def test_b2_at_most_two_blockers_and_each_takes_the_defender_he_reaches_first():
    defs = [(58., 46., -9., 0.), (58., 54., -9., 0.)]
    kinds = {}
    for me in ((53., 46.), (53., 54.)):
        v, b, i, rec = block_view((50., 50.), me, defs)
        out = R.choose_block(v, b, i, rec)[0]; kinds[me] = (out.kind, out.target)
    assert kinds[(53., 46.)] == ('block', 'B:0') and kinds[(53., 54.)] == ('block', 'B:1')


def move_scene(height, speed=8., oppspeed=-5., gap=1.6, enabled=True, me=(50., 50.)):
    v, tr = tactics_scene(me=me, opps=[(me[0] + gap, me[1])], oppvel=(oppspeed, 0.), heights={'B:0': height})
    v = replace(v, body=replace(v.body, vx=speed, vy=0.), rb3_carrier_moves_enabled=enabled)
    b = replace(defender_view(rb3(), 'A:0')[1], tracks=tr, own_feedback=(), last_ball=None)
    return v, b


def test_b3_truck_against_a_lighter_tackler_and_stiff_arm_against_a_heavier_one_in_front():
    i0 = C.ActionIntent('i', 'd', 'A:0', 'carry', None, (100., 50.), None, None, 0)
    out = R.choose_carrier_move(*move_scene(1.9), i0, {})[0]; assert out.kind == 'truck' and out.target == 'B:0'
    out = R.choose_carrier_move(*move_scene(2.9), i0, {})[0]; assert out.kind == 'stiff_arm'
    assert R.choose_carrier_move(*move_scene(1.9, enabled=False), i0, {})[0].kind == 'carry'       # control: flag off
    assert R.choose_carrier_move(*move_scene(1.9, gap=14.), i0, {})[0].kind == 'carry'             # control: tackler not within 0.5 s
    v, b = move_scene(1.9); v = replace(v, body=replace(v.body, vx=-8.))
    assert R.choose_carrier_move(v, b, i0, {})[0].kind != 'truck'                                    # not facing the goal: no truck


def test_b3_stretch_from_one_metre_short_of_the_plane_scores():
    from .test_rb318 import fixture
    p, rosters, c, d = fixture(moves=True, handoffs=True)
    s, e = p.m.s, p.m.e; sign, goal = s.attack_sign('A'), s.attack_goal('A')
    c.x, c.y = goal - sign * 1.0, 50.; d.x, d.y = 70., 80.
    p.capture(s.now); s.now += p.config.latency_ms
    v, b = p.view(c.id, s.now)
    i, _ = C.decide(v, b); assert i.kind == 'stretch', i.kind
    assert p.submit(i)['status'] == 'accepted'
    for _ in range(120):
        p.step()
        if any(x['event'] == 'stretch_goal' for x in e.log): break
    assert any(x['event'] == 'stretch_goal' for x in e.log)
    p2, _, c2, d2 = fixture(moves=False, handoffs=False)
    c2.x, c2.y = p2.m.s.attack_goal('A') - sign * 1.0, 50.; d2.x, d2.y = 70., 80.
    p2.capture(p2.m.s.now); p2.m.s.now += p2.config.latency_ms
    v2, b2 = p2.view(c2.id, p2.m.s.now); assert C.decide(v2, b2)[0].kind != 'stretch'              # control: flag off


def test_determinism_part_a_and_b_decisions():
    v, tr = tactics_scene(opps=[(60., 45.), (58., 58.)], mates=[(53., 52.), (62., 40.)], matevel=(6., 0.))
    assert opts(v, tr) == opts(v, tr)


def test_defaults_leave_the_effective_config_record_unchanged():
    from .config import RulebookConfigV3
    from .test_rb33 import control_rosters
    d = tuple(control_rosters()[t].digest for t in ('A', 'B'))
    off, on = RulebookConfigV3(roster_digests=d), RulebookConfigV3(roster_digests=d, rb319_ball_in_play_enabled=True)
    assert 'rb319_ball_in_play_enabled' not in off.record() and 'rb319_parts' not in off.record()
    assert on.record()['rb319_parts'] == 'A1A2A3A4' and on.digest != off.digest
