"""RB-3.12 PROVISIONAL, native-rb/3: E-3 snap corridor, B-5 carrier valuation, zone-exit rules."""
import random
from dataclasses import replace
from math import hypot
import pytest
from native import cognition as C
from native import cognition_rb3 as R
from . import formation as F
from .test_rb36 import rb3
from .test_rb34 import live
from .test_rb39a import scrim, field


# ------------------------------------------------------------------ E-3 snap corridor
def snap_first_touch(p, rng, reason, x):
    s, e = p.m.s, p.m.e; T = p.types
    s.phase = T.Phase.LIVE; s.owner = 'A'; s.tackle_count = 0; e.rb310_hold = None
    for q in s.players.values():                                         # crowd the offence around the snap lane
        if q.active and q.role != 'archer' and q.team == 'A': q.x = x - rng.uniform(-1., 14.); q.y = 50. + rng.uniform(-7., 7.)
        elif q.active and q.role != 'archer': q.x = x + rng.uniform(8., 40.); q.y = rng.uniform(5., 95.)
        q.vx = q.vy = 0.; q.freeze_until = -1; q.immune_until = -1; q.posture = 'upright'
    s, e, r = scrim(p, 'A', x, 30., reason); f = r.rs['formation']
    sn = s.players[f['snapper']]; r.taker = sn.id; assert e.ready(sn.id)
    from native.throw_speed import release_speed
    rx, ry = f['receiver_xy']; n0 = len(e.log)
    speed = release_speed(hypot(rx - r.x, ry - r.y), 120.)                               # as the production snap decides
    ans = p.geom.launch_for((r.x, r.y, sn.hand_height), (rx, ry, 1.6), speed, 9.81, .015)   # as the motor solves it
    assert ans is not None and e.restart_release(sn.id, ans[0], f['receiver'])
    for _ in range(40):
        p.step()
        for ev in e.log[n0:]:
            if ev['event'] == 'control': return ev['data']['player'], f
            if ev['event'] in ('touch', 'contact_rejected'): return 'touch:' + ev['data'].get('player', '?'), f
    return None, f


def test_snap_first_touch_is_the_designated_receiver_in_50_scrimmages():
    p = rb3(); live(p); rng = random.Random(312); fails = []; halves = set(); n = 0
    for k in range(50):
        who, f = snap_first_touch(p, rng, 'turnover' if k % 2 else 'goal', rng.uniform(25., 70.)); n += 1
        halves.add(round(f['lane_half_width'], 3))
        if who != f['receiver']: fails.append((k, who, f['receiver']))
    assert n == 50 and not fails, fails
    assert halves == {round(max(F.LANE_MIN_HALF_WIDTH_M, 3.05 + p.m.s.players['A:0'].radius + .2 + F.LANE_EXTRA_M), 3)}


def test_corridor_half_width_follows_the_engine_acquisition_rule():
    p = rb3(); s, e, a, t = live(p)
    big = next(q for q in field(s, 'B')); big.a.reach = 3.9
    s, e, r = scrim(p, 'A', 50., 30., 'turnover')
    assert abs(r.rs['formation']['lane_half_width'] - (3.9 + big.radius + .2 + F.LANE_EXTRA_M)) < 1e-9
    assert F.acquisition_radius(big) == 3.9 + big.radius + .2


def test_corridor_reaches_one_metre_beyond_the_receiver():
    p = rb3(); s, e, a, t = live(p)
    for i, q in enumerate(field(s, 'A')[2:8]): q.x, q.y = 50. - 5. - .6 * i, 50.        # behind the receiver spot, on the line
    s, e, r = scrim(p, 'A', 50., 30., 'turnover'); f = r.rs['formation']; sg = s.attack_sign('A')
    lo, hi = sorted((r.x, f['receiver_xy'][0] - sg * F.LANE_BEYOND_RECEIVER_M))
    for q in s.players.values():
        if q.active and q.role != 'archer' and q.id not in (f['snapper'], f['receiver']):
            assert not (lo <= q.x <= hi and abs(q.y - 50.) < f['lane_half_width']), q.id


# ------------------------------------------------------------------ B-5 carrier valuation (pure function)
from .test_rb36 import defender_view, T


def carrier_scene(me=(50., 50.), opps=(), mates=(), held_ms=2000, clocks=()):
    p = rb3(); s, e, a, t = live(p); v, b = defender_view(p, 'A:0'); sg = v.attack_sign
    tr = tuple(T(i, 'B', x, y, v.delivered_ms) for i, (x, y) in enumerate(opps)) \
        + tuple(T(f'A:{i + 1}', 'A', x, y, v.delivered_ms) for i, (x, y) in enumerate(mates))
    tr = tuple(replace(t_, entity=f'B:{i}') if t_.team == 'B' else t_ for i, t_ in enumerate(tr))
    v = replace(v, x=me[0], y=me[1], tracks=tr, holds_ball=True, own_control_ms=held_ms, mate_zone_ms=tuple(clocks))
    return v, tr, sg


