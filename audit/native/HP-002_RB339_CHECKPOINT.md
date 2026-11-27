# OWNER BRIEFING

1. **Accomplished.** DESIGN COMPLETE, IMPLEMENTED and TESTED. Edge braking, turn direction, and the speed-aware aim margin are independently selectable. E1 combines them on the R3 period-budget setup.
2. **What Native can do now.** Surface locomotion checks the athlete’s own stopping and turning distances before reaching a line. Carrier body-outs averaged 20.31 in R3 and 5.25 in E1 per team per game.
3. **Unproven.** The two matchups measure eight paired games. Contact impulses and the ability to stop before a given line remain part of the physics.
4. **Blocking.** None for this checkpoint.
5. **Recommended action.** Review E1 as a candidate for adoption given the reduction in exits. Weigh the increase in near-line takedowns and the drop in possessions. The period-budget sizes still need the owner’s confirmation.

## Implementation and test design

Parent `f64b9ab4836885ba6936aaaa3d57d61e37a7eebd`. Implementation `791b95cd9c5d6c985472168977ef62c60f3288ea` and profile guard fix `834c277` on `codex/rb-3-39-edge`. CPython 3.13.5. The two matchups used the ratings 0.4 workbook at SHA-256 `47b48af7a19035428d517582370fa1782b542980c783edf3dfb20619cf437fba`.

- The brake checks the body edge against stopping distance with the 0.3 m buffer. It spends the step first on cancelling outward motion and uses leftover time for the existing propulsion limits. At a corner the closest threatened line takes priority.
- The turn-direction check uses twice the body-model turning radius and the signed short-turn side. It only changes the turn when the desired direction is more than 90° behind the current heading.
- The aim clamp uses max(2.0 m, body radius + outward stopping distance + 0.5 m) per line. It caps geometrically infeasible margins at the opposite line’s minimum clearance. The own-body calculation is shared by cognition and the surface motor.
- At the attacked goal the carrier can keep a route that intersects the legal mouth chord at hand height. Dead-ball movement and marked substitution exits bypass the new guard. The existing contact integration, surface judge, and scoring remain in force.

## Evidence

Garvian Guardians–Ala Apex seeds 1–5 and Yukïma Cowhands–Isu’Kari Sirenwings seeds 1–3. Eight new E1 games finished with invariants passing and all restarts resolved. The eight E0 replays matched their archived R3 fingerprints and supplied the additional perimeter witnesses. All eight archived R3 results supply the already available comparison measures. At most two simulation processes ran for the paired games.

Carrier body-outs changed by -15.06 ± 1.98 per team per game. Inside-aim steering overshoots changed by -10.38 ± 1.73. Non-carrier body-outs changed by -51.31 ± 1.93.

Takedowns within 3 m of a line rose by 3.56 ± 1.31, while overall takedown success and per-pairing margins stayed within paired noise. Possessions changed by -12.19 ± 4.02, and points by -2.06 ± 4.14. The matched-observer runtime change was -4.68 ± 4.35 CPU seconds per game.

The replay archives embed named CSV and JSON box scores. The observer sampled 20 E1 exits with fixed seed 20261129. The linked files include per-game results, all paired contrasts, and complete episode histories.

[Reproduction guide](rb339/README.md) · [Paired tables](rb339/TABLES.md) · [Raw evidence](rb339/evidence/) · [Episode sample](rb339/SAMPLED_BODY_OUTS.json.gz)

## Combined highlights

| Measure | R3 | E1 | E1 − R3 |
| --- | ---: | ---: | ---: |
| Carrier body-outs | 20.31 | 5.25 | -15.06 ± 1.98 |
| Carrier body-outs, sideline | 11.25 | 2.50 | -8.75 ± 0.95 |
| Carrier body-outs, end line | 9.06 | 2.75 | -6.31 ± 1.34 |
| Carrier out, steering overshoot with aim inside | 15.00 | 4.62 | -10.38 ± 1.73 |
| Carrier out, contact push | 5.31 | 0.56 | -4.75 ± 0.41 |
| Non-carrier body-outs | 54.44 | 3.12 | -51.31 ± 1.93 |
| Passes out | 13.00 | 15.19 | +2.19 ± 1.28 ~ |
| Loose balls out | 0.75 | 0.44 | -0.31 ± 0.23 ~ |
| Possessions/team | 125.75 | 113.56 | -12.19 ± 4.02 |
| Mean possession duration (s) | 14.55 | 15.60 | +1.06 ± 0.51 |
| Points/team | 87.19 | 85.12 | -2.06 ± 4.14 ~ |
| Carry goals | 2.56 | 2.25 | -0.31 ± 0.37 ~ |
| Pass completion (%) | 82.55 | 82.23 | -0.32 ± 1.29 ~ |
| Takedown episodes | 395.69 | 380.12 | -15.56 ± 14.57 ~ |
| Takedown success (%) | 14.18 | 14.93 | +0.74 ± 0.81 ~ |
| Takedowns within 3 m of a line | 12.00 | 15.56 | +3.56 ± 1.31 |
| Arrows net charged | 39.38 | 39.06 | -0.31 ± 0.97 ~ |
| Freezes | 9.25 | 8.75 | -0.50 ± 0.95 ~ |
| Carrier-freeze fumbles | 4.50 | 4.56 | +0.06 ± 0.77 ~ |
| Second team minus first team margin | 12.62 | 5.75 | -6.88 ± 12.58 ~ |
| CPU seconds/game, matched observer | 283.44 | 278.76 | -4.68 ± 4.35 ~ |

