# RB/3.1 provisional soak r2 (rb-3-2-toss-timeout-provisional @ a8bda94)

**Measurements only. Nothing here is ACCEPTED.** Provisional branch, provisional banded scoring (`provisional=True` in the report basis).

Provenance: commit a8bda94; roster ref 81f92e3 (Garvian Guardians = A, Ala Apex = B); scoring banded; config native-rb/3; step cap 200,000 per match; 2 matches concurrently on 2 cores. Runner path: native/run.py::run_match via the rb31_soak.job path (reproduces the KNOWN REFERENCE hashes for real seed 3). Runner `tools/soak_driver2.py`; aggregation `tools/soak_table.py`, `tools/soak_analyze.py`.

## Determinism gate (real roster, seed 3) vs KNOWN REFERENCE

| run | status | score | steps | trace_hash | state_hash |
|---|---|---|---|---|---|
| this run (real-seed03) | final | 99-63 | 54508 | `e0d55c70d04f3a40500a96b7bdc34f342faabf6d48d995cf3794419fd45c730b` | `6113fb266d68aed1e25b503de916342663a983717da8b806ae25ed8f957e3875` |
| KNOWN REFERENCE | passed | 99-63 | — | `e0d55c70d04f3a40500a96b7bdc34f342faabf6d48d995cf3794419fd45c730b` | `6113fb266d68aed1e25b503de916342663a983717da8b806ae25ed8f957e3875` |

Result: **match**. Runtime 125.41 s here vs 179 s in the reference (machine timing only; hashes are the check).

## Block A: real roster (seeds 1-10)

| seed | status | score A-B | possessions A / B | share ending in attempt A / B | goal pts (play) A / B | foul-award pts A / B | carry attempts A / B | carry goals A / B | groundings | restart timeouts | legal-arrow rate A / B | DQs A / B | runtime_s | trace_hash | state_hash |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | final | 92-143 | 324 / 325 | 1.5% / 3.7% | 5 / 12 | 87 / 131 | 18 / 25 | 0 / 0 | 140 | 79 | 43.8% / 34.4% | 19 / 17 | 122.45 | `c9e5efc1008a187e…` | `6ccc1d4a1601a13e…` |
| 2 | final | 99-38 | 336 / 336 | 2.7% / 4.5% | 0 / 11 | 99 / 27 | 23 / 25 | 0 / 0 | 194 | 53 | 52.9% / 27.3% | 9 / 16 | 144.16 | `4bf9155185d5cc8f…` | `2f34b6b9e98e4838…` |
| 3 | final | 99-63 | 317 / 317 | 3.2% / 3.8% | 14 / 8 | 85 / 55 | 22 / 27 | 0 / 0 | 145 | 54 | 61.9% / 37.8% | 14 / 15 | 125.41 | `e0d55c70d04f3a40…` | `6113fb266d68aed1…` |
| 4 | final | 103-147 | 350 / 350 | 3.7% / 5.1% | 6 / 20 | 97 / 127 | 22 / 33 | 0 / 0 | 155 | 66 | 39.1% / 45.1% | 20 / 14 | 112.63 | `c169ef4f7861e832…` | `d00b4960916e8b1e…` |
| 5 | final | 105-33 | 310 / 311 | 2.9% / 4.5% | 10 / 19 | 95 / 14 | 22 / 25 | 0 / 0 | 171 | 60 | 44.0% / 45.6% | 2 / 19 | 129.24 | `eba646be9ea3486a…` | `5a5b3b2fc5718e50…` |
| 6 | final | 101-104 | 329 / 328 | 4.0% / 4.0% | 3 / 6 | 98 / 98 | 26 / 28 | 0 / 0 | 120 | 74 | 54.7% / 37.0% | 19 / 19 | 122.49 | `1126db0b725c7251…` | `7992785b46ba525a…` |
| 7 | final | 97-94 | 314 / 317 | 5.1% / 4.7% | 13 / 5 | 84 / 89 | 31 / 32 | 0 / 0 | 182 | 63 | 38.4% / 40.4% | 17 / 17 | 128.85 | `c29f42f2e1f68e53…` | `9142b30f707d0c22…` |
| 8 | final | 93-121 | 338 / 340 | 5.3% / 2.1% | 18 / 7 | 75 / 114 | 35 / 46 | 0 / 0 | 161 | 64 | 37.3% / 54.7% | 19 / 16 | 118.63 | `6186bdd817933607…` | `8003730fcabf7ee6…` |
| 9 | final | 91-79 | 328 / 330 | 3.7% / 3.0% | 4 / 5 | 87 / 74 | 45 / 19 | 0 / 0 | 183 | 45 | 52.9% / 39.2% | 17 / 17 | 116.2 | `0e7207fd1e75f474…` | `f8870e1911e2ea34…` |
| 10 | final | 68-71 | 403 / 405 | 2.2% / 1.7% | 3 / 9 | 65 / 62 | 26 / 28 | 0 / 0 | 135 | 284 | 54.2% / 13.8% | 21 / 13 | 131.75 | `c60e08a72f830a59…` | `85bfef8cfe2f8d31…` |

