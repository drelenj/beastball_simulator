"""In-play style shooting: a power-70 shooter (101 m/s max) of accuracy 40/70/100 (touch 70) chooses ball speed and aim; net 6 m x 3 m.  Per (accuracy, distance): best speed and its goal rate.  Aim = the best of 8 corner/low points."""
import sys, os, json, multiprocessing as mp, collections
os.environ['NETR'] = os.environ.get('NETR', '3'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import keeper_drill_v0 as K
if __name__ == '__main__':
    Ds = (10, 15, 20, 25, 30, 40, 50); Vs = (20., 30., 45., 60., 80., 100.6); phis = (15., 30., 45., 60., 120., 135., 150., 165.); As = (40, 70, 100); NS = 6
    jobs = [(D, v, phi, sd, A, 70) for A in As for D in Ds for v in Vs for phi in phis for sd in range(1, NS + 1)]
    with mp.Pool(2, maxtasksperchild=40) as pool: res = pool.map(K.one, jobs, chunksize=12)
    agg = collections.defaultdict(list)
    for a, r in res:
        if r: agg[(a[4], a[0], a[1], a[2])].append(1 if r['goal'] else 0)
    out = {}
    for A in As:
        for D in Ds:
            best = None
            for v in Vs:
                rates = {phi: sum(agg[(A, D, v, phi)]) / max(1, len(agg[(A, D, v, phi)])) for phi in phis}; ph = max(rates, key=rates.get)
                if best is None or rates[ph] > best[0]: best = (rates[ph], v, ph, sum(rates.values()) / len(rates))
            out['%d|%d' % (A, D)] = dict(goal_rate=best[0], speed=best[1], aim=best[2], mean_over_aims=best[3])
            print('accuracy %3d  D=%2d m: best aim %3.0f deg at %5.1f m/s -> goal rate %.2f (all aims avg %.2f)' % (A, D, best[2], best[1], best[0], best[3]), flush=True)
    json.dump(out, open('keeper_shot_v1.json', 'w'))
