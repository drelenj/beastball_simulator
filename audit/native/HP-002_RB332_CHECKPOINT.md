# OWNER BRIEFING

1. **DESIGN COMPLETE, IMPLEMENTED, TESTED** for pass clearance, carry finish, fresh takedown evidence and boundary braking. The Keeper reach check is read-only.
2. The simulator can run each fix separately or together. The comparison uses the same **18 games in each of the six arms** at fatigue scale 0.58.
3. The historical clearance audit covers 582 of 1,020 believed-clear interceptions. Score, possession and margin results are descriptive and **not judged on this sample**.
4. The two matches already in progress finished. The schedulers launched no further matches. The full suite, legacy hashes, identities and repeated combined run passed.
5. Use the paired event results to review each fix and the combined arm. Keep adoption decisions separate from the descriptive scoring results.

## Standing gates

 a) pytest -q b1 native, full suite, after the last change.

 b) Legacy hash guards unchanged (six rows).

 c) Determinism.

 d) Compatibility: real seed 1 = 57-76, trace 44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072, state 046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d.

 e) CORE identity (fatigue off): neutral-real seed 1 = 61-80, trace c1a578db3f2754d3f69b47ba81a1f9d5b9336e1d87f496de2fa8dc3daee7a256, state c517e00f864f1438705cdd1d9768d61523ee1aaac69746f57a2e9f1f4adf2745.

 f) RB-3.28 identity (fatigue ON, threshold-only): ratings 0.4, Garvian vs Ala seed 1 = 85-86, trace a399f74f81d891c8a0cd4014fc5d10bc5623ad835c448932a94cd50ffac7ac4b, state bc4898a8229d147bd60defdc623db55fac13a3845fb5f29f812198b4bf5f61d4.

 g) RB-3.31 planned identity (all fixes OFF): Garvian vs Ala seed 1 = 64-96, trace ab86f8befcf2baca264ab87fabdd39af3e218cb80032eab52b356a089319a08a, state e8318c85ba3ae5205861d138f8d4f63e16202dd6d84f4ab8b5df02066e141047.

 h) Speed: all fixes ON at most 5% per step slower than RB-3.31 planned mode.

## Method and revisions

- Branch `codex/rb-3-32-paired-fixes`, parent `aef46501ffbcbc4a6aea27feb351117c0002e649`
- Opt-in policy, tests and measurement runner `f07940e`
- Refined Keeper commitment check `9dabd54` and historical view audit
  `415742e`. Pre-adjudication boundary witness `6b0e3c9`.
- Separate boundary-braking switch `4dcaae6`. It joined the combined arm
  after the OFF witness showed end-line drift with the ball still held.
- Ratings 0.4, explicit technical ratings, OVR 0.422 selection, eleven planned
  starters, individuation on, and hand-set values. No rule change.
- Calibrated `0.58` in two pilot games. Garvian–Ala seed 1 recorded 1 and 6
  override exits. Mbuya Ïmu–Ala seed 1 recorded 3 and 3. Average 3.25 per team.
  Every experimental arm, including OFF, uses 0.58. The separate historical
  identity and clearance replays use 0.52. Trial results at the two scales are
  distinct populations.
- The schedule has Garvian–Ala seeds 1–10, Yukïma–Isu’Kari seeds 1–5,
  Mbuya Ïmu–Ala seeds 1–5, and the five league pairings at seeds 1–2.
- The paired standard error resamples matchup/seed blocks together, retaining
  each stratum's game count. It applies to the same estimator on both arms
  for both weighted rates and nonlinear statistics. See the [reproduction guide](rb332/README.md).

## Status and verification

| Work | Status |
|---|---|
| Fatigue calibration | DESIGN COMPLETE, IMPLEMENTED, TESTED in two pilots at scale 0.58. |
| Pass clearance | DESIGN COMPLETE, IMPLEMENTED, TESTED on 18 paired games. Historical coverage below. |
| Carry finish | DESIGN COMPLETE, IMPLEMENTED, TESTED on 18 paired games. |
| Fresh takedown evidence | DESIGN COMPLETE, IMPLEMENTED, TESTED on 18 paired games. |
| Boundary diagnosis and guard | DESIGN COMPLETE, IMPLEMENTED, TESTED on 18 paired games. |
| Keeper reach diagnosis | DESIGN COMPLETE, IMPLEMENTED, TESTED as a read-only audit of 18 OFF games. |
| Combined policy | DESIGN COMPLETE, IMPLEMENTED, TESTED on 18 paired games and a repeated seed-1 run. |

