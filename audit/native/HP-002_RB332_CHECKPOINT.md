# OWNER BRIEFING

1. **DESIGN COMPLETE, IMPLEMENTED** for pass clearance, carry finish, fresh takedown evidence and boundary braking. Each runs under its own switch. Keeper reach is a read-only audit.
2. All trial arms use the 0.58 fatigue scale, which averaged 3.25 override exits per team in the calibration pilots. 7 of 180 trial games and 1 of 30 historical replays are recorded.
3. Trial effects below are provisional until the remaining games finish. The reach and boundary assignments are observational.
4. Verification is still in progress.
5. Review matched deltas, especially pass volume and changes in scoring and possession, before selecting a behavior profile.

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
| Fatigue calibration | DESIGN COMPLETE, IMPLEMENTED, TESTED. Two scale-0.58 pilots. |
| Pass clearance | DESIGN COMPLETE, IMPLEMENTED. 2 of 30 ON cases finished. |
| Carry finish | DESIGN COMPLETE, IMPLEMENTED. 1 of 30 ON cases finished. |
| Fresh takedown evidence | DESIGN COMPLETE, IMPLEMENTED. 1 of 30 ON cases finished. |
| Boundary diagnosis and guard | DESIGN COMPLETE, IMPLEMENTED. 1 OFF and 1 ON cases. |
| Keeper reach diagnosis | DESIGN COMPLETE, IMPLEMENTED. 1 OFF cases. |
| Combined policy | DESIGN COMPLETE, IMPLEMENTED. 1 of 30 ON cases finished. |


## Historical pass clearance

The forecast flagged **27 of 42**
measured cases from **42** of the original 1,020
believed-clear interceptions. Classification is evaluated on the admitted
decision view and selected delivery, with the historical population keyed to
the unchanged RB-3.31 trace. The number measures historical flags.

## Paired changes

The parent owner reference ranges are 75–90 for median team score and
100–150 for mean possessions per team. No tuning used the observed trial
outcomes.

### pass_clearance

1 paired games.

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 97.50 | 77.00 | -20.50 | — |
| possessions | 144.00 | 139.00 | -5.00 | — |
| attempt share | 37.15% | 34.53% | -2.62 pp | — |
| pass completion | 78.47% | 78.76% | +0.29 pp | — |
| passes attempted per team | 288.00 | 259.00 | -29.00 | — |
| interceptions per team | 47.50 | 45.00 | -2.50 | — |
| boundaries per team | 28.50 | 25.00 | -3.50 | — |
| carry goals per team | 0.50 | 0.00 | -0.50 | — |
| tackle commits per team | 354.00 | 396.00 | +42.00 | — |
| tackle wrong target share | 35.03% | 40.28% | +5.25 pp | — |
| tackle episode success | 11.72% | 11.62% | -0.11 pp | — |
| tackle hold success | 24.82% | 24.94% | +0.13 pp | — |
| keeper save rate | 8.79% | 15.79% | +7.00 pp | — |
| keeper save on target rate | 12.50% | 20.34% | +7.84 pp | — |
| four point share | 59.49% | 54.55% | -4.94 pp | — |
| median absolute margin | 5.00 | 24.00 | +19.00 | — |
| within five | 100.00% | 0.00% | -100.00 pp | — |
| team score sd | 3.54 | 16.97 | +13.44 | — |
| ala minus garvian margin | 5.00 | -24.00 | -29.00 | — |
| ala margin se | — | — | — | — |
| ala win share | 100.00% | 0.00% | -100.00 pp | — |
| planned changes per team | 40.00 | 41.00 | +1.00 | — |
| override exits per team | 3.50 | 4.00 | +0.50 | — |
| turnovers.fumble | 8.00 | 16.50 | +8.50 | — |
| turnovers.interception | 47.50 | 45.00 | -2.50 | — |
| turnovers.opponent control | 11.00 | 9.00 | -2.00 | — |
| turnovers.out of bounds | 28.50 | 25.00 | -3.50 | — |
| turnovers.play clock | 2.50 | 2.50 | +0.00 | — |
| turnovers.score restart | 27.50 | 21.50 | -6.00 | — |
| turnovers.strip | 2.50 | 0.50 | -2.00 | — |
| turnovers.tackle | 13.00 | 12.50 | -0.50 | — |
| turnovers.toss timeout | 0.50 | 0.00 | -0.50 | — |
| turnovers.turnover | 0.50 | 1.00 | +0.50 | — |
| turnovers.zone violation | 0.50 | 3.50 | +3.00 | — |
| carries.freeze | 0.00 | 1.00 | +1.00 | — |
| carries.goal | 0.50 | 0.00 | -0.50 | — |
| carries.handoff | 3.00 | 2.50 | -0.50 | — |
| carries.out of bounds | 11.50 | 13.50 | +2.00 | — |
| carries.pass | 3.50 | 5.50 | +2.00 | — |
| carries.shot | 24.50 | 21.50 | -3.00 | — |
| carries.stopped short | 5.00 | 7.00 | +2.00 | — |
| carries.strip | 1.00 | 0.50 | -0.50 | — |
| carries.tackle | 5.00 | 5.00 | +0.00 | — |
| carries.zone violation | 0.00 | 0.50 | +0.50 | — |
| stretches.end.lost control or expired | 0.00 | 0.00 | +0.00 | — |
| stretches.end.replaced | 0.00 | 0.00 | +0.00 | — |
| stretches.stretch end | 0.00 | 0.00 | +0.00 | — |
| stretches.stretch goal | 0.00 | 0.00 | +0.00 | — |
| stretches.stretch start | 0.00 | 0.00 | +0.00 | — |

