"""RB-3.11 Part A PROVISIONAL (owner behavioural defaults, 19 Nov 2026), native-rb/3 cognition only:
Z-2 attacker exit by time-to-arc, Z-3 off-ball attackers stay out, Z-4 defender marking in his own zone."""
from dataclasses import replace
from math import hypot
import pytest
from native import cognition as C
from native import cognition_rb3 as R
from .test_rb36 import rb3
from .test_rb34 import live
from .test_rb39a import scrim, field


def drive_live(p, steps, watch=(), stop_on=None):
    """The run_match loop for a prepared port, recording how long each watched player stays in a zone."""
    s = p.m.s; e = p.m.e; nd = {}; ns = 0; T = p.types; inz = {}; longest = {w: 0 for w in watch}
    for _ in range(steps):
        now = s.now
        if now >= ns: p.capture(now); ns = now + p.config.sense_ms
        for pid in p.active_ids():
            if now < nd.get(pid, 0): continue
            v, b = p.view(pid, now)
            if v is None: continue
            i, _ = C.decide(v, b); p.submit(i); nd[pid] = now + p.config.decision_ms
        p.step()
        for w in watch:
            q = s.players[w]
            if s.phase == T.Phase.LIVE and e.zone(q.x, q.y) is not None: inz.setdefault(w, s.live_ms); longest[w] = max(longest[w], s.live_ms - inz[w])
            else: inz.pop(w, None)
        if stop_on and stop_on(s, e): break
    return longest


def zr(e): return [x for x in e.log if x['event'] == 'restart_awarded' and x['data']['reason'] == 'zone_residence']
def zu(e): return [x for x in e.log if x['event'] == 'foul' and x['data'].get('reason') == 'zone_unmarked']


def stay_put(monkeypatch):
    """Base decisions: every field player without the ball stands still (so only RB-3.11 can move him)."""
    base = C.decide_v2
    def decide_v2(view, belief):
        i, r = base(view, belief)
        if view.role == 'field' and view.restart is None and i.kind not in ('restart_claim', 'hunt_claim'):
            if view.holds_ball: i = replace(i, kind='retain', aim=None, target=None, contact=None)
            else: i = replace(i, kind='scan', aim=(round(view.x, 3), round(view.y, 3)), target=None, contact=None)
        return i, r
    monkeypatch.setattr(C, 'decide_v2', decide_v2)


def freeze_baselines(monkeypatch):
    """Base decisions stand still and the RB-3.6 baseline is off, so only the RB-3.11 behaviour can move a player."""
    stay_put(monkeypatch); monkeypatch.setattr(R, 'defender_baseline', lambda v, b, i, r: (i, r))


def off_ball_clock_run(behavior_on, monkeypatch):
    freeze_baselines(monkeypatch)
    if not behavior_on: monkeypatch.setattr(R, 'zone_behavior', lambda v, b, i, r: (i, r))
    p = rb3(); s, e, a, t = live(p)
    mates = field(s, 'A'); ys = (36., 42., 58., 64.)
    for i, m in enumerate(mates[2:6]): m.x, m.y = 95., ys[i]
    for q in field(s, 'B'): q.x, q.y = 30., 10. + (hash(q.id) % 80)
    s, e, r = scrim(p, 'A', 90., 30., 'turnover'); f = r.rs['formation']
    deep = [m.id for m in mates[2:6] if m.id not in (f['receiver'], f['snapper'])]
    assert r.x == 90. and len(deep) >= 2 and all(abs(s.players[d].x - 89.) < 1e-6 for d in deep)   # placed inside the attacked zone
    T = p.types; s.restart = None; e.rb_period_start_open = False; e.rb310_hold = None; s.phase = T.Phase.LIVE
    holder = next(q for q in mates if q.id not in deep + [f['receiver'], f['snapper']] and q.role == 'field')
    holder.x, holder.y = 60., 50.; s.owner = 'A'; e.possession.pp = 'A'; e.possession.tc = 'A'; e.rb.possession = 'A'
    s.ball = T.Ball(mode=T.BallMode.CONTROLLED, x=60., y=50., z=1.5, carrier=holder.id, control_time=s.now, scoring=True, last_touch='A')
    for q in s.players.values(): q.vx = q.vy = 0.; q.target = (q.x, q.y); p.move[q.id] = (q.x, q.y)
    e.native_sync()
    return p, e, deep, drive_live(p, 120, watch=deep)


