import sys, os, json, multiprocessing as mp, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import keeper_drill_v0 as K
if __name__ == '__main__':
    Ds = (5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90); phis = [i * 15. for i in range(13)]; out = {}
    for R in (6., 5., 4., 3., 2.5, 2.):
        os.environ['NETR'] = str(R)
        jobs = [(D, v, phi, sd) for v in (67.1, 100.6, 134.1) for D in Ds for phi in phis for sd in (1, 2)]
        with mp.Pool(2, maxtasksperchild=40) as pool: res = pool.map(K.one, jobs, chunksize=8)
        agg = collections.defaultdict(lambda: collections.defaultdict(list))
        for a, r in res:
            if r: agg[(a[1], a[0])][a[2]].append(1 if r['goal'] else 0)
        for (v, D), row in sorted(agg.items()):
            rates = {phi: sum(x) / len(x) for phi, x in row.items()}
            out['%g|%.0f|%d' % (R, v, D)] = dict(all=sum(1 for x in rates.values() if x == 1.), n=len(rates), any_sure=sum(1 for x in rates.values() if x == 1.) > 0, mean=sum(rates.values()) / len(rates))
        print('net radius', R, 'done', flush=True); json.dump(out, open('keeper_net_v0.json', 'w'))
