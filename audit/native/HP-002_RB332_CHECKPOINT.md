# OWNER BRIEFING

1. **DESIGN COMPLETE, IMPLEMENTED** for pass clearance, carry finish, fresh takedown evidence and boundary braking. Each runs under its own switch. Keeper reach is a read-only audit.
2. All trial arms use the 0.58 fatigue scale, which averaged 3.25 override exits per team in the calibration pilots. 60 of 180 trial games and 9 of 30 historical replays are recorded.
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
| Pass clearance | DESIGN COMPLETE, IMPLEMENTED. 10 of 30 ON cases finished. |
| Carry finish | DESIGN COMPLETE, IMPLEMENTED. 10 of 30 ON cases finished. |
| Fresh takedown evidence | DESIGN COMPLETE, IMPLEMENTED. 10 of 30 ON cases finished. |
| Boundary diagnosis and guard | DESIGN COMPLETE, IMPLEMENTED. 10 OFF and 10 ON cases. |
| Keeper reach diagnosis | DESIGN COMPLETE, IMPLEMENTED. 10 OFF cases. |
| Combined policy | DESIGN COMPLETE, IMPLEMENTED. 10 of 30 ON cases finished. |

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

The forecast flagged **173 of 291**
measured cases from **291** of the original 1,020
believed-clear interceptions. Classification is evaluated on the admitted
decision view and selected delivery, with the historical population keyed to
the unchanged RB-3.31 trace. The number measures historical flags.

## Paired changes

The parent owner reference ranges are 75–90 for median team score and
100–150 for mean possessions per team. No tuning used the observed trial
outcomes.

### pass_clearance

10 paired games.

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 92.50 | 78.50 | -14.00 | 4.24 |
| possessions | 153.05 | 139.85 | -13.20 | 2.52 |
| attempt share | 35.18% | 35.79% | +0.60 pp | 0.93 pp |
| pass completion | 76.61% | 80.06% | +3.45 pp | 0.51 pp |
| passes attempted per team | 282.85 | 255.80 | -27.05 | 5.15 |
| interceptions per team | 52.50 | 41.55 | -10.95 | 1.42 |
| boundaries per team | 31.90 | 30.85 | -1.05 | 1.06 |
| carry goals per team | 0.30 | 0.65 | +0.35 | 0.25 |
| tackle commits per team | 351.10 | 363.05 | +11.95 | 10.92 |
| tackle wrong target share | 39.65% | 38.11% | -1.54 pp | 1.09 pp |
| tackle episode success | 10.31% | 11.38% | +1.07 pp | 0.39 pp |
| tackle hold success | 22.73% | 24.19% | +1.46 pp | 0.93 pp |
| keeper save rate | 14.46% | 12.97% | -1.48 pp | 2.16 pp |
| keeper save on target rate | 19.14% | 18.03% | -1.11 pp | 2.76 pp |
| four point share | 50.33% | 46.02% | -4.32 pp | 1.07 pp |
| median absolute margin | 24.50 | 30.00 | +5.50 | 6.76 |
| within five | 20.00% | 10.00% | -10.00 pp | 17.04 pp |
| team score sd | 16.16 | 19.82 | +3.65 | 3.71 |
| ala minus garvian margin | 23.60 | 9.80 | -13.80 | 10.86 |
| ala margin se | 4.91 | 10.29 | +5.39 | 1.65 |
| ala win share | 100.00% | 50.00% | -50.00 pp | 16.28 pp |
| planned changes per team | 41.55 | 42.40 | +0.85 | 0.56 |
| override exits per team | 2.85 | 2.30 | -0.55 | 0.34 |
| turnovers.fumble | 11.95 | 12.80 | +0.85 | 1.21 |
| turnovers.held ball | 0.00 | 0.00 | +0.00 | 0.00 |
| turnovers.interception | 52.50 | 41.55 | -10.95 | 1.42 |
| turnovers.major | 0.05 | 0.00 | -0.05 | 0.05 |
| turnovers.opponent control | 11.75 | 10.70 | -1.05 | 0.75 |
| turnovers.out of bounds | 31.90 | 30.85 | -1.05 | 1.06 |
| turnovers.play clock | 1.75 | 2.05 | +0.30 | 0.39 |
| turnovers.score restart | 25.55 | 22.30 | -3.25 | 1.25 |
| turnovers.strip | 1.70 | 1.60 | -0.10 | 0.40 |
| turnovers.tackle | 10.40 | 11.80 | +1.40 | 0.98 |
| turnovers.toss timeout | 0.40 | 0.75 | +0.35 | 0.29 |
| turnovers.turnover | 0.50 | 0.50 | +0.00 | 0.18 |
| turnovers.zone violation | 2.55 | 2.85 | +0.30 | 0.47 |
| carries.freeze | 0.00 | 0.20 | +0.20 | 0.10 |
| carries.goal | 0.30 | 0.65 | +0.35 | 0.25 |
| carries.handoff | 2.45 | 1.45 | -1.00 | 0.42 |
| carries.out of bounds | 12.95 | 12.20 | -0.75 | 0.64 |
| carries.pass | 2.60 | 3.60 | +1.00 | 0.54 |
| carries.shot | 26.65 | 25.05 | -1.60 | 1.66 |
| carries.stopped short | 5.05 | 5.40 | +0.35 | 0.74 |
| carries.strip | 0.70 | 0.35 | -0.35 | 0.29 |
| carries.tackle | 4.00 | 4.30 | +0.30 | 0.69 |
| carries.zone violation | 0.55 | 0.35 | -0.20 | 0.17 |
| stretches.end.lost control or expired | 0.00 | 0.05 | +0.05 | 0.05 |
| stretches.end.replaced | 0.00 | 0.05 | +0.05 | 0.05 |
| stretches.stretch end | 0.00 | 0.10 | +0.10 | 0.09 |
| stretches.stretch goal | 0.00 | 0.05 | +0.05 | 0.05 |
| stretches.stretch start | 0.00 | 0.10 | +0.10 | 0.09 |