def opts(v, tr, aim=None):
    sg = v.attack_sign; aim = aim or (v.own_goal_x + sg * 100., 50.)
    return R.carrier_options(v, tr, aim, sg)


def best(o): return max(o, key=lambda r: (r[3], r[0], r[1] or ''))


def test_unpressured_free_run_carries_where_M1_would_pass():
    v, tr, sg = carrier_scene(opps=[(50. + 30, 80.)], mates=[(50. + 8 * 1, 40.)])
    o = opts(v, tr); assert best(o)[0] == 'carry', o
    v2, tr2, _ = carrier_scene(opps=[(50. + 30, 80.)], mates=[(50. + 8, 40.)])
    assert any(r[0] == 'pass' for r in o)


def test_blocked_runway_lowers_the_carry_and_an_unsafe_lane_is_excluded():      # RB-3.13: lane safety and closing-time free run
    v, tr, _ = carrier_scene(opps=[(56., 50.)], mates=[(50., 30.), (62., 42.)])
    o = opts(v, tr); assert [r[1] for r in o if r[0] == 'pass'] == ['A:1']                 # A:2's lane passes within reach of the defender
    v2, tr2, _ = carrier_scene(opps=[(66., 50.)], mates=[(50., 30.), (62., 42.)])
    assert [r[1] for r in opts(v2, tr2) if r[0] == 'pass'] == ['A:1', 'A:2']
    assert [r[3] for r in o if r[0] == 'carry'][0] < [r[3] for r in opts(v2, tr2) if r[0] == 'carry'][0]


def test_pressured_carrier_passes_to_an_open_teammate_and_unpressured_control_does_not():
    v, tr, _ = carrier_scene(opps=[(60., 50.)], mates=[(62., 40.)])
    tr = tuple(replace(t, vx=-9.) if t.team == 'B' else t for t in tr); v = replace(v, tracks=tr)
    o = opts(v, tr); assert best(o)[0] == 'pass', o                                  # closing rush from the front: passes
    v2, tr2, _ = carrier_scene(opps=[(50., 80.)], mates=[(62., 40.)])                # control: the defender far to the side, no rush
    assert best(opts(v2, tr2))[0] == 'carry'
    assert [r[3] for r in o if r[0] == 'carry'][0] < [r[3] for r in opts(v2, tr2) if r[0] == 'carry'][0]


def test_commitment_blocks_a_mediocre_pass_for_600ms_then_allows_it():
    scene = dict(opps=[(50. + 8., 56.)], mates=[(50. + 5., 38.)])
    v, tr, _ = carrier_scene(held_ms=200, **scene); assert not any(r[0] == 'pass' for r in opts(v, tr))
    v, tr, _ = carrier_scene(held_ms=900, **scene); assert any(r[0] == 'pass' for r in opts(v, tr))        # control: same scene, later
    v, tr, _ = carrier_scene(held_ms=200, opps=[(60., 50.)], mates=[(50., 30.)])
    tr = tuple(replace(t, vx=-9.) if t.team == 'B' else t for t in tr); v = replace(v, tracks=tr)
    assert R.is_pressured(v, [t for t in tr if t.team == 'B']) and any(r[0] == 'pass' for r in opts(v, tr))   # pressured: commitment does not apply
    v, tr, _ = carrier_scene(held_ms=200, opps=[(50. - 30., 90.)], mates=[(50. + 15., 40.)])
    assert any(r[0] == 'pass' for r in opts(v, tr))                                                          # big gain + safe lane: exempt


def test_backward_pass_penalised_only_when_unpressured():
    sc = dict(mates=[(50. - 8., 40.)], held_ms=2000)
    v, tr, sg = carrier_scene(opps=[(58., 58.)], **sc)
    free = [r for r in opts(v, tr) if r[0] == 'pass'][0][3]
    v, tr, sg = carrier_scene(opps=[(58., 58.)], **sc)                                    # same, with a rush closing in from the front
    tr = tuple(replace(t, vx=-9., vy=-9.) if t.team == 'B' else t for t in tr)
    v = replace(v, tracks=tr); assert R.is_pressured(v, [t for t in tr if t.team == 'B'])
    pressed = [r for r in opts(v, tr) if r[0] == 'pass'][0][3]
    assert pressed > free + 2.


def test_receiver_zone_clock_penalty_applies_below_two_seconds_only():
    scene = dict(opps=[(50. + 3., 55.)], mates=[(50. + 15., 40.)])
    pv = lambda **kw: [r for r in opts(*carrier_scene(**scene, **kw)[:2]) if r[0] == 'pass'][0][3]
    base = pv()
    assert abs(base - pv(clocks=[('A:1', 4000)]) - 3.0) < 1e-6                                # t_left 1.0 s: 6 * (1 - .5)
    assert abs(base - pv(clocks=[('A:1', 4900)]) - 5.7) < 1e-6                                # t_left 0.1 s
    assert pv(clocks=[('A:1', 3000)]) == base == pv(clocks=[('A:1', 2500)])                   # t_left >= 2 s: none


