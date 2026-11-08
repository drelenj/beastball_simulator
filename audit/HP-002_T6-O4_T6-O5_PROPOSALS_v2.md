# HP-002 — Revised T6-O4 and T6-O5 contract proposals (v2) with Codex request and response record
Claude, 2026-11-08. **Proposal only. Not governing. rc2 (`a95cdb05…722a`) and manifest v2 are unchanged.** Contract v1 remains NOT FROZEN. No implementation, native work, Keeper optimization, recalibration or rules change is begun. Supersedes `HP-002_PROPOSALS_COMMAND_PRIORITY_CAUSAL_ID_AND_CODEX_COORDINATION.md` (kept as history).

## 0. Codex status: NO RESPONSES OBTAINED
I have no channel to Codex; you relay. Nothing below is marked agreed. Part A is the request with an explicit response form per item, and Part D records every item as `AWAITING CODEX`. I will not infer agreement from silence.

## A. Codex request (please relay verbatim; reply per item with ACCEPT, ACCEPT-WITH-CHANGE or DISAGREE, plus reasons)
**A1. TI-9 Keeper modes.** Is the T6 §6.3 mode list (positional adjustment, set, dive, jump, gather, parry, hold, recovery) complete against B0 Keeper behaviour? Deliver, read-only, the historical Keeper modes with the B0 code path, entry and exit conditions, and any mode not in the list.
**A2. CT-4 / RNG-2.** Can T5's per-step transition hashing include per-athlete PRISM streams (`fprism`/`kprism`, `rng`, `rng_t`) without consuming a draw and at what cost? If not, the per-decision alternative.
**A3. RN-3 / GB-2.** Can T3A express injected draw ledgers for release, catch and arrow so identical commands plus draws give identical outcomes? Which fixtures cannot?
**A4. SQ-1.** Is T6 phase 4 (command-replay physical boundary) a B1 prerequisite, or is T3A command replay sufficient for Python B1? State what B1 needs beyond T3A, if anything.
**A5. T6-O4 extraction (read-only, no behaviour change).** For every B0 action (carry, pass, shot, move, pursue, tackle, block, catch/reach, jump/takeoff, Keeper modes, Archer load/draw/aim/release, restarts), report:
| Column | Content |
|---|---|
| action | name and code path |
| channels | which of `locomotion`, `ball_release`, `contact`, `hands_reach`, `takeoff`, `archer_draw` it occupies (or a channel I missed) |
| commitment boundary | the point after which B0 cannot revoke it, with the event or state that marks it |
| B0 conflict behaviour | what B0 does when a new request arrives: overwrite, ignore, queue, or undefined |
| queue | whether B0 queues at all, depth, and what invalidates a queued item |
| inability | what B0 does when the body cannot execute (limits, fatigue, injury) |
| evidence | file and line, and a trace if available |
**This extraction describes B0; it does not decide B1.** Each B0 behaviour is classified KEEP, CHANGE or UNDECIDED by you; UNDECIDED fails configuration validation (CFG-5) until decided.
**A6.** Acknowledgments from rc2 still outstanding: TI-8 precedence reading; RN-5 cognition-draw invariant; T6's O1–O10 list is stale.

