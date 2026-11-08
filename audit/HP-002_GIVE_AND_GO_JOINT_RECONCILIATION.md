# HP-002 / HP-001 — Give-and-go: Claude and Codex stress tests reconciled
Claude, 2026-11-08. **Design only. Non-governing. rc2, manifest v2 and B0 unchanged; Contract v1 NOT FROZEN; nothing implemented.**
Compared: Codex `HP-002_HP-001_GIVE_AND_GO_DESIGN_STRESS_TEST.md` (copied read-only to `baseline/codex_evidence/GG/`) and my `HP-002_GIVE_AND_GO_STRESS_TEST.md`. Codex cites line numbers in the original single-file source; I did not re-verify them against that file. Where Codex and I read the same B0 behavior independently, I treat the finding as corroborated.

## 1. B0 findings: corroborated, and two of my open items closed
| Finding | Claude | Codex | Result |
|---|---|---|---|
| wind-up stores one pending action; carrier actions suppressed meanwhile; release at exact due time inside the integration step | yes | yes | corroborated |
| locomotion continues through wind-up | yes | yes | corroborated |
| release re-plans from true state and may substitute the next receiver | yes | yes | corroborated |
| 400 ms post-release `next_action` | yes | yes | corroborated |
| `next_action` does not gate running | "to confirm" | confirmed (`Player.eligible` excludes it; movement is gated by `next_decision`) | **closed** by Codex |
| controller pass trigger needs more than 180 ms of control | not established | stated | **closed** by Codex (legacy threshold, not a PRISM contract) |
| no give-and-go object; intended receiver routed to the flight intercept with `next_decision` reset | partly | yes | corroborated |

## 2. Agreements (adopt as joint)
1. The plan is athlete-owned cognition state, outside the motor queue, consuming no resource.
2. Only activated intents reach command ingress; dormant stages are never commands.
3. Pass and locomotion run concurrently on disjoint resources.
4. B's return pass is always B's own cognition; A's plan cannot write, select or queue anything for B; A's call is evidence in B's view.
5. No recipient or target substitution at release (B0's substitution is not acceptable in B1).
6. Commitment uses ordered physical events, not whole-tick inclusion.
7. Queue depth one suffices when future stages stay in the plan; deeper queues would hide stale tactics.
8. Activation of a preselected stage must not create an option evaluation; it is traced.

## 3. Differences and how I propose to resolve them
| ID | Topic | Claude | Codex | Proposed joint position |
|---|---|---|---|---|
| D-1 | Cut representation | `run_to(R)` issued in the same bundle at t0, so A moves toward R during the wind-up | the cut is a dormant stage that activates at the committed release and supersedes the current locomotion bundle | **Adopt Codex's** as the default for a give-and-go ("pass, then cut"). A plan may still contain an immediate move intent when the athlete chose to move now; that is an ordinary decision. |
| D-2 | Receive stage | stage 2 "await return" holds expectation only; catching preparation stays in three-stage cognition | A3 instantiates a `CatchPrepareIntent` as plan continuation after a delivered return observation and a reaction gate, with no new option menu | **Unresolved, owner choice (J-4).** Risk: A3 is a second route into catch preparation that the accepted three-stage catching assigns to ordinary cognition (where/whether to move, readiness). If adopted it must reuse the same observation delivery and reaction latency and add no readiness advantage. |
| D-3 | Wind-up revocability | non-revocable by cognition after `prep_started` (B0 behavior); only physics or rules end it | a new A decision or a declared cancel guard may supersede the pass bundle before release commits | **Unresolved, owner choice (J-5).** Codex's reading changes B0 (carrier cannot decide while pending). Default: preserve B0 until you decide. |
| D-4 | Queue semantics | depth 1 per channel | depth 1 per exclusive resource or conflict set, multi-resource bundles admitted or queued atomically, never a single global queue | **Adopt Codex's** (strictly more precise). My conditions (one active plan, one active stage) remain, see J-7. |
| D-5 | Coincident events | event-rank table | common pre-event snapshot, causal dependencies and an approved coincident-event table, one batch commit | **Adopt Codex's** batches. Consequence for IDs: the canonical `order` tuple gains `batch_seq`; my T6-O5 `order` becomes `(sim_ms, batch_seq, stage, actor_rank, local_seq)`. |
| D-6 | Dormant-stage identity | stage objects get ordinals when created | GNG-PLAN-1: dormant stages consume no causal sequence | **Adopt Codex's:** stage IDs are derived as `<plan_id>/s<k>` with no counter draw; only plan creation and activation consume ordinals. |
| D-7 | Activation record | `decision_free: true` flag | `PlanStageActivation` record with `source_decision_id`, trigger, reaction gate, `no_new_option_evaluation: true` | **Adopt Codex's record.** |
| D-8 | Plan limits | one active plan per athlete; one active stage per plan | not addressed | Keep mine as a proposal (J-7); Codex to respond. |

## 4. Joint test list
Use Codex's GNG-B0-1/2, PLAN-1/2, NOFREE-1/2, B-INDEP-1/2, OVERLAP-1, CONTACT-1, INTERCEPT-1, STALE-1, LATE-1, POSSESSION-1, QUEUE-1/2, ATOMIC-1, EVENT-1, PERMUTE-1, TELEM-1. Add from mine: GG-1 (poison A's plan, B unchanged), GG-3 decision-budget invariant, GG-4 delayed-belief predicates, GG-11 plan limits, GG-12 plan privacy, and GG-7 cancellation (form depends on J-5). Drop my GG-6 (tick-relative commitment) in favour of GNG-EVENT-1 plus batch tests; drop my GG-10 (subsumed by QUEUE-1/2).

## 5. Choices requiring owner approval (nothing assumed)
| ID | Choice | Joint recommendation |
|---|---|---|
| J-1 | continuation of a preselected stage without a new decision cycle | approve only for stages semantically chosen in the source decision, with explicit guard, expiry, trace and no option evaluation |
| J-2 | queue semantics | one queued conflicting bundle per exclusive resource or conflict set, atomic admission, replacement not accumulation, no global athlete queue |
| J-3 | own-release trigger | approve: the preselected cut activates at the committed release event |
| J-4 | observed-return receive stage (A3) | **no joint position yet.** Codex recommends approval after delivered observation plus reaction gate; I recommend it only if it adds no readiness advantage over ordinary catching cognition, and would otherwise leave reception to ordinary cognition |
| J-5 | wind-up revocable by cognition? | **no joint position yet.** Default preserve B0 (non-revocable) |
| J-6 | remove recipient substitution at release | joint: remove; it changes B0 and appears as a Gate C difference |
| J-7 | one active plan per athlete, one active stage per plan | my proposal, awaiting Codex |
| J-8 | commitment by ordered events and coincident-event batches | joint recommendation; Codex treats it as already governed by accepted T6-O4 direction |
Parts of Codex's list I agree are not owner choices: B's independent return decision; no silent retarget; physical constraints and RNG ownership.

## 6. Still needed
- **Codex:** response on D-2, D-3, D-8; the per-action commitment events and the coincident-event table; the extraction already requested (channels, B0 conflict behavior, Keeper modes).
- **Effects on my proposals if you approve the above:** T6-O4 v3 would replace the inclusive-tick rule with ordered events and batches, use per-resource queue semantics with atomic bundles, and add the plan layer; T6-O5 v3 would add `batch_seq` and derived stage IDs. I have not written v3 because J-4 and J-5 change its content.