### carry_finish

10 paired games.

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 92.50 | 106.50 | +14.00 | 3.57 |
| possessions | 153.05 | 150.10 | -2.95 | 2.16 |
| attempt share | 35.18% | 35.44% | +0.26 pp | 0.59 pp |
| pass completion | 76.61% | 77.16% | +0.55 pp | 0.43 pp |
| passes attempted per team | 282.85 | 276.50 | -6.35 | 2.90 |
| interceptions per team | 52.50 | 50.75 | -1.75 | 1.60 |
| boundaries per team | 31.90 | 28.85 | -3.05 | 1.62 |
| carry goals per team | 0.30 | 2.20 | +1.90 | 0.26 |
| tackle commits per team | 351.10 | 339.55 | -11.55 | 8.85 |
| tackle wrong target share | 39.65% | 40.61% | +0.97 pp | 1.17 pp |
| tackle episode success | 10.31% | 9.92% | -0.39 pp | 0.39 pp |
| tackle hold success | 22.73% | 22.57% | -0.16 pp | 0.78 pp |
| keeper save rate | 14.46% | 14.43% | -0.02 pp | 1.41 pp |
| keeper save on target rate | 19.14% | 20.11% | +0.96 pp | 1.92 pp |
| four point share | 50.33% | 39.37% | -10.97 pp | 3.18 pp |
| median absolute margin | 24.50 | 44.00 | +19.50 | 12.61 |
| within five | 20.00% | 0.00% | -20.00 pp | 12.45 pp |
| team score sd | 16.16 | 26.44 | +10.28 | 3.31 |
| ala minus garvian margin | 23.60 | 44.70 | +21.10 | 7.80 |
| ala margin se | 4.91 | 7.00 | +2.10 | 1.51 |
| ala win share | 100.00% | 100.00% | +0.00 pp | 0.00 pp |
| planned changes per team | 41.55 | 42.25 | +0.70 | 0.43 |
| override exits per team | 2.85 | 2.60 | -0.25 | 0.24 |
| turnovers.fumble | 11.95 | 12.45 | +0.50 | 1.01 |
| turnovers.held ball | 0.00 | 0.00 | +0.00 | 0.00 |
| turnovers.interception | 52.50 | 50.75 | -1.75 | 1.60 |
| turnovers.major | 0.05 | 0.00 | -0.05 | 0.05 |
| turnovers.opponent control | 11.75 | 12.60 | +0.85 | 0.74 |
| turnovers.out of bounds | 31.90 | 28.85 | -3.05 | 1.62 |
| turnovers.play clock | 1.75 | 1.55 | -0.20 | 0.29 |
| turnovers.score restart | 25.55 | 28.10 | +2.55 | 0.87 |
| turnovers.strip | 1.70 | 1.20 | -0.50 | 0.29 |
| turnovers.tackle | 10.40 | 9.15 | -1.25 | 0.99 |
| turnovers.toss timeout | 0.40 | 0.45 | +0.05 | 0.16 |
| turnovers.turnover | 0.50 | 0.70 | +0.20 | 0.20 |
| turnovers.zone violation | 2.55 | 2.10 | -0.45 | 0.47 |
| carries.freeze | 0.00 | 0.00 | +0.00 | 0.00 |
| carries.goal | 0.30 | 2.20 | +1.90 | 0.26 |
| carries.handoff | 2.45 | 1.15 | -1.30 | 0.54 |
| carries.out of bounds | 12.95 | 7.10 | -5.85 | 0.73 |
| carries.pass | 2.60 | 1.90 | -0.70 | 0.47 |
| carries.shot | 26.65 | 33.70 | +7.05 | 1.80 |
| carries.stopped short | 5.05 | 4.60 | -0.45 | 0.69 |
| carries.strip | 0.70 | 0.45 | -0.25 | 0.23 |
| carries.tackle | 4.00 | 2.30 | -1.70 | 0.53 |
| carries.zone violation | 0.55 | 0.15 | -0.40 | 0.12 |
| stretches.end.lost control or expired | 0.00 | 0.20 | +0.20 | 0.08 |
| stretches.end.replaced | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch end | 0.00 | 0.20 | +0.20 | 0.08 |
| stretches.stretch goal | 0.00 | 0.20 | +0.20 | 0.08 |
| stretches.stretch start | 0.00 | 0.20 | +0.20 | 0.08 |

