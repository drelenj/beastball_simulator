# HP-002 / HP-001 — Give-and-Go Design Stress Test

**Date:** 2026-11-08  
**Status:** Design-only coordination evidence; no contract freeze  
**Baseline:** B0-P4-DEFAULT at commit 2abe497 remains unchanged  
**Authority boundary:** No B0, B1, T3A, physics, cognition, rules, telemetry, or native implementation change is authorized or made.

## 1. Joint recommendation

A give-and-go should be an **athlete-owned conditional tactical plan whose stages are selected or authorized by cognition**, not a stack of future motor commands.

- Athlete A may select “pass, then cut” in one PRISM decision.
- The pass becomes an immediate PassIntent and accepted release bundle.
- The cut is a preselected conditional plan stage. It occupies no command resource and no queue slot before activation.
- A's own committed release activates the already-selected cut without a new option-evaluation cycle. This is plan continuation, not a free tactical decision.
- Athlete B receives no imposed return-pass instruction. After perceiving possession and the field, B independently generates, evaluates, and selects carry, pass, shot, or other options.
- If B selects the return, A's preparation to receive must arise either from an explicitly preselected receive stage after a delivered observation/reaction gate or from A's next ordinary cognition cycle. A plan may not silently choose a new receiver, route, target, or technique.
- Motor queue depth one remains sufficient **per conflicting resource set** if dormant plan stages remain outside the motor queue and newly activated bundles replace rather than accumulate behind an older queued bundle.
- Physical commitment and arbitration must use precise ordered event times and coincident-event batches, not an inclusive “everything in this tick counts” rule.

## 2. What B0 currently does

### 2.1 Pass preparation and release

When the carrier selects a pass, B0:

1. records pass_signal=(recipient, now);
2. computes a preparation delay from ball handling and, where applicable, grip restraint;
3. stores one pending_ball_actions entry containing due time, action kind, and recipient;
4. emits ball_action_prepared;
5. suppresses another carrier action while that pending entry exists;
6. cuts the C3 integration interval at the exact due time; and
7. on the next committed-state decision boundary, attempts release.

Evidence: Beastball Pocket 2 0(1).py:3645-3659, 3703-3719, and 3948-3965.

At release, the C1 path can re-plan from true current state and silently substitute the next eligible receiver when the original is unreachable (3661-3669). That is historical B0 behavior, not acceptable B1 no-retarget behavior. A successful pass sets next_action=now+400 ms (3678-3679).

### 2.2 Continued locomotion

Pass preparation does not stop carrier movement. In the C3 path, motion and contact integrate up to the release deadline before release is attempted. The held locomotion target continues unless the ordinary target-decision cadence admits a new one.

next_action does not generally block upright locomotion: Player.eligible excludes freeze/injury/disqualification but not next_action (line 598). Movement target updates are controlled separately by next_decision (4081-4088). The 400 ms post-release next_action cooldown blocks ball contact/catch and a new carrier action if the passer regains control immediately, but it does not itself freeze running.

Physical limits on overlap are historical acceleration, braking, turning, maximum-speed/fatigue limits, posture and freeze state, contact avoidance, and C3 holds. An upper hold can delay or cancel hand-release preparation; a lower hold can impair propulsion; grounding or loss of control cancels the pending release. Evidence: 3870-3889, 4231-4277, and 4072-4097.

Pocket 4's release sampler incorporates the thrower's current velocity, so movement during preparation can affect the physical release without becoming a new tactical decision (pocket4_proto.py:137-180).

### 2.3 After the pass

B0 has no give-and-go plan memory.

- While the ball is free, team policy produces free-ball chase/shape targets. The intended receiver is specially routed to the observable flight intercept, and next_decision is reset so that target applies immediately (5294-5303).
- The passer can continue moving, but there is no stored “cut after pass” stage. Depending on proximity/rank, the passer may chase the ball or take a generic support position (2695-2714).
- When B secures control, ordinary policy makes B the carrier and gives teammates—including A—formation/escort/support targets (2715-2745). A special return lane is not preserved.
- B's carrier policy is invoked on later engine steps. A pass trigger ordinarily requires more than 180 ms of control (3747-3755), but this is a legacy controller threshold, not a general PRISM reaction contract.
- The B0 PRISM field wrapper updates perception after the wrapped match step and applies with_view to selected movement/pass evaluations. Carrier and off-ball decisions remain embedded in legacy policy scheduling rather than a complete staged give-and-go model (prism_field_v0.py:65-80, 233-277).

