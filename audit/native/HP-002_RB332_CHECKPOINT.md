# OWNER BRIEFING

1. **DESIGN COMPLETE, IMPLEMENTED** for pass clearance, carry finish, fresh takedown evidence and boundary braking. Each runs under its own switch. Keeper reach is a read-only audit.
2. All trial arms use the 0.58 fatigue scale, which averaged 3.25 override exits per team in the calibration pilots. 90 of 180 trial games and 14 of 30 historical replays are recorded.
3. Trial effects below are provisional until the remaining games finish. The reach and boundary assignments are observational.
4. The maintained suite, identities and deterministic combined replay are verified. CPU overhead measured -0.41%.
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
| Pass clearance | DESIGN COMPLETE, IMPLEMENTED. 15 of 30 ON cases finished. |
| Carry finish | DESIGN COMPLETE, IMPLEMENTED. 15 of 30 ON cases finished. |
| Fresh takedown evidence | DESIGN COMPLETE, IMPLEMENTED. 15 of 30 ON cases finished. |
| Boundary diagnosis and guard | DESIGN COMPLETE, IMPLEMENTED. 15 OFF and 15 ON cases. |
| Keeper reach diagnosis | DESIGN COMPLETE, IMPLEMENTED. 15 OFF cases. |
| Combined policy | DESIGN COMPLETE, IMPLEMENTED. 15 of 30 ON cases finished. |

`pytest -q b1 native` reported `811 passed, 1 warning, 23 subtests passed in 646.88s (0:10:46)`.
All six legacy rows matched.
The paired production benchmark used four 1,500-step windows from the same
seeds and fatigue scale. The OFF mode used 4.133 process CPU ms/step
and combined used 4.116, a change of -0.41%.
- compatibility 57–76, exact trace `44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072` and state `046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d`.
- core 61–80, exact trace `c1a578db3f2754d3f69b47ba81a1f9d5b9336e1d87f496de2fa8dc3daee7a256` and state `c517e00f864f1438705cdd1d9768d61523ee1aaac69746f57a2e9f1f4adf2745`.
- R1 85–86, exact trace `a399f74f81d891c8a0cd4014fc5d10bc5623ad835c448932a94cd50ffac7ac4b` and state `bc4898a8229d147bd60defdc623db55fac13a3845fb5f29f812198b4bf5f61d4`.
- PLANNED 64–96, exact trace `ab86f8befcf2baca264ab87fabdd39af3e218cb80032eab52b356a089319a08a` and state `e8318c85ba3ae5205861d138f8d4f63e16202dd6d84f4ab8b5df02066e141047`.
- Combined repeat 99–74, trace `0045e62d5de38fc85a6c38fd58298284f637bb6d1766ddb7d50cfb159ac22601` and state `b2b6857584bbdc7c486b54f52bd8ebf9c2c89fde8e15893a42c70f5c3be9d9de`.

## Historical pass clearance

The forecast flagged **296 of 469**
measured cases from **469** of the original 1,020
believed-clear interceptions. Classification is evaluated on the admitted
decision view and selected delivery, with the historical population keyed to
the unchanged RB-3.31 trace. The number measures historical flags.

## Paired changes

The parent owner reference ranges are 75–90 for median team score and
100–150 for mean possessions per team. No tuning used the observed trial
outcomes.

### pass_clearance

