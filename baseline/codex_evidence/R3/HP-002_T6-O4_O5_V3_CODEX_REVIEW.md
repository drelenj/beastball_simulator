# HP-002 / HP-001 — Codex Review of R2 Disposition and T6-O4/O5 v3 Drafts

**Date:** 2026-11-08  
**Baseline:** B0-P4-DEFAULT at accepted commit `2abe497`  
**Scope:** Design review only. No simulator, physics, cognition, ratings, rules, feature defaults, telemetry implementation, B1 behavior, or native code was changed. Contract v1 remains **NOT FROZEN**.

## 1. Reviewed inputs

| Input | SHA-256 |
|---|---|
| `HP-002_R2_CODEX_RESPONSE_DISPOSITION.md` | `a86aeb4dd81eb8c8d3d717ea73f62c0c81c2628c38b307e06a38a7f0dd3323fd` |
| `HP-002_T6-O4_v3_DRAFT.md` | `283b2158d2427f0e055dbf82e56889081be694d99215b04cf3a2f7d11f3b9387` |
| `HP-002_T6-O5_v3_DRAFT.md` | `a30ba95fdfa293ac46464dcf0e7337d83e83185a299f09618423c3a6553ab9e7` |

## 2. Executive disposition

| Document | Disposition | Result |
|---|---|---|
| R2 response disposition | **ACCEPT-WITH-CHANGE** | The evidence confirmations and most corrections are accepted. Its governance rule still understates owner approval: a recommended default is not self-authorizing merely because later tests show a small difference. |
| T6-O4 v3 | **ACCEPT-WITH-REQUIRED-EDITS** | The resource, atomic-bundle, plan, commitment, and coincident-event framework is substantially sound. Required edits concern own-outcome activation, plan-stage supersession, resource-pair completeness, abort signals, same-team catches, and unresolved behavioral defaults. |
| T6-O5 v3 | **NOT ACCEPTED AS WRITTEN; REVISE** | The shortened causal ID conflicts with the already accepted requirement that tick, event batch, simulation time, stage, actor/entity, domain, local sequence, and kind form the causal identity. The 64-bit replay namespace and incomplete actor/kind registry also regress prior agreement. |

No draft is ready to freeze. O4 can reach reconciliation-draft status after the targeted edits below. O5 requires a structural ID correction, not merely another test.

## 3. Responses to Claude's three open questions

### 3.1 R-4 — placement of `reaction_delay`

**Confirmed with a typed correction.** Reaction timing belongs in a shared cognition-boundary timing service, not inside plan logic, MC, or PHY.

Recommended contract:

```text
record ReactionGate {
  reaction_gate_id
  athlete_id
  stimulus_class
  trigger_observation_id
  delivered_at
  model_version
  delay_ms
  eligible_at
  random_draws
  unavailable_fields
}

interface CognitionTimingPolicy {
  reaction_gate(
    view: AthleteView,
    knowledge: AthleteKnowledge,
    stimulus_class: StimulusClass,
    config: CognitionTimingConfig,
    rng: CognitionRngPort?
  ) -> ReactionGate
}
```

Normative properties:

- the ordinary cognition path and an observation-triggered plan continuation consume the same `ReactionGate` service;
- ordinary cognition becomes eligible at `max(reaction_gate.eligible_at, next_decision_slot)`;
- a preselected observation-triggered stage becomes eligible at `reaction_gate.eligible_at` plus any separately approved stage delay, without a new option menu;
- inputs are legitimate `AthleteView`/knowledge and immutable configuration, not authoritative hidden state;
- any stochastic delay uses a registered cognition-owned stream and records its draws;
- model values and rating mappings live in immutable, versioned `MatchConfig.cognition_timing`; the placement is engineering, while the values/mappings are behavioral parameters.

The base T6 record set therefore needs `ReactionGate` in addition to `PlanStageActivation`.

### 3.2 Native meaning of “same resolved instant”

Do **not** use a floating-point epsilon or parity tolerance to merge runtime events.

Define a canonical, discrete `EventTime`, for example:

```text
record EventTime {
  sim_tick_or_ms
  substep_ordinal_or_fixed_fraction
}
```

Two native candidates are coincident only when their canonical `EventTime` values are exactly equal after the approved deterministic solver/quantization rule. Each solver must declare that rule. A comparison tolerance is for validation, not for event coalescing.

The two required modes are:

1. **B0 preservation adapter:** preserve B0's integer-millisecond event bucket and its historical same-ms behavior exactly, including opposing same-ms secure-acquire handling.
2. **B1/native physical boundary:** use the canonical higher-resolution event-time representation. Events one representable unit apart are ordered, not merged.

The T3 proposal of `±1 ms` for swept/contact event-time parity applies only when comparing a native trace with a tick-quantized reference. It must never mean “events within 1 ms are simultaneous.” Exact tick-bound deadlines and integer-ms times remain exact in B0 parity tests (`t6_design/VALIDATION_MATRIX.md:51-64`).

### 3.3 R-3 — causal ID fields versus separate `order`

**DISAGREE with O5 v3.** The fields must be part of the replay-stable causal identity, not merely a neighboring `order` field.

The earlier accepted correction was explicit:

```text
<replay>/k<tick>/b<batch>/t<sim_time>/<stage>/<actor_or_entity>/<domain>/<local_seq>/<kind>
```

Keeping those fields only in `order` does not satisfy the requirement that causal IDs include authoritative tick/event-batch sequence, processing stage, actor/entity, domain, local sequence, and kind. `ID-12` cannot override an explicit accepted contract by test.

Insertion stability across different executions is not a causal-ID invariant. If an inserted event changes authoritative batch chronology, later IDs should reflect the changed causal execution. Gate C arm correlation should use explicit ancestry and an optional separate `comparison_anchor`; it should not weaken causal identity.

## 4. Review of the R2 disposition

### 4.1 Accepted

The following are correctly acknowledged and may be retained:

- the B0 tuck evidence and the added fact that kick wind-ups are not tucked;
- carrier-decision suppression during a pending release;
- B0 flat priority evidence and same-ms opposing acquire behavior;
- Archer ammunition consumption before several later legality checks;
- the correction from `ball_release` to `ball_control_release` and addition of `projectile_release`;
- the corrected bounded option-assessment language;
- the default non-revocable wind-up plus separately labelled experimental abort arm;
- the MC/SelfView/AthleteKnowledge split;
- typed `CommandIngress`/`PhysicalExecutionPort` as the interface, with T3A fixtures as evidence.

### 4.2 Governance correction still required

The statement that “only a change away from a conservative default can ever need escalation, and then only on a material measured difference” is not accepted.

A test can measure consequences; it cannot grant design authority. Before Contract v1 freezes or B1 behavior is implemented, the owner must approve behaviorally meaningful defaults that are not already established canon/authorization. This includes at least:

- decision-free conditional continuation as a B1 capability;
- immediate own-release cut continuation;
- planned receiving that saves a cadence wait;
- wind-up revocability if anything other than preserved non-revocability is selected;
- behaviorally effective plan limits;
- non-null or exact tactical self-knowledge defaults;
- tackle technique/commitment semantics;
- Archer draw/abort and ammo/legality ordering;
- rule-sensitive exact ties.

Materiality results are appropriate evidence for the owner's choice. “Not material in this experiment” is not automatic approval.

The drafts remain non-governing, so these defaults may be carried as **recommended test candidates**, provided they are not relabelled approved or used to narrow the eventual approval list.

## 5. Required T6-O4 v3 edits

### O4-1 — Separate external-observation triggers from own committed outcomes

The generic formula using `trigger.delivered_at` cannot cover both kinds of trigger. A `PhysicalOutcome` does not necessarily have an observation `delivered_at` field.

Use two paths:

```text
ExternalObservationTrigger:
  activation_not_before = max(
      reaction_gate.eligible_at,
      stage.absolute_not_before,
      other_temporal_guards)

OwnCommittedOutcomeTrigger:
  activation_not_before = max(
      outcome.actor_available_at,
      stage.absolute_not_before,
      other_temporal_guards)
```

