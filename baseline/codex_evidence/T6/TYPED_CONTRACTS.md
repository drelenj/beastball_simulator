# Typed Contracts

These contracts are normative, language-neutral algebraic data types. Units are
part of each type. Implementations may use equivalent native representations
only if serialization and invariants remain stable.

## 1. Common value types

```text
type SimTimeMs       = Int64                 // simulation clock, milliseconds
type TickIndex       = UInt64
type Sequence        = UInt64
type Scalar          = Float64
type Meters          = Float64
type MetersPerSecond = Float64
type Radians          = Float64
type Probability     = Float64               // finite, 0 <= x <= 1

type MatchId         = Branded<String>
type AthleteId       = Branded<String>
type EntityId        = Branded<String>
type ObservationId   = Branded<String>
type BeliefRevisionId= Branded<String>
type DecisionId      = Branded<String>
type OptionId        = Branded<String>
type IntentId        = Branded<String>
type CommandId       = Branded<String>
type OutcomeId       = Branded<String>
type PhysicalEventId = Branded<String>
type RngDrawId       = Branded<String>
type ConfigHash      = Branded<SHA256>

record Vec2 { x_m: Meters; y_m: Meters }
record Vec3 { x_m: Meters; y_m: Meters; z_m: Meters }
record Velocity3 { x_mps; y_mps; z_mps: MetersPerSecond }
```

All physical vectors declare the world frame. Observed relative vectors declare
the observer frame and transformation provenance. NaN and infinity are invalid
unless a specific diagnostic type permits them.

```text
enum UnavailableReason {
  not_observed, occluded, outside_attention, not_yet_delivered,
  unknown_to_athlete, prohibited_by_ia001, not_applicable,
  legacy_not_exposed, instrumentation_disabled, not_computed
}

union Availability<T> =
  Available {
    value: T
    provenance: Provenance
    captured_at: SimTimeMs
    delivered_at: SimTimeMs
    confidence: Probability?
  }
  | Unavailable { reason: UnavailableReason; detail_code: String? }
```

An unavailable field carries no placeholder value.

## 2. `SimState`

```text
record SimState {
  match_id: MatchId
  tick: TickIndex
  now: SimTimeMs
  revision: Sequence
  config_hash: ConfigHash
  clock: AuthoritativeClockState
  rules: AuthoritativeRuleState
  athletes: OrderedMap<AthleteId, AthletePhysicalState>
  ball: BallPhysicalState
  arrows: OrderedMap<EntityId, ArrowPhysicalState>
  environment: EnvironmentState
  execution: ExecutionState
  pending_physical_events: OrderedList<PhysicalEvent>
  rng_cursors: OrderedMap<RandomStreamId, UInt64>
}
```

**Invariants**

- `SimState` is an immutable committed snapshot or a private PHY transaction.
- Only PHY/rules may mutate a transaction and commit its successor.
- Cognition never receives this type or a reference into it.
- Ordered collections use canonical stable keys and order.
- `revision` increases exactly once per committed transition.
- True opponent ratings, fatigue, status timers, intents, and RNG cursors remain
  authoritative fields, not view fields.

`ExecutionState` contains accepted/queued command references, body commitments,
pending releases, and interruption state. It is authoritative scheduling state;
only the restricted self portion may be projected into `SelfView`.

## 3. `ObservationFrame` and `AthleteView`

```text
record ObservationFrame {
  observation_id: ObservationId
  observer: AthleteId
  captured_at: SimTimeMs
  delivered_at: SimTimeMs
  sensor_model_version: String
  attention_state: AthleteAttentionState
  observed_entities: OrderedList<ObservedEntity>
  observed_ball: Availability<ObservedBall>
  observed_arrows: OrderedList<ObservedArrow>
  public_match_state: PublicMatchState
  communications: OrderedList<DeliveredCommunication>
}

record AthleteView {
  observer: AthleteId
  frame: ObservationFrame
  self: SelfView
  knowledge: AthleteKnowledge
  belief_revision: BeliefRevisionId
  apparent_legal_actions: OrderedList<ApparentLegality>
}
```

`SelfView` may contain accurate own body state, ratings, fatigue, impairments, and
commitments according to approved self-knowledge. An `ObservedEntity` contains
only observed/inferred appearance and kinematics with uncertainty; it is never a
live athlete object. Apparent legality is advisory and view-relative.

