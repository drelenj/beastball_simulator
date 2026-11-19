"""RB-3.8 report from soak_driver3 raw logs (reads files; runs no match).
python3 native/evidence/rb38/tools/rb38_report.py native/evidence/rb38
"""
import json, sys
from collections import Counter
from pathlib import Path

RUNS = (('real', 'real-seed01'), ('real', 'real-seed03'), ('control', 'control-seed01'))


def analyse(root, block, name):
    res = json.loads((root/block/f'{name}.json').read_text())
    rawp = root/block/f'raw-{name}.json'; text = rawp.read_text(); raw = json.loads(text); log = raw['log']
    play = Counter(); award = Counter(); calls = []
    for r in log:
        d = r['data']
        if r['event'] == 'goal': play[d['team']] += d['points']
        elif r['event'] == 'foul_award': award[d['team']] += d['points']
        elif r['event'] == 'zone_foul_diagnosis' and d['kind'] == 'zone_unmarked':
            f = d['fouler']; nob = d['nearest_off_ball_offence']; nany = d['nearest_offence_any']
            calls.append(dict(t_live_ms=r['live_ms'], period=r['period'], fouler=f['id'], team=f['team'],
                              x=f['x'], y=f['y'], distance_to_own_goal_centre=f['distance_to_zone_centre'],
                              live_s_in_zone=round(f['live_ms_in_zone'] / 1000, 2),
                              nearest_opponent=dict(id=nany['id'], role=nany['role'], distance=nany['distance_to_fouler']) if nany else None,
                              nearest_off_ball_opponent=dict(id=nob['id'], role=nob['role'], distance=nob['distance_to_fouler']) if nob else None,
                              ball_distance=d['ball']['distance_to_fouler'], ball_status=d['ball']['status']))
    m = res.get('metrics', {}); poss = m.get('possessions', {})
    shots = Counter(a['team'] for a in raw.get('rb_attempts', []) if a.get('shot_attempt'))
    carries = {t: v['attempts'] for t, v in m.get('carry_attempts', {}).items()}
    total = sum(play.values()) + sum(award.values())
    return dict(name=name, status=res['status'], score=res.get('score'), runtime_s=res.get('runtime_s'),
                trace_hash=res.get('trace_hash'), state_hash=res.get('state_hash'), config_digest=res.get('config_digest'),
                raw_log=str(rawp), result_file=str(root/block/f'{name}.json'),
                freeze_recovery_mentions_in_raw_log=text.count('freeze_recovery'),
                zone_unmarked=len(calls), zone_unmarked_calls=calls, foul_reasons=res.get('foul_reasons'),
                possessions={t: v['count'] for t, v in poss.items()},
                shot_attempts=dict(shots), carry_attempts=carries,
                attempts_per_possession={t: round((shots[t] + carries.get(t, 0)) / poss[t]['count'], 4) for t in poss if poss[t]['count']},
                share_possessions_ending_in_attempt={t: round(v['share_ending_in_attempt'], 4) for t, v in poss.items() if v.get('share_ending_in_attempt') is not None},
                points_from_play=dict(play), points_from_foul_awards=dict(award),
                share_points_from_fouls=round(sum(award.values()) / total, 3) if total else None)


if __name__ == '__main__':
    root = Path(sys.argv[1]); rows = [analyse(root, b, n) for b, n in RUNS if (root/b/f'{n}.json').exists()]
    (root/'rb38_table.json').write_text(json.dumps(rows, indent=2, sort_keys=True) + '\n')
    for r in rows: print(json.dumps({k: v for k, v in r.items() if k != 'zone_unmarked_calls'}, sort_keys=True))
