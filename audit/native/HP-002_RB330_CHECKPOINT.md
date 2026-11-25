# OWNER BRIEFING

1. **DESIGN COMPLETE, IMPLEMENTED, TESTED.** RB-3.30 adds planned rest waves and completes the 30-game matchup schedule. The box scores now show names and count committed carrier engagements.
2. The coach plan gave the ten scheduled starters **31.86 regulation minutes** on average. Teams averaged **2.60 energy-override exits** at the 0.52 rate scale.
3. The ten-starter plan covers the requested 30 games. The owner still has a lineup decision for the eleventh field-role player.
4. All implementation and replay gates passed on the measured workloads.
5. Review the committed soak and named box scores before selecting a rotation policy.

## Standing gates

 a) pytest -q b1 native, full suite, after the last change.

 b) Legacy hash guards unchanged (six rows).

 c) Determinism.

 d) Compatibility: real seed 1 = 57-76, trace 44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072, state 046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d.

 e) CORE identity (fatigue off): neutral-real seed 1 = 61-80, trace c1a578db3f2754d3f69b47ba81a1f9d5b9336e1d87f496de2fa8dc3daee7a256, state c517e00f864f1438705cdd1d9768d61523ee1aaac69746f57a2e9f1f4adf2745.

 f) RB-3.28 identity (fatigue ON, threshold-only rotation at RB-3.28 rates): ratings 0.4, Garvian Guardians vs Ala Apex seed 1 = 85-86, trace a399f74f81d891c8a0cd4014fc5d10bc5623ad835c448932a94cd50ffac7ac4b, state bc4898a8229d147bd60defdc623db55fac13a3845fb5f29f812198b4bf5f61d4. (Box-score changes must not alter play.)

 g) Speed: planned rotation adds at most 3% per step.

## Revisions and scope

- Branch `codex/rb-3-30-planned-rotation` from `b33217a6393e3c0db7f6ba1318476c23038ae1a3`.
- Box-score observer and display metadata in `2dd4cf2`, real neutral-roster display propagation in `7d01b60`, planned mode and reproduction tools in `3f4378bc4f9defb34cbce6faf56d6a62b6127c6e`.
- Ratings 0.4, explicit skills, individuation on, hand-set values. The workbook and reproduction commands are pinned in the [reproduction guide](rb330/README.md).

| Task | Status |
|---|---|
| 1. Box-score fixes | DESIGN COMPLETE, IMPLEMENTED, TESTED. Named rows and committed-engagement credit. |
| 2. Planned rotation | DESIGN COMPLETE, IMPLEMENTED, TESTED. Dead-ball scenario tests and real-roster calibration. |
| 3. Match soak | DESIGN COMPLETE, IMPLEMENTED, TESTED. Thirty games under the selected plan. |

## Planned rotation

The ten OVR-ordered field starters split into two waves, with each position
group's count differing by at most one between the waves. Wave 1 sits in the
last four minutes of periods 1 and 3. Wave 2 sits in the first four of periods
2 and 4. Planned changes use the next dead ball, prior to restart placement.
The plan selects all ten for the final six minutes of each half and overtime.
The 0.60 energy override may still remove a player. An overridden starter can
return in his slot once the plan calls for him and his energy reaches 0.75.

The coach names the backups before kickoff in position, group and OVR order.
Each wave's backups are unique. If a named backup cannot enter, the ordinary
priority selects from the available bench, with named assignments for the same
dead ball reserved for their slots. The Keeper's fatigue substitution requires
36 regulation minutes already played. Archers have no fatigue substitution.
Required injury and exclusion cover uses the existing rulebook.

Sprint drain and bench recovery change from the RB-3.28 rates of 0.0054 and
0.0016 reserve units per second to **0.002808** and **0.000832**. The 0.52
scale applies only in planned mode. Field recovery and the fatigue effect on
performance are unchanged. Two 0.40 pilots logged zero override exits. Two
0.52 pilots logged 2, 2, 0 and 6 across the four team-games, an average of 2.50.

Open owner question in [QUESTIONS.md](../../QUESTIONS.md). The engine admits
eleven field-role players plus a Keeper per side, with the Archer separate.
The scheduled waves cover ten. The eleventh remains active outside the coach's
rest windows and is still subject to the energy override.

## Regression evidence

All six legacy rows matched the pinned trace, state and config hashes. The
maintained suite reported `801 passed, 1 warning, 23 subtests passed in 667.66s
(0:11:07)`. The warning was the pytest dependency's `CallSpec2` deprecation.
Compatibility, CORE and threshold-only R1 reproduced the scores and both
hashes in gates d through f with the updated box-score observer enabled. Their
configuration fingerprints matched the RB-3.29 reference results as well.

Garvian–Ala planned seed 1 finished 82–79 twice in fresh processes. All recorded
match and compact box-score data matched apart from CPU timings.

