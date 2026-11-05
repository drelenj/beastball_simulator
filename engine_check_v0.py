"""Do tackling and passing ratings change outcomes?  (a) defender tackling 0.2 vs 0.95, everything else fixed;  (b) pass landing error by passing skill and distance."""
import sys, os, json, math, random, statistics as st, importlib, copy
os.environ.setdefault('RULES_V03', '1'); os.environ['PRISM_I'] = '1'; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scenario_1v2_v0 as SC
p = SC.proc(); P = p['P']; CO = p['CO']; base = copy.deepcopy(P.ROSTER_OVERRIDES)
field = ['A%d' % i for i in range(10)]
def duel(tack_def, N=12, geo=dict(dd=15., sD=0.)):
    res = []
    for i in field:
        for j in ('B0', 'B2', 'B4', 'B6', 'B8'):
            ov = copy.deepcopy(base); ov[j]['tackling'] = tack_def; P.ROSTER_OVERRIDES = ov
            hits = 0; t_ = []
            for sd in range(N):
                a1 = next(k for k in field if k != i); r = SC.run(sd + 1, dict(vc=6., tx=8., ty=6., ids=(i, a1, j, None), dec_ms=99999, **geo), 0.)
                hits += 1 if (r['ev']['tackle_count'] or r['ev']['strip']) else 0; t_.append(r['t_end'])
            res.append(hits / N)
    P.ROSTER_OVERRIDES = base; return st.mean(res)
if __name__ == '__main__':
    out = {}
    for t in (40., 100.):
        out['tackling_%d' % t] = duel(t, N=int(sys.argv[1]) if len(sys.argv) > 1 else 6); print('defender tackling', t, 'tackle rate', round(out['tackling_%d' % t], 3), flush=True)
    m = CO.match.Match(P.configuration(p['st'], 1, P.CALIBRATION)); core = importlib.import_module(CO.match.Match.__module__); rng = random.Random(1)
    print('assume catch_noise', m.assume['catch_noise'], 'pass_aim_error_deg', m.assume['pass_aim_error_deg'])
    out['pass'] = {}
    for d in (10, 25, 40):
        for skill in (.5, .7, .85, .95):
            errs = []
            for _ in range(300):
                o = (50., 50., 1.6); tgt = (50. + d, 50., 1.6); vel = m.ball_velocity(o, tgt, skill, 'pass')
                b = type('B', (), dict(x=o[0], y=o[1], z=o[2], vx=vel[0], vy=vel[1], vz=vel[2], radius=.1075))()
                path = core.predict_path(b, m.assume['gravity'], m.assume['ball_drag'], .7745966692, horizon=4., step=.02)
                pt = min(path, key=lambda r: abs(r[1] - tgt[0]) + 0 * r[3]); errs.append(math.hypot(pt[1] - tgt[0], pt[2] - tgt[1]))
            out['pass']['%d|%.2f' % (d, skill)] = st.mean(errs); print('pass %2d m skill %.2f: mean lateral miss %.2f m' % (d, skill, st.mean(errs)))
    json.dump(out, open('engine_check_v0.json', 'w'))
