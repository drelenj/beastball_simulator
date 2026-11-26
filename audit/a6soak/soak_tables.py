"""Aggregate A6 soak games (Claude). Usage: python3 soak_tables.py GAMES_DIR WORKBOOK"""
import gzip, json, glob, sys, statistics as st
from collections import Counter, defaultdict
import openpyxl

games_dir, book = sys.argv[1], sys.argv[2]
wb = openpyxl.load_workbook(book, read_only=True)
rows = list(wb['Player Ratings'].iter_rows(values_only=True))
h = rows[0]; ovr = {r[h.index('Player ID')]: r[h.index('OVR 0.422')] for r in rows[1:] if r[1]}

G = []
for f in sorted(glob.glob(games_dir + '/*.json.gz')):
    d = json.loads(gzip.decompress(open(f, 'rb').read()))
    teams = {t['team']: t for t in d['box']['teams']}
    strength = {}
    for side in 'AB':
        pl = [p for p in d['box']['players'] if p['team'] == side and p.get('minutes')]
        m = sum(p['minutes'] for p in pl)
        strength[side] = sum(ovr[p['player'].split(':',1)[1]] * p['minutes'] for p in pl) / m
    G.append(dict(id=d['game_id'], names=d['teams'], score=d['score'], t=teams, s=strength, cpu=d['cpu_s'],
                  status=d['status'], inv=d['invariants'], keeper=d['keeper'], passes=d['passes'], unset=d['unset']))

def q(xs, p):
    xs = sorted(xs); k = (len(xs) - 1) * p; i = int(k)
    return xs[i] + (xs[min(i + 1, len(xs) - 1)] - xs[i]) * (k - i)
def line(name, xs, fmt='{:.1f}'):
    print(f'| {name} | ' + ' | '.join(fmt.format(v) for v in (st.mean(xs), st.median(xs), st.pstdev(xs), q(xs, .1), q(xs, .9))) + ' |')

T = [(g, side) for g in G for side in 'AB']
tv = lambda k: [g['t'][s].get(k, 0) for g, s in T]
print(f'games {len(G)}  team-games {len(T)}  statuses {Counter(g["status"] for g in G)}')
print('\n| Per team per game | mean | median | SD | P10 | P90 |\n|---|---|---|---|---|---|')
line('Points', tv('points')); line('Possessions', tv('possessions'))
line('Possessions ending in attempt (%)', [100 * g['t'][s]['possessions_ending_in_attempt'] / g['t'][s]['possessions'] for g, s in T])
for m in ('carry', 'throw_2', 'throw_3', 'throw_4', 'half_goal', 'full_goal_award', 'own'):
    line(f'Points from {m}', [g['t'][s]['scoring_points_by_method'].get(m, 0) for g, s in T])
line('Carry goals', [g['t'][s]['goals_by_method'].get('carry', 0) for g, s in T])
line('Stretch attempts', tv('stretch_attempts'))
line('Turnovers (all)', tv('turnovers'))
for k in ('interception', 'out_of_bounds', 'fumble', 'strip', 'tackle', 'zone_violation', 'play_clock'):
    line(f'Turnovers: {k}', [g['t'][s]['turnovers_by_type'].get(k, 0) for g, s in T])
line('Passes attempted', tv('passes_attempted'))
line('Pass completion (%)', [100 * g['t'][s]['passes_completed'] / max(1, g['t'][s]['passes_attempted']) for g, s in T])
line('Drops', tv('drops'))
line('Keeper save rate (% shots faced)', [100 * g['t'][s]['saves'] / max(1, g['t'][s]['shots_faced']) for g, s in T])
line('Shots faced', tv('shots_faced'))
line('Tackles made', tv('tackles_made')); line('Tackles attempted', tv('tackles_attempted'))
line('CPU s per game', [g['cpu'] for g in G])

margins = [abs(g['score']['A'] - g['score']['B']) for g in G]
print(f"\nMedian absolute margin {st.median(margins):.1f}; within 5: {100*sum(m<=5 for m in margins)/len(G):.1f}%; within 10: {100*sum(m<=10 for m in margins)/len(G):.1f}%")
# skill amplification: margin (A-B) vs strength gap (A-B)
x = [g['s']['A'] - g['s']['B'] for g in G]; y = [g['score']['A'] - g['score']['B'] for g in G]
mx, my = st.mean(x), st.mean(y)
slope = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sum((a - mx) ** 2 for a in x)
r = st.correlation(x, y)
fav = [(yy > 0) == (xx > 0) for xx, yy in zip(x, y) if abs(xx) >= 1]
print(f"Margin vs minutes-weighted OVR 0.422 gap: slope {slope:.2f} points per OVR point, r {r:.2f}; stronger side won {100*sum(fav)/len(fav):.0f}% of {len(fav)} games with gap >= 1")
for lo, hi in ((0, 1), (1, 2), (2, 3), (3, 5), (5, 99)):
    sel = [(abs(a), b if a > 0 else -b) for a, b in zip(x, y) if lo <= abs(a) < hi]
    if sel: print(f"  gap {lo}-{hi}: n {len(sel)}, mean margin for stronger side {st.mean(b for _, b in sel):.1f}, stronger won {100*sum(b>0 for _, b in sel)/len(sel):.0f}%")
print('\nStrength range (team-games):', round(min(g['s'][s] for g, s in T), 1), '-', round(max(g['s'][s] for g, s in T), 1))
