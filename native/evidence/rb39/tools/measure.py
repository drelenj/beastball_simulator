"""RB-3.9 per-match measurements from raw logs (reads files; runs no match).
python3 measure.py <label> <dir with real/ control/> [<label> <dir> ...]  -> prints a table, writes measure.json
Raw logs: soak_driver3 raw-*.json or raw-*.json.gz. Seeds: real 1, 3, 5 and control 1.
"""
import gzip, json, sys
from collections import Counter
from pathlib import Path
RUNS = [('real', 1), ('real', 3), ('real', 5), ('control', 1)]


def load(p):
    return json.load(gzip.open(p, 'rt')) if str(p).endswith('.gz') else json.loads(Path(p).read_text())


def measure(root, block, seed):
    name = f'{block}-seed{seed:02d}'; base = Path(root) / block
    rawp = base / f'raw-{name}.json'; rawp = rawp if rawp.exists() else base / f'raw-{name}.json.gz'
    raw = load(rawp); log = raw['log']; res = load(base / f'{name}.json')
    award = {r['data']['restart_id']: r['data'] for r in log if r['event'] == 'restart_awarded'}
    form = {r['data']['restart_id']: r['data'] for r in log if r['event'] == 'scrimmage_formation'}
    snap = Counter(); lost5 = 0; restarts = 0; nose = 0; passes = Counter()
    for q, r in enumerate(log):
        e, d = r['event'], r['data']
        if e == 'restart_release':
            restarts += 1; a = award.get(d['restart_id'], {}); kind = a.get('kind'); team = d['team']; out = 'unresolved'
            for x in log[q + 1:q + 400]:
                if x['event'] == 'control':
                    out = 'own' if x['data']['player'][0] == team else 'opp'
                    if out == 'opp' and form.get(d['restart_id'], {}).get('nose') == x['data']['player']: nose += 1
                    break
                if x['event'] in ('boundary', 'restart_awarded', 'goal'): out = 'out_or_dead'; break
            if kind in ('scrim', 'snap40'): snap[(kind, out)] += 1
            for x in log[q + 1:]:
                if x['live_ms'] - r['live_ms'] > 5000: break
                if x['event'] == 'rb_quota_reset' and x['data']['ruling']['team'] != team: lost5 += 1; break
        if e == 'release' and d['kind'] == 'pass':
            team = d['player'][0]; out = 'unresolved'
            for x in log[q + 1:q + 400]:
                if x['event'] == 'control': out = 'own' if x['data']['player'][0] == team else 'opp'; break
                if x['event'] in ('boundary', 'restart_awarded', 'goal'): out = 'out_or_dead'; break
            passes[out] += 1
    m = res.get('metrics', {}); poss = m.get('possessions', {})
    goals = [r['data'] for r in log if r['event'] == 'goal']
    carry_out = Counter(r['data']['outcome'] for r in log if r['event'] == 'carry_outcome')
    sc = lambda k: sum(v for (kk, o), v in snap.items() if kk == k)
    tot = sum(snap.values())
    return dict(name=name, status=res['status'], score=res['score'], runtime_s=res.get('runtime_s'),
                trace_hash=res['trace_hash'], state_hash=res['state_hash'], raw_log=str(rawp),
                possessions_per_team=round(sum(v['count'] for v in poss.values()) / 2, 1),
                share_ending_in_attempt=round(sum(v['ending_in_attempt'] for v in poss.values()) / max(1, sum(v['count'] for v in poss.values())), 4),
                scrim_snaps=sc('scrim'), scrim_intercepted=snap[('scrim', 'opp')], scrim_completed=snap[('scrim', 'own')],
                scrim_interception_rate=round(snap[('scrim', 'opp')] / max(1, sc('scrim')), 3),
                snap40=sc('snap40'), snap40_completed=snap[('snap40', 'own')],
                snap_completion_rate=round((snap[('scrim', 'own')] + snap[('snap40', 'own')]) / max(1, tot), 3),
                nose_tackle_interceptions=nose, restarts_released=restarts, restarts_lost_within_5s=lost5,
                open_play_passes=sum(passes.values()), open_play_completion=round(passes['own'] / max(1, sum(passes.values())), 3),
                carry_attempts=sum(v['attempts'] for v in m.get('carry_attempts', {}).values()),
                carry_goals=sum(1 for g in goals if g.get('method') == 'carry'), carry_outcomes=dict(carry_out),
                tackles=sum(1 for r in log if r['event'] == 'tackle_count'),
                zone_residence_calls=sum(1 for r in log if r['event'] == 'restart_awarded' and r['data']['reason'] == 'zone_residence'),
                points_from_play=sum(g['points'] for g in goals), points_from_fouls=sum(r['data']['points'] for r in log if r['event'] == 'foul_award'),
                restart_repeat_reports=sum(1 for r in log if r['event'] == 'restart_repeat_report'))


if __name__ == '__main__':
    args = sys.argv[1:]; out = {}
    for label, root in zip(args[::2], args[1::2]):
        out[label] = [measure(root, b, s) for b, s in RUNS if (Path(root) / b / f'{b}-seed{s:02d}.json').exists()]
    keys = ['possessions_per_team', 'share_ending_in_attempt', 'scrim_interception_rate', 'snap_completion_rate', 'nose_tackle_interceptions',
            'restarts_lost_within_5s', 'open_play_completion', 'carry_attempts', 'carry_goals', 'tackles', 'zone_residence_calls', 'points_from_play', 'points_from_fouls']
    for label, rows in out.items():
        print('==', label)
        for r in rows: print('  ', r['name'], r['status'], r['score'], ' '.join(f"{k}={r[k]}" for k in keys))
    Path(args[1]).parent.joinpath('measure-' + '-'.join(args[::2]) + '.json').write_text(json.dumps(out, indent=1) + '\n') if False else None
    print(json.dumps(out)[:0])
    Path('native/evidence/rb39').mkdir(parents=True, exist_ok=True)
    (Path('native/evidence/rb39') / ('measure-' + '-'.join(args[::2]) + '.json')).write_text(json.dumps(out, indent=1, sort_keys=True) + '\n')
