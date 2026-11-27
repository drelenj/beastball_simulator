# OWNER BRIEFING

1. **Accomplished.** IMPLEMENTED the two universal traction settings on the three-tackle trial. TESTED all 24 games in the paired comparison and archived named box scores and event measures.
2. **What Native can do now.** The same Agility rating controls stronger braking and turning for every role. Native can replay the original three-tackle trial and run either traction setting. Across the eight pairs, carrier body-outs averaged 19.19, 18.94 and 21.25 per team per game at 1×, 1.5× and 2×.
3. **Unproven.** The two pairings do not establish a league-wide effect. Unresolved fumble attributions are itemized below.
4. **Blocking.** None for this checkpoint.
5. **Recommended action.** Keep L0 as the reference. The 1.5× body-out change was within paired noise, and 2× increased self-run end-line exits. Both higher scales increased possessions.

## Build and evidence

Parent `3dc4eef3aa871f72d8c13ef46a4b3b81b5c4bac3`, branch `codex/rb-3-37-traction`. Engine commit `570fd12`, corrected loss-event observer `e19353d`. CPython 3.13.5. Workbook SHA-256 `47b48af7a19035428d517582370fa1782b542980c783edf3dfb20619cf437fba`.

## Traction implementation and consumer audit

DESIGN COMPLETE and IMPLEMENTED in `570fd12`. The three-tackle T3 rules and the same planned-rotation settings apply in all arms. The trial changes braking and lateral acceleration for all bodies, from field players to Keepers and Archers, wherever their movement uses those parameters. Traction is applied once when constructing the body from the roster. It leaves acceleration, top speed, Agility itself, ratings data and sport rules unchanged.

- Turning = 16.25 × Agility × traction scale (m/s²).
- Braking = 16.875 × Agility × traction scale (m/s²).
- L0 uses 1×, L1 uses 1.5×, and L2 uses 2×. The default value is omitted from the serialized config so historical config digests remain replayable.
- At 0.70 Agility, braking is 11.81, 17.72 and 23.63 m/s². The corresponding reactive set speeds, braking × 0.40 s, are 4.73, 7.09 and 9.45 m/s. Fresh-body turning radius is v² ÷ turning. Fatigue still acts on the mapped body during play.

| Consumer | Source of braking or turning |
| --- | --- |
| `core_src/match.py`: `move_players`, `update_archers`, `c3_desired`, `c3_move`, `c3_free`, `c3_run` | Desired speeds, lateral steering, slowing for contact, player-motion bounds and braking. The contact solver caches mapped body values for the current step. |
| `core_src/match.py`: `c4c2_engage_s`, `c3_driven`, `c3_no_time`, `pocket_receiver_position` | Tackle, reach and receiver motion estimates use the participating body's value. |
| `core_src/engine.py`: `recovery_committed`, `exit_run`, `zone_compliance_time`; `core_src/geometry.py`: `intercept_xy` | Recovery and zone-exit timing, steering and receiver lead use body values. |
| `native/port.py`: `body`; `native/cognition_rb3.py`: `time_to_cover`, `typical_time_to` | Own-body braking feeds stopping and reversal estimates. On scaled arms, the nominal opponent reversal estimate is derived from the same mapping at 0.70 Agility and passed as a public constant. It has no access to opponent attributes. |
| `native/turnovers.py`: `boundary_risk`; `native/paired_policy.py`: `boundary_aim`; `native/ladder.py`: `brake_target` and its clamp | Projected stops, legal aim and reactive locomotion braking read the mapped braking value through the athlete view or engine body. |
| `native/reaction_clock.py`: `set_speed`; `native/substrate.py` Keeper unset patch | The threshold reads the body's braking. The 0.40 s multiplier remains the same for everybody. |
| `native/restart_metric.py`: `observe`; `native/rulebook/fatigue_rotation.py`: `advance` | Restart timing estimates and fatigue work read mapped braking. The fatigue baseline caches the mapped values once, before applying existing fatigue multipliers. |
| `core_src/policies.py` history and marking helpers; `core_src/match.py`: `pocket_init` | The legacy readers consume their body values. The old roster initializers and optional Pocket Keeper override are bypassed on the Native roster path. They retain their historical settings for older profiles. |
| `native/roster.py`, `native/port.py`, `core_src/types.py`, `native/attr_sensitivity.py`, `native/prism_lab.py` | Mapping, attribute validation and diagnostic readbacks. |

