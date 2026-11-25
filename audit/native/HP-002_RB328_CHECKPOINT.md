# OWNER BRIEFING

1. **IMPLEMENTED and TESTED.** RB-3.28 adds an optional energy reserve and dead-ball fatigue rotation. Both modes completed all 20 scheduled games.
2. With the switch on, the engine reduces tired athletes’ physical and technical outputs and rests eligible field players. Rested starters return to their own slots. The match uses the ratings 0.4 workbook and hand-set decision values.
3. Fatigue on averaged 32.35 minutes per field starter, a median team score of 85.5 and 146.5 possessions per team. Score margins and spread remained above the season reference.
4. Promotion warrants review of 135.53 fatigue substitutions per team per game and the results against the season reference.
5. Keep the switch opt-in while reviewing the rotation frequency and score spread against the season reference.

## Revisions and status

- Branch `codex/rb-3-28-fatigue-rotation`
- Lead-verified parent `b91440df56a8b3234d476630e6e949eb2c9f2202`
- Core implementation `3bcc5cf`
- Fixed constants and configuration fingerprints `66dfc2a`
- Calibration pilots and sprint curves `ef17538`
- Ratings 0.4 source `b284e822fa2f23c820987c795a2d780f16334fc3`
- Workbook SHA-256 `47b48af7a19035428d517582370fa1782b542980c783edf3dfb20619cf437fba`
- [Reproduction](rb328/README.md)

| Task | Status |
|---|---|
| 1. Fatigue | DESIGN COMPLETE, IMPLEMENTED, TESTED |
| 2. Rotation | DESIGN COMPLETE, IMPLEMENTED, TESTED |
| 3. Calibration and soak | DESIGN COMPLETE, IMPLEMENTED, TESTED |

## Standing gates

 a) pytest -q b1 native, full suite, after the last change.

 b) Legacy hash guards unchanged (six rows, native/evidence/rb3-reach/legacy-hashes.txt).

 c) Determinism: same code + roster + seed gives identical trace and state hashes.

 d) Compatibility (individuation off, fatigue off): real seed 1 = 57-76, trace 44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072, state 046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d.

 e) CORE identity (fatigue off, learned values off): neutral-real seed 1 = 61-80, trace c1a578db3f2754d3f69b47ba81a1f9d5b9336e1d87f496de2fa8dc3daee7a256, state c517e00f864f1438705cdd1d9768d61523ee1aaac69746f57a2e9f1f4adf2745.

 f) Speed: fatigue and rotation ON may add at most 5% per step on top of CORE.

## Workload and rotation

The default-off switch is `fatigue_rotation`. Off retains the original CORE kernel. On replaces the old kernel writes to its reserve with a live-work and recovery model. Fresh athletes start at 1.0. The live workload uses the greater of achieved speed and the braking-envelope speed for the current movement command, relative to the athlete’s effective maximum speed. A concave workload curve accounts for repeated short movement demands. Stamina adjusts intensity in the middle of the range and preserves the standing and full-sprint endpoints. Its rate modifier speeds recovery and slows drain. Dead time recovers at the standing rate for the field lineup. The bench recovers at the same independent rate for every athlete.

Effective speed and acceleration retain the kernel coefficients `0.70 + 0.30 × reserve` and `0.55 + 0.45 × reserve`. Braking, turning, strength, agility, jumping and maximum throwing speed use `1 − 0.40 × (1 − reserve)`. Technical execution uses `rating × (1 − 0.30 × (1 − reserve) × (1 − rating))`. This reduces poor form by a greater fraction. Under fatigue, release motion still follows the existing admission and timing path. The motor caps release speed at current throwing capacity and updates execution accuracy. The own-body view reflects available movement output. Strategy, perception and decision ratings retain their roster values.

A field athlete crossing 0.60 is marked to leave at the next dead ball. If an eligible reserve is unavailable, the athlete remains eligible for removal at the next dead ball. Rested starters reclaim their original slots first at 0.75. Elective replacements use exact legacy position, position group, then Overall rank, in that order. Overall and legacy position stay in roster selection metadata. A Keeper can rotate from fatigue once his regulation participation reaches 36 minutes. Archers receive no elective fatigue substitutions. Existing disciplinary and injury-cover rules remain in force. Playing time is measured on the regulation clock, and required and elective substitutions have separate event records.

## Named constants and controlled scenarios

| Parameter | Value |
|---|---:|
| `bench_recovery` | 0.0016 |
| `effort_exponent` | 0.3 |
| `field_recovery` | 0.00035 |
| `keeper_regulation_min_ms` | 2160000 |
| `neutral_effort` | 0.5 |
| `output_update_ms` | 500 |
| `physical_loss` | 0.4 |
| `rest_threshold` | 0.6 |
| `return_threshold` | 0.75 |
| `sprint_drain` | 0.0054 |
| `stamina_rate_range` | 0.65 |
| `stamina_sensitivity` | 0.3 |
| `technique_loss` | 0.3 |

Rates are reserve units per simulated second. The fatigue switch records these parameters in the effective match configuration.

| Held sprint Stamina | Reserve at 0 s | 30 s | 60 s | 90 s | Seconds to 0.60 |
|---:|---:|---:|---:|---:|---:|
| 0.60 | 1.000 | 0.827 | 0.653 | 0.480 | 69.26 |
| 0.70 | 1.000 | 0.838 | 0.676 | 0.514 | 74.07 |
| 0.85 | 1.000 | 0.852 | 0.705 | 0.557 | 81.30 |
| 1.00 | 1.000 | 0.864 | 0.729 | 0.593 | 88.52 |

