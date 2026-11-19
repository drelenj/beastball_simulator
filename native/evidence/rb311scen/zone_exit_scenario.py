"""Zone-exit timing scenario (no full match). A defender stands in his own Keeper Zone with no opponent near;
measure live time until he is out of the zone, at several depths.
Mode 'physics': he is told (intent 'position') to run straight to the nearest point 1 m outside the arc from t=0 (pure movement).
Mode 'cognition': the RB-3.11 behaviour decides (Z-4), everything else frozen, as in test_rb311.
Run from the repo root: python3 native/evidence/rb311scen/zone_exit_scenario.py"""
import sys, math, json
from dataclasses import replace
import pytest
from native import cognition as C, cognition_rb3 as R
from native.rulebook import test_rb311 as T311
from native.rulebook.test_rb36 import rb3
from native.rulebook.test_rb34 import live
from native.rulebook.test_rb39a import field

def run(depth_from_goal, mode, mp, lateral=0.):
    T311.freeze_baselines(mp)
    p = rb3(); s, e, a, t = live(p); Ty = p.types; s.restart = None; e.rb_period_start_open = False
    A = field(s, 'A'); B = field(s, 'B')
    for i, q in enumerate(s.players.values()):
        if q.role != 'archer': q.x, q.y = 60. + (i % 5), 5. + 4. * (i % 20)
    d = A[0]
    ang = math.atan2(lateral, depth_from_goal) if depth_from_goal else 0.
    gx, gy = 0., 50.                      # A defends the goal at x = 0 (as in test_rb311.defender_run)
    d.x, d.y = gx + depth_from_goal, gy + lateral
    carrier = B[1]; carrier.x, carrier.y = 60., 50.
    s.owner = 'B'; e.possession.pp = 'B'; e.possession.tc = 'B'; e.rb.possession = 'B'
    s.ball = Ty.Ball(mode=Ty.BallMode.CONTROLLED, x=carrier.x, y=carrier.y, z=1.5, carrier=carrier.id, control_time=s.now, scoring=True, last_touch='B')
    for q in s.players.values(): q.vx = q.vy = 0.; q.target = (q.x, q.y); p.move[q.id] = (q.x, q.y)
    e.native_sync()
    assert e.zone(d.x, d.y) is not None, 'not inside the zone'
    r = math.hypot(d.x - gx, d.y - gy) or 1e-9; ux, uy = (d.x - gx) / r, (d.y - gy) / r
    if r < 1e-6: ux, uy = 1., 0.
    out_pt = (gx + ux * 21., gy + uy * 21.)
    if mode == 'physics':
        base = C.decide_v2
        def dv2(view, belief):
            i, rr = base(view, belief)
            if getattr(view, 'athlete', None) == d.id: i = replace(i, kind='position', aim=out_pt, target=None, contact=None)
            return i, rr
        mp.setattr(C, 'decide_v2', dv2); mp.setattr(R, 'zone_behavior', lambda v, b, i, r: (i, r))
    t0 = s.live_ms; out_at = None; called = False
    def stop(s_, e_):
        nonlocal out_at, called
        if T311.zu(e_): called = True; return True
        if s_.phase == Ty.Phase.LIVE and e_.zone(d.x, d.y) is None and out_at is None: out_at = s_.live_ms; return True
        return False
    T311.drive_live(p, 200, watch=(d.id,), stop_on=stop)
    vmax = None
    return dict(depth=depth_from_goal, mode=mode, exit_s=None if out_at is None else round((out_at - t0) / 1000, 2),
                called=called, accel=round(getattr(d, 'acceleration', float('nan')) if hasattr(d, 'acceleration') else float('nan'), 2), player=d.id)

if __name__ == '__main__':
    rows = []
    for mode in ('physics', 'cognition'):
        for depth in (1., 5., 10., 15., 19.):
            mp = pytest.MonkeyPatch()
            try: rows.append(run(depth, mode, mp))
            finally: mp.undo()
    p = rb3(); s, e, a, t = live(p); d = field(s, 'A')[0]
    p.capture(s.now); s.now += 300; v, b = p.view(d.id, s.now)
    print(json.dumps(dict(player=d.id, acceleration=v.body.acceleration, top_speed=v.body.maximum_speed, decision_ms=p.config.decision_ms)))
    for r in rows: print(json.dumps(r))