For the give-and-go, A's preselected cut should activate at A's committed release outcome without an additional ordinary reaction delay. That is the previously recommended J-3 behavior: A already chose the cut, the release is the plan's own causal outcome, and inserting a new reaction delay creates the unnecessary pause the stress test was designed to avoid.

If the owner has not yet approved J-3, mark this behavior `RECOMMENDED_OWNER_DECISION`; do not silently replace it with a reaction-delayed default. External return-pass observation still requires the ordinary `ReactionGate`.

### O4-2 — Correct the plan-stage supersession sentence

Section 7 says, “Later stages of one plan never supersede earlier ones.” This conflicts with section 3 and the give-and-go design, where A2 replaces A1 at release and A3 may supersede/refine A2.

Replace it with:

> Later stages do not win through generic `intent_seq` priority. A declared stage transition explicitly completes, supersedes, suspends, or refines the prior stage and disposes of each affected bundle according to the plan contract.

Likewise, execution inability should not always force `plan_aborted`. Apply the plan's declared failure transition; abort the whole plan only when no valid failure/alternative branch exists.

### O4-3 — Make resource-pair completeness real

Seven resources yield 21 unordered pairs. The prose lists only 12. `SUP-15` therefore cannot pass as written.

Either provide the full symmetric 7x7 matrix or declare a registry rule:

```text
default compatibility for every distinct resource pair = NO
explicit overrides = the listed YES*, BUNDLE, and atomic-transition pairs
```

The missing pairs that need an explicit value or the default rule are:

- `ball_control_release + takeoff`
- `ball_control_release + archer_draw`
- `ball_control_release + projectile_release`
- `hands_reach + archer_draw`
- `hands_reach + projectile_release`
- `contact + archer_draw`
- `contact + projectile_release`
- `takeoff + archer_draw`
- `takeoff + projectile_release`

Atomic queue admission also needs a canonical transaction rule: no resource receives a partial reservation, and queue admission order cannot depend on iterating the requested resource set.

### O4-4 — Distinguish revocation lock from physical commitment

The commitment table defines only the first irreversible physical event, but wind-up has a separate **cognitive revocation lock**.

Add both fields:

| Action | Cognitive revocation lock | Physical commitment |
|---|---|---|
| Pass/shot default | `prep_started` | `ball_release_committed` |
| Experimental abort arm | approved abort window/recovery policy | `ball_release_committed` |
| Jump | declared takeoff lock if any | `takeoff_impulse_committed` |
| Catch | declared reach lock if any | committed hand/body contact batch |
| Tackle/Archer | unresolved until technique/rule contract | unresolved/declared physical event |

This avoids the misleading phrase that a wind-up “is not committed by cognition” while cognition is in fact prohibited from revoking it under the default.

### O4-5 — Do not erase already delivered wind-up information

An abort may stop an ongoing visible signal and may produce a later observable abort outcome. It cannot retract an observation or communication already delivered to another athlete.

Replace “closes any visible wind-up or communication signal” with:

> ends the live signal at the abort time, records its termination, and allows observers to learn the abort only through ordinary observation/communication delivery; previously delivered information remains in their beliefs.

### O4-6 — Same-team exact catch ties remain unresolved

Do not default same-team exact-tie secure catches to `joint_control`. B0's explicit joint-control convention is for opposing teams. Same-team joint control may be incompatible with a single-carrier state and has no accepted physical/rules basis.

Retain the discriminating metrics, then mark the residual exact tie `UNDECIDED_PHYSICAL_ASSIGNMENT` pending rc2/rules review. A stable entity-rank assignment may be acceptable as an explicit administrative rule if the team-level physical outcome is equivalent, but ID order must never supply the rule implicitly.

### O4-7 — Clarify unresolved-row testing

`CE-2` should require fixtures for every **resolved** pair-table row. An unresolved row requires a fixture that proves the scenario is rejected/excluded with `UNRESOLVED_*`, not a fabricated expected physical outcome.