`pytest -q b1 native` reported `811 passed, 1 warning, 23 subtests passed in 646.88s (0:10:46)`.
All six legacy rows matched. The full suite ran after the final runtime change. The final cohort aggregation was checked offline after the run stop.

The paired production benchmark used four 1,500-step windows from the same
seeds and fatigue scale. The OFF mode used 4.133 process CPU ms/step
and combined used 4.116, a change of -0.41%.

- compatibility 57–76, exact trace `44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072` and state `046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d`.
- core 61–80, exact trace `c1a578db3f2754d3f69b47ba81a1f9d5b9336e1d87f496de2fa8dc3daee7a256` and state `c517e00f864f1438705cdd1d9768d61523ee1aaac69746f57a2e9f1f4adf2745`.
- R1 85–86, exact trace `a399f74f81d891c8a0cd4014fc5d10bc5623ad835c448932a94cd50ffac7ac4b` and state `bc4898a8229d147bd60defdc623db55fac13a3845fb5f29f812198b4bf5f61d4`.
- PLANNED 64–96, exact trace `ab86f8befcf2baca264ab87fabdd39af3e218cb80032eab52b356a089319a08a` and state `e8318c85ba3ae5205861d138f8d4f63e16202dd6d84f4ab8b5df02066e141047`.
- Combined repeat 99–74, trace `0045e62d5de38fc85a6c38fd58298284f637bb6d1766ddb7d50cfb159ac22601` and state `b2b6857584bbdc7c486b54f52bd8ebf9c2c89fde8e15893a42c70f5c3be9d9de`.

## Historical pass clearance

The forecast flagged **357 of 582**
measured cases from **582** of the original 1,020
believed-clear interceptions. Classification is evaluated on the admitted
decision view and selected delivery, with the historical population keyed to
the unchanged RB-3.31 trace. A flag means a negative forecast clearance. The audit does not measure whether those historical interceptions would have been prevented.

The replays covered 18 games in the common cohort. The other 438 historical interceptions are outside this audit.

## Common cohort

| Matchup | Included seeds |
|---|---|
| Garvian Guardians vs Ala Apex | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 |
| Yukïma Cowhands vs Isu’Kari Sirenwings | 1, 2, 3, 4, 5 |
| Mbuya Ïmu Moonhawks vs Ala Apex | 1, 2, 3 |

The analysis includes 108 trial games. The additional
OFF match, Mbuya Ïmu Moonhawks vs Ala Apex seed 4, finished and is preserved
as raw evidence. It has no matching ON record and is excluded from the
paired tables and the OFF-only boundary and Keeper audits. No league-sample
game entered the common cohort.

## Paired changes

Event counts are per team per game. Rates pool the underlying counts within
an arm. Paired changes are ON minus OFF. Standard errors use 1,000 paired
game-level bootstrap draws stratified by matchup. Percentage-point differences
are marked pp. An undefined rate is shown as an em dash. Turnover types retain
the possession ledger’s labels, including score restarts. Near-goal carry
outcomes count held-ball segments begun within 20 m of goal. The carry-goal
row also includes successful releases inside 3 m. Tackle episode success
uses all admitted commitment episodes, including no contact. Hold success
uses the narrower box-score denominator of committed driving holds. Stretch
starts, ends and goals are event counts, which can overlap.

