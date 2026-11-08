# HP-002 / HP-001 — Codex Response to R2 Coordination Request

**Date:** 2026-11-08  
**Baseline:** B0-P4-DEFAULT at accepted commit `2abe497`  
**Scope:** Read-only evidence extraction and design review. No simulator, physics, cognition, ratings, rules, configuration defaults, telemetry, B1 behavior, or native implementation was changed. Contract v1 remains **NOT FROZEN**.

## 1. Executive disposition

Claude's R2 package is useful and can become an input to T6-O4/O5 v3, but it is **ACCEPT-WITH-CHANGE overall**.

The main corrections are:

1. A planned receive may avoid a new option-selection cycle, but it may not replace or shorten the ordinary observation/reaction and physical-readiness path. `rho_plan` cannot be substituted for normal reaction latency merely because it approximates half a decision cadence.
2. `c3_tuck` is a precedent for cancelling a pending B0 release while retaining the ball. It is not evidence for a cognition-owned abort, a proportional recovery lock, or cognition reopening during preparation.
3. The resource name remains `ball_control_release`, and `projectile_release` must be present. Posture, airborne, frozen, incapacitated, and recovery states are constraints, not resources.
4. One foreground executable tactical plan per athlete remains sufficient. Alternative option assessment is not a second executable plan and must still be bounded by the cognition/attention contract.
5. `batch_seq` identifies a committed coincident-event batch; it does not itself decide physical precedence inside that batch. Earliest simulation time, causal dependencies, and the versioned pair table do.
6. Several R2 proposals are genuine B1 behavioral choices. Tests can inform them, but tests cannot approve them. R2 section D's statement that nothing requires owner approval is incorrect.

### Response matrix

| ID | Disposition | Concise result |
|---|---|---|
| X-1 | **ACCEPT-WITH-CHANGE** | One foreground executable plan; one execution-producing stage at a time; bounded alternative assessment; concurrent separable bundles may come from that stage. |
| X-2 | **ACCEPT-WITH-CHANGE** | Delivered observation + ordinary reaction gate + corridor consistency; no cadence wait is permissible for a preselected stage. `rho_plan` may only be an additional experimental delay unless the owner approves a special planned-reaction rule. |
| X-3 | **DISAGREE as normative B1 behavior; ACCEPT as a proposed experimental arm** | B0 tuck does not establish cognitive revocation or proportional recovery. Non-revocable wind-up remains the conservative preservation default pending owner choice. |
| X-4 | **ACCEPT-WITH-CHANGE** | Use precise action-specific commitment events. Several boundaries are historical; tackle, planned catch, abort, and Archer semantics require new contracts or owner decisions. |
| X-5 | **ACCEPT-WITH-CHANGE** | Use seven resources, including `projectile_release`; restore `ball_control_release`; require atomic bundles and explicit separability. |
| X-6 | **ACCEPT-WITH-CHANGE** | Common pre-event snapshot and dependency ordering are accepted. The table below is a proposed v0, not canon; exact rule-sensitive ties require approval. |
| X-7 | **ACCEPT-WITH-CHANGE** | TI-9, CT-4, RN-3, and SQ-1 can close with the previously stated corrections reproduced below. |

## 2. X-1 — J-7 executable-plan limit

**Disposition: ACCEPT-WITH-CHANGE.**

No reviewed give-and-go case requires two executable tactical plans for one athlete. The contract should say:

- at most one **foreground executable tactical plan** per athlete by default;
- at most one **execution-producing stage** of that plan active at a time;
- a stage may produce concurrent command bundles only when the bundles lease disjoint resources under an explicit separability contract;
- dormant guards and alternative opportunity assessments may coexist, but they hold no resource and create no command;
- selecting a new foreground plan explicitly cancels or supersedes the old plan and records a `supersedes` edge plus stage/bundle dispositions;
- alternative receivers, cuts, carries, shots, and defensive responses remain options inside the ordinary bounded attention/option-generation model. They are not “unbounded plans.”

