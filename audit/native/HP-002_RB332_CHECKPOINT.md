# OWNER BRIEFING

1. **DESIGN COMPLETE, IMPLEMENTED** for pass clearance, carry finish, fresh takedown evidence and boundary braking. Each runs under its own switch. Keeper reach is a read-only audit.
2. All trial arms use the 0.58 fatigue scale, which averaged 3.25 override exits per team in the calibration pilots. 13 of 180 trial games and 2 of 30 historical replays are recorded.
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
| Pass clearance | DESIGN COMPLETE, IMPLEMENTED. 2 of 30 ON cases finished. |
| Carry finish | DESIGN COMPLETE, IMPLEMENTED. 2 of 30 ON cases finished. |
| Fresh takedown evidence | DESIGN COMPLETE, IMPLEMENTED. 2 of 30 ON cases finished. |
| Boundary diagnosis and guard | DESIGN COMPLETE, IMPLEMENTED. 3 OFF and 2 ON cases. |
| Keeper reach diagnosis | DESIGN COMPLETE, IMPLEMENTED. 3 OFF cases. |
| Combined policy | DESIGN COMPLETE, IMPLEMENTED. 2 of 30 ON cases finished. |

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

The forecast flagged **47 of 81**
measured cases from **81** of the original 1,020
believed-clear interceptions. Classification is evaluated on the admitted
decision view and selected delivery, with the historical population keyed to
the unchanged RB-3.31 trace. The number measures historical flags.

## Paired changes

The parent owner reference ranges are 75–90 for median team score and
100–150 for mean possessions per team. No tuning used the observed trial
outcomes.

### pass_clearance

2 paired games.

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 97.50 | 77.00 | -20.50 | 2.24 |
| possessions | 149.75 | 145.75 | -4.00 | 0.72 |
| attempt share | 37.06% | 34.82% | -2.24 pp | 0.26 pp |
| pass completion | 76.91% | 77.94% | +1.03 pp | 0.56 pp |
| passes attempted per team | 281.50 | 259.50 | -22.00 | 5.06 |
| interceptions per team | 51.25 | 47.00 | -4.25 | 1.26 |
| boundaries per team | 31.75 | 29.25 | -2.50 | 0.72 |
| carry goals per team | 0.25 | 0.25 | +0.00 | 0.36 |
| tackle commits per team | 333.50 | 368.25 | +34.75 | 5.24 |
| tackle wrong target share | 37.56% | 39.17% | +1.62 pp | 2.82 pp |
| tackle episode success | 10.34% | 11.41% | +1.06 pp | 0.90 pp |
| tackle hold success | 23.05% | 24.75% | +1.71 pp | 1.28 pp |
| keeper save rate | 12.02% | 15.76% | +3.74 pp | 2.34 pp |
| keeper save on target rate | 15.94% | 21.31% | +5.37 pp | 1.64 pp |
| four point share | 53.54% | 46.60% | -6.94 pp | 1.32 pp |
| median absolute margin | 22.50 | 29.50 | +7.00 | 8.67 |
| within five | 50.00% | 0.00% | -50.00 pp | 36.14 pp |
| team score sd | 16.66 | 17.33 | +0.67 | 5.21 |
| ala minus garvian margin | 22.50 | -29.50 | -52.00 | 16.62 |
| ala margin se | 17.50 | 5.50 | -12.00 | 6.00 |
| ala win share | 100.00% | 0.00% | -100.00 pp | 0.00 pp |
| planned changes per team | 40.00 | 42.00 | +2.00 | 0.72 |
| override exits per team | 3.25 | 3.25 | +0.00 | 0.36 |
| turnovers.fumble | 10.25 | 15.00 | +4.75 | 2.71 |
| turnovers.interception | 51.25 | 47.00 | -4.25 | 1.26 |
| turnovers.opponent control | 10.75 | 10.75 | +0.00 | 1.45 |
| turnovers.out of bounds | 31.75 | 29.25 | -2.50 | 0.72 |
| turnovers.play clock | 2.25 | 2.25 | +0.00 | 0.00 |
| turnovers.score restart | 27.25 | 22.25 | -5.00 | 0.72 |
| turnovers.strip | 1.50 | 1.00 | -0.50 | 1.08 |
| turnovers.tackle | 11.00 | 12.00 | +1.00 | 1.08 |
| turnovers.toss timeout | 0.25 | 0.25 | +0.00 | 0.36 |
| turnovers.turnover | 0.25 | 1.00 | +0.75 | 0.18 |
| turnovers.zone violation | 1.25 | 2.75 | +1.50 | 1.08 |
| carries.freeze | 0.00 | 0.50 | +0.50 | 0.36 |
| carries.goal | 0.25 | 0.25 | +0.00 | 0.36 |
| carries.handoff | 2.75 | 1.75 | -1.00 | 0.36 |
| carries.out of bounds | 14.50 | 14.25 | -0.25 | 1.63 |
| carries.pass | 3.00 | 4.00 | +1.00 | 0.72 |
| carries.shot | 25.50 | 24.00 | -1.50 | 1.08 |
| carries.stopped short | 4.50 | 6.75 | +2.25 | 0.18 |
| carries.strip | 1.00 | 0.25 | -0.75 | 0.18 |
| carries.tackle | 3.25 | 3.75 | +0.50 | 0.36 |
| carries.zone violation | 0.25 | 0.50 | +0.25 | 0.18 |
| stretches.end.lost control or expired | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.end.replaced | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch end | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch goal | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch start | 0.00 | 0.00 | +0.00 | 0.00 |