## 4. `BeliefState`

```text
record BeliefState {
  revision_id: BeliefRevisionId
  athlete_id: AthleteId
  based_on: OrderedList<ObservationId>
  prior_revision: BeliefRevisionId?
  effective_at: SimTimeMs
  entities: OrderedMap<EntityId, EntityBelief>
  ball: BallBelief
  arrows: OrderedMap<EntityId, ArrowBelief>
  possession: PossessionBelief
  tactical_hypotheses: OrderedList<TacticalHypothesis>
  update_random_draws: OrderedList<RngDrawId>
}

record Estimate<T> {
  central: T
  uncertainty: UncertaintyModel
  last_evidence_at: SimTimeMs
  provenance: OrderedList<ObservationId>
}
```

Beliefs may be wrong, stale, or explicitly unknown. They may not be silently
corrected from `SimState`. A deterministic update has an empty draw list; a
stochastic update owns named cognition-stream draws.

## 5. `ActionIntent`

```text
record ActionIntent {
  intent_id: IntentId
  decision_id: DecisionId
  athlete_id: AthleteId
  kind: IntentKind
  selected_option: OptionId
  based_on_view: ObservationId
  based_on_belief: BeliefRevisionId
  decided_at: SimTimeMs
  not_before: SimTimeMs
  expires_at: SimTimeMs?
  priority: IntentPriority
  commitment: CommitmentPolicy
  supersedes: IntentId?
  payload: IntentPayload
}

union IntentPayload =
  MoveIntent { destination_belief; route_constraints; arrival_window }
  | PursueIntent { target_belief; intercept_region; contact_purpose? }
  | CarryIntent { direction; maneuver; protect_side; release_plan? }
  | PassIntent { receiver_belief; aim_region; release_window; technique }
  | ShotIntent { aim_region; release_window; technique }
  | TackleIntent { target_belief; contact_region; timing_window }
  | BlockIntent { protected_region; threat_belief; timing_window }
  | CatchPrepareIntent { intercept_region; technique; ready_window; reach_mode }
  | JumpIntent { purpose; desired_takeoff_window; desired_reach_region }
  | KeeperIntent { mode; ball_belief; intercept_region; timing_window }
  | ArcherLaneIntent { lane_destination; threat_constraints }
  | ArcherLoadIntent { arrow_source; desired_ready_by }
  | ArcherAimIntent { target_belief; aim_point; lead_model; hold_window }
  | ArcherReleaseIntent { target_belief; release_window; aim_parent_intent }
  | ArcherHoldIntent { reason; reconsider_at }
  | RestOrRecoverIntent { duration_or_condition }
  | NoActionIntent { reason; reconsider_at }
```

An intent describes desired semantics, not achieved motion. Belief targets are
snapshots or stable belief references; they are not engine entity handles.
Changing action kind or semantic target requires a new intent.

## 6. `MotorCommand`

```text
enum CommandDisposition { accepted, queued, rejected }

record MotorCommand {
  command_id: CommandId
  intent_id: IntentId
  athlete_id: AthleteId
  disposition: CommandDisposition
  rejection_or_queue_reason: Availability<CommandReason>
  accepted_at: SimTimeMs
  scheduled_start: SimTimeMs
  scheduled_release_or_contact: SimTimeMs?
  valid_until: SimTimeMs?
  own_state_revision: Sequence
  payload: MotorPayload
  applied_limits: OrderedList<OwnBodyLimit>
  error_model: ErrorModelReference
  random_draws: OrderedList<RngDrawId>
}

union MotorPayload =
  LocomotionCommand { desired_velocity; desired_facing; braking; turn_profile }
  | PoseCommand { pose; protect_side; transition_duration }
  | BallReleaseCommand { origin; velocity; spin; release_time; technique }
  | ContactAttemptCommand { body_region; direction; brace; contact_window }
  | ReachCommand { hand_targets; arm_trajectory; readiness_window }
  | TakeoffCommand { impulse_request; orientation; takeoff_time }
  | KeeperSaveCommand { step_or_dive; launch; hand_targets; contact_window }
  | ArcherDrawCommand { draw_progression; ready_time }
  | ArcherAimCommand { aim_geometry; stabilization; hold_until }
  | ArrowReleaseCommand { origin; velocity; orientation; release_time }
  | NoMotorCommand { reason }
```

