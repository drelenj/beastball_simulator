"""Paired block test: same style, same roster, same seeds, sides swapped; only block_rate differs (0 vs X).  python3 block_test.py seeds"""
import sys, os, json, random, collections, multiprocessing as mp
os.environ.setdefault('RULES_V03', '1'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selfplay_v0 as SP
N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
champ = json.load(open('selfplay_run_v3.json'))['champ']
def duel(pool, gx, gy, seeds):
    jobs = []
    for sd in seeds: jobs += [(gx, gy, sd, 60), (gy, gx, sd, 60)]
    res = pool.map(SP.game, jobs); per = []
    for i, sd in enumerate(seeds):
        a, b = res[2 * i], res[2 * i + 1]           # a: gx is team A; b: gx is team B
        fx = SP.fit(a['s'], 'A', 'B') + SP.fit(b['s'], 'B', 'A')
        pts = a['s']['A']['points_flat_total'] - a['s']['B']['points_flat_total'] + b['s']['B']['points_flat_total'] - b['s']['A']['points_flat_total']
        bl = a['s']['A']['blocks_offence'] + b['s']['B']['blocks_offence']; blo = a['s']['B']['blocks_offence'] + b['s']['A']['blocks_offence']
        per.append(dict(seed=sd, fit=fx, pts=pts, blocks_x=bl, blocks_y=blo))
    return per
def ci(v, rng=random.Random(3)):
    m = sum(v) / len(v); bs = sorted(sum(rng.choice(v) for _ in v) / len(v) for _ in range(2000)); return m, bs[50], bs[1949]
if __name__ == '__main__':
    pool = mp.Pool(2, maxtasksperchild=8); out = {}
    seeds = list(range(5000, 5000 + N))
    for label, g in (('baseline style', SP.clampg(SP.BASE)), ('evolved champion style', SP.clampg(champ))):
        for rate in (.66, 1.0):
            gx = dict(g, block_rate=rate, block_reach=8.); gy = dict(g, block_rate=0.)
            per = duel(pool, gx, gy, seeds); f = ci([p['fit'] for p in per]); pts = ci([p['pts'] for p in per])
            out['%s | block %.2f vs 0' % (label, rate)] = dict(fit=f, pts=pts, blocks_x=sum(p['blocks_x'] for p in per) / len(per) / 2, blocks_y=sum(p['blocks_y'] for p in per) / len(per) / 2, n_games=2 * len(per))
            print(label, 'block %.2f vs 0: points diff per seed-pair %+.2f  CI [%+.2f, %+.2f] | offence blocks per game %.1f vs %.1f' % (rate, pts[0], pts[1], pts[2], out['%s | block %.2f vs 0' % (label, rate)]['blocks_x'], out['%s | block %.2f vs 0' % (label, rate)]['blocks_y']), flush=True)
            json.dump(out, open('block_test.json', 'w'))
