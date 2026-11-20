"""Control side-bias analysis (identical-rating teams). Reads result JSON and gzipped raw logs only.
python3 native/evidence/rb316-control/tools/control_bias.py native/evidence/rb316-control
Slot A = team 'A', slot B = team 'B'. Both slots have identical ratings (rb3_control_rosters).
Attack direction per period: median x of the team's shot releases in that period (x > 50 => attacks toward x = 100).
Fallback when no shot: median x of that team's goal balls in that period.
"""
import gzip
import json
import math
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(sys.argv[1])
SEEDS = list(range(1, 24))


def load_raw(seed):
    p = ROOT / 'control' / f'raw-control-seed{seed:02d}.json.gz'
    return json.loads(gzip.open(p, 'rt').read())


def load_res(seed):
    return json.loads((ROOT / 'control' / f'control-seed{seed:02d}.json').read_text())


def match_row(seed):
    res = load_res(seed)
    raw = load_raw(seed)
    L = raw['log']
    m = res['metrics']
    coin = [e['data'] for e in L if e['event'] == 'coin_flip']
    coin_winner = coin[0]['winner'] if coin else None
    offence = {e['data']['period']: e['data']['offence'] for e in L if e['event'] == 'period_start'}
    # shots and their outcomes (same classification as measure316_soak.py)
    shot_team = Counter(); shot_scored = Counter()
    shots_by_period = defaultdict(Counter); scored_by_period = defaultdict(Counter)
    shot_x = defaultdict(list)
    goal_x = defaultdict(list)
    points_p = defaultdict(int)
    for i, r in enumerate(L):
        dd = r.get('data') or {}
        if r['event'] == 'goal':
            points_p[(r['period'], dd['team'])] += dd['points']
            goal_x[(r['period'], dd['team'])].append(r['ball'][0])
        elif r['event'] == 'foul_award':
            points_p[(r['period'], dd['team'])] += dd['points']
        if r['event'] == 'release' and dd.get('kind') == 'shot':
            tm = dd['player'].split(':')[0]
            shot_team[tm] += 1
            shots_by_period[r['period']][tm] += 1
            shot_x[(r['period'], tm)].append(r['ball'][0])
            outcome = 'other'
            for e in L[i + 1:i + 90]:
                if e['event'] == 'goal':
                    outcome = 'scored'; break
                if e['event'] in ('keeper_contact', 'control', 'boundary', 'restart_awarded'):
                    break
            if outcome == 'scored':
                shot_scored[tm] += 1
                scored_by_period[r['period']][tm] += 1
    periods = sorted({r['period'] for r in L if 'period' in r})
    per = []
    for p in (1, 2, 3, 4):
        row = dict(period=p, offence=offence.get(p))
        for t in 'AB':
            row[f'points_{t}'] = points_p[(p, t)]
            row[f'shots_{t}'] = shots_by_period[p][t]
            row[f'scored_{t}'] = scored_by_period[p][t]
            xs = shot_x[(p, t)] or goal_x[(p, t)]
            row[f'attacks_{t}'] = ('x100' if st.median(xs) > 50 else 'x0') if xs else None
        per.append(row)
    return dict(
        seed=seed, status=res['status'], score={t: res['score'][t] for t in 'AB'},
        possessions={t: m['possessions'][t]['count'] for t in 'AB'},
        attempt_share={t: m['possessions'][t]['share_ending_in_attempt'] for t in 'AB'},
        shots={t: shot_team[t] for t in 'AB'}, shots_scored={t: shot_scored[t] for t in 'AB'},
        coin_flip_winner=coin_winner, first_offence=coin[0]['purpose'] if coin else None,
        per_period=per, runtime_s=res['runtime_s'], trace_hash=res['trace_hash'], state_hash=res['state_hash'],
        raw_log=f'native/evidence/rb316-control/control/raw-control-seed{seed:02d}.json.gz',
    )


def tstat(x):
    m = st.mean(x); sd = st.stdev(x); n = len(x)
    se = sd / math.sqrt(n)
    return m, sd, m / se, n


def t_crit_975(df):
    # two-sided 95% critical t (table up to df 30, else 1.96)
    table = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262,
             10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110,
             18: 2.101, 19: 2.093, 20: 2.086, 21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060,
             26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042}
    return table.get(df, 1.96)