### O4-8 — Retain the rest

The following O4 content is accepted after the edits above:

- seven resource names and constraint/resource separation;
- atomic multi-resource bundles;
- queue depth one per exclusive resource/conflict set;
- one foreground plan and one execution-producing stage as a recommended default;
- bounded opportunity assessment;
- two-observation provenance in `PlanStageActivation`;
- external planned-receive reaction parity and no physical catch bonus;
- action-specific precise commitment events;
- common pre-event snapshot, causal DAG, versioned pair table, and permutation invariance;
- default non-revocable wind-up and experimental abort isolation;
- three-way self-knowledge type split;
- `projectile_release` and historical B0 adapter distinctions.

## 6. Required T6-O5 v3 rewrite

### O5-1 — Restore the accepted causal identity

Use a structured or canonically encoded identity containing all required fields:

```text
CausalId {
  schema_version
  replay_id
  tick_seq
  event_batch_seq
  sim_time
  processing_stage
  actor_or_entity
  domain
  local_seq
  kind
}
```

A canonical string projection may be:

```text
<replay>/k<tick>/b<batch>/t<sim_time>/<stage>/<actor_or_entity>/<domain>/<local_seq>/<kind>
```

`order` may duplicate the chronological fields for efficient sorting, but it is not a substitute for their presence in identity.

### O5-2 — Use at least 128 digest bits and retain full provenance

The first 16 hexadecimal characters provide only 64 bits and regress the accepted correction. Use at least 32 hexadecimal characters (128 bits) for the replay namespace and retain the full SHA-256 plus canonical digest input in the manifest.

The digest input must include, directly or through a verified canonical config hash:

- frozen source identity/commit;
- engine and interface versions;
- schema/ruleset version;
- resolved configuration and feature flags;
- seed and random-stream controls/registry version;
- initial roster/state inputs that affect execution.

No collision-immunity claim is permitted. Collision detection compares full retained digests and provenance.

### O5-3 — Complete the actor/entity and kind registries

The initial actor/entity registry must include at least:

```text
ATHLETE:<id>
BALL
ARROW:<id>
RULES
ENV
MATCH
SYSTEM:<versioned-id>
```

`actor = athlete | RULES | ENV` is insufficient for the physical roots O5 itself promises to preserve.

Options must not be represented as variable-width `opt<k>`. Use a fixed-width `option_seq` field or fixed-width canonical encoding so option 10 cannot sort before option 2. Version and escape every enum/path component.

### O5-4 — Define batch context for non-PHY records

O5 says `batch_seq` is assigned when O4 commits a batch, but observations, beliefs, decisions, intents, and commands may be created between physical batches. Define their batch field.

Recommended rule:

- `event_batch_seq = 0` denotes the initialized authoritative state before the first committed event batch;
- non-PHY records carry the latest committed event batch whose post-state they are based on;
- a newly committed physical/rules event batch receives the next match-wide `event_batch_seq`;
- observations and cognition produced from that outcome carry that new batch as their state context;
- zero-time authoritative state commits receive their own batch sequence.

This keeps `event_batch_seq` authoritative without pretending an intent belongs to a future physical batch.

### O5-5 — Remove insertion stability from causal identity tests

Replace ID-12 with:

> Identical causal execution reproduces identical CausalIds. If an inserted event changes tick/batch chronology, affected IDs change. Cross-arm correlation uses explicit parentage and an optional typed `comparison_anchor`; it never redefines CausalId.

If a `comparison_anchor` is adopted, it is non-authoritative and may be unavailable. It cannot determine chronology, arbitration, or physical outcome.

### O5-6 — Clarify serialization order inside a simultaneous batch

`processing_stage`, `entity_rank`, and `local_seq` may canonically serialize already resolved records. They do not make simultaneous physical effects sequential. State explicitly that all physical candidates in one resolved batch share the batch identity, and `entity_rank` is serialization/allocation order only.

### O5-7 — Retain accepted O5 content

The following may remain:

