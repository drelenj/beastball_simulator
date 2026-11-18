"""RB-3.7: pass miss decomposition (reads soak raw logs and observer files; runs no match).
For each pass / restart throw with an intended receiver: the receiver's lateral offset from the
ball's line of flight AT RELEASE (aim error) and his distance from the ball at closest approach,
plus how far he moved during the flight.  python3 pass_aim.py <soak dir> <observe dir>"""
import gzip, json, math, sys, bisect
from collections import defaultdict
from pathlib import Path
soak, obs = Path(sys.argv[1]), Path(sys.argv[2])
out = defaultdict(list)
for block, seeds in (('real', range(1, 11)), ('control', range(1, 4))):
    for seed in seeds:
        name = f'{block}-seed{seed:02d}'
        log = json.load(gzip.open(soak / block / f'raw-{name}.json.gz', 'rt'))['log']
        o = json.load(gzip.open(obs / f'observe-{name}.json.gz', 'rt')); snap = {s['id']: s for s in o['snaps']}; fl = o['ball_flight']
        for q, r in enumerate(log):
            if r['event'] not in ('release', 'restart_release'): continue
            d = r['data']; kind = d.get('kind', 'restart') if r['event'] == 'release' else 'restart'
            if kind not in ('pass', 'restart') or not d.get('target'): continue
            passer = d.get('player') or d.get('taker'); tgt = d['target']; s = snap.get(r['id'])
            if not s: continue
            P = {p[0]: p for p in s['players']}
            if tgt not in P: continue
            vx, vy = d['velocity'][0], d['velocity'][1]; n = math.hypot(vx, vy) or 1
            bx, by = s['ball']; tx, ty = P[tgt][3], P[tgt][4]
            along = ((tx - bx) * vx + (ty - by) * vy) / n
            lateral = abs((tx - bx) * vy - (ty - by) * vx) / n
            res = 'unresolved'
            for z in range(q + 1, min(len(log), q + 400)):
                e = log[z]['event']
                if e == 'control': res = 'ok' if log[z]['data']['player'][0] == passer[0] else 'fail'; break
                if e in ('boundary', 'restart_awarded'): res = 'fail'; break
            lo = bisect.bisect_left(fl, [r['live_ms']]); best = None
            for f in fl[lo:lo + 60]:
                if f[0] > r['live_ms'] + 3000: break
                if f[6] == passer and f[7] == tgt and f[8] is not None:
                    dd = math.hypot(f[3] - f[8], f[4] - f[9])
                    if best is None or dd < best[0]: best = (dd, math.hypot(f[8] - tx, f[9] - ty), f[5])
            out[(block, kind, res)].append((lateral, along, best))
def q(xs):
    xs = sorted(xs)
    return None if not xs else dict(n=len(xs), q1=round(xs[len(xs)//4], 2), median=round(xs[len(xs)//2], 2), q3=round(xs[3*len(xs)//4], 2))
rep = {}
for k, v in sorted(out.items()):
    rep['/'.join(k)] = dict(lateral_offset_at_release_m=q([x[0] for x in v]), receiver_distance_along_flight_m=q([x[1] for x in v]),
                            closest_ball_to_receiver_m=q([x[2][0] for x in v if x[2]]), receiver_moved_during_flight_m=q([x[2][1] for x in v if x[2]]),
                            ball_height_at_closest_m=q([x[2][2] for x in v if x[2]]),
                            behind_passer_share=round(sum(1 for x in v if x[1] < 0) / len(v), 3))
print(json.dumps(rep, indent=1))
Path(obs).parent.joinpath('pass_aim.json').write_text(json.dumps(rep, indent=1, sort_keys=True) + '\n')
