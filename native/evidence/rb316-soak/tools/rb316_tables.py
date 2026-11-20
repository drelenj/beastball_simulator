import json, statistics, sys
from pathlib import Path
root = Path(sys.argv[1])
rows = json.loads((root / 'measure316_table.json').read_text())
S = json.loads((root / 'measure316_summary.json').read_text())
def f(x):
    if x is None: return '—'
    if isinstance(x, float): return f'{x:.3f}' if x < 1.5 and x > 0 and False else (f'{x:.1f}' if abs(x) >= 1 else f'{x:.3f}')
    return str(x)
L = ['# RB-3.16 soak: per-match and summary (TESTED measurements; not ACCEPTED)', '']
L.append('## Per match')
L.append('| match | status | score A-B | play pts A/B | award pts A/B | points by method | possessions A/B | % poss ending in attempt A/B | shots A/B | shot outcome % (scored/keeper/field/own/out-award) | passes | pass intercepted % | intercepted <=3 m | tackles | carry att A/B | carry goals A/B | fouls by reason | DQs A/B | legal-arrow A/B | restart TO | restart compl. | zone_unmarked | runtime s | trace_hash | state_hash |')
L.append('|' + '---|' * 25)
for r in rows:
    if r.get('status') != 'final':
        L.append(f"| {r['name']} | {r.get('status')} | {r.get('error')} |"); continue
    sc = r['shot_outcome_shares_pct']
    so = '/'.join(str(sc.get(k, 0)) for k in ('scored', 'keeper', 'field', 'own', 'out/award'))
    meth = ', '.join(f'{k}={v}' for k, v in r['points_by_method'].items())
    fr = ', '.join(f'{k}={v}' for k, v in sorted(r['foul_reasons'].items())) or 'none'
    sh = r['shots_by_team']
    L.append(f"| {r['name']} | final | {r['score']['A']}-{r['score']['B']} | {r['points_play']['A']}/{r['points_play']['B']} | {r['points_awards']['A']}/{r['points_awards']['B']} | {meth} | "
             f"{r['possessions']['A']}/{r['possessions']['B']} | {100*r['attempt_share']['A']:.1f} / {100*r['attempt_share']['B']:.1f} | {sh.get('A',0)}/{sh.get('B',0)} | {so} | {r['passes']} | {r['pass_interception_pct']} | {r['interceptions_within_3m']} | {r['tackles_total']} | "
             f"{r['carry_attempts']['A']}/{r['carry_attempts']['B']} | {r['carry_goals']['A']}/{r['carry_goals']['B']} | {fr} | {r['dqs']['A']}/{r['dqs']['B']} | "
             f"{100*r['legal_arrow_rate']['A']:.1f}/{100*r['legal_arrow_rate']['B']:.1f} | {r['restart_timeouts']} | {r['restart_completion_ratio']} | {r['zone_unmarked_calls']} | {r['runtime_s']} | `{r['trace_hash']}` | `{r['state_hash']}` |")
L.append('')
L.append('## Real-roster team scores vs owner target (20 team-games)')
t = S['real_team_scores']; o = S['owner_target_canon']
L.append('| statistic | this soak (real, n=20) | owner target (canon) |')
L.append('|---|---|---|')
L.append(f"| median | {t['median']} | {o['median']} |")
L.append(f"| mean | {t['mean']} | — |")
L.append(f"| sd (sample) | {t['sd_sample']} | {o['sd']} |")
L.append(f"| p5 / p95 | {t['p5']:.1f} / {t['p95']:.1f} | {o['p5_p95'][0]} / {o['p5_p95'][1]} |")
L.append(f"| min / max | {t['min']} / {t['max']} | — |")
L.append('')
def stats_block(label, rs):
    L.append(f'## Summary: {label} (n = {len(rs)}; min / median / max across seeds)')
    L.append('| measure | min | median | max |')
    L.append('|---|---|---|---|')
    def add(name, fn):
        vals = [fn(r) for r in rs]; vals = [v for v in vals if v is not None]
        if not vals: L.append(f'| {name} | — | — | — |'); return
        fmt = lambda x: round(x, 3) if isinstance(x, float) else x
        L.append(f'| {name} | {fmt(min(vals))} | {fmt(statistics.median(vals))} | {fmt(max(vals))} |')
    add('team score A', lambda r: r['score']['A'])
    add('team score B', lambda r: r['score']['B'])
    add('play points A', lambda r: r['points_play']['A'])
    add('play points B', lambda r: r['points_play']['B'])
    add('award points A', lambda r: r['points_awards']['A'])
    add('award points B', lambda r: r['points_awards']['B'])
    add('possessions A', lambda r: r['possessions']['A'])
    add('possessions B', lambda r: r['possessions']['B'])
    add('% possessions ending in attempt A', lambda r: 100*r['attempt_share']['A'])
    add('% possessions ending in attempt B', lambda r: 100*r['attempt_share']['B'])
    add('shots A', lambda r: r['shots_by_team'].get('A', 0))
    add('shots B', lambda r: r['shots_by_team'].get('B', 0))
    for k in ('scored', 'keeper', 'field', 'own', 'out/award'):
        add(f'shot outcome % {k}', lambda r, k=k: r['shot_outcome_shares_pct'].get(k, 0))
    add('pass interception %', lambda r: r['pass_interception_pct'])
    add('interceptions within 3 m', lambda r: r['interceptions_within_3m'])
    add('tackles per match', lambda r: r['tackles_total'])
    add('carry attempts A', lambda r: r['carry_attempts']['A'])
    add('carry attempts B', lambda r: r['carry_attempts']['B'])
    add('carry goals A', lambda r: r['carry_goals']['A'])
    add('carry goals B', lambda r: r['carry_goals']['B'])
    add('DQs A', lambda r: r['dqs']['A'])
    add('DQs B', lambda r: r['dqs']['B'])
    add('legal-arrow rate A %', lambda r: 100*r['legal_arrow_rate']['A'])
    add('legal-arrow rate B %', lambda r: 100*r['legal_arrow_rate']['B'])
    add('restart timeouts', lambda r: r['restart_timeouts'])
    add('restart completion ratio', lambda r: r['restart_completion_ratio'])
    add('zone_unmarked calls', lambda r: r['zone_unmarked_calls'])
    add('zone_residence events', lambda r: r['zone_residence_events'])
    add('runtime s', lambda r: r['runtime_s'])
    L.append('')
real = [r for r in rows if r['block'] == 'real' and r.get('status') == 'final']
ctl = [r for r in rows if r['block'] == 'control' and r.get('status') == 'final']
stats_block('real roster', real)
stats_block('control', ctl)
L.append('## Foul reasons, all matches')
reasons = sorted({k for r in rows if r.get('status') == 'final' for k in r['foul_reasons']})
L.append('| match | ' + ' | '.join(reasons) + ' |'); L.append('|' + '---|' * (len(reasons) + 1))
for r in rows:
    if r.get('status') == 'final':
        L.append(f"| {r['name']} | " + ' | '.join(str(r['foul_reasons'].get(k, 0)) for k in reasons) + ' |')
(root / 'SUMMARY_TABLE.md').write_text('\n'.join(L) + '\n')
print('ok', len(L))