### carry_finish

2 paired games.

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 97.50 | 97.50 | +0.00 | 7.64 |
| possessions | 149.75 | 149.25 | -0.50 | 1.45 |
| attempt share | 37.06% | 37.02% | -0.04 pp | 0.00 pp |
| pass completion | 76.91% | 76.93% | +0.02 pp | 0.21 pp |
| passes attempted per team | 281.50 | 275.25 | -6.25 | 1.26 |
| interceptions per team | 51.25 | 50.50 | -0.75 | 2.35 |
| boundaries per team | 31.75 | 31.50 | -0.25 | 1.99 |
| carry goals per team | 0.25 | 2.25 | +2.00 | 1.08 |
| tackle commits per team | 333.50 | 315.00 | -18.50 | 9.03 |
| tackle wrong target share | 37.56% | 40.63% | +3.08 pp | 1.21 pp |
| tackle episode success | 10.34% | 10.08% | -0.27 pp | 0.73 pp |
| tackle hold success | 23.05% | 23.56% | +0.52 pp | 0.46 pp |
| keeper save rate | 12.02% | 15.49% | +3.47 pp | 0.26 pp |
| keeper save on target rate | 15.94% | 21.29% | +5.35 pp | 0.17 pp |
| four point share | 53.54% | 47.28% | -6.26 pp | 9.15 pp |
| median absolute margin | 22.50 | 55.50 | +33.00 | 24.58 |
| within five | 50.00% | 0.00% | -50.00 pp | 36.14 pp |
| team score sd | 16.66 | 35.46 | +18.80 | 14.18 |
| ala minus garvian margin | 22.50 | 55.50 | +33.00 | 24.58 |
| ala margin se | 17.50 | 16.50 | -1.00 | 0.50 |
| ala win share | 100.00% | 100.00% | +0.00 pp | 0.00 pp |
| planned changes per team | 40.00 | 41.75 | +1.75 | 0.18 |
| override exits per team | 3.25 | 3.00 | -0.25 | 0.18 |
| turnovers.fumble | 10.25 | 9.75 | -0.50 | 2.17 |
| turnovers.interception | 51.25 | 50.50 | -0.75 | 2.35 |
| turnovers.opponent control | 10.75 | 14.25 | +3.50 | 0.72 |
| turnovers.out of bounds | 31.75 | 31.50 | -0.25 | 1.99 |
| turnovers.play clock | 2.25 | 1.50 | -0.75 | 0.18 |
| turnovers.score restart | 27.25 | 27.50 | +0.25 | 1.99 |
| turnovers.strip | 1.50 | 1.00 | -0.50 | 0.72 |
| turnovers.tackle | 11.00 | 7.75 | -3.25 | 1.26 |
| turnovers.toss timeout | 0.25 | 0.50 | +0.25 | 0.18 |
| turnovers.turnover | 0.25 | 0.75 | +0.50 | 0.36 |
| turnovers.zone violation | 1.25 | 1.75 | +0.50 | 0.00 |
| carries.freeze | 0.00 | 0.00 | +0.00 | 0.00 |
| carries.goal | 0.25 | 2.25 | +2.00 | 1.08 |
| carries.handoff | 2.75 | 1.50 | -1.25 | 0.18 |
| carries.out of bounds | 14.50 | 8.50 | -6.00 | 0.00 |
| carries.pass | 3.00 | 1.75 | -1.25 | 0.18 |
| carries.shot | 25.50 | 31.00 | +5.50 | 2.89 |
| carries.stopped short | 4.50 | 4.50 | +0.00 | 1.08 |
| carries.strip | 1.00 | 0.50 | -0.50 | 0.36 |
| carries.tackle | 3.25 | 2.75 | -0.50 | 1.45 |
| carries.zone violation | 0.25 | 0.00 | -0.25 | 0.18 |
| stretches.end.lost control or expired | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.end.replaced | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch end | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch goal | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch start | 0.00 | 0.00 | +0.00 | 0.00 |

