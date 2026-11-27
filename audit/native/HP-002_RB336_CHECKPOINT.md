# OWNER BRIEFING

1. **DESIGN COMPLETE.** RB-3.36 separates the corrected carrier end-line rule, equal set-speed rules, the shared reactive delay and the two experimental tackle limits.
2. **IMPLEMENTED.** A held ball can cross wide while the carrier stays in bounds. A genuine goal and free-ball boundary remain swept events. Athletes use their own braking for set speed. Reactive hand contact, tackle authorization and loose-ball pursuit can pay the same 0.10 s unset delay.
3. **TESTED.** Five matched seeds ran on each of C0, C1, C2, T3 and T4. This is evidence about one pairing. The two-tackle rule remains the configured default and T3/T4 remain trials.
4. The focused suite, full suite and replay gates passed. During the first build attempt, a queued reflex cue hit an athlete after substitution and stopped C2 before producing a record. The trial arms now opt in to discarding those cues. The interrupted T3 launch was restarted with the same guard.
5. Keep both limits as trials. If another paired check is authorized, test tackle 3 first. Both limits reduced possessions versus C2, and the added pace effect of tackle 4 versus tackle 3 was within noise in this pairing. No league soak ran.

## Implementation sites

- **Boundary.** `turnovers.boundary_risk` interpolates the lateral coordinate on each planned segment crossing an end line, with a body-radius inset when assessing a leading body edge. `NativePort.view` supplies the athlete’s own radius under the end-line switch. The mouth check uses the hand height and ball radius. `substrate.build_core`, `rules.install` and `geometry.held_endline_in_play` suppress wide held-ball plane events. `NativePort.step` and `geometry.body_out` still adjudicate body contact. The existing locomotion braking buffer remains conservative.
- **Set speed.** `reaction_clock.set_speed` returns 0.40 × effective braking, which derives from Agility. `NativePort.keeper_motor` and the substrate Keeper reaction expression use that athlete’s threshold when switched on. The original unset time remains 0.10 s. In the universal reaction clock it is read as `unset_s` from the historical configuration key.
- **Reactive actions.** `substrate.build_core` shifts the swept hand-reach readiness floor and the hands-set sampling clock for receptions, interceptions and deflection attempts. `ReactionClock` latches speed on release or a new course. A physical body block is passive. `NativePort._submit_intent` starts the wrap/takedown and loose-ball pursuit clocks. Native contact authorization rejects an early tackle reach until the deadline. `MatchDriver.advance` supplies the delivered loose-ball signal. `NativePort.step` applies the deferred pursuit movement and cuts a physics step at a pending deadline. Own passes and carries use their planned timings.
- **Tackle counts.** `RulebookConfigV3` validates 2/3/4. `rules.tackle` retains the same team on any grounding below N. `rules.award` records retained-tackle scrimmage timing and normalizes Nth-tackle restarts like the second-tackle default. `rules.offside` and its procedural timeout caller, `rules.foul`, and `rulebook.discipline.foul` use N for count increases. Defence decrements respect zero and preserve scoring awards. The Native and Rulebook port invariants use 0 through N−1. Ledger turnover attribution recognizes both the original second-tackle and new Nth-tackle labels. Inherited replay code retains its original scale. The view and scoreboard still carry the same count field.
- **Reflex delivery.** `MatchDriver.advance` removes inactive recipients from the reflex batch. `RulebookPort.capture_core_metadata` skips inactive observers when writing the matching public frame metadata. The additional switch defaults off.

## Five-seed results

| Arm | Possessions/team | Median duration (s) | Points/team | Ala minus Garvian | CPU s/game |
| --- | ---: | ---: | ---: | ---: | ---: |
| B4 | 149.40 | 9.52 | 77.30 | 25.00 | 273.46 |
| C0 | 147.40 | 9.51 | 76.20 | 48.00 | 259.12 |
| C1 | 146.10 | 9.93 | 71.80 | 40.40 | 262.90 |
| C2 | 151.40 | 9.12 | 87.30 | 42.60 | 261.20 |
| T3 | 142.20 | 9.17 | 80.90 | 45.80 | 266.65 |
| T4 | 139.10 | 8.96 | 91.80 | 44.80 | 265.64 |

