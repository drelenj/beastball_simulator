# E1 league soak, interim: 77 of 210 games (codex/e1-soak-data @ 672f2bc7e488290d52c903096b099f6664ac76ba)

Games r000-r037 both seeds + r038-s2 (same schedule as the A6 soak; 77 games pair one-to-one with A6). Box-score definitions. Regenerate: python3 audit/a6soak/soak_tables.py <games dir> <ratings 0.4 workbook>

Paired vs A6 (77 common games, per team per game): points -8.5 +/- 2.1, possessions -41.1 +/- 1.1, absolute margin -6.1 +/- 3.4; games within 5: A6 3.9%, E1 13.0%.

```
games 77  team-games 154  statuses Counter({'final': 77})

| Per team per game | mean | median | SD | P10 | P90 |
|---|---|---|---|---|---|
| Points | 91.3 | 89.0 | 23.3 | 64.0 | 122.4 |
| Possessions | 119.4 | 119.0 | 7.7 | 109.0 | 129.0 |
| Possessions ending in attempt (%) | 36.6 | 37.1 | 6.1 | 29.2 | 44.3 |
| Points from carry | 15.5 | 14.0 | 12.3 | 0.0 | 28.0 |
| Points from throw_2 | 2.4 | 2.0 | 2.3 | 0.0 | 6.0 |
| Points from throw_3 | 34.1 | 33.0 | 11.0 | 21.0 | 48.0 |
| Points from throw_4 | 38.4 | 36.0 | 13.9 | 21.2 | 54.8 |
| Points from half_goal | 0.1 | 0.0 | 0.2 | 0.0 | 0.0 |
| Points from full_goal_award | 0.1 | 0.0 | 0.6 | 0.0 | 0.0 |
| Points from own | 0.7 | 0.0 | 1.3 | 0.0 | 2.0 |
| Carry goals | 2.2 | 2.0 | 1.8 | 0.0 | 4.0 |
| Stretch attempts | 9.4 | 2.0 | 12.2 | 0.0 | 23.0 |
| Turnovers (all) | 117.3 | 117.0 | 7.7 | 107.0 | 127.0 |
| Turnovers: interception | 27.3 | 26.5 | 6.4 | 19.3 | 35.0 |
| Turnovers: out_of_bounds | 28.0 | 28.0 | 5.4 | 21.3 | 35.0 |
| Turnovers: fumble | 4.2 | 4.0 | 1.9 | 2.0 | 7.0 |
| Turnovers: strip | 1.5 | 1.0 | 1.2 | 0.0 | 3.0 |
| Turnovers: tackle | 7.4 | 7.0 | 2.8 | 4.0 | 11.0 |
| Turnovers: zone_violation | 4.5 | 4.0 | 2.1 | 2.0 | 7.0 |
| Turnovers: play_clock | 5.9 | 5.0 | 2.6 | 3.0 | 9.0 |
| Passes attempted | 260.0 | 259.0 | 18.7 | 239.0 | 282.7 |
| Pass completion (%) | 80.4 | 80.0 | 3.0 | 76.4 | 84.4 |
| Drops | 11.2 | 11.0 | 4.8 | 5.0 | 17.0 |
| Keeper save rate (% shots faced) | 22.1 | 22.2 | 6.8 | 13.7 | 30.3 |
| Shots faced | 46.9 | 46.0 | 9.2 | 35.3 | 60.0 |
| Tackles made | 72.3 | 71.0 | 9.3 | 61.0 | 86.0 |
| Tackles attempted | 268.3 | 271.5 | 35.8 | 221.2 | 312.0 |
| CPU s per game | 292.5 | 292.2 | 11.2 | 281.1 | 304.8 |

Median absolute margin 29.0; within 5: 13.0%; within 10: 22.1%
Margin vs minutes-weighted OVR 0.422 gap: slope 4.65 points per OVR point, r 0.64; stronger side won 82% of 57 games with gap >= 1
  gap 0-1: n 20, mean margin for stronger side -1.4, stronger won 45%
  gap 1-2: n 12, mean margin for stronger side 12.7, stronger won 75%
  gap 2-3: n 7, mean margin for stronger side -9.4, stronger won 29%
  gap 3-5: n 13, mean margin for stronger side 23.2, stronger won 92%
  gap 5-99: n 25, mean margin for stronger side 36.9, stronger won 96%

Strength range (team-games): 77.2 - 89.7
```