### Pass Clearance

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| turnovers per team | 149.72 | 137.42 | -12.31 | 1.75 |
| near goal carries per team | 55.06 | 53.22 | -1.83 | 1.75 |
| pass completion | 76.62% | 80.27% | +3.65 pp | 0.43 pp |
| passes attempted per team | 282.81 | 258.25 | -24.56 | 3.21 |
| interceptions per team | 53.17 | 41.53 | -11.64 | 1.03 |
| boundaries per team | 31.39 | 30.75 | -0.64 | 0.95 |
| carry goals per team | 0.42 | 0.61 | +0.19 | 0.20 |
| tackle commits per team | 348.94 | 357.39 | +8.44 | 7.63 |
| tackle wrong target share | 39.47% | 37.63% | -1.84 pp | 0.91 pp |
| tackle episode success | 10.02% | 11.13% | +1.11 pp | 0.32 pp |
| tackle hold success | 22.44% | 24.06% | +1.63 pp | 0.68 pp |
| keeper save rate | 14.54% | 13.11% | -1.43 pp | 1.25 pp |
| keeper save on target rate | 19.48% | 17.97% | -1.51 pp | 1.58 pp |
| planned changes per team | 40.72 | 42.11 | +1.39 | 0.34 |
| override exits per team | 3.47 | 2.72 | -0.75 | 0.19 |
| turnovers.fumble | 11.69 | 12.89 | +1.19 | 0.86 |
| turnovers.held ball | 0.00 | 0.00 | +0.00 | 0.00 |
| turnovers.interception | 53.17 | 41.53 | -11.64 | 1.03 |
| turnovers.major | 0.03 | 0.00 | -0.03 | 0.03 |
| turnovers.opponent control | 11.92 | 10.97 | -0.94 | 0.60 |
| turnovers.out of bounds | 31.39 | 30.75 | -0.64 | 0.95 |
| turnovers.play clock | 1.67 | 1.81 | +0.14 | 0.24 |
| turnovers.score restart | 25.08 | 23.53 | -1.56 | 0.79 |
| turnovers.strip | 1.47 | 1.47 | +0.00 | 0.28 |
| turnovers.tackle | 9.81 | 11.08 | +1.28 | 0.75 |
| turnovers.toss timeout | 0.42 | 0.56 | +0.14 | 0.17 |
| turnovers.turnover | 0.50 | 0.39 | -0.11 | 0.13 |
| turnovers.zone violation | 2.58 | 2.44 | -0.14 | 0.36 |
| carries.freeze | 0.08 | 0.17 | +0.08 | 0.08 |
| carries.goal | 0.42 | 0.61 | +0.19 | 0.20 |
| carries.handoff | 2.61 | 1.72 | -0.89 | 0.27 |
| carries.out of bounds | 12.33 | 12.17 | -0.17 | 0.65 |
| carries.pass | 2.94 | 3.39 | +0.44 | 0.32 |
| carries.shot | 26.36 | 25.17 | -1.19 | 1.17 |
| carries.stopped short | 5.50 | 5.31 | -0.19 | 0.54 |
| carries.strip | 0.58 | 0.36 | -0.22 | 0.18 |
| carries.tackle | 3.69 | 4.00 | +0.31 | 0.51 |
| carries.zone violation | 0.53 | 0.33 | -0.19 | 0.14 |
| stretches.end.lost control or expired | 0.00 | 0.03 | +0.03 | 0.03 |
| stretches.end.replaced | 0.00 | 0.03 | +0.03 | 0.03 |
| stretches.stretch end | 0.00 | 0.06 | +0.06 | 0.05 |
| stretches.stretch goal | 0.00 | 0.03 | +0.03 | 0.03 |
| stretches.stretch start | 0.00 | 0.06 | +0.06 | 0.05 |