- T3 minus C2 possessions/team -9.20 ± 3.51 paired SE, median elapsed possession duration +0.05 ± 0.26 paired SE (within two SEs) s and Ala minus Garvian +3.20 ± 28.82 paired SE (within two SEs) points. Mean duration changed by +1.15 ± 0.32 paired SE s.
- T4 minus C2 possessions/team -12.30 ± 2.24 paired SE, median elapsed possession duration -0.16 ± 0.34 paired SE (within two SEs) s and Ala minus Garvian +2.20 ± 30.50 paired SE (within two SEs) points. Mean duration changed by +1.38 ± 0.19 paired SE s.

The C1 minus C0 change in Keeper movement above the active threshold was -33.96 ± 3.34 paired SE percentage points. The reported threshold changes between those arms. The event save-rate contrast was within two paired SEs. C2 field catches paid the cost 86.90 times per team per game and interception opportunities paid it 47.90 times.

The old B4 files contain the required common match outcomes. They predate reach-opportunity instrumentation, so the field success split is unavailable for B4. The C0 and C1 controls provide success rates with zero field cost. CPU comparisons against B4 include the cost of the added reaction observer. Hand reach opportunities exclude passive body blocks. Relative success among unset and set opportunities is descriptive because these groups have different approach speeds and situations.

[All arm means, rung differences, SEs and margins](rb336/TABLES.md) · [Raw records and named boxes](rb336/evidence) · [Reproduction commands and definitions](rb336/README.md)

## Gates

- a) Full suite. `836 passed, 23 subtests passed in 596.76s (0:09:56)`.
- b) All six legacy windows matched byte for byte.
- c) T3 seed 1 matched on an independent repeat, including the box and diagnostic payload.
- d–g) Compatibility 57–76, CORE 61–80, RB-3.28 85–86 and RB-3.31 64–96 reproduced the historical identities.
- h) RB-3.32 combined was 99–74. Trace `0045e62d5de38fc85a6c38fd58298284f637bb6d1766ddb7d50cfb159ac22601`. State `b2b6857584bbdc7c486b54f52bd8ebf9c2c89fde8e15893a42c70f5c3be9d9de`.
- i) A6 seed 1 was 61–105, trace `2437b8084c08d99b954395db42c7b55bdad93402586796a9bdd4ad665dd16aee`, state `e10536f2eb9366ba3d2ea3a8e38a741e93b387bdc15ef3d80dc6f2b53661eeaa`. B4 seed 1 was 57–112, trace `f424c4eefded4723efe017b2b86dea0c2ce252d587d79e7cddb899138443e9c9`, state `1d701334a0a83c26a77e4b41fd091d68958ab481442d2e10888b49e950298d82`.

All matches used CPython 3.13.5. Each trial reached the final whistle, satisfied invariants and closed all restarts.

- **C0 seed 1** 66–95. Trace `9874a8e59c2886cfc8195ea44de82fd560e9ff7c92a8240f380a14eb0299fe7b`. State `f0c329192f62c7cce440147427e16158ce31e8213623ccd814496445affd15bb`. Config `ffd7180fdeeaaad1ad312c3588fe3c789949dc8910952d0de7fc0016d800aff8`.
- **C2 seed 1** 95–80. Trace `10bbc5ac89ace5f300a833e95032c40769baee89a1aa81480636451bd094f0ef`. State `cf621d95b70f8cc341afa269dac30f488245921891e6d06e1cffacd8187e60c4`. Config `76ffd9b6385a6fa345493c14d871390691a86aff4fdff32856537761b4315c14`.
- **T3 seed 1** 44–122. Trace `539c554801a03f2645627110264112ff67f55b3ff21b6182bf6241efb22309c9`. State `0383c42494aa3d8f601c149d54de2d1c119d7c30639d4a064b326b3dd6a39793`. Config `9342b188992c593fc9533826695fcc439ab183c428189a5aa5aa77a85b78e386`.
- **T4 seed 1** 58–148. Trace `b9bcc83e14f27229f73bc30e11f7abbc642ee7e0d6b7725b0cd551499f6849d6`. State `4d02b5a6f3d0746220f834898f9565eda1702f63a3c60b88e520c90bd986ea65`. Config `1bfffb8973e17aea2c840be8fd24aa7e7267a6156802d498ef181bf767f45b72`.
