# SPRINT30 LIMITATIONS

Experimental evidence only. **Nothing here is ACCEPTED; no milestone is declared accepted.** Every module below is labeled `PRIMITIVE:`/`PROVISIONAL` in code and registered in `b1/registry.py`.

## PRIMITIVE / PROVISIONAL modules

| registry key | what it is / simplifies | how it limits validity |
|---|---|---|
| `cognition.option_scoring` | PRIMITIVE: hand-set rule-based option values for all roles; no learning, no lookahead, no teammate-intent model. | Match statistics (scores, pass rates, turnovers) say nothing about real PRISM cognition quality; values are untuned. |
| `cognition.home_position` | PRIMITIVE: slot-grid formation assigned from outside the athlete (deviation from BA-7). | Team shape is imposed, not perceived or chosen; violates BA-7; any spacing result is an artifact. |
| `cognition.believed_carrier` | PRIMITIVE: carrier inferred as nearest perceived non-archer body within 1.8 m of the perceived ball. | Mis-attributes the carrier in crowds; press/mark/archer targeting inherit that error. |
| `cognition.archer` | PRIMITIVE+PROVISIONAL (R-RS, ARC-1): targets only the believed opposing carrier, never a Keeper; fixed 2.5 s self-imposed interval. | Archer behaviour is not evidence for the open Archer foul mapping (SELF-1) or the 1.0.2 target policy; 0 freezes were observed in the seed-1 match. |
| `cognition.keeper` | PRIMITIVE+PROVISIONAL (U-1..U-4): line positioning and a save intent from perceived ball velocity; Keeper-zone canon unresolved. | Only 1 save intent in the seed-1 match: Keepers almost never react in time; Keeper-zone behaviour is not canon. |
| `sensor.ball_as_body` | PRIMITIVE: the ball is fed to the B0 PRISM perception model as one more body (same FOV, latency and noise as an athlete). | Ball visibility/noise is not a calibrated ball-perception model; airborne balls are treated as near-ground bodies. |
| `sensor.public_signals` | PRIMITIVE: phase, clocks, score, restart spot/team/taker delivered instantly as public officiating signals. | Assumes every athlete hears/sees every signal instantly, including possession clock and restart taker designation. |
| `sensor.gaze` | PRIMITIVE: gaze focus is the athlete own believed ball position; with no belief the body facing is used. | No scanning policy; athletes who lose the ball rely on memory ("search"). |
| `motor.pass_release` | PRIMITIVE: release-time aim uses the B0 plan_pass on the intended receiver true kinematics (receiver cannot be replaced: pass_ranked is empty). | Pass accuracy does not degrade with the passer belief error about the receiver; only the choice of receiver is belief-driven. |
| `motor.shot` | PRIMITIVE: shot aimed at the intent aim point with the B0 release-state / perturbation physics. | Shot placement choice is one of two fixed corners. |
| `motor.archer` | PRIMITIVE: ballistic lead from the intent believed position and velocity; nominal target height 1.4 m; low arc only; no obstacle check. | No friendly-fire/obstacle legality check before release; legality is whatever the B0 engine enforces. |
| `motor.keeper_save` | PRIMITIVE+PROVISIONAL: a B1 keeper_save intent enables the B0 C4c dive/step planner, which tracks the true flight at motor level; without the intent the planner is masked. | Save execution quality is the B0 kernel, not belief-limited; only save timing/attempt is owned by B1. |
| `motor.contact_kernel` | PRIMITIVE: grip/hold/escape micro-behaviour and catch/jump reflexes are the B0 C3/P4 physics kernels, not B1 decisions. | Tackle/hold/strip decisions inside reach are engine reflexes: "tackle" in B1 is only the choice to close on the carrier (press). |
| `procedure.dead_ball` | PROVISIONAL: restart placement (taker walks to mark, opponents clear) is the B0 engine procedure targets_dead; the taker chooses the receiver; after 3 s without a choice the B0 pass-into-space fallback fires. | Restart positioning is not athlete-owned; restart delay timing is provisional; engine fallback may pass into space. |
| `procedure.substitutions` | PRIMITIVE: rotation/substitution is the B0 bench procedure. | No coach/bench cognition (158 engine substitutions in the seed-1 match). |
| `procedure.penalty` | PRIMITIVE: penalty phase uses the same B1 option scoring; no dedicated penalty cognition. | Penalty phase behaviour unvalidated (no penalty observed in recorded runs is asserted). |
| `match.regulation_profile` | PRIMITIVE: default run uses the B0-P4-DEFAULT profile (2 x 120 s, ruleset 1.0.1), the same profile as M1; not the 4 x 600 s league profile. | "Regulation" here means the B0-P4-DEFAULT 2 x 120 s profile on ruleset 1.0.1. The 4 x 600 s league profile and RULES_V03 were not run. |

## Open canon gates (not resolved, not invented)

- **U-1..U-4 (Keeper-zone rules), ball-clock/zone rules, R-RS (rules-state table):** B1 adds no rule. All rule enforcement is the frozen B0 engine on ruleset 1.0.1. B1 Keeper behaviour is PROVISIONAL.
- **SELF-1 / Archer foul mapping:** not implemented in B1; the Archer primitive only targets the believed opposing carrier and never a Keeper (PROVISIONAL). Engine legality decides everything else.
- No `UnresolvedOutcome` type was needed/raised because B1 never adjudicates a rule itself; this also means the canon gates are **untested**, not satisfied.

## Known defects and unverified items

- `b1/preservation.py` inventory guard fails on a clean checkout: 23 of 235 inventory entries were never committed to git (pre-existing at `8d98234`). 212 present files are byte-identical and `git diff 2abe497` shows no B0 file changed (tested separately).
- Spec deviation BR-3: `decide(view, belief)` takes two arguments (inherited from M1), not a single AthleteView.
- Spec deviation BA-7: slot-grid home positions.
- Public `Signals` include `possession_ms` and restart taker designation delivered without latency.
- `view.holds_ball`, own x/y, posture and quiver count are exact proprioception (no noise).
- The engine `targets_dead`, substitution, C3 contact and C4c save kernels still act on true state at the physics level (labeled above).
- Motor pass release aims with true receiver kinematics.
- Action-resource model (O4) is reduced to three resources (ball, bow, locomotion), one pending command per athlete, no queued bundles; causal IDs (O5) are string-prefixed chains observation -> decision -> intent -> command, outcomes reference command ids.
- Trace files keep sampled decisions and all ball/bow action chains (capped), not every decision; the trace hash covers every decision row and every outcome.
- No calibration, no statistical validation, no performance budget, no 4 x 600 s run.
- G1 was closed by a new sprint scenario (`--scenario g1`, `g1_close`); the governed G1 commit `c083ae9` on `b1/m1-decision-outcome` was not used (sprint was instructed to start from `8d98234`).