15 paired games.

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 90.50 | 81.00 | -9.50 | 4.67 |
| possessions | 152.27 | 138.93 | -13.33 | 1.98 |
| attempt share | 34.94% | 36.16% | +1.22 pp | 0.75 pp |
| pass completion | 76.57% | 80.09% | +3.52 pp | 0.45 pp |
| passes attempted per team | 280.73 | 255.03 | -25.70 | 3.74 |
| interceptions per team | 53.00 | 41.43 | -11.57 | 1.11 |
| boundaries per team | 31.87 | 30.70 | -1.17 | 1.01 |
| carry goals per team | 0.40 | 0.70 | +0.30 | 0.22 |
| tackle commits per team | 340.80 | 353.40 | +12.60 | 7.68 |
| tackle wrong target share | 39.18% | 36.89% | -2.29 pp | 0.82 pp |
| tackle episode success | 10.27% | 11.25% | +0.98 pp | 0.37 pp |
| tackle hold success | 22.60% | 23.69% | +1.09 pp | 0.76 pp |
| keeper save rate | 14.12% | 12.29% | -1.83 pp | 1.46 pp |
| keeper save on target rate | 18.91% | 17.14% | -1.77 pp | 1.88 pp |
| four point share | 48.95% | 47.01% | -1.94 pp | 2.68 pp |
| median absolute margin | 24.00 | 29.00 | +5.00 | 7.40 |
| within five | 13.33% | 13.33% | +0.00 pp | 12.56 pp |
| team score sd | 16.50 | 18.83 | +2.33 | 2.58 |
| ala minus garvian margin | 23.60 | 9.80 | -13.80 | 10.86 |
| ala margin se | 4.91 | 10.29 | +5.39 | 1.61 |
| ala win share | 100.00% | 50.00% | -50.00 pp | 15.70 pp |
| planned changes per team | 41.20 | 42.07 | +0.87 | 0.41 |
| override exits per team | 3.23 | 2.70 | -0.53 | 0.23 |
| turnovers.fumble | 11.57 | 13.00 | +1.43 | 1.02 |
| turnovers.held ball | 0.00 | 0.00 | +0.00 | 0.00 |
| turnovers.interception | 53.00 | 41.43 | -11.57 | 1.11 |
| turnovers.major | 0.03 | 0.00 | -0.03 | 0.03 |
| turnovers.opponent control | 11.70 | 10.57 | -1.13 | 0.64 |
| turnovers.out of bounds | 31.87 | 30.70 | -1.17 | 1.01 |
| turnovers.play clock | 1.67 | 1.83 | +0.17 | 0.28 |
| turnovers.score restart | 25.17 | 23.07 | -2.10 | 0.91 |
| turnovers.strip | 1.53 | 1.57 | +0.03 | 0.33 |
| turnovers.tackle | 10.07 | 11.17 | +1.10 | 0.81 |
| turnovers.toss timeout | 0.40 | 0.63 | +0.23 | 0.20 |
| turnovers.turnover | 0.53 | 0.40 | -0.13 | 0.15 |
| turnovers.zone violation | 2.67 | 2.50 | -0.17 | 0.39 |
| carries.freeze | 0.10 | 0.17 | +0.07 | 0.09 |
| carries.goal | 0.40 | 0.70 | +0.30 | 0.22 |
| carries.handoff | 2.73 | 1.67 | -1.07 | 0.32 |
| carries.out of bounds | 12.47 | 12.00 | -0.47 | 0.65 |
| carries.pass | 2.83 | 3.33 | +0.50 | 0.37 |
| carries.shot | 26.37 | 25.00 | -1.37 | 1.31 |
| carries.stopped short | 5.30 | 5.23 | -0.07 | 0.64 |
| carries.strip | 0.57 | 0.33 | -0.23 | 0.19 |
| carries.tackle | 3.63 | 4.03 | +0.40 | 0.52 |
| carries.zone violation | 0.50 | 0.27 | -0.23 | 0.14 |
| stretches.end.lost control or expired | 0.00 | 0.03 | +0.03 | 0.03 |
| stretches.end.replaced | 0.00 | 0.03 | +0.03 | 0.03 |
| stretches.stretch end | 0.00 | 0.07 | +0.07 | 0.06 |
| stretches.stretch goal | 0.00 | 0.03 | +0.03 | 0.03 |
| stretches.stretch start | 0.00 | 0.07 | +0.07 | 0.06 |

### carry_finish