def test_off_ball_attackers_placed_deep_by_a_goal_line_formation_exit_before_5s(monkeypatch):
    p, e, deep, longest = off_ball_clock_run(True, monkeypatch)
    assert not zr(e), 'zone_residence called'
    assert max(longest.values()) < 5000


def test_the_same_scenario_without_the_behaviour_is_called_at_5s(monkeypatch):
    p, e, deep, longest = off_ball_clock_run(False, monkeypatch)      # control: the test above is discriminating
    assert zr(e) and max(longest.values()) >= 4900          # called at 5 s of live time (watcher starts one step after the engine clock)


def test_off_ball_attacker_outside_the_zone_does_not_enter_it_unless_involved():
    p = rb3(); s, e, a, t = live(p); me = field(s, 'A')[3]
    p.capture(s.now); s.now += 300; v, b = p.view(me.id, s.now)
    v = replace(v, restart=None, pending_command_id=None, holds_ball=False, x=70., y=50.,
                signals=replace(v.signals, passive_team='A', phase='live', pass_call=None), formation=None)
    far = tuple(t for t in b.tracks if t.entity != C.BALL) + (C.Track(C.BALL, 'ball', 'ball', 40., 50., 0., 0., v.delivered_ms),)
    b = replace(b, tracks=far); v = replace(v, tracks=far)
    walk_in = C.ActionIntent('i', 'd', me.id, 'support', None, (92., 50.), None, None, v.delivered_ms)
    out, rec = R.zone_behavior(v, b, walk_in, {})
    assert rec['rb311']['rule'] == 'Z-3_stay_out' and hypot(out.aim[0] - 100., out.aim[1] - 50.) >= 20.
    # involved: the intended pass target, the designated receiver, or near the carrier
    assert R.zone_behavior(replace(v, signals=replace(v.signals, pass_call=('A:1', me.id, 92., 50.))), b, walk_in, {})[0] is walk_in
    assert R.zone_behavior(replace(v, formation=('A:0', me.id, 92., 50., None, None)), b, walk_in, {})[0] is walk_in
    near = tuple(t for t in far if t.entity != C.BALL) + (C.Track(C.BALL, 'ball', 'ball', 78., 50., 0., 0., v.delivered_ms),
                                                         C.Track('A:7', 'A', 'field', 78., 50., 0., 0., v.delivered_ms))
    assert R.zone_behavior(replace(v, tracks=near), replace(b, tracks=near), walk_in, {})[0] is walk_in


def test_designated_receiver_is_public_during_the_hold_and_exits_on_time_after():
    p = rb3(); s, e, a, t = live(p)
    s, e, r = scrim(p, 'A', 60., 30., 'turnover'); f = r.rs['formation']
    sn = s.players[f['snapper']]; r.taker = sn.id; assert e.ready(sn.id)
    assert e.restart_release(sn.id, (-12.5, 0., 1.), f['receiver'])
    p.capture(s.now); s.now += 300; v, b = p.view(f['receiver'], s.now)
    assert v.restart is None and v.formation[1] == f['receiver']
    w, _ = p.view('A:0' if f['snapper'] != 'A:0' else 'A:1', s.now)
    assert w.formation[1] == f['receiver']


def test_carrier_going_to_goal_under_the_carrier_rule_is_not_pulled_out_and_scores():
    from .test_rb39c import open_play, drive
    p = rb3(); s, e, car = open_play(p, (80.5, 50.)); drive(p, 120)
    goals = [r['data'] for r in e.log if r['event'] == 'goal']
    assert goals and goals[0]['method'] == 'carry' and goals[0]['points'] == 5 and not zr(e)


def carrier_scene(p, zone_elapsed, defender_near=True):
    from .test_rb39c import open_play, carrier_view
    s, e, car = open_play(p, (92., 48.)); v, b = carrier_view(p, car)
    tr = b.tracks + ((C.Track('B:9', 'B', 'field', car.x - 2., car.y, 0., 0., v.delivered_ms),) if defender_near else ())
    return car, replace(v, tracks=tr, zone_elapsed_ms=zone_elapsed), replace(b, tracks=tr)


