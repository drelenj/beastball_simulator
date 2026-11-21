"""RB-3.21 soak measurement. Reads result JSON and gzipped raw logs only.
python3 native/evidence/rb321-soak/tools/rb321_measure.py native/evidence/rb321-soak
Shot / keeper / pass definitions follow native/evidence/rb316-soak/tools/measure316_soak.py.
Keeper = each team's first role-keeper in roster order (real: A:NBL24-07-11, B:NBL24-01-11; control: A:18, B:18).

POSSESSION END CAUSE (no end-reason is logged; classified from the span before the next possession change):
the possession span runs from one 'possession' event to the next. Its cause is the FIRST terminating event in the span
(a restart that follows a boundary or goal is a consequence, not the cause):
  goal                  -> 'goal'
  boundary, last release a pass by the holding team -> 'pass out of bounds'
  boundary, otherwise   -> 'other out'
  carry_outcome turnover -> 'intercepted/loose' ; carry_outcome grounded -> 'carrier frozen'
  carry_outcome stopped_short -> 'carrier stopped short'
  freeze (rb_freeze)    -> 'carrier frozen'
  restart_awarded reason second_tackle -> 'second tackle'
  restart_awarded reason first_tackle  -> 'first tackle'
  restart_awarded other -> 'restart (other)'
  release loose / interception by the other team -> 'intercepted/loose'
  no terminating event  -> 'unclassified'
Restart throw lost is reported separately: a restart release followed within 5 s by a rb_quota_reset ruling for the other team.
"""
import gzip
import json
import math
import statistics as st
import sys
from collections import Counter
from pathlib import Path

REPO = Path('/home/user/beastball_simulator')
sys.path.insert(0, str(REPO))
from native.nbl_roster import load_canon_nbl  # noqa: E402
from native.roster import rb3_control_rosters  # noqa: E402

ROOT = Path(sys.argv[1])
SEEDS = {'real': list(range(1, 11)), 'control': [1, 2, 3]}


def keepers(block):
    R = load_canon_nbl(('Garvian Guardians', 'Ala Apex')) if block == 'real' else rb3_control_rosters()
    return {t: f"{t}:{next(a for a in R[t].athletes if a.role == 'keeper').source_id}" for t in 'AB'}


def read(p):
    p = Path(p)
    if p.exists():
        return json.loads(p.read_text())
    return json.loads(gzip.open(str(p) + '.gz', 'rt').read())


def possession_causes(L):
    starts = [i for i, r in enumerate(L) if r['event'] == 'possession']
    causes = Counter(); per_team = Counter()
    last_release = {}
    for k, s in enumerate(starts):
        end = starts[k + 1] if k + 1 < len(starts) else len(L)
        team = L[s]['data']['team']
        per_team[team] += 1
        cause = 'unclassified'
        for j in range(s + 1, end):
            e = L[j]; ev = e['event']; d = e.get('data') or {}
            if ev == 'release':
                last_release[d['player'].split(':')[0]] = d.get('kind')
            if cause != 'unclassified':
                break
            if ev == 'goal':
                cause = 'goal'
            elif ev == 'boundary':
                cause = 'pass out of bounds' if last_release.get(team) == 'pass' else 'other out'
            elif ev == 'carry_outcome':
                cause = {'turnover': 'intercepted/loose', 'grounded': 'carrier frozen', 'stopped_short': 'carrier stopped short',
                         'goal': 'goal'}.get(d.get('outcome'), 'other')
            elif ev == 'rb_freeze':
                cause = 'carrier frozen'
            elif ev == 'restart_awarded':
                rs = d.get('reason')
                cause = {'second_tackle': 'second tackle', 'first_tackle': 'first tackle'}.get(rs, 'restart (other)')
            elif ev == 'release' and d.get('kind') == 'loose':
                cause = 'intercepted/loose'
        causes[cause] += 1
    return causes, per_team


def restart_lost_within_5s(L):
    lost = 0; restarts = 0
    for q, r in enumerate(L):
        if r['event'] != 'restart_release':
            continue
        restarts += 1; team = r['data']['team']
        for x in L[q + 1:q + 400]:
            if x['live_ms'] - r['live_ms'] > 5000:
                break
            if x['event'] == 'rb_quota_reset' and x['data']['ruling']['team'] != team:
                lost += 1; break
    return lost, restarts