**MC invariants**

- A command references exactly one intent; related command sequences share the
  intent ID and have distinct command IDs.
- MC may use the executing athlete's true ratings, body/fatigue, and physical
  constraints, but may not choose a new semantic target.
- Error sources are explicit. Current B0 Focus is a perception/attention input;
  using Focus as motor error would be a behavioral change requiring approval.
- `rejected` commands still appear in telemetry and lead to an outcome/trace.

## 7. `PhysicalOutcome`

```text
enum OutcomeStatus {
  completed, partial, interrupted, rejected, illegal,
  no_contact, missed, caught, bobbled, dropped, deflected,
  possession_changed, scored, frozen, immune, expired
}

record PhysicalOutcome {
  outcome_id: OutcomeId
  match_id: MatchId
  athlete_id: AthleteId?
  causal_intent: IntentId?
  causal_commands: OrderedList<CommandId>
  emergent_cause: Availability<PhysicalCause>
  status: OutcomeStatus
  started_at: SimTimeMs
  release_or_contact_at: SimTimeMs?
  resolved_at: SimTimeMs
  pre_state_revision: Sequence
  post_state_revision: Sequence
  state_delta: PhysicalStateDelta
  physical_events: OrderedList<PhysicalEventId>
  rules_events: OrderedList<RuleEventId>
  random_draws: OrderedList<RngDrawId>
  interruption: Availability<InterruptionReason>
}
```

An outcome reports what happened, including failure or interruption. Emergent
events such as passive collisions may have no intent or command but must state an
emergent cause.

## 8. `DecisionTrace`

```text
record DecisionTrace {
  decision_id: DecisionId
  match_id: MatchId
  athlete_id: AthleteId
  domain: DecisionDomain
  owner: DecisionOwner                 // athlete, rule, team_planner, legacy_table
  opened_at: SimTimeMs
  completed_at: SimTimeMs
  observation_id: ObservationId
  belief_revision: BeliefRevisionId
  generated_options: OrderedList<OptionTrace>
  selected_option: Availability<OptionId>
  selected_intent: Availability<IntentId>
  decision_random_draws: OrderedList<RngDrawId>
  legacy_provenance: Availability<LegacySource>
  command_ids: OrderedList<CommandId>
  outcome_ids: OrderedList<OutcomeId>
  unavailable_fields: OrderedList<UnavailableField>
}

record OptionTrace {
  option_id: OptionId
  kind: IntentKind
  generation_reason: Availability<ReasonRecord>
  evaluated_value: Availability<Scalar>
  value_components: Availability<OrderedMap<String, Scalar>>
  apparent_legality: Availability<ApparentLegality>
  rejected_reason: Availability<OptionRejection>
}
```

A trace never fabricates option sets or values for legacy code that did not
expose them. Such fields use `legacy_not_exposed`. A root decision links to all
downstream intents, commands, outcomes, rule events, and random draws.

## 9. Configuration and random records

```text
record MatchConfig {
  schema_version; engine_version; interface_version: String
  source_identity: String
  rules: VersionedRuleConfig
  features: OrderedMap<String, ScalarOrBoolOrEnum>
  timing: TimingConfig
  roster_hash: SHA256
  random: RandomConfig
  modules: ModuleConfig
  numeric: NumericPolicy
  telemetry: TelemetryConfig
  supervisor: SupervisorConfig
}

record RandomDrawRecord {
  draw_id: RngDrawId
  stream: RandomStreamId
  ordinal: UInt64
  purpose: String
  distribution: DistributionSpec
  sampled_value: Availability<ScalarOrVectorOrDiscrete>
  causal_id: DecisionId | CommandId | OutcomeId
}
```

The B0 adapter may mark draw details `legacy_not_exposed` while separately
recording pre/post generator state, as T5 does. Instrumentation does not draw.

## 10. Causal ID format

The conceptual canonical form is:

```text
<match>/<tick-or-event-seq>/<actor>/<domain>/<local-seq>/<kind>
```

Escaping, normalization, width, and binary encoding are fixed by a future schema
version. Allocation occurs in canonical stage and actor order. IDs contain no
wall time, process ID, UUID, hash-map order, or random sample.
