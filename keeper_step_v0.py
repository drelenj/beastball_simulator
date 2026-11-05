import sys, os, json, multiprocessing as mp
os.environ['NETR'] = '3'; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import keeper_drill_v0 as K
if __name__ == '__main__':
    cases = [(D, v, phi, sd) for D in (10, 20, 30) for v in (20., 45., 80.) for phi in (15., 30., 45., 60., 90., 120., 135., 150., 165.) for sd in (1, 2, 3)]
    for f in ('0.95', '0.7', '0.5', '0.3', '0.1'):
        os.environ['KEEPER_STEP_FRAC'] = f
        with mp.Pool(2, maxtasksperchild=60) as pool: res = pool.map(K.one, cases, chunksize=9)
        g = {}
        for a, r in res: g.setdefault((a[0], a[1]), []).append(1 if r and r['goal'] else 0)
        print('step frac %-4s' % f, ' '.join('D%d@%.0f:%.2f' % (D, v, sum(x) / len(x)) for (D, v), x in sorted(g.items())), flush=True)