15 paired games.

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 90.50 | 108.00 | +17.50 | 5.64 |
| possessions | 152.27 | 152.07 | -0.20 | 1.87 |
| attempt share | 34.94% | 35.69% | +0.75 pp | 0.53 pp |
| pass completion | 76.57% | 76.64% | +0.07 pp | 0.33 pp |
| passes attempted per team | 280.73 | 278.17 | -2.57 | 3.32 |
| interceptions per team | 53.00 | 51.80 | -1.20 | 1.23 |
| boundaries per team | 31.87 | 29.60 | -2.27 | 1.25 |
| carry goals per team | 0.40 | 2.97 | +2.57 | 0.22 |
| tackle commits per team | 340.80 | 328.47 | -12.33 | 6.48 |
| tackle wrong target share | 39.18% | 39.39% | +0.20 pp | 0.91 pp |
| tackle episode success | 10.27% | 10.08% | -0.19 pp | 0.33 pp |
| tackle hold success | 22.60% | 22.51% | -0.09 pp | 0.67 pp |
| keeper save rate | 14.12% | 14.02% | -0.10 pp | 1.07 pp |
| keeper save on target rate | 18.91% | 19.75% | +0.84 pp | 1.49 pp |
| four point share | 48.95% | 38.18% | -10.77 pp | 2.73 pp |
| median absolute margin | 24.00 | 39.00 | +15.00 | 14.06 |
| within five | 13.33% | 13.33% | +0.00 pp | 11.00 pp |
| team score sd | 16.50 | 24.14 | +7.64 | 2.44 |
| ala minus garvian margin | 23.60 | 44.70 | +21.10 | 7.80 |
| ala margin se | 4.91 | 7.00 | +2.10 | 1.46 |
| ala win share | 100.00% | 100.00% | +0.00 pp | 0.00 pp |
| planned changes per team | 41.20 | 41.90 | +0.70 | 0.44 |
| override exits per team | 3.23 | 2.90 | -0.33 | 0.24 |
| turnovers.fumble | 11.57 | 12.67 | +1.10 | 0.84 |
| turnovers.held ball | 0.00 | 0.00 | +0.00 | 0.00 |
| turnovers.interception | 53.00 | 51.80 | -1.20 | 1.23 |
| turnovers.major | 0.03 | 0.03 | +0.00 | 0.04 |
| turnovers.opponent control | 11.70 | 12.93 | +1.23 | 0.51 |
| turnovers.out of bounds | 31.87 | 29.60 | -2.27 | 1.25 |
| turnovers.play clock | 1.67 | 1.43 | -0.23 | 0.25 |
| turnovers.score restart | 25.17 | 28.60 | +3.43 | 0.98 |
| turnovers.strip | 1.53 | 1.17 | -0.37 | 0.22 |
| turnovers.tackle | 10.07 | 8.47 | -1.60 | 0.72 |
| turnovers.toss timeout | 0.40 | 0.53 | +0.13 | 0.13 |
| turnovers.turnover | 0.53 | 0.63 | +0.10 | 0.18 |
| turnovers.zone violation | 2.67 | 2.03 | -0.63 | 0.39 |
| carries.freeze | 0.10 | 0.10 | +0.00 | 0.08 |
| carries.goal | 0.40 | 2.97 | +2.57 | 0.22 |
| carries.handoff | 2.73 | 1.20 | -1.53 | 0.46 |
| carries.out of bounds | 12.47 | 7.63 | -4.83 | 0.64 |
| carries.pass | 2.83 | 1.70 | -1.13 | 0.33 |
| carries.shot | 26.37 | 32.87 | +6.50 | 1.42 |
| carries.stopped short | 5.30 | 4.80 | -0.50 | 0.50 |
| carries.strip | 0.57 | 0.43 | -0.13 | 0.16 |
| carries.tackle | 3.63 | 2.20 | -1.43 | 0.47 |
| carries.zone violation | 0.50 | 0.33 | -0.17 | 0.12 |
| stretches.end.lost control or expired | 0.00 | 0.20 | +0.20 | 0.08 |
| stretches.end.replaced | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch end | 0.00 | 0.20 | +0.20 | 0.08 |
| stretches.stretch goal | 0.00 | 0.20 | +0.20 | 0.08 |
| stretches.stretch start | 0.00 | 0.20 | +0.20 | 0.08 |

### fresh_takedown

