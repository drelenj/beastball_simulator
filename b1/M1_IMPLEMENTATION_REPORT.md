# OWNER BRIEFING

1. **Accomplished:** M0 is recorded as closed with the v3.5/readiness contract
   hashes and all IMPL-01…10 defaults. The M1 candidate has been corrected for
   the five blocking findings in Claude's R1 review: physical-state sensing,
   proprioceptive self-view, athlete-derived gaze/ratings, a real hidden-state
   poison test, and stepped decision/outcome feedback.
2. **What B1 can do now:** One B1 field athlete senses actual active engine
   bodies through PRISM, forms an age-bounded individual belief, chooses
   pass/retain/no-action, explicitly continues an accepted pass during wind-up,
   and changes its next choice after interruption or rejection. Remote receiver
   contact remains a world event rather than private thrower feedback.
3. **What remains unimplemented or unproven:** locomotion commands, multiple
   independently deciding athletes, receiver cognition/catch ownership and
   completed/intercepted/dropped/tackled outcome diversity,
   general bundle queues, full causal-ID schema, full T1 rerun, and Claude's
   review of this revised candidate. This is still an M1 candidate; no M1
   acceptance is claimed.
4. **What blocks the next milestone:** M1 still lacks physical outcome diversity.
   Independently deciding defenders and receivers cross into M2, which remains
   unauthorized. No canon question is exposed by the work completed here.
5. **Recommended action:** Continue within M1 authority. Have Claude review the
   corrected information boundary and behavioral trace before closing M1.

## M0 closure

`M0_CLOSURE.md` now contains the frozen minimum contracts and full IMPL-01…10
text. `M0_FREEZE_MANIFEST.json` records hashes for the accepted O4/O5 v3.5
drafts, review disposition, readiness roadmap, and T1–T5 accepted evidence
manifests. It pins B0 at commit `2abe497ca82588cb2d8c871a7aab61daaae95c12`.
Inputs not vendored into the repository remain recorded by their frozen digest.
Regenerate with `python3 -m b1.m0_manifest`. No B0 source edit occurred.

## R1 finding disposition

| Finding | Correction in this candidate | Evidence / remaining limit |
|---|---|---|
| F1 hand-written sensor fixtures | PRISM bodies are projected from active `s.players` in the installed physical state. A1 and B0 are actual active engine entities. | Integration test verifies active bodies and that A1's noisy contact derives from the physical entity. Bodies remain stationary scenario inputs; they are not B1-controlled athletes. |
| F2 constant self pose/possession | AthleteView x/y and holds-ball derive from A0's physical body and authoritative carrier field. Eye height and facing derive from A0 body. | Proprioceptive fields are explicitly in projector, outside cognition. |
| F3 scripted gaze/ratings | PRISM rating profile comes from existing `prism_ratings_v0.assign`; gaze follows A0's body facing, with no focus target. | Existing ratings and PRISM mappings are unchanged. Cognition does not receive exact ratings. |
| F4 ineffective poison test | Test constructs one delivered view, mutates true B0 position while keeping that view fixed, and asserts identical decision; separately tests observation-driven choice change. | The immutable frame is the only cognition input. |
| F5 forced one-shot timing | Runner advances physical simulation in 100 ms observation steps. Decision cadence is from PRISM judgment profile; each subsequent AthleteView contains prior own-action feedback. | The field evaluator is still a limited new provisional policy. No movement or second actor loop. |
| F8 stale belief age | Belief contact ages are checked against PRISM memory lifetime; stale contacts are excluded and listed in DecisionTrace. | No general belief confidence calibration is claimed. |
| F10 preparation/speed constants | Motor derives `pass_release_ms` from `m.assume`, ball handling from physical athlete attributes, and speed from configured `cfg['pocket']['pass_speed']`. | Existing sampler still owns the final release velocity. No physical constant was changed. |

F6/F7 and F11/F12 remain as R1 described: telemetry-off computes the same trace
then suppresses serialization; the import guard is narrow but the cognition
module's imports were inspected; the final versioned causal ID schema is not
implemented; profile IDs remain scoped to this Python candidate. Historical
legacy traps still cover the known decision/target entry points, while a
complete unimportable-controller capability boundary is not yet demonstrated.

