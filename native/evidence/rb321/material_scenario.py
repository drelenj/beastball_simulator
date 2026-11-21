"""RB-3.21 ball-material scenario in the real native-rb/3 engine (no match): 20/35/50 m/s releases from 1.5 m, level and at the
normal pass launch angle (launch_for to 1.6 m at speed x 0.4 s), nobody near; and a 58 m/s level shot's speed at 10/20/30 m.
Also the forecast check: geometry.predict_path and Match.c4c_path positions at 1 s vs the engine.
Run from the repo root: python3 -m native.evidence.rb321.material_scenario [--json out.json]"""
import json, math, sys
from native.rulebook.test_rb36 import rb3
from native.rulebook.test_rb34 import live


def setup(p, x0=2., y0=50., far=True):
    s, e, a, t = live(p); T = p.types; s.restart = None; e.rb_period_start_open = False
    for i, q in enumerate(q for q in s.players.values() if q.role != 'archer'):
        q.x, q.y = 2. + (i % 6) * .8, 96. + (i // 6) * .8; q.vx = q.vy = 0.; q.target = (q.x, q.y); p.move[q.id] = (q.x, q.y)
    s.owner = 'A'; e.possession.pp = 'A'; e.possession.tc = 'A'; e.rb.possession = 'A'
    return s, e, T


def release(p, speed, mode, x0=2., y0=50., z0=1.5):
    s, e, T = setup(p)
    v = (speed, 0., 0.) if mode == 'level' else p.geom.launch_for((x0, y0, z0), (x0 + speed * .4, y0, 1.6), speed, 9.81, .015)[0]
    s.ball = T.Ball(mode=T.BallMode.PASS, x=x0, y=y0, z=z0, carrier=None, control_time=0, scoring=False, last_touch='A', vx=v[0], vy=v[1], vz=v[2])
    e.native_sync()
    return s, e, T, v


def trial(speed, mode, max_s=12., **cfg):
    p = rb3(**cfg); s, e, T, v = release(p, speed, mode)
    b = s.ball; fc = p.geom.predict_path(b, 9.81, .015, .7746, horizon=1.0, step=.05)[-1]
    kc = p.m.c4c_path(b, horizon=1.0)
    kc = min(kc, key=lambda r: abs(r[0] - 1.0))
    t0 = s.now; n0 = len(e.log); at = {}; rest = None; out = None; pos1 = None
    while (s.now - t0) / 1000. < max_s:
        p.step(); b = s.ball; tt = round((s.now - t0) / 1000., 3)
        for T_ in (1., 2., 3.):
            if abs(tt - T_) < 1e-6: at[f's{int(T_)}'] = round(b.x - 2., 2)
        if abs(tt - 1.) < 1e-6: pos1 = (b.x, b.y, b.z)
        if any(x['event'] in ('boundary', 'rb_boundary') for x in e.log[n0:]) or s.phase != T.Phase.LIVE:
            out = dict(t_s=tt, x_m=round(b.x - 2., 2)); break
        if math.hypot(b.vx, b.vy) < 1e-9 and b.z <= b.radius + 1e-6 and b.vz == 0:
            rest = dict(t_s=tt, x_m=round(b.x - 2., 2)); break
        n0 = len(e.log)
    fe = None if pos1 is None else dict(predict_path_err_m=round(math.dist(pos1, fc[1:]), 3), c4c_path_err_m=round(math.dist(pos1, kc[1:]), 3))
    return dict(speed=speed, mode=mode, launch=[round(c, 3) for c in v], distance_at=at, rest=rest, left_field=out, forecast_at_1s=fe)


def shot(speed=58., **cfg):
    p = rb3(**cfg); s, e, T = setup(p)
    s.ball = T.Ball(mode=T.BallMode.PASS, x=2., y=50., z=1.5, carrier=None, control_time=0, scoring=False, last_touch='A', vx=speed, vy=0., vz=0.)
    from native.rulebook import ball_material as BM
    P = BM.params(p.config); st = (2., 50., 1.5, speed, 0., 0.); out = {}
    while st[0] < 32.:
        st, _, g = BM.fly(st, .005, P, .1075, stop_at_ground=True)
        for d in (10., 20., 30.):
            if f'{int(d)}m' not in out and st[0] - 2. >= d:
                out[f'{int(d)}m'] = round(math.sqrt(st[3] ** 2 + st[4] ** 2 + st[5] ** 2) / speed, 4)
        if g: break
    return dict(shot_speed=speed, speed_fraction_at=out)


if __name__ == '__main__':
    res = [trial(sp, m) for sp in (20., 35., 50.) for m in ('level', 'pass_angle')] + [shot()]
    for r in res: print(json.dumps(r))
    if '--json' in sys.argv: json.dump(res, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1)