Seed 3 is the determinism gate: its hashes match the KNOWN REFERENCE exactly (trace e0d55c70…, state 6113fb26…).

## Block B: control, uniform athletes (rating 0.70, height 2.39 m, mass 226 kg, reach 3.05 m), seeds 1-10

**All 10 seeds are NON-FINISHING** (hit the 200,000-step cap). Table of stall facts:

| seed | status | steps | simulated ms | live ms | phase at cap | score | possessions | restarts | foul/DQ | last restart kind & spot | runtime_s | trace_hash | state_hash |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **NON-FINISHING** | 200000 | 23038789 | 18772989 | Phase.OPENING | 0-0 | 0 / 0 | 0 | none | none recorded | 432.27 | `95b9010dd0394d25…` | `698fbb8119b75c55…` |
| 2 | **NON-FINISHING** | 200000 | 23038789 | 18772989 | Phase.OPENING | 0-0 | 0 / 0 | 0 | none | none recorded | 434.46 | `95b9010dd0394d25…` | `698fbb8119b75c55…` |
| 3 | **NON-FINISHING** | 200000 | 23038789 | 18772989 | Phase.OPENING | 0-0 | 0 / 0 | 0 | none | none recorded | 432.92 | `95b9010dd0394d25…` | `698fbb8119b75c55…` |
| 4 | **NON-FINISHING** | 200000 | 23038789 | 18772989 | Phase.OPENING | 0-0 | 0 / 0 | 0 | none | none recorded | 431.75 | `95b9010dd0394d25…` | `698fbb8119b75c55…` |
| 5 | **NON-FINISHING** | 200000 | 23038789 | 18772989 | Phase.OPENING | 0-0 | 0 / 0 | 0 | none | none recorded | 429.96 | `95b9010dd0394d25…` | `698fbb8119b75c55…` |
| 6 | **NON-FINISHING** | 200000 | 23038789 | 18772989 | Phase.OPENING | 0-0 | 0 / 0 | 0 | none | none recorded | 430.59 | `95b9010dd0394d25…` | `698fbb8119b75c55…` |
| 7 | **NON-FINISHING** | 200000 | 23038789 | 18772989 | Phase.OPENING | 0-0 | 0 / 0 | 0 | none | none recorded | 428.66 | `95b9010dd0394d25…` | `698fbb8119b75c55…` |
| 8 | **NON-FINISHING** | 200000 | 23038789 | 18772989 | Phase.OPENING | 0-0 | 0 / 0 | 0 | none | none recorded | 438.22 | `95b9010dd0394d25…` | `698fbb8119b75c55…` |
| 9 | **NON-FINISHING** | 200000 | 23038789 | 18772989 | Phase.OPENING | 0-0 | 0 / 0 | 0 | none | none recorded | 456.45 | `95b9010dd0394d25…` | `698fbb8119b75c55…` |
| 10 | **NON-FINISHING** | 200000 | 23038789 | 18772989 | Phase.OPENING | 0-0 | 0 / 0 | 0 | none | none recorded | 457.52 | `95b9010dd0394d25…` | `698fbb8119b75c55…` |

The seeds share one trace_hash and one state_hash, so the seed had no observable effect in this block. Event log (seed 1): 58 period_end events; ~12,300 each of hunt_start, hunt_claim, simultaneous_contact, joint_control, hunt_retake, rb_hunt_release; no possession, restart, foul, arrow, or goal events. Stall cause not determined here.

