# HP-002 — T6-O4 v3 (DRAFT reconciliation): command arbitration, plans, commitment, coincident events
Claude with Codex R2 response incorporated. **DRAFT. Not frozen. Non-governing.** rc2 and manifest v2 unchanged; Contract v1 NOT FROZEN; B1 not authorized; B0 frozen. Labels: **[B0-VERIFIED]** read from frozen source; **[PROPOSED]**; **[ENG] [BEH] [CANON]** governance class. Supersedes O4 v2 (v2 SUP-10 whole-tick commitment inclusion stays withdrawn).

## 1. Vocabulary (carried forward)
tactical plan → conditional stage → action intent → accepted command bundle → occupied resource lease → queued command. Posture, airborne, grounded, frozen, incapacitated and recovery are **constraints**, not resources.

## 2. Resources and compatibility [ENG, adopted from Codex X-5]
Seven exclusive resources: `locomotion`, `ball_control_release`, `hands_reach`, `contact`, `takeoff`, `archer_draw`, `projectile_release`. A `pose` resource is not added without a concrete limb-conflict model.
| Action | Resources |
|---|---|
| run, cut, pursue, Keeper approach/step | `locomotion` |
| pass, shot, held-ball kick (prep and release) | `ball_control_release` |
| catch prep / standing reach | `hands_reach` |
| jump catch | `hands_reach + takeoff` (atomic) |
| Keeper launch save | `hands_reach + takeoff` (+ `locomotion` only when one atomic command includes a committed lead-in) |
| tackle / grab / brace | `contact`, or `locomotion + contact` (atomic) |
| Archer draw / release | `archer_draw` / `projectile_release` (release depends on a completed valid draw) |
| no-attempt, hold position without movement | none |
Compatibility (YES\* = only under an action-specific separability contract; BUNDLE = only as one atomic bundle): locomotion+ball_control_release YES\*; locomotion+hands_reach YES\*; locomotion+contact BUNDLE; locomotion+takeoff BUNDLE; hands_reach+takeoff BUNDLE; archer_draw+locomotion YES\*; projectile_release+locomotion YES\*; archer_draw→projectile_release atomic transition; ball_control_release+hands_reach NO; ball_control_release+contact NO; hands_reach+contact NO; takeoff+contact BUNDLE only. The table is data with an entry for every pair, checked for completeness and symmetry (SUP-15).
**Queues.** Depth one per resource. A bundle is admitted atomically: all resources start, or the whole bundle queues. If a queued bundle loses any of its queue positions (replacement or invalidation of one component), the whole bundle gets one `queue_replaced` or `queue_invalidated` outcome and none of it runs. Dormant plan stages hold no queue position.

## 3. Plans and stages [ENG/BEH]
- **Foreground executable plan:** at most one per athlete by default (configuration). **Execution-producing stage:** at most one active. A stage may emit concurrent bundles only if they lease disjoint resources under a declared separability contract. Dormant guards and alternative opportunity assessments may coexist, hold no resource and emit no command. Selecting a new foreground plan supersedes the old with a `supersedes` edge and a disposition for each stage and bundle.
- **Opportunity assessment is not unbounded.** It stays inside the existing attention and option-generation model. The plan-count limit simply does not count option candidates.
- **PlanStageActivation record** [PROPOSED, from Codex 3.3]: `plan_id, stage_id, source_decision_id, source_observation_id, trigger_observation_id_or_outcome_id, activated_at, reaction_gate_satisfied_at, guard_evaluation, no_new_option_evaluation: true`. The activated intent keeps the source `source_decision_id`, gets a new `intent_id`, and cannot be backdated. Both the selecting view and the triggering observation are retained.
- **Activation rule** [BEH, default stated]:
```
activation_not_before = max(
    trigger.delivered_at + reaction_delay(athlete, stimulus_class),
    stage.additional_plan_delay_not_before,     # default 0, swept, experimental
    stage.other_declared_temporal_guards)
```
`reaction_delay` is one function used by both the ordinary path and plan activation (disposition R-4). A planned stage therefore saves only the cadence wait, not reaction latency, hand preparation, reach, capacity, security or contention. A faster planned reaction is a possible change from this default and is measured, not assumed. Corridor consistency is computed from the delivered observation and the athlete's belief only, never from the authoritative path.
- **Own-outcome triggers** [BEH]: a stage triggered by the athlete's own release activates at delivery of that outcome and pays the ordinary reaction delay by default. Sweep in Gate C.