### Carry Finish

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| turnovers per team | 149.72 | 150.14 | +0.42 | 1.67 |
| near goal carries per team | 55.06 | 54.67 | -0.39 | 1.27 |
| pass completion | 76.62% | 76.93% | +0.31 pp | 0.30 pp |
| passes attempted per team | 282.81 | 281.25 | -1.56 | 3.06 |
| interceptions per team | 53.17 | 51.97 | -1.19 | 1.09 |
| boundaries per team | 31.39 | 29.42 | -1.97 | 1.17 |
| carry goals per team | 0.42 | 2.69 | +2.28 | 0.20 |
| tackle commits per team | 348.94 | 337.00 | -11.94 | 5.47 |
| tackle wrong target share | 39.47% | 39.61% | +0.15 pp | 0.89 pp |
| tackle episode success | 10.02% | 10.13% | +0.11 pp | 0.31 pp |
| tackle hold success | 22.44% | 22.79% | +0.35 pp | 0.55 pp |
| keeper save rate | 14.54% | 14.69% | +0.15 pp | 1.02 pp |
| keeper save on target rate | 19.48% | 20.30% | +0.82 pp | 1.31 pp |
| planned changes per team | 40.72 | 41.67 | +0.94 | 0.43 |
| override exits per team | 3.47 | 3.00 | -0.47 | 0.20 |
| turnovers.fumble | 11.69 | 12.06 | +0.36 | 0.69 |
| turnovers.held ball | 0.00 | 0.00 | +0.00 | 0.00 |
| turnovers.interception | 53.17 | 51.97 | -1.19 | 1.09 |
| turnovers.major | 0.03 | 0.03 | +0.00 | 0.04 |
| turnovers.opponent control | 11.92 | 13.14 | +1.22 | 0.46 |
| turnovers.out of bounds | 31.39 | 29.42 | -1.97 | 1.17 |
| turnovers.play clock | 1.67 | 1.58 | -0.08 | 0.22 |
| turnovers.score restart | 25.08 | 28.86 | +3.78 | 0.86 |
| turnovers.strip | 1.47 | 1.08 | -0.39 | 0.19 |
| turnovers.tackle | 9.81 | 8.92 | -0.89 | 0.62 |
| turnovers.toss timeout | 0.42 | 0.53 | +0.11 | 0.11 |
| turnovers.turnover | 0.50 | 0.58 | +0.08 | 0.17 |
| turnovers.zone violation | 2.58 | 1.97 | -0.61 | 0.35 |
| carries.freeze | 0.08 | 0.11 | +0.03 | 0.07 |
| carries.goal | 0.42 | 2.69 | +2.28 | 0.20 |
| carries.handoff | 2.61 | 1.08 | -1.53 | 0.38 |
| carries.out of bounds | 12.33 | 7.67 | -4.67 | 0.62 |
| carries.pass | 2.94 | 1.75 | -1.19 | 0.28 |
| carries.shot | 26.36 | 33.61 | +7.25 | 1.20 |
| carries.stopped short | 5.50 | 4.69 | -0.81 | 0.46 |
| carries.strip | 0.58 | 0.36 | -0.22 | 0.15 |
| carries.tackle | 3.69 | 2.39 | -1.31 | 0.40 |
| carries.zone violation | 0.53 | 0.31 | -0.22 | 0.11 |
| stretches.end.lost control or expired | 0.00 | 0.17 | +0.17 | 0.07 |
| stretches.end.replaced | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch end | 0.00 | 0.17 | +0.17 | 0.07 |
| stretches.stretch goal | 0.00 | 0.17 | +0.17 | 0.07 |
| stretches.stretch start | 0.00 | 0.17 | +0.17 | 0.07 |