### fresh_takedown

10 paired games.

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 92.50 | 87.50 | -5.00 | 3.66 |
| possessions | 153.05 | 151.55 | -1.50 | 2.20 |
| attempt share | 35.18% | 32.99% | -2.19 pp | 0.99 pp |
| pass completion | 76.61% | 75.93% | -0.69 pp | 0.37 pp |
| passes attempted per team | 282.85 | 277.50 | -5.35 | 2.26 |
| interceptions per team | 52.50 | 52.80 | +0.30 | 1.29 |
| boundaries per team | 31.90 | 31.00 | -0.90 | 1.29 |
| carry goals per team | 0.30 | 0.30 | +0.00 | 0.15 |
| tackle commits per team | 351.10 | 305.00 | -46.10 | 11.77 |
| tackle wrong target share | 39.65% | 26.95% | -12.70 pp | 0.89 pp |
| tackle episode success | 10.31% | 10.72% | +0.41 pp | 0.51 pp |
| tackle hold success | 22.73% | 20.27% | -2.45 pp | 1.09 pp |
| keeper save rate | 14.46% | 14.85% | +0.40 pp | 1.64 pp |
| keeper save on target rate | 19.14% | 20.15% | +1.01 pp | 2.16 pp |
| four point share | 50.33% | 48.90% | -1.43 pp | 2.04 pp |
| median absolute margin | 24.50 | 12.50 | -12.00 | 10.92 |
| within five | 20.00% | 10.00% | -10.00 pp | 16.62 pp |
| team score sd | 16.16 | 15.46 | -0.70 | 4.93 |
| ala minus garvian margin | 23.60 | 17.00 | -6.60 | 9.88 |
| ala margin se | 4.91 | 6.98 | +2.07 | 1.97 |
| ala win share | 100.00% | 90.00% | -10.00 pp | 9.47 pp |
| planned changes per team | 41.55 | 41.45 | -0.10 | 0.66 |
| override exits per team | 2.85 | 2.95 | +0.10 | 0.33 |
| turnovers.fumble | 11.95 | 14.20 | +2.25 | 0.97 |
| turnovers.held ball | 0.00 | 0.00 | +0.00 | 0.00 |
| turnovers.interception | 52.50 | 52.80 | +0.30 | 1.29 |
| turnovers.major | 0.05 | 0.00 | -0.05 | 0.05 |
| turnovers.opponent control | 11.75 | 12.25 | +0.50 | 0.66 |
| turnovers.out of bounds | 31.90 | 31.00 | -0.90 | 1.29 |
| turnovers.play clock | 1.75 | 1.20 | -0.55 | 0.32 |
| turnovers.score restart | 25.55 | 24.15 | -1.40 | 0.94 |
| turnovers.strip | 1.70 | 1.30 | -0.40 | 0.37 |
| turnovers.tackle | 10.40 | 8.40 | -2.00 | 1.34 |
| turnovers.toss timeout | 0.40 | 0.55 | +0.15 | 0.18 |
| turnovers.turnover | 0.50 | 0.70 | +0.20 | 0.13 |
| turnovers.zone violation | 2.55 | 2.90 | +0.35 | 0.53 |
| carries.freeze | 0.00 | 0.10 | +0.10 | 0.06 |
| carries.goal | 0.30 | 0.30 | +0.00 | 0.15 |
| carries.handoff | 2.45 | 2.15 | -0.30 | 0.77 |
| carries.out of bounds | 12.95 | 9.25 | -3.70 | 0.74 |
| carries.pass | 2.60 | 2.65 | +0.05 | 0.39 |
| carries.shot | 26.65 | 24.80 | -1.85 | 1.48 |
| carries.stopped short | 5.05 | 4.40 | -0.65 | 0.71 |
| carries.strip | 0.70 | 0.35 | -0.35 | 0.27 |
| carries.tackle | 4.00 | 2.95 | -1.05 | 0.54 |
| carries.zone violation | 0.55 | 0.55 | +0.00 | 0.20 |
| stretches.end.lost control or expired | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.end.replaced | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch end | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch goal | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch start | 0.00 | 0.00 | +0.00 | 0.00 |

