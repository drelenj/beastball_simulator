# RB/3.1 provisional soak (rb-3-2-toss-timeout-provisional @ a8bda94)

**Measurements only. Nothing here is ACCEPTED.** Provisional branch, provisional banded scoring (`provisional=True` in the report basis).

Provenance: commit a8bda94; roster ref 81f92e3 (Garvian Guardians = A, Ala Apex = B); scoring banded; config native-rb/3; step cap 200,000 per match; 2 matches concurrently on 2 cores; runner `tools/soak_driver.py`, aggregation `tools/soak_table.py`/`tools/soak_analyze.py`.

## Determinism check (real roster, seed 1, two runs)

| run | status | score | steps | trace_hash | state_hash |
|---|---|---|---|---|---|
| run a | final | 92-143 | 57526 | `cf4db123fbf60664b730789e6cdff98cd1797705da472ff09411c452249d1be1` | `eea794457c6c6034efd65e71f0d09f4c3592bee19cb8ce0eda44e337b6edb36f` |
| run b | final | 92-143 | 57526 | `cf4db123fbf60664b730789e6cdff98cd1797705da472ff09411c452249d1be1` | `eea794457c6c6034efd65e71f0d09f4c3592bee19cb8ce0eda44e337b6edb36f` |

Result: **identical** trace_hash and state_hash across both runs.

## Block A: real roster (seeds 1, 2, 3, 7, 8, 9, 10)

| seed | status | score A-B | possessions A / B | share ending in attempt A / B | goal pts (play) A / B | foul-award pts A / B | carry attempts A / B | carry goals A / B | groundings | restart timeouts | legal-arrow rate A / B | DQs A / B | runtime_s | trace_hash | state_hash |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | final | 92-143 | 324 / 325 | 1.5% / 3.7% | 5 / 12 | 87 / 131 | 18 / 25 | 0 / 0 | 140 | 79 | 43.8% / 34.4% | 19 / 17 | 115.07 | `cf4db123fbf60664…` | `eea794457c6c6034…` |
| 2 | final | 99-38 | 336 / 336 | 2.7% / 4.5% | 0 / 11 | 99 / 27 | 23 / 25 | 0 / 0 | 194 | 53 | 52.9% / 27.3% | 9 / 16 | 135.2 | `c4c30f5ff578e9a3…` | `a389033f7f464de3…` |
| 3 | final | 99-63 | 317 / 317 | 3.2% / 3.8% | 14 / 8 | 85 / 55 | 22 / 27 | 0 / 0 | 145 | 54 | 61.9% / 37.8% | 14 / 15 | 120.62 | `201d592724833248…` | `f4be0a6c15e846ae…` |
| 7 | final | 97-94 | 314 / 317 | 5.1% / 4.7% | 13 / 5 | 84 / 89 | 31 / 32 | 0 / 0 | 182 | 63 | 38.4% / 40.4% | 17 / 17 | 122.78 | `c97496189fe89797…` | `eb42ac9b99dc9e0e…` |
| 8 | final | 93-121 | 338 / 340 | 5.3% / 2.1% | 18 / 7 | 75 / 114 | 35 / 46 | 0 / 0 | 161 | 64 | 37.3% / 54.7% | 19 / 16 | 116.33 | `452b1d24e6fb769e…` | `009cfc0a91fcaae3…` |
| 9 | final | 91-79 | 328 / 330 | 3.7% / 3.0% | 4 / 5 | 87 / 74 | 45 / 19 | 0 / 0 | 183 | 45 | 52.9% / 39.2% | 17 / 17 | 113.49 | `0a5a68baeb2adb04…` | `c0047cacac1f2f58…` |
| 10 | final | 68-71 | 403 / 405 | 2.2% / 1.7% | 3 / 9 | 65 / 62 | 26 / 28 | 0 / 0 | 135 | 284 | 54.2% / 13.8% | 21 / 13 | 132.59 | `813c58a4f3fa08f2…` | `e548fd45a499d5c7…` |

Seeds 1 and 2 are reruns on the new code line; seeds 4, 5, 6 were not run in this block (not in the request).

## Block B: control, uniform athletes (rating 0.70, height 2.39 m, mass 226 kg, reach 3.05 m), seeds 1-10

**All 10 seeds are NON-FINISHING** (hit the 200,000-step cap). Table of stall facts:

| seed | status | steps | simulated ms | live ms | phase at cap | score | possessions | restarts | foul/DQ | last restart kind & spot | runtime_s | trace_hash | state_hash |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **NON-FINISHING** | 200000 | 23038789 | 18772989 | Phase.OPENING | 0-0 | 0 / 0 | 0 | none | none recorded | 427.74 | `84ed5e8e085a6a79…` | `f33884dd5372c753…` |
| 2 | **NON-FINISHING** | 200000 | 23038789 | 18772989 | Phase.OPENING | 0-0 | 0 / 0 | 0 | none | none recorded | 422.14 | `84ed5e8e085a6a79…` | `f33884dd5372c753…` |
| 3 | **NON-FINISHING** | 200000 | 23038789 | 18772989 | Phase.OPENING | 0-0 | 0 / 0 | 0 | none | none recorded | 422.1 | `84ed5e8e085a6a79…` | `f33884dd5372c753…` |
| 4 | **NON-FINISHING** | 200000 | 23038789 | 18772989 | Phase.OPENING | 0-0 | 0 / 0 | 0 | none | none recorded | 422.94 | `84ed5e8e085a6a79…` | `f33884dd5372c753…` |
| 5 | **NON-FINISHING** | 200000 | 23038789 | 18772989 | Phase.OPENING | 0-0 | 0 / 0 | 0 | none | none recorded | 433.28 | `84ed5e8e085a6a79…` | `f33884dd5372c753…` |
| 6 | **NON-FINISHING** | 200000 | 23038789 | 18772989 | Phase.OPENING | 0-0 | 0 / 0 | 0 | none | none recorded | 432.49 | `84ed5e8e085a6a79…` | `f33884dd5372c753…` |
| 7 | **NON-FINISHING** | 200000 | 23038789 | 18772989 | Phase.OPENING | 0-0 | 0 / 0 | 0 | none | none recorded | 421.17 | `84ed5e8e085a6a79…` | `f33884dd5372c753…` |
| 8 | **NON-FINISHING** | 200000 | 23038789 | 18772989 | Phase.OPENING | 0-0 | 0 / 0 | 0 | none | none recorded | 422.38 | `84ed5e8e085a6a79…` | `f33884dd5372c753…` |
| 9 | **NON-FINISHING** | 200000 | 23038789 | 18772989 | Phase.OPENING | 0-0 | 0 / 0 | 0 | none | none recorded | 435.7 | `84ed5e8e085a6a79…` | `f33884dd5372c753…` |
| 10 | **NON-FINISHING** | 200000 | 23038789 | 18772989 | Phase.OPENING | 0-0 | 0 / 0 | 0 | none | none recorded | 437.99 | `84ed5e8e085a6a79…` | `f33884dd5372c753…` |

The seeds share one trace_hash and one state_hash, so the seed had no observable effect in this block. Event log (seed 1): 58 period_end events; ~12,300 each of hunt_start, hunt_claim, simultaneous_contact, joint_control, hunt_retake, rb_hunt_release; no possession, restart, foul, arrow, or goal events. Stall cause not determined here.

## Extended: goal points, live play vs within one possession of a restart (real roster)

"Restart-linked" = goal scored by the team that received the most recent restart, before any possession change to the other team. Everything else = live play.

| seed | A live | A restart-linked | B live | B restart-linked |
|---|---|---|---|---|
| 1 | 0 | 5 | 6 | 6 |
| 2 | 0 | 0 | 11 | 0 |
| 3 | 11 | 3 | 2 | 6 |
| 7 | 10 | 3 | 5 | 0 |
| 8 | 14 | 4 | 5 | 2 |
| 9 | 4 | 0 | 0 | 5 |
| 10 | 0 | 3 | 2 | 7 |

## Extended: fouls by rule and offender role (real roster, all seeds summed)

| rule (reason) | offender role | team | count |
|---|---|---|---|
| archery_target | archer | A | 70 |
| archery_target | archer | B | 70 |
| archery_target | field | A | 283 |
| archery_target | field | B | 348 |
| archery_target | keeper | A | 15 |
| frozen_contact | field | A | 95 |
| frozen_contact | field | B | 54 |
| frozen_contact | keeper | A | 6 |
| frozen_contact | keeper | B | 3 |
| illegal_release | field | A | 9 |
| illegal_release | field | B | 16 |
| immune_contact | field | A | 12 |
| immune_contact | field | B | 1 |
| zone_unmarked | field | A | 78 |
| zone_unmarked | field | B | 75 |

## Extended: DQs by offence class and offender role (real roster, all seeds summed)

| offence class (kind_of_foul) | offender role | team | DQs |
|---|---|---|---|
| major | field | A | 29 |
| major | field | B | 14 |
| major | keeper | A | 1 |
| major | keeper | B | 1 |
| minor | archer | A | 14 |
| minor | archer | B | 14 |
| minor | field | A | 69 |
| minor | field | B | 82 |
| minor | keeper | A | 3 |

## Extended: foul awards by method and team (real roster, all seeds summed)

| method | points | team | awards |
|---|---|---|---|
| full_goal_award | 3 | A | 74 |
| full_goal_award | 3 | B | 87 |
| half_goal | 1 | A | 360 |
| half_goal | 1 | B | 291 |

## Extended: arrows per Archer (real roster, all seeds summed; Archer-role players only)

Legal release = `arrow_release` event by that player. Illegal target = `foul` with reason `archery_target` and that player as actor. Hit and miss are not recorded (see missing fields).

| Archer (player id) | team | legal releases | illegal target | miss |
|---|---|---|---|---|
| A:DRAFT26-09 | A | 28 | 35 | not recorded |
| A:NBL25-D32 | A | 24 | 35 | not recorded |
| B:NBL24-01-12 | B | 15 | 35 | not recorded |
| B:UFA26-BB-04 | B | 17 | 35 | not recorded |

Legal releases by shooter role, all seeds: {'archer': 84, 'field': 488, 'keeper': 18}. Most legal releases are by field players, not Archers.

## Missing fields (not in the existing report; not guessed)

- **Carry attempts by outcome** (tackled / grounded / turnover / stopped short): not recorded. Only counts and timestamps exist.
- **Foul award to originating rule**: foul_award rows carry method and points, not the foul that caused them.
- **DQ to rule**: discipline calls carry kind_of_foul and dq, not the reason.
- **Arrow miss and hit**: not recorded as outcomes. arrow_geometry_impact exists but is not classified.
- **Stall cause in control block**: not determined.


## Files

- `real/`, `control/`, `determinism/`: per-seed summary JSON (`*-seedNN.json`) and raw engine logs (`raw-*.json.gz`; gunzip before running `tools/soak_analyze.py`).
- `summary.json`, `extended.json`: aggregated data. `tools/`: runner and aggregation scripts used for this run.
