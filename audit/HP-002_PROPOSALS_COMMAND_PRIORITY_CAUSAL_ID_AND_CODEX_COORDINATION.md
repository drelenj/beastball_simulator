# HP-002 — Proposals for T6-O4 and T6-O5, and Codex coordination package
Claude, 2026-11-08. **Proposal only. Not governing, not in the manifest (rc2 and manifest v2 are untouched).** Nothing here is approved; nothing is implemented. Baseline: rc2 sha256 `a95cdb05…722a`.

## A. Codex coordination package (OPEN-C items)
Please relay to Codex. Each item: my position, what I need, how it would be tested.
| ID | Question | My position | Needed from Codex | Test |
|---|---|---|---|---|
| TI-9 | Keeper intent modes and arbitration | Mode enum from T6 §6.3 (positional adjustment, set, dive, jump, gather, parry, hold, recovery) enters Contract v1; arbitration policy is not needed before freeze, only before Keeper migration | confirm the enum is complete against the B0 Keeper paths; read-only extraction of the B0 phases each mode corresponds to | DO-4 |
| CT-4 / RNG-2 | per-step hashing of per-athlete PRISM streams (`fprism`, `kprism`: `rng`, `rng_t`) | extend T5's per-step transition hash to include them (T5 currently hashes them only at checkpoints) | feasibility and cost of per-step hashing; confirm it consumes no draw | RNG-2 |
| RN-3 / GB-2 | fixed-draw fixtures | T3A must include fixtures with injected draw ledgers so identical commands plus draws give identical outcomes | confirm T3A scope can express draw injection for release, catch, arrow | GB-2 |
| SQ-1 | T6 phase 4 (command-replay physical boundary) | native-track; for Python B1, T3A fixtures already replay explicit commands with cognition suppressed | confirm, or state what B1 needs beyond T3A | GB-1 |
Acknowledgments requested (RES-P): TI-8 precedence reading; RN-5 invariant (cognition draws never advance PHY or match streams); T6's O1–O10 list is stale relative to your 2026-11-07 resolutions. Also useful: the T4 report and packet.
Read-only extraction I will need for the proposals below (no behaviour change): B0's existing commitment boundaries per action (for example when a pending pass or shot, a takeoff, an arrow draw becomes non-revocable) and the channel each action occupies.

## B. Proposal for T6-O4: command priority
**Channels.** Each athlete has independent command channels: `locomotion`, `ball_release`, `contact`, `hands_reach`, `takeoff`, `archer_draw`. A command occupies one or more channels (a table of data, extracted read-only from B0). At most one active command per occupied channel.
**Rules, applied in this order**
1. **Authoritative interruption wins** and is never a "priority" among intents: rules stoppage, then authoritative physical change (freeze, incapacitation, possession loss, contact that ends the action), then expiry. Each yields an outcome with a reason.
2. **Authorization.** Only the athlete's own decision owner may issue an intent in B1. Any other issuer (team planner, legacy table, MC itself) is rejected with reason `owner_not_authorized`. (The B0 adapter is exempt and tagged.)
3. **Commitment.** Each intent kind declares commitment points. Before a point the intent is `revocable`; after it, `committed`. A later same-owner intent may supersede a revocable intent; against a committed one it is queued until the commitment completes or rule 1 interrupts it.
4. **Conflicts across channels.** A compatibility table (data) lists which channel pairs cannot run together. A new intent that conflicts supersedes the earlier one on the conflicting channels only, subject to rule 3.
5. **Determinism.** Same-tick issuance is ordered by (`decided_at`, athlete ID, intent sequence). Result must not depend on iteration order.
Every supersession records new intent ID, `supersedes` edge, and an interruption outcome (rc2 §3a).
**Not proposed:** commitment values and the compatibility table; those come from the read-only extraction, not from me.
**Tests (new)**
| ID | Check |
|---|---|
| SUP-2 | permuting same-tick issuance order leaves all commands and outcomes identical |
| SUP-3 | a committed intent is not superseded by a later intent; the later one is queued |
| SUP-4 | rule 1 precedence order holds for each pair of authoritative causes |
| SUP-5 | an unauthorized issuer is rejected with the reason, and the athlete's state is unchanged |
| SUP-6 | every supersession has ID, edge and outcome; no silent replacement |
| SUP-7 | non-conflicting channels run concurrently without interference |
**Approval requested:** rules 1–5 as the skeleton. Values are a Codex extraction task.

## C. Proposal for T6-O5: causal-ID encoding and schema version
**Form (ASCII, `/`-separated):** `<match>/t<sim_ms, 9 digits>/<actor>/<domain>/<local>/<kind>`
- `match`: first 16 hex of SHA-256 over the canonical `MatchConfig` hash plus seed (deterministic, parallel matches cannot collide).
- `actor`: athlete ID such as `A07`, or `RULES`, `ENV`.
- `domain`: enumeration: `carry pass shot move pursue tackle block catch jump keeper archer rest rule`.
- `local`: per (tick, actor, domain) counter from 0, allocated in canonical stage order (observe, belief, decide, intent, command, physics), actors in sorted ID order.
- `kind`: `obs bel dec opt<k> int cmd out rule draw`.
- Example: `3f9c1a7b22d04e88/t000001380/A07/catch/0/dec`.
- Draw IDs: `<causal id>/draw/<stream>/<ordinal>`; in the B0 tier draws are `legacy_not_exposed`.
Sorted lexicographically, IDs order chronologically. Prohibited sources: wall time, UUIDs, hash-map order, RNG draws, process IDs.
**Schema version:** string `hp002-ct-v1` on every B1-tier record. T5's `hp001-t5-v1` records stay valid and are the B0 tier.
**Tests (new)**
| ID | Check |
|---|---|
| ID-3 | same IDs at telemetry off, minimal and full |
| ID-4 | same IDs under `PYTHONHASHSEED` 0 and 1, and with shuffled dict insertion order |
| ID-5 | all IDs in a run are unique; two parallel matches never collide |
| ID-6 | every outcome links back through command, intent, decision, belief to observation |
| ID-7 | same IDs under CPython 3.12 and 3.13 |
| ID-8 | static scan finds no prohibited source in the allocator |
(ID-2 replay identity is already in rc2.)
**Approval requested:** the form, the `hp002-ct-v1` version string, and the prohibited-source list.

## D. State
Open and unchanged: U-1…U-4, SELF-1, R-RS, T6-O3 (deferred), T6-O6 (deferred). Contract v1 remains NOT FROZEN. B1 implementation, native work, Keeper optimization and rules changes are not begun.
