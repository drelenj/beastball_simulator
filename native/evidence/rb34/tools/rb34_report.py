"""RB-3.4 evidence table from soak_driver2 outputs (reads files; runs no match).
python3 native/evidence/rb34/tools/rb34_report.py native/evidence/rb34
"""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path


def analyse(root, block, seed):
    name = f'{block}-seed{seed:02d}'
    res = json.loads((root/block/f'{name}.json').read_text())
    out = dict(name=name, status=res['status'], finished=res['status'] == 'final', score=res.get('score'),
               runtime_s=res.get('runtime_s'), steps=res.get('steps'), trace_hash=res.get('trace_hash'),
               state_hash=res.get('state_hash'), error=res.get('error'), foul_reasons=res.get('foul_reasons'))
    rawp = root/block/f'raw-{name}.json'
    if not rawp.exists():
        return out
    log = json.loads(rawp.read_text())['log']
    play = Counter(); award = Counter(); dq = []; dq_off = Counter(); flip = None
    legal = Counter(); illegal = Counter(); refunded = Counter(); inert = Counter(); late = Counter()
    timeouts = Counter(); diag = Counter(); zone = []
    for r in log:
        ev, d = r['event'], r['data']
        if ev == 'goal': play[d['team']] += d['points']
        elif ev == 'foul_award': award[d['team']] += d['points']
        elif ev == 'coin_flip' and d['purpose'] == 'first_offence': flip = d['winner']
        elif ev == 'rb_discipline' and d['ruling'].get('dq'):
            ru = d['ruling']; dq.append(ru['player'][0]); dq_off[(ru.get('offence') or {}).get('reason')] += 1
        elif ev == 'arrow_release': legal[d['player']] += 1
        elif ev == 'foul' and d.get('reason') == 'archery_target': illegal[d['actor']] += 1
        elif ev == 'arrow_inert':
            inert[d['reason']] += 1
            if d['reason'] == 'dead_ball_in_flight' and d.get('refunded'): refunded[d['player']] += 1
        elif ev == 'arrow_outcome' and d['outcome'] == 'inert': late[d.get('late_reason')] += 1
        elif ev == 'restart_closed' and d['status'].endswith('timeout'): timeouts[r['period']] += 1
        elif ev == 'archery_target_diagnosis': diag[','.join(d['failed'])] += 1
        elif ev == 'zone_unmarked_diagnosis': zone.append(d)
    archers = sorted(set(legal) | set(illegal))
    m = res.get('metrics', {}); poss = m.get('possessions', {})
    total = sum(play.values()) + sum(award.values())
    out.update(
        coin_flip_winner=flip,
        points_from_play=dict(play), points_from_foul_awards=dict(award),
        share_points_from_fouls=round(sum(award.values())/total, 3) if total else None,
        dqs_per_team={t: dq.count(t) for t in ('A', 'B')}, dq_offences=dict(dq_off),
        arrows=dict(legal_released=sum(legal.values()), illegal=sum(illegal.values()),
                    inert_dead_ball_release=inert['dead_ball_release'], inert_dead_ball_in_flight=inert['dead_ball_in_flight'],
                    inert_late_on_arrival=dict(late), inert_late_total=sum(late.values())),
        quota_spent_per_archer={a: legal[a] + illegal[a] - refunded[a] for a in archers},
        restart_timeouts_per_period={str(k): v for k, v in sorted(timeouts.items())}, restart_timeouts=sum(timeouts.values()),
        possessions={t: v['count'] for t, v in poss.items()},
        share_possessions_ending_in_attempt={t: round(v['share_ending_in_attempt'], 4) if v.get('share_ending_in_attempt') is not None else None for t, v in poss.items()},
        archery_target_failed_predicates=dict(diag),
        zone_unmarked=dict(count=len(zone), actor_roles=dict(Counter(z['actor_role'] for z in zone)),
                           short_after_dqs=sum(z['short_after_dqs'] for z in zone),
                           mean_eligible_field_defenders=round(sum(z['eligible_field_defenders'] for z in zone)/len(zone), 2) if zone else None))
    return out


if __name__ == '__main__':
    root = Path(sys.argv[1]); rows = []
    for block, seeds in (('real', (1, 3, 10)), ('control', (1, 2, 3))):
        for seed in seeds:
            if (root/block/f'{block}-seed{seed:02d}.json').exists():
                rows.append(analyse(root, block, seed))
    (root/'rb34_table.json').write_text(json.dumps(rows, indent=2, sort_keys=True, default=str)+'\n')
    for r in rows: print(json.dumps(r, sort_keys=True, default=str))