The RB/3 trial uses one body source for braking and turning. Historical profiles still use their historical defaults. The second pairing's signed margin is Isu’Kari minus Yukïma, and the first pairing's signed margin is Ala minus Garvian.

## Paired games

Garvian Guardians–Ala Apex seeds 1–5 and Yukïma Cowhands–Isu’Kari Sirenwings seeds 1–3. The five Garvian–Ala baseline games were replayed to collect the new observers and checked against the archived T3 fingerprints. All 24 games finished with invariants passing and every restart resolved. No league soak ran. At most two simulator processes ran in parallel.

Counts are per team per game, rates are game-level percentages, and CPU is per game. Differences use the same pairing and seed. A tilde denotes a difference within two paired standard errors.

| Measure | L0 | L1 | L2 | L1 − L0 | L2 − L0 | L2 − L1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Carrier body-outs, total | 19.19 | 18.94 | 21.25 | -0.25 ± 1.31 ~ | +2.06 ± 1.34 ~ | +2.31 ± 0.99 |
| Carrier body-out sideline self-run | 8.44 | 8.94 | 9.69 | +0.50 ± 1.01 ~ | +1.25 ± 0.98 ~ | +0.75 ± 0.65 ~ |
| Carrier body-out sideline after contact | 2.81 | 1.44 | 1.56 | -1.38 ± 0.69 ~ | -1.25 ± 0.48 | +0.12 ± 0.52 ~ |
| Carrier body-out end line self-run | 6.62 | 7.56 | 9.06 | +0.94 ± 0.86 ~ | +2.44 ± 0.78 | +1.50 ± 0.58 |
| Carrier body-out end line after contact | 1.31 | 1.00 | 0.94 | -0.31 ± 0.34 ~ | -0.38 ± 0.42 ~ | -0.06 ± 0.22 ~ |
| Passed balls out | 14.25 | 16.94 | 16.94 | +2.69 ± 1.17 | +2.69 ± 1.23 | +0.00 ± 1.27 ~ |
| Held end-line flights staying in play | 9.00 | 8.69 | 8.06 | -0.31 ± 1.18 ~ | -0.94 ± 0.95 ~ | -0.62 ± 0.92 ~ |
| Possessions/team | 140.62 | 149.19 | 157.00 | +8.56 ± 2.44 | +16.38 ± 2.97 | +7.81 ± 3.24 |
| Mean possession duration (s) | 12.70 | 11.73 | 11.35 | -0.98 ± 0.30 | -1.35 ± 0.24 | -0.37 ± 0.26 ~ |
| Points/team | 84.19 | 91.94 | 92.88 | +7.75 ± 5.94 ~ | +8.69 ± 6.17 ~ | +0.94 ± 4.58 ~ |
| Carry goals | 2.44 | 3.00 | 3.44 | +0.56 ± 0.82 ~ | +1.00 ± 0.78 ~ | +0.44 ± 0.48 ~ |
| Targeted drops | 10.62 | 11.12 | 10.75 | +0.50 ± 0.66 ~ | +0.12 ± 1.51 ~ | -0.38 ± 1.27 ~ |
| Interceptions (ledger) | 26.44 | 31.56 | 35.62 | +5.12 ± 1.34 | +9.19 ± 2.41 | +4.06 ± 2.52 ~ |
| Possession-ending fumbles, classified | 21.38 | 20.56 | 17.94 | -0.81 ± 1.73 ~ | -3.44 ± 1.80 ~ | -2.62 ± 1.02 |
| Event Keeper save rate (%) | 18.78 | 19.73 | 18.76 | +0.95 ± 2.24 ~ | -0.02 ± 1.74 ~ | -0.97 ± 2.28 ~ |
| Takedown success (%) | 13.85 | 12.63 | 13.66 | -1.22 ± 0.55 | -0.19 ± 0.51 ~ | +1.03 ± 0.48 |
| CPU seconds/game | 259.66 | 254.88 | 260.47 | -4.79 ± 1.73 | +0.81 ± 2.06 ~ | +5.60 ± 2.45 |
| Garvian–Ala, Carrier body-outs, total | 19.90 | 21.00 | 23.50 | +1.10 ± 1.59 ~ | +3.60 ± 1.68 | +2.50 ± 1.41 ~ |
| Garvian–Ala, Possessions/team | 142.20 | 147.60 | 160.30 | +5.40 ± 3.07 ~ | +18.10 ± 4.14 | +12.70 ± 2.00 |
| Garvian–Ala, Points/team | 80.90 | 86.00 | 91.30 | +5.10 ± 6.10 ~ | +10.40 ± 8.60 ~ | +5.30 ± 5.30 ~ |
| Garvian–Ala, Second team minus first team margin | 45.80 | 42.00 | 47.80 | -3.80 ± 14.91 ~ | +2.00 ± 16.20 ~ | +5.80 ± 15.53 ~ |
| Yukïma–Isu’Kari, Carrier body-outs, total | 18.00 | 15.50 | 17.50 | -2.50 ± 1.89 ~ | -0.50 ± 1.44 ~ | +2.00 ± 1.53 ~ |
| Yukïma–Isu’Kari, Possessions/team | 138.00 | 151.83 | 151.50 | +13.83 ± 1.36 | +13.50 ± 4.31 | -0.33 ± 5.60 ~ |
| Yukïma–Isu’Kari, Points/team | 89.67 | 101.83 | 95.50 | +12.17 ± 13.77 ~ | +5.83 ± 10.10 ~ | -6.33 ± 7.72 ~ |
| Yukïma–Isu’Kari, Second team minus first team margin | 14.00 | 5.00 | 5.67 | -9.00 ± 11.36 ~ | -8.33 ± 15.65 ~ | +0.67 ± 16.33 ~ |