### Fresh Takedown

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| turnovers per team | 149.72 | 149.11 | -0.61 | 1.90 |
| near goal carries per team | 55.06 | 49.36 | -5.69 | 1.68 |
| pass completion | 76.62% | 76.33% | -0.29 pp | 0.42 pp |
| passes attempted per team | 282.81 | 277.94 | -4.86 | 2.34 |
| interceptions per team | 53.17 | 52.19 | -0.97 | 1.39 |
| boundaries per team | 31.39 | 30.58 | -0.81 | 1.18 |
| carry goals per team | 0.42 | 0.44 | +0.03 | 0.11 |
| tackle commits per team | 348.94 | 295.31 | -53.64 | 7.43 |
| tackle wrong target share | 39.47% | 26.72% | -12.74 pp | 0.67 pp |
| tackle episode success | 10.02% | 10.70% | +0.68 pp | 0.32 pp |
| tackle hold success | 22.44% | 20.67% | -1.77 pp | 0.69 pp |
| keeper save rate | 14.54% | 15.43% | +0.89 pp | 1.30 pp |
| keeper save on target rate | 19.48% | 20.86% | +1.38 pp | 1.63 pp |
| planned changes per team | 40.72 | 41.36 | +0.64 | 0.44 |
| override exits per team | 3.47 | 3.25 | -0.22 | 0.21 |
| turnovers.fumble | 11.69 | 13.92 | +2.22 | 0.66 |
| turnovers.held ball | 0.00 | 0.00 | +0.00 | 0.00 |
| turnovers.interception | 53.17 | 52.19 | -0.97 | 1.39 |
| turnovers.major | 0.03 | 0.00 | -0.03 | 0.03 |
| turnovers.opponent control | 11.92 | 13.25 | +1.33 | 0.54 |
| turnovers.out of bounds | 31.39 | 30.58 | -0.81 | 1.18 |
| turnovers.play clock | 1.67 | 1.11 | -0.56 | 0.26 |
| turnovers.score restart | 25.08 | 24.89 | -0.19 | 0.89 |
| turnovers.strip | 1.47 | 1.14 | -0.33 | 0.20 |
| turnovers.tackle | 9.81 | 8.42 | -1.39 | 0.80 |
| turnovers.toss timeout | 0.42 | 0.36 | -0.06 | 0.10 |
| turnovers.turnover | 0.50 | 0.56 | +0.06 | 0.11 |
| turnovers.zone violation | 2.58 | 2.69 | +0.11 | 0.36 |
| carries.freeze | 0.08 | 0.14 | +0.06 | 0.09 |
| carries.goal | 0.42 | 0.44 | +0.03 | 0.11 |
| carries.handoff | 2.61 | 1.83 | -0.78 | 0.53 |
| carries.out of bounds | 12.33 | 9.50 | -2.83 | 0.48 |
| carries.pass | 2.94 | 3.08 | +0.14 | 0.26 |
| carries.shot | 26.36 | 25.72 | -0.64 | 1.10 |
| carries.stopped short | 5.50 | 4.47 | -1.03 | 0.54 |
| carries.strip | 0.58 | 0.36 | -0.22 | 0.16 |
| carries.tackle | 3.69 | 3.28 | -0.42 | 0.46 |
| carries.zone violation | 0.53 | 0.53 | +0.00 | 0.13 |
| stretches.end.lost control or expired | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.end.replaced | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch end | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch goal | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch start | 0.00 | 0.00 | +0.00 | 0.00 |