Counts are per team per game unless labelled. A tilde marks differences within two paired standard errors. The complete tables include per-pairing rates, line and cause breakdowns, evasion measures, and per-game CPU and margins.

## Gates

- a) Full suite. TESTED with `pytest -q b1 native`. 857 passed, 23 subtests passed in 611.81s (0:10:11).
- b) All six legacy hashes match the recorded 3,000-step windows for seeds 1 and 3 byte for byte. The first run caught an installer guard that also matched Native v0/3. Requiring the exact native-rb/3 profile resolved it, and the final E1 repeat retained the original trial fingerprints.
- c) E1 seed 1 repeats exactly for score, trace, state, box scores and raw observations. Timing and sampled CPU profiles are measured separately.
- d)–h) Compatibility, CORE, RB-3.28, RB-3.31 and RB-3.32 reproduce their recorded fingerprints.
- i) A6, B4, T3 and R3 seed 1 reproduce exactly. E1 seed 1 is recorded below.

| Mode | Score | Trace SHA-256 | State SHA-256 | Config SHA-256 |
| --- | ---: | --- | --- | --- |
| compatibility | 57–76 | `44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072` | `046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d` | `3d66214c927b42abf493bfe93c9d7ef85675364f54b5e6a9f245daadc4799550` |
| core | 61–80 | `c1a578db3f2754d3f69b47ba81a1f9d5b9336e1d87f496de2fa8dc3daee7a256` | `c517e00f864f1438705cdd1d9768d61523ee1aaac69746f57a2e9f1f4adf2745` | `e3eb027d0506db1297def02bb74924cb9c3878fa17226ffb6a47e56722976835` |
| RB-3.28 threshold rotation | 85–86 | `a399f74f81d891c8a0cd4014fc5d10bc5623ad835c448932a94cd50ffac7ac4b` | `bc4898a8229d147bd60defdc623db55fac13a3845fb5f29f812198b4bf5f61d4` | `3af62b414b132cad51d1547dd1abb6bc735fef5a147d41aafebc3475b414df5e` |
| PLANNED | 64–96 | `ab86f8befcf2baca264ab87fabdd39af3e218cb80032eab52b356a089319a08a` | `e8318c85ba3ae5205861d138f8d4f63e16202dd6d84f4ab8b5df02066e141047` | `117f5525293e5a2a24476697e32278ca4fec2cb761a8e8df299e57e2d19410bc` |
| RB332 | 99–74 | `0045e62d5de38fc85a6c38fd58298284f637bb6d1766ddb7d50cfb159ac22601` | `b2b6857584bbdc7c486b54f52bd8ebf9c2c89fde8e15893a42c70f5c3be9d9de` | `374ab384a9a9fb5e777a0415e76a7131dc3b58ffc01ec527695c0724a149434d` |
| A6 | 61–105 | `2437b8084c08d99b954395db42c7b55bdad93402586796a9bdd4ad665dd16aee` | `e10536f2eb9366ba3d2ea3a8e38a741e93b387bdc15ef3d80dc6f2b53661eeaa` | `c6dfe491fdb0dc792a7c4c9c12c803bad5fee1d5173edd874800fe7be1e7bd44` |
| B4 | 57–112 | `f424c4eefded4723efe017b2b86dea0c2ce252d587d79e7cddb899138443e9c9` | `1d701334a0a83c26a77e4b41fd091d68958ab481442d2e10888b49e950298d82` | `a3b387b7f81193daa6321db0b3670798edc4acb6e653e9160a7f9edb87badbe1` |
| T3 | 44–122 | `539c554801a03f2645627110264112ff67f55b3ff21b6182bf6241efb22309c9` | `0383c42494aa3d8f601c149d54de2d1c119d7c30639d4a064b326b3dd6a39793` | `9342b188992c593fc9533826695fcc439ab183c428189a5aa5aa77a85b78e386` |
| R3 | 64–123 | `ec8cfaf293304865597d85eb55ddad7b608eabd66a1073748dac24fc8ccc0c09` | `2eada874338852ba7c9d27221eeda616c69862a0cdeb011b61cfd0aa170ed909` | `dbbc7a4f5a855add6df0af0bcd02b2809654ae6df245b6cd08279e84b9138126` |
| E1 | 89–96 | `8145286b995dde65d454364b307051c94f65fba461a984e6818681837932e0c5` | `175ef33be73eb45fa3d77129b95f957946b837ba5e19ba1f5ef8f7e7284fc05c` | `f207194a947cecf2f0fe66c72d837f54bf490742faa46f73de85b1fb90c3b3a9` |

## Open questions

The R3 regulation and overtime budget sizes remain pending owner confirmation.
