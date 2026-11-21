"""RB-3.19 per-stage metrics from raw logs (log-only). usage: stages.py label=dir [label=dir ...]; dir holds real/ control/ raw logs (.json or .json.gz)."""
import sys, json, gzip, statistics as st, collections
RUNS = [('real', 'real-seed01'), ('real', 'real-seed03'), ('real', 'real-seed05'), ('control', 'control-seed01')]
def load(p):
    import os
    if os.path.exists(p): return json.load(open(p))
    return json.load(gzip.open(p + '.gz', 'rt'))
def one(root, b, name):
    log = load(f'{root}/{b}/raw-{name}.json')['log']; res = load(f'{root}/{b}/{name}.json')
    kind = {r['data']['restart_id']: r['data'].get('kind') for r in log if r['event'] == 'restart_awarded'}
    out = collections.Counter(); bnd = collections.Counter(); pts = collections.Counter(); ptsm = collections.Counter(); goals = collections.Counter()
    last = None; missed = rec = passes = 0; hand = collections.Counter()
    for i, r in enumerate(log):
        e, d = r['event'], r.get('data') or {}
        if e in ('release', 'restart_release', 'control'):
            last = (e, d)
        if e == 'release' and d.get('kind') == 'pass':
            passes += 1; team = d['player'][0]
            for x in log[i + 1:i + 300]:
                if x['event'] == 'control':
                    p = x['data']['player']
                    if p != d.get('target'):
                        missed += 1; rec += p[0] == team
                    break
                if x['event'] in ('boundary', 'restart_awarded', 'goal'): missed += 1; break
        if e == 'boundary':
            x = r['ball'][0]; typ = 'end' if x < 1. or x > 99. else 'side'; bnd[typ] += 1
            if last is None: cause = 'other'
            elif last[0] == 'control': cause = 'carrier'
            elif last[0] == 'release': cause = 'pass' if last[1].get('kind') == 'pass' else 'shot'
            else: cause = 'toss' if kind.get(last[1].get('restart_id')) in ('toss', 'boundary') else 'restart-' + str(kind.get(last[1].get('restart_id')))
            out[cause] += 1
        if e == 'goal':
            pts[d['team']] += d['points']; ptsm[d['method'] + ('_release_carry' if d.get('release_carry') else '')] += d['points']; goals[d['method']] += 1
        if e in ('handoff_complete', 'block_engaged', 'truck', 'truck_broken', 'stiff_arm', 'stretch_goal', 'truck_stopped'): hand[e] += 1
    return dict(name=name, score=res['score'], boundaries=sum(bnd.values()), boundary_type=dict(bnd), boundary_after=dict(out),
                passes=passes, missed=missed, missed_recovered_by_passer_team=rec, goals=dict(goals), points_by_method=dict(ptsm), actions=dict(hand))
if __name__ == '__main__':
    for arg in sys.argv[1:]:
        lab, root = arg.split('=')
        rows = [one(root, b, n) for b, n in RUNS]
        scores = [v for r in rows for v in r['score'].values()]
        print('==', lab, 'median_team_score', st.median(scores), 'scores', scores)
        for r in rows: print(json.dumps(r, sort_keys=True))