def test_carrier_without_the_carrier_rule_exits_in_time_or_scores_as_last_resort():
    p = rb3(); car, v, b = carrier_scene(p, 3600)                        # defender within 5 m: no carrier rule; 1.4 s left
    base = C.ActionIntent('i', 'd', car.id, 'pass', 'A:1', (70., 50.), None, None, v.delivered_ms)
    out, rec = R.zone_behavior(v, b, base, {})
    assert rec['rb311']['rule'] in ('Z-2_carrier_exit', 'Z-2_carrier_last_resort_to_goal')
    early = replace(v, zone_elapsed_ms=500)
    assert R.zone_behavior(early, b, base, {})[0] is base                  # plenty of time: untouched
    last = replace(v, zone_elapsed_ms=4300, x=98.5, y=50.)                 # 1.5 m from goal, 0.7 s left: arc too far, goal near
    out, rec = R.zone_behavior(last, b, base, {})
    assert rec['rb311']['rule'] == 'Z-2_carrier_last_resort_to_goal' and out.kind == 'carry' and out.aim == (99., 50.)
    shot = C.ActionIntent('i', 'd', car.id, 'shoot', None, (100., 51.), None, None, v.delivered_ms)
    assert R.zone_behavior(replace(v, zone_elapsed_ms=1000), b, shot, {})[0] is shot     # a real shot option is exempt


@pytest.mark.parametrize('zone_ms,exits', [(0, False), (1000, False), (4300, True)])
def test_involved_attacker_exits_when_time_to_arc_plus_margin_reaches_time_left(zone_ms, exits):
    p = rb3(); s, e, a, t = live(p); me = field(s, 'A')[3]
    p.capture(s.now); s.now += 300; v, b = p.view(me.id, s.now)
    v = replace(v, restart=None, pending_command_id=None, holds_ball=False, x=92., y=50., zone_elapsed_ms=zone_ms,
                signals=replace(v.signals, passive_team='A', phase='live', pass_call=('A:1', me.id, 95., 50.)))
    keep = C.ActionIntent('i', 'd', me.id, 'receive', 'A:1', (95., 50.), None, None, v.delivered_ms)
    out, rec = R.zone_behavior(v, b, keep, {})
    d = hypot(v.x - 100., v.y - 50.); t_arc = R.time_to_cover(v, v.zone_radius + R.ARC_INSET_M - d)
    assert (rec.get('rb311', {}).get('rule') == 'Z-2_exit') == exits
    assert exits == (t_arc + R.EXIT_MARGIN_S >= (5000 - zone_ms) / 1000.)
    if exits: assert hypot(out.aim[0] - 100., out.aim[1] - 50.) >= 20.


def test_time_to_cover_uses_the_athletes_own_acceleration_and_speed():
    p = rb3(); s, e, a, t = live(p); p.capture(s.now); s.now += 300; v, b = p.view(field(s, 'A')[0].id, s.now)
    acc, top = v.body.acceleration, v.body.maximum_speed * R.EXIT_SPEED_FRAC
    assert R.time_to_cover(v, 0.) == 0. and abs(R.time_to_cover(v, 1.) - (2. / acc) ** .5) < 1e-9
    big = 50.; assert abs(R.time_to_cover(v, big) - (top / acc + (big - top * top / (2 * acc)) / top)) < 1e-9


def defender_run(opp_xy, behavior_on, monkeypatch):
    freeze_baselines(monkeypatch)
    if not behavior_on: monkeypatch.setattr(R, 'zone_behavior', lambda v, b, i, r: (i, r))
    p = rb3(); s, e, a, t = live(p); T = p.types; s.restart = None; e.rb_period_start_open = False
    A = field(s, 'A'); B = field(s, 'B')
    for i, q in enumerate(s.players.values()):
        if q.role != 'archer': q.x, q.y = 60. + (i % 5), 5. + 4. * (i % 20)
    d = A[0]; d.x, d.y = 6., 50.; att = B[0]; att.x, att.y = opp_xy
    carrier = B[1]; carrier.x, carrier.y = 60., 50.
    s.owner = 'B'; e.possession.pp = 'B'; e.possession.tc = 'B'; e.rb.possession = 'B'
    s.ball = T.Ball(mode=T.BallMode.CONTROLLED, x=carrier.x, y=carrier.y, z=1.5, carrier=carrier.id, control_time=s.now, scoring=True, last_touch='B')
    for q in s.players.values(): q.vx = q.vy = 0.; q.target = (q.x, q.y); p.move[q.id] = (q.x, q.y)
    e.native_sync()
    return p, e, d, drive_live(p, 100, watch=(d.id,))


