# SPRINT45 LIMITATIONS

Experimental evidence only. **Nothing is ACCEPTED; M1 itself is not accepted (H3 open).** Generated from `b1/registry.py`.

## PRIMITIVE modules

| registry key | what it is / simplifies | how it limits validity |
|---|---|---|
| `cognition.option_scoring` | PRIMITIVE: hand-set rule-based option values for all roles; no learning, no lookahead, no teammate-intent model. | Scores, pass rates and turnovers say nothing about real PRISM cognition; values are untuned. |
| `cognition.home_position` | PRIMITIVE: slot-grid formation assigned from outside the athlete (deviation from BA-7). | Team shape is imposed (BA-7 deviation); spacing results are artifacts. |
| `cognition.believed_carrier` | PRIMITIVE: carrier inferred as nearest perceived non-archer body within 1.8 m of the perceived ball. | Mis-attributes the carrier in crowds; press and Archer preference inherit the error. |
| `sensor.ball_as_body` | PRIMITIVE: the ball is fed to the B0 PRISM perception model as one more body (same FOV, latency and noise as an athlete). | Not a calibrated ball-perception model. |
| `sensor.public_signals` | PRIMITIVE: phase, clocks, score, restart spot/team/taker are public officiating signals, delivered exact (no noise) after the athlete own perception latency. | Every athlete receives every rules signal (including passive possession, contested, immune players) exactly, delayed only by its latency. |
| `sensor.proprioception` | PRIMITIVE: own position, posture, ball-in-hand and quiver count are exact (no noise), delivered after the athlete own perception latency. | Athletes never mis-sense their own body or possession. |
| `procedure.archer_platform` | PRIMITIVE: Archer movement along the platform is the B0 engine procedure update_archers (follows the true ball); B1 Archers do not choose their position. | Archer positioning is not athlete-owned and follows the true ball at physics level. |
| `sensor.gaze` | PRIMITIVE: gaze focus is the athlete own believed ball position; with no belief the body facing is used. | No scanning policy. |
| `motor.shot` | PRIMITIVE: shot aimed at the intent aim point with the B0 release-state / perturbation physics. | Shot placement is one of two fixed corners. |
| `motor.archer` | PRIMITIVE: ballistic lead from the intent believed position and velocity; nominal target height 1.4 m; low arc only; no obstacle check. | Arrow aim is a simple ballistic lead; hit rates are not meaningful. |
| `motor.keeper_save` | PRIMITIVE+PROVISIONAL: a B1 keeper_save intent enables the B0 C4c dive/step planner, which tracks the true flight at motor level; without the intent the planner is masked. | Save execution is the B0 kernel reading the true flight; only the attempt and its timing are B1-owned. |
| `motor.contact_kernel` | PRIMITIVE: grip/hold/escape micro-behaviour and catch/jump reflexes are the B0 C3/P4 physics kernels, not B1 decisions. | Tackle/hold/strip decisions inside reach are engine reflexes. |
| `procedure.dead_ball` | PROVISIONAL: restart placement (taker walks to mark, opponents clear) is the B0 engine procedure targets_dead; the taker chooses the receiver; after 3 s without a choice the B0 pass-into-space fallback fires. | Restart positioning and taker selection are not athlete-owned. |
| `procedure.substitutions` | PRIMITIVE: rotation/substitution is the B0 bench procedure. | No coach or bench cognition. |
| `procedure.penalty` | PRIMITIVE: penalty phase uses the same B1 option scoring; no dedicated penalty cognition. | Penalty-phase behaviour unvalidated. |
| `rules.touch_source` | PRIMITIVE: "touching the ball" is derived from the B0 engine carrier, the engine CONTESTED ball mode and engine touch events; B0 has no hand-level simultaneous-touch model, so contests (R-04/R-22) are under-detected. | Contested states are rarer than the canon definition implies; C-1/R-04 behaviour in matches is weakly exercised (unit tests cover the logic). |
| `rules.enforcement` | PRIMITIVE: the possession layer records ZR-1/ZR-C/ZR-T violations and Keeper-protection breaches in its ledger but does not enforce them (no RST-1 restart is injected); the B0 engine keeps adjudicating fouls, restarts and scoring under its own state. | The match is still adjudicated by B0 rules state, so B1 passive possession and the engine owner can disagree; zone-clock and KP violations change nothing in play. |
| `rules.ball_status` | PRIMITIVE: no ball-height input, so a loose ball is always loose_ground; control ending without an engine event is inferred as loose (ledger marks inferred). | loose_airborne never appears; inferred-loose entries are an inference, flagged in the ledger. |
| `rules.keeper_protection` | PRIMITIVE: KP is applied in cognition (no press on a protected Keeper, Archers never target a Keeper inside his zone) and monitored in the ledger (R-15); KP-08 and KP-OG are not implemented. | KP is behaviourally respected only as far as primitive cognition goes; breaches are counted, not penalised. |
| `cognition.archer` | PRIMITIVE: ruleset 1.0.2 target choice from belief (carrier preferred, else opponent nearest the ball), hand-set belief margins (12-62 m, track age <= 700 ms), 2.6 s self-interval; abort_draw when own belief says the release is illegal. No true-state interlock: wrong beliefs become engine fouls. | Archer fouls now depend on belief quality; freeze counts are not calibrated. |
| `cognition.keeper` | PRIMITIVE: line positioning and a save intent from perceived ball velocity. | Keepers rarely react in time. |
| `cognition.m1_delegation` | PRIMITIVE: carry-vs-pass and defender pursuit/lane sub-decisions are delegated to Base A core.decide with its provisional values; shoot, support, mark, pursue, restart and role logic remain Round 1 rule scoring. | Two scoring vocabularies are mixed; Base A values are themselves provisional (M1 not accepted, H3 open). |
| `cognition.pass_lead` | PRIMITIVE: the semantic pass aim is the believed receiver position advanced by believed velocity over a nominal flight time. | Lead quality is not validated. |
| `comms.pass_call` | PRIMITIVE: a passer shout (passer, target, aim) reaches teammates losslessly after their perception latency; no other communication exists. | Lossless team shout is not the M2 communication channel; no plan layer. |
| `motor.pass_release` | Base A pass-release-v1 (draft engineering contract): fixed 27 m/s admission, direction recomputed to the fixed aim, 60 degree bound, rejected_geometry feedback. PRIMITIVE in the match: engine wind-up timing is used for the release instant. | With moving receivers most passes in the seed-1 match did not reach a teammate; the fixed admission speed and missing engine pass planning are the suspected cause (NOT shown). |
| `match.regulation_profile` | PRIMITIVE: B0-P4-DEFAULT profile (2 x 120 s) with ruleset switched to 1.0.2 for the B1 instance; not the 4 x 600 s league profile. | "Regulation" is the 2 x 120 s B0 default profile. |

