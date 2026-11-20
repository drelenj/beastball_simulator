"""RB-3.13 PROVISIONAL, native-rb/3: pass safety, pressure by time, closing-time carry, zone-clock gate, no arrows during the snap hold."""
import random
from dataclasses import replace
from math import hypot
import pytest
from native import cognition as C
from native import cognition_rb3 as R
from .test_rb36 import rb3, defender_view, T
from .test_rb34 import live
from .test_rb39a import scrim, field
from .test_rb312 import carrier_scene, opts, best


def moving(tr, vx, vy):
    return tuple(replace(t, vx=vx, vy=vy) if t.team == 'B' else t for t in tr)


def decide(v, tr, p=None):
    p = p or rb3(); s, e, a, t = live(p); v0, b = defender_view(p, 'A:0')
    return C.decide(v, replace(b, tracks=tr, own_feedback=(), last_ball=None))


def opp_tracks(tr): return [t for t in tr if t.team == 'B']


# a. a pass lane within reach of a defender is excluded
def test_a_no_pass_into_a_lane_within_a_defenders_reach_and_the_control_passes():
    v, tr, _ = carrier_scene(opps=[(60., 52.4)], mates=[(70., 52.)], held_ms=2000)   # the forward lane passes within corrected arm reach
    tr = moving(tr, -12., 0.); v = replace(v, tracks=tr)
    assert R.is_pressured(v, opp_tracks(tr))
    o = opts(v, tr); assert not any(r[0] == 'pass' for r in o), o
    i, _ = decide(v, tr); assert i.kind != 'pass'
    v2, tr2, _ = carrier_scene(opps=[(60., 90.)], mates=[(70., 52.)], held_ms=2000)  # control: defender well clear of the lane
    tr2 = moving(tr2, -12., 0.); v2 = replace(v2, tracks=tr2)
    assert any(r[0] == 'pass' for r in opts(v2, tr2))


def test_a_lane_margin_is_beyond_the_acquisition_reach_and_uses_velocity():
    v, tr, _ = carrier_scene(opps=[(60., 58.)], mates=[(70., 40.)])
    mate = next(t for t in tr if t.team == 'A'); still = [t for t in tr if t.team == 'B']
    m0 = R.lane_margin(v, mate, still, 46.)
    m1 = R.lane_margin(v, mate, [replace(still[0], vy=-30.)], 46.)       # the same defender running toward the lane
    assert m1 < m0 and m0 > 0 and R.acquisition_reach(v) == pytest.approx(.529 * 2.39 + .45 + .2)


# b. receiver after the snap
def test_b_receiver_with_a_closing_rush_passes_when_a_safe_pass_exists_and_escapes_laterally_when_not():
    rush = dict(opps=[(58., 50.)], held_ms=100)
    v, tr, _ = carrier_scene(mates=[(50., 30.)], **rush); tr = moving(tr, -9., 0.); v = replace(v, tracks=tr)
    assert R.is_pressured(v, opp_tracks(tr))
    i, _ = decide(v, tr); assert i.kind == 'pass' and i.target == 'A:1'                         # passes before contact
    v, tr, _ = carrier_scene(mates=[], **rush); tr = moving(tr, -9., 0.); v = replace(v, tracks=tr)
    o = opts(v, tr); car = [r for r in o if r[0] == 'carry'][0]
    assert abs(car[2][1] - 50.) > 5., car                                                        # no safe pass: escapes laterally
    straight = R.carry_value(v, opp_tracks(tr), (100., 50.))[0]
    assert car[3] > straight
    R_esc = R.ESCAPE_ANGLES_DEG
    try:
        R.ESCAPE_ANGLES_DEG = ()                                                                  # control: without the escape directions he carries straight
        assert [r for r in opts(v, tr) if r[0] == 'carry'][0][2] == (100., 50.)
    finally:
        R.ESCAPE_ANGLES_DEG = R_esc


# c. free run reflects closing time; no commitment into contact
def test_c_free_run_reflects_closing_time_and_commitment_does_not_apply_when_pressured():
    v, tr, _ = carrier_scene(opps=[(60., 50.)], mates=[(50., 30.)], held_ms=100)
    still = R.free_run_m(v, opp_tracks(tr), (100., 50.))
    closing = R.free_run_m(v, [replace(o, vx=-12.) for o in opp_tracks(tr)], (100., 50.))
    # free_run is set by the opponent's reach time to the path, not by his velocity: the closing rush is pressured instead
    assert still < R.CARRY_FREE_MAX_M and closing <= still
    assert not R.is_pressured(v, opp_tracks(tr))
    trc = moving(tr, -12., 0.); vc = replace(v, tracks=trc)
    assert R.is_pressured(vc, opp_tracks(trc)) and any(r[0] == 'pass' for r in opts(vc, trc))   # not committed for 0.6 s
    vm, trm, _ = carrier_scene(opps=[(66., 56.)], mates=[(55., 36.)], held_ms=100)           # control: unpressured and held 0.1 s
    assert not R.is_pressured(vm, opp_tracks(trm)) and not any(r[0] == 'pass' for r in opts(vm, trm))


def test_c_free_run_is_a_closing_time_not_a_static_distance():
    v, tr, _ = carrier_scene(opps=[(70., 62.)], mates=[])
    far = R.free_run_m(v, opp_tracks(tr), (100., 50.))
    v2, tr2, _ = carrier_scene(opps=[(60., 50.)], mates=[])
    near = R.free_run_m(v2, opp_tracks(tr2), (100., 50.))
    assert 0 <= near < far <= R.CARRY_FREE_MAX_M
    assert R.free_run_m(v2, [], (100., 50.)) == R.CARRY_FREE_MAX_M


