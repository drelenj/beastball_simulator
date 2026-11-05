"""Constrained self-play, v0.  Two teams play the real Pocket engine under PRISM I; the only thing that evolves is each team's style genome = the engine's own Tactics fields.
Nothing models behaviour: ratings, physics, rules and perception are fixed; the genome only sets how the team's existing policy leans (width, support, pace, pass pressure, shoot distance,
escort, patience, hunt count, risk, defence shape, arrow interval, arrow reserve).  Scoring is the experiment's flat scoring (goal 2 / half goal 1 overlay) via drill_score_v0.
Search: (1+lambda) evolution strategy.  A challenger plays the champion AND a rotating preset opponent, sides swapped, same seeds for every challenger of a generation (paired).
A challenger must beat the champion on a confirmation set of fresh seeds before it replaces him.  Exploits are flagged, never patched.
usage: python3 selfplay_v0.py [generations] [challengers] [live_seconds]   -> selfplay_run.json, selfplay_log.txt
"""
import sys, os, json, random, time, math, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
FIELDS = dict(width=(10, 45), support=(3, 18), pace=(.3, 1.), pass_pressure=(1, 9), shoot_distance=(8, 32), escort=(0, 4), escort_spacing=(1.8, 4), possession_patience=(0, 1), hunt_count=(1, 6), risk=(0, 1), arrow_interval=(4, 26), reserve=(0, 4), block_rate=(0, 1), block_reach=(4, 20), dribble_rate=(0, 1), skip_rate=(0, 1), bounce_shot_rate=(0, 1))
INTS = ('escort', 'hunt_count', 'reserve'); DEFENSES = ('adaptive', 'hunt', 'man', 'zone')   # block_rate / block_reach feed block_option_v0, the rest are Tactics fields
BASE = dict(width=25, support=9, pace=.75, pass_pressure=5, shoot_distance=23, escort=1, escort_spacing=2.5, possession_patience=.5, hunt_count=3, risk=.5, arrow_interval=18, reserve=2, block_rate=0., block_reach=10., dribble_rate=0., skip_rate=0., bounce_shot_rate=0., defense='adaptive')
OPP = ['speed', 'contact', 'wide', 'conservative', 'zone_pressure', 'hunt']      # rotating preset opponents (engine presets, converted to genomes at run time)

def clampg(g):
    g = dict(g)
    for k, (lo, hi) in FIELDS.items(): g[k] = min(hi, max(lo, g[k])); g[k] = int(round(g[k])) if k in INTS else round(float(g[k]), 3)
    return g
def mutate(g, rng, sig=.15):
    g = dict(g)
    for k, (lo, hi) in FIELDS.items():
        if rng.random() < .5: g[k] = g[k] + rng.gauss(0, sig * (hi - lo))
    if rng.random() < .15: g['defense'] = rng.choice(DEFENSES)
    return clampg(g)
def preset(name):
    from dataclasses import asdict
    import pocket4_proto as X
    T = X.install(X.load_pocket()).CORE.policies.TACTICS[name]; d = asdict(T); d.pop('escort_shape', None); return d

# ---- one game (worker) -------------------------------------------------------------------------
_W = {}
def _setup():
    if _W: return _W
    os.environ.setdefault('PRISM_I', '1'); os.environ.setdefault('RULES_V03', '1')
    import tend_check as T, pocket4_proto as X, drill_score_v0 as DS
    P = X.install(X.load_pocket()); CO = P.CORE; Pol = CO.policies.Policy; o = Pol.__init__; GEN = {}
    from dataclasses import replace
    def init(self, team, tac, defense=None):
        g = GEN.get(team)
        if g: tac = replace(tac, **{k: v for k, v in g.items() if k not in ('defense', 'block_rate', 'block_reach', 'dribble_rate', 'skip_rate', 'bounce_shot_rate')}); defense = g.get('defense', defense)
        o(self, team, tac, defense)
    Pol.__init__ = init
    rows = T.G.read_csv('Ala_Lady_Reds_input.csv')
    _W.update(T=T, X=X, DS=DS, P=P, GEN=GEN, rows=rows); return _W