## R2 finding disposition

| Finding | Current correction | Status |
|---|---|---|
| G2 own-action state and unused feedback | `AthleteView` carries the pending command and release time. Cognition selects `continue_current`; one-shot interruption/rejection feedback changes the next choice. | Implemented and tested |
| G3 isolation evidence | Separate deterministic physical runs perturb hidden attributes and relocate an unsensed defender, then a visible-frame change proves the converse. | Implemented and tested |
| F13 remote contact feedback | Receiver contact remains in the authoritative outcome ledger and is excluded from the thrower's private feedback. | Implemented and tested |
| F14 timing metadata | Trace records nominal readiness plus actual quantized decision times and effective cadence. | Implemented and tested |
| F16 import guard | Test scans `Import`, `ImportFrom`, and forbidden engine symbols. | Implemented and tested |
| G1 outcome diversity | Catch/interception/drop/tackle and independently controlled opposition remain absent. | Open |

## Implemented and tested gates

| Gate | Current evidence | Status |
|---|---|---|
| BLK-01 information isolation | Frozen cognition values, pure decision module, actual projector, independent hidden-state perturbation, observation sensitivity, stale-contact test | Implemented/tested for current pass slice; R2 retest pending |
| BLK-02 no legacy override | Historical match step and known target/policy functions trapped; command target fidelity asserted | Pass command path only; movement path not implemented |
| BLK-03 typed physical port | `CommandIngress` and `PhysicalExecutionPort`; cognition-free command replay; release, interruption, and real kernel contact feedback | Locomotion and fixed catch/interception replay fixtures absent |
| BLK-04 deterministic arbitration | Canonical single-resource admission, permutation check, repeated execution/state/RNG hashes | General bundles, queues, and simultaneous event-batch invariance absent |
| BLK-05 preservation | Source hash guard around tests; B0 source snapshot untouched; stored T3/T5 verifiers rerun | Full ten-case T1 match rerun not performed |

DESIGN COMPLETE: M0 Core Slice v1 and its engineering defaults frozen.
IMPLEMENTED: stepped physical-world perception and one-athlete pass/retain path.
TESTED: twelve M1 tests plus stored T3/T5 packet integrity checks.
ACCEPTED: M0 and M1 authority only; revised M1 candidate not formally accepted.

## Reproduction and evidence

```bash
python3 -m b1.m0_manifest
python3 -m unittest b1.test_m1 -v
python3 -m b1.evidence
python3 -m b1.run --case pass --seed 1 --out b1/evidence/pass.json
python3 -m b1.run --case retain --seed 1 --out b1/evidence/retain.json
python3 -m b1.run --case interrupted --seed 1 --out b1/evidence/interrupted.json
python3 HP-001_T3_FINAL_PACKET/tools/verify_packet.py HP-001_T3_FINAL_PACKET
python3 HP-001_T5_EVIDENCE_PACKET/verify_packet.py HP-001_T5_EVIDENCE_PACKET
```

Trace files identify scenario positions, observations, beliefs, decision options,
intents, admissions, physical samples/events, outcomes, and own feedback. The
current IDs are deterministic within the profile but are not yet the full
versioned `beastball-causal-v1` structure. B0 verifier results are stored-packet
integrity checks, not new simulation repeats. Performance remains import-heavy;
the short scenario does not support a match-throughput claim.

## Known limits

- The example's A1 and B0 are true physical entities and sensor inputs, but
  neither has independent PRISM cognition or Motor Control.
- Passive entities do not move under B1 commands. They may still participate in
  unchanged physical event handling where the Pocket kernel does so.
- No general move, catch-intent, or multi-resource command bundle is exposed.
- The B1 decision evaluator is a small provisional lane-clearance rule. It does
  not reproduce the full historical PRISM option suite and does not prove
  behavioral quality.
- RNG evidence is state signatures for known streams, not a full draw ledger.
- The implementation branch is rooted directly at the accepted B0 Git commit;
  source-hash verification excludes `b1/` and guards the inherited tree.
- No Claude coordination tool is available in this session. Review findings
  were applied from the attached R1; no new Claude review or signoff is claimed.
