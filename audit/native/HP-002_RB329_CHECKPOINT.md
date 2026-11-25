# OWNER BRIEFING

1. **DESIGN COMPLETE, IMPLEMENTED, TESTED.** RB-3.29 completed 150 matches with the read-only ledger and all five individual rotation profiles.
2. The simulator exports reconciled JSON and CSV box scores. With the ledger on, R1 reproduced RB-3.28, and all three required identity runs matched.
3. R1 averaged 32.18 starter minutes. Slowing the rates cut substitutions and put each slower profile outside the allowed starter-minute range.
4. The full pool still diverged from the season reference. Median absolute margin was 24 versus 13, and 11.33% of games finished within five points versus 23%.
5. Keep the five profiles available for the owner’s rhythm decision. Use the scoring-rate, matchup and four-point-throw findings to choose the next experiment.

## Standing gates

 a) pytest -q b1 native, full suite, after the last change.

 b) Legacy hash guards unchanged (six rows).

 c) Determinism.

 d) Compatibility: real seed 1 = 57-76, trace 44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072, state 046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d.

 e) CORE identity (fatigue off): neutral-real seed 1 = 61-80, trace c1a578db3f2754d3f69b47ba81a1f9d5b9336e1d87f496de2fa8dc3daee7a256, state c517e00f864f1438705cdd1d9768d61523ee1aaac69746f57a2e9f1f4adf2745.

 f) RB-3.28 identity (fatigue ON at RB-3.28 rates): ratings 0.4, Garvian Guardians vs Ala Apex seed 1 = 85-86, trace a399f74f81d891c8a0cd4014fc5d10bc5623ad835c448932a94cd50ffac7ac4b, state bc4898a8229d147bd60defdc623db55fac13a3845fb5f29f812198b4bf5f61d4.

 g) Speed: the stats ledger adds at most 3% per step.

## Revisions and scope

- Branch `codex/rb-3-29-stats-rotation-swing`
- Lead-verified parent `49447ae7861d01e0f7a96e62db8b05ae6c838efc`
- Implementation `0dc9bf9` and final individual credit correction `010e47b`.
- [Reproduction, box-score definitions and denominators](rb329/README.md)

| Task | Status |
|---|---|
| 1. Player stats ledger | DESIGN COMPLETE, IMPLEMENTED, TESTED. Identity and timing gates passed. |
| 2. Rotation rhythm options | DESIGN COMPLETE, IMPLEMENTED, TESTED. Thirty matches per profile, with starter-minute drift reported. |
| 3. Possession swing diagnosis | DESIGN COMPLETE, IMPLEMENTED, TESTED. All 150 games analyzed from their reconciled ledgers. |

The workload uses the ratings 0.4 workbook and the established on-field selection from OVR 0.422. All five profiles use hand-set values and individual substitutions. The thresholds and position preference stay fixed. The soak reports a starter-minute drift greater than 1.5 minutes from 32.

## Regression evidence

The maintained suite reported `779 passed, 1 warning, 23 subtests passed in 641.04s (0:10:41)`. The warning was the pytest dependency deprecation. The six legacy rows matched exactly.

The compatibility and CORE identity matches used the ledger. Both reproduced the exact scores, configuration, trace and state in the parent evidence. The two full observed R1 seed-1 games also reproduced the parent fingerprints, covering gates c through f.

| Seed | Ledger off, CPU ms/step | Ledger on, CPU ms/step |
|---:|---:|---:|
| 1 | 4.143 | 4.167 |
| 3 | 3.815 | 3.912 |

In the two paired 1,500-step windows, the score and all fingerprints matched. Ledger cost was **+1.52%**, within the 3% gate. The timings include box-score reconciliation at the end of the window.

A separate full R3M seed-1 process reproduced **48–97**, the complete compact ledger and these fingerprints.

- Config `f4ed515117cff93db936b40892814e9f503c45b17dc1f3bc889b89d76a54b483`
- Trace `dc3a4a2482bf3ff114e4477016113ba95391ea2788cc1c7d427ac494cc9537fc`
- State `361cedff1c283719c1634e8e04f0addfdd805fdc234b167dde7a4697ae7fc942`

The 150 scored runs used **23,119.27 process CPU seconds**. The two-possession floor changed the final score in 17 of 30 R2 pairs and seven of 30 R3 pairs. Its effect on aggregate regulation minutes was under 0.02 minutes in both rate pairs.

## Rotation rhythms

Each profile ran 30 games. The workbook, matchup order, seed list, ratings, scoring, thresholds and substitute preference were held fixed. The minimum-stint rule applies to individual substitutions. Regulation minutes exclude overtime. Stints are contiguous live time and may include overtime.