## 4. Commitment events [adopted from Codex X-4; UNDECIDED cells stay open]
"Commitment" = first irreversible execution event; intent selection and command acceptance are earlier. Commitment is by **ordered physical events and coincident batches**, not by whole-tick inclusion.
| Action | Commitment event | Class |
|---|---|---|
| Locomotion / cut | each committed integration result is irreversible; future locomotion stays supersedable | KEEP boundary, CHANGE ownership |
| Pass / shot | `ball_release_committed` (atomic carrier-to-flight mutation, B0 release 1077-1095); wind-up is not committed by cognition under the default (§6) | KEEP boundary, CHANGE retarget policy |
| Historical kick | same event; B0 adapter preserved; **not tucked in B0** | KEEP for B0; B1 semantics not inferred |
| Catch / grasp | reach revocable until its declared irreversible phase; outcome commits in the coincident contact batch | CHANGE ownership |
| Jump / Keeper launch | `takeoff_impulse_committed` | KEEP boundary, CHANGE ownership |
| Keeper step save | future steps supersedable; irreversible at committed hand/body contact | CHANGE ownership |
| Tackle / hold | first declared irreversible contact act, else first committed contact impulse | **UNDECIDED** (technique) |
| Archer draw | draw start is execution start; abort policy | **UNDECIDED** |
| Archer release | atomic projectile-release transaction; ammo/legality order | **UNDECIDED, CANON candidate CE-C3** |
| Keeper no-attempt | no command, no commitment | KEEP |
UNDECIDED rows fail validation (SUP-17) until resolved or explicitly waived as out of scope for the scenarios run.

## 5. Coincident-event resolution [ENG]
1. Advance to the earliest candidate sim time. 2. Capture one authoritative pre-event snapshot. 3. Collect all candidates from it. 4. Drop those invalid under the snapshot and resource contracts. 5. Order by causal dependency. 6. For same-state writers without a dependency, apply the versioned pair rule below, or a simultaneous multi-contact solve. 7. Commit one atomic batch. 8. Assign `batch_seq`; emit outcomes; release or transition leases. 9. Evaluate plan guards, then open timing-eligible cognition after the batch.
`batch_seq` is replay identity and batch chronology only. Actor ID, input order, hash-map order and telemetry order never decide a physical result. Candidate input permutations must yield identical state, events, RNG consumption and causal IDs (CE-1).
**Pair table v0** (preservation evidence from B0 line 2346 is not automatic B1 approval):
| Coincident candidates | Proposed resolution | Status |
|---|---|---|
| effective safety/administrative stop vs command | reject command | KEEP |
| strip / possession loss vs held-ball release | loss first; release rejected | B0-compatible [ENG] |
| grounding / tackle outcome vs held-ball release | grounding first; voluntary release rejected | B0-compatible [ENG] |
| freeze-causing Arrow impact vs release/takeoff/contact | impact first; revalidate | B0-compatible [ENG] |
| secure acquire vs unsecured touch/parry on same ball | acquire first; touch rejected | B0-compatible [ENG] |
| opponents secure-acquire same resolved instant | contested/joint control | KEEP concept; native tolerance open |
| independent simultaneous body contacts | one multi-contact solve from common snapshot | REQUIRED [ENG] |
| contact impulse vs release at same instant | solve contact, then realize or reject release from resulting state | proposed [ENG/BEH] |
| contact/grounding vs takeoff | takeoff only if still eligible and feasible | proposed [ENG] |
| Arrow impact on ball vs hand/body contact | simultaneous solve or approved pair rule; never actor order | UNDECIDED (physical) |
| same-team exact-tie secure catches | discriminating metric (continuous contact time, then ball-point distance); joint control if none; check against rc2 PA/TC first | proposed [ENG], rc2 check pending |
| goal/boundary crossing vs secure catch (exact tie) | `tie_rule` slot, ruleset-versioned | **UNRESOLVED_CANON (CE-C2)** |
| clock/period/possession expiry vs release (exact tie) | `tie_rule` slot; B0 ordering (release before clock) held in B0 adapter only | **UNRESOLVED_CANON (CE-C1)** |
| Archer legality/ammo vs projectile creation | atomic transaction; ordering approved by rule | **UNRESOLVED_CANON (CE-C3)** |
**Native tolerance.** B0 runs on integer milliseconds, so same-ms ties are common. "Same resolved instant" must be defined for the native port. Open item for Codex.