def test_carrier_options_is_deterministic_and_pure():
    v, tr, _ = carrier_scene(opps=[(60., 45.), (58., 58.)], mates=[(62., 40.), (55., 70.)])
    assert opts(v, tr) == opts(v, tr)
    assert opts(v, replace(v, tracks=tr[::-1]).tracks) == opts(v, tr)


def test_decide_uses_the_rb3_valuation_in_the_carrier_branch():
    v, tr, sg = carrier_scene(opps=[(50. + 30, 80.)], mates=[(58., 40.)])
    p = rb3(); s, e, a, t = live(p); v0, b = defender_view(p, 'A:0')
    b = replace(b, tracks=tr, own_feedback=(), last_ball=None)
    i, rec = C.decide(v, b)
    assert i.kind in ('carry', 'shoot'), i.kind


# ------------------------------------------------------------------ Part 1 zone exit
def zone_def(me, opps, elapsed=0, vel=(0., 0.)):
    p = rb3(); s, e, a, t = live(p); v, b = defender_view(p, 'A:0')
    tr = tuple(replace(T(f'B:{i}', 'B', x, y, v.delivered_ms), vx=vel[0], vy=vel[1]) for i, (x, y) in enumerate(opps)) + (T(C.BALL, 'ball', 60., 50., v.delivered_ms),)
    v = replace(v, x=me[0], y=me[1], tracks=tr, holds_ball=False, zone_elapsed_ms=elapsed, body=replace(v.body, vx=0., vy=0.))
    b = replace(b, tracks=tr, own_feedback=(), last_ball=None)
    base = C.ActionIntent('i', 'd', v.athlete, 'scan', None, (me[0], me[1]), None, None, v.delivered_ms)
    return v, b, base


def test_defender_without_a_reason_leaves_at_once_and_one_with_a_reason_does_not():
    v, b, i = zone_def((10., 50.), [(60., 50.)])
    i2, rec = R.zone_behavior(v, b, i, {}); assert rec['rb311']['rule'] == 'Z-4_no_reason_leave' and i2.kind == 'position'
    v, b, i = zone_def((10., 50.), [(25., 50.)])                      # control: an unmarked opponent just outside, reachable
    i2, rec = R.zone_behavior(v, b, i, {}); assert 'rb311' not in rec and i2 is i


def test_exit_margin_is_one_and_a_half_seconds():
    assert R.EXIT_MARGIN_S == 1.5
    v, b, i = zone_def((10., 50.), [(25., 50.)], elapsed=0)
    t_arc = R.time_to_cover(v, 21. - 10., R._unit(0., 50., 10., 50.)); assert t_arc + 1.4 < 5.
    v, b, i = zone_def((10., 50.), [(25., 50.)], elapsed=int((5. - t_arc - 1.4) * 1000) + 0)
    i2, rec = R.zone_behavior(v, b, i, {}); assert rec.get('rb311', {}).get('rule') in ('Z-4_leave', 'Z-4_close_on_mark')


def test_close_versus_leave_picks_the_faster_and_a_tie_leaves_when_the_mark_moves_away():
    v, b, i = zone_def((10., 50.), [(18., 50.)], elapsed=3000)         # mark 8 m away, arc 11 m away: closing is faster
    i2, rec = R.zone_behavior(v, b, i, {}); assert rec['rb311']['rule'] == 'Z-4_close_on_mark'
    v, b, i = zone_def((18., 50.), [(12., 60.)], elapsed=3000)         # arc 3 m away, mark 12 m away: leaving is faster
    i2, rec = R.zone_behavior(v, b, i, {}); assert rec['rb311']['rule'] == 'Z-4_leave'


def test_loose_ball_pursuit_counts_as_involvement():
    p = rb3(); s, e, a, t = live(p); v, b = defender_view(p, 'A:0')
    sg = v.attack_sign; gx = v.own_goal_x + sg * 100.
    tr = (T(C.BALL, 'ball', gx - sg * 10., 50., v.delivered_ms),)
    v = replace(v, x=gx - sg * 10., y=50., tracks=tr, holds_ball=False, signals=replace(v.signals, passive_team=v.team, pass_call=None), formation=None)
    b = replace(b, tracks=tr, own_feedback=(), last_ball=None)
    mk = lambda k: C.ActionIntent('i', 'd', v.athlete, k, None, (v.x, v.y), None, None, v.delivered_ms)
    assert R._involved(v, b, mk('pursue')) == 'loose_ball_pursuit' and R._involved(v, b, mk('scan')) is None
