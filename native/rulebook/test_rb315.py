"""RB-3.15 PROVISIONAL, native-rb/3: S-1 aim away from the keeper, S-2 shot lane, own release delay."""
import random
from dataclasses import replace
from math import hypot
import pytest
from native import cognition as C
from native import cognition_rb3 as R
from .test_rb36 import rb3, defender_view, T
from .test_rb34 import live
from .test_rb39a import field


def shooter_scene(keeper_y=50., keeper_reach=1.26431, keeper_vy=0., defenders=(), release_ms=250, me=(88., 50.), def_vel=(0., 0.)):
    p = rb3(); s, e, a, t = live(p); v, b = defender_view(p, 'A:0')
    tr = [replace(T('B:K', 'B', 100. - 2., keeper_y, v.delivered_ms), role='keeper', vy=keeper_vy)]
    tr += [replace(T(f'B:{i}', 'B', x, y, v.delivered_ms), vx=def_vel[0], vy=def_vel[1]) for i, (x, y) in enumerate(defenders)]
    tr = tuple(tr)
    br = (('B:K', keeper_reach),) + tuple((f'B:{i}', 1.26431) for i in range(len(defenders)))   # RB-3.16: arm reach (R-1)
    bh = tuple((t_.entity, 2.39) for t_ in tr)
    v = replace(v, x=me[0], y=me[1], tracks=tr, holds_ball=True, own_control_ms=2000, body_reach=br, body_height=bh,
                own_release_ms=release_ms, pass_release_ms=release_ms)
    return v, tr


# a. aim near a post side, outside the keeper's reach; switches with the keeper
def test_a_aim_is_near_a_post_side_outside_the_keepers_reach_and_switches_sides_with_him():
    v, tr = shooter_scene(keeper_y=50.)
    plan = R.shot_plan(v, tr); assert plan is not None
    dy = plan['aim'][1] - 50.; assert abs(dy) >= 1.8 and plan['margin'] >= R.SHOT_MIN_MARGIN_M
    assert plan['z'] == .4 or abs(dy) < 2.4                                   # inside the 3.0 - ball radius - .3 disc
    v2, tr2 = shooter_scene(keeper_y=51.5); p2 = R.shot_plan(v2, tr2)
    assert p2['aim'][1] - 50. < 0 and abs(p2['aim'][1] - 50.) >= 1.8          # keeper shifted toward +y: the far side is -y
    v3, tr3 = shooter_scene(keeper_y=48.5); p3 = R.shot_plan(v3, tr3)
    assert p3['aim'][1] - 50. > 0                                              # and the other way
    assert abs(50. + 1. - 51.5) < 1.2                                          # control: the old aim (goal, 50 +/- 1) sits on the keeper


def test_a_keeper_is_advanced_by_his_velocity_over_release_and_flight():
    v, tr = shooter_scene(keeper_y=50., keeper_vy=8.)                          # he is moving toward +y: the far side is -y and the margin is larger
    plan = R.shot_plan(v, tr); assert plan['aim'][1] < 50.
    vs, trs = shooter_scene(keeper_y=50.)
    assert plan['margin'] > R.shot_plan(vs, trs)['margin']


# b. a keeper covering the whole mouth: no shot offered
def test_b_keeper_covering_the_whole_mouth_gets_no_shot_and_the_control_gets_one():
    v, tr = shooter_scene(keeper_reach=9.0)
    assert R.shot_plan(v, tr) is None
    pp = rb3(); ss, ee, aa, tt = live(pp); v0, b0 = defender_view(pp, 'A:0')
    i, rec = C.decide(replace(v, observation_id=v0.observation_id, delivered_ms=v0.delivered_ms), replace(b0, tracks=tr, own_feedback=(), last_ball=None))
    assert i.kind != 'shoot'
    vc, trc = shooter_scene(); assert R.shot_plan(vc, trc) is not None


# c. a field defender in the lane
def test_c_field_defender_in_the_shot_lane_blocks_the_shot_and_out_of_the_lane_does_not():
    v, tr = shooter_scene(defenders=[(94., 49.)])
    assert R.shot_plan(v, tr) is None
    vo, tro = shooter_scene(defenders=[(94., 49.)], def_vel=(0., 20.))        # the same defender running out of the lane
    vf, trf = shooter_scene(defenders=[(94., 62.)])                            # control: well clear
    assert R.shot_plan(vf, trf) is not None
    assert R.shot_plan(vo, tro) is not None