### carry_finish

1 paired games.

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 97.50 | 116.00 | +18.50 | — |
| possessions | 144.00 | 145.50 | +1.50 | — |
| attempt share | 37.15% | 37.11% | -0.04 pp | — |
| pass completion | 78.47% | 78.21% | -0.26 pp | — |
| passes attempted per team | 288.00 | 280.00 | -8.00 | — |
| interceptions per team | 47.50 | 50.00 | +2.50 | — |
| boundaries per team | 28.50 | 25.50 | -3.00 | — |
| carry goals per team | 0.50 | 4.00 | +3.50 | — |
| tackle commits per team | 354.00 | 323.00 | -31.00 | — |
| tackle wrong target share | 35.03% | 39.63% | +4.60 pp | — |
| tackle episode success | 11.72% | 10.53% | -1.20 pp | — |
| tackle hold success | 24.82% | 24.85% | +0.04 pp | — |
| keeper save rate | 8.79% | 12.73% | +3.94 pp | — |
| keeper save on target rate | 12.50% | 17.95% | +5.45 pp | — |
| four point share | 59.49% | 41.38% | -18.11 pp | — |
| median absolute margin | 5.00 | 72.00 | +67.00 | — |
| within five | 100.00% | 0.00% | -100.00 pp | — |
| team score sd | 3.54 | 50.91 | +47.38 | — |
| ala minus garvian margin | 5.00 | 72.00 | +67.00 | — |
| ala margin se | — | — | — | — |
| ala win share | 100.00% | 100.00% | +0.00 pp | — |
| planned changes per team | 40.00 | 41.50 | +1.50 | — |
| override exits per team | 3.50 | 3.00 | -0.50 | — |
| turnovers.fumble | 8.00 | 10.50 | +2.50 | — |
| turnovers.interception | 47.50 | 50.00 | +2.50 | — |
| turnovers.opponent control | 11.00 | 13.50 | +2.50 | — |
| turnovers.out of bounds | 28.50 | 25.50 | -3.00 | — |
| turnovers.play clock | 2.50 | 1.50 | -1.00 | — |
| turnovers.score restart | 27.50 | 30.50 | +3.00 | — |
| turnovers.strip | 2.50 | 1.00 | -1.50 | — |
| turnovers.tackle | 13.00 | 8.00 | -5.00 | — |
| turnovers.toss timeout | 0.50 | 0.50 | +0.00 | — |
| turnovers.turnover | 0.50 | 1.50 | +1.00 | — |
| turnovers.zone violation | 0.50 | 1.00 | +0.50 | — |
| carries.freeze | 0.00 | 0.00 | +0.00 | — |
| carries.goal | 0.50 | 4.00 | +3.50 | — |
| carries.handoff | 3.00 | 2.00 | -1.00 | — |
| carries.out of bounds | 11.50 | 5.50 | -6.00 | — |
| carries.pass | 3.50 | 2.50 | -1.00 | — |
| carries.shot | 24.50 | 34.00 | +9.50 | — |
| carries.stopped short | 5.00 | 3.50 | -1.50 | — |
| carries.strip | 1.00 | 0.00 | -1.00 | — |
| carries.tackle | 5.00 | 2.50 | -2.50 | — |
| carries.zone violation | 0.00 | 0.00 | +0.00 | — |
| stretches.end.lost control or expired | 0.00 | 0.00 | +0.00 | — |
| stretches.end.replaced | 0.00 | 0.00 | +0.00 | — |
| stretches.stretch end | 0.00 | 0.00 | +0.00 | — |
| stretches.stretch goal | 0.00 | 0.00 | +0.00 | — |
| stretches.stretch start | 0.00 | 0.00 | +0.00 | — |