From 0.60, a standing 0.70-Stamina athlete has 0.621 after 60 seconds and 0.642 after 120 seconds. A standing 1.00-Stamina athlete has 0.650 after 120 seconds. The bench reaches 0.696 at 60 seconds, the return threshold after 93.75 seconds, and 0.792 at 120 seconds for every Stamina rating. At reserve 0.60, technique 0.50 falls to 0.4700 and technique 0.95 falls to 0.9443. The focused suite passed five tests.

## Calibration trials

| Garvian–Ala seed 1 | Effort exponent | Sprint drain | Bench recovery | Mean field starter minutes |
|---|---:|---:|---:|---:|
| First workload curve | 1.00 | 0.0040 | 0.0030 | 39.90 |
| Concave workload | 0.40 | 0.0040 | 0.0020 | 39.30 |
| Stronger workload and longer bench rest | 0.24 | 0.0060 | 0.0016 | 28.42 |
| Reduced drain and workload | 0.28 | 0.0055 | 0.0016 | 30.86 |
| Locked for soak | 0.30 | 0.0054 | 0.0016 | See the soak |

The first two pilots predate the final motor and body-view integration. The last two pilots used the final implementation before the effective-configuration fingerprint was added. The paired soak uses one fixed set of fatigue constants. Prior pilots are available as raw records under `rb328/evidence/`.

## Timing

| Mode | Seed 1 CPU ms/step | Seed 3 CPU ms/step | Median CPU ms/step |
|---|---:|---:|---:|
| Fatigue off | 4.358 | 4.501 | 4.430 |
| Fatigue on | 4.309 | 3.989 | 4.149 |

The paired 1,500-step windows passed gate f. Fatigue on was -6.34% in net CPU time per step, including the work from different match trajectories.

## Full suite and match guards

The final maintained suite reported `772 passed, 1 warning, 23 subtests passed in 626.58s (0:10:26)`. The warning was a pytest dependency deprecation. All six legacy trace, state and config rows matched. All twenty fatigue-off regulation runs also reproduced the RB-3.27 scores and configuration, trace and state hashes exactly.

Gates d and e reproduced 57–76 and 61–80 with the exact trace and state hashes above. The fresh-process fatigue-on repeat reproduced Garvian–Ala seed 1 **85–86** in **32,761 steps**, including configuration, trace and state.

- Config `3af62b414b132cad51d1547dd1abb6bc735fef5a147d41aafebc3475b414df5e`
- Trace `a399f74f81d891c8a0cd4014fc5d10bc5623ad835c448932a94cd50ffac7ac4b`
- State `bc4898a8229d147bd60defdc623db55fac13a3845fb5f29f812198b4bf5f61d4`

The independent checker verified the 40 soak results, the logged minimum incoming reserve, Archer prohibition and Keeper playing-time floor, the two identity runs and the full fatigue-on repeat. The forced Keeper case verifies the 36-minute threshold before a substitution is admitted.

## Ratings 0.4 paired soak

Garvian Guardians (A) and Ala Apex (B) played seeds 1–10. The other five RB-3.27 pairings played seeds 1 and 2. The same inputs and hand-set values were used in both modes. All 40 games finished with every restart resolved. No competition rule or hand-set decision value was tuned.

| Measure | Fatigue off | Fatigue on | Owner reference |
|---|---:|---:|---:|
| Field starter regulation minutes, mean | 39.96 | 32.35 | About 32 |
| Field starter minute range | 27.52–40.00 | 25.85–37.95 | |
| Field bench regulation minutes, mean | 0.17 | 12.10 | |
| Keeper starter / reserve minutes, mean | 40.00 / 0.00 | 40.00 / 0.00 | 36 minimum for fatigue removal |
| Archer starter / reserve minutes, mean | 23.55 / 12.89 | 22.04 / 14.99 | No fatigue rotation |
| All substitutions per team per game | 2.35 | 137.60 | |
| Fatigue substitutions per team per game | 0.00 | 135.53 | |
| Median team score | 89.5 | 85.5 | 75–90 |
| Mean / median possessions per team | 153.15 / 152 | 146.50 / 147 | 100–150 |
| Possessions ending in an attempt | 35.41% | 35.08% | |
| Ala minus Garvian, mean margin ± SE | +27.0 ± 6.14 | +37.3 ± 7.22 | |
| Ala wins, ten primary games | 9 | 10 | |
| Median absolute game margin | 29.5 | 23.0 | 13 |
| Games decided by five or fewer | 10% | 10% | 23% |
| Team score sample SD | 20.11 | 20.87 | 12.7 |

The Keeper fatigue rule was verified in the forced dead-ball scenario. No Keeper fatigue substitution was needed during the soak. The Archer time split reflects existing required substitutions and exclusion time. All Archer fatigue substitution counts were zero. Platform play uses standing recovery under the locomotion workload model.

| Fatigue substitution priority | Count across 20 fatigue-on matches | Per team per game |
|---|---:|---:|
| Exact legacy position | 1,166 | 29.15 |
| Position group | 1,103 | 27.58 |
| Overall fallback | 515 | 12.88 |
| Starter returns to original slot | 2,637 | 65.93 |
| Total | 5,421 | 135.53 |

The existing admission rules produced 94 required substitutions in the off block (91 Archer and three field) and 83 in the on block (81 Archer and two field). Match setup admissions are excluded from the substitution counts.

The twenty fatigue-off games took 3,060.3 process CPU seconds.

The twenty fatigue-on games took 3,112.8 process CPU seconds.

[Per-match CSV](rb328/evidence/matches.csv) · [Numeric summary](rb328/evidence/summary.json) · [Raw match and calibration evidence](rb328/evidence)

## Open questions

No canon ruling was required. The measured swap frequency and wider margins and score spread than the season reference remain review items.
