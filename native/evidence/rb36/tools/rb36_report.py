"""RB-3.6 evidence table from soak_driver3 outputs (reads files; runs no match).
python3 native/evidence/rb36/tools/rb36_report.py native/evidence/rb36
"""
import json, sys
from collections import Counter
from pathlib import Path

RUNS = (('real', 'real-seed01'), ('real', 'real-seed03'), ('control', 'control-seed01'),
        ('real', 'real-seed01-fixoff'), ('real', 'real-seed01-leash15'), ('real', 'real-seed01-leash35'))


def quart(xs):
    xs = sorted(xs)
    if not xs: return None
    at = lambda f: xs[min(len(xs) - 1, int(round(f * (len(xs) - 1))))]
    return dict(n=len(xs), min=xs[0], q1=at(.25), median=at(.5), q3=at(.75), max=xs[-1])


def analyse(root, block, name):
    res = json.loads((root/block/f'{name}.json').read_text())
    log = json.loads((root/block/f'raw-{name}.json').read_text())['log']
    ev = Counter(r['event'] for r in log)
    play = Counter(); award = Counter(); dq = Counter(); carry = Counter(); summ = None
    for r in log:
        d = r['data']
        if r['event'] == 'goal': play[d['team']] += d['points']
        elif r['event'] == 'foul_award': award[d['team']] += d['points']
        elif r['event'] == 'rb_discipline' and d['ruling'].get('dq'): dq[d['ruling']['player'][0]] += 1
        elif r['event'] == 'carry_outcome': carry[d['outcome']] += 1
        elif r['event'] == 'zone_time_summary': summ = d['teams']
    diag = Counter(r['data']['kind'] for r in log if r['event'] == 'zone_foul_diagnosis')
    m = res.get('metrics', {}); poss = m.get('possessions', {})
    total = sum(play.values()) + sum(award.values())
    teams = {t: {k: summ[t][k] for k in ('share_in_own_zone', 'share_in_own_zone_unmarked', 'share_baseline_satisfied')} for t in ('A', 'B')} if summ else None
    players = summ.get('players', {}) if summ else {}
    return dict(name=name, status=res['status'], score=res.get('score'), runtime_s=res.get('runtime_s'),
                trace_hash=res.get('trace_hash'), state_hash=res.get('state_hash'), config_digest=res.get('config_digest'),
                zone_unmarked=diag['zone_unmarked'], zone_residence=diag['zone_residence'], foul_reasons=res.get('foul_reasons'),
                defender_time=teams, per_defender_baseline_share=quart(list(players.values())),
                dqs_per_team={t: dq[t] for t in ('A', 'B')},
                points_from_play=sum(play.values()), points_from_foul_awards=sum(award.values()),
                share_points_from_fouls=round(sum(award.values()) / total, 3) if total else None,
                possessions={t: v['count'] for t, v in poss.items()},
                share_possessions_ending_in_attempt={t: round(v['share_ending_in_attempt'], 4) for t, v in poss.items() if v.get('share_ending_in_attempt') is not None},
                carry_attempts={t: v for t, v in m.get('carry_attempts', {}).items()}, carry_outcomes=dict(carry),
                tackles=ev['tackle_count'], groundings=m.get('groundings'), restart_timeouts=m.get('restart_timeouts'))


if __name__ == '__main__':
    root = Path(sys.argv[1]); rows = []
    for block, name in RUNS:
        if (root/block/f'{name}.json').exists(): rows.append(analyse(root, block, name))
    (root/'rb36_table.json').write_text(json.dumps(rows, indent=2, sort_keys=True) + '\n')
    for r in rows: print(json.dumps(r, sort_keys=True))