### fresh_takedown

2 paired games.

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 97.50 | 80.50 | -17.00 | 5.70 |
| possessions | 149.75 | 142.75 | -7.00 | 0.36 |
| attempt share | 37.06% | 31.87% | -5.19 pp | 1.54 pp |
| pass completion | 76.91% | 77.92% | +1.01 pp | 0.47 pp |
| passes attempted per team | 281.50 | 267.25 | -14.25 | 6.32 |
| interceptions per team | 51.25 | 47.00 | -4.25 | 0.54 |
| boundaries per team | 31.75 | 31.00 | -0.75 | 0.54 |
| carry goals per team | 0.25 | 0.25 | +0.00 | 0.36 |
| tackle commits per team | 333.50 | 318.00 | -15.50 | 27.47 |
| tackle wrong target share | 37.56% | 26.34% | -11.22 pp | 2.26 pp |
| tackle episode success | 10.34% | 11.71% | +1.37 pp | 2.02 pp |
| tackle hold success | 23.05% | 20.96% | -2.08 pp | 1.79 pp |
| keeper save rate | 12.02% | 10.43% | -1.59 pp | 2.16 pp |
| keeper save on target rate | 15.94% | 14.53% | -1.41 pp | 1.58 pp |
| four point share | 53.54% | 44.98% | -8.56 pp | 5.65 pp |
| median absolute margin | 22.50 | 4.50 | -18.00 | 15.18 |
| within five | 50.00% | 50.00% | +0.00 pp | 72.28 pp |
| team score sd | 16.66 | 11.73 | -4.93 | 9.29 |
| ala minus garvian margin | 22.50 | 4.50 | -18.00 | 15.18 |
| ala margin se | 17.50 | 3.50 | -14.00 | 7.00 |
| ala win share | 100.00% | 100.00% | +0.00 pp | 0.00 pp |
| planned changes per team | 40.00 | 42.00 | +2.00 | 0.00 |
| override exits per team | 3.25 | 2.50 | -0.75 | 0.18 |
| turnovers.fumble | 10.25 | 12.50 | +2.25 | 1.26 |
| turnovers.interception | 51.25 | 47.00 | -4.25 | 0.54 |
| turnovers.opponent control | 10.75 | 9.50 | -1.25 | 0.18 |
| turnovers.out of bounds | 31.75 | 31.00 | -0.75 | 0.54 |
| turnovers.play clock | 2.25 | 2.00 | -0.25 | 0.18 |
| turnovers.score restart | 27.25 | 23.50 | -3.75 | 1.99 |
| turnovers.strip | 1.50 | 2.00 | +0.50 | 1.08 |
| turnovers.tackle | 11.00 | 10.25 | -0.75 | 2.71 |
| turnovers.toss timeout | 0.25 | 0.00 | -0.25 | 0.18 |
| turnovers.turnover | 0.25 | 0.50 | +0.25 | 0.18 |
| turnovers.zone violation | 1.25 | 2.50 | +1.25 | 0.54 |
| carries.freeze | 0.00 | 0.25 | +0.25 | 0.18 |
| carries.goal | 0.25 | 0.25 | +0.00 | 0.36 |
| carries.handoff | 2.75 | 1.00 | -1.75 | 0.18 |
| carries.out of bounds | 14.50 | 9.25 | -5.25 | 0.54 |
| carries.pass | 3.00 | 1.75 | -1.25 | 0.18 |
| carries.shot | 25.50 | 23.50 | -2.00 | 3.25 |
| carries.stopped short | 4.50 | 3.25 | -1.25 | 0.54 |
| carries.strip | 1.00 | 0.00 | -1.00 | 0.00 |
| carries.tackle | 3.25 | 2.75 | -0.50 | 1.45 |
| carries.zone violation | 0.25 | 0.75 | +0.50 | 0.36 |
| stretches.end.lost control or expired | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.end.replaced | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch end | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch goal | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch start | 0.00 | 0.00 | +0.00 | 0.00 |

