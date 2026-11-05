#!/usr/bin/env python3
"""Writes sample_roster_A.csv / sample_roster_B.csv (name,position,overall) with placeholder names, and generated_players_<X>.csv
(the full attribute sheet the generator produces from them).  Replace the names/positions/overalls with real ones."""
import csv, random, sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import player_gen_v1 as G
LAYOUT = [('QB', 3), ('RB', 2), ('WR', 3), ('TE', 1), ('OL', 3), ('LB', 3), ('CB', 3), ('S', 2), ('K', 1), ('A', 1)]
def main():
    for t, seed in (('A', 11), ('B', 12)):
        rng = random.Random(seed); rows = []
        for pos, k in LAYOUT:
            for i in range(k): rows.append(dict(name=f'Team{t} {pos}{i + 1}', position=pos, overall=round(rng.uniform(62, 86), 1)))
        with open(os.path.join(HERE, f'sample_roster_{t}.csv'), 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['name', 'position', 'overall']); w.writeheader(); w.writerows(rows)
        gen = [G.generate(r['name'], r['position'], r['overall']) for r in rows]
        with open(os.path.join(HERE, f'generated_players_{t}.csv'), 'w', newline='') as f:
            cols = ['name', 'position', 'archetype', 'overall', 'height_m', 'mass_kg'] + list(gen[0]['ratings'])
            w = csv.writer(f); w.writerow(cols)
            for a in gen: w.writerow([a['name'], a['position'], a['archetype'], round(a['overall'], 3), round(a['height_m'], 3), round(a['mass_kg'], 1)] + [round(a['ratings'][k], 3) for k in gen[0]['ratings']])
if __name__ == '__main__': main()
