import sys, os, json, multiprocessing as mp
os.environ['NETR'] = '3'; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import keeper_drill_v0 as K
if __name__ == '__main__':
    sel = json.load(open('keeper_shot_v1.json')); NS = 30; jobs = []
    for k, v in sel.items():
        A, D = map(int, k.split('|')); jobs += [(D, v['speed'], v['aim'], 100 + sd, A, 70) for sd in range(NS)]
    with mp.Pool(2, maxtasksperchild=40) as pool: res = pool.map(K.one, jobs, chunksize=10)
    import collections; agg = collections.defaultdict(list)
    for a, r in res:
        if r: agg[(a[4], a[0])].append(1 if r['goal'] else 0)
    for A in (40, 70, 100):
        print('accuracy', A, ' '.join('%dm:%.2f@%.0f' % (D, sum(agg[(A, D)]) / len(agg[(A, D)]), sel['%d|%d' % (A, D)]['speed']) for D in (10, 15, 20, 25, 30, 40, 50)))