The 1.5× scale left total body-outs within paired noise at −0.25 ± 1.31. The 2× scale raised self-run end-line exits by 2.44 ± 0.78 versus L0 and by 1.50 ± 0.58 versus L1. Its change in total exits versus L0, +2.06 ± 1.34, remained within paired noise. Possessions rose by 8.56 ± 2.44 at 1.5× and 16.38 ± 2.97 at 2× versus L0. Both matchups’ signed margin differences stayed within paired noise.

The [complete paired tables](rb337/TABLES.md) include per-pairing and combined possession endpoints, line and contact splits, scoring mix, passing, evasion, Keeper outcomes, turning radii and individual scores. A dash marks an unavailable denominator or a contrast with fewer than two paired observations.

## Fumble diagnosis

The observer reconciled all 958 possession-ending fumbles to the box ledger. Other includes 949 witnessed carrier freezes, 0 unresolved forced releases and 0 unlinked ledger attributions. Initial observer smoke records were replayed after the attribution fix.

| Classification | L0 | L1 | L2 | L1 − L0 | L2 − L0 | L2 − L1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Fumble wrap/takedown | 0.12 | 0.25 | 0.19 | +0.12 ± 0.18 ~ | +0.06 ± 0.18 ~ | -0.06 ± 0.06 ~ |
| Fumble strip attempt | 0.00 | 0.00 | 0.00 | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ |
| Fumble collision without grip | 0.00 | 0.00 | 0.00 | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ |
| Fumble reception drop | 0.00 | 0.00 | 0.00 | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ |
| Fumble handoff | 0.00 | 0.00 | 0.00 | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ |
| Fumble other | 21.25 | 20.31 | 17.75 | -0.94 ± 1.82 ~ | -3.50 ± 1.91 ~ | -2.56 ± 1.03 |
| Other fumble, freeze of carrier | 21.25 | 20.31 | 17.75 | -0.94 ± 1.82 ~ | -3.50 ± 1.91 ~ | -2.56 ± 1.03 |
| Other fumble, unresolved forced release | 0.00 | 0.00 | 0.00 | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ |
| Other fumble, unlinked ledger attribution | 0.00 | 0.00 | 0.00 | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ | +0.00 ± 0.00 ~ |
| Related turnover strip attempt | 1.62 | 1.50 | 1.50 | -0.12 ± 0.50 ~ | -0.12 ± 0.45 ~ | +0.00 ± 0.67 ~ |
| Related turnover reception drop | 5.88 | 6.75 | 6.38 | +0.88 ± 0.61 ~ | +0.50 ± 1.36 ~ | -0.38 ± 1.14 ~ |