B0 therefore permits motion through a wind-up and after release, but it does not represent A's pass-and-cut intention or B's return-pass decision as explicit causal stages.

## 3. B1 plan, intent, command, and resource model

### 3.1 Tactical plan

~~~text
TacticalPlan {
  plan_id
  athlete_id
  source_decision_id
  selected_at
  expires_at
  stages: OrderedList<PlanStage>
  status
}

PlanStage {
  stage_id
  semantic_template
  activation_guard
  cancellation_guards
  activation_mode
  expires_at
  status
}
~~~

A plan belongs to one athlete. It is cognition state, not an MC reservation. It consumes no execution resource and no command-queue slot.

For A:

~~~text
Plan GNG-A
  Stage A1: PassIntent(receiver_belief=B, aim_region=R1)
  Stage A2: MoveIntent(cut_region=R2)
            activates on A1 PhysicalOutcome(release_committed)
  Stage A3: ReceivePreparedStage(from=B, corridor=R3, window=W)
            activates only after a qualifying return-pass observation is delivered
            and its declared reaction gate is satisfied
~~~

Stages A2 and A3 are not new option menus. Their semantic choices were made in the source decision. Activation may instantiate a traceable ActionIntent with activation_source=plan_continuation, but it retains the original source_decision_id and emits no new option evaluation or selection record.

### 3.2 Conditional-stage restrictions

A dormant stage may:

- test an explicitly declared guard against A's own outcomes, delivered AthleteView, A's beliefs, public rules state, or received communication;
- instantiate only the semantic action, target class, and bounds selected earlier;
- derive motor parameters from A's current own-body state when MC accepts it;
- expire, cancel, or fail explicitly.

It may not:

- inspect true state hidden by IA-001;
- rank new tactical options;
- silently change receiver, destination, action kind, or technique;
- create a plan or intent for B;
- bypass observation delivery, reaction delay, or an authoritative physical constraint;
- reactivate after expiry without a new cognition decision.

### 3.3 Object and queue distinctions

| Layer | Give-and-go object | Resource effect |
|---|---|---|
| Tactical plan | A's conditional pass/cut/possible-receive structure | None |
| Dormant/active stage | A1 pass; later A2 cut; optionally A3 receive preparation | None until an intent is instantiated |
| Action intent | PassIntent, MoveIntent, CatchPrepareIntent | Requests MC evaluation |
| Accepted command bundle | Concrete release preparation, locomotion, reach/takeoff commands | Acquires declared resource leases |
| Queued command bundle | One accepted-but-not-started conflicting bundle | Occupies one queue slot on every required exclusive resource atomically |
| PHY outcome | Release, interception, catch, contact, grounding, possession change | Commits state and activates/cancels guards |

## 4. Locomotion/release overlap

### 4.1 Recommended separability contract

A pass-and-cut uses separate bundles because the actions can safely overlap:

~~~text
Bundle P — pass preparation/release
  resources: ball_control_release [exclusive]
  optional: pose [only if later adopted as a resource]

Bundle L — locomotion
  resources: locomotion [exclusive]
~~~

The current locomotion bundle may continue throughout pass preparation. At release commitment, A2 may atomically supersede the revocable locomotion bundle with the preselected cut bundle. Bundle P completes independently.

The separability contract must state:

- locomotion may continue if release is delayed;
- cut activation requires the declared release outcome, not merely scheduled release time;
- cancellation or rejection of the pass prevents an on_release_committed cut stage from activating;
- contact can affect one or both bundles according to authoritative physical state;
- release completion does not erase momentum, contact state, fatigue, or posture.

### 4.2 Physical constraints

Overlap is limited by:

- acceleration, braking, turn rate, fatigue, anatomy, and current velocity;
- whether the release technique permits the current pose and movement;
- restraint of arms/hands, body contact, grip, or loss of balance;
- grounded, airborne, frozen, incapacitated, or recovery state;
- possession and actual ball control at release;
- rules legality at release;
- any explicit MC error model coupling body motion to release quality.

MC may scale, delay, queue, or reject execution within those constraints. It may not stop movement merely because a pass is being considered, and it may not grant ideal release mechanics while ignoring sprinting/cutting consequences.

## 5. B's independent return-pass decision

A's plan can make A cut and can produce an observable call or movement cue. It cannot insert an intent into B.

The B sequence is:

1. B receives delivered observations of the incoming pass and may select catch preparation.
2. PHY resolves whether B actually gains control.
3. B receives proprioceptive/possession outcome plus updated observations.
4. B's next eligible PRISM cognition opportunity opens only after applicable observation delivery, reaction delay, and decision cadence.
5. B independently generates options: retain/carry, return to A, pass elsewhere, shoot, evade, or no action.
6. B evaluates those options using B's beliefs, ratings, policy, communication, and perceived field.
7. Only if B selects A does B emit a PassIntent targeting B's belief about A.

A's call or shared tactical context is evidence in B's view/knowledge, not a command. A team planner may communicate a pattern or assignment but cannot select B's return pass or write B's destination.

## 6. PRISM cadence and plan-stage activation

### 6.1 Three different clocks

The design keeps separate:

1. **Observation/reaction clock:** when an athlete can respond to newly delivered information.
2. **Decision cadence:** when PRISM may open a new option-generation/evaluation/selection cycle.
3. **Plan-continuation trigger:** when a choice already made may advance to its next declared stage.

### 6.2 Activation rules

- **Own release → cut:** A already selected the cut. A's own release outcome is proprioceptive and causally bound to the plan. A2 can activate at the precise release-commit event without another PRISM option cycle.
- **Observed return → receive preparation:** A3 cannot activate before the return observation is delivered and the plan's reaction gate is satisfied. It need not run a new tactical option menu if the receive action and corridor were already selected, but activation is recorded as plan continuation.
- **New tactical choice:** any retarget, alternative cut, abandon-and-defend choice, or unplanned reception requires a normal PRISM decision opportunity.
- **B return choice:** always a normal B cognition cycle unless B independently selected its own prior conditional plan. A's plan cannot waive B's cadence.

Plan activation emits:

~~~text
PlanStageActivation {
  plan_id
  stage_id
  source_decision_id
  triggering_observation_or_outcome
  activated_at
  reaction_gate
  no_new_option_evaluation: true
}
~~~

This record proves continuation was not a free decision cycle.

## 7. Failure and cancellation stress cases

| Case | Required behavior |
|---|---|
| A cancels before release | Only a new authorized A cognition decision, a declared cancel guard, or an authoritative interruption may supersede the revocable pass bundle. A2 does not activate because no committed release exists. |
| Defender delays A's wind-up | Pass bundle remains executing/queued according to physical constraint. Existing locomotion continues if physically possible. The trigger follows actual release, not scheduled time. |
| A is grounded/frozen before release | PHY interruption terminates affected bundles explicitly. Dormant stages requiring release cancel. No cut is manufactured. |
| Initial pass is intercepted | A2 may already be active because A did release and cut; that is realistic. A3 requires a qualifying B-origin return and never activates. A changes to defense only after legitimate observation/belief and cadence unless rules stop play. |
| Ball is deflected but B later controls | B's control is a new physical outcome. B evaluates independently. A3 activates only if its declared observation guard accepts the later B return and remains inside TTL. |
| B catches but holds/carries | Nothing forces a return. A continues the preselected cut until its end/TTL or a later A decision supersedes it. |
| B selects another teammate | A3 does not activate. A's plan cannot reinterpret another pass as the intended return unless the original semantic template expressly covered that class. |
| B's belief about A is stale | B may pass to a stale believed region. MC cannot replace A with a better target. PHY resolves the resulting pass. |
| B begins return, then contact restrains B | Contact can delay, scale, interrupt, or cause explicit tuck/cancellation under the approved physical contract. No silent completion. |
| Return pass is intercepted | A's receive preparation may execute but produces no catch; interception and possession change are PHY outcomes. |
| A is contacted during the cut | Contact modifies locomotion and may interrupt reach/takeoff. It does not erase the plan without explicit cancellation or expiry. |
| Late return after A3 TTL | The stage is expired and cannot resurrect. A responds only through an ordinary current cognition/preparation path. |
| A's cut target becomes stale/blocked | MC follows only selected region/constraints, reports infeasibility, or rejects/interrupts. A new lane requires cognition. |
| Team possession changes | Possession-dependent stages cancel explicitly. Locomotion does not instantly retarget from hidden true state; defensive behavior waits for legitimate observation/cadence unless rules stop play. |
| Match stoppage | Rules constraints interrupt/expire affected bundles. Plans suspend or cancel by explicit policy; no stage fires during prohibited play. |

