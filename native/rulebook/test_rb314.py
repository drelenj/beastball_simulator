"""RB-3.14 PROVISIONAL, native-rb/3: release-time lane check, perceived opponents' own reach, typical-athlete free run."""
from dataclasses import replace
import pytest
from native import cognition as C
from native import cognition_rb3 as R
from .test_rb312 import carrier_scene, opts
from .test_rb313 import moving, opp_tracks


def scene(opps, mates, reach=None, release_ms=250, vel=(0., 0.), held_ms=2000, **kw):
    v, tr, _ = carrier_scene(opps=opps, mates=mates, held_ms=held_ms, **kw)
    tr = tuple(replace(t, vx=vel[0], vy=vel[1]) if t.team == 'B' else t for t in tr)
    br = tuple((t.entity, reach if reach is not None else 3.05) for t in tr if t.team == 'B')
    return replace(v, tracks=tr, pass_release_ms=release_ms, body_reach=br), tr


def passes(v, tr): return [r for r in opts(v, tr) if r[0] == 'pass']


# a. clear at decision time, blocked at release
def test_a_lane_clear_now_but_blocked_at_release_is_rejected_and_the_old_timing_accepts_it():
    kw = dict(opps=[(50., 53.)], mates=[(70., 50.)], reach=.5, vel=(0., -6.))           # 3 m to the side, closing on the pass line
    v, tr = scene(**kw)
    now = R.lane_margin(v, tr[-1], opp_tracks(tr), 46., t_release=0.)                    # at decision time (and ignoring release) the lane is clear
    assert now > 0
    assert R.lane_margin(v, tr[-1], opp_tracks(tr), 46.) < 0                              # advanced over the 250 ms release time: blocked
    assert not passes(v, tr)
    v0, tr0 = scene(release_ms=0, **kw)                                                  # control: the RB-3.13 timing (no release time) would pass
    assert passes(v0, tr0)


# b. defender within reach of the release point: no pass, lateral escape
def test_b_defender_within_reach_of_the_release_point_blocks_every_pass_and_the_carrier_escapes_laterally():
    v, tr = scene(opps=[(52., 50.)], mates=[(50., 30.), (70., 40.), (40., 50.)])
    assert R.release_blocked(v, opp_tracks(tr)) and R.is_pressured(v, opp_tracks(tr))
    assert not passes(v, tr)
    car = [r for r in opts(v, tr) if r[0] == 'carry'][0]
    assert abs(car[2][1] - 50.) > 5., car
    vc, trc = scene(opps=[(50., 90.)], mates=[(50., 30.), (70., 40.), (40., 50.)])      # control: defender far away
    assert not R.release_blocked(vc, opp_tracks(trc)) and passes(vc, trc)


# c. free run by typical kinematics
def test_c_free_run_distinguishes_a_still_from_a_closing_defender_by_kinematics():
    still, trs = scene(opps=[(62., 50.)], mates=[])
    clos, trc = scene(opps=[(62., 50.)], mates=[], vel=(-10., 0.))
    f_s = R.free_run_m(still, opp_tracks(trs), (100., 50.)); f_c = R.free_run_m(clos, opp_tracks(trc), (100., 50.))
    assert 0 <= f_c < f_s < R.CARRY_FREE_MAX_M
    for v, tr, f in ((still, trs, f_s), (clos, trc, f_c)):                               # f + buffer is the first sample the opponent gets there in time
        o = opp_tracks(tr)[0]; s_hit = f + R.CARRY_CONTACT_BUFFER_M
        t_me = R.time_to_cover(v, s_hit, (1., 0.)); t_op = R.typical_time_to(o, v.x + s_hit, 50., R.opp_reach(v, o))
        assert t_op <= t_me + 1e-9
        s_before = s_hit - R.CARRY_PATH_STEP_M
        assert R.typical_time_to(o, v.x + s_before, 50., R.opp_reach(v, o)) > R.time_to_cover(v, s_before, (1., 0.))
    assert R.TYPICAL_ACCEL == 8.75 and abs(R.TYPICAL_TOP - .88 * 31.2928) < 1e-9


def test_c_a_slow_defender_far_to_the_side_does_not_block_the_carry():
    v, tr = scene(opps=[(55., 80.)], mates=[], vel=(0., -1.))
    assert R.free_run_m(v, opp_tracks(tr), (100., 50.)) == R.CARRY_FREE_MAX_M
    v2, tr2 = scene(opps=[(55., 80.)], mates=[], vel=(0., -12.))                          # control: the same defender sprinting at the path
    assert R.free_run_m(v2, opp_tracks(tr2), (100., 50.)) < R.CARRY_FREE_MAX_M


def test_c_typical_kinematics_unit_values():
    from native.cognition import Track
    o = Track('B:0', 'B', 'field', 0., 0., 0., 0., 0)
    t = R.typical_time_to(o, 10., 0., 0.)
    assert abs(t - (2 * 10. / 8.75) ** .5) < 1e-9                                        # from rest, below the speed cap: sqrt(2d/a)
    away = replace(o, vx=-8.)
    assert R.typical_time_to(away, 10., 0., 0.) > t + 8. / 8.75 - 1e-9                    # moving away has to brake first
    assert R.typical_time_to(replace(o, vx=10.), 10., 0., 0.) < t


# d. perceived reach; unperceived ignored
def test_d_a_tall_perceived_defender_blocks_a_lane_a_control_sized_one_does_not_and_unperceived_is_ignored():
    kw = dict(opps=[(60., 55.)], mates=[(70., 50.)])
    vt, trt = scene(reach=4.11, **kw); vc, trc = scene(reach=3.05, **kw)
    assert not passes(vt, trt) and passes(vc, trc)
    assert R.opp_reach(vt, opp_tracks(trt)[0]) == 4.11 + R.ACQ_RADIUS_M + R.ACQ_EXTRA_M
    unseen = tuple(t for t in trt if t.team != 'B')                                      # the same tall defender, not in the fresh tracks
    assert passes(vt, unseen)
    vn, trn = scene(**kw); vn = replace(vn, body_reach=())                               # control: no body size in the view falls back to the estimate
    assert passes(vn, trn)


def test_body_size_and_release_time_are_public_view_fields_that_round_trip():
    from .test_rb36 import rb3
    from .test_rb34 import live
    p = rb3(); s, e, a, t = live(p); p.capture(s.now); s.now += 300
    v, b = p.view('A:0', s.now)
    assert v.pass_release_ms == v.own_release_ms == 250
    assert dict(v.body_reach)['B:0'] == round(.529 * 2.39, 4)
    assert len(v.body_reach) == len([q for q in s.players.values() if q.active])


def test_determinism():
    v, tr = scene(opps=[(60., 55.), (58., 45.)], mates=[(70., 50.), (62., 35.)], vel=(-3., 1.))
    assert opts(v, tr) == opts(v, tr)