def test_defender_in_his_own_zone_is_marked_or_leaves_before_5s(monkeypatch):
    p, e, d, longest = defender_run((30., 50.), True, monkeypatch)           # nobody near: he must leave
    assert not zu(e) and longest[d.id] < 5000
    p, e, d, longest = defender_run((12., 62.), True, monkeypatch)           # an attacker 13 m away: he closes to mark him
    assert not zu(e)
    mark = [x for x in e.log if x['event'] == 'zone_foul_diagnosis']
    assert not mark


def test_the_same_defender_scenarios_without_the_behaviour_are_called_at_5s(monkeypatch):
    for xy in ((30., 50.), (12., 62.)):
        p, e, d, longest = defender_run(xy, False, monkeypatch)
        assert zu(e), xy


def test_defender_rule_unmarked_and_marked_cases_are_unit_decisions():
    p = rb3(); s, e, a, t = live(p); me = field(s, 'A')[0]
    p.capture(s.now); s.now += 300; v, b = p.view(me.id, s.now)
    tr = (C.Track('B:5', 'B', 'field', 30., 50., 0., 0., v.delivered_ms), C.Track('B:6', 'B', 'field', 9., 56., 0., 0., v.delivered_ms))
    v = replace(v, restart=None, pending_command_id=None, holds_ball=False, x=6., y=50., zone_elapsed_ms=0, tracks=tr,
                signals=replace(v.signals, passive_team='B', phase='live'))
    b = replace(b, tracks=tr)
    keep = C.ActionIntent('i', 'd', me.id, 'scan', None, (6., 50.), None, None, v.delivered_ms)
    assert R.zone_behavior(v, b, keep, {})[0] is keep                                # plenty of time
    out, rec = R.zone_behavior(replace(v, zone_elapsed_ms=3900), b, keep, {})
    assert rec['rb311']['rule'] in ('Z-4_close_on_mark', 'Z-4_leave')
    marked = tr + (C.Track('B:7', 'B', 'field', 8., 52., 0., 0., v.delivered_ms),)   # an opposing player within 5 m
    assert R.zone_behavior(replace(v, zone_elapsed_ms=3900, tracks=marked), replace(b, tracks=marked), keep, {})[0] is keep


def test_determinism_same_code_roster_seed():
    from native.run import run_match
    a, _ = run_match(1, rb3().config, max_steps=2500, port_factory=lambda *x, **k: rb3())
    b, _ = run_match(1, rb3().config, max_steps=2500, port_factory=lambda *x, **k: rb3())
    assert (a['trace_hash'], a['state_hash']) == (b['trace_hash'], b['state_hash'])


def test_time_to_cover_counts_braking_when_moving_away_from_the_target():
    p = rb3(); s, e, a, t = live(p); p.capture(s.now); s.now += 300; v, b = p.view(field(s, 'A')[0].id, s.now)
    from dataclasses import replace as rep
    still = R.time_to_cover(v, 5., (1., 0.))
    runs_away = rep(v, body=rep(v.body, vx=-18., vy=0.))          # running at 18 m/s in -x; the target is in +x
    runs_toward = rep(v, body=rep(v.body, vx=18., vy=0.))
    assert abs(still - R.time_to_cover(v, 5.)) < 1e-12                           # no direction: from rest
    stop_t, stop_d = 18. / v.body.braking, 18. * 18. / (2. * v.body.braking)
    assert abs(R.time_to_cover(runs_away, 5., (1., 0.)) - (stop_t + R.time_to_cover(v, 5. + stop_d))) < 1e-9
    assert R.time_to_cover(runs_away, 5., (1., 0.)) > still + .5
    assert R.time_to_cover(runs_toward, 5., (1., 0.)) == still                    # moving toward it: conservative, from rest
