"""RB-3.7: restart-throw interception geometry (reads logs and observer files; runs no match).
python3 restart_lane.py <soak dir> <observe dir>"""
import gzip, json, math, sys
from collections import defaultdict, Counter
from pathlib import Path
soak, obs = Path(sys.argv[1]), Path(sys.argv[2])
rows = defaultdict(list); who = Counter()
def seg(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay; L = dx * dx + dy * dy or 1
    f = max(0., min(1., ((px - ax) * dx + (py - ay) * dy) / L)); return math.hypot(px - ax - f * dx, py - ay - f * dy), f
for block, seeds in (('real', range(1, 11)), ('control', range(1, 4))):
    for seed in seeds:
        name = f'{block}-seed{seed:02d}'
        log = json.load(gzip.open(soak / block / f'raw-{name}.json.gz', 'rt'))['log']
        snap = {s['id']: s for s in json.load(gzip.open(obs / f'observe-{name}.json.gz', 'rt'))['snaps']}
        award = {r['data']['restart_id']: r['data'] for r in log if r['event'] == 'restart_awarded'}
        for q, r in enumerate(log):
            if r['event'] != 'restart_release': continue
            d = r['data']; tgt = d.get('target'); s = snap.get(r['id']); a = award.get(d['restart_id'], {})
            if not tgt or not s: continue
            P = {p[0]: p for p in s['players']}; team = d['team']
            if tgt not in P: continue
            bx, by = s['ball']; tx, ty = P[tgt][3], P[tgt][4]
            opp = [p for p in s['players'] if p[1] != team]
            lane = min((seg(p[3], p[4], bx, by, tx, ty)[0] for p in opp), default=99.)
            near_spot = sum(1 for p in opp if math.hypot(p[3] - bx, p[4] - by) <= 5)
            res = 'unresolved'; ctrl = None
            for z in range(q + 1, min(len(log), q + 400)):
                e = log[z]['event']
                if e == 'control':
                    c = log[z]['data']['player']; res = 'ok' if c[0] == team else 'intercepted'
                    cs = snap.get(log[z]['id']); ctrl = cs and next((p for p in cs['players'] if p[0] == c), None); break
                if e in ('boundary', 'restart_awarded'): res = 'out_or_dead'; break
            if res == 'intercepted' and ctrl:
                who['interceptor was in the lane (<2 m) at release' if any(p[0] == ctrl[0] and seg(p[3], p[4], bx, by, tx, ty)[0] < 2 for p in opp) else 'interceptor came from elsewhere'] += 1
                rows[(block, a.get('kind'), 'intercept_point_from_spot')].append(math.hypot(ctrl[3] - bx, ctrl[4] - by))
            rows[(block, a.get('kind'), res, 'lane')].append(lane); rows[(block, a.get('kind'), res, 'opp_within_5m_of_spot')].append(near_spot)
            rows[(block, a.get('kind'), res, 'distance')].append(math.hypot(tx - bx, ty - by))
def q(xs):
    xs = sorted(xs); return dict(n=len(xs), q1=round(xs[len(xs)//4], 2), median=round(xs[len(xs)//2], 2), q3=round(xs[3*len(xs)//4], 2)) if xs else None
rep = {'/'.join(map(str, k)): q(v) for k, v in sorted(rows.items(), key=lambda kv: str(kv[0]))}
rep['interceptor_origin'] = dict(who)
Path(obs).parent.joinpath('restart_lane.json').write_text(json.dumps(rep, indent=1, sort_keys=True) + '\n')
for k, v in rep.items():
    if k.startswith('real') or k == 'interceptor_origin': print(k, v)
