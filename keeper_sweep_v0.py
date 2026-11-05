import sys, os, json, multiprocessing as mp, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import keeper_drill_v0 as K
if __name__ == '__main__':
    Ds = (20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 98); phis = [i * 7.5 for i in range(25)]
    jobs = [(D, v, phi, sd) for v in (67.1, 134.1) for D in Ds for phi in phis for sd in (1, 2, 3)]
    with mp.Pool(2, maxtasksperchild=40) as pool: res = pool.map(K.one, jobs, chunksize=6)
    agg = collections.defaultdict(lambda: collections.defaultdict(list))
    for a, r in res:
        if r: agg[(a[1], a[0])][a[2]].append(1 if r['goal'] else 0)
    out = {}
    for (v, D), row in sorted(agg.items()):
        rates = {phi: sum(x) / len(x) for phi, x in row.items()}
        out['%.0f|%d' % (v, D)] = dict(all_targets_score=sum(1 for x in rates.values() if x == 1.), n=len(rates), best_targets=[phi for phi, x in rates.items() if x == 1.], mean_score_rate=sum(rates.values()) / len(rates), worst=min(rates.values()))
        o = out['%.0f|%d' % (v, D)]; print('v=%3.0f D=%2d: %2d/%d placements score every time (3/3); mean %.2f; worst %.2f; always-scoring angles %s' % (v, D, o['all_targets_score'], o['n'], o['mean_score_rate'], o['worst'], sorted(o['best_targets'])[:12]), flush=True)
    json.dump(out, open('keeper_sweep_v0.json', 'w'))