- Config `117f5525293e5a2a24476697e32278ca4fec2cb761a8e8df299e57e2d19410bc`
- Trace `101d92f751a9b36cfacb8a90957b074faa08fb38ef908e619915f4d470b60b1b`
- State `e5a8a71ad65bbf7d0f92c8d2358e5603ca72b8f5702b8465e1fe32dd5f649338`

The paired benchmark used two 1,500-step repeats per mode and seed, reversing
mode order. Both modes used the observer. Times are process CPU milliseconds
per step. The aggregate increase was **0.89%**, within the 3% gate. Seed 3
was slower by 6.27% in these windows and seed 1 was faster by 4.51%.

| Seed | Threshold-only R1 | Planned |
|---|---:|---:|
| 1 | 4.287 | 4.094 |
| 3 | 4.298 | 4.567 |
| Combined | 4.293 | 4.331 |

## Box-score correction

The observer credits one attempt per physical hold with an explicit consumed
takedown intent. It credits success when the same defender receives the
rulebook takedown on that hold. The broader observed grounding totals remain
available. The Garvian–Ala threshold-only R2 seed-1 replay kept its 40–110
result and exact config, trace and state fingerprints.

| Team | Old attempts | New attempts | Old made | New made | Groundings |
|---|---:|---:|---:|---:|---:|
| Garvian Guardians | 549 | 154 | 39 | 39 | 39 |
| Ala Apex | 878 | 220 | 52 | 50 | 52 |

The `native-box/2` JSON and CSV preserve player ID and team side. Both formats
add the workbook player name, team name and legacy position. The state and
replay fingerprints exclude display metadata. Synthetic rosters without a
workbook record keep the ID display and an empty position.

An independent join of the exported JSON and CSV against the source workbook
matched all 44 player rows by ID, with 22 per franchise. The 712 workbook
player IDs were unique. The archive holds the full named seed-1 box score.

## Planned rotation soak

All 30 matches finished, passed invariants and closed every restart. The
schedule used Garvian–Ala seeds 1–10, Yukïma–Isu’Kari seeds 1–5,
Mbuya Ïmu–Ala seeds 1–5 and the five RB-3.27 league pairings at seeds 1–2.
The matches took 4,916.71 process CPU seconds in total.

| Participation | Mean regulation minutes | Range |
|---|---:|---:|
| Ten scheduled field starters | 31.86 | 28.06–34.46 |
| Original reserve field players | 12.05 | 0.00–24.39 |
| Eleventh active field player | 37.32 | 29.62–40.00 |
| Starting Keepers | 40.00 | 40.00–40.00 |
| Starting Archers | 25.77 | 3.89–40.00 |

All starting Keepers played 40 regulation minutes. The soak recorded zero
elective Archer changes. The starting Archer minutes reflect rulebook
availability, including required cover recorded in the named seed-1 box score.

| Substitutions | Total | Per team per game |
|---|---:|---:|
| Planned exits | 1170 | 19.50 |
| Planned returns | 1172 | 19.53 |
| Energy override exits | 156 | 2.60 |
| Energy override returns | 122 | 2.03 |
| All elective changes | 2620 | 43.67 |

Planned returns include eligible originals restored by the coach plan after
required cover. The energy-override target uses exits. Return counts track
the later restoration and are kept separate.

| Stamina | Override exits |
|---:|---:|
| 0.67 | 3 |
| 0.68 | 13 |
| 0.69 | 1 |
| 0.70 | 20 |
| 0.71 | 3 |
| 0.72 | 20 |
| 0.74 | 6 |
| 0.75 | 12 |
| 0.76 | 25 |
| 0.78 | 8 |
| 0.79 | 25 |
| 0.80 | 1 |
| 0.84 | 9 |
| 0.86 | 3 |
| 0.87 | 7 |

| Match measure | Result |
|---|---:|
| Median team score | 90.5 |
| Mean possessions per team | 151.02 |
| Possessions ending in an attempt | 34.76% |
| Ala minus Garvian mean margin ± SE | +16.80 ± 6.96 |
| Ala wins vs Garvian | 8/10 |
| Games within five points | 10.00% |
| Median absolute margin | 18 |
| Team score SD | 17.36 |
| Points from four-point throws | 45.35% |

Attempt share uses the pooled possession count. The team score SD is the
sample SD across 60 scores. The matchup margin SE uses the ten Garvian–Ala
score differences.

## Evidence

- [Named seed-1 JSON](rb330/evidence/boxes/planned-seed01.json) and [CSV](rb330/evidence/boxes/planned-seed01.csv)
- [Per-match table and fingerprints](rb330/evidence/matches.csv), [aggregate totals](rb330/evidence/summary.json) and [compressed match records](rb330/evidence/runs)
- [Full suite](rb330/evidence/pytest.txt), [legacy hashes](rb330/evidence/legacy.txt), [identity results](rb330/evidence/identities.txt), [repeat](rb330/evidence/repeat.txt) and [timing samples](rb330/evidence/benchmark.json)