### boundary_guard

2 paired games.

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 97.50 | 108.00 | +10.50 | 1.89 |
| possessions | 149.75 | 148.75 | -1.00 | 0.36 |
| attempt share | 37.06% | 36.13% | -0.93 pp | 1.40 pp |
| pass completion | 76.91% | 77.89% | +0.98 pp | 1.01 pp |
| passes attempted per team | 281.50 | 272.50 | -9.00 | 15.18 |
| interceptions per team | 51.25 | 51.25 | +0.00 | 1.08 |
| boundaries per team | 31.75 | 20.50 | -11.25 | 0.90 |
| carry goals per team | 0.25 | 2.50 | +2.25 | 0.18 |
| tackle commits per team | 333.50 | 354.00 | +20.50 | 31.08 |
| tackle wrong target share | 37.56% | 39.12% | +1.57 pp | 0.50 pp |
| tackle episode success | 10.34% | 10.95% | +0.60 pp | 1.63 pp |
| tackle hold success | 23.05% | 23.97% | +0.92 pp | 2.62 pp |
| keeper save rate | 12.02% | 12.44% | +0.42 pp | 3.63 pp |
| keeper save on target rate | 15.94% | 16.13% | +0.19 pp | 4.13 pp |
| four point share | 53.54% | 38.53% | -15.01 pp | 5.99 pp |
| median absolute margin | 22.50 | 26.00 | +3.50 | 21.32 |
| within five | 50.00% | 0.00% | -50.00 pp | 36.14 pp |
| team score sd | 16.66 | 16.57 | -0.09 | 12.31 |
| ala minus garvian margin | 22.50 | 26.00 | +3.50 | 21.32 |
| ala margin se | 17.50 | 12.00 | -5.50 | 2.75 |
| ala win share | 100.00% | 100.00% | +0.00 pp | 0.00 pp |
| planned changes per team | 40.00 | 42.50 | +2.50 | 0.36 |
| override exits per team | 3.25 | 1.50 | -1.75 | 0.54 |
| turnovers.fumble | 10.25 | 13.75 | +3.50 | 0.72 |
| turnovers.interception | 51.25 | 51.25 | +0.00 | 1.08 |
| turnovers.opponent control | 10.75 | 10.75 | +0.00 | 0.72 |
| turnovers.out of bounds | 31.75 | 20.50 | -11.25 | 0.90 |
| turnovers.play clock | 2.25 | 2.00 | -0.25 | 0.18 |
| turnovers.score restart | 27.25 | 32.25 | +5.00 | 0.72 |
| turnovers.strip | 1.50 | 0.75 | -0.75 | 0.54 |
| turnovers.tackle | 11.00 | 11.25 | +0.25 | 3.07 |
| turnovers.toss timeout | 0.25 | 0.00 | -0.25 | 0.18 |
| turnovers.turnover | 0.25 | 0.75 | +0.50 | 0.36 |
| turnovers.zone violation | 1.25 | 3.50 | +2.25 | 0.90 |
| carries.freeze | 0.00 | 0.25 | +0.25 | 0.18 |
| carries.goal | 0.25 | 2.50 | +2.25 | 0.18 |
| carries.handoff | 2.75 | 2.50 | -0.25 | 0.54 |
| carries.out of bounds | 14.50 | 5.75 | -8.75 | 0.90 |
| carries.pass | 3.00 | 3.75 | +0.75 | 0.18 |
| carries.shot | 25.50 | 34.00 | +8.50 | 2.53 |
| carries.stopped short | 4.50 | 3.00 | -1.50 | 1.08 |
| carries.strip | 1.00 | 0.50 | -0.50 | 0.00 |
| carries.tackle | 3.25 | 3.75 | +0.50 | 2.53 |
| carries.zone violation | 0.25 | 1.50 | +1.25 | 0.90 |
| stretches.end.lost control or expired | 0.00 | 0.75 | +0.75 | 0.18 |
| stretches.end.replaced | 0.00 | 0.25 | +0.25 | 0.18 |
| stretches.stretch end | 0.00 | 1.00 | +1.00 | 0.00 |
| stretches.stretch goal | 0.00 | 0.75 | +0.75 | 0.18 |
| stretches.stretch start | 0.00 | 1.00 | +1.00 | 0.00 |

