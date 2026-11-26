# OWNER BRIEFING

1. **DESIGN COMPLETE.** The ladder separates projected beliefs, carrier boundaries, Keeper planting and the final contact gate.
2. **IMPLEMENTED.** Each change is opt-in. The planning copy uses only delivered observations. The boundary judge lets an airborne held ball cross a sideline while its carrier remains in play. The Keeper can plant from a visually observed wind-up. The final gate checks the intended wrap or takedown against fresh believed holder evidence.
3. **TESTED.** Twenty new games cover the four rungs on Garvian Guardians–Ala Apex seeds 1–5. Observed pass arrival and collision timing use the simulation step and logged events. They have the resolution and attribution limits documented below.
4. All specified replay and suite gates passed. The comparison covers one pairing, with five seed-matched differences per full measure.
5. Review the possession and contact results before adopting the combined rung. In particular, test the Keeper trigger against actual shots and examine the remaining stale holder commitments before any tuning. No league soak was started.

## Implementation and call sites

Built from RB-3.34 commit `9d4de6d1630ff23690fabf3e030259f996f5fa1e` on `codex/rb-3-35-turnovers`. Python was CPython 3.13.5. The build used the same workbook, planned rotation and A6 scoring as the parent.

- `native/turnovers.py` centralizes field-clamped projection. It uses the Instinct forecast factor for capture age and the Anticipation factor for time ahead. `prism_core.decide` makes projected planning tracks while retaining original timestamps and raw evidence. `NativePort.core_tracks` skips the former memory extrapolation on this path.
- `cognition._base_decide` consumes projected tracks for option generation, pressure, target pursuit and receiver lead. Pass lead adds wind-up before iterating flight time. Receive and loose-ball pursuit also use the projection helper for their look-ahead. `prism_core.passing` recomputes alternate leads including elected wait. `paired_policy.arrival_clearance` projects defenders through age, wind-up and flight while retaining existing radius growth.
- `cognition_rb3.release_blocked`, `lane_margin`, `shot_plan`, `missed_ball_pursuit` and the later finishing aim use projected positions. `cognition_v3.defender_contact` uses the projected meeting point. The PRISM defender menu and the baseline positioning read the projected planning tracks. `prism_core` projects the pursuit landing, finishing Keeper position and the settle target. Holder freshness uses the capture-time tracks.
- `substrate`, `rules` and `geometry` handle held-ball sideline crossings in the swept boundary judge. The end-line plane and goal-mouth logic retain their original path. `prism_core.carrier` values boundary-crossing carry aims at zero, the value of giving up possession. Under pressure it adds a cut away from the edge and a brace that targets current position and accepts ordinary contact. The stopping envelope uses current velocity, own braking and the minimum body radius. The inward cut uses a 5 m inset.
- `NativePort.capture` records loaded posture or active release wind-up only for already visible opponents of a Keeper. `prism_core.keeper_options` reads it with fresh holder evidence in the existing 40 m shooting range. Plant targets current position. The existing save and movement physics apply.
- `prism_core.decide` records whether contact came from the PRISM defender menu, the baseline or another path. The final gate in `turnovers.gate_contact` checks target and fresh evidence, including release cues. `cognition.decide` applies the same gate on the fallback path.

## Match evidence

- A6 averaged 155.1 possessions, 95.2 points and 33.7 interceptions per team. CPU averaged 244.6 seconds per game.
- B1 averaged 147.3 possessions, 70.6 points and 27.4 interceptions per team. CPU averaged 270.5 seconds per game.
- B2 averaged 153.4 possessions, 79.4 points and 27.5 interceptions per team. CPU averaged 275.0 seconds per game.
- B3 averaged 150.5 possessions, 73.8 points and 25.6 interceptions per team. CPU averaged 272.6 seconds per game.
- B4 averaged 149.4 possessions, 77.3 points and 24.7 interceptions per team. CPU averaged 273.5 seconds per game.

B4 minus A6 possessions per team were -5.70 ± 3.08 paired SE (within two SEs). Points were -17.90 ± 8.27 paired SE. Boundary possession ends were -3.00 ± 2.43 paired SE (within two SEs).
B1 minus A6 open-play believed lane margin was +1.58 ± 1.27 paired SE (within two SEs) m. The true-margin contrast was -0.78 ± 0.57 paired SE (within two SEs) m. These are conditional on an interception.
B3 minus B2 Keeper movement above set speed at release was +3.07 ± 3.95 paired SE (within two SEs) percentage points. B4 minus B3 non-carrier takedowns were -9.25 ± 0.86 paired SE percentage points.
1 held-ball sideline crossings continued play in B2–B4. This count uses an unchanged carrier across physics steps. The swept-crossing test exercises the rule independently of whether it appears in a match.

B1 cut interceptions by -6.30 ± 1.38 paired SE per team and moved the median receiver-to-aim miss by -0.97 ± 0.14 paired SE m. B4 still averaged 149.4 possessions per team against the owner range of 80–110. Its boundary difference from A6 was within two paired SEs.
The B3 and B4 records contain 65 Keeper plant choices and 0 plant witnesses at shot release. The match data leave the proposed shot-time effect unproven.

Over five games, B3 issued 31,412 PRISM defender-menu and 2,469 other contact commands. B4 issued 31,633 PRISM defender-menu and 2,393 other contact commands. The final gate downgraded 1,200 of the B4 other commands. No commands were attributed to the baseline path in either arm. These command counts include renewals. Episode counts group renewals separately.

All 25 arm records reached the final whistle, passed invariants and closed all restarts. Four exploratory processes were stopped before the fixed trial build, and an A6 audit launch hit an observer composition error before running. The completed comparisons use the corrected audit entry point. The first legacy window check exposed older views without switch metadata. The final compatibility guard defaults those views to no switches. The first full suite after that guard found one import-boundary violation. FAB-1 now calls the same helper through the existing cognition interface. The final B4 repeat confirms the active path is identical.

The box Keeper rate divides the recorded save events by the recorded shots faced. The independent event table counts a save when a Keeper touched a projected on-target shot that did not score, divided by the observed reconstructed shots faced.

[Arm means, every adjacent difference and B4 minus A6](rb335/TABLES.md) · [Raw records and named box scores](rb335/evidence) · [Commands and measure definitions](rb335/README.md)

## Gates

- a) Full suite. `824 passed, 23 subtests passed in 622.29s (0:10:22)`.
- b) All six legacy hashes matched byte for byte.
- c) B4 seed 1 matched on an independent repeat, including the diagnostic payload and named box.
- d–g) Compatibility 57–76, CORE 61–80, RB-3.28 85–86 and RB-3.31 64–96 reproduced their full historical identities.
- h) RB-3.32 combined was 99–74. Trace `0045e62d5de38fc85a6c38fd58298284f637bb6d1766ddb7d50cfb159ac22601`, state `b2b6857584bbdc7c486b54f52bd8ebf9c2c89fde8e15893a42c70f5c3be9d9de`.
- i) The five A6 replays matched RB-3.34. Seed 1 was 61–105, trace `2437b8084c08d99b954395db42c7b55bdad93402586796a9bdd4ad665dd16aee`, state `e10536f2eb9366ba3d2ea3a8e38a741e93b387bdc15ef3d80dc6f2b53661eeaa`.

B4 seed 1 was 57–112. Trace `f424c4eefded4723efe017b2b86dea0c2ce252d587d79e7cddb899138443e9c9`. State `1d701334a0a83c26a77e4b41fd091d68958ab481442d2e10888b49e950298d82`. Config `a3b387b7f81193daa6321db0b3670798edc4acb6e653e9160a7f9edb87badbe1`.
