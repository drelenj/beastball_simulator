# HP-001 / HP-002 — M0 Contract Freeze and Closure

**State:** M0 CLOSED; M1 implementation authorized; M1 acceptance remains open.
**Baseline:** B0-P4-DEFAULT, accepted source commit
`2abe497ca82588cb2d8c871a7aab61daaae95c12`.
**Implementation boundary:** B1 exists only under `b1/` on a branch rooted at
the accepted baseline; historical B0 source, accepted evidence, defaults, and
result hashes are read-only inputs.

## Frozen minimum contracts

1. Each athlete owns option generation, evaluation, selection, plans, and targets.
2. Cognition receives immutable `AthleteView`, individual `BeliefState`, approved
   self knowledge, and delivered communication. It receives no `SimState`, live
   entity, engine callback, or hidden recovery path.
3. Data flow is `ObservationFrame → AthleteView → BeliefState → DecisionTrace /
   ActionIntent → CommandIngress → MotorCommand → PhysicalExecutionPort →
   PhysicalOutcome`.
4. MC uses own-body/capability data only to execute the selected intention. It
   cannot change the action family, target, receiver, or tactical plan.
5. Deterministic command ingestion is distinct from simultaneous physical
   resolution. B1 commands do not enter historical target selection or policies.
6. Capture, delivery, reaction/cadence, command acceptance, execution, physical
   commitment, and outcome times remain separately represented.
7. Queueing, supersession, interruption, rejection, and failure are explicit;
   none silently replaces a selected intention.
8. Every physical change is resolved from authoritative state and emits a
   traceable physical/rules outcome. True state remains authoritative for PHY.
9. B0 and B1 use separate code paths, manifests, processes, and evidence.
10. M1 exclusions are bound in the conformance profile. Unsupported conditions
    fail explicitly; no implicit fallback to legacy cognition is permitted.

## Frozen engineering defaults (IMPL-01 … IMPL-10)

| ID | Frozen M1 default |
|---|---|
| IMPL-01 | Ledger domains: `perception`, `belief`, and `communication`; `DecisionTrace` uses its declared decision domain. |
| IMPL-02 | `UnresolvedOutcome` is a causal ledger record at stage `physics`, kind `unresolved`, no state mutation, followed by a loud run failure. |
| IMPL-03 | `ConformanceProfile.policy_bindings` enumerates resolved, unresolved, and unsupported policies; excluded scenario classes are explicit and hashed. |
| IMPL-04 | `tick_seq`, `event_batch_seq`, `local_seq`: UInt64 as 20-digit decimal strings; base time: UInt53 as 16 digits; substep, option/multiplicity sequences, registry ranks: UInt32 as 10 digits. |
| IMPL-05 | EventTime base unit is 1 ms; substep is fixed 2^-32 of a millisecond from exact/fixed-point scheduling, never host-float encounter order. B0 projection uses substep zero. |
| IMPL-06 | Every emitted record family has semantic ID slots; parentless roots use `EmergentRootKey`; multiplicity is semantic, not encounter order. |
| IMPL-07 | Visible slice observations are deterministic immutable value copies. Unobserved/unmodeled attributes are unavailable, never filled from truth. Exact ratings and hidden reserves are unavailable to cognition; self pose/motion can be exact. |
| IMPL-08 | Belief v0 is deterministic, individual, provenance-carrying, age-bounded, and may extrapolate constant velocity only from delivered observations. |
| IMPL-09 | Existing physical constants, rating mappings, release sampler, and named physical draws are reused unchanged. No recalibration. |
| IMPL-10 | Archer A2 possession-relative foul mapping uses the selected ruleset's offence/defence minor by authoritative possession owner. Deferred from M1; Archer disabled. |

These are the accepted roadmap's provisional engineering defaults frozen for
the M1 implementation profile. They are not canon changes. Any incompatible
schema change requires a version increment and tests; no T6 contract is silently
rewritten by this record.

## M1 profile and implementation scope

Profile: `m1-pass-flight-v1` (schema `b1-m1-python-0`). One controlled field
athlete receives PRISM perception from physical active bodies, maintains an
individual belief, chooses pass/retain/no-action, submits a typed command, and
receives bounded physical outcomes. Pass preparation uses accepted Pocket 4
`pass_release_ms`, athlete ball handling, configured `pass_speed`, and the
existing release sampler. The runner advances simulation time in bounded
steps; it does not assign an arbitrary decision timestamp.

The profile excludes multi-athlete cognition, locomotion commands, give-and-go,
Keeper, Archer, tackles, contested jump/catch ownership, scoring, and regulation
simulation. A1/B0 are active physical scenario bodies but do not decide. Their
positions are scenario configuration, not receiving assignments. A1's physical
contact/catch behavior remains the existing kernel behavior and is not a B1
catch-cognition claim.

## Preservation and acceptance boundary

- No B0 source file may be edited; a per-file hash guard runs before and after
  B1 verification.
- Historical T1–T5 packets are not regenerated or overwritten.
- `2abe497` is both the pinned historical reference and the parent of the B1
  implementation branch. The branch does not redefine the B0 baseline.
- Stored T3/T5 verification is preservation evidence only. It is not a new T1
  full-match rerun.
- M0 is closed. M1 implementation is ongoing; no M1 acceptance is claimed.
- M2 and later milestones are not authorized by this record.

## Input contract hashes

Exact SHA-256 digests for the accepted v3.5 drafts, review disposition,
readiness plan, and historical evidence manifests are in
`M0_FREEZE_MANIFEST.json`. Inputs not vendored into the source repository retain
their frozen digest and are marked unavailable. Recreate with:

```bash
python3 -m b1.m0_manifest
```