def apply_variant(over, ex, names, variant, team, seed):
    """role ablations for one team: mismatch = position/tendency bundles rotated among the ten field slots; no_tend = every field slot gets the generic TRK tendency;
    identical = every field athlete replaced by the team mean athlete; generic = identical + no_tend."""
    ids = ['%s%d' % (team, i) for i in range(10)]; bench = ['%s%d' % (team, i) for i in range(12, 22)]
    if variant == 'mismatch':
        rng = random.Random(seed); order = list(range(10))
        while any(order[i] == i for i in range(10)): rng.shuffle(order)
        old = {p: (names[p]['position'], names[p].get('report_arch', '')) for p in ids}
        for i, p in enumerate(ids): names[p]['position'], names[p]['report_arch'] = old[ids[order[i]]]
    if variant in ('no_tend', 'generic'):
        for p in ids + bench: names[p]['position'] = 'TRK'; names[p]['report_arch'] = ''
    if variant in ('identical', 'generic'):
        for tab in (over, ex):
            keys = [k for k, v in tab[ids[0]].items() if isinstance(v, float)]
            mean = {k: sum(tab[p][k] for p in ids) / 10. for k in keys}
            for p in ids + bench: tab[p] = dict(tab[p], **mean)

def game(args):
    gA, gB, seed, live_s = args[:4]; mods = args[4] if len(args) > 4 else None; w = _setup(); X, P, DS = w['X'], w['P'], w['DS']; w['GEN'].clear(); w['GEN']['A'] = gA; w['GEN']['B'] = gB
    import block_option_v0 as BO
    import bounce_option_v0 as BN; BN.reset()
    for t_, g_ in (('A', gA), ('B', gB)):
        BO.BG[t_].update(block_rate=g_.get('block_rate', 0.), block_reach=g_.get('block_reach', 10.))
        BN.BG[t_].update(dribble_rate=g_.get('dribble_rate', 0.), skip_rate=g_.get('skip_rate', 0.), bounce_shot_rate=g_.get('bounce_shot_rate', 0.))
    over, ex, names = X.make_rosters(w['rows'], w['rows'], seed)          # same roster both sides: only style differs
    if mods: apply_variant(over, ex, names, mods[0], mods[1], seed)
    kft = float(os.environ.get('KEEPER_FT', '0'))
    if kft:   # match setting: both Keepers at this height (ft); reach .46 x height
        for kid in ('A10', 'B10'):
            if kid in over: over[kid]['height'] = round(kft * .3048, 4); over[kid]['reach'] = round(.46 * kft * .3048, 4)
    X.C2.cl.BASE_HAZ = 1.7e-4 * X.INJ_HAZ
    S = X.S; S.tend = {pid: X.PT.Tend(n['position'] if n['position'] in X.PT.POSITIONS else 'TRK', n.get('report_arch', '')) for pid, n in names.items()}
    S.on = set(X.SYSTEMS); S.shape = 'sphere'; S.extras = ex; S.names = names; S.seed = seed; S.prism_r = X.PRAT.assign(over, names)
    st = dict(P.SETTINGS); st['save_events'] = False; st.update(period_seconds=live_s, periods=1, overtime_seconds=10)
    P.ROSTER_OVERRIDES = P.validate_roster(over) and over
    t = time.time(); result, log = P.run_match(st, seed=seed, progress=False)
    import block_option_v0 as BO
    blk = BO.summary(log); BO.PAIRS.clear(); BO._HOLD.clear()
    return dict(seed=seed, s=DS.score(log), engine=result['score'], el=round(time.time() - t, 1), blk=blk)

def fit(s, me, other):
    """pre-declared fitness for team `me` (flat points diff + tiny distance term to break ties)"""
    return (s[me].get('points_flat_total', 0) - s[other].get('points_flat_total', 0)) + .005 * (s[me].get('distance_progressed_m', 0) - s[other].get('distance_progressed_m', 0))