## Settled rules (decision record D1) and what this build does with them

- Implemented and unit-tested in `b1/possession.py`: direct/passive/contested possession, P-1 threshold (250/500/1000), C-1..C-3, zone clock and its resets, R-01..R-22 as state transitions. Row-by-row status: `b1/sprint45/CANON_NOTES.md`.
- Ruleset 1.0.2 is set on the B1 match instance through the B0 engine configuration switch; B0 files and the B0 default (1.0.1) are unchanged.
- **Not enforced:** ZR-1/ZR-C/ZR-T violations and Keeper-protection breaches are recorded in the ledger only. KP-08 and KP-OG are not implemented.
- Not settled by the record and therefore provisional or raised as `UnresolvedOutcome`: Archer freeze eligibility as a target role, unknown event kinds.

## Deviations and known defects

- Branch created from `4b19719` (prompt Phase A names its parent `77604e1`; section 2 and Phase B name `4b19719`).
- BR-3: `decide(view, belief)` takes two arguments. BA-7: slot-grid positions.
- `b1/preservation.py` inventory guard fails on any clean checkout (23 of 235 inventory files were never committed); a separate git-identity test passes.
- Ingress rejections (`infeasible`, `unknown_target`, `resource_busy`) are derived from true state and fed back as own-action feedback.
- Engine wind-up (`make_pass` preparation) still times the release instant; the release itself is Base A pass-release-v1.
- Legacy engine procedures still run underneath: `c4c_keepers` (under a save intent), `targets_dead`, `update_archers`, `auto_substitutions`, shot preparation.
- Round 1 behaviour changed: pass completion in the seed-1 match is much lower than Round 1 after replacing the true-state pass planner with the release contract. This is one seed; no effect size is claimed.
- Trace files keep sampled decisions, capped action chains, the first 400 ledger entries and 200 release records; hashes cover every decision row, outcome and ledger entry.
- The independent review describes the code when it ran; later fixes are not re-reviewed unless stated in the implementation report.
