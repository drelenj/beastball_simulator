# Archer platform study (omniscient archer, drag-aware lead on, arrows 100 m/s)
6 short games per row, Ala vs Xenar rosters, seeds 1-6. Heights/setbacks/ranges are test inputs, not canon.
Knobs (env): PLAT=1, PLAT_H, PLAT_SET, RULESET (1.0.1|1.0.2), ARCH_RMIN/ARCH_RMAX, ARCH_NEAR, FREEZE_CAP, ARROW_V. Run: `python3 plat_study.py <tag> 1,2,3,4,5,6`.
Platform: static x,y (setback behind own goal plane, y=50), arrow origin = height + .72 x body height, no lane limit, reload at the platform.

| config | arrows | freezes (carrier / non-carrier) | on-target | blocked | inert | misses | mean range m | points A-B |
|---|---|---|---|---|---|---|---|---|
| stock lateral zone, ruleset 1.0.1 | 148 | 8 (8/0) | 13 | 43 | 48 | 71 | 54 | 18-34 |
| lateral zone, 1.0.2, any target | 181 | 29 (5/24) | 15 | 39 | 25 | 102 | 52 | 15-33 |
| platform 5 m, 1.0.2 | 165 | 23 (10/13) | 22 | 13 | 12 | 122 | 55 | 12-40 |
| platform 10 m, 1.0.2 | 157 | 24 (13/11) | 24 | 15 | 15 | 113 | 56 | 23-55 |
| platform 15 m, 1.0.2 | 157 | 28 (17/11) | 30 | 4 | 6 | 118 | 57 | 15-45 |
| platform 10 m, range 120 m | 194 | 20 (7/13) | 16 | 17 | 12 | 133 | 75 | 24-20 |
| platform 10 m, cap 2 freezes/possession | 157 | 24 (13/11) | 24 | 15 | 15 | 113 | 56 | 23-55 |

Notes: cap 2 never bound (identical to uncapped) - cap 1 needed to see an effect. Small samples; scores are noise-level.
