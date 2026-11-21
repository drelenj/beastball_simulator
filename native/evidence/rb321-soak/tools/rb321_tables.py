"""Per-match and summary tables for RB-3.21 (reads rb321_table.json and rb321_summary.json only).
python3 native/evidence/rb321-soak/tools/rb321_tables.py native/evidence/rb321-soak
"""
import json, statistics as st, sys
from pathlib import Path
root = Path(sys.argv[1])
rows = json.loads((root / 'rb321_table.json').read_text())
S = json.loads((root / 'rb321_summary.json').read_text())
L = ['# RB-3.21 soak: per-match and summary (TESTED measurements; not ACCEPTED)', '']
L.append('## Per match')
L.append('| match | score A-B | play A/B | award A/B | possessions A/B (metrics) | control-change spans | end causes (n) | shots A/B | scored A/B | conv % | points by method | handoffs done/started | blocks engaged/shed | trucks att/broken | stiff arms | stretch goals | DQs A/B | legal-arrow % A/B | restart TO | restart throw lost ≤5 s | runtime s | trace_hash | state_hash |')
L.append('|' + '---|' * 24)
for r in rows:
    if r['status'] != 'final':
        L.append(f"| {r['name']} | {r['status']} {r.get('error')} |"); continue
    causes = '; '.join(f'{k} {v}' for k, v in sorted(r['possession_end_causes'].items(), key=lambda kv: -kv[1]))
    meth = ', '.join(f'{k} {v}' for k, v in r['points_by_method'].items())
    L.append(f"| {r['name']} | {r['score']['A']}-{r['score']['B']} | {r['points_play']['A']}/{r['points_play']['B']} | {r['points_awards']['A']}/{r['points_awards']['B']} | "
             f"{r['possessions']['A']}/{r['possessions']['B']} | {sum(r['possession_end_causes'].values())} | {causes} | {r['shots']['A']}/{r['shots']['B']} | {r['shots_scored']['A']}/{r['shots_scored']['B']} | {r['shot_conversion_pct']} | {meth} | "
             f"{r['handoffs_completed']}/{r['handoffs_started']} | {r['blocks_engaged']}/{r['blocks_shed']} | {r['trucks_attempted']}/{r['trucks_broken']} | {r['stiff_arms']} | {r['stretch_goals']} | "
             f"{r['dqs']['A']}/{r['dqs']['B']} | {100*r['legal_arrow_rate']['A']:.1f}/{100*r['legal_arrow_rate']['B']:.1f} | {r['restart_timeouts']} | {r['restart_throw_lost_within_5s']} | {r['runtime_s']} | `{r['trace_hash']}` | `{r['state_hash']}` |")
L.append('')
ts = S['team_score']; pt = S['possessions_team']
L += ['## Summary vs owner ranges (real roster, 20 team-games)', '| measure | this soak | owner range / reference |', '|---|---|---|',
      f"| median team score | {ts['median']} | 75-90 (pro NBL median 76) |",
      f"| mean team score | {ts['mean']} | — |",
      f"| team-score sd (sample) | {ts['sd_sample']} | pro reference 12.7 |",
      f"| team-score p5 / p95 | {ts['p5']} / {ts['p95']} | — |",
      f"| possessions per team, mean | {pt['mean']} | 100-150 |",
      f"| possessions per team, median | {pt['median']} | 100-150 |",
      f"| possessions per team, min / max | {pt['min']} / {pt['max']} | 100-150 |",
      f"| team-matches with possessions > 150 | {pt['n_over_150']} of {pt['n']} team-matches" if 'n' in pt else f"| team-matches with possessions > 150 | {pt['n_over_150']} of 20 |",
      f"| matches where any team exceeds 150 | {S['matches_any_team_over_150']} of 10 |", '']
real = [r for r in rows if r['block'] == 'real' and r['status'] == 'final']
ctl = [r for r in rows if r['block'] == 'control' and r['status'] == 'final']
def block(label, rs):
    L.append(f'## Summary: {label} (n = {len(rs)}; min / median / max across matches)')
    L.append('| measure | min | median | max |'); L.append('|---|---|---|---|')
    def add(name, fn):
        v = [fn(r) for r in rs]; v = [x for x in v if x is not None]
        if not v: L.append(f'| {name} | — | — | — |'); return
        f = lambda x: round(x, 2) if isinstance(x, float) else x
        L.append(f'| {name} | {f(min(v))} | {f(st.median(v))} | {f(max(v))} |')
    add('score A', lambda r: r['score']['A']); add('score B', lambda r: r['score']['B'])
    add('possessions A', lambda r: r['possessions']['A']); add('possessions B', lambda r: r['possessions']['B'])
    add('control-change spans', lambda r: sum(r['possession_end_causes'].values()))
    for c in ('goal', 'pass out of bounds', 'other out', 'intercepted/loose', 'carrier frozen', 'carrier stopped short', 'first tackle', 'second tackle', 'restart (other)', 'unclassified'):
        add(f'end cause: {c}', lambda r, c=c: r['possession_end_causes'].get(c, 0))
    add('shots A', lambda r: r['shots']['A']); add('shots B', lambda r: r['shots']['B'])
    add('shot conversion %', lambda r: r['shot_conversion_pct'])
    for m in ('release', 'carry', 'half', 'award', 'own'):
        add(f'points {m} (both teams)', lambda r, m=m: r['points_by_method'].get(m, 0))
    add('handoffs completed', lambda r: r['handoffs_completed']); add('handoffs started', lambda r: r['handoffs_started'])
    add('blocks engaged', lambda r: r['blocks_engaged']); add('blocks shed', lambda r: r['blocks_shed'])
    add('trucks attempted', lambda r: r['trucks_attempted']); add('trucks broken', lambda r: r['trucks_broken'])
    add('stiff arms', lambda r: r['stiff_arms']); add('stretch goals', lambda r: r['stretch_goals'])
    add('DQs A', lambda r: r['dqs']['A']); add('DQs B', lambda r: r['dqs']['B'])
    add('legal-arrow % A', lambda r: 100 * r['legal_arrow_rate']['A']); add('legal-arrow % B', lambda r: 100 * r['legal_arrow_rate']['B'])
    add('restart timeouts', lambda r: r['restart_timeouts'])
    add('restart throw lost ≤5 s', lambda r: r['restart_throw_lost_within_5s'])
    add('zone_unmarked calls', lambda r: r['zone_unmarked_calls'])
    L.append('')
block('real roster', real); block('control', ctl)
(root / 'SUMMARY_TABLE.md').write_text('\n'.join(L) + '\n')
print('ok', len(L))