### boundary_guard

10 paired games.

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 92.50 | 101.00 | +8.50 | 5.23 |
| possessions | 153.05 | 144.85 | -8.20 | 2.43 |
| attempt share | 35.18% | 35.66% | +0.47 pp | 0.83 pp |
| pass completion | 76.61% | 77.36% | +0.75 pp | 0.72 pp |
| passes attempted per team | 282.85 | 271.40 | -11.45 | 4.06 |
| interceptions per team | 52.50 | 49.55 | -2.95 | 2.03 |
| boundaries per team | 31.90 | 22.20 | -9.70 | 0.78 |
| carry goals per team | 0.30 | 1.10 | +0.80 | 0.31 |
| tackle commits per team | 351.10 | 348.85 | -2.25 | 11.05 |
| tackle wrong target share | 39.65% | 39.47% | -0.17 pp | 0.82 pp |
| tackle episode success | 10.31% | 10.68% | +0.37 pp | 0.46 pp |
| tackle hold success | 22.73% | 23.79% | +1.06 pp | 0.77 pp |
| keeper save rate | 14.46% | 13.01% | -1.44 pp | 1.54 pp |
| keeper save on target rate | 19.14% | 17.26% | -1.88 pp | 1.91 pp |
| four point share | 50.33% | 43.13% | -7.21 pp | 2.98 pp |
| median absolute margin | 24.50 | 33.00 | +8.50 | 10.15 |
| within five | 20.00% | 10.00% | -10.00 pp | 16.45 pp |
| team score sd | 16.16 | 22.85 | +6.69 | 4.20 |
| ala minus garvian margin | 23.60 | 28.40 | +4.80 | 10.14 |
| ala margin se | 4.91 | 7.79 | +2.88 | 1.44 |
| ala win share | 100.00% | 90.00% | -10.00 pp | 9.71 pp |
| planned changes per team | 41.55 | 42.45 | +0.90 | 0.52 |
| override exits per team | 2.85 | 2.30 | -0.55 | 0.42 |
| turnovers.fumble | 11.95 | 12.60 | +0.65 | 0.89 |
| turnovers.held ball | 0.00 | 0.00 | +0.00 | 0.00 |
| turnovers.interception | 52.50 | 49.55 | -2.95 | 2.03 |
| turnovers.major | 0.05 | 0.00 | -0.05 | 0.05 |
| turnovers.opponent control | 11.75 | 11.60 | -0.15 | 1.02 |
| turnovers.out of bounds | 31.90 | 22.20 | -9.70 | 0.78 |
| turnovers.play clock | 1.75 | 2.20 | +0.45 | 0.31 |
| turnovers.score restart | 25.55 | 29.25 | +3.70 | 1.06 |
| turnovers.strip | 1.70 | 1.55 | -0.15 | 0.27 |
| turnovers.tackle | 10.40 | 9.65 | -0.75 | 0.93 |
| turnovers.toss timeout | 0.40 | 0.30 | -0.10 | 0.12 |
| turnovers.turnover | 0.50 | 0.60 | +0.10 | 0.22 |
| turnovers.zone violation | 2.55 | 3.15 | +0.60 | 0.66 |
| carries.freeze | 0.00 | 0.15 | +0.15 | 0.07 |
| carries.goal | 0.30 | 1.10 | +0.80 | 0.31 |
| carries.handoff | 2.45 | 2.30 | -0.15 | 0.65 |
| carries.out of bounds | 12.95 | 6.15 | -6.80 | 0.56 |
| carries.pass | 2.60 | 4.05 | +1.45 | 0.48 |
| carries.shot | 26.65 | 30.70 | +4.05 | 1.41 |
| carries.stopped short | 5.05 | 4.40 | -0.65 | 1.25 |
| carries.strip | 0.70 | 0.85 | +0.15 | 0.36 |
| carries.tackle | 4.00 | 3.90 | -0.10 | 1.01 |
| carries.zone violation | 0.55 | 1.05 | +0.50 | 0.31 |
| stretches.end.lost control or expired | 0.00 | 0.25 | +0.25 | 0.10 |
| stretches.end.replaced | 0.00 | 0.10 | +0.10 | 0.06 |
| stretches.stretch end | 0.00 | 0.35 | +0.35 | 0.14 |
| stretches.stretch goal | 0.00 | 0.25 | +0.25 | 0.10 |
| stretches.stretch start | 0.00 | 0.35 | +0.35 | 0.14 |