## 6. Wind-up revocability [BEH]
**Default:** once release preparation starts, cognition cannot revoke it; authoritative physical and rules interruptions remain (the tuck is one). **Experimental arm:** cognition may abort at an eligible opportunity. If the arm is run, the abort is one atomic transaction that: cancels the pending release and due time; discards command-local wind-up progress; releases or transitions the `ball_control_release` lease into the configured recovery; closes any visible wind-up or communication signal; emits a causal `aborted` outcome; evaluates dependent plan guards from it; consumes no release-error draws; leaves possession, locomotion, momentum, fatigue, contact and posture untouched. The recovery formula and factor exist only inside the arm and are experimental. **B0-VERIFIED:** the tuck is skipped for kicks, is not a cognitive act, and resets nothing else, so it cannot be cited as support for this arm.

## 7. Same-athlete conflicts, queue and inability (carried from v2, adjusted) [ENG]
Intents carry `(decided_at, decision_stage, intent_seq)` with `intent_seq` allocated in canonical pipeline order. Later stages of one plan never supersede earlier ones. Conflicting intents from different decisions in the same tick: higher `intent_seq` supersedes a revocable earlier one (`superseded_before_start`). Queue replacement never touches a committed command. A queued command is invalidated, with a reason and never silently, by a rules stoppage, possession loss, freeze, incapacitation, expiry, a precondition that no longer holds, or the blocker ending in a way the precondition forbids. Promotion re-checks preconditions only and does not refresh the target belief. Inability at acceptance: `rejected / infeasible_at_acceptance`. During execution: `interrupted` or `partial` / `execution_inability`; remaining plan stages get `plan_aborted`.

## 8. Self-knowledge types [BEH]
`MotorFeedback` (Motor Control only, command-local authoritative body projection), `SelfView.proprioception` (sensed own pose, motion, contact, fatigue symptoms), `AthleteKnowledge.self` (stable capability and technique estimates). Cognition cannot import `MotorFeedback` or authoritative state; MC cannot accept `SelfView`. Hidden reserves, exact ratings, hidden timers and implementation-only impairments are not exposed. Default: zero error and latency on sensed pose and motion, and zero-error capability estimates labelled placeholders, not a canon model. Named self-perception parameters replace the IQ sweep.

## 9. Acceptance tests
| ID | Check |
|---|---|
| SUP-2…9, 11…16 | as in v2 |
| SUP-10 | **withdrawn** (whole-tick inclusion) |
| SUP-15 | the compatibility table has an entry for every pair of the seven resources and is symmetric where declared |
| SUP-17 | UNDECIDED / UNRESOLVED_CANON rows fail validation unless waived for the scenarios run |
| SUP-18 | atomic bundle admission: partial queue loss yields one outcome for the whole bundle |
| CE-1 | any permutation of coincident candidates gives identical state, events, RNG consumption and IDs |
| CE-2 | each pair-table row has a fixture with expected outcome |
| CE-3 | opposing same-instant secure acquires yield joint control; tolerance test at the native boundary |
| CE-4 | `batch_seq` appears in replay identity and is not read by any resolution code |
| RX-1…4, 7 | as in R2 §2, with the ordinary reaction delay substituted; RX-7 also asserts no B0-style `pass_signal` credit and no change to PHY catch probability for identical command, state and draws |
| RX-5 | compares like-for-like physical readiness and delivered observations |
| RX-6 | sweeps the **additional** `ρ_plan` only |
| RX-8 | activation produces no `OptionTrace` and keeps the source-decision link |
| RX-9 | perturbing the true trajectory with delivered observation and belief unchanged does not change the corridor result |
| AB-1…4 | experimental arm only, as in R2 §3 |
| AB-5 | bounded watchdog with explicit censored/timeout denominators |
| AS-1…4 | as in R2 §4 |
| AS-5 | with the plan subsystem disabled, B1-only configuration changes no B0 hash |
| SELF-1…4 | type-level isolation; poison tests; MC output unchanged under perturbed `SelfView`; sweep over named self-perception parameters |

## 10. Status
Engineering content here is a proposal to Codex for confirmation. Defaults are conservative and none is presented as approved behavior. Still open for Codex: reaction-delay placement, native "same instant" tolerance. Still canon-class and owner-only if the rulebook is silent: CE-C1, CE-C2, CE-C3 (after a rulebook check).
