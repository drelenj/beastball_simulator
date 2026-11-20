# RB-3.16 side-swap test (claude/soak-rb-3-16-swap from 9c37fd4)

TESTED measurements only. Not ACCEPTED. Question: is the Ala Apex over Garvian Guardians gap in the RB-3.16 soak (409135f) the TEAMS or the SIDE (slot A vs slot B)?

## OWNER BRIEFING

1. **Accomplished (TESTED).** Driver copy with a `--swap` flag (only change to the RB-3.14 driver). Verification without `--swap` reproduced real seed 1 exactly (trace `93b1f57e…`, state `b9962ddf…`). All ten real seeds were run with `--swap` (Ala Apex in slot A), and all finished with status `final`.
2. **What it shows (TESTED).** Both effects are present, and the team effect is the larger one. Ala Apex is better by 18.1 points per game when averaged over both slot orientations (paired t = 3.2, n = 10 seeds; 95% interval roughly 5 to 31). The slot effect is +6.0 points for slot B over slot A, pooled over 20 games; per-seed t = 1.4, so it is not established at this sample size. The original 24.1-point gap splits exactly into 18.1 team plus 6.0 side.
3. **Unproven.** The slot effect is not significant with 10 seeds. Almost all of it sits on the Ala side: Ala scores +12.7 more in slot B than slot A, while Garvian shows −0.7. So the side effect may be team-specific, and this test cannot separate that from noise. The control block (identical ratings) was not run with `--swap`, because its two teams have identical ratings and the instruction was to skip. The original control soak nonetheless shows slot B ahead by +20.7 across 3 games with identical ratings. That is evidence of a side effect with no team difference, but 3 games is far too few to rely on.
4. **Blocking.** Nothing blocks the run. The next test needs more control games.
5. **Recommended action.** Owner to run the identical-ratings control in both slot orders for 10 or more seeds. That isolates the side effect cleanly and is the decisive test for the slot question. Owner to decide whether the team gap of about 18 points (vs the pro gap of about 11) is acceptable given its 5-to-31 interval.

## Verdict
**Both.** TEAM effect: about +18 points per game for Ala Apex, consistent in both orientations (Ala won 9 of 10 in the original and 7 of 10 swapped, 16 of 20 overall). SIDE effect: about +6 points for slot B over slot A across all 20 games, not significant at n = 10, and concentrated on Ala. The control with identical ratings points to a side effect of similar or larger size, but it is only 3 games.

## Table: per seed
| seed | original: Garvian A - Ala B | swapped: Ala A - Garvian B | Ala won (orig / swap) | team effect (Ala − Garv, avg) | slot B − slot A |
|---|---|---|---|---|---|
| 1 | 74-92 | 89-60 | yes / yes | +23.5 | −5.5 |
| 2 | 71-104 | 70-88 | yes / no | +7.5 | +25.5 |
| 3 | 42-92 | 75-42 | yes / yes | +41.5 | +8.5 |
| 4 | 68-76 | 62-47 | yes / yes | +11.5 | −3.5 |
| 5 | 84-60 | 75-78 | no / no | −13.5 | −10.5 |
| 6 | 58-82 | 62-90 | yes / no | −2.0 | +26.0 |
| 7 | 67-104 | 98-64 | yes / yes | +35.5 | +1.5 |
| 8 | 55-101 | 82-59 | yes / yes | +34.5 | +11.5 |
| 9 | 74-94 | 83-49 | yes / yes | +27.0 | −7.0 |
| 10 | 51-80 | 62-60 | yes / yes | +15.5 | +13.5 |

## Summary
| measure | value |
|---|---|
| Ala Apex mean, slot B (original) | 88.5 |
| Ala Apex mean, slot A (swapped) | 75.8 |
| Ala Apex wins, original / swapped | 9/10 / 7/10 |
| Garvian mean, slot A (original) | 64.4 |
| Garvian mean, slot B (swapped) | 63.7 |
| slot A mean points, all 20 games | 70.1 |
| slot B mean points, all 20 games | 76.1 |
| slot B − slot A, all 20 games | +6.0 |
| team effect (Ala − Garvian), per seed: mean / sd / t | +18.1 / 17.6 / 3.25 |
| side effect (slot B − slot A), per seed: mean / sd / t | +6.0 / 13.2 / 1.44 |
| Ala side difference (B − A) | +12.7 |
| Garvian side difference (B − A) | −0.7 |
| control, identical ratings, original orientation, n = 3: slot B − slot A | +20.7 (not run swapped) |

## Files
- Real swapped results: `native/evidence/rb316-swap/real/real-seedNN-swap.json`; raw logs: `native/evidence/rb316-swap/real/raw-real-seedNN-swap.json.gz`.
- Gate (no `--swap`, reproduces the original): `native/evidence/rb316-swap/real/real-seed01.json`, raw `raw-real-seed01.json.gz`.
- Original orientation results (from 409135f): `native/evidence/rb316-swap/original/real/` and `original/control/`.
- Tables: `native/evidence/rb316-swap/SWAP_TABLE.md`, `swap_table.json`.
- Driver: `native/evidence/rb316-swap/tools/soak_driver3_swap.py`; diff against the RB-3.14 original: `tools/driver.diff`; wrapper: `tools/reach_run_swap.py`.
- Recompute: `python3 native/evidence/rb316-swap/tools/swap_report.py native/evidence/rb316-swap`.
