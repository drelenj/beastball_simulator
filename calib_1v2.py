"""Calibrate the defender's Inference (predicted attack gain per option) on TRAIN scenarios, then score Judgment on a held-out TEST set.
python3 calib_1v2.py   (uses probe_1v2_A_100/200.json as train, probe_1v2_A_300.json as test)"""
import json, math, random, collections, sys, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OPTS = (0., .35, .7, 1.); DECS = (1.5, 1.8, 2.2)
SIG, HAB = .5, .3; JS = (0., .1, .3, .5, .7, .95, 1.)
def load(stage, seeds):
    rows = []
    for sd in seeds:
        f = os.path.join(HERE, 'probe_1v2_%s_%d.json' % (stage, sd)) if sd != 100 else os.path.join(HERE, 'probe_1v2_%s.json' % stage)
        rows += json.load(open(f))
    return [r for r in rows if r['feat'].get('seen_c')]
def phi(d, t, m=0.): return [1., d, t, d * t, d * d, m, m * t]
def fit(rows, stage):
    co = {}
    for o in OPTS:
        X = np.array([phi(r['sc']['dec_ms'] / 1000., r['feat']['t_contact'], mate(r, stage)) for r in rows]); y = np.array([r['vals'][str(o)] for r in rows])
        co[o] = np.linalg.lstsq(X, y, rcond=None)[0]
    return co
def mate(r, stage):
    if stage != 'B': return 0.
    f = r['feat']; return math.exp(-f['d_mt'] / 6.) if f.get('seen_m') and f.get('d_mt') is not None else 0.
def pred(co, r, stage):
    t = r['feat']['t_contact']; m = mate(r, stage)
    return {o: sum(float(np.dot(co[o], phi(d, t, m))) for d in DECS) / len(DECS) for o in OPTS}
def choose(g, J, rng):
    s = {o: v + SIG * (1 - J) * rng.gauss(0, 1) - (HAB * (1 - J) if o == 0. else 0.) for o, v in g.items()}
    return min(s, key=s.get)
def report(rows, co, stage, label):
    print('==', label, 'n =', len(rows))
    for o in OPTS: print('  always f=%.2f  %.3f' % (o, sum(r['vals'][str(o)] for r in rows) / len(rows)))
    print('  oracle %.3f' % (sum(min(r['vals'].values()) for r in rows) / len(rows)))
    res = {}
    for J in JS:
        tot = 0.; pk = collections.Counter()
        for k, r in enumerate(rows):
            o = choose(pred(co, r, stage), J, random.Random(1000 + k)); tot += r['vals'][str(o)]; pk[o] += 1
        res[J] = tot / len(rows); print('  Judgment %.2f  gain %.3f  picks %s' % (J, res[J], {a: pk[a] for a in sorted(pk)}))
    return res
if __name__ == '__main__':
    stage = sys.argv[1] if len(sys.argv) > 1 else 'A'
    tr = load(stage, [100, 200]); te = load(stage, [300]); co = fit(tr, stage)
    report(tr, co, stage, 'TRAIN (fit on these)'); report(te, co, stage, 'TEST (held out)')