def log(msg, f=[None]):
    if f[0] is None: f[0] = open(os.path.join(HERE, 'selfplay_log.txt'), 'a')
    f[0].write(msg + '\n'); f[0].flush(); print(msg, flush=True)

def main():
    import multiprocessing as mp
    G = int(sys.argv[1]) if len(sys.argv) > 1 else 10; K = int(sys.argv[2]) if len(sys.argv) > 2 else 6; LIVE = int(sys.argv[3]) if len(sys.argv) > 3 else 60; NC = int(sys.argv[4]) if len(sys.argv) > 4 else 2; TAG = sys.argv[5] if len(sys.argv) > 5 else ''
    rng = random.Random(7); pool = mp.Pool(2, maxtasksperchild=8); champ = clampg(BASE); presets = {n: clampg(dict(BASE, **{k: v for k, v in preset(n).items() if k in FIELDS or k == 'defense'})) for n in OPP}
    run = dict(champ0=champ, gens=[], live_s=LIVE); seedc = [1000]
    def fresh(n): seedc[0] += n; return list(range(seedc[0] - n, seedc[0]))
    def duel(gx, gy, seeds):     # gx vs gy, sides swapped per seed: returns total fitness for gx and the raw per-team stats
        jobs = []
        for sd in seeds: jobs += [(gx, gy, sd, LIVE), (gy, gx, sd, LIVE)]
        res = pool.map(game, jobs); fx = 0.; agg = []
        for (a, b, sd, _), r in zip(jobs, res):
            me, ot = ('A', 'B') if a is gx else ('B', 'A'); fx += fit(r['s'], me, ot); agg.append((me, r['s']))
        return fx, agg
    t0 = time.time()
    for gen in range(1, G + 1):
        opp = OPP[(gen - 1) % len(OPP)]; seeds = fresh(1); chal = [mutate(champ, rng) for _ in range(K)]; rows = []
        for i, c in enumerate(chal):
            f1, _ = duel(c, champ, seeds); f2, _ = duel(c, presets[opp], seeds); rows.append((f1 + f2, f1, f2, i))
        rows.sort(reverse=True); best = chal[rows[0][3]]; msg = 'gen %2d opp=%-13s best fit %+.2f (vs champ %+.2f, vs %s %+.2f)' % (gen, opp, rows[0][0], rows[0][1], opp, rows[0][2])
        # confirmation on fresh seeds: must beat the champion AND not lose to the rotating opponent overall
        cs = fresh(NC); fc, agg = duel(best, champ, cs); fo, _ = duel(best, presets[opp], cs); acc = (fc > 0 and fc + fo > 0)
        msg += ' | confirm vs champ %+.2f vs opp %+.2f -> %s  [%.0fs]' % (fc, fo, 'ACCEPT' if acc else 'reject', time.time() - t0); log(msg)
        run['gens'].append(dict(gen=gen, opp=opp, best=best, fit=rows[0][:3], confirm=(fc, fo), accepted=acc))
        if acc: champ = best; log('   champion: ' + json.dumps(champ))
        json.dump(dict(run, champ=champ), open(os.path.join(HERE, 'selfplay_run%s.json' % TAG), 'w'))
    # final holdout: champion vs original baseline and vs every preset, fresh seeds
    hs = fresh(NC * 2); out = {}
    for name, g in [('baseline', clampg(BASE))] + list(presets.items()):
        f, agg = duel(champ, g, hs); out[name] = round(f, 2)
    log('HOLDOUT champion vs: ' + json.dumps(out)); run['holdout'] = out; run['champ'] = champ
    # style readout from the champion's holdout games vs baseline (for the exploit flags)
    _, agg = duel(champ, clampg(BASE), fresh(NC * 2)); tot = collections.Counter(); 
    for me, s in agg:
        for k, v in s[me].items():
            if isinstance(v, (int, float)): tot[k] += v
    run['style_readout'] = dict(tot); json.dump(run, open(os.path.join(HERE, 'selfplay_run%s.json' % TAG), 'w')); log('done in %.0fs' % (time.time() - t0))
if __name__ == '__main__': main()