### Boundary Guard

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| turnovers per team | 149.72 | 141.53 | -8.19 | 2.34 |
| near goal carries per team | 55.06 | 54.53 | -0.53 | 2.23 |
| pass completion | 76.62% | 77.54% | +0.92 pp | 0.72 pp |
| passes attempted per team | 282.81 | 271.72 | -11.08 | 3.32 |
| interceptions per team | 53.17 | 48.42 | -4.75 | 1.86 |
| boundaries per team | 31.39 | 23.31 | -8.08 | 0.67 |
| carry goals per team | 0.42 | 0.83 | +0.42 | 0.19 |
| tackle commits per team | 348.94 | 340.25 | -8.69 | 6.58 |
| tackle wrong target share | 39.47% | 38.72% | -0.75 pp | 0.77 pp |
| tackle episode success | 10.02% | 10.70% | +0.68 pp | 0.30 pp |
| tackle hold success | 22.44% | 23.83% | +1.39 pp | 0.53 pp |
| keeper save rate | 14.54% | 13.62% | -0.92 pp | 1.27 pp |
| keeper save on target rate | 19.48% | 18.29% | -1.19 pp | 1.61 pp |
| planned changes per team | 40.72 | 41.89 | +1.17 | 0.42 |
| override exits per team | 3.47 | 2.92 | -0.56 | 0.28 |
| turnovers.fumble | 11.69 | 11.97 | +0.28 | 0.61 |
| turnovers.held ball | 0.00 | 0.00 | +0.00 | 0.00 |
| turnovers.interception | 53.17 | 48.42 | -4.75 | 1.86 |
| turnovers.major | 0.03 | 0.03 | +0.00 | 0.04 |
| turnovers.opponent control | 11.92 | 12.39 | +0.47 | 0.85 |
| turnovers.out of bounds | 31.39 | 23.31 | -8.08 | 0.67 |
| turnovers.play clock | 1.67 | 2.00 | +0.33 | 0.24 |
| turnovers.score restart | 25.08 | 28.50 | +3.42 | 1.00 |
| turnovers.strip | 1.47 | 1.58 | +0.11 | 0.18 |
| turnovers.tackle | 9.81 | 9.61 | -0.19 | 0.62 |
| turnovers.toss timeout | 0.42 | 0.28 | -0.14 | 0.09 |
| turnovers.turnover | 0.50 | 0.53 | +0.03 | 0.16 |
| turnovers.zone violation | 2.58 | 2.92 | +0.33 | 0.43 |
| carries.freeze | 0.08 | 0.11 | +0.03 | 0.07 |
| carries.goal | 0.42 | 0.83 | +0.42 | 0.19 |
| carries.handoff | 2.61 | 2.06 | -0.56 | 0.40 |
| carries.out of bounds | 12.33 | 6.31 | -6.03 | 0.42 |
| carries.pass | 2.94 | 3.75 | +0.81 | 0.32 |
| carries.shot | 26.36 | 31.64 | +5.28 | 1.23 |
| carries.stopped short | 5.50 | 4.25 | -1.25 | 0.75 |
| carries.strip | 0.58 | 0.72 | +0.14 | 0.24 |
| carries.tackle | 3.69 | 3.89 | +0.19 | 0.64 |
| carries.zone violation | 0.53 | 0.97 | +0.44 | 0.19 |
| stretches.end.lost control or expired | 0.00 | 0.14 | +0.14 | 0.06 |
| stretches.end.replaced | 0.00 | 0.06 | +0.06 | 0.03 |
| stretches.stretch end | 0.00 | 0.19 | +0.19 | 0.08 |
| stretches.stretch goal | 0.00 | 0.14 | +0.14 | 0.06 |
| stretches.stretch start | 0.00 | 0.19 | +0.19 | 0.08 |

### Combined

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| turnovers per team | 149.72 | 135.56 | -14.17 | 1.90 |
| near goal carries per team | 55.06 | 51.03 | -4.03 | 2.23 |
| pass completion | 76.62% | 80.63% | +4.01 pp | 0.45 pp |
| passes attempted per team | 282.81 | 254.39 | -28.42 | 2.57 |
| interceptions per team | 53.17 | 40.06 | -13.11 | 1.53 |
| boundaries per team | 31.39 | 19.75 | -11.64 | 0.85 |
| carry goals per team | 0.42 | 2.08 | +1.67 | 0.34 |
| tackle commits per team | 348.94 | 337.08 | -11.86 | 5.10 |
| tackle wrong target share | 39.47% | 26.25% | -13.22 pp | 0.92 pp |
| tackle episode success | 10.02% | 11.66% | +1.64 pp | 0.28 pp |
| tackle hold success | 22.44% | 22.18% | -0.25 pp | 0.54 pp |
| keeper save rate | 14.54% | 15.00% | +0.47 pp | 1.34 pp |
| keeper save on target rate | 19.48% | 20.25% | +0.77 pp | 1.73 pp |
| planned changes per team | 40.72 | 42.17 | +1.44 | 0.47 |
| override exits per team | 3.47 | 2.47 | -1.00 | 0.26 |
| turnovers.fumble | 11.69 | 15.61 | +3.92 | 0.71 |
| turnovers.held ball | 0.00 | 0.06 | +0.06 | 0.03 |
| turnovers.interception | 53.17 | 40.06 | -13.11 | 1.53 |
| turnovers.major | 0.03 | 0.06 | +0.03 | 0.04 |
| turnovers.opponent control | 11.92 | 12.69 | +0.78 | 0.55 |
| turnovers.out of bounds | 31.39 | 19.75 | -11.64 | 0.85 |
| turnovers.play clock | 1.67 | 1.75 | +0.08 | 0.31 |
| turnovers.score restart | 25.08 | 27.72 | +2.64 | 0.73 |
| turnovers.strip | 1.47 | 1.33 | -0.14 | 0.36 |
| turnovers.tackle | 9.81 | 11.36 | +1.56 | 0.35 |
| turnovers.toss timeout | 0.42 | 0.31 | -0.11 | 0.13 |
| turnovers.turnover | 0.50 | 0.75 | +0.25 | 0.18 |
| turnovers.zone violation | 2.58 | 4.11 | +1.53 | 0.45 |
| carries.freeze | 0.08 | 0.17 | +0.08 | 0.05 |
| carries.goal | 0.42 | 2.08 | +1.67 | 0.34 |
| carries.handoff | 2.61 | 1.75 | -0.86 | 0.39 |
| carries.out of bounds | 12.33 | 2.08 | -10.25 | 0.56 |
| carries.pass | 2.94 | 2.25 | -0.69 | 0.38 |
| carries.shot | 26.36 | 32.97 | +6.61 | 1.26 |
| carries.stopped short | 5.50 | 4.67 | -0.83 | 0.68 |
| carries.strip | 0.58 | 0.44 | -0.14 | 0.16 |
| carries.tackle | 3.69 | 3.44 | -0.25 | 0.64 |
| carries.zone violation | 0.53 | 1.17 | +0.64 | 0.18 |
| stretches.end.lost control or expired | 0.00 | 0.28 | +0.28 | 0.08 |
| stretches.end.replaced | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch end | 0.00 | 0.28 | +0.28 | 0.08 |
| stretches.stretch goal | 0.00 | 0.28 | +0.28 | 0.08 |
| stretches.stretch start | 0.00 | 0.28 | +0.28 | 0.08 |