Strip and reception-drop turnovers are reported separately where the engine uses a different ledger label. The complete tables split each cause by the athlete’s kickoff Ball Handling band. A drop uses the intended receiver’s rating. The `rb337.fumbles` and `rb337.supplemental_losses` records identify the player and available source timing. Evasion outcome definitions are in the [observer documentation](rb337/README.md).

## Gates

- a) full suite. TESTED with `pytest -q b1 native` after the source changes. 839 passed, 23 subtests passed in 590.73s (0:09:50).
- b) six legacy hashes. TESTED byte for byte against `native/evidence/rb3-reach/legacy-hashes.txt`.
- c) L1 seed 1 repeats exactly. TESTED. All archived values except measured CPU and sampled profiling data are equal, including the named box scores and fumble observations.
- d)–h) unchanged (compat, CORE, RB-3.28, RB-3.31, RB-3.32 combined 99-74 trace 0045e62d...2601 state b2b68575...d9de). TESTED against the recorded identities.
- i) A6 (61-105, trace 2437b808...6aee), B4 (57-112, trace f424c4ee...e9c9) and T3 (44-122, trace 539c5548...09c9) seed 1 reproduce exactly with the new switches OFF; record score, trace, state and config digest of L1 and L2 seed 1. TESTED.

| Mode | Score | Trace SHA-256 | State SHA-256 | Config SHA-256 |
| --- | ---: | --- | --- | --- |
| compatibility | 57–76 | `44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072` | `046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d` | `3d66214c927b42abf493bfe93c9d7ef85675364f54b5e6a9f245daadc4799550` |
| core | 61–80 | `c1a578db3f2754d3f69b47ba81a1f9d5b9336e1d87f496de2fa8dc3daee7a256` | `c517e00f864f1438705cdd1d9768d61523ee1aaac69746f57a2e9f1f4adf2745` | `e3eb027d0506db1297def02bb74924cb9c3878fa17226ffb6a47e56722976835` |
| R1 | 85–86 | `a399f74f81d891c8a0cd4014fc5d10bc5623ad835c448932a94cd50ffac7ac4b` | `bc4898a8229d147bd60defdc623db55fac13a3845fb5f29f812198b4bf5f61d4` | `3af62b414b132cad51d1547dd1abb6bc735fef5a147d41aafebc3475b414df5e` |
| PLANNED | 64–96 | `ab86f8befcf2baca264ab87fabdd39af3e218cb80032eab52b356a089319a08a` | `e8318c85ba3ae5205861d138f8d4f63e16202dd6d84f4ab8b5df02066e141047` | `117f5525293e5a2a24476697e32278ca4fec2cb761a8e8df299e57e2d19410bc` |
| RB332 | 99–74 | `0045e62d5de38fc85a6c38fd58298284f637bb6d1766ddb7d50cfb159ac22601` | `b2b6857584bbdc7c486b54f52bd8ebf9c2c89fde8e15893a42c70f5c3be9d9de` | `374ab384a9a9fb5e777a0415e76a7131dc3b58ffc01ec527695c0724a149434d` |
| A6 | 61–105 | `2437b8084c08d99b954395db42c7b55bdad93402586796a9bdd4ad665dd16aee` | `e10536f2eb9366ba3d2ea3a8e38a741e93b387bdc15ef3d80dc6f2b53661eeaa` | `c6dfe491fdb0dc792a7c4c9c12c803bad5fee1d5173edd874800fe7be1e7bd44` |
| B4 | 57–112 | `f424c4eefded4723efe017b2b86dea0c2ce252d587d79e7cddb899138443e9c9` | `1d701334a0a83c26a77e4b41fd091d68958ab481442d2e10888b49e950298d82` | `a3b387b7f81193daa6321db0b3670798edc4acb6e653e9160a7f9edb87badbe1` |
| L0 | 44–122 | `539c554801a03f2645627110264112ff67f55b3ff21b6182bf6241efb22309c9` | `0383c42494aa3d8f601c149d54de2d1c119d7c30639d4a064b326b3dd6a39793` | `9342b188992c593fc9533826695fcc439ab183c428189a5aa5aa77a85b78e386` |
| L1 | 74–102 | `358b01cb4ce1043580023148bdf18eb89d8b5e1f86a7eb48ef62dc37b1442237` | `9555a4dc39e559e2e6b4fadd5e8183e129f6737c7d5f0775d5e40e994ccfc02d` | `4866ffee07894eda6b22d1d0ed7c0c5a8653cec95fac60f4f76968c3901f9c69` |
| L2 | 60–147 | `6fd45925b9f1779da2117a41fa8a19c77630ae9b4836abebe686cd6ac3cf53ee` | `7cc1a09805c5b15bdb5edfb2fb988fe98f0cbfc7dcb02a280603af87a6fb6908` | `1858e2c42485398ee8ce682ebd3606fbc145c6aa28218a55ac8024333cd0f1f6` |