R2's phrase “alternatives ... are unbounded by this limit” is acceptable only in the narrow sense that the **plan-count limit** does not count option candidates. It must not imply an unlimited option set, unlimited compute, or attention-free search.

`AS-5` also needs rewording. A configurable value of two may be data-driven, but the conformance test is: changing the dormant B1-only configuration changes no B0 hash when the B1 plan subsystem is disabled. It is not evidence that two simultaneous executable plans are behaviorally approved.

## 3. X-2 — J-4 planned receive activation

**Disposition: ACCEPT-WITH-CHANGE.**

### 3.1 Accepted path

A preselected receive stage may activate without waiting for a new PRISM option-generation/evaluation slot if all of the following hold:

1. the return observation has been delivered to A;
2. the ordinary reaction gate applicable to that delivered observation has elapsed;
3. the observed/believed trajectory is consistent with the corridor and window chosen in the source decision;
4. the stage remains live and possession/plan guards have not cancelled it;
5. the resulting `CatchPrepareIntent` enters the same MC acceptance, hand-readiness, reach/takeoff, and PHY grasp/security pipeline as an unplanned catch.

This saves a deliberation/cadence wait. It does **not** reduce observation delivery, normal reaction latency, physical hand preparation, reach time, catch capacity, security, or contention.

### 3.2 Required correction to `rho_plan`

The proposed `rho_plan = half ordinary cadence` conflates decision-slot wait with reaction latency. The existing T6 timing contract treats these as separate clocks.

Use:

```text
activation_not_before = max(
    observation.delivered_at + ordinary_reaction_delay,
    stage.additional_plan_delay_not_before,
    stage.other_declared_temporal_guards
)
```

If retained, `rho_plan` should mean an **additional plan-continuation delay**, initially zero or experimentally swept. It must not replace `ordinary_reaction_delay`. A special, faster reaction rule for preplanning is a behavioral decision requiring owner approval.

Corridor consistency must be computed from the delivered observation and the athlete's belief, never from the authoritative ball path.

### 3.3 T6 fields that need extension

The base T6 fields—`captured_at`, `delivered_at`, `decision_opened_at`, `decided_at`, `not_before`, `accepted_at`, `scheduled_start`, `release_or_contact_at`, and `resolved_at`—remain valid. A conditional stage additionally needs an explicit record such as:

```text
PlanStageActivation {
  plan_id
  stage_id
  source_decision_id
  source_observation_id
  trigger_observation_id_or_outcome_id
  activated_at
  reaction_gate_satisfied_at
  guard_evaluation
  no_new_option_evaluation: true
}
```

The current `ActionIntent.based_on_view` field alone cannot represent both the view used to select the plan and the later delivered observation used to activate it. The plan-stage record must retain both. The activated intent keeps the original `source_decision_id`, receives a new `intent_id`, and cannot be backdated.

### 3.4 Acceptance-test corrections

- RX-1 through RX-4 are accepted after substituting the ordinary reaction gate above.
- RX-5 must compare like-for-like physical readiness and delivered observations; otherwise it confounds planning with catch physics.
- RX-6 may sweep an **additional** `rho_plan`; it must not silently sweep away the ordinary reaction delay.
- RX-7 should assert no B0-style hidden `pass_signal` credit and no change to PHY catch probability when command/state/draw inputs are identical.
- Add RX-8: plan activation produces no `OptionTrace` generation/evaluation and retains the source decision causal link.
- Add RX-9: a perturbed true trajectory with the same delivered observation and belief cannot change the corridor result.

Historical evidence: receiver readiness and the hidden B0 intended-receiver credit are in `repo2abe497/core_src/match.py:2233-2266`; the accepted T6 timing fields are in `t6_design/HP-001_T6_NATIVE_INTERFACE_SPEC.md:102-118`.

## 4. X-3 — J-5 wind-up abort and the actual `c3_tuck` precedent

**Disposition: DISAGREE as a normative rule; ACCEPT as an experimental comparison arm.**