## Score, possession and margin — not judged on this sample

The owner reference ranges are 75–90 median team score and 100–150
possessions per team. The abbreviated sample is reported descriptively.

### Pass Clearance

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 90.00 | 82.50 | -7.50 | 3.75 |
| possessions | 151.83 | 139.47 | -12.36 | 1.77 |
| attempt share | 35.03% | 36.59% | +1.55 pp | 0.61 pp |
| four point share | 49.78% | 47.96% | -1.82 pp | 2.43 pp |
| median absolute margin | 24.50 | 27.00 | +2.50 | 6.52 |
| within five | 11.11% | 16.67% | +5.56 pp | 11.73 pp |
| team score sd | 16.41 | 18.63 | +2.22 | 2.39 |
| ala minus garvian margin | 23.60 | 9.80 | -13.80 | 10.51 |
| ala win share | 100.00% | 50.00% | -50.00 pp | 15.81 pp |

Ala–Garvian mean margin within-arm SE 4.91 OFF and 10.29 ON.

### Carry Finish

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 90.00 | 105.50 | +15.50 | 4.36 |
| possessions | 151.83 | 152.28 | +0.44 | 1.67 |
| attempt share | 35.03% | 35.90% | +0.86 pp | 0.45 pp |
| four point share | 49.78% | 38.19% | -11.59 pp | 2.33 pp |
| median absolute margin | 24.50 | 27.50 | +3.00 | 9.13 |
| within five | 11.11% | 16.67% | +5.56 pp | 10.13 pp |
| team score sd | 16.41 | 23.32 | +6.91 | 2.10 |
| ala minus garvian margin | 23.60 | 44.70 | +21.10 | 7.90 |
| ala win share | 100.00% | 100.00% | +0.00 pp | 0.00 pp |

Ala–Garvian mean margin within-arm SE 4.91 OFF and 7.00 ON.

### Fresh Takedown

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 90.00 | 87.50 | -2.50 | 4.36 |
| possessions | 151.83 | 151.19 | -0.64 | 1.92 |
| attempt share | 35.03% | 34.17% | -0.86 pp | 0.70 pp |
| four point share | 49.78% | 49.09% | -0.69 pp | 2.35 pp |
| median absolute margin | 24.50 | 11.50 | -13.00 | 7.79 |
| within five | 11.11% | 16.67% | +5.56 pp | 11.57 pp |
| team score sd | 16.41 | 17.39 | +0.98 | 3.05 |
| ala minus garvian margin | 23.60 | 17.00 | -6.60 | 9.65 |
| ala win share | 100.00% | 90.00% | -10.00 pp | 9.39 pp |