def test_pressure_by_time_to_contact():
    v, tr, _ = carrier_scene(opps=[(55., 50.)], mates=[])
    o = opp_tracks(tr)[0]
    still = replace(o, x=57.); fast = replace(o, x=59., vx=-10.); close = replace(o, x=51.8)
    assert not R.is_pressured(v, [still]) and R.is_pressured(v, [fast]) and R.is_pressured(v, [close])
    assert R.time_to_contact(v, close) == 0.


# zone-clock penalty and the Q-RB312-2 perception gate
def test_zone_clock_penalty_is_read_only_for_a_perceived_teammate():
    v, tr, _ = carrier_scene(opps=[(53., 55.)], mates=[(65., 40.)], clocks=[('A:1', 4500)])
    base = [r for r in opts(*carrier_scene(opps=[(53., 55.)], mates=[(65., 40.)])[:2]) if r[0] == 'pass'][0][3]
    seen = [r for r in opts(v, tr) if r[0] == 'pass'][0][3]
    assert abs(base - seen - 4.5) < 1e-6                                                    # t_left 0.5 s: 6 * (1 - .25)
    stale = tuple(replace(t, captured_ms=v.delivered_ms - 2600) if t.team == 'A' else t for t in tr)
    unseen = [r for r in opts(v, stale) if r[0] == 'pass'][0][3]
    assert unseen == base                                                                   # same teammate, same clock, outside fresh tracks
    assert R.zone_clock_penalty(v, stale[-1], 2000) == 0. and R.zone_clock_penalty(v, tr[-1], 2000) > 0.


# d. no arrow during the snap hold
def test_d_archer_does_not_choose_a_release_during_the_hold_and_does_after_it():
    p = rb3(); s, e, a, t = live(p); p.capture(s.now); s.now += 300
    v, b = p.view(a, s.now); tr = next(x for x in b.tracks if x.entity == t.id)
    sig = replace(v.signals, passive_team='B', ball_status='carried', phase='live')
    base = dict(hunt_cleared=True, signals=sig)
    assert C.decide(replace(v, **base), b)[0].kind == 'draw_release'                       # control: not in a hold
    assert C.decide(replace(v, snap_hold=True, **base), b)[0].kind != 'draw_release'
    pend = dict(pending_command_id='cmd', pending_kind='draw_release', pending_target=t.id, pending_release_ms=v.delivered_ms, **base)
    assert C.decide(replace(v, **pend), b)[0].kind == 'release_arrow'
    assert C.decide(replace(v, snap_hold=True, **pend), b)[0].kind == 'abort_draw'


def hold_state(p):
    s, e, a, t = live(p)
    s, e, r = scrim(p, 'A', 50., 30., 'turnover'); f = r.rs['formation']; sn = s.players[f['snapper']]; r.taker = sn.id
    from native.throw_speed import release_speed
    rx, ry = f['receiver_xy']; speed = release_speed(hypot(rx - r.x, ry - r.y), 120.)
    ans = p.geom.launch_for((r.x, r.y, sn.hand_height), (rx, ry, 1.6), speed, 9.81, .015)
    assert e.restart_release(sn.id, ans[0], f['receiver']) and e.rb310_hold
    return s, e, p.types


def test_d_a_forced_release_during_the_hold_is_inert_without_foul_and_refunded():
    p = rb3(); s, e, T_ = hold_state(p)
    arch = next(q for q in s.players.values() if q.role == 'archer' and q.team == 'B')
    tgt = next(q for q in s.players.values() if q.team == 'A' and q.role == 'field' and q.active)
    spent = e.rb.quotas['B']['arrows']; n0 = len(e.log); fouls = lambda: [x for x in e.log[n0:] if x['event'] in ('foul', 'discipline', 'rb_discipline')]
    assert e.shoot_arrow(arch.id, tgt.id, (30., 0., 0.)) is False
    ev = [x for x in e.log[n0:] if x['event'] == 'arrow_inert']
    assert ev and ev[-1]['data']['reason'] == 'snap_hold_release' and ev[-1]['data']['refunded'] is True
    assert not fouls() and e.rb.quotas['B']['arrows'] == spent and not s.arrows
    # control: with the hold gone the same call is judged by the ordinary rules (not the inert hold branch)
    e.rb310_hold = None; n1 = len(e.log); e.shoot_arrow(arch.id, tgt.id, (30., 0., 0.))
    assert not [x for x in e.log[n1:] if x['event'] == 'arrow_inert' and x['data'].get('reason') == 'snap_hold_release']
    assert e.rb.quotas['B']['arrows'] == spent + 1 or [x for x in e.log[n1:] if x['event'] in ('foul', 'archery_target_diagnosis')]


def test_hold_flag_is_public_in_the_view_and_round_trips():
    p = rb3(); s, e, T_ = hold_state(p); p.capture(s.now); s.now += 300
    a = next(q.id for q in s.players.values() if q.role == 'archer' and q.team == 'A')
    v, b = p.view(a, s.now); assert v.snap_hold is True
    e.rb310_hold = None; v2, _ = p.view(a, s.now); assert v2.snap_hold is False


def test_carrier_options_deterministic():
    v, tr, _ = carrier_scene(opps=[(60., 45.), (58., 58.)], mates=[(62., 40.), (55., 70.)])
    assert opts(v, tr) == opts(v, tr)