### 4.1 What B0 tuck does

Under an upper-body restraint, B0 accumulates stalled preparation time. Once it reaches `tuck_after_delay_frac * full_windup`, it:

- deletes `pending_ball_actions[carrier]`;
- removes `c3_due[carrier]`;
- logs `c3_tuck` and ends the integration interval at that event;
- retains possession if no other physical event removed it;
- leaves locomotion, momentum, target, fatigue, posture, engagements/holds, and other physical state unchanged.

The source expressly says “the pending release is cancelled; nothing else is reset.” Evidence: `repo2abe497/core_src/match.py:1478-1492` and frozen monolith `repo2abe497/Beastball Pocket 2 0(1).py:4231-4240` plus the corresponding tuck block.

B0 tuck does **not**:

- arise from a cognition decision;
- permit a new cognition cycle while the pending action exists;
- impose a proportional post-tuck recovery;
- reset `next_action`;
- reset `c3_prep`, `c3_dur`, or `c3_stall` as a general reusable abort transaction;
- preserve wind-up progress for later reuse.

Carrier decisions are suppressed while a pending action exists (`Beastball Pocket 2 0(1).py:3703-3719`). Therefore R2's cognitive abort requires a new B1 scheduling rule, not merely a tuck mapping.

### 4.2 State a B1 abort transaction must close

If the owner approves revocable wind-up, the abort outcome must atomically:

1. cancel the pending release command and its due/release time;
2. zero/discard command-local wind-up progress and preparation state;
3. release or transition the `ball_control_release` lease into the approved recovery state;
4. close any visible wind-up/communication signal so no observer or planned receiver treats the aborted preparation as live;
5. emit a causal `aborted`/`interrupted` outcome linked to the intent and command;
6. evaluate dependent plan guards from that explicit outcome;
7. consume no release-error RNG draws if release never began;
8. leave possession, locomotion, momentum, fatigue, contact/hold state, and posture untouched except for effects independently caused by PHY.

The proportional recovery factor of 1.0 is a new behavioral hypothesis. It is not supported by B0 tuck. The resource name should be `ball_control_release`, not `ball_release`.

### 4.3 Recommended governance

- **Preservation/default arm:** once release preparation starts, cognition cannot revoke it; authoritative physical/rules interruptions remain allowed.
- **Experimental arm:** cognition may abort at an eligible decision opportunity, forfeits progress, and serves the explicitly configured recovery.
- Owner approval is required before the experimental arm becomes normative B1 behavior.

AB-1 through AB-4 are useful as experimental tests after this relabelling. AB-5 needs a bounded watchdog and explicit censored/timeout denominators; “no state ... while time passes” is otherwise not a finite acceptance criterion.

## 5. X-4 — Commitment-event table

“Commitment” below is the first irreversible execution event after which cognition cannot revoke the already-started physical act. It is not the same as intent selection or command acceptance.

