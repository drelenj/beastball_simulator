"""Goalkeeping sweep: the keeper drill (shot on a net, 10 ft Keeper, net 5.5) at three Goalkeeping ratings; saves per shot set.  usage: python3 gk_sweep.py"""
import os, sys, json, subprocess
PROG = r'''
import os, sys, json
sys.path.insert(0, %r); import keeper_drill_v0 as K
import multiprocessing as mp
jobs = [(D, v, phi, sd) for v in (45.,) for D in (25, 35) for phi in range(0, 181, 30) for sd in (1, 2, 3)]
with mp.Pool(2, maxtasksperchild=10) as pool: res = pool.map(K.one, jobs, chunksize=2)
g = [r['goal'] for a, r in res if r]; print('RESULT' + json.dumps(dict(n=len(g), goals=sum(g))))
''' % os.path.dirname(os.path.abspath(__file__))
if __name__ == '__main__':
    for gk in (.4, .7, .98):
        base = {k: .7 for k in ('vision', 'awareness', 'clarity', 'reaction', 'focus', 'instinct', 'anticipation', 'judgment')}; base['goalkeeping'] = gk
        env = dict(os.environ, PRISM_JSPLIT='1', PRISM_KEEPER='1', KP_MINOBS='3', CATCH_V2='1', NETR='5.5', NET_R='5.5', KFT='10', KEEPER_FT='10', PRISM_KEEPER_RATINGS=json.dumps(base))
        o = subprocess.run([sys.executable, '-c', PROG], env=env, capture_output=True, text=True, timeout=3000)
        l = [x for x in o.stdout.splitlines() if x.startswith('RESULT')]
        print('Goalkeeping %.2f' % gk, json.loads(l[0][6:]) if l else o.stderr[-300:], flush=True)