## Extended: goal points, live play vs within one possession of a restart (real roster)

"Restart-linked" = goal scored by the team that received the most recent restart, before any possession change to the other team. Everything else = live play.

| seed | A live | A restart-linked | B live | B restart-linked |
|---|---|---|---|---|
| 1 | 0 | 5 | 6 | 6 |
| 2 | 0 | 0 | 11 | 0 |
| 3 | 11 | 3 | 2 | 6 |
| 4 | 4 | 2 | 14 | 6 |
| 5 | 6 | 4 | 17 | 2 |
| 6 | 3 | 0 | 6 | 0 |
| 7 | 10 | 3 | 5 | 0 |
| 8 | 14 | 4 | 5 | 2 |
| 9 | 4 | 0 | 0 | 5 |
| 10 | 0 | 3 | 2 | 7 |

## Extended: fouls by rule and offender role (real roster, all seeds summed)

| rule (reason) | offender role | team | count |
|---|---|---|---|
| archery_target | archer | A | 100 |
| archery_target | archer | B | 100 |
| archery_target | field | A | 391 |
| archery_target | field | B | 506 |
| archery_target | keeper | A | 23 |
| archery_target | keeper | B | 5 |
| frozen_contact | field | A | 124 |
| frozen_contact | field | B | 82 |
| frozen_contact | keeper | A | 7 |
| frozen_contact | keeper | B | 6 |
| illegal_release | field | A | 12 |
| illegal_release | field | B | 23 |
| immune_contact | field | A | 14 |
| immune_contact | field | B | 3 |
| protected_keeper | field | B | 1 |
| zone_unmarked | field | A | 114 |
| zone_unmarked | field | B | 108 |
| zone_unmarked | keeper | A | 2 |

## Extended: DQs by offence class and offender role (real roster, all seeds summed)

| offence class (kind_of_foul) | offender role | team | DQs |
|---|---|---|---|
| major | field | A | 36 |
| major | field | B | 20 |
| major | keeper | A | 1 |
| major | keeper | B | 2 |
| minor | archer | A | 20 |
| minor | archer | B | 20 |
| minor | field | A | 95 |
| minor | field | B | 120 |
| minor | keeper | A | 5 |
| minor | keeper | B | 1 |

## Extended: foul awards by method and team (real roster, all seeds summed)

| method | points | team | awards |
|---|---|---|---|
| full_goal_award | 3 | A | 123 |
| full_goal_award | 3 | B | 127 |
| half_goal | 1 | A | 503 |
| half_goal | 1 | B | 410 |

## Extended: arrows per Archer (real roster, all seeds summed; Archer-role players only)

Legal release = `arrow_release` event by that player. Illegal target = `foul` with reason `archery_target` and that player as actor. Hit and miss are not recorded (see missing fields).

| Archer (player id) | team | legal releases | illegal target | miss |
|---|---|---|---|---|
| A:DRAFT26-09 | A | 34 | 50 | not recorded |
| A:NBL25-D32 | A | 33 | 50 | not recorded |
| B:NBL24-01-12 | B | 34 | 50 | not recorded |
| B:UFA26-BB-04 | B | 27 | 50 | not recorded |

Legal releases by shooter role, all seeds: {'archer': 128, 'field': 706, 'keeper': 32}. Most legal releases are by field players, not Archers.

## Missing fields (not in the existing report; not guessed)

- **Carry attempts by outcome** (tackled / grounded / turnover / stopped short): not recorded. Only counts and timestamps exist.
- **Foul award to originating rule**: foul_award rows carry method and points, not the foul that caused them.
- **DQ to rule**: discipline calls carry kind_of_foul and dq, not the reason.
- **Arrow miss and hit**: not recorded as outcomes. arrow_geometry_impact exists but is not classified.
- **Stall cause in control block**: not determined.


## Files

- `real/`, `control/`: per-seed summary JSON (`*-seedNN.json`) and raw engine logs (`raw-*.json`, gzipped before commit; gunzip before running `tools/soak_analyze.py`).
- `summary.json`, `extended.json`: aggregated data. `tools/`: runner (`soak_driver2.py`) and aggregation scripts.