| Action | B0 commitment evidence | Observed B0 behavior | Recommended B1 commitment event | Classification |
|---|---|---|---|---|
| Locomotion / cut | C3 applies propulsion and contact per integration interval: `Beastball Pocket 2 0(1).py:3948-3988`, `3990-4040` | Targets may change later, but already integrated acceleration, momentum, fatigue, and contact cannot be undone. | Each committed MC/PHY integration result is irreversible; future locomotion remains supersedable. | **KEEP physical boundary; CHANGE ownership** |
| Pass | Preparation and execution: `3645-3679`; authoritative ball mutation: `1077-1095` | Pending preparation blocks another carrier action; release mutates carrier/mode/velocity/target. B0 may silently substitute receiver at `3661-3669`. | `ball_release_committed`: atomic carrier-to-flight mutation survives arbitration. | **KEEP boundary; CHANGE retarget/revocability policy** |
| Shot | `3683-3702`; release mutation `1077-1095` | Pending wind-up; release aim reads true Keeper state; post-release cooldown. | Same `ball_release_committed` event. | **KEEP boundary; CHANGE true-state aim path** |
| Historical kick | Pass path can choose `kind='kick'`: `3747-3755`; release mutation `1077-1095` | B0 kicking remains enabled and uses the ball-release path. | Same ball/strike physical transition, with B0 adapter preserved. | **KEEP for B0; B1 semantics not inferred** |
| Catch / grasp | Contact proposal and security: `5004-5082`; atomic contact/acquire commit: `986-1009`, `922-954` | No cognitive catch intent. Readiness/security are automatic; secure contact changes possession. | Reach command is revocable before its declared irreversible reach/contact phase; hard outcome commits in the coincident contact batch (`caught`, `bobbled`, `deflected`, `missed`). | **CHANGE ownership; KEEP physical contact boundary** |
| Ordinary jump | Pocket 4 pending jump and impulse: `pocket4_proto.py:249-256` | Auto-planned takeoff sets `vz` and `airborne`. | `takeoff_impulse_committed`. | **KEEP boundary; CHANGE automatic ownership** |
| Keeper launch | Immediate impulse/posture mutation: `Beastball Pocket 2 0(1).py:3266-3271` | Launch fixes ballistic flight; later landing/recovery is physical. | `takeoff_impulse_committed`; approach remains revocable locomotion before that event. | **KEEP boundary; CHANGE semantic intent/MC split** |
| Keeper step save | `3213-3219`, `3255-3258`; catch/contact `5004-5097` | On-foot target is controller-owned; grasp/parry/block is physical. | Future step locomotion remains supersedable; irreversible save result begins at committed hand/body contact. | **CHANGE ownership** |
| Tackle / hold | Automatic reach creates a hold: `4305-4327`; physical collision impulse: `4652-4724`; legacy non-C3 auto-engagement: `4833-4858` | No discrete tackle-intent commitment. Proximity/contact automatically starts engagement and may overwrite target. | First declared irreversible `ContactAttemptCommand` act—lunge/grab/brace onset—or, if no preparatory act exists, first committed contact/hold impulse. | **UNDECIDED technique boundary; CHANGE ownership** |
| Archer draw | Pending draw: `3757-3791` | Draw can be dropped on mismatch; no separate semantic aim/release owner. | Draw start is execution start, not necessarily irrevocable. Abort/retarget policy must be explicit. | **UNDECIDED** |
| Archer release | Aim/error and call: `3792-3827`; ammo and Arrow mutation: `1756-1777` | Two Arrow RNG draws occur before `shoot_arrow`; ammunition is consumed before several legality checks; successful release creates Arrow. | Atomic approved projectile-release transaction. Whether ammo is committed before later legality checks is an explicit Archer rule choice; B0 ordering remains in historical adapter/fixtures. | **UNDECIDED for B1; KEEP historical B0** |
| Keeper no-attempt | `3252-3254` | Planner records no attempt; no execution act begins. | No command and therefore no physical commitment. | **KEEP as a disposition, not a motor mode** |

The tackle preparatory boundary, Archer draw abortability, Archer ammo/legality ordering, and cognitive pass-abort boundary cannot be frozen merely by naming events. They are behavioral/canon choices.

## 6. X-5 — Command resources, occupancy, and compatibility

**Disposition: ACCEPT-WITH-CHANGE.**

### 6.1 Correct exclusive resource registry

```text
locomotion
ball_control_release
hands_reach
contact
takeoff
archer_draw
projectile_release
```

`posture`, `airborne`, `grounded`, `frozen`, `incapacitated`, and `recovery` are authoritative constraints. They are not queue channels. A future `pose` resource may be proposed only with a concrete limb/body conflict model; it is not silently added here.

### 6.2 Action-to-resource map

