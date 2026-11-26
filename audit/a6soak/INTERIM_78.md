# A6 soak, interim: 78 of 210 games (codex/a6-soak-data @ 0675f4560d2ff2d1dea2bac9532d56bdbb2fe57b)

Games r000-r038, seeds 1-2: three complete balanced rounds (every team 6 games vs 3 opponents). Garvian-Ala not yet run. Box-score definitions. Regenerate: python3 audit/a6soak/soak_tables.py <games dir> <ratings 0.4 workbook>

```
games 78  team-games 156  statuses Counter({'final': 78})

| Per team per game | mean | median | SD | P10 | P90 |
|---|---|---|---|---|---|
| Points | 99.6 | 97.5 | 27.4 | 67.5 | 136.0 |
| Possessions | 160.6 | 161.0 | 6.9 | 152.0 | 169.5 |
| Possessions ending in attempt (%) | 29.9 | 30.4 | 4.8 | 23.4 | 35.8 |
| Points from carry | 26.8 | 28.0 | 15.9 | 7.0 | 49.0 |
| Points from throw_2 | 2.1 | 2.0 | 2.3 | 0.0 | 6.0 |
| Points from throw_3 | 29.7 | 30.0 | 9.9 | 15.0 | 42.0 |
| Points from throw_4 | 35.9 | 36.0 | 14.2 | 20.0 | 56.0 |
| Points from half_goal | 1.8 | 2.0 | 1.3 | 0.0 | 4.0 |
| Points from full_goal_award | 2.1 | 3.0 | 2.5 | 0.0 | 6.0 |
| Points from own | 1.2 | 0.0 | 1.5 | 0.0 | 4.0 |
| Carry goals | 3.8 | 4.0 | 2.3 | 1.0 | 7.0 |
| Stretch attempts | 1.2 | 1.0 | 1.1 | 0.0 | 3.0 |
| Turnovers (all) | 158.5 | 159.0 | 6.9 | 149.5 | 167.5 |
| Turnovers: interception | 34.0 | 34.0 | 6.2 | 26.0 | 42.0 |
| Turnovers: out_of_bounds | 41.0 | 42.0 | 5.9 | 32.0 | 48.0 |
| Turnovers: fumble | 14.8 | 14.0 | 4.0 | 10.0 | 20.0 |
| Turnovers: strip | 1.4 | 1.0 | 1.1 | 0.0 | 3.0 |
| Turnovers: tackle | 13.4 | 13.0 | 4.1 | 8.0 | 19.0 |
| Turnovers: zone_violation | 4.6 | 4.0 | 2.2 | 2.0 | 8.0 |
| Turnovers: play_clock | 1.1 | 1.0 | 1.2 | 0.0 | 3.0 |
| Passes attempted | 267.8 | 267.0 | 16.1 | 249.5 | 286.5 |
| Pass completion (%) | 77.1 | 77.0 | 2.5 | 73.7 | 80.5 |
| Drops | 10.3 | 10.0 | 4.7 | 4.5 | 17.0 |
| Keeper save rate (% shots faced) | 33.3 | 32.8 | 7.2 | 24.3 | 42.2 |
| Shots faced | 48.5 | 48.0 | 9.6 | 37.0 | 59.5 |
| Tackles made | 59.7 | 59.0 | 9.0 | 48.0 | 72.0 |
| Tackles attempted | 249.3 | 246.0 | 31.4 | 216.0 | 290.5 |
| CPU s per game | 237.8 | 238.2 | 8.4 | 226.0 | 247.3 |

Median absolute margin 31.5; within 5: 3.8%; within 10: 17.9%
Margin vs minutes-weighted OVR 0.422 gap: slope 5.96 points per OVR point, r 0.66; stronger side won 84% of 56 games with gap >= 1
  gap 0-1: n 22, mean margin for stronger side 9.8, stronger won 77%
  gap 1-2: n 12, mean margin for stronger side 2.0, stronger won 67%
  gap 2-3: n 6, mean margin for stronger side -15.2, stronger won 50%
  gap 3-5: n 15, mean margin for stronger side 34.3, stronger won 93%
  gap 5-99: n 23, mean margin for stronger side 49.3, stronger won 96%

Strength range (team-games): 76.9 - 89.6
```
