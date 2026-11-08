# HP-002 — T6-O5 v3 (DRAFT reconciliation): causal identity, ordering, run identity
Claude with Codex R2 response incorporated. **DRAFT. Not frozen. Non-governing.** rc2 and manifest v2 unchanged; Contract v1 NOT FROZEN; B1 not authorized. Class: all items **[ENG]**. Supersedes O5 v2.

## 1. Changes from v2
- Schema name changes from `hp002-ct-v1` to the joint neutral name **`beastball-causal-v1`** (Codex request). T5's `hp001-t5-v1` stays unchanged as the B0 tier.
- Order key gains `tick_seq` and `batch_seq`, aligned with O4 v3 §5.
- Cross-match uniqueness is no longer claimed as collision-immune (see §3).
- New record kinds for plan activation and batches.

## 2. Identity and order
`causal_id = <logical_match_id>/<actor>/<domain>/<kind>/<ordinal>`
- `actor`: athlete ID, or `RULES`, `ENV`. `domain`: `carry pass shot move pursue tackle block catch jump keeper archer rest rule physics plan batch`. `kind`: `obs bel dec opt<k> int cmd out act rule draw`.
- `ordinal`: a counter per (match, actor, domain, kind), assigned by the core at entity creation.
- Dormant plan stages: `<plan_id>/s<k>`. A `PlanStageActivation` is `<…>/plan/act/<n>` and links the stage ID.

**Required `order` field** (a separate structured field on every record):
`order = (tick_seq, batch_seq, sim_ms, stage, entity_rank, local_seq)`
- `tick_seq`: the outer step counter. `batch_seq`: a match-wide counter assigned when O4 v3 §5 commits a batch.
- `stage` order: observe, belief, decide, intent, command, physics, rules.
- Consumers recover chronology from `order` only. **`batch_seq`, `entity_rank` and ID text never decide a physical outcome** (CE-4); they only name and order what the resolution code has already decided.

**Disposition R-3 (open with Codex).** Codex asks that the identifier encode tick, batch, time, stage, entity, domain, local sequence and kind. This draft keeps those in `order` and keeps the ID's ordinal, so that inserting an unrelated event does not renumber other IDs, which matters for comparing Gate C arms. If a consumer needs those fields inside the ID string, they can be included without changing allocation. Test ID-12 decides.

## 3. Logical vs operational identity
- `logical_match_id` = first 16 hex of SHA-256 over canonical config hash and seed. Reproducible: same configuration and seed gives the same causal IDs on every replay.
- `run_instance_id` (run, attempt, start time, host) lives only in the run manifest and telemetry envelope, never in a causal ID.
- **No collision-immunity claim.** Within one logical match, IDs are unique by construction. Across matches, a 64-bit truncated hash has non-zero collision probability (about n²/2⁶⁵ for n matches); the run manifest checks for duplicate `logical_match_id` and fails loudly.

## 4. Ancestry
Events with no cognitive ancestor (passive collision, bounce, clock-based rule violation, injury threshold, rules-state change) get IDs under `ENV`, `RULES` or the affected athlete with `causal_intent` absent and `emergent_cause` populated. In the B0 tier, ancestry that exists but was not exposed reads `legacy_not_exposed`. An outcome may name a `causal_intent` only if it resolves and `intent.decided_at <= outcome.started_at`. Non-cognitive physical and rules roots are preserved and never replaced by a fabricated chain.
Plan activation: a `PlanStageActivation` record links the **source decision**, the **selecting view** and the **trigger observation or outcome**. The activated intent keeps the source decision link and gets a new `intent_id`.

## 5. Allocation
Allocated in core execution, independent of telemetry. The allocator is a pure counter: no draws, no I/O, no ordering effect, no wall time, no UUID, no hash-map order, no host or run identity. IDs exist with telemetry off. Adding the allocator is an instrumentation change and triggers the rc2 §8 NI re-runs.
`sim_ms` is an integer in 0..2⁵³−1; ordinals are capped at 2⁵³−1. On exceeding either limit the allocator raises `id_range_exceeded`; it never wraps, saturates or truncates.

## 6. Per-step PRISM stream hashing (CT-4, accepted from Codex)
A versioned registry lists all cognition-owned streams. The full registered vector is hashed once after each committed outer step, and the previous post-vector is reused as the next pre-vector. Stream creation or removal is recorded as an explicit `unavailable→hash` or `hash→unavailable` transition. Hashing must not instantiate minds, draw, or iterate a mutating unordered store. Prior audit evidence: 84 PRISM states ≈ 3.922 ms per full snapshot, so one post-commit vector per step, not duplicate snapshots.

## 7. Tests
| ID | Check |
|---|---|
| ID-1…3, 7, 8 | as v2 (schema, replay equality, telemetry-off/min/full equality, Python versions, static scan of allocator) |
| ID-4 | identical under `PYTHONHASHSEED` 0 and 1 and shuffled dict insertion order |
| ID-5 | unique within a logical match by construction; duplicate `logical_match_id` across a batch of runs is detected |
| ID-6 | every outcome naming `causal_intent` resolves a full chain to an observation; outcomes without ancestry carry `emergent_cause` |
| ID-9 | at the range limit the allocator raises and does not wrap; same-ms events are ordered by `stage`, `entity_rank`, `local_seq` |
| ID-10 | shuffling ID text does not change chronology recovered from `order`; nothing sorts by ID text |
| ID-11 | allocator with no sink gives the same IDs and leaves NI-1…4 unchanged |
| ID-12 | inserting an unrelated event does not renumber other IDs; `order` round-trips all fields |
| ID-13 | permuting coincident candidates changes neither IDs nor outcomes (pairs with CE-1) |
| ID-14 | non-cognitive roots are present and never replaced by synthetic chains |
| ID-15 | `PlanStageActivation` resolves to source decision, selecting view and trigger |
| CT4-1 | hashing off/on neutrality: no draws, no state change; overhead reported |

## 8. Status
Awaiting Codex on R-3 and the confirmation of `beastball-causal-v1` encoding. Nothing here is frozen.
