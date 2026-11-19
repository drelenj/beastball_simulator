"""RB-3.10 zone_residence diagnosis: read-only re-run of RB-3.9 stage 3 (6a328bf) matches.
Records, at each zone_residence call, positions of the offender, ball, nearest teammate and nearest
defender, the previous scrimmage formation (and whether it placed him in the zone he attacks) and the
award that followed. Asserts the re-run reproduces the stored trace and state hashes.
python3 zr_observe.py <repo at 6a328bf> <block> <seed> <stage3 result json> <out json>"""
import json, math, sys
repo, block, seed, ref, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5]
sys.path.insert(0, repo); sys.path.insert(0, repo + '/native/evidence/rb39/tools')
from native.run import run_match
from native.rulebook.config import RulebookConfigV3
from native.rulebook.port import RulebookPort
from native.nbl_roster import load_canon_nbl
from native.rulebook import zone_residence as Z
from soak_driver3 import control_rosters
rosters = control_rosters() if block == 'control' else load_canon_nbl(('Garvian Guardians', 'Ala Apex'))
cfg = RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A', 'B')))
p = RulebookPort(seed, cfg, rosters=rosters); s, e = p.m.s, p.m.e
old = e.rb_carry_attempt
def count(holder, *a, **k): return old(holder, *a, **k)          # same wrapper shape as soak_driver3
e.rb_carry_attempt = count
calls = []; last = {}
oform = e.rb_form_restart
def form():
    ok = oform()
    if ok:
        r = s.restart; f = r.rs['formation']
        last.update(rid=r.native_id, kind=r.kind, reason=r.reason, team=r.team, line_x=f['line_x'], spots=dict(f['spots']), t=s.now, live=s.live_ms)
    return ok
e.rb_form_restart = form
odiag = Z.diagnosis
def diag(port, pl, zn, kind, start):
    if kind == 'zone_residence':
        goal = (0., 50.) if zn == 0 else (100., 50.)
        mates = [q for q in s.players.values() if q.active and q.team == pl.team and q.role != 'archer' and q.id != pl.id]
        opps = [q for q in s.players.values() if q.active and q.team != pl.team and q.role != 'archer']
        nm = min(mates, key=lambda q: math.hypot(q.x - pl.x, q.y - pl.y)); nd = min(opps, key=lambda q: math.hypot(q.x - pl.x, q.y - pl.y))
        spot = last.get('spots', {}).get(pl.id) if last.get('team') == pl.team else None
        placed_in = spot is not None and math.hypot(spot[0] - goal[0], spot[1] - goal[1]) < 20.
        calls.append(dict(live_ms=s.live_ms, offender=pl.id, carrier=s.ball.carrier == pl.id, x=round(pl.x, 2), y=round(pl.y, 2),
                          dist_goal_centre=round(math.hypot(pl.x - goal[0], pl.y - goal[1]), 2), ball=[round(s.ball.x, 2), round(s.ball.y, 2)],
                          dist_ball=round(math.hypot(s.ball.x - pl.x, s.ball.y - pl.y), 2),
                          nearest_teammate=dict(id=nm.id, role=nm.role, dist=round(math.hypot(nm.x - pl.x, nm.y - pl.y), 2)),
                          nearest_defender=dict(id=nd.id, role=nd.role, dist=round(math.hypot(nd.x - pl.x, nd.y - pl.y), 2)),
                          live_ms_in_zone=s.live_ms - port.m.e.rb35['entry'].get(pl.id, start), live_ms_timer=s.live_ms - start,
                          previous_formation=dict(kind=last.get('kind'), reason=last.get('reason'), team=last.get('team'), line_x=last.get('line_x'),
                                                  his_spot=spot, placed_inside_attacked_zone=placed_in,
                                                  live_ms_since_formation=s.live_ms - last['live'] if last else None) if last else None))
    return odiag(port, pl, zn, kind, start)
Z.diagnosis = diag
score_before = None
r, _ = run_match(seed, cfg, rosters=rosters, port_factory=lambda *a, **k: p)
for c in calls:                                   # the award that followed each call
    after = [x for x in e.log if x['event'] == 'restart_awarded' and x['data']['reason'] == 'zone_residence' and x['live_ms'] == c['live_ms']]
    c['award'] = dict(kind=after[0]['data']['kind'], team=after[0]['data']['team'], spot=after[0]['data']['spot'], points=0) if after else None
refd = json.load(open(ref))
assert (r['trace_hash'], r['state_hash']) == (refd['trace_hash'], refd['state_hash']), 'hash mismatch'
fa = [x['data'] for x in e.log if x['event'] == 'foul_award']
json.dump(dict(name=f'{block}-seed{seed:02d}', trace_hash=r['trace_hash'], state_hash=r['state_hash'], zone_residence_calls=calls,
               foul_awards=[dict(points=d['points'], method=d.get('method'), origin=(d.get('origin_foul') or {}).get('reason')) for d in fa]),
          open(out, 'w'), indent=1)
print(block, seed, 'calls', len(calls), 'hash ok')