### combined

10 paired games.

| Metric | OFF | ON | Paired change | SE |
|---|---:|---:|---:|---:|
| median team score | 92.50 | 98.50 | +6.00 | 4.57 |
| possessions | 153.05 | 137.40 | -15.65 | 2.49 |
| attempt share | 35.18% | 35.08% | -0.10 pp | 0.82 pp |
| pass completion | 76.61% | 80.62% | +4.01 pp | 0.47 pp |
| passes attempted per team | 282.85 | 255.15 | -27.70 | 3.54 |
| interceptions per team | 52.50 | 40.15 | -12.35 | 1.98 |
| boundaries per team | 31.90 | 19.80 | -12.10 | 1.26 |
| carry goals per team | 0.30 | 1.90 | +1.60 | 0.35 |
| tackle commits per team | 351.10 | 345.20 | -5.90 | 6.38 |
| tackle wrong target share | 39.65% | 26.45% | -13.20 pp | 0.90 pp |
| tackle episode success | 10.31% | 11.46% | +1.15 pp | 0.44 pp |
| tackle hold success | 22.73% | 21.76% | -0.97 pp | 0.75 pp |
| keeper save rate | 14.46% | 13.88% | -0.58 pp | 1.81 pp |
| keeper save on target rate | 19.14% | 19.00% | -0.14 pp | 2.46 pp |
| four point share | 50.33% | 36.02% | -14.32 pp | 2.20 pp |
| median absolute margin | 24.50 | 32.00 | +7.50 | 8.80 |
| within five | 20.00% | 0.00% | -20.00 pp | 12.45 pp |
| team score sd | 16.16 | 22.71 | +6.55 | 2.66 |
| ala minus garvian margin | 23.60 | 26.30 | +2.70 | 5.59 |
| ala margin se | 4.91 | 7.80 | +2.89 | 1.68 |
| ala win share | 100.00% | 90.00% | -10.00 pp | 9.20 pp |
| planned changes per team | 41.55 | 42.45 | +0.90 | 0.72 |
| override exits per team | 2.85 | 2.05 | -0.80 | 0.31 |
| turnovers.fumble | 11.95 | 16.20 | +4.25 | 0.77 |
| turnovers.held ball | 0.00 | 0.10 | +0.10 | 0.06 |
| turnovers.interception | 52.50 | 40.15 | -12.35 | 1.98 |
| turnovers.major | 0.05 | 0.00 | -0.05 | 0.05 |
| turnovers.opponent control | 11.75 | 11.55 | -0.20 | 0.72 |
| turnovers.out of bounds | 31.90 | 19.80 | -12.10 | 1.26 |
| turnovers.play clock | 1.75 | 1.75 | +0.00 | 0.36 |
| turnovers.score restart | 25.55 | 27.80 | +2.25 | 1.12 |
| turnovers.strip | 1.70 | 1.60 | -0.10 | 0.55 |
| turnovers.tackle | 10.40 | 11.70 | +1.30 | 0.49 |
| turnovers.toss timeout | 0.40 | 0.25 | -0.15 | 0.14 |
| turnovers.turnover | 0.50 | 0.65 | +0.15 | 0.22 |
| turnovers.zone violation | 2.55 | 3.85 | +1.30 | 0.51 |
| carries.freeze | 0.00 | 0.05 | +0.05 | 0.05 |
| carries.goal | 0.30 | 1.90 | +1.60 | 0.35 |
| carries.handoff | 2.45 | 1.90 | -0.55 | 0.60 |
| carries.out of bounds | 12.95 | 1.95 | -11.00 | 0.66 |
| carries.pass | 2.60 | 1.80 | -0.80 | 0.54 |
| carries.shot | 26.65 | 32.60 | +5.95 | 1.69 |
| carries.stopped short | 5.05 | 5.15 | +0.10 | 1.20 |
| carries.strip | 0.70 | 0.55 | -0.15 | 0.27 |
| carries.tackle | 4.00 | 3.40 | -0.60 | 0.82 |
| carries.zone violation | 0.55 | 1.05 | +0.50 | 0.28 |
| stretches.end.lost control or expired | 0.00 | 0.20 | +0.20 | 0.10 |
| stretches.end.replaced | 0.00 | 0.00 | +0.00 | 0.00 |
| stretches.stretch end | 0.00 | 0.20 | +0.20 | 0.10 |
| stretches.stretch goal | 0.00 | 0.20 | +0.20 | 0.10 |
| stretches.stretch start | 0.00 | 0.20 | +0.20 | 0.10 |

