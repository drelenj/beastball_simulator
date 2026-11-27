# OWNER BRIEFING

1. **Accomplished.** DESIGN COMPLETE, IMPLEMENTED and TESTED. The current rulebook defaults to three tackles. The branch adds an opt-in Archer draw-and-aim cycle, two team budget trials and a read-only carrier body-out observer.
2. **What Native can do now.** Use one budget per Archer team across a match, or reset it each period. In R0 / R1 / R2 / R3 order, freezes averaged 96.19 / 59.50 / 4.81 / 9.25 per team per game. Carrier-freeze fumbles averaged 21.25 / 20.25 / 2.50 / 4.50, and possessions averaged 140.62 / 142.50 / 119.88 / 125.75.
3. **Unproven.** Budget selection still belongs to the owner. The two pairings measure these configurations on the trial sample. The body-out classes describe event timing and motion evidence.
4. **Blocking.** None for this checkpoint.
5. **Recommended action.** Review the match and period spending curves alongside freezes, possession endings and score margins before choosing a budget.

## Source, schedule and reproduction

Parent `ad3d9aeaa14beb6cc27d0c60bc7122306683bbbc`. Archer implementation `bd89a8dd228c6189dc214bbecedac2aacf1e30aa`. Final engine and observer source `09d901259d7d1e6efce988c8b118b83719920362` on `codex/rb-3-38-archer`. CPython 3.13.5. The ratings 0.4 workbook is pinned at SHA-256 `47b48af7a19035428d517582370fa1782b542980c783edf3dfb20619cf437fba`.

The schedule was Garvian Guardians–Ala Apex seeds 1–5 and Yukïma Cowhands–Isu’Kari Sirenwings seeds 1–3. There were 24 new trial games and eight read-only R0 replays to capture exact release times and body-out histories missing from the inherited evidence. All eight R0 score, trace, state and config fingerprints match the RB-3.37 L0 files. All 32 scheduled games finished with invariants passing and every restart resolved. At most two simulator processes ran in parallel.

The [reproduction guide](rb338/README.md) lists commands. The [raw results](rb338/evidence/) contain per-game event observations plus named CSV and JSON box scores. The [complete paired tables](rb338/TABLES.md) include all requested means, paired contrasts, spending by minute and margins. The [20 sampled exits](rb338/SAMPLED_BODY_OUTS.json) list each decision and physics sample in their rolling histories.

## Rules and mechanism

- The current `RulebookConfigV3` sets three tackles. Archived runners explicitly request their original two-tackle config. Named T3 stays at three. Config records retain the old serialized form at two so the historical digest stays stable.
- Before the trial, Native cognition queried a 2,600 ms wait after the previous release and the motor scheduled a 600 ms draw. The frozen core also contains a 2-second cooldown and a 5-second reload, but Native disables that reload and uses its own release authority.
- On R0, elapsed-clock release intervals pooled by same Archer are 3.26 / 5.83 / 29.48 seconds at P10 / P50 / P90. The live-clock counterparts are 3.21 / 4.00 / 18.53 seconds. The main tables also report the means of the within-game quantiles.
- `archer_cycle` defaults OFF. When enabled, draw takes 1,000 × [1 + 0.6 × (0.70 − Strength)] ms and aim takes 800 × [1 + 0.6 × (0.70 − Archery Accuracy)] ms. A new target restarts aim after the original draw deadline. Final aim uses the athlete’s delivered observation and velocity estimate. The engine validates the target and deadline and charges only at release.
- R2 allots 25 arrows and five freezes per team for the entire match. R3 allots 10 and four each regulation period, then five and two each overtime period. Neither trial resets its budget on possession changes. Both maintain the existing illegal-release charge and dead-ball refunds. The quiver invariant checks the effective allocation.
- Budget counts come through the public view. The Archer compares the existing option values with the cost of spending a limited shot. The reserve uses the existing carrier-target value at the observed distance, multiplied by the fraction of remaining possible cycles that cannot be covered by the smaller of the two resource balances. Holding a draw spends nothing. The same seeded Disruption decision error applies.
- The observer stores every body-out with the previous two seconds of committed physics and decisions, including before the player became the carrier. The [witness definitions](rb338/README.md) give the classification priority and distinguish observed contact timing from causation.

## Combined highlights

