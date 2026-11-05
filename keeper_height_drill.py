import sys, os, json, multiprocessing as mp, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NETR'] = '5.5'
import keeper_drill_v0 as K
if __name__ == '__main__':
    out = {}
    Ds = (10, 20, 30, 40, 60); phis = [i * 15. for i in range(13)]
    for ft in (9, 10, 11, 12):
        os.environ['KFT'] = str(ft)
        jobs = [(D, v, phi, sd) for v in (67.1, 100.6) for D in Ds for phi in phis for sd in (1, 2)]
        with mp.Pool(2, maxtasksperchild=40) as pool: res = pool.map(K.one, jobs, chunksize=8)
        agg = collections.defaultdict(list)
        for a, r in res:
            if r: agg[(a[1], a[0])].append(1 if r['goal'] else 0)
        for (v, D), x in sorted(agg.items()): out['%d|%.0f|%d' % (ft, v, D)] = dict(goal=sum(x) / len(x), n=len(x))
        print('ft', ft, 'done', flush=True); json.dump(out, open('keeper_height_drill.json', 'w'))