15 paired games.

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 90.50 | 86.00 | -4.50 | 4.98 |
| possessions | 152.27 | 150.80 | -1.47 | 2.31 |
| attempt share | 34.94% | 34.06% | -0.88 pp | 0.86 pp |
| pass completion | 76.57% | 76.01% | -0.56 pp | 0.45 pp |
| passes attempted per team | 280.73 | 274.73 | -6.00 | 2.75 |
| interceptions per team | 53.00 | 52.17 | -0.83 | 1.47 |
| boundaries per team | 31.87 | 31.27 | -0.60 | 1.21 |
| carry goals per team | 0.40 | 0.43 | +0.03 | 0.13 |
| tackle commits per team | 340.80 | 291.83 | -48.97 | 8.10 |
| tackle wrong target share | 39.18% | 26.64% | -12.55 pp | 0.70 pp |
| tackle episode success | 10.27% | 10.49% | +0.22 pp | 0.37 pp |
| tackle hold success | 22.60% | 19.96% | -2.64 pp | 0.83 pp |
| keeper save rate | 14.12% | 14.22% | +0.11 pp | 1.18 pp |
| keeper save on target rate | 18.91% | 19.61% | +0.70 pp | 1.54 pp |
| four point share | 48.95% | 47.63% | -1.32 pp | 2.65 pp |
| median absolute margin | 24.00 | 10.00 | -14.00 | 8.96 |
| within five | 13.33% | 13.33% | +0.00 pp | 12.82 pp |
| team score sd | 16.50 | 17.65 | +1.15 | 3.71 |
| ala minus garvian margin | 23.60 | 17.00 | -6.60 | 9.96 |
| ala margin se | 4.91 | 6.98 | +2.07 | 1.97 |
| ala win share | 100.00% | 90.00% | -10.00 pp | 9.64 pp |
| planned changes per team | 41.20 | 41.13 | -0.07 | 0.51 |
| override exits per team | 3.23 | 3.27 | +0.03 | 0.23 |
| turnovers.fumble | 11.57 | 13.73 | +2.17 | 0.76 |
| turnovers.held ball | 0.00 | 0.00 | +0.00 | 0.00 |
| turnovers.interception | 53.00 | 52.17 | -0.83 | 1.47 |
| turnovers.major | 0.03 | 0.00 | -0.03 | 0.03 |
| turnovers.opponent control | 11.70 | 12.87 | +1.17 | 0.55 |
| turnovers.out of bounds | 31.87 | 31.27 | -0.60 | 1.21 |
| turnovers.play clock | 1.67 | 1.10 | -0.57 | 0.31 |
| turnovers.score restart | 25.17 | 24.60 | -0.57 | 1.00 |
| turnovers.strip | 1.53 | 1.03 | -0.50 | 0.25 |
| turnovers.tackle | 10.07 | 8.00 | -2.07 | 0.89 |
| turnovers.toss timeout | 0.40 | 0.40 | +0.00 | 0.12 |
| turnovers.turnover | 0.53 | 0.57 | +0.03 | 0.12 |
| turnovers.zone violation | 2.67 | 2.97 | +0.30 | 0.45 |
| carries.freeze | 0.10 | 0.07 | -0.03 | 0.07 |
| carries.goal | 0.40 | 0.43 | +0.03 | 0.13 |
| carries.handoff | 2.73 | 2.07 | -0.67 | 0.64 |
| carries.out of bounds | 12.47 | 9.43 | -3.03 | 0.55 |
| carries.pass | 2.83 | 2.97 | +0.13 | 0.29 |
| carries.shot | 26.37 | 25.90 | -0.47 | 1.20 |
| carries.stopped short | 5.30 | 4.80 | -0.50 | 0.59 |
| carries.strip | 0.57 | 0.33 | -0.23 | 0.19 |
| carries.tackle | 3.63 | 3.40 | -0.23 | 0.51 |
| carries.zone violation | 0.50 | 0.60 | +0.10 | 0.16 |
| stretches.end.lost control or expired | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.end.replaced | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch end | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch goal | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch start | 0.00 | 0.00 | +0.00 | 0.00 |

### boundary_guard