| Measure | R0 | R1 | R2 | R3 | R1 − R0 | R2 − R0 | R3 − R0 | R3 − R2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Arrows released (legal) | 299.69 | 221.75 | 17.62 | 40.31 | -77.94 ± 4.00 | -282.06 ± 2.46 | -259.38 ± 2.82 | +22.69 ± 1.68 |
| Arrows net charged | 298.06 | 218.69 | 17.19 | 39.38 | -79.38 ± 3.57 | -280.88 ± 2.83 | -258.69 ± 3.12 | +22.19 ± 1.69 |
| Arrow impacts on players | 185.06 | 117.19 | 9.44 | 20.19 | -67.88 ± 4.35 | -175.62 ± 2.56 | -164.88 ± 2.22 | +10.75 ± 1.01 |
| Freezes | 96.19 | 59.50 | 4.81 | 9.25 | -36.69 ± 5.40 | -91.38 ± 4.08 | -86.94 ± 4.32 | +4.44 ± 0.57 |
| Freezes (carrier) | 33.06 | 31.12 | 3.69 | 6.69 | -1.94 ± 3.08 ~ | -29.38 ± 2.19 | -26.38 ± 2.34 | +3.00 ± 0.57 |
| Carrier-freeze fumbles | 21.25 | 20.25 | 2.50 | 4.50 | -1.00 ± 1.60 ~ | -18.75 ± 1.32 | -16.75 ± 1.47 | +2.00 ± 0.61 |
| Possessions/team | 140.62 | 142.50 | 119.88 | 125.75 | +1.88 ± 3.24 ~ | -20.75 ± 3.75 | -14.88 ± 4.73 | +5.88 ± 2.74 |
| Mean possession duration (s) | 12.70 | 12.49 | 14.74 | 14.55 | -0.22 ± 0.30 ~ | +2.04 ± 0.41 | +1.84 ± 0.48 | -0.19 ± 0.40 ~ |
| Carrier body-outs | 19.19 | 17.56 | 16.06 | 20.31 | -1.62 ± 1.48 ~ | -3.12 ± 1.33 | +1.12 ± 1.33 ~ | +4.25 ± 1.41 |
| Carrier out, contact push | 5.25 | 3.62 | 3.62 | 5.31 | -1.62 ± 0.52 | -1.62 ± 1.05 ~ | +0.06 ± 1.04 ~ | +1.69 ± 0.47 |
| Carrier out, maneuver path | 0.00 | 0.00 | 0.00 | 0.00 | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ |
| Carrier out, steering overshoot with aim inside | 13.94 | 13.94 | 12.44 | 15.00 | +0.00 ± 1.81 ~ | -1.50 ± 1.47 ~ | +1.06 ± 1.31 ~ | +2.56 ± 1.30 ~ |
| Carrier out, aim outside | 0.00 | 0.00 | 0.00 | 0.00 | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ |
| Carrier out, frozen or stunned | 0.00 | 0.00 | 0.00 | 0.00 | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ |
| Carrier out, other | 0.00 | 0.00 | 0.00 | 0.00 | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ |
| Points/team | 84.19 | 82.44 | 81.06 | 87.19 | -1.75 ± 5.15 ~ | -3.12 ± 7.09 ~ | +3.00 ± 4.26 ~ | +6.12 ± 5.93 ~ |
| Second team minus first team margin | 33.88 | 29.38 | 14.88 | 12.62 | -4.50 ± 14.19 ~ | -19.00 ± 14.57 ~ | -21.25 ± 13.97 ~ | -2.25 ± 11.59 ~ |
| CPU seconds/game | 267.74 | 269.83 | 267.36 | 276.25 | +2.10 ± 1.77 ~ | -0.37 ± 1.05 ~ | +8.51 ± 5.05 ~ | +8.88 ± 4.77 ~ |

Counts are per team per game unless labelled. Paired contrasts use matching seeds and opponents. A tilde marks effects within two paired standard errors. See the complete tables for the matchup splits, event-based Keeper rates and named box rates.

R1 reduced total freezes by 36.69 ± 5.40 versus R0. Its changes in carrier-freeze fumbles and possessions stayed within paired noise. R2 and R3 reduced both, with possession differences of −20.75 ± 3.75 and −14.88 ± 4.73 versus R0. Combined mean score and signed margin changes stayed within paired noise.

By the end of period 1, 14 of 16 teams had spent all five match-budget freezes in R2. In R3, teams used their full arrow budget in 57 of 64 regulation team-periods. The R3 overtime case was pair 1 seed 3 and reconciled to its separate overtime budget.

In R0, 13.94 of 19.19 carrier body-outs per team per game had an inside locomotion target and no recent-contact or active-maneuver classification. This was the largest category in every arm. R3 recorded 4.25 ± 1.41 more body-outs than R2.

## Gates

