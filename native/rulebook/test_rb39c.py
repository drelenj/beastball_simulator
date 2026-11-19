"""RB-3.9c PROVISIONAL (native-rb/3): an unopposed carrier near the goal he attacks carries on to the
goal when he can arrive before the zone_residence limit; attackers exit at 4 s otherwise."""
from dataclasses import replace
import pytest
from native import cognition as C
from native import cognition_rb3 as R
from .test_rb36 import rb3
from .test_rb34 import live


def open_play(p, carrier_xy, defenders_x=(20., 35.), keeper_xy=(97., 80.)):
    s, e, a, t = live(p); T = p.types
    s.restart = None; e.rb_period_start_open = False
    A = [q for q in s.players.values() if q.team == 'A' and q.active and q.role != 'archer']
    B = [q for q in s.players.values() if q.team == 'B' and q.active and q.role != 'archer']
    for i, q in enumerate(A): q.x, q.y = 45. + (i % 4) * 2., 10. + (i // 4) * 25.
    for i, q in enumerate(B):
        q.x, q.y = (keeper_xy if q.role == 'keeper' else (defenders_x[0] + (i % 4) * 4., 8. + (i // 4) * 28.))
    car = next(q for q in A if q.role == 'field'); car.x, car.y = carrier_xy
    for q in A + B: q.vx = q.vy = 0.; q.target = (q.x, q.y); p.move[q.id] = (q.x, q.y)
    s.owner = 'A'; e.possession.pp = 'A'; e.possession.tc = 'A'; e.rb.possession = 'A'
    s.ball = T.Ball(mode=T.BallMode.CONTROLLED, x=car.x, y=car.y, z=1.5, carrier=car.id, control_time=s.now, scoring=True, last_touch='A')
    e.native_sync()
    assert s.attack_goal('A') == 100
    return s, e, car


def drive(p, steps):
    s = p.m.s; nd = {}; ns = 0; T = p.types
    for _ in range(steps):
        now = s.now
        if now >= ns: p.capture(now); ns = now + p.config.sense_ms
        for pid in p.active_ids():
            if now < nd.get(pid, 0): continue
            v, b = p.view(pid, now)
            if v is None: continue
            i, _ = C.decide(v, b); p.submit(i); nd[pid] = now + p.config.decision_ms
        p.step()
        if s.phase != T.Phase.LIVE: break


def test_unopposed_carry_from_the_zone_edge_scores_5():
    p = rb3(); s, e, car = open_play(p, (80.5, 50.))
    drive(p, 120)
    goals = [r['data'] for r in e.log if r['event'] == 'goal']
    assert goals and goals[0]['method'] == 'carry' and goals[0]['points'] == 5 and s.score['A'] == 5
    assert not any(r['event'] == 'restart_awarded' and r['data']['reason'] == 'zone_residence' for r in e.log)


def carrier_view(p, car):
    s = p.m.s; p.capture(s.now); s.now += 300; v, b = p.view(car.id, s.now)
    return replace(v, restart=None, pending_command_id=None), b


def test_decision_rules():
    p = rb3(); s, e, car = open_play(p, (82., 50.)); v, b = carrier_view(p, car)
    base = C.ActionIntent('i', 'd', car.id, 'pass', 'A:1', (70., 50.), None, None, v.delivered_ms)
    i, r = R.carrier_to_goal(v, b, base, {})
    assert i.kind == 'carry' and i.aim == (99., 50.) and r['rb39c']['rule'] == 'unopposed_carry_to_goal'
    # a believed defender within 5 m: no override
    near = b.tracks + (C.Track('B:9', 'B', 'field', car.x + 3., car.y, 0., 0., v.delivered_ms),)
    assert R.carrier_to_goal(replace(v, tracks=near), replace(b, tracks=near), base, {})[0] is base
    # Keeper in the lane: no override
    lane = b.tracks + (C.Track('B:10', 'B', 'keeper', 92., 50.5, 0., 0., v.delivered_ms),)
    assert R.carrier_to_goal(replace(v, tracks=lane), replace(b, tracks=lane), base, {})[0] is base
    # too late to arrive before the 5 s limit: no override (the 4 s exit stands)
    late = replace(v, zone_elapsed_ms=4300)
    assert R.carrier_to_goal(late, b, base, {})[1]['rb39c'] == 'cannot_reach_goal_in_time'
    # far from the goal: no override
    p2 = rb3(); s2, e2, c2 = open_play(p2, (55., 50.)); v2, b2 = carrier_view(p2, c2)
    assert R.carrier_to_goal(v2, b2, base, {})[0] is base


def test_attacker_exits_before_5s_when_he_cannot_score_and_the_old_defender_exit_stays_for_other_profiles():
    # RB-3.11: the fixed 4 s attacker timer of RB-3.9c is replaced by time-to-arc exits (see test_rb311.py);
    # the fixed 3 s exit stays for every profile other than native-rb/3.
    p = rb3(); s, e, car = open_play(p, (88., 45.)); v, b = carrier_view(p, car)   # 13 m from goal, in the zone
    near = b.tracks + (C.Track('B:9', 'B', 'field', car.x + 2., car.y, 0., 0., v.delivered_ms),)
    v, b = replace(v, tracks=near), replace(b, tracks=near)
    k, _ = C.decide(replace(v, zone_elapsed_ms=500), b)
    assert not (k.kind == 'position' and ((k.aim[0] - 100.) ** 2 + (k.aim[1] - 50.) ** 2) ** .5 > 20.)   # no exit at 0.5 s
    i, _ = C.decide(replace(v, zone_elapsed_ms=4000), b)
    assert i.kind == 'position' and ((i.aim[0] - 100.) ** 2 + (i.aim[1] - 50.) ** 2) ** .5 > 20.
    d = replace(v, holds_ball=False, signals=replace(v.signals, passive_team='B'), zone_elapsed_ms=3000, cognition='native-v0/2')
    j, _ = C.decide_v2(d, b); assert j.kind == 'position'