## Boundary audit

| Cause | Events | Mean absolute launch yaw | Inside aim | Outside aim | Pressured carrier exits | Mean believed edge distance |
|---|---:|---:|---:|---:|---:|---:|
| carrier | 105 | —° | 0 | 0 | 57/105 | 1.40 m |
| deflection | 31 | 0.81° | 31 | 0 | 0/0 | — m |
| held_ball | 372 | —° | 0 | 0 | 87/372 | 1.78 m |
| loose_ball | 6 | —° | 0 | 0 | 0/0 | — m |
| pass | 80 | 0.59° | 80 | 0 | 0/0 | — m |
| shot | 101 | 0.97° | 101 | 0 | 0/0 | — m |

The largest classified group is **held_ball**, with **372** events. The ball crossed while the body was still in bounds. In seed 1 this accounted for 31 of 64 boundary events, often with outward velocity and an aim toward the center. The guard reserves own braking distance and only exempts a route within the whole-ball goal-mouth envelope. This is a behavioral choice.

## Keeper envelope

The audit measured **694** of **700** on-target
shots in the OFF arm. **187** (26.95%) were reachable
under the physical release-time upper bound. **82**
(43.85%) of those were saved. Mean release-to-plane time was
**0.34 s**. Projected misses for otherwise on-target
records are reported separately (6).

| Outcome among physically reachable shots | Count |
|---|---:|
| save | 82 |
| no_commit | 75 |
| touch_without_save | 21 |
| late_commit | 9 |

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
