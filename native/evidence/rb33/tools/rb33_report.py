"""RB-3.3 evidence table from soak_driver2 outputs (reads files; runs no match).
python3 native/evidence/rb33/tools/rb33_report.py native/evidence/rb33
"""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, '/home/user/beastball_simulator')
from native.rulebook.port import RulebookPort
from native.rulebook.config import RulebookConfigV3
from native.nbl_roster import load_canon_nbl


def initial_roles(block, seed):
    sys.path.insert(0, str(Path(__file__).parent))
    from soak_driver2 import control_rosters
    rosters = control_rosters() if block == 'control' else load_canon_nbl(('Garvian Guardians', 'Ala Apex'))
    cfg = RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A', 'B')))
    p = RulebookPort(seed, cfg, rosters=rosters)
    return {q.id: q.role for q in p.m.s.players.values()}, p.m.e.rb_flip['first']


def analyse(root, block, seed):
    name = f'{block}-seed{seed:02d}'
    res = json.loads((root/block/f'{name}.json').read_text())
    out = dict(name=name, status=res['status'], finished=res['status'] == 'final', score=res.get('score'),
               runtime_s=res.get('runtime_s'), steps=res.get('steps'), live_ms=res.get('live_ms'),
               trace_hash=res.get('trace_hash'), state_hash=res.get('state_hash'), error=res.get('error'))
    rawp = root/block/f'raw-{name}.json'
    if not rawp.exists():
        return out
    raw = json.loads(rawp.read_text()); log = raw['log']
    roles, flip = initial_roles(block, seed); out['coin_flip_winner'] = flip
    team = lambda pid: pid[0] if pid else None
    fouls_by_role = Counter(); legal = Counter(); illegal = Counter(); dq = []; arrow_out = Counter(); carry = Counter()
    award_origin = Counter(); shot_roles = defaultdict(set); play_pts = Counter(); award_pts = Counter()
    for r in log:
        ev, d = r['event'], r['data']
        if ev == 'rb_substitution':
            ru = d['ruling']; roles[ru['incoming']] = ru['role']
        elif ev == 'rb_specialist_fallback':
            roles[d['ruling']['player']] = d['ruling']['role']
        elif ev == 'foul' and d.get('reason') == 'archery_target':
            fouls_by_role[roles.get(d['actor'], '?')] += 1; illegal[d['actor']] += 1; shot_roles[d['actor']].add(roles.get(d['actor'], '?'))
        elif ev == 'arrow_release':
            legal[d['player']] += 1; shot_roles[d['player']].add(roles.get(d['player'], '?'))
        elif ev == 'rb_discipline' and d['ruling'].get('dq'):
            ru = d['ruling']; pid = ru.get('player')
            dq.append(dict(player=pid, team=team(pid), role=roles.get(pid, '?'), offence=(ru.get('offence') or {}).get('reason')))
        elif ev == 'arrow_outcome':
            arrow_out[d['outcome']] += 1
        elif ev == 'carry_outcome':
            carry[d['outcome']] += 1
        elif ev == 'goal':
            play_pts[d['team']] += d['points']
        elif ev == 'foul_award':
            award_pts[d['team']] += d['points']; award_origin[(d.get('origin_foul') or {}).get('reason')] += 1
    archers = sorted(set(legal) | set(illegal))
    m = res.get('metrics', {})
    total = sum(play_pts.values()) + sum(award_pts.values())
    out.update(
        archery_target_fouls=sum(fouls_by_role.values()), archery_target_fouls_by_actor_role=dict(fouls_by_role),
        arrows_per_archer={a: dict(roles_when_shooting=sorted(shot_roles[a]), legal=legal[a], illegal=illegal[a]) for a in archers},
        arrow_outcomes=dict(arrow_out),
        dqs_per_team={t: sum(x['team'] == t for x in dq) for t in ('A', 'B')},
        archer_dqs=sum(x['role'] == 'archer' for x in dq), dq_offences=dict(Counter(x['offence'] for x in dq)),
        points_from_play=dict(play_pts), points_from_foul_awards=dict(award_pts),
        share_points_from_fouls=round(sum(award_pts.values())/total, 3) if total else None,
        foul_award_origins=dict(award_origin), carry_outcomes=dict(carry),
        possessions={t: v['count'] for t, v in m.get('possessions', {}).items()},
        restart_timeouts=m.get('restart_timeouts'), restart_statuses=res.get('restart_statuses'),
        foul_reasons=res.get('foul_reasons'))
    return out


if __name__ == '__main__':
    root = Path(sys.argv[1]); rows = []
    for block, seeds in (('real', (1, 3, 10)), ('control', (1, 2, 3))):
        for seed in seeds:
            if (root/block/f'{block}-seed{seed:02d}.json').exists():
                rows.append(analyse(root, block, seed))
    (root/'rb33_table.json').write_text(json.dumps(rows, indent=2, sort_keys=True, default=str)+'\n')
    for r in rows:
        print(json.dumps(r, sort_keys=True, default=str))