## 8. Physical-event commitment versus whole-tick inclusion

Commitment should use precise ordered physical events.

A whole-tick-inclusive rule creates failures:

- a tackle at 299 ms and release at 301 ms can both be treated as “this tick” despite real causal order;
- a cut stage can activate from a release that should have been prevented by earlier grounding;
- an interception and B return decision can appear in one broad tick without observation/reaction;
- input iteration order can decide which event appears first;
- resource leases can release too early or too late.

Recommended order:

1. advance to the earliest candidate event time;
2. evaluate coincident candidates against one pre-event snapshot;
3. apply causal dependencies and the approved coincident-event table;
4. commit one event batch;
5. transition bundle leases and plan guards from that committed batch;
6. open only cognition/plan activations whose timing requirements are satisfied.

“Release committed” means the authoritative ball-release transition survived arbitration and entered the committed batch. Scheduled time, attempted command, or tick membership is insufficient.

## 9. Queue-depth finding

### 9.1 Depth one is sufficient

Queue depth one remains sufficient if defined as:

- one executing bundle per exclusive resource;
- at most one queued conflicting bundle per resource;
- a multi-resource bundle is admitted or queued atomically across all required resources;
- a newer authorized conflicting bundle supersedes/replaces the older queued bundle rather than appending;
- dormant tactical stages are not commands and never occupy the queue.

The give-and-go then uses:

- active locomotion bundle for A;
- active pass bundle on ball_control_release;
- dormant cut stage with no lease;
- at release, cut bundle supersedes the active revocable locomotion bundle rather than entering a long queue;
- dormant receive stage with no lease;
- after a qualifying return observation, one receive bundle can combine locomotion and hands_reach, plus takeoff if needed.

### 9.2 What would make depth one insufficient

Depth one fails if implementation:

- pre-submits every future plan stage as a motor command;
- uses one global athlete queue that serializes disjoint resources;
- allows old queued commands to accumulate rather than be superseded;
- models “run, reach, jump, catch” as unrelated queued commands instead of one receive bundle;
- requires speculative commands for every conditional branch.

Those designs should be rejected rather than increasing queue depth. A deeper motor queue would hide stale tactical choices and complicate cancellation.

## 10. Illustrative successful timeline

Times are illustrative design values, not B0 measurements or canon.

| Time | Athlete/layer | Event | Resources/commitment |
|---:|---|---|---|
| 0 ms | A cognition | Eligible PRISM cycle. A selects plan GNG-A: pass to B, cut to R2, prepare for a qualified return in W. | Plan created; dormant stages occupy nothing. |
| 20 ms | A MC | PassIntent A1 accepted. Release preparation begins. Existing locomotion continues. | ball_control_release and locomotion occupied independently. |
| 20–300 ms | MC/PHY | A runs while preparing. Motion, fatigue, and contact affect execution. | Pass revocable until commitment. |
| 300 ms | PHY | Ball release commits. | Pass bundle completes; ball state changes. |
| 300 ms | A plan continuation | A2 guard receives A1's committed outcome. Preselected cut intent instantiates without option evaluation. | Cut bundle supersedes prior revocable locomotion bundle. |
| 300–650 ms | PHY | Ball flies; A cuts. B perceives/tracks and prepares to receive under B's cognition. | A locomotion active; B reach/locomotion may be active. |
| 650 ms | PHY | B secures control. | B catch and possession outcomes commit. |
| 700 ms | B cognition input | B's outcome and updated view are delivered. Reaction/cadence continues. | No forced return. |
| 900 ms | B cognition | B independently evaluates A's cut, defenders, carry, shot, and other passes; selects return to believed A region. | B PassIntent created from B's decision. |
| 920 ms | B MC | Return preparation accepted while locomotion may continue. | B ball_control_release occupied independently. |
| 1,150 ms | PHY | Return release commits. | B pass bundle completes. |
| 1,200 ms | A observation | Return observation delivered; A3 reaction gate begins/is checked. | No command if gate unsatisfied. |
| 1,320 ms | A plan continuation | A3 qualifies inside corridor/window. CatchPrepareIntent instantiates without a new option menu. | Receive bundle acquires hands_reach plus required locomotion/takeoff. |
| 1,520 ms | PHY | Ball-hand intersection and grasp resolve. | Explicit caught/bobbled/dropped/intercepted outcome. |

## 11. Proposed acceptance tests