def main():
    rows = [match_row(s) for s in SEEDS]
    diffs = [r['score']['B'] - r['score']['A'] for r in rows]
    m, sd, t, n = tstat(diffs)
    half = t_crit_975(n - 1) * sd / math.sqrt(n)
    summary = dict(
        n=n,
        slotA_mean=st.mean(r['score']['A'] for r in rows), slotB_mean=st.mean(r['score']['B'] for r in rows),
        diff_B_minus_A_mean=m, diff_sd=sd, paired_t=t, ci95=[m - half, m + half],
        B_wins=sum(d > 0 for d in diffs), A_wins=sum(d < 0 for d in diffs), ties=sum(d == 0 for d in diffs),
        coin_winner_B=sum(r['coin_flip_winner'] == 'B' for r in rows if r['coin_flip_winner']),
        coin_winner_A=sum(r['coin_flip_winner'] == 'A' for r in rows if r['coin_flip_winner']),
        shots_A_mean=st.mean(r['shots']['A'] for r in rows), shots_B_mean=st.mean(r['shots']['B'] for r in rows),
        shots_scored_A_mean=st.mean(r['shots_scored']['A'] for r in rows), shots_scored_B_mean=st.mean(r['shots_scored']['B'] for r in rows),
        possessions_A_mean=st.mean(r['possessions']['A'] for r in rows), possessions_B_mean=st.mean(r['possessions']['B'] for r in rows),
    )
    # per-period breakdown across games (only when |t| > 2)
    if abs(t) > 2:
        pb = {}
        for p in (1, 2, 3, 4):
            pts_d = [r['per_period'][p - 1]['points_B'] - r['per_period'][p - 1]['points_A'] for r in rows]
            sh_d = [r['per_period'][p - 1]['shots_B'] - r['per_period'][p - 1]['shots_A'] for r in rows]
            pb[p] = dict(points_B_minus_A_mean=st.mean(pts_d), shots_B_minus_A_mean=st.mean(sh_d))
        summary['by_period'] = pb
        ends = Counter()
        for r in rows:
            for pr in r['per_period']:
                ends[(pr['period'], pr['attacks_A'], pr['attacks_B'])] += 1
        summary['attack_end_by_period_counts'] = {str(k): v for k, v in sorted(ends.items(), key=lambda kv: str(kv[0]))}
    out = dict(summary=summary, rows=rows)
    (ROOT / 'control_bias.json').write_text(json.dumps(out, indent=1, default=str) + '\n')
    L = ['# RB-3.16 control side-bias (identical ratings; TESTED, not ACCEPTED)', '',
         '| seed | score A-B | B - A | possessions A/B | shots A/B | shots scored A/B | coin flip winner | runtime s |',
         '|---|---|---|---|---|---|---|---|']
    for r in rows:
        L.append(f"| {r['seed']} | {r['score']['A']}-{r['score']['B']} | {r['score']['B']-r['score']['A']:+d} | {r['possessions']['A']}/{r['possessions']['B']} | "
                 f"{r['shots']['A']}/{r['shots']['B']} | {r['shots_scored']['A']}/{r['shots_scored']['B']} | {r['coin_flip_winner'] or '—'} | {r['runtime_s']} |")
    L += ['', '## Summary (23 games)', '| measure | value |', '|---|---|',
          f"| slot A mean points | {summary['slotA_mean']:.2f} |",
          f"| slot B mean points | {summary['slotB_mean']:.2f} |",
          f"| mean difference B − A | {m:+.2f} (sd {sd:.2f}) |",
          f"| paired t (n = {n}) | {t:.2f} |",
          f"| 95% interval for mean B − A | {m - half:+.2f} to {m + half:+.2f} |",
          f"| B wins / A wins / ties | {summary['B_wins']} / {summary['A_wins']} / {summary['ties']} |",
          f"| coin flip winner B / A | {summary['coin_winner_B']} / {summary['coin_winner_A']} |",
          f"| shots mean A / B | {summary['shots_A_mean']:.1f} / {summary['shots_B_mean']:.1f} |",
          f"| shots scored mean A / B | {summary['shots_scored_A_mean']:.1f} / {summary['shots_scored_B_mean']:.1f} |",
          f"| possessions mean A / B | {summary['possessions_A_mean']:.1f} / {summary['possessions_B_mean']:.1f} |"]
    if 'by_period' in summary:
        L += ['', '## Breakdown by period (|t| > 2)', '| period | mean B − A points | mean B − A shots |', '|---|---|---|']
        for p, v in summary['by_period'].items():
            L.append(f"| {p} | {v['points_B_minus_A_mean']:+.2f} | {v['shots_B_minus_A_mean']:+.2f} |")
        L += ['', '## Attacking end by period (A end, B end: count of game-periods)', '| period, A attacks, B attacks | count |', '|---|---|']
        for k, v in summary['attack_end_by_period_counts'].items():
            L.append(f"| {k} | {v} |")
    (ROOT / 'CONTROL_BIAS.md').write_text('\n'.join(L) + '\n')
    print(json.dumps(summary, indent=1, default=str))


if __name__ == '__main__':
    main()