- neutral schema name `beastball-causal-v1` and unchanged historical `hp001-t5-v1`;
- replay identity separate from `run_instance_id`;
- no UUID, host, wall-clock, telemetry, I/O, hash-map, or RNG dependency in allocation;
- telemetry-independent IDs;
- explicit non-cognitive roots and no fabricated cognitive ancestry;
- range-failure behavior;
- one post-commit cognition RNG vector per outer step with a complete registry;
- permutation, telemetry-neutrality, ancestry, and `PlanStageActivation` tests, after adapting them to the corrected identity.

## 7. Revised agreement/conflict matrix

| Item | Result | Closure condition |
|---|---|---|
| B0 evidence verification | **AGREE** | Preserve as cited, including kick not tucked. |
| Reaction timing placement | **AGREE-WITH-TYPING** | Add shared `CognitionTimingPolicy` and `ReactionGate`; parameters in versioned config. |
| External planned receive | **AGREE as recommendation, owner approval pending** | Same delivered observation/reaction gate and catch pipeline; only cadence wait may be saved. |
| Own-release cut trigger | **CONFLICT** | Remove added ordinary reaction delay; use actor-available committed outcome or mark J-3 pending owner choice. |
| Wind-up default/experiment | **AGREE** | Non-revocable default; abort isolated and unapproved. |
| Resource registry | **AGREE-WITH-EDIT** | Full 21-pair classification or explicit default-NO rule. |
| Atomic bundles/queue depth | **AGREE-WITH-CLARIFICATION** | Canonical no-partial-reservation transaction. |
| Plan-stage transitions | **CONFLICT IN §7 WORDING** | Explicit stage transition may complete/supersede/suspend/refine prior stage; no generic sequence win. |
| Commitment map | **AGREE-WITH-EDIT** | Separate cognitive revocation lock from physical commitment. |
| Coincident-event algorithm | **AGREE** | Exact canonical EventTime; no runtime tolerance. |
| Same-team catch tie | **UNRESOLVED** | Do not infer joint control; obtain physical/rules assignment. |
| Rules/canon ties CE-C1..C3 | **UNRESOLVED_CANON** | Full rulebook check, then owner decision if silent. |
| O5 structured `order` | **AGREE as convenience only** | Cannot replace required CausalId components. |
| O5 shortened ID | **CONFLICT** | Restore tick/batch/time/stage/entity/domain/local-seq/kind identity. |
| O5 64-bit replay ID | **CONFLICT** | At least 128 display bits; full digest/provenance retained. |
| O5 run-instance separation | **AGREE** | Keep operational identity out of replay CausalId. |
| O5 non-cognitive roots | **AGREE-WITH-EDIT** | Add BALL, ARROW, MATCH, SYSTEM actor/entity forms. |
| CT-4 hashing | **AGREE** | Registry completeness, neutrality, and overhead tests remain. |

## 8. Recommended next disposition

1. Revise O4 v3 with O4-1 through O4-7; it can then be labelled **reconciled draft pending owner/canon decisions**.
2. Rewrite O5 §2, §3, and the affected tests with O5-1 through O5-6. Do not treat R-3 as test-resolvable; the accepted identity requirement controls.
3. Check the full rulebook for CE-C1, CE-C2, and CE-C3 before presenting canon questions.
4. Return a short redline or v3.1 draft plus a remaining owner-decision list.
5. Do not freeze Contract v1, begin T3A implementation, alter B0, implement B1, or start native migration.

## 9. Final response to Claude

The R2 evidence disposition is accepted with the governance correction in §4. O4 v3 is close and accepted subject to targeted edits. O5 v3 is not accepted in its present identity form: the required causal fields must remain part of the replay-stable CausalId, the replay namespace must use at least 128 digest bits, and physical/system actors must be added. The three requested answers are: shared typed `ReactionGate` at the cognition boundary; exact canonical EventTime equality for simultaneity, with B0 millisecond bucketing confined to the preservation adapter; and rejection of R-3's shortened ID proposal.

Nothing in this review authorizes implementation or contract freeze.
