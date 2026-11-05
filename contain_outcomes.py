"""Contain vs drive: outcomes from the engine's own log (no hooks).  python3 contain_outcomes.py [seeds] [workers]
For each c3_containment episode: what followed for that carrier (zone expiry = turnover, grounding = first tackle taken, hold ended, strip, goal) and the context."""
import sys, os, json, subprocess, collections
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
SEEDS = [int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else '1,2,3,4,5,6').split(',')]; W = int(sys.argv[2]) if len(sys.argv) > 2 else 4
RUN = r'''
import sys, os, json, collections
seed = int(sys.argv[1]); os.chdir(%r); sys.path.insert(0, %r)
import tend_check as T, pocket4_proto as X
P = X.install(X.load_pocket())
over, ex, names = X.make_rosters(T.G.read_csv('Ala_Lady_Reds_input.csv'), T.G.read_csv('Xenar_Dzaku_input.csv'), seed)
r, log, el = X.run(P, over, ex, names, off=(), seed=seed, short=True)
ev = collections.Counter(e['event'] for e in log)
want = ('c3_containment', 'c3_descent_start', 'c3_grounding', 'attacking_zone_expiry', 'c3_hold_end', 'strip', 'goal', 'possession_change')
rows = [dict(i=i, ev=e['event'], t=e.get('t', e.get('now')), d=e.get('data', {})) for i, e in enumerate(log) if e['event'] in want]
print('RESULT' + json.dumps(dict(counts={k: ev[k] for k in want}, rows=rows[:4000])))
''' % (HERE, HERE)
def one(sd):
    o = subprocess.run([sys.executable, '-c', RUN, str(sd)], capture_output=True, text=True, timeout=1800)
    l = [x for x in o.stdout.splitlines() if x.startswith('RESULT')]
    return sd, (json.loads(l[0][6:]) if l else {'err': o.stderr[-400:]})
tot = collections.Counter(); eps = []
with ThreadPoolExecutor(W) as ex:
    for sd, d in ex.map(one, SEEDS):
        if 'err' in d: print('ERR', sd, d['err']); continue
        for k, v in d['counts'].items(): tot[k] += v
        rows = d['rows']
        for j, r in enumerate(rows):
            if r['ev'] != 'c3_containment': continue
            nxt = [x['ev'] + (':' + str(x['d'].get('manner', x['d'].get('cause', ''))) if x['ev'] in ('c3_grounding', 'c3_hold_end') else '') for x in rows[j + 1:j + 8] if x['ev'] != 'c3_containment'][:4]
            eps.append(dict(seed=sd, zone_left=r['d'].get('zone_remaining_ms'), grip=r['d'].get('grip'), actor=r['d'].get('actor'), target=r['d'].get('target'), then=nxt))
print('totals', dict(tot)); print('containment episodes', len(eps))
c = collections.Counter(tuple(e['then'][:2]) for e in eps)
for k, v in c.most_common(12): print(v, k)
json.dump(eps, open(os.path.join(HERE, 'contain_episodes.json'), 'w'))
