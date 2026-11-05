"""Paired probe for defender Judgment in 1v2.  python3 probe_1v2.py [n_scenarios] [workers] [stage]
stage A: lone defender (no teammate).  stage B: a teammate B1 who marks the threat is on the pitch; B0 may or may not see him.
For every scenario all four options are played from identical starts (deterministic).  The defender's belief-based features are computed at the decision time;
Judgment J then picks an option from a menu scored by predicted attack gain, with choice noise (1-J)*SIG and a pull to the habitual option (chase) (1-J)*HAB.
Reported on identical scenarios: mean REALIZED attack gain (0 = stopped, .4 = contained, 1 = got past; lower is better for the defender)."""
import sys, os, json, math, random, subprocess, collections
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
N = int(sys.argv[1]) if len(sys.argv) > 1 else 60; W = int(sys.argv[2]) if len(sys.argv) > 2 else 4; STAGE = sys.argv[3] if len(sys.argv) > 3 else 'A'; SEED0 = int(sys.argv[4]) if len(sys.argv) > 4 else 100
SIG, HAB = .5, .3                      # [P] choice noise (gain units) and habit pull at Judgment 0
PRIOR_DEC_S, SIG_EST = 1.8, .3         # defender's prior on when the carrier acts (s after start) and his uncertainty
JS = (0., .1, .3, .5, .7, .95, 1.)

WORKER = r'''
import sys, os, json, math, random; os.chdir(%r); sys.path.insert(0, %r)
os.environ['PRISM_FIELD'] = '1'
import scenario_1v2_v0 as SC
seed = int(sys.argv[1]); scs = json.loads(sys.argv[2]); out = []
def feats(m, s, sc):
    p = SC._P; S = p['S']; pr = S.fprism.get(sc['ids'][2]); now = s.now / 1000.; d = s.players[sc['ids'][2]]
    f = dict(seen_c=0, seen_t=0, seen_m=0, gap=None, t_contact=None, d_mt=None)
    if pr is None: return f
    bc = pr.bget(sc['ids'][0]); bt = pr.bget(sc['ids'][1]); bm = pr.bget(sc['ids'][3]) if sc['ids'][3] else None
    if bc is not None:
        c = pr.at_bounded(bc, now); v = pr.intent_vel(bc, now); gap = math.hypot(c[0] - d.x, c[1] - d.y); ux, uy = (c[0] - d.x) / max(gap, 1e-6), (c[1] - d.y) / max(gap, 1e-6)
        sp = max(math.hypot(d.vx, d.vy), 8.); closing = sp - (v[0] * ux + v[1] * uy)
        f.update(seen_c=1, gap=gap, t_contact=gap / max(closing, 3.), cx=c[0], cy=c[1])
    if bt is not None:
        t = pr.at_bounded(bt, now); f.update(seen_t=1, tx=t[0], ty=t[1])
    if bm is not None and bt is not None:
        mp = pr.at_bounded(bm, now); f.update(seen_m=1, d_mt=math.hypot(mp[0] - t[0], mp[1] - t[1]))
    return f
for sc in scs:
    row = dict(sc=sc, vals={}, ev={})
    for o in SC.OPTIONS:
        r = SC.run(seed, sc, o, hooks=dict(decide=feats))
        row['vals'][str(o)] = r['beat']; row['ev'][str(o)] = r['f']; row['feat'] = r['chosen']
    out.append(row)
print('RESULT' + json.dumps(out))
''' % (HERE, HERE)

def scenarios(n, stage, seed0=100):
    rng = random.Random(seed0); out = []
    for k in range(n):
        a = rng.sample(range(10), 2); bs = [i for i in range(10) if i not in a]
        sc = dict(vc=rng.uniform(6.5, 8.5), dd=rng.uniform(18, 28), sD=rng.uniform(-3, 3), tx=rng.uniform(2, 10), ty=rng.choice((-1, 1)) * rng.uniform(8, 16), dec_ms=rng.choice((1500, 1800, 2200)),
                  ids=['A0', 'A1', 'B0', None], b1pos=None, b1mode=None)
        if stage == 'B':
            sc['ids'][3] = 'B1'; near = rng.random() < .5
            # teammate near the threat (marks him) or far behind and irrelevant
            sc['b1pos'] = [25. + sc['dd'] * .7 + rng.uniform(-2, 4), 50. + sc['ty'] + (rng.uniform(-4, 4) if near else rng.uniform(-30, 30))]; sc['b1mode'] = 'marks' if near else 'idle'
        out.append(sc)
    return out

def pred_gain(f, J_unused=None):
    """Defender's Inference: predicted attack gain per option from beliefs (chase = gamble on arriving first, cover = contained unless the carrier runs past)."""
    if not f or not f.get('seen_c'): return None
    rem = PRIOR_DEC_S - .4 - f['t_contact']                        # margin by which he arrives before the carrier acts (s)
    P = .5 * (1 + math.erf(rem / (SIG_EST * math.sqrt(2))))       # P(arrive first)
    pm = 0.
    if f.get('seen_m') and f.get('d_mt') is not None: pm = math.exp(-f['d_mt'] / 6.)
    v_chase = (1 - P) * (1 - .6 * pm)
    v_cover = .4 * (1 - .5 * pm)
    return {o: (1 - o) * v_chase + o * v_cover for o in (0., .35, .7, 1.)}

def choose(f, J, rng):
    g = pred_gain(f)
    if g is None: return 0.7                                        # cannot see the carrier: sit in the lane
    sc_ = {o: v + SIG * (1 - J) * rng.gauss(0, 1) - (HAB * (1 - J) if o == 0. else 0.) for o, v in g.items()}
    return min(sc_, key=sc_.get)

if __name__ == '__main__':
    scs = scenarios(N, STAGE, SEED0); chunks = [scs[i::W] for i in range(W)]
    def one(ch):
        o = subprocess.run([sys.executable, '-c', WORKER, '1', json.dumps(ch)], capture_output=True, text=True, timeout=7200)
        l = [x for x in o.stdout.splitlines() if x.startswith('RESULT')]
        return json.loads(l[0][6:]) if l else (print('ERR', o.stderr[-500:]) or [])
    rows = []
    with ThreadPoolExecutor(W) as ex:
        for r in ex.map(one, chunks): rows += r
    json.dump(rows, open(os.path.join(HERE, 'probe_1v2_%s_%d.json' % (STAGE, SEED0)), 'w'))
    print('stage', STAGE, 'scenarios', len(rows))
    opts = (0., .35, .7, 1.)
    for o in opts: print('always f=%.2f  mean gain %.3f' % (o, sum(r['vals'][str(o)] for r in rows) / len(rows)))
    print('oracle (best option each scenario)  %.3f' % (sum(min(r['vals'].values()) for r in rows) / len(rows)))
    rng0 = random.Random(7)
    for J in JS:
        tot = 0.; chose = collections.Counter()
        for k, r in enumerate(rows):
            rr = random.Random(1000 + k); o = choose(r['feat'], J, rr); tot += r['vals'][str(o)]; chose[o] += 1
        print('Judgment %.2f  mean gain %.3f   picks %s' % (J, tot / len(rows), {k: chose[k] for k in sorted(chose)}))