### fresh_takedown

1 paired games.

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 97.50 | 92.00 | -5.50 | — |
| possessions | 144.00 | 137.50 | -6.50 | — |
| attempt share | 37.15% | 34.18% | -2.97 pp | — |
| pass completion | 78.47% | 80.19% | +1.72 pp | — |
| passes attempted per team | 288.00 | 265.00 | -23.00 | — |
| interceptions per team | 47.50 | 44.00 | -3.50 | — |
| boundaries per team | 28.50 | 28.50 | +0.00 | — |
| carry goals per team | 0.50 | 0.00 | -0.50 | — |
| tackle commits per team | 354.00 | 300.50 | -53.50 | — |
| tackle wrong target share | 35.03% | 26.79% | -8.24 pp | — |
| tackle episode success | 11.72% | 10.32% | -1.41 pp | — |
| tackle hold success | 24.82% | 20.39% | -4.42 pp | — |
| keeper save rate | 8.79% | 10.23% | +1.44 pp | — |
| keeper save on target rate | 12.50% | 13.64% | +1.14 pp | — |
| four point share | 59.49% | 43.48% | -16.01 pp | — |
| median absolute margin | 5.00 | 8.00 | +3.00 | — |
| within five | 100.00% | 0.00% | -100.00 pp | — |
| team score sd | 3.54 | 5.66 | +2.12 | — |
| ala minus garvian margin | 5.00 | 8.00 | +3.00 | — |
| ala margin se | — | — | — | — |
| ala win share | 100.00% | 100.00% | +0.00 pp | — |
| planned changes per team | 40.00 | 42.00 | +2.00 | — |
| override exits per team | 3.50 | 2.50 | -1.00 | — |
| turnovers.fumble | 8.00 | 12.00 | +4.00 | — |
| turnovers.interception | 47.50 | 44.00 | -3.50 | — |
| turnovers.opponent control | 11.00 | 9.50 | -1.50 | — |
| turnovers.out of bounds | 28.50 | 28.50 | +0.00 | — |
| turnovers.play clock | 2.50 | 2.00 | -0.50 | — |
| turnovers.score restart | 27.50 | 26.50 | -1.00 | — |
| turnovers.strip | 2.50 | 1.50 | -1.00 | — |
| turnovers.tackle | 13.00 | 8.50 | -4.50 | — |
| turnovers.toss timeout | 0.50 | 0.00 | -0.50 | — |
| turnovers.turnover | 0.50 | 0.50 | +0.00 | — |
| turnovers.zone violation | 0.50 | 2.50 | +2.00 | — |
| carries.freeze | 0.00 | 0.00 | +0.00 | — |
| carries.goal | 0.50 | 0.00 | -0.50 | — |
| carries.handoff | 3.00 | 1.50 | -1.50 | — |
| carries.out of bounds | 11.50 | 7.00 | -4.50 | — |
| carries.pass | 3.50 | 2.00 | -1.50 | — |
| carries.shot | 24.50 | 27.00 | +2.50 | — |
| carries.stopped short | 5.00 | 3.00 | -2.00 | — |
| carries.strip | 1.00 | 0.00 | -1.00 | — |
| carries.tackle | 5.00 | 2.50 | -2.50 | — |
| carries.zone violation | 0.00 | 1.00 | +1.00 | — |
| stretches.end.lost control or expired | 0.00 | 0.00 | +0.00 | — |
| stretches.end.replaced | 0.00 | 0.00 | +0.00 | — |
| stretches.stretch end | 0.00 | 0.00 | +0.00 | — |
| stretches.stretch goal | 0.00 | 0.00 | +0.00 | — |
| stretches.stretch start | 0.00 | 0.00 | +0.00 | — |

### boundary_guard