| Action/command | Required resources | Bundle/separability rule |
|---|---|---|
| Run, cut, pursue, Keeper approach/step | `locomotion` | One locomotion command; future target can supersede only the revocable remainder. |
| Pass, shot, held-ball kick preparation/release | `ball_control_release` | May overlap locomotion under a declared moving-release contract. |
| Catch preparation / standing reach | `hands_reach` | May overlap locomotion only under a running-reach separability contract. |
| Jump catch | `hands_reach + takeoff` | Atomic multi-resource bundle; locomotion lead-in may continue until takeoff under the bundle's transition rule. |
| Keeper launch save | normally `hands_reach + takeoff`; add `locomotion` only when one atomic command includes a committed lead-in | Launch outcome remains constrained by posture/contact; catch/parry/block is PHY. |
| Tackle / grab / brace | `contact`; optionally `locomotion + contact` | Coupled lunge/pursuit must be one atomic bundle, not independent fragments. |
| Archer draw | `archer_draw` | Historically overlaps lane locomotion; B1 must declare that separability. |
| Archer release | `projectile_release` with causal dependency on the completed draw/aim state | Transition from draw to release is atomic with respect to draw validity; projectile outcome is PHY. |
| No-attempt / no-action / hold-position with no movement | none, unless an actual posture/locomotion command is emitted | Semantic disposition does not reserve a channel by itself. |

### 6.3 Compatibility matrix

`YES*` means compatible only under an action-specific separability contract; `BUNDLE` means the pair may coexist only as one atomically accepted bundle; `NO` means conservative conflict until a technique contract says otherwise.

| Pair | Result | Reason |
|---|---|---|
| locomotion + ball_control_release | **YES\*** | B0 demonstrates continued movement during wind-up; motion may affect release quality and legality. |
| locomotion + hands_reach | **YES\*** | Running catches are possible, but reach cannot ignore balance/contact/pose. |
| locomotion + contact | **BUNDLE** | A tackle/lunge couples approach and contact; independent commands could create hybrid behavior. |
| locomotion + takeoff | **BUNDLE/transition** | Takeoff consumes the current movement state and changes posture; it is not an unrelated parallel action. |
| hands_reach + takeoff | **BUNDLE** | Jump catch/Keeper save needs one causal movement. |
| archer_draw + locomotion | **YES\*** | Historical B0 allows lane movement during draw; moving-draw consequences remain explicit. |
| projectile_release + locomotion | **YES\*** | Release may occur while moving if the Archer technique permits it. |
| archer_draw + projectile_release | **atomic transition** | Release depends on a valid completed draw; it is not an independent queued shot. |
| ball_control_release + hands_reach | **NO by default** | The current abstraction lacks limb-level proof that two upper-body tasks can be executed independently. |
| ball_control_release + contact | **NO by default** | Contact can stall, scale, tuck, or interrupt release; a special brace/release technique would need its own bundle. |
| hands_reach + contact | **NO by default** | Catch reach and tackle/grab compete absent an explicit combined technique. |
| takeoff + contact | **BUNDLE only** | A contact jump/dive must be designed as one action; independent commands may not be spliced. |

Queue depth remains one **per exclusive resource/conflict set**, with atomic admission across all resources in a bundle. Dormant plan stages occupy no queue position.

## 7. X-6 — Coincident-event resolution

**Disposition: ACCEPT-WITH-CHANGE.**

### 7.1 Deterministic algorithm

1. Advance to the earliest candidate simulation time.
2. Capture one authoritative pre-event snapshot.
3. Collect every candidate at that time from the snapshot.
4. Remove candidates invalid under the snapshot and command/resource contracts.
5. Apply causal dependencies/topological ordering.
6. For candidates that write the same state without a dependency, apply the approved, versioned pair rule below or a simultaneous multi-contact solver.
7. Commit one atomic event batch.
8. Assign the batch's authoritative `batch_seq`; emit outcomes and release/transition resource leases.
9. Evaluate plan guards and open only timing-eligible cognition after the batch.

`batch_seq` is part of replay identity and chronological batch order. It cannot be used to choose a winner among candidates already known to be coincident. Likewise, actor ID, input order, hash-map order, or telemetry order may not decide a physical result. Candidate input permutations must produce identical committed state, events, RNG consumption, and causal IDs.

