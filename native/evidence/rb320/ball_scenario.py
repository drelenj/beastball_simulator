"""RB-3.20 Part 1A: free-ball ground physics scenario (no match). A ball is released at 20, 35 and 50 m/s from 1.5 m,
level and at the normal pass launch angle (launch_for to a target at 1.6 m at the distance for which that speed is the
RB/3 release speed: speed x 0.4 s), nobody near, and the engine steps it (native-rb/3 port, real match kernel).
Run from the repo root: python3 -m native.evidence.rb320.ball_scenario [--json out.json]"""
import json, math, sys
from native.rulebook.test_rb36 import rb3
from native.rulebook.test_rb34 import live


def trial(speed, mode, max_s=8., fix=True):
    p = rb3(rb320_exact_bounce=fix); s, e, a, t = live(p); T = p.types; s.restart = None; e.rb_period_start_open = False
    for i, q in enumerate(q for q in s.players.values() if q.role != 'archer'):
        q.x, q.y = 2. + (i % 6) * .8, 96. + (i // 6) * .8; q.vx = q.vy = 0.; q.target = (q.x, q.y); p.move[q.id] = (q.x, q.y)
    x0, y0, z0 = 2., 50., 1.5
    if mode == 'level':
        v = (speed, 0., 0.)
    else:
        ans = p.geom.launch_for((x0, y0, z0), (x0 + speed * .4, y0, 1.6), speed, 9.81, .015); v = ans[0]
    s.owner = 'A'; e.possession.pp = 'A'; e.possession.tc = 'A'; e.rb.possession = 'A'
    s.ball = T.Ball(mode=T.BallMode.PASS, x=x0, y=y0, z=z0, carrier=None, control_time=0, scoring=False, last_touch='A', vx=v[0], vy=v[1], vz=v[2])
    e.native_sync(); t0 = s.now; n0 = len(e.log)
    rows = []; bounces = []; first = None; prev_vz = s.ball.vz; out = None; stop = None
    while (s.now - t0) / 1000. < max_s:
        b = s.ball; before = (b.vx, b.vy, b.vz, b.z)
        p.step(); b = s.ball; tt = (s.now - t0) / 1000.
        sp = math.hypot(b.vx, b.vy)
        rows.append((round(tt, 3), round(b.x - x0, 3), round(b.z, 3), round(sp, 3), round(b.vz, 3)))
        if before[2] < -1e-9 and (b.vz > 0 or (b.vz == 0. and b.z <= b.radius + 1e-6)):
            hsp = math.hypot(before[0], before[1])
            if first is None: first = dict(t_s=tt, speed_h=round(hsp, 2), vz_in=round(before[2], 2), x_m=round(b.x - x0, 2), contact='bounce' if b.vz > 0 else 'roll')
            if b.vz > 0: bounces.append(dict(t_s=tt, apex_m=round(b.z + b.vz * b.vz / (2 * 9.81) - b.radius, 4),
                                             h_in=round(hsp, 2), h_out=round(sp, 2), h_ratio=round(sp / hsp, 3) if hsp else None))
        if any(x['event'] in ('boundary', 'rb_boundary') for x in e.log[n0:]) or s.phase != T.Phase.LIVE:
            out = dict(t_s=tt, x_m=round(b.x - x0, 2)); break
        if sp < .05 and b.z <= b.radius + 1e-6 and b.vz == 0:
            stop = dict(t_s=tt, x_m=round(b.x - x0, 2)); break
        n0 = len(e.log)
    for i in range(1, len(bounces)):
        bounces[i]['e_from_apex'] = round((bounces[i]['apex_m'] / bounces[i - 1]['apex_m']) ** .5, 4)
    at = lambda T_: next((r[1] for r in rows if r[0] >= T_), None)
    return dict(speed=speed, mode=mode, launch=[round(c, 3) for c in v], first_ground=first, bounces=bounces,
                distance_at=dict(s1=at(1.), s2=at(2.), s3=at(3.)), stopped=stop, left_field=out,
                height_vs_time=[r for r in rows if abs((r[0] * 10) - round(r[0] * 10)) < 1e-6][:60])


if __name__ == '__main__':
    res = []
    for fix in (False, True):
        print('== rb320_exact_bounce', fix)
        for sp in (20., 35., 50.):
            for m in ('level', 'pass_angle'):
                r = trial(sp, m, fix=fix); r['fix'] = fix; res.append(r)
                print(json.dumps({k: v for k, v in r.items() if k != 'height_vs_time'}))
    if '--json' in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1)