Ala–Garvian mean margin within-arm SE 4.91 OFF and 6.98 ON.

### Boundary Guard

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 90.00 | 97.50 | +7.50 | 4.77 |
| possessions | 151.83 | 143.69 | -8.14 | 2.35 |
| attempt share | 35.03% | 36.57% | +1.54 pp | 0.69 pp |
| four point share | 49.78% | 44.66% | -5.12 pp | 3.33 pp |
| median absolute margin | 24.50 | 24.50 | +0.00 | 6.74 |
| within five | 11.11% | 11.11% | +0.00 pp | 10.49 pp |
| team score sd | 16.41 | 20.06 | +3.65 | 2.53 |
| ala minus garvian margin | 23.60 | 28.40 | +4.80 | 9.66 |
| ala win share | 100.00% | 90.00% | -10.00 pp | 9.29 pp |

Ala–Garvian mean margin within-arm SE 4.91 OFF and 7.79 ON.

### Combined

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 90.00 | 98.00 | +8.00 | 2.94 |
| possessions | 151.83 | 137.61 | -14.22 | 1.92 |
| attempt share | 35.03% | 35.69% | +0.65 pp | 0.74 pp |
| four point share | 49.78% | 36.48% | -13.30 pp | 1.94 pp |
| median absolute margin | 24.50 | 22.00 | -2.50 | 7.34 |
| within five | 11.11% | 0.00% | -11.11 pp | 6.83 pp |
| team score sd | 16.41 | 19.29 | +2.88 | 1.87 |
| ala minus garvian margin | 23.60 | 26.30 | +2.70 | 5.60 |
| ala win share | 100.00% | 90.00% | -10.00 pp | 9.23 pp |

Ala–Garvian mean margin within-arm SE 4.91 OFF and 7.80 ON.

## Boundary audit

| Cause | Events | Mean absolute launch yaw | Inside aim | Outside aim | Pressured carrier exits | Mean believed edge distance |
|---|---:|---:|---:|---:|---:|---:|
| carrier | 188 | —° | 0 | 0 | 99/188 | 1.48 m |
| deflection | 53 | 0.87° | 53 | 0 | 0/0 | — m |
| held_ball | 658 | —° | 0 | 0 | 144/658 | 1.81 m |
| loose_ball | 8 | —° | 0 | 0 | 0/0 | — m |
| pass | 140 | 0.64° | 140 | 0 | 0/0 | — m |
| shot | 185 | 1.07° | 185 | 0 | 0/0 | — m |

The largest classified group is **held_ball**, with **658** events. The ball crossed while the body was still in bounds. In seed 1 this accounted for 31 of 64 boundary events, often with outward velocity and an aim toward the center. The guard reserves own braking distance and only exempts a route within the whole-ball goal-mouth envelope. This is a behavioral choice.

## Keeper envelope

The audit measured **1218** of **1232** on-target
shots in the OFF arm. **312** (25.62%) were reachable
under the physical release-time upper bound. **150**
(48.08%) of those were saved. Mean release-to-plane time was
**0.34 s**. Projected misses for otherwise on-target
records are reported separately (14).

| Outcome among physically reachable shots | Count |
|---|---:|
| save | 150 |
| touch_without_save | 31 |
| no_commit | 113 |
| late_commit | 15 |
| wrong_side | 2 |
| no_contact_after_commit | 1 |

The underlying per-shot records carry the Keeper's release position, measured arm
and standing reach, effective jump, Reflex and remaining action time. These
are upper bounds without later traffic and decision delay. A touch without
a save is a contact result. Wrong-side classification compares the save
intent's perceived path with the true crossing. Untouched shots after a
timely same-side commitment stay separate rather than being counted as a
catch failure.

## Evidence

- [Paired aggregates and case lists](rb332/evidence/paired.json)
- [Per-case records and named seed-1 box scores](rb332/evidence)
- [Reproduction commands](rb332/README.md)

No new CANON question arose.
