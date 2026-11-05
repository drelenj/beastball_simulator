"""Regression test for the S.fowner correction (prism_field_v0.py): perception minds and their tick clock must restart for every new match in one process.
Before the fix the second match in a process ran with a stale tick clock: hidden opponents fell 8x, defender view error rose ~11x.  Usage: python3 test_perception_multimatch.py [path_to_prism_field_module_name]
Exits 1 if match 2 shows degraded perception relative to match 1."""
import os, sys
os.environ.update(PRISM_I='1'); sys.argv = sys.argv[:1]
import pocket4_proto as P4
from collections import Counter
P = P4.install(P4.load_pocket()); S = P4.S
counts = []
for seed in (1, 2):
    over, extras, names = P4.make_rosters(None, None, seed)
    before = Counter(S.fstats)
    P4.run(P, over, extras, names, (), 'sphere', seed, True)
    d = Counter({k: S.fstats[k] - before.get(k, 0) for k in S.fstats})
    counts.append(d); print('match', seed, 'minds', len(S.fprism), 'perception work', {k: d[k] for k in sorted(d)[:6]}, 'total', sum(d.values()), flush=True)
def stat(d):
    n = max(1, d['dreg_n']); return dict(hidden_opp=d['hidden_opp'], mean_view_miss=d['dreg_miss_view_x100'] / n / 100., dreg_n=d['dreg_n'], carrier_unaware=d['carrier_unaware'])
s1, s2 = stat(counts[0]), stat(counts[1]); print('match1', s1); print('match2', s2)
ok = s2['hidden_opp'] >= .5 * s1['hidden_opp'] and s2['mean_view_miss'] <= 2. * s1['mean_view_miss']
print('PASS' if ok else 'FAIL: match 2 perception degraded (stale tick clock)'); sys.exit(0 if ok else 1)