| Profile | Subs per team/game | Median stint | Stint range | Starter mean | Starter range | Bench mean | Keeper starter mean (range) | Drift from 32 | ±1.5 min |
|---|---|---|---|---|---|---|---|---|---|
| R1 | 139.40 | 2.07 | 0.003–35.16 | 32.18 | 25.84–39.96 | 12.35 | 40.00 (40.00–40.00) | +0.18 | Within |
| R2 | 24.65 | 4.62 | 0.005–45.00 | 37.58 | 29.93–40.00 | 3.81 | 40.00 (40.00–40.00) | +5.58 | Outside |
| R3 | 1.57 | 40.00 | 0.025–40.00 | 39.80 | 34.43–40.00 | 0.38 | 40.00 (40.00–40.00) | +7.80 | Outside |
| R2M | 24.33 | 4.44 | 0.011–46.04 | 37.59 | 30.81–40.00 | 3.84 | 40.00 (40.00–40.00) | +5.59 | Outside |
| R3M | 1.58 | 40.00 | 0.025–40.00 | 39.79 | 34.43–40.00 | 0.43 | 40.00 (40.00–40.00) | +7.79 | Outside |

Fatigue-only substitutions include starter returns. Stints shorter than a possession can still occur at match end or because of a required substitution.

| Profile | Median team score | Mean team score | Team score SD | Mean possessions | Attempt-ending share | Ala margin ± SE | Ala wins | Within 5 | Median abs. margin | Ties |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | 86 | 88.27 | 20.21 | 147.50 | 35.26% | +37.30 ± 7.22 | 10/10 | 6.67% | 26 | 0 |
| R2 | 84.5 | 86.30 | 18.66 | 148.75 | 34.79% | +31.00 ± 7.33 | 9/10 | 16.67% | 24 | 0 |
| R3 | 87 | 89.97 | 19.05 | 150.13 | 35.92% | +37.70 ± 4.92 | 10/10 | 13.33% | 22 | 0 |
| R2M | 87.5 | 86.85 | 16.97 | 149.05 | 35.03% | +30.60 ± 6.75 | 10/10 | 10.00% | 22 | 0 |
| R3M | 88.5 | 89.95 | 20.18 | 149.97 | 36.03% | +41.20 ± 5.64 | 10/10 | 10.00% | 26.5 | 0 |
| Pooled | 87 | 88.27 | 19.11 | 149.08 | 35.40% | +35.56 ± 2.82 | 49/50 | 11.33% | 24 | 0 |
| NBL 25–26 | — | 78.1 | 12.7 | — | — | — | — | 23% | 13 | 0 |

## Possession swing

The possession histogram uses points scored by the team in possession. Score events for the other team are recorded in the same match and tracked separately from the histogram. The margin decomposition uses all scoreboard points.

| Profile | Possessions | Mean points | Point SD | 0 | 1 | 2 | 3 | 4 | 5 | More |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | 8,850 | 0.581 | 1.310 | 82.10% | 0.73% | 3.04% | 6.31% | 7.04% | 0.55% | 0.23% |
| R2 | 8,925 | 0.563 | 1.286 | 82.54% | 0.68% | 3.05% | 6.39% | 6.62% | 0.52% | 0.20% |
| R3 | 9,008 | 0.585 | 1.306 | 81.76% | 0.70% | 3.43% | 6.66% | 6.63% | 0.62% | 0.20% |
| R2M | 8,943 | 0.563 | 1.288 | 82.50% | 0.70% | 3.15% | 6.21% | 6.71% | 0.55% | 0.18% |
| R3M | 8,998 | 0.585 | 1.306 | 81.73% | 0.70% | 3.53% | 6.65% | 6.53% | 0.64% | 0.21% |
| Pooled | 44,724 | 0.575 | 1.299 | 82.13% | 0.70% | 3.24% | 6.44% | 6.71% | 0.58% | 0.20% |

The pooled ledger records 752 scoreboard points outside the scoring team’s own possession. The per-team distributions and end-reason tables for every matchup are in the numeric summary.

| Profile | Carry | Throw 2 | Throw 3 | Throw 4 | Half goal | Full award | Own goal |
|---|---|---|---|---|---|---|---|
| R1 | 2.83% | 10.20% | 33.65% | 47.96% | 2.55% | 2.66% | 0.15% |
| R2 | 2.90% | 10.43% | 34.99% | 46.97% | 2.51% | 2.09% | 0.12% |
| R3 | 3.15% | 11.75% | 34.85% | 45.28% | 2.54% | 2.22% | 0.22% |
| R2M | 3.26% | 10.78% | 33.97% | 47.51% | 2.65% | 1.67% | 0.15% |
| R3M | 3.15% | 12.15% | 34.80% | 44.91% | 2.59% | 2.17% | 0.22% |
| Pooled | 3.06% | 11.07% | 34.45% | 46.51% | 2.57% | 2.16% | 0.17% |