## B. T6-O4 revised: command priority and queueing
Retained from v1: authoritative interruption first; decision-owner authorization; commitment; channel compatibility; deterministic processing.
**B1. Authority order (unchanged).** (1) rules stoppage, (2) authoritative physical change, (3) expiry. These end commands; they are not competing intents.
**B2. Same-athlete, same-tick conflicts.**
- Intents carry `(decided_at, decision_stage, intent_seq)`; `intent_seq` is allocated by the simulation in canonical pipeline order, not by arrival or iteration order.
- Intents from one decision form a **plan** (for example Archer load, aim, release). Later stages never supersede earlier stages of the same plan; they are ordered by stage.
- Two intents from different decisions of the same athlete in the same tick that conflict on a channel: the higher `intent_seq` supersedes if the earlier is revocable. The earlier gets outcome `superseded_before_start`, zero execution.
- Commitment is inclusive: an intent whose commitment point is reached at tick t is committed for all processing at t.
**B3. Queue.** One queued command per channel (depth 1; proposal, configurable only by approval).
- A committed command blocks; a conflicting later same-owner intent is queued.
- **Replacement:** a newer same-owner intent replaces the queued one; the replaced one gets outcome `queue_replaced` with its edge. Queue replacement never touches the committed command.
**B4. Queue invalidation.** A queued command is invalidated, with outcome `queue_invalidated` and a reason, when: a B1 authority event occurs (rules stoppage, possession loss, freeze, incapacitation); its `expires_at` passes; its declared precondition (for example "carrying the ball" for a pass) no longer holds; or the committed command ends in a way its precondition forbids. Invalidations are never silent; cognition learns through its next view of its own state.
**B5. Promotion.** When the blocker ends, a still-valid queued command is promoted. Promotion re-checks preconditions only; MC does not re-evaluate, retarget or refresh the target belief. A stale target is allowed; cognition may supersede it.
**B6. Execution inability.**
- *At acceptance:* the command is infeasible under the athlete's own body limits: disposition `rejected`, reason `infeasible_at_acceptance`.
- *During execution:* the body cannot continue (fatigue limit, injury, constraint): outcome `interrupted` or `partial`, reason `execution_inability`. MC substitutes nothing; the plan's remaining stages are invalidated with `plan_aborted`.
**B7. Compatibility table.** Data, explicit entry for every channel pair (compatible, conflicting, or conflicting-if-condition); no default. Completeness and symmetry are checked.
**B8. Authorization and determinism (unchanged).** Unauthorized issuers get `owner_not_authorized`; results never depend on iteration order.
**B9. B0 is evidence, not authority.** B0 arbitration is not assumed correct for B1; see A5.
**Tests (extends SUP-2…7)**
| ID | Check |
|---|---|
| SUP-2…7 | as in v1 |
| SUP-8 | same-athlete same-tick conflict: higher `intent_seq` wins; loser has `superseded_before_start` |
| SUP-9 | multi-stage plan never self-supersedes |
| SUP-10 | commitment inclusivity: intent decided in the tick the commitment point is reached is queued, not superseded |
| SUP-11 | queue depth 1: replacement yields `queue_replaced` and edge; committed command unaffected |
| SUP-12 | each invalidation cause yields `queue_invalidated` with its reason |
| SUP-13 | promotion re-checks preconditions only; target belief is not refreshed |
| SUP-14 | inability at acceptance versus during execution produce the specified distinct outcomes; plan stages invalidated |
| SUP-15 | compatibility table has an entry for every channel pair and is symmetric where declared |
| SUP-16 | expiry while queued |
| SUP-17 | B0 KEEP/CHANGE/UNDECIDED classification complete; UNDECIDED fails validation |