# d. own release delay
def test_d_own_release_delay_is_read_from_the_view_and_used_for_the_advance():
    from .test_rb36 import rb3 as mk
    p = mk(); s, e, a, t = live(p)
    A = field(s, 'A'); A[0].a.ball_handling = .2; A[1].a.ball_handling = .9
    p.capture(s.now); s.now += 300
    v0, _ = p.view(A[0].id, s.now); v1, _ = p.view(A[1].id, s.now)
    assert v0.own_release_ms == round(250 * (1.35 - .5 * .2)) and v1.own_release_ms == round(250 * (1.35 - .5 * .9))
    assert v0.own_release_ms > v1.own_release_ms
    assert abs(R.release_time_s(v0) - v0.own_release_ms / 1000.) < 1e-9
    kw = dict(defenders=[(92., 60.)], def_vel=(0., -20.))
    fast, trf = shooter_scene(release_ms=100, **kw); slow, trs = shooter_scene(release_ms=500, **kw)
    assert R.shot_plan(fast, trf) is not None and R.shot_plan(slow, trs) is None   # the longer delay lets him reach the lane


def test_determinism():
    v, tr = shooter_scene(defenders=[(94., 62.)], keeper_y=50.7)
    assert R.shot_plan(v, tr) == R.shot_plan(v, tr)


# e. fixed-geometry shot batch (the clean conversion measure)
def shot_trial(seed, mode, dist=12., dy0=0.):
    from native.rulebook.port import RulebookPort
    from native.rulebook.config import RulebookConfigV3
    from .test_rb33 import control_rosters
    rosters = control_rosters()
    p = RulebookPort(seed, RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A', 'B')), **{}), rosters=rosters)
    s, e, a, t = live(p); T_ = p.types; s.restart = None; e.rb_period_start_open = False
    for i, q in enumerate(q for q in s.players.values() if q.role != 'archer'):
        q.x, q.y = 30. + (i % 6) * 2, 92. + (i // 6) * 1.5; q.vx = q.vy = 0.; q.target = (q.x, q.y); p.move[q.id] = (q.x, q.y)
    shooter = field(s, 'A')[0]; keeper = next(q for q in s.players.values() if q.team == 'B' and q.role == 'keeper' and q.active)
    shooter.x, shooter.y = 100. - dist, 50. + dy0; keeper.x, keeper.y = 98., 50.; keeper.vx = keeper.vy = 0.
    s.owner = 'A'; e.possession.pp = 'A'; e.possession.tc = 'A'; e.rb.possession = 'A'
    s.ball = T_.Ball(mode=T_.BallMode.CONTROLLED, x=shooter.x, y=shooter.y, z=1.5, carrier=shooter.id, control_time=s.now, scoring=True, last_touch='A')
    e.native_sync(); n0 = len(e.log); nd = {}; ns = 0; shot = False
    for _ in range(260):
        now = s.now
        if now >= ns: p.capture(now); ns = now + p.config.sense_ms
        for pid in (shooter.id, keeper.id):
            if now < nd.get(pid, 0): continue
            v, b = p.view(pid, now)
            if v is None: continue
            if pid == shooter.id and not shot and v.holds_ball:
                fresh = tuple(x for x in b.tracks if 0 <= v.delivered_ms - x.captured_ms <= b.max_track_age_ms)
                k = next((x for x in fresh if x.role == 'keeper'), None)
                if mode == 'new':
                    plan = R.shot_plan(v, fresh); assert plan is not None
                    aim, z = plan['aim'], plan['z']
                else:
                    aim, z = (100., 50. + (-1. if k is not None and k.y > 50 else 1.)), 1.6
                i = C.ActionIntent('shot', 'd', pid, 'shoot', None, aim, None, None, v.delivered_ms, speed=R.shot_speed(v), height=z, period=s.period)
                assert p.submit(i)['status'] == 'accepted'; shot = True; nd[pid] = now + 4000; continue
            if pid == keeper.id:
                i, _ = C.decide(v, b); p.submit(i); nd[pid] = now + p.config.decision_ms
        p.step()
        for ev in e.log[n0:]:
            d = ev['data']
            if ev['event'] == 'goal': return 'scored'
            if ev['event'] == 'keeper_contact' or (ev['event'] == 'control' and d['player'] == keeper.id): return 'keeper'
            if ev['event'] in ('boundary',): return 'out'
            if ev['event'] == 'control': return 'other'
        n0 = len(e.log)
    return 'none'


def test_e_batch_from_12_m_s1_vs_the_old_aim():
    from collections import Counter
    new = Counter(); old = Counter()
    for k in range(50):
        dy0 = ((k % 5) - 2) * .8
        new[shot_trial(k + 1, 'new', 12., dy0)] += 1; old[shot_trial(k + 1, 'old', 12., dy0)] += 1
    print('BATCH new', dict(new), 'old', dict(old))
    assert sum(new.values()) == 50 and sum(old.values()) == 50
    assert new['scored'] > old['scored']                                        # the S-1 aim converts more from the same geometry
    open('/tmp/rb315_batch.txt', 'w').write(f'S-1 {dict(new)}\nold {dict(old)}\n')