1 paired games.

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 97.50 | 110.00 | +12.50 | — |
| possessions | 144.00 | 142.50 | -1.50 | — |
| attempt share | 37.15% | 38.25% | +1.09 pp | — |
| pass completion | 78.47% | 78.10% | -0.37 pp | — |
| passes attempted per team | 288.00 | 258.00 | -30.00 | — |
| interceptions per team | 47.50 | 49.00 | +1.50 | — |
| boundaries per team | 28.50 | 18.50 | -10.00 | — |
| carry goals per team | 0.50 | 2.50 | +2.00 | — |
| tackle commits per team | 354.00 | 331.50 | -22.50 | — |
| tackle wrong target share | 35.03% | 36.95% | +1.92 pp | — |
| tackle episode success | 11.72% | 10.11% | -1.62 pp | — |
| tackle hold success | 24.82% | 22.25% | -2.56 pp | — |
| keeper save rate | 8.79% | 14.15% | +5.36 pp | — |
| keeper save on target rate | 12.50% | 18.52% | +6.02 pp | — |
| four point share | 59.49% | 36.36% | -23.12 pp | — |
| median absolute margin | 5.00 | 38.00 | +33.00 | — |
| within five | 100.00% | 0.00% | -100.00 pp | — |
| team score sd | 3.54 | 26.87 | +23.33 | — |
| ala minus garvian margin | 5.00 | 38.00 | +33.00 | — |
| ala margin se | — | — | — | — |
| ala win share | 100.00% | 100.00% | +0.00 pp | — |
| planned changes per team | 40.00 | 42.00 | +2.00 | — |
| override exits per team | 3.50 | 1.00 | -2.50 | — |
| turnovers.fumble | 8.00 | 12.50 | +4.50 | — |
| turnovers.interception | 47.50 | 49.00 | +1.50 | — |
| turnovers.opponent control | 11.00 | 10.00 | -1.00 | — |
| turnovers.out of bounds | 28.50 | 18.50 | -10.00 | — |
| turnovers.play clock | 2.50 | 2.50 | +0.00 | — |
| turnovers.score restart | 27.50 | 33.50 | +6.00 | — |
| turnovers.strip | 2.50 | 1.00 | -1.50 | — |
| turnovers.tackle | 13.00 | 9.00 | -4.00 | — |
| turnovers.toss timeout | 0.50 | 0.00 | -0.50 | — |
| turnovers.turnover | 0.50 | 0.50 | +0.00 | — |
| turnovers.zone violation | 0.50 | 4.00 | +3.50 | — |
| carries.freeze | 0.00 | 0.50 | +0.50 | — |
| carries.goal | 0.50 | 2.50 | +2.00 | — |
| carries.handoff | 3.00 | 2.00 | -1.00 | — |
| carries.out of bounds | 11.50 | 4.00 | -7.50 | — |
| carries.pass | 3.50 | 4.00 | +0.50 | — |
| carries.shot | 24.50 | 36.50 | +12.00 | — |
| carries.stopped short | 5.00 | 2.00 | -3.00 | — |
| carries.strip | 1.00 | 0.50 | -0.50 | — |
| carries.tackle | 5.00 | 2.00 | -3.00 | — |
| carries.zone violation | 0.00 | 2.50 | +2.50 | — |
| stretches.end.lost control or expired | 0.00 | 0.50 | +0.50 | — |
| stretches.end.replaced | 0.00 | 0.50 | +0.50 | — |
| stretches.stretch end | 0.00 | 1.00 | +1.00 | — |
| stretches.stretch goal | 0.00 | 0.50 | +0.50 | — |
| stretches.stretch start | 0.00 | 1.00 | +1.00 | — |

### combined