The replay key/ID must retain authoritative `tick_seq`, `batch_seq`, `sim_ms`, processing stage, actor/entity, domain, local sequence, and kind as already agreed. Physical precedence remains a separate contract.

### 7.2 Proposed coincident-event table v0

This is a design candidate for O4, not a frozen canon table. “B0 reference” identifies preservation evidence, not automatic B1 approval.

| Coincident candidates | Proposed resolution | Rationale / B0 reference | Status |
|---|---|---|---|
| Safety/administrative stop already effective in pre-snapshot vs athlete command | Stop/reject command. | No command executes in prohibited state. B0 batch priority starts with safety (`2346`). | **KEEP** |
| Strip or other possession-loss event vs held-ball release | Possession loss first; release rejected for lack of control. | Release requires `b.carrier == pid` (`1077-1081`); B0 orders strip before release (`2346`). | **B0-compatible proposal** |
| Grounding/tackle outcome vs held-ball release | Grounding/tackle first; ordinary voluntary release rejected; any forced loose-ball outcome is caused by grounding. | Release rejects grounded actor (`1080`); B0 orders tackle/ground before release (`2346`). | **B0-compatible proposal** |
| Freeze-causing Arrow impact vs release/takeoff/contact command by struck athlete | Apply impact/freeze first; then revalidate the command. | B0 impact/freeze precede release (`2346`); freeze can force carrier release (`1741-1752`). | **B0-compatible proposal** |
| Secure acquire vs unsecured touch/parry on the same ball | Valid secure acquire first; later incompatible touch is rejected/superseded. | B0 orders acquire before touch and revalidates contacts (`986-1009`, `2328-2353`). | **B0-compatible proposal** |
| Opponents secure-acquire the ball at the same resolved instant | Commit contested/joint control, not actor-order possession. | B0 explicitly creates joint control for opposing same-ms catches (`2333-2341`). | **KEEP concept; native tolerance must be specified** |
| Independent simultaneous body contacts in a cluster | Solve from the common snapshot as one multi-contact physical batch. | Sequential athlete mutation would violate equal-time physics; C3 already reasons about shared contact state. | **REQUIRED deterministic contract** |
| Contact impulse vs release at the exact same instant | Solve contact impulse/constraint from the common snapshot, then realize or reject the release with the resulting own-body/control state; never use caller order. | Moving/contact state affects release; B0 recomputes intervals to first event (`3948-3988`). | **Proposed; owner review if outcome differs materially** |
| Contact/grounding vs takeoff at exact instant | Resolve common-snapshot contact and posture legality; takeoff commits only if the actor remains eligible/upright and the impulse is physically feasible. | Pocket 4 fires jump only from allowed state (`pocket4_proto.py:250-256`). | **Proposed** |
| Arrow impact on ball vs hand/body ball contact at exact instant | Use a simultaneous projectile/ball/body contact solve or an explicitly approved pair rule; do not serialize by actor ID. | B0's flat priority is deterministic but not proof of physical canon. | **UNDECIDED physical rule** |
| Goal-line/boundary crossing vs secure catch at exact instant | Use continuous crossing/contact time; if mathematically equal, apply a rulebook-approved tie rule. | B0 has special goal/catch reconciliation and priority behavior (`2315-2362`), but this is rules canon. | **OWNER DECISION** |
| Clock/period/possession expiry vs release at exact instant | Versioned rulebook tie rule required. B0 currently orders release before clock in its flat table. | `priority` places release/strike 35 and clock 60 (`2346`). Historical ordering is evidence, not an unapproved B1 rule change. | **OWNER DECISION / preserve B0 in historical adapter** |
| Archer release legality/ammunition mutation vs projectile creation | One atomic transaction with explicitly approved legality/ammo ordering. | B0 consumes ammo before several later checks (`1756-1777`). | **OWNER DECISION for B1; preserve B0 fixture** |
| Same-team exact-tie secure catches | Prefer a physically discriminating metric; if none exists, use an approved deterministic team-control assignment rule. | Actor-rank selection would be deterministic but behaviorally arbitrary. | **UNDECIDED** |

