# RB-3.21 evidence (PROVISIONAL, claude/rb-3-21-ball-material; code bd1e481; baseline RB-3.20 Part 1 014f774 / evidence 786a117)
Runs: real seeds 1/3/5 and control 1, python -m native.rulebook.reach_run with rb3_carrier_moves_enabled, rb3_handoff_block_enabled,
rb319_ball_in_play_enabled ON (worktree at bd1e481). Raw logs (gzipped): native/evidence/rb321/runs/m/{real,control}/raw-*.json.gz.
Baseline "p1" = native/evidence/rb320/runs/p1. Metrics: diag/metrics.py -> metrics.txt/metrics.json; diag/shots.py -> diag_shots.txt.

## OWNER BRIEFING
1. Accomplished (IMPLEMENTED, TESTED): the Beastball ball material (owner ruling 21 Nov) - quadratic air drag, horizontal speed kept per
   bounce, vertical restitution and constant rolling resistance as four named config values - replaces the old hard-coded ball on
   native-rb/3 in the engine step and in every forecast (receiver path forecast, launch solver, Keeper threat forecast, the Native
   Keeper's course). RB-3.20 Part 2 reverted (A4 1.0 s; RB-3.19 handoff rule) keeping "no hand-back within 2 s" and "never backward
   unless pressured".
2. Can do now: a missed pass no longer runs off the field - it stops about 20 m from release (median; was 28 m to its end, 55 m to the
   line); pass-out-of-bounds ends 5.3% of possessions (was 20.2%); the passer's team recovers 46% of missed passes (was 30%); pass
   completion .62-.65 (was .52-.55); real median team score 85.5 (inside 75-90); shots keep 99% of speed over 20 m.
3. Unproven: possessions per team 152.0 on real (target 100-150; was 166.7); interceptions/loose after a pass rose 15.1% -> 24.8% of
   possession ends; shot conversion .511 -> .491; single 4-match sample. The material values sit near both edges of the target band.
4. Blocking: none for the owner; BEHAVIORAL questions for Claude in QUESTIONS_FOR_CLAUDE.md.
5. Recommended: the lead picks the next lever for possessions (question 1) and whether to widen the T-B1/T-B2 band (question 2).

## Material parameters (config native/rulebook/config.py; model native/rulebook/ball_material.py)
| name | value | was (RB-3.20) | design basis |
|---|---|---|---|
| rb321_ball_drag_k | .0005 /m (dv/dt = -k|v|v) | linear .015 /s | T-B3 needs k <= .00527; smallest k on the feasible grid |
| rb321_ball_bounce_h | .44 | .76 | T-B1/T-B2/T-B4 rest distances |
| rb321_ball_restitution | .60 | .7746 | same |
| rb321_ball_roll_decel | 3.0 m/s^2 (constant) | v *= 1 - 3 dt | same; 3.0 ~ the old decay at 1 m/s |
| roll threshold | |vz| <= 2 m/s (unchanged) | same | engine rule |
Chosen as the gentlest grid point meeting T-B1..T-B4 (material_search.py, then a finer grid: k 0-.003 step .0005, h .42-.60 step .02,
e .30-.775 step .025-.05, a 2-5 step .5; 22 feasible points; cost = sum of squared relative changes, see question 3).
rb321_ball_material_enabled=false restores the RB-3.20 ball (and all rb321 keys leave the effective config).

## Scenario (engine, material ON; material_scenario.out / .json)
| release | 1 s | 2 s | 3 s | rest | forecast error at 1 s (predict_path / c4c_path) |
|---|---|---|---|---|---|
| 20 m/s level | 14.7 | 19.1 | - | 20.1 m at 2.9 s | 0.000 / 0.000 m |
| 20 m/s pass angle | 17.6 | 23.7 | - | 24.4 m at 2.8 s (T-B4 <= 25) | 0 / 0 |
| 35 m/s level | 25.7 | 33.5 | 37.3 | 38.2 m at 3.8 s (T-B1 38-45) | 0 / 0 |
| 35 m/s pass angle | 30.9 | 41.4 | 43.3 | 43.3 m at 3.2 s | 0 / 0 |
| 50 m/s level | 36.6 | 47.8 | 54.4 | 58.7 m at 4.7 s (T-B2 <= 60) | 0 / 0 |
| 50 m/s pass angle | 44.1 | 59.0 | 62.0 | 62.5 m at 3.6 s | 0 / 0 |
58 m/s level shot speed kept: 99.5% at 10 m, 99.2% at 20 m (T-B3 >= 90%), 98.9% at 30 m.
RB-3.20 ball for comparison (rb320 PHYSICS.md): 35 level rests 67.9 m, 50 level 97 m, 20 pass angle 47 m.

## Tests, identity, guards
- Full suite after the last change: 656 passed (15 new in test_rb321.py). Updated tests that encoded replaced behaviour:
  test_rb319.py restored to its RB-3.19 version (the RB-3.20b re-staging undone) with its toss-flight scenario pinned to the
  RB-3.20 ball (rb321_ball_material_enabled=False; under the material both tosses stay in); test_rb320.py Part 1 tests pinned
  to the RB-3.20 ball, and its Part 2 tests replaced by revert tests (A4 1.0 s refuses the 0.67 s corner pass; the RB-3.19
  handoff rule is back); the no-hand-back tests unchanged and passing.
- native-v0/2, native-v0/3, native-rb/2 hashes: all six rows of native/evidence/rb3-reach/legacy-hashes.txt reproduced at bd1e481.
- Flags off, rb319 off, carry_release_radius 0, rb320_exact_bounce off, rb321 material off: real seed 1 = 93b1f57e268ee6c4.../b9962ddfb23dbc96... (RB-3.16).

## Before/after (real seeds 1/3/5; control in brackets)
| metric | RB-3.20 Part 1 | RB-3.21 |
|---|---|---|
| team scores | 95-84, 92-75, 82-109 [106-60] | 57-76, 64-117, 99-95 [55-79] |
| median team score (real, 75-90) | 88.0 | 85.5 |
| possessions per team (100-150) | 166.7 [152.5] | 152.0 [142.5] |
| ends: pass out of bounds | 20.2% | 5.3% |
| ends: pass intercepted / loose after pass | 15.1% | 24.8% |
| ends: goal | 14.1% | 14.5% |
| ends: other out / carrier frozen / restart throw lost / second tackle | 11.6 / 8.5 / 7.3 / 6.2 % | 14.9 / 10.6 / 6.6 / 7.9 % |
| missed passes: median distance to their end (exit or pickup) | 28.0 m | 20.6 m |
| missed passes that leave the field untouched: count / median distance | 205 / 55.1 m | 48 / 32.1 m |
| missed passes recovered by the passer's team | 157 / 529 (30%) | 255 / 554 (46%) |
| open-play completion | .526/.548/.523 | .652/.642/.617 |
| shot conversion (scored share, real) | 114 / 223 = .511 | 114 / 232 = .491 |
| handoffs per match (real) | 297 | 256 |

## Per-match hashes (trace / state): hashes.txt
control-seed01 {'A': 55, 'B': 79} b4f5ed690665f894ad06560b1108a83f9b556b9cfe50e56463fdc39adb9f523b b28b5ba40f82c6d0d601af8dc6a8a86e0b3dcad763df14b6c75da83cd6645676 33097
real-seed01 {'A': 57, 'B': 76} 44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072 046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d 32528
real-seed03 {'A': 64, 'B': 117} 4ae3525dadd2f463c9337f7f76f879fae3d6298f740baf6f023dd95698ec6db9 19dc3a43d6be47264b57d0eab25948cfe43903165c85dc5c8575c50e0f730565 31752
real-seed05 {'A': 99, 'B': 95} 953c2c79f7283c9fca4de4c2538f372d1627555e6a04018935559effbef4e74d 8f78544774717c46aec571fa37f054b9ab0f9dfa5419248b0bb250e4c0460160 32743