def shots(L, K):
    out = Counter(); team_shots = Counter(); team_scored = Counter()
    for i, r in enumerate(L):
        dd = r.get('data') or {}
        if r['event'] != 'release' or dd.get('kind') != 'shot':
            continue
        tm = dd['player'].split(':')[0]; o = 'other'
        for e in L[i + 1:i + 90]:
            if e['event'] == 'goal':
                o = 'scored'; break
            if e['event'] == 'keeper_contact':
                o = 'keeper'; break
            if e['event'] == 'control':
                p = e['data']['player']
                o = 'own' if p.split(':')[0] == tm else ('keeper' if p in K.values() else 'field')
                break
            if e['event'] in ('boundary', 'restart_awarded'):
                o = 'out/award'; break
        out[o] += 1; team_shots[tm] += 1
        if o == 'scored':
            team_scored[tm] += 1
    return out, team_shots, team_scored


def row(block, seed):
    name = f'{block}-seed{seed:02d}'
    res = read(ROOT / block / f'{name}.json')
    if res.get('status') != 'final':
        return dict(name=name, block=block, status=res.get('status'), error=res.get('error'))
    raw = read(ROOT / block / f'raw-{name}.json')
    L = raw['log']; m = res['metrics']; P = m['points']
    K = keepers(block)
    causes, per_team = possession_causes(L)
    lost, restarts = restart_lost_within_5s(L)
    sh, team_shots, team_scored = shots(L, K)
    methods = Counter()
    for e in L:
        d = e.get('data') or {}
        if e['event'] == 'goal':
            methods[('release' if d['method'] == 'release' else d['method'])] += d['points']
        elif e['event'] == 'foul_award':
            methods[{'half_goal': 'half', 'full_goal_award': 'award'}.get(d['method'], d['method'])] += d['points']
    cnt = Counter(e['event'] for e in L)
    tot_shots = sum(sh.values())
    return dict(
        name=name, block=block, status=res['status'], steps=res['steps'], runtime_s=res['runtime_s'],
        score=res['score'], trace_hash=res['trace_hash'], state_hash=res['state_hash'],
        possessions={t: m['possessions'][t]['count'] for t in 'AB'},
        possession_end_causes=dict(causes),
        points_play={t: P[t]['play'] for t in 'AB'}, points_awards={t: P[t]['penalty_awards'] for t in 'AB'},
        points_by_method={f'{k}': v for k, v in sorted(methods.items())},
        shots={t: team_shots.get(t, 0) for t in 'AB'}, shots_scored={t: team_scored.get(t, 0) for t in 'AB'},
        shot_outcomes=dict(sh), shot_conversion_pct=round(100 * sh['scored'] / tot_shots, 1) if tot_shots else None,
        handoffs_started=cnt['handoff_start'], handoffs_completed=cnt['handoff_complete'],
        blocks_engaged=cnt['block_engaged'], blocks_shed=cnt['block_shed'],
        trucks_attempted=cnt['truck'], trucks_broken=cnt['truck_broken'],
        stiff_arms=cnt['stiff_arm'], stretch_goals=cnt['stretch_goal'],
        stretch_goals_by_team=dict(Counter(e['data']['team'] for e in L if e['event'] == 'stretch_goal')),
        dqs={t: m['dqs'][t] for t in 'AB'},
        legal_arrow_rate={t: m['arrows'][t]['legal_rate'] for t in 'AB'},
        restart_timeouts=m['restart_timeouts'], restart_completion_ratio=res['restart_completion_ratio'],
        restart_throw_lost_within_5s=lost, restarts_released=restarts,
        zone_unmarked_calls=sum(1 for e in L if e['event'] == 'zone_foul_diagnosis' and e['data'].get('kind') == 'zone_unmarked'),
        keepers=K,
    )


def pct(vals, q):
    return st.quantiles(vals, n=100, method='inclusive')[q - 1]


def main():
    rows = [row(b, s) for b in ('real', 'control') for s in SEEDS[b]]
    (ROOT / 'rb321_table.json').write_text(json.dumps(rows, indent=1, sort_keys=True, default=str) + '\n')
    real = [r for r in rows if r.get('block') == 'real' and r.get('status') == 'final']
    team_games = [r['score'][t] for r in real for t in 'AB']
    poss_team = [r['possessions'][t] for r in real for t in 'AB']
    summary = dict(
        team_score=dict(n=len(team_games), median=st.median(team_games), mean=round(st.mean(team_games), 2),
                        sd_sample=round(st.stdev(team_games), 2), p5=round(pct(team_games, 5), 1), p95=round(pct(team_games, 95), 1)),
        possessions_team=dict(mean=round(st.mean(poss_team), 1), median=st.median(poss_team), min=min(poss_team), max=max(poss_team),
                              n_over_150=sum(p > 150 for p in poss_team), n_under_100=sum(p < 100 for p in poss_team)),
        matches_any_team_over_150=sum(any(r['possessions'][t] > 150 for t in 'AB') for r in real),
    )
    (ROOT / 'rb321_summary.json').write_text(json.dumps(summary, indent=1, sort_keys=True) + '\n')
    print(json.dumps(summary, indent=1))


if __name__ == '__main__':
    main()