Legacy 3,000-step windows, seeds 1 and 3.

```
native-v0/2 1 bae2fd67c560f8cf0c6b3b21df7a97c7675942eb10213dc7f2c823117f793dff 71404bda04ae86480f59001b5b8ada97e3eaedb759047bc9b6a1861555d03aff f31b44a1eb787f14c9d606be74fa40658c6b7b9772ee1e882b075b856edc3035
native-v0/2 3 26e98a2289deb7925aa39ea2f66ef63e325f937718848471546abd92e353e390 22b137e5614a359a63c3126f52cb2779ce17553b43bd8bb1e7db085e56321d88 f31b44a1eb787f14c9d606be74fa40658c6b7b9772ee1e882b075b856edc3035
native-v0/3 1 22dd578040e924d2bd438a60e461ef90d61c6a69ad80b5806ce150ed8492837e 952b220f540319c72b0c4b5816beeadb8998efe39ad9c590e1a5cccc19c6ea4e 2e90666654a575ce158fea7781fc5bb2aade49ec1996d4d98ee447c317bf626b
native-v0/3 3 1ff87cd2fb2f40f34e749bd57f753cd705353d283cbe1fb0f05c628796aa6e08 e8b777d95758df9f2894c2f2ab5d3b4f60728035bac6f842cf05e3669a4235d4 2e90666654a575ce158fea7781fc5bb2aade49ec1996d4d98ee447c317bf626b
native-rb/2 1 250e79ce04701352dc2baa66a847b6b161a43cbc6707710e3dc8b3bbe713d13b b479da4538a5103bf1bd83a06ba54ecd0b62668b21c856152c94538e9153770a 383e127fa59b439efb51cce2fbc42351beb9e01e8f94bf28d5af70274b07c1f5
native-rb/2 3 27a32d2bf27f8b1342378e1bb001c2450f0407f1c9fca25571c3db30a79139e1 1e60bca9ac1e7a5fb9ef6ddd12e8a648b1ada1bcf254b054187b1e9f138ec535 383e127fa59b439efb51cce2fbc42351beb9e01e8f94bf28d5af70274b07c1f5
```

## Reproduction

The [reproduction guide](rb337/README.md) pins the workbook and lists the match, aggregation and verification commands. Each gzip file under [raw evidence](rb337/evidence/) embeds both the named JSON box score and named CSV box score. Game keys follow `{arm}-{pair}-{seed}`, with 0 for Garvian–Ala and 1 for Yukïma–Isu’Kari. Historical replays, the L1 repeat, the legacy hash report and the full suite log are in the same directory.

```bash
python3.13 -m audit.native.rb337.tables audit/native/rb337/evidence audit/native/rb336/evidence /tmp/rb337-tables.md
cmp /tmp/rb337-tables.md audit/native/rb337/TABLES.md
python3.13 -m audit.native.rb337.check
```

## Open questions

No CANON interpretation was needed. The two scales remain trial settings.