- a) Full suite. TESTED with `pytest -q b1 native`. 847 passed, 23 subtests passed in 586.80s (0:09:46).
- b) The six legacy hashes match the saved 3,000-step windows on seeds 1 and 3 byte for byte.
- c) R3 seed 1 repeats exactly, including event observations and named box scores. CPU and profiling samples are timing measurements.
- d)–h) Compatibility, CORE, RB-3.28, RB-3.31 and RB-3.32 reproduced their recorded scores and full trace, state and config fingerprints.
- i) A6, B4 and T3 seed 1 reproduced exactly. R1, R2 and R3 seed-1 fingerprints are recorded below.

| Mode | Score | Trace SHA-256 | State SHA-256 | Config SHA-256 |
| --- | ---: | --- | --- | --- |
| compatibility | 57–76 | `44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072` | `046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d` | `3d66214c927b42abf493bfe93c9d7ef85675364f54b5e6a9f245daadc4799550` |
| core | 61–80 | `c1a578db3f2754d3f69b47ba81a1f9d5b9336e1d87f496de2fa8dc3daee7a256` | `c517e00f864f1438705cdd1d9768d61523ee1aaac69746f57a2e9f1f4adf2745` | `e3eb027d0506db1297def02bb74924cb9c3878fa17226ffb6a47e56722976835` |
| RB-3.28 threshold rotation | 85–86 | `a399f74f81d891c8a0cd4014fc5d10bc5623ad835c448932a94cd50ffac7ac4b` | `bc4898a8229d147bd60defdc623db55fac13a3845fb5f29f812198b4bf5f61d4` | `3af62b414b132cad51d1547dd1abb6bc735fef5a147d41aafebc3475b414df5e` |
| PLANNED | 64–96 | `ab86f8befcf2baca264ab87fabdd39af3e218cb80032eab52b356a089319a08a` | `e8318c85ba3ae5205861d138f8d4f63e16202dd6d84f4ab8b5df02066e141047` | `117f5525293e5a2a24476697e32278ca4fec2cb761a8e8df299e57e2d19410bc` |
| RB332 | 99–74 | `0045e62d5de38fc85a6c38fd58298284f637bb6d1766ddb7d50cfb159ac22601` | `b2b6857584bbdc7c486b54f52bd8ebf9c2c89fde8e15893a42c70f5c3be9d9de` | `374ab384a9a9fb5e777a0415e76a7131dc3b58ffc01ec527695c0724a149434d` |
| A6 | 61–105 | `2437b8084c08d99b954395db42c7b55bdad93402586796a9bdd4ad665dd16aee` | `e10536f2eb9366ba3d2ea3a8e38a741e93b387bdc15ef3d80dc6f2b53661eeaa` | `c6dfe491fdb0dc792a7c4c9c12c803bad5fee1d5173edd874800fe7be1e7bd44` |
| B4 | 57–112 | `f424c4eefded4723efe017b2b86dea0c2ce252d587d79e7cddb899138443e9c9` | `1d701334a0a83c26a77e4b41fd091d68958ab481442d2e10888b49e950298d82` | `a3b387b7f81193daa6321db0b3670798edc4acb6e653e9160a7f9edb87badbe1` |
| T3 / R0 | 44–122 | `539c554801a03f2645627110264112ff67f55b3ff21b6182bf6241efb22309c9` | `0383c42494aa3d8f601c149d54de2d1c119d7c30639d4a064b326b3dd6a39793` | `9342b188992c593fc9533826695fcc439ab183c428189a5aa5aa77a85b78e386` |
| R1 | 38–119 | `3f0faa4f6891917a6c8601609f29e7ceed8107222a198c33c296ed3b69ec1f5d` | `54a35a08bfaf9355000d3bda57e456ee6257f3c8126c6c01b961e4e288ebc184` | `74a7f822487fc573506196401ab9780cc746d5c59882314f08ea431693d4f0c1` |
| R2 | 60–90 | `8c0e7d5e6f0d399c58bd89f9a11c69c5abd11b89ce0ba7c324d24fa6a1b33f7a` | `df0b060af6fcc2151257b1684eae7540d4a558f8f10502915a08f3e56812adf4` | `26e71cc2dad1b179e51e9247711658adef1b031abdc45db5a07afbd13735fb5b` |
| R3 | 64–123 | `ec8cfaf293304865597d85eb55ddad7b608eabd66a1073748dac24fc8ccc0c09` | `2eada874338852ba7c9d27221eeda616c69862a0cdeb011b61cfd0aa170ed909` | `dbbc7a4f5a855add6df0af0bcd02b2809654ae6df245b6cd08279e84b9138126` |

Legacy outputs are in [legacy.txt](rb338/evidence/legacy.txt). The generated tables and episode sample reproduce byte for byte with the commands above.

## Open questions

The choice of budget size and reset scope remains with the owner.
