import sys, os, json, multiprocessing as mp
os.environ['NETR'] = '3'; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import keeper_drill_v0 as K
if __name__ == '__main__':
    variants = {'base': '', 'extension .45': 'keeper_extension_frac=.45', 'dive lean .2 + attempt margin 3': 'keeper_dive_lean=.2,keeper_attempt_margin_m=3.', 'dive time .5': 'keeper_dive_time_s=.5', 'pushoff .8': 'keeper_pushoff_frac=.8', 'all of these': 'keeper_extension_frac=.45,keeper_dive_lean=.2,keeper_attempt_margin_m=3.,keeper_dive_time_s=.5,keeper_pushoff_frac=.8'}
    cases = [(D, v, phi, sd) for D in (10, 20) for v in (20., 45.) for phi in (15., 30., 45., 60., 90., 120., 135., 150., 165.) for sd in (1, 2, 3)]
    for name, cal in variants.items():
        os.environ['CAL'] = cal
        with mp.Pool(2, maxtasksperchild=40) as pool: res = pool.map(K.one, cases, chunksize=9)
        g = {}
        for a, r in res: g.setdefault((a[0], a[1]), []).append(1 if r and r['goal'] else 0)
        print('%-34s' % name, ' '.join('D%d@%.0f: %.2f' % (D, v, sum(x) / len(x)) for (D, v), x in sorted(g.items())), flush=True)
