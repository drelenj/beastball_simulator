"""Tests for the installed individual layer (PRISM_I=1).  python3 test_prism_install.py   (each game in its own subprocess: flags are read at import)."""
import os, sys, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
RUN = r'''
import sys, os, json, collections
seed = int(sys.argv[1]); os.chdir(%r); sys.path.insert(0, %r)
import tend_check as T, pocket4_proto as X
P = X.install(X.load_pocket())
over, ex, names = X.make_rosters(T.G.read_csv('Ala_Lady_Reds_input.csv'), T.G.read_csv('Xenar_Dzaku_input.csv'), seed)
r, log, el = X.run(P, over, ex, names, off=(), seed=seed, short=True)
ev = collections.Counter(e['event'] for e in log); fs = dict(getattr(X.S, 'fstats', {}) or {}); pm = getattr(X.S, 'pm', None)
pr = getattr(X.S, 'prism_r', None)
print('RESULT' + json.dumps(dict(score=r['score'], ev={k: ev[k] for k in ('tackle_count', 'strip', 'possession_change', 'goal')}, f=fs, pm=bool(pm and pm.stats),
      nrat=(len(pr) if pr else 0), keys=(sorted(next(iter(pr.values()))) if pr else []), distinct=(len({round(v['judgment'], 3) for v in pr.values()}) if pr else 0), nfp=len(getattr(X.S, 'fprism', {}) or {}))))
''' % (HERE, HERE)
def game(seed, **env):
    e = dict(os.environ); [e.pop(k, None) for k in ('PRISM_I', 'PRISM_FIELD', 'PRISM_DEF', 'PRISM_BOUNDED', 'PRISM_MANEUVERS', 'PRISM_FIELD_RATINGS', 'PRISM_AUDIT')]; e.update({k: str(v) for k, v in env.items()})
    o = subprocess.run([sys.executable, '-c', RUN, str(seed)], env=e, capture_output=True, text=True, timeout=1800)
    l = [x for x in o.stdout.splitlines() if x.startswith('RESULT')]; assert l, o.stderr[-800:]; return json.loads(l[0][6:])
def ok(c, m): print(('PASS ' if c else 'FAIL ') + m); assert c, m
if __name__ == '__main__':
    off = game(1); ok(off['nrat'] == 0 and off['nfp'] == 0 and not off['pm'], 'switch off: no PRISM state at all (layer absent)')
    a, b = game(1, PRISM_I=1), game(1, PRISM_I=1)
    ok(a == b, 'PRISM_I=1: two runs identical (deterministic)')
    ok(a['nrat'] >= 22 and set(['vision', 'awareness', 'clarity', 'reaction', 'focus', 'instinct', 'anticipation', 'judgment']) <= set(a['keys']), 'every athlete has the eight ratings (%d athletes)' % a['nrat'])
    ok(a['distinct'] > 10, 'ratings differ between athletes (%d distinct judgment values)' % a['distinct'])
    ok(a['nfp'] > 0 and a['pm'], 'perception tables and poses/maneuvers are active (%d PRISM minds)' % a['nfp'])
    ok(a['f'].get('def_views', 0) > 0 and a['f'].get('carrier_views', 0) > 0, 'defender and carrier decisions run on beliefs (def %d, carrier %d)' % (a['f'].get('def_views', 0), a['f'].get('carrier_views', 0)))
    ok(a['f'].get('ball_leak', 0) == 0 and a['f'].get('carrier_leak', 0) == 0 and a['f'].get('carrier_unaware', 0) > 0, 'no free ball / carrier position reaches a defender (leak counters 0; %d never-seen views get a placeholder)' % a['f'].get('carrier_unaware', 0))
    c = game(1, PRISM_I=1, PRISM_AUDIT=1); ok(c['f'].get('audit_n', 0) > 0 and c['f'].get('audit_diff', 0) == 0, 'sentinel audit: %d views with hidden bodies, 0 differences' % c['f'].get('audit_n', 0))
    d = game(1, PRISM_I=1, PRISM_DEF=0); ok(d['f'].get('def_views', 0) == 0 and d['f'].get('carrier_views', 0) > 0, 'an explicit flag overrides the switch (PRISM_DEF=0 turns defenders off)')
    e = game(1, PRISM_I=1, PRISM_FIELD_RATINGS=json.dumps({k: .5 for k in ('vision', 'awareness', 'clarity', 'reaction', 'focus', 'instinct', 'anticipation', 'judgment')}))
    ok(e != a, 'a global ratings override (sweeps) replaces per-athlete ratings')
    print('ALL PASS')