15 paired games.

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 90.50 | 99.50 | +9.00 | 6.34 |
| possessions | 152.27 | 143.60 | -8.67 | 2.51 |
| attempt share | 34.94% | 36.54% | +1.60 pp | 0.81 pp |
| pass completion | 76.57% | 77.33% | +0.76 pp | 0.79 pp |
| passes attempted per team | 280.73 | 269.40 | -11.33 | 3.75 |
| interceptions per team | 53.00 | 48.67 | -4.33 | 2.03 |
| boundaries per team | 31.87 | 23.17 | -8.70 | 0.67 |
| carry goals per team | 0.40 | 0.93 | +0.53 | 0.23 |
| tackle commits per team | 340.80 | 332.90 | -7.90 | 7.99 |
| tackle wrong target share | 39.18% | 38.47% | -0.71 pp | 0.69 pp |
| tackle episode success | 10.27% | 10.75% | +0.48 pp | 0.33 pp |
| tackle hold success | 22.60% | 23.61% | +1.01 pp | 0.60 pp |
| keeper save rate | 14.12% | 12.70% | -1.42 pp | 1.22 pp |
| keeper save on target rate | 18.91% | 17.25% | -1.65 pp | 1.55 pp |
| four point share | 48.95% | 44.43% | -4.52 pp | 3.81 pp |
| median absolute margin | 24.00 | 28.00 | +4.00 | 8.34 |
| within five | 13.33% | 6.67% | -6.67 pp | 11.33 pp |
| team score sd | 16.50 | 21.43 | +4.93 | 2.94 |
| ala minus garvian margin | 23.60 | 28.40 | +4.80 | 9.89 |
| ala margin se | 4.91 | 7.79 | +2.88 | 1.43 |
| ala win share | 100.00% | 90.00% | -10.00 pp | 9.42 pp |
| planned changes per team | 41.20 | 41.80 | +0.60 | 0.43 |
| override exits per team | 3.23 | 2.80 | -0.43 | 0.33 |
| turnovers.fumble | 11.57 | 12.03 | +0.47 | 0.70 |
| turnovers.held ball | 0.00 | 0.00 | +0.00 | 0.00 |
| turnovers.interception | 53.00 | 48.67 | -4.33 | 2.03 |
| turnovers.major | 0.03 | 0.03 | +0.00 | 0.04 |
| turnovers.opponent control | 11.70 | 11.87 | +0.17 | 0.89 |
| turnovers.out of bounds | 31.87 | 23.17 | -8.70 | 0.67 |
| turnovers.play clock | 1.67 | 2.00 | +0.33 | 0.26 |
| turnovers.score restart | 25.17 | 28.77 | +3.60 | 1.13 |
| turnovers.strip | 1.53 | 1.67 | +0.13 | 0.21 |
| turnovers.tackle | 10.07 | 9.47 | -0.60 | 0.74 |
| turnovers.toss timeout | 0.40 | 0.30 | -0.10 | 0.11 |
| turnovers.turnover | 0.53 | 0.50 | -0.03 | 0.19 |
| turnovers.zone violation | 2.67 | 2.97 | +0.30 | 0.52 |
| carries.freeze | 0.10 | 0.10 | +0.00 | 0.08 |
| carries.goal | 0.40 | 0.93 | +0.53 | 0.23 |
| carries.handoff | 2.73 | 2.20 | -0.53 | 0.48 |
| carries.out of bounds | 12.47 | 6.50 | -5.97 | 0.44 |
| carries.pass | 2.83 | 3.77 | +0.93 | 0.36 |
| carries.shot | 26.37 | 31.10 | +4.73 | 1.37 |
| carries.stopped short | 5.30 | 4.30 | -1.00 | 0.87 |
| carries.strip | 0.57 | 0.80 | +0.23 | 0.26 |
| carries.tackle | 3.63 | 3.87 | +0.23 | 0.69 |
| carries.zone violation | 0.50 | 0.97 | +0.47 | 0.23 |
| stretches.end.lost control or expired | 0.00 | 0.17 | +0.17 | 0.07 |
| stretches.end.replaced | 0.00 | 0.07 | +0.07 | 0.04 |
| stretches.stretch end | 0.00 | 0.23 | +0.23 | 0.10 |
| stretches.stretch goal | 0.00 | 0.17 | +0.17 | 0.07 |
| stretches.stretch start | 0.00 | 0.23 | +0.23 | 0.10 |

### combined