| Test | Acceptance condition |
|---|---|
| GNG-B0-1 | Historical preparation continues locomotion and preserves B0 hashes under observation-only instrumentation. |
| GNG-B0-2 | B0 pending pass blocks another carrier action but creates no give-and-go stage. |
| GNG-PLAN-1 | Dormant stages consume no resource, queue slot, causal sequence, or RNG draw. |
| GNG-PLAN-2 | A2 activates only from committed A1 release, never scheduled time or failed attempt. |
| GNG-NOFREE-1 | A2 activation retains the source decision ID and emits no new option-evaluation/selection record. |
| GNG-NOFREE-2 | Any retarget or alternative route produces a new PRISM decision and intent ID. |
| GNG-B-INDEP-1 | A's plan cannot create, select, or queue a B intent. |
| GNG-B-INDEP-2 | B's return appears only after B's observation, reaction/cadence eligibility, option set, evaluation, and selection. |
| GNG-OVERLAP-1 | Locomotion and pass preparation overlap on disjoint resources; body motion affects release execution. |
| GNG-CONTACT-1 | Earlier contact/grounding prevents release and therefore prevents A2 activation. |
| GNG-INTERCEPT-1 | Initial interception leaves A's already-activated cut intact until legitimate cancellation/expiry but cannot activate return reception. |
| GNG-STALE-1 | B can act on stale belief about A; MC cannot substitute receiver or aim region. |
| GNG-LATE-1 | Expired receive stage cannot reactivate; late return requires current cognition/preparation. |
| GNG-POSSESSION-1 | Possession change cancels dependent stages without leaking hidden true state into locomotion retargeting. |
| GNG-QUEUE-1 | Successful sequence never requires more than one queued conflicting bundle per resource. |
| GNG-QUEUE-2 | Newer conflicting intent replaces queued bundle with explicit supersession rather than increasing depth. |
| GNG-ATOMIC-1 | Multi-resource receive bundle is admitted/queued atomically; no hands-only or jump-only hybrid remains. |
| GNG-EVENT-1 | Release 1 ms before/after grounding produces different correct outcomes independent of outer tick width. |
| GNG-PERMUTE-1 | Permuting same-time command inputs leaves physical batch, plan activation, IDs, and RNG identical. |
| GNG-TELEM-1 | Telemetry off/minimal/full leaves plan activation, decisions, commands, scheduling, and RNG unchanged. |

## 12. Choices requiring owner approval

| Choice | Joint recommendation | Why owner approval is appropriate |
|---|---|---|
| Conditional continuation without a new full decision cycle | Approve only for stages semantically selected in the source PRISM decision, with explicit guards, TTL, trace, and no new option evaluation | Defines B1 cognition responsiveness and prevents both artificial pauses and free tactical choices. |
| Queue-depth semantics | Approve one queued conflicting bundle **per exclusive resource/conflict set**, not one global athlete queue | A global queue would unnecessarily serialize locomotion and release; deeper queues preserve stale tactics. |
| Immediate own-release trigger | Approve A's preselected cut activating at the committed release event | The athlete knows their own completed release; another decision cycle creates an artificial pause. |
| Return-receive trigger | Approve only after delivered observation plus declared reaction gate; no new option menu if the receive stage was preselected | Preserves reaction delay and information boundaries while allowing a genuine planned combination. |

Already governed or not an owner choice:

- B independently deciding whether to return follows established athlete decision ownership.
- Precise event-time commitment, common pre-event snapshots, and input-permutation invariance follow accepted T6-O4 direction.
- MC/PHY cannot silently retarget under the accepted no-replacement rule.
- Physical constraints and RNG ownership remain engineering/validation matters unless a future proposal changes canon.

## 13. Final disposition

The give-and-go does **not** require queue depth greater than one. It requires a plan layer explicitly outside the motor queue, event-triggered stage activation, and trace evidence that activation performed no hidden tactical selection.

T6-O4 should specify:

1. tactical plans and dormant conditional stages occupy no command resources;
2. only activated intents reach CommandIngress;
3. pass and locomotion may execute concurrently on disjoint resources;
4. preselected cut activation follows the pass's committed physical outcome;
5. B's return pass always belongs to B's cognition;
6. receive preparation obeys observation/reaction requirements;
7. queue depth is one per conflicting exclusive resource set;
8. commitment uses ordered physical events and coincident-event batches, never whole-tick inclusion.

Contract v1 remains unfrozen, and B1/native implementation remains unauthorized.