| Pooled possession end | Count | Share | Mean points |
|---|---|---|---|
| interception | 15,498 | 34.65% | 0.013 |
| boundary | 9,188 | 20.54% | 0.014 |
| score | 7,551 | 16.88% | 3.314 |
| opponent_control | 3,671 | 8.21% | 0.038 |
| fumble | 3,523 | 7.88% | 0.019 |
| second_tackle | 2,812 | 6.29% | 0.037 |
| period_end | 601 | 1.34% | 0.027 |
| possession_expiry | 457 | 1.02% | 0.000 |
| strip | 357 | 0.80% | 0.025 |
| turnover | 257 | 0.57% | 0.074 |
| ZR-C | 230 | 0.51% | 0.000 |
| zone_residence | 185 | 0.41% | 0.119 |
| ZR-1 | 179 | 0.40% | 0.000 |
| ZR-T | 171 | 0.38% | 0.000 |
| first_tackle | 20 | 0.04% | 0.000 |
| own_goal | 16 | 0.04% | 0.000 |
| held_ball | 6 | 0.01% | 0.000 |
| major | 2 | 0.00% | 0.000 |

The per-profile and per-matchup end-reason splits are in the numeric summary.

| Profile | Total variance | Within matchup | Between matchups | Possession-count term | Points-per-possession term | 2 × covariance |
|---|---|---|---|---|---|---|
| R1 | 1031.53 | 484.65 | 546.88 | 0.37 | 1031.95 | -0.79 |
| R2 | 817.32 | 411.29 | 406.03 | 0.45 | 823.24 | -6.37 |
| R3 | 763.89 | 235.32 | 528.57 | 0.39 | 770.03 | -6.52 |
| R2M | 752.18 | 344.62 | 407.56 | 0.33 | 750.68 | 1.18 |
| R3M | 919.67 | 297.67 | 622.01 | 0.39 | 926.09 | -6.81 |
| Pooled | 857.60 | 438.62 | 418.97 | 0.40 | 860.98 | -3.78 |

The first split weights matchups by games played. Pooled within-matchup variation includes seeds and profiles. The count, scoring-rate and twice-covariance terms add to total variance.

| Profile | Median longest run | Max longest run | 3+ possession runs | Team-games with a 3+ run | Margin per OVR point |
|---|---|---|---|---|---|
| R1 | 20 | 34 | 41 | 48.33% | +3.90 |
| R2 | 19.5 | 43 | 40 | 51.67% | +4.08 |
| R3 | 18.5 | 38 | 59 | 56.67% | +4.54 |
| R2M | 18 | 43 | 41 | 46.67% | +4.16 |
| R3M | 19 | 38 | 55 | 56.67% | +4.37 |
| Pooled | 19 | 43 | 236 | 52.00% | +4.21 |


| Matchup (A vs B) | Starter OVR difference B − A | Mean margin B − A |
|---|---|---|
| Garvian Guardians vs Ala Apex | +9.23 | +35.56 |
| Yukïma Cowhands vs Isu’Kari Sirenwings | -0.31 | -12.56 |
| Mbuya Ïmu Moonhawks vs Ala Apex | -1.92 | +5.68 |
| Ala Marauders vs Kasuf Bloodravens | -2.77 | -29.60 |
| Dōmyu Dominators vs Güunlekia Serpents | +6.15 | +21.90 |
| Hina’sola Hunters vs Isu’Kari Sirenwings | +0.85 | +4.20 |
| Kalundu Shockwave vs Khemara Sunscourge | +1.15 | +9.60 |
| Ndomiri Sentinels vs Zafiren Tidewings | +0.69 | +9.30 |

## Three measured swing drivers and candidate experiments

1. **Scoring rate per possession.** Its variance term was 861.0 point² out of 857.6 total. The possession-count term was 0.40 point² and twice their covariance was -3.78 point². **BEHAVIORAL** candidate. Test pressure-aware shot denial and outlet choice at the current scoring and restart settings.
2. **Persistent matchup differences.** Between-matchup variation was 48.85% of the total, and each point of the starter OVR difference was associated with +4.21 points of signed margin across the eight matchup means. **BEHAVIORAL** candidate. Test a narrower provisional rating-to-execution slope for throwing and catching while holding roster selection and physical movement rules fixed.
3. **Four-point throws.** They supplied 46.51% of scoreboard points and 59.12% of the variance allocated by scoring method. **CANON** candidate. Ask the owner whether to test a smaller score gap between the outer two throwing bands.

These are overlapping diagnostics. The season reference contains final scores only, so it supplies targets for the output distribution. Each candidate is an experiment for review.

## Raw evidence and open questions

All 150 matches finished and reconciled team points, goals, possessions and turnovers. Twenty R1 games shared an exact RB-3.28 reference. The full ledger exports for the five Garvian–Ala seed-1 games are committed as JSON and CSV. The soak archive stores compact per-match evidence, including each possession and score event. Use the single-match command to export a full box score for any other case.

[Numeric summary](rb329/evidence/summary.json) · [Per-match CSV](rb329/evidence/matches.csv) · [Seed-1 box scores](rb329/evidence/boxes) · [All 150 raw cases](rb329/evidence/runs)

No canon ruling is needed to reproduce this build. The owner’s rhythm choice and any experiment involving scoring values remain open.
