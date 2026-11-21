"""RB-3.15 shot conversion from raw logs (log-only): shots by distance band and outcome, keeper takes classified by the
keeper ids of the log (players with any keeper_contact), points, points per attempt. usage: shots.py <dir with real/ control/> ..."""
import sys, json, math, collections
RUNS = [('real', 'real-seed01'), ('real', 'real-seed03'), ('real', 'real-seed05'), ('control', 'control-seed01')]
def band(d): return '<10' if d < 10 else ('10-20' if d < 20 else '20+')
def run(root):
    tot = collections.defaultdict(collections.Counter); per = {}
    for b, name in RUNS:
        log = json.load(open(f'{root}/{b}/raw-{name}.json'))['log']
        keepers = {r['data']['player'] for r in log if r['event'] == 'keeper_contact'}
        shots = collections.defaultdict(collections.Counter); pts = collections.Counter(); carry_goals = 0; n = 0
        for i, r in enumerate(log):
            d = r.get('data') or {}
            if r['event'] == 'goal':
                pts[d['team']] += d['points']; carry_goals += d.get('method') == 'carry'
            if r['event'] == 'release' and d.get('kind') == 'shot':
                tm = d['player'][0]; n += 1; bx, by = r['ball'][0], r['ball'][1]
                # distance to the goal the shooter attacks: the goal the ball is flying toward
                v = d.get('velocity') or (1., 0., 0.); gx = 100. if v[0] > 0 else 0.
                dist = math.hypot(gx - bx, 50. - by); o = 'other'
                for e in log[i + 1:i + 90]:
                    if e['event'] == 'goal': o = 'scored'; break
                    if e['event'] == 'keeper_contact': o = 'keeper'; break
                    if e['event'] == 'control':
                        p = e['data']['player']
                        o = 'keeper' if p in keepers else 'own recovery' if p[0] == tm else 'field defender'; break
                    if e['event'] == 'boundary': o = 'out'; break
                    if e['event'] == 'restart_awarded': o = 'award'; break
                shots[band(dist)][o] += 1; tot[band(dist)][o] += 1
        res = json.load(open(f'{root}/{b}/{name}.json'))['score']
        per[name] = dict(score=res, shots=n, shots_by_band={k: dict(v) for k, v in shots.items()}, carry_goals=carry_goals,
                         outcome={o: sum(v[o] for v in shots.values()) for o in ('scored', 'keeper', 'field defender', 'own recovery', 'out', 'award', 'other')})
    return per
if __name__ == '__main__':
    for root in sys.argv[1:]:
        print('==', root)
        for k, v in run(root).items(): print(k, json.dumps(v, sort_keys=True))