### combined

2 paired games.

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 97.50 | 102.00 | +4.50 | 16.58 |
| possessions | 149.75 | 143.00 | -6.75 | 4.52 |
| attempt share | 37.06% | 36.71% | -0.35 pp | 3.19 pp |
| pass completion | 76.91% | 80.27% | +3.36 pp | 1.43 pp |
| passes attempted per team | 281.50 | 263.50 | -18.00 | 8.31 |
| interceptions per team | 51.25 | 43.50 | -7.75 | 3.43 |
| boundaries per team | 31.75 | 22.00 | -9.75 | 3.79 |
| carry goals per team | 0.25 | 0.50 | +0.25 | 0.54 |
| tackle commits per team | 333.50 | 308.00 | -25.50 | 12.29 |
| tackle wrong target share | 37.56% | 26.54% | -11.01 pp | 1.79 pp |
| tackle episode success | 10.34% | 12.99% | +2.64 pp | 1.52 pp |
| tackle hold success | 23.05% | 24.54% | +1.49 pp | 1.80 pp |
| keeper save rate | 12.02% | 13.52% | +1.50 pp | 3.61 pp |
| keeper save on target rate | 15.94% | 19.30% | +3.36 pp | 4.83 pp |
| four point share | 53.54% | 34.74% | -18.80 pp | 1.70 pp |
| median absolute margin | 22.50 | 34.00 | +11.50 | 6.14 |
| within five | 50.00% | 0.00% | -50.00 pp | 36.14 pp |
| team score sd | 16.66 | 30.75 | +14.09 | 5.25 |
| ala minus garvian margin | 22.50 | 9.00 | -13.50 | 11.93 |
| ala margin se | 17.50 | 34.00 | +16.50 | 8.25 |
| ala win share | 100.00% | 50.00% | -50.00 pp | 36.14 pp |
| planned changes per team | 40.00 | 42.25 | +2.25 | 0.18 |
| override exits per team | 3.25 | 2.75 | -0.50 | 0.72 |
| turnovers.fumble | 10.25 | 14.00 | +3.75 | 3.43 |
| turnovers.interception | 51.25 | 43.50 | -7.75 | 3.43 |
| turnovers.opponent control | 10.75 | 11.00 | +0.25 | 1.99 |
| turnovers.out of bounds | 31.75 | 22.00 | -9.75 | 3.79 |
| turnovers.play clock | 2.25 | 1.50 | -0.75 | 0.90 |
| turnovers.score restart | 27.25 | 31.00 | +3.75 | 3.79 |
| turnovers.strip | 1.50 | 0.75 | -0.75 | 0.90 |
| turnovers.tackle | 11.00 | 12.25 | +1.25 | 0.54 |
| turnovers.toss timeout | 0.25 | 0.25 | +0.00 | 0.36 |
| turnovers.turnover | 0.25 | 0.75 | +0.50 | 0.36 |
| turnovers.zone violation | 1.25 | 4.00 | +2.75 | 1.63 |
| carries.freeze | 0.00 | 0.00 | +0.00 | 0.00 |
| carries.goal | 0.25 | 0.50 | +0.25 | 0.54 |
| carries.handoff | 2.75 | 2.75 | +0.00 | 0.72 |
| carries.out of bounds | 14.50 | 1.75 | -12.75 | 2.35 |
| carries.pass | 3.00 | 1.75 | -1.25 | 0.90 |
| carries.shot | 25.50 | 39.50 | +14.00 | 1.81 |
| carries.stopped short | 4.50 | 6.50 | +2.00 | 3.25 |
| carries.strip | 1.00 | 0.75 | -0.25 | 0.54 |
| carries.tackle | 3.25 | 3.75 | +0.50 | 2.89 |
| carries.zone violation | 0.25 | 1.00 | +0.75 | 0.18 |
| stretches.end.lost control or expired | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.end.replaced | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch end | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch goal | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch start | 0.00 | 0.00 | +0.00 | 0.00 |