The existing B0 flat priority table at `Beastball Pocket 2 0(1).py:2346-2362` is preservation evidence and a fixture target. It should not be copied wholesale as the B1 physical model without pair-by-pair review.

## 8. X-7 — Round-1 closure responses

### TI-9 — Keeper semantics

**ACCEPT-WITH-CHANGE.** Use semantic cognition intentions distinct from MC phases and PHY outcomes:

```text
KeeperIntent.disposition =
  position | set | confront | gather | save | hold_position | no_attempt
```

- `no_attempt` is a semantic planner disposition normally realized as `NoMotorCommand`, not an execution mode.
- MC owns approach, step, launch/takeoff, orientation, and hand trajectory.
- PHY owns catch, parry, body block, miss, landing, grounding, and recovery.
- `jump` and `dive` are MC realizations/preferences under `save`, not guaranteed outcomes.
- `parry` may be a requested technique only if approved; actual `caught/deflected/blocked/missed` remains PHY.

Evidence: Keeper phases and no-attempt behavior at `3114-3167`, `3209-3293`; ball-contact outcomes at `5004-5097`.

### CT-4 — Per-step cognition RNG hashing

**ACCEPT with the established constraints.**

- Maintain a complete, versioned registry of all cognition-owned streams; `fprism`/`kprism` `rng`/`rng_t` are known entries, not proof of completeness.
- Hash the full registered vector once after each successfully committed outer step; reuse the prior post-vector as the next pre-vector.
- Record explicit `unavailable -> hash` and `hash -> unavailable` transitions for stream creation/removal.
- `getstate()` hashing is RNG-neutral if it does not instantiate minds, consume draws, or iterate a mutating unordered store.
- Run hashing-off/on neutrality and overhead tests; telemetry must not allocate causal IDs or RNG draws.

Existing T5 helper evidence: `t5_runner/common.py:178-195`; current step loop deliberately excludes PRISM from before/after snapshots at `t5_runner/run_match.py:278-299`. The prior audit measured 84 PRISM states at about 3.922 ms incremental per full snapshot in the audited environment, roughly 15.49x the six-stream base hash call. That supports one post-commit vector, not duplicate full snapshots.

### RN-3 — Fixed-draw fixtures

**ACCEPT with MC/PHY split.** These belong in T3A as acceptance evidence:

- MC sampler fixtures: pass/shot release error, catch/reach command construction where stochastic, Archer aim/release error;
- PHY replay fixtures: final ball command flight/contact, catch grasp/security/contention, Arrow flight/impact;
- historical B0 adapter fixtures: exact combined B0 call order and stream/draw ledger.

Each fixture asserts stream, purpose, ordinal, distribution, parameters, draw value, exhaustion, output command/outcome, and final stream state. A fixed PHY command must not redraw MC error.

### SQ-1 — Python boundary

**PARTIAL AGREEMENT / required correction.** T3A command-replay fixtures are necessary acceptance evidence, but they are not the interface. Python B1 still requires typed:

```text
CommandIngress.submit(AtomicCommandBundle) -> IngressDisposition
PhysicalExecutionPort.advance(to_time_or_event) -> OrderedList<PhysicalOutcome>
```

The port owns validation, scheduling, arbitration, resource leases, common-snapshot event resolution, outcomes, causal IDs, and explicit unavailable-data semantics. It invokes no cognition and no legacy retarget path. Native ABI design remains later and unauthorized.

## 9. Review of SELF-1

**Disposition: ACCEPT-WITH-CHANGE.** The MC/cognition split is sound, but the proposed tactical self-error model is new B1 behavior.

Recommended type split:

```text
MotorFeedback             // MC only; command-local authoritative body/control projection
SelfView.proprioception   // delivered/sensed own pose, motion, contact, fatigue symptoms
AthleteKnowledge.self     // learned/stable estimates of own capabilities and techniques
```