15 paired games.

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 90.50 | 97.50 | +7.00 | 3.54 |
| possessions | 152.27 | 137.20 | -15.07 | 2.03 |
| attempt share | 34.94% | 35.69% | +0.75 pp | 0.75 pp |
| pass completion | 76.57% | 80.62% | +4.04 pp | 0.44 pp |
| passes attempted per team | 280.73 | 251.60 | -29.13 | 2.66 |
| interceptions per team | 53.00 | 39.70 | -13.30 | 1.63 |
| boundaries per team | 31.87 | 19.90 | -11.97 | 1.02 |
| carry goals per team | 0.40 | 2.13 | +1.73 | 0.38 |
| tackle commits per team | 340.80 | 334.87 | -5.93 | 4.86 |
| tackle wrong target share | 39.18% | 26.12% | -13.06 pp | 0.84 pp |
| tackle episode success | 10.27% | 11.53% | +1.26 pp | 0.31 pp |
| tackle hold success | 22.60% | 21.67% | -0.92 pp | 0.57 pp |
| keeper save rate | 14.12% | 14.79% | +0.67 pp | 1.41 pp |
| keeper save on target rate | 18.91% | 20.23% | +1.33 pp | 1.90 pp |
| four point share | 48.95% | 35.16% | -13.79 pp | 2.40 pp |
| median absolute margin | 24.00 | 22.00 | -2.00 | 7.52 |
| within five | 13.33% | 0.00% | -13.33 pp | 8.34 pp |
| team score sd | 16.50 | 20.06 | +3.56 | 2.05 |
| ala minus garvian margin | 23.60 | 26.30 | +2.70 | 5.78 |
| ala margin se | 4.91 | 7.80 | +2.89 | 1.67 |
| ala win share | 100.00% | 90.00% | -10.00 pp | 9.33 pp |
| planned changes per team | 41.20 | 42.13 | +0.93 | 0.51 |
| override exits per team | 3.23 | 2.40 | -0.83 | 0.23 |
| turnovers.fumble | 11.57 | 16.03 | +4.47 | 0.75 |
| turnovers.held ball | 0.00 | 0.07 | +0.07 | 0.04 |
| turnovers.interception | 53.00 | 39.70 | -13.30 | 1.63 |
| turnovers.major | 0.03 | 0.03 | +0.00 | 0.04 |
| turnovers.opponent control | 11.70 | 12.50 | +0.80 | 0.56 |
| turnovers.out of bounds | 31.87 | 19.90 | -11.97 | 1.02 |
| turnovers.play clock | 1.67 | 1.80 | +0.13 | 0.37 |
| turnovers.score restart | 25.17 | 27.43 | +2.27 | 0.84 |
| turnovers.strip | 1.53 | 1.33 | -0.20 | 0.41 |
| turnovers.tackle | 10.07 | 11.03 | +0.97 | 0.38 |
| turnovers.toss timeout | 0.40 | 0.33 | -0.07 | 0.15 |
| turnovers.turnover | 0.53 | 0.63 | +0.10 | 0.21 |
| turnovers.zone violation | 2.67 | 4.33 | +1.67 | 0.50 |
| carries.freeze | 0.10 | 0.10 | +0.00 | 0.04 |
| carries.goal | 0.40 | 2.13 | +1.73 | 0.38 |
| carries.handoff | 2.73 | 1.87 | -0.87 | 0.48 |
| carries.out of bounds | 12.47 | 2.07 | -10.40 | 0.59 |
| carries.pass | 2.83 | 2.13 | -0.70 | 0.41 |
| carries.shot | 26.37 | 32.93 | +6.57 | 1.35 |
| carries.stopped short | 5.30 | 4.80 | -0.50 | 0.81 |
| carries.strip | 0.57 | 0.47 | -0.10 | 0.19 |
| carries.tackle | 3.63 | 3.37 | -0.27 | 0.62 |
| carries.zone violation | 0.50 | 1.27 | +0.77 | 0.21 |
| stretches.end.lost control or expired | 0.00 | 0.23 | +0.23 | 0.09 |
| stretches.end.replaced | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch end | 0.00 | 0.23 | +0.23 | 0.09 |
| stretches.stretch goal | 0.00 | 0.23 | +0.23 | 0.09 |
| stretches.stretch start | 0.00 | 0.23 | +0.23 | 0.09 |

## Boundary audit

| Cause | Events | Mean absolute launch yaw | Inside aim | Outside aim | Pressured carrier exits | Mean believed edge distance |
|---|---:|---:|---:|---:|---:|---:|
| carrier | 156 | —° | 0 | 0 | 85/156 | 1.48 m |
| deflection | 47 | 0.89° | 47 | 0 | 0/0 | — m |
| held_ball | 556 | —° | 0 | 0 | 132/556 | 1.80 m |
| loose_ball | 7 | —° | 0 | 0 | 0/0 | — m |
| pass | 120 | 0.68° | 120 | 0 | 0/0 | — m |
| shot | 155 | 1.13° | 155 | 0 | 0/0 | — m |

The largest classified group is **held_ball**, with **556** events. The ball crossed while the body was still in bounds. In seed 1 this accounted for 31 of 64 boundary events, often with outward velocity and an aim toward the center. The guard reserves own braking distance and only exempts a route within the whole-ball goal-mouth envelope. This is a behavioral choice.

## Keeper envelope

The audit measured **1014** of **1026** on-target
shots in the OFF arm. **256** (25.25%) were reachable
under the physical release-time upper bound. **123**
(48.05%) of those were saved. Mean release-to-plane time was
**0.34 s**. Projected misses for otherwise on-target
records are reported separately (12).

| Outcome among physically reachable shots | Count |
|---|---:|
| save | 123 |
| no_commit | 90 |
| touch_without_save | 29 |
| late_commit | 12 |
| wrong_side | 2 |

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