## Boundary audit

| Cause | Events | Mean absolute launch yaw | Inside aim | Outside aim | Pressured carrier exits | Mean believed edge distance |
|---|---:|---:|---:|---:|---:|---:|
| carrier | 33 | —° | 0 | 0 | 18/33 | 1.57 m |
| deflection | 9 | 0.71° | 9 | 0 | 0/0 | — m |
| held_ball | 106 | —° | 0 | 0 | 15/106 | 1.81 m |
| loose_ball | 4 | —° | 0 | 0 | 0/0 | — m |
| pass | 19 | 0.50° | 19 | 0 | 0/0 | — m |
| shot | 33 | 0.96° | 33 | 0 | 0/0 | — m |

The largest classified group is **held_ball**, with **106** events. The ball crossed while the body was still in bounds. In seed 1 this accounted for 31 of 64 boundary events, often with outward velocity and an aim toward the center. The guard reserves own braking distance and only exempts a route within the whole-ball goal-mouth envelope. This is a behavioral choice.

## Keeper envelope

The audit measured **205** of **208** on-target
shots in the OFF arm. **46** (22.44%) were reachable
under the physical release-time upper bound. **24**
(52.17%) of those were saved. Mean release-to-plane time was
**0.34 s**. Projected misses for otherwise on-target
records are reported separately (3).

| Outcome among physically reachable shots | Count |
|---|---:|
| save | 24 |
| touch_without_save | 5 |
| no_commit | 15 |
| late_commit | 2 |

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