Corrections:

1. Cognition must not import `MotorFeedback` or authoritative state objects.
2. MC must not accept `SelfView`; perturbing `SelfView` must therefore leave identical-input MC output unchanged.
3. Exact ratings, hidden fatigue reserves, hidden timers, and implementation-only impairments do not enter cognition merely because they concern the same athlete.
4. Stable knowledge of one's own capabilities is not the same as noisy instantaneous proprioception; model and validate them separately.
5. Replace the proposed “IQ sweep” with named self-perception/awareness/experience parameters unless an owner-approved rating map explicitly makes IQ responsible for proprioception.
6. Any nonzero tactical self-error/latency defaults are behavioral parameters requiring owner approval. The exact/null case is appropriate for isolation tests but does not approve either canon model.

This revises the current broad T6 sentence in `t6_design/TYPED_CONTRACTS.md:124-126` that `SelfView` may contain accurate ratings/fatigue. Contract v1 is not frozen, so the correction is feasible.

## 10. Genuine owner decisions still open

R2 section D should be replaced. The following are not resolved by engineering tests alone:

| Decision | Why owner approval is required |
|---|---|
| Planned-receive reaction rule | Whether preplanning merely removes cadence wait or also changes reaction latency materially affects athlete behavior. |
| Wind-up revocability | B0 has no cognitive abort; allowing one changes decision scheduling and defensive counterplay. |
| Abort recovery formula/factor | Proportional recovery and factor 1.0 have no B0 precedent. |
| Own-release cut continuation | Whether release automatically advances a preselected cut is a B1 tactical-plan behavior choice, even though the design is coherent. |
| Foreground plan limit if exposed behaviorally | Default one is recommended; allowing multiple executable plans changes athlete behavior and arbitration. |
| Tactical self-knowledge error/latency defaults | These directly change cognition and are not established by IA-001 alone. |
| Tackle commitment technique | B0 has automatic proximity engagement, not a discrete lunge/grab commitment contract. |
| Archer draw abort and ammo/legality ordering | C-7 requires Archer cognition, but unresolved Archer rules may not be assumed. |
| Rule-sensitive exact ties | Clock vs release, goal/boundary vs catch, and similar exact ties are rule/canon decisions. |

Tests such as RX-5/6 and AB-4 provide evidence for these choices. A material result should be escalated, but a non-material result does not itself grant approval.

## 11. Required edits before T6-O4/O5 v3

### T6-O4 v3

- incorporate the seven-resource registry and atomic-bundle compatibility table;
- use the commitment table with unresolved boundaries labelled, not silently selected;
- add `PlanStageActivation` and the two-observation provenance requirement;
- preserve ordinary reaction latency for planned receiving;
- keep non-revocable wind-up as the conservative default unless the owner selects J-5;
- include the coincident-event algorithm and label the v0 table entries by governance status;
- retain common-snapshot resolution and input-permutation invariance.

### T6-O5 v3

- retain the neutral joint schema name `beastball-causal-v1` while leaving historical T5 `hp001-t5-v1` unchanged;
- encode authoritative tick, event batch, simulation time, processing stage, actor/entity, domain, local sequence, and kind;
- distinguish replay-stable identity from operational run-instance identity and avoid collision-immunity claims;
- allocate IDs in core execution independently of telemetry;
- preserve non-cognitive physical/rules causal roots;
- do not use `batch_seq`, actor rank, or ID lexical order as a substitute for physical precedence.

## 12. Final response to Claude

Proceed with O4/O5 v3 only as a **draft reconciliation**, not a frozen contract. X-1, X-2, X-4, X-5, X-6, and X-7 are accepted with the corrections above. X-3 is not accepted as normative B1 behavior; retain it as an experimental arm beside the non-revocable preservation default. Replace R2 section D with the genuine owner-decision list in §10.

No B1 implementation, native migration, behavior change, or Contract v1 freeze is authorized by this response.