1 paired games.

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 97.50 | 86.50 | -11.00 | — |
| possessions | 144.00 | 143.50 | -0.50 | — |
| attempt share | 37.15% | 32.40% | -4.75 pp | — |
| pass completion | 78.47% | 79.88% | +1.41 pp | — |
| passes attempted per team | 288.00 | 258.50 | -29.50 | — |
| interceptions per team | 47.50 | 44.50 | -3.00 | — |
| boundaries per team | 28.50 | 24.00 | -4.50 | — |
| carry goals per team | 0.50 | 0.00 | -0.50 | — |
| tackle commits per team | 354.00 | 311.50 | -42.50 | — |
| tackle wrong target share | 35.03% | 26.32% | -8.70 pp | — |
| tackle episode success | 11.72% | 12.36% | +0.64 pp | — |
| tackle hold success | 24.82% | 24.04% | -0.77 pp | — |
| keeper save rate | 8.79% | 15.38% | +6.59 pp | — |
| keeper save on target rate | 12.50% | 23.08% | +10.58 pp | — |
| four point share | 59.49% | 39.31% | -20.18 pp | — |
| median absolute margin | 5.00 | 25.00 | +20.00 | — |
| within five | 100.00% | 0.00% | -100.00 pp | — |
| team score sd | 3.54 | 17.68 | +14.14 | — |
| ala minus garvian margin | 5.00 | -25.00 | -30.00 | — |
| ala margin se | — | — | — | — |
| ala win share | 100.00% | 0.00% | -100.00 pp | — |
| planned changes per team | 40.00 | 42.00 | +2.00 | — |
| override exits per team | 3.50 | 2.00 | -1.50 | — |
| turnovers.fumble | 8.00 | 16.50 | +8.50 | — |
| turnovers.interception | 47.50 | 44.50 | -3.00 | — |
| turnovers.opponent control | 11.00 | 8.50 | -2.50 | — |
| turnovers.out of bounds | 28.50 | 24.00 | -4.50 | — |
| turnovers.play clock | 2.50 | 0.50 | -2.00 | — |
| turnovers.score restart | 27.50 | 26.00 | -1.50 | — |
| turnovers.strip | 2.50 | 0.50 | -2.00 | — |
| turnovers.tackle | 13.00 | 15.00 | +2.00 | — |
| turnovers.toss timeout | 0.50 | 0.00 | -0.50 | — |
| turnovers.turnover | 0.50 | 0.50 | +0.00 | — |
| turnovers.zone violation | 0.50 | 5.50 | +5.00 | — |
| carries.freeze | 0.00 | 0.00 | +0.00 | — |
| carries.goal | 0.50 | 0.00 | -0.50 | — |
| carries.handoff | 3.00 | 2.00 | -1.00 | — |
| carries.out of bounds | 11.50 | 2.00 | -9.50 | — |
| carries.pass | 3.50 | 1.00 | -2.50 | — |
| carries.shot | 24.50 | 36.00 | +11.50 | — |
| carries.stopped short | 5.00 | 2.50 | -2.50 | — |
| carries.strip | 1.00 | 0.00 | -1.00 | — |
| carries.tackle | 5.00 | 1.50 | -3.50 | — |
| carries.zone violation | 0.00 | 1.00 | +1.00 | — |
| stretches.end.lost control or expired | 0.00 | 0.00 | +0.00 | — |
| stretches.end.replaced | 0.00 | 0.00 | +0.00 | — |
| stretches.stretch end | 0.00 | 0.00 | +0.00 | — |
| stretches.stretch goal | 0.00 | 0.00 | +0.00 | — |
| stretches.stretch start | 0.00 | 0.00 | +0.00 | — |

## Boundary audit

| Cause | Events | Mean absolute launch yaw | Inside aim | Outside aim | Pressured carrier exits | Mean believed edge distance |
|---|---:|---:|---:|---:|---:|---:|
| carrier | 8 | —° | 0 | 0 | 5/8 | 2.14 m |
| deflection | 5 | 0.64° | 5 | 0 | 0/0 | — m |
| held_ball | 31 | —° | 0 | 0 | 4/31 | 1.92 m |
| loose_ball | 2 | —° | 0 | 0 | 0/0 | — m |
| pass | 5 | 0.61° | 5 | 0 | 0/0 | — m |
| shot | 13 | 0.79° | 13 | 0 | 0/0 | — m |

The largest classified group is **held_ball**, with **31** events. The ball crossed while the body was still in bounds. In seed 1 this accounted for 31 of 64 boundary events, often with outward velocity and an aim toward the center. The guard reserves own braking distance and only exempts a route within the whole-ball goal-mouth envelope. This is a behavioral choice.

## Keeper envelope

The audit measured **64** of **64** on-target
shots in the OFF arm. **16** (25.00%) were reachable
under the physical release-time upper bound. **6**
(37.50%) of those were saved. Mean release-to-plane time was
**0.35 s**. Projected misses for otherwise on-target
records are reported separately (0).

| Outcome among physically reachable shots | Count |
|---|---:|
| save | 6 |
| touch_without_save | 2 |
| no_commit | 8 |

Every reachable record carries the Keeper's release position, measured arm
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