## C. T6-O5 revised: causal identity, ordering, run identity
**C1. Identity is separate from order.** The ID names an entity; it encodes no time and is never sorted to recover chronology.
`causal_id = <logical_match_id>/<actor>/<domain>/<kind>/<ordinal>`
- `actor`: `A07`-style athlete ID, or `RULES`, `ENV`.
- `domain`: `carry pass shot move pursue tackle block catch jump keeper archer rest rule physics`.
- `kind`: `obs bel dec opt<k> int cmd out rule draw`.
- `ordinal`: counter per (match, actor, domain, kind), allocated by the simulation at entity creation.
**Canonical order** is a separate record field: `order = (sim_ms, stage, actor_rank, local_seq)` with `stage` in the fixed order observe, belief, decide, intent, command, physics, rules. Consumers sort by `order`, never by ID text (test ID-10).
**C2. Logical vs operational identity.**
- `logical_match_id`: first 16 hex of SHA-256 over the canonical config hash and seed. Reproducible: the same configuration and seed gives the same value and the same causal IDs on every replay.
- `run_instance_id`: operational (T5 `run_id`, attempt, start time, host). Lives only in the run manifest and telemetry envelope, **never in a causal ID**. Two runs of one logical match have equal causal IDs and different run instances.
**C3. No fabricated ancestry.** Physical and rules events with no cognitive ancestor (passive collision, bounce, clock-based rule violation, injury threshold) get IDs under `ENV`, `RULES` or the affected athlete, with `causal_intent` absent and `emergent_cause` populated; ancestry reads `not_applicable`. In the B0 tier, ancestry that exists but was not exposed reads `legacy_not_exposed`. An outcome may name a `causal_intent` only if it resolves and `intent.decided_at <= outcome.started_at`.
**C4. Allocation is telemetry-independent.** The allocator is simulation-owned, runs at entity creation, and is a pure counter: no draw, no I/O, no ordering effect. IDs exist with telemetry off; sinks only read them. Adding the allocator is an instrumentation change and triggers the rc2 §8 NI re-runs.
**C5. Time precision, range, overflow.** `sim_ms` is the integer simulation clock in milliseconds (Int64, valid range 0 to 2^53−1 so JSON round-trips exactly); no fractional times; sub-millisecond ordering is `stage`, `actor_rank`, `local_seq`. Ordinals are UInt64 capped at 2^53−1. On exceeding either limit the allocator **raises `id_range_exceeded`**; it never wraps, saturates or truncates. (B0 regulation reaches about 3×10^6 ms; the limit is theoretical.)
**C6. Schema version** `hp002-ct-v1` on every B1-tier record; T5's `hp001-t5-v1` stays the B0 tier.
**C7. Prohibited ID sources:** wall time, UUIDs, hash-map order, RNG draws, process or host IDs, run instance.
**Tests (revised)**
| ID | Check |
|---|---|
| ID-2 | replay of one logical match yields identical IDs and `order` values |
| ID-3 | identical IDs at telemetry off, minimal, full |
| ID-4 | identical under `PYTHONHASHSEED` 0 and 1 and shuffled dict insertion order |
| ID-5 (revised) | IDs are unique within a logical match; different logical matches in parallel never collide; two run instances of the same logical match are equal, not colliding, and are distinguished by `run_instance_id` |
| ID-6 (revised) | every outcome that names `causal_intent` resolves a full chain to an observation; outcomes with no cognitive ancestor carry `emergent_cause`, ancestry `not_applicable`, and no chain; a fabrication detector flags any chain whose times are inconsistent or which links a physical-only event to a decision |
| ID-7 | identical under CPython 3.12 and 3.13 |
| ID-8 | static scan finds no prohibited source in the allocator |
| ID-9 | allocator at the range limit raises and does not wrap; same-ms events ordered by `stage`, `actor_rank`, `local_seq` |
| ID-10 | shuffling ID text does not change chronology recovered from `order`; nothing sorts by ID text |
| ID-11 | allocator with no sink attached produces the same IDs and leaves NI-1…4 unchanged |

## D. Disposition record
| Item | Status |
|---|---|
| A1 TI-9 | AWAITING CODEX |
| A2 CT-4 / RNG-2 | AWAITING CODEX |
| A3 RN-3 / GB-2 | AWAITING CODEX |
| A4 SQ-1 | AWAITING CODEX |
| A5 extraction | AWAITING CODEX; no B0 value is assumed |
| A6 acknowledgments (TI-8, RN-5, stale list) | AWAITING CODEX |
| T6-O4 revised (B1–B9, SUP-8…17) | PROPOSED; commitment values and compatibility table depend on A5 |
| T6-O5 revised (C1–C7, ID-5, ID-6 revised, ID-9…11 new) | PROPOSED |
| Unresolved disagreements | none recorded, because no Codex response exists |
Two choices of mine you may want to overrule: commitment is inclusive at the tick it is reached (B2), and queue depth is 1 (B3).
