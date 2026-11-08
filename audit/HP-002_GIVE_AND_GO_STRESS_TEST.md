# HP-002 / HP-001 — Give-and-go design stress test (T6-O4 command arbitration, queue depth)
Claude, 2026-11-08. **Design only. Non-governing. rc2 and manifest v2 unchanged; Contract v1 NOT FROZEN; B0 untouched; nothing implemented.**
**Joint status:** this is Claude's analysis and recommendation. **Codex concurrence has not been obtained**; §11 lists what I need from Codex. B0 facts below come from my reading of the frozen source (`core_src/match.py`, `engine.py`); anything I could not establish is marked.
Scenario: A passes to B, cuts into space, may receive a return pass. B decides independently. Defenders can disrupt either stage. Ratings and times in §10 are **illustrative**, using B0 formulas, not measurements.

## 1. How B0 handles it (source facts)
| Phase | B0 behaviour | Source |
|---|---|---|
| Decision to pass | the carrier's decision calls `make_pass` (prepare). It computes `delay = pass_release_ms × (1.35 − 0.5 × ball_handling)`, with `pass_release_ms = 250` (so about 212–337 ms), stores `pending_ball_actions[carrier] = (due, kind, recipient)`, and emits `ball_action_prepared` | `match.py:862-871`, defaults |
| Receiver foreknowledge | `pass_signal = (recipient, now)` is set at preparation start. For the intended receiver, readiness is credited up to 500 ms of earlier observation (`min(500, release_time − pass_signal_time)`). This is a hidden "you are the target" side-channel | `match.py:862, 2251` |
| During preparation | the carrier's own decisions are skipped while a pending action exists (`carrier_decision` returns after the due check). **Locomotion is not paused:** movement integrates toward the held `p.target`, which changes only when `now ≥ next_decision` (cadence `decision_speed × (1.3 − 0.4 × awareness)`). The integrator cuts the step at the preparation-complete instant (an in-step ordered event), so the release time is not rounded to a tick | `match.py:921-931, 757, 1443-1456` |
| Physical disruption | a defender hold stalls the wind-up; if the stall reaches `tuck_after_delay_frac` of its length the pending release is cancelled (`c3_tuck`). Preparation begun before a loss of control is dropped | `match.py:1479-1492, 922-923` |
| Release | at the due time `make_pass(execute=True)` re-plans with the **receiver's true current state**, and if that receiver is unreachable it **substitutes the next-ranked teammate** (`pass_ranked`). This is a hidden recipient decision inside execution | `match.py:875-893` |
| After release | `p.next_action = now + 400`. That blocks contact eligibility (`'cooldown'`) and the carrier decision; in the code I read, running is not gated by it (only a grounded posture is) — **Codex to confirm** | `engine.py:240`, `match.py:893, 926` |
| The cut | there is no "pass-and-cut" object. A's cut is whatever target he holds, or chooses at his next cadence slot. | `match.py:757` |
| Return pass | B's catch, then B's own carrier decision. A is one candidate among B's options. Nothing links the two passes. | — |
| Not established | the cadence of the carrier decision itself on the controller path (`c4c2_decide`); whether any B0 path lets A move toward a cut target faster during preparation | Codex extraction |

## 2. B1 representation of "pass and cut" without a pause or free decisions
A's intention is **one decision** at one cadence slot, recorded as a **plan** that A owns privately. The decision does the thinking (who to pass to, where to cut, under what condition to expect a return). Everything afterwards is execution and bookkeeping:
- Stage 1 (decided at t0): `pass(B)` and `run_to(R)` issued together as one **bundle** from the same decision. They occupy different resources, so they run concurrently; no pause exists.
- Stage 2 (armed at t0, activates on A's own release event): `await_return`. It contains no motion command and no choice; it only keeps the expectation in A's memory with an expiry.
No stage may evaluate alternatives or select among them. Anything that needs a choice is a new decision and waits for A's cadence slot (§7).

## 3. Vocabulary (what each thing is)
| Term | Definition | Owner | Lifetime |
|---|---|---|---|
| **Tactical plan** | an athlete-private memory object: ordered stages, activation predicates, abort conditions, expiry. It carries decided content only. | the athlete | from a decision to completion, abort or expiry |
| **Conditional stage** | a stage with a predicate over the athlete's own state and events, or over his delayed beliefs about others. Activation is bookkeeping, not a decision. | the plan | armed until activated, aborted or expired |
| **Command bundle** | the intents from one decision (or one stage activation), with a shared `bundle_id`, stage order, and a policy: `required` or `best_effort` per member | the athlete via MC | until each member resolves |
| **Occupied resource** | a channel (`locomotion`, `ball_release`, `hands_reach`, `contact`, `takeoff`, `archer_draw`) held by a command between two ordered physical events | MC | acceptance event to release event |
| **Queued command** | an accepted-pending command waiting on a committed occupant of a conflicting channel | MC | until promoted, replaced or invalidated |
Plan stages are **not** queued commands. A future stage lives in the plan; only a command that is activated and blocked can enter a queue.

## 4. Can locomotion overlap pass preparation and release? Yes. Limits.
Locomotion and `ball_release` are compatible channels. Overlap is bounded by physics, none of which needs a new rule:
1. **Defender restraint** (B0 `c3_rho`): slows or stalls the wind-up; can cancel it (tuck). It also changes the carrier's movement during restraint.
2. **Release speed limit** (`ball_limit` 40 m/s) and restraint speed loss.
3. **Locomotion limits** (acceleration, braking, turning) bound how sharply A can cut while winding up.
4. **Launch point:** the ball leaves from A's position at the release instant, so the cut changes where the pass starts; MC aims from that point using the belief of B at that instant.
5. **Post-release recovery** (400 ms): occupies `hands_reach` (and contact eligibility), so a return arriving inside that window cannot be touched by A. B0 has no accuracy penalty for moving while winding up; B1 inherits that (a B0 simplification, not changed).

## 5. B chooses the return pass independently
- B observes the pass (ball flight) and learns he is the target by **explicit communication or observable inference (O2)**, not B0's hidden `pass_signal`. A may issue a communication as part of stage 1; it travels with latency and may go unobserved.
- After B gains control, B's next decision uses **B's AthleteView only**: A's delayed observed motion (A is cutting into space), defenders, B's own state. A is one candidate. B never reads A's plan, which is private.
- **Test of no centralized imposition (GG-1):** replace A's cut by an unplanned identical movement; B's decision is identical. Poison A's private plan fields; B's decision is identical. Remove A's communication; B's decision changes only through what B observes.
- The give-and-go exists only if A planned it **and** B independently chose A.

## 6. Disruption scenarios
| # | Scenario | B1 behaviour |
|---|---|---|
| S1 | **Cancellation.** A wants to cancel during the wind-up | cognition cannot cancel once the wind-up has begun (B0 fact; commitment event `prep_started`); only physics (tuck, loss of control) or rules can. Before `prep_started` the intent is revocable. After release, the cut command is revocable by A's next decision at his cadence slot. *Owner approval AP-3.* |
| S2 | **Defensive interception** of the pass | outcome `interception`, possession changes. Stage 2 predicate `possession_unchanged` fails: the plan is aborted with reason `possession_changed`. A learns through his next view; his next decision occurs at his next slot, not instantly. |
| S3 | **Stale target** (B moved since the decision) | MC re-aims from the belief of B at release (allowed geometry). **No recipient substitution** (B0 `pass_ranked` fallback is removed). If infeasible: `execution_inability` at execution, pass aborted, ball retained, bundle's other members continue per policy, plan aborted for stage 2. *Owner approval AP-4 (changes B0).* |
| S4 | **Late return pass** (arrives after the plan's expiry or after A's cut command has ended) | physics does not care about the plan: if A's hands are ready, he catches. A's readiness comes from his perception and being target (three-stage catching). Expiry only deletes the plan; it creates no decision and A keeps his last locomotion target until his next slot. |
| S5 | **Contact interruption** of A during the cut | locomotion command interrupted (`physical_change`); plan stage 2 aborted `self_grounded` or `contact`; B's later decision sees A grounded or delayed through B's view. |
| S6 | **Contact interruption** during the pass wind-up | restraint stalls the wind-up; tuck cancels it with outcome `interrupted`/`tuck`; bundle's pass member ends, plan aborted; the locomotion member continues if it is not itself interrupted. |
| S7 | **Possession change** after B catches but before B returns | B's decision does not occur (B no longer carries); the plan's stage 2 is aborted at the observable possession change. |
| S8 | **B ignores A** | stage 2 expires; A decides normally at his next slot. Nothing is owed. |
| S9 | **Two-stage clash:** A's fresh decision at a cadence slot while stage 2 is armed | the new decision supersedes any plan-originated command on conflicting channels (decisions outrank plan stages); an armed stage with no commands stays armed until expiry or abort, and A can read his own plan in the new decision. |

## 7. Plan stages, PRISM cadence and reaction delays
Rules to prevent silent decisions:
1. **A plan is created only by a decision**, which is gated by the athlete's decision cadence and reaction delay like any decision.
2. **Stage activation is not a decision.** Its parameters are either (a) frozen at t0, or (b) a named **tracking reference** resolved by MC geometry (for example, "run to the point offset d from B's position"). A parameter that would require comparing alternatives is a decision and must wait for a cadence slot.
3. **Predicates read only the athlete's own state and events, or his delayed beliefs.** An own event (own release) has no perception delay. An event about others (B catches, B passes) is evaluated on A's belief after the O3 delivery latency, never on truth.
4. **Decision-budget invariant:** per athlete, per cadence period, the number of decisions with a plan equals the number without. Stage activation records `decision_free: true`.
5. **Sentinels:** evaluation and selection functions raise if called from a stage activation (extends DO-1).
6. **Timing fields:** an activated command carries all nine timing fields; delays that apply to the activity (preparation, release) still apply.

## 8. Commitment: ordered physical events instead of a whole-tick inclusive rule — recommended
B0 already resolves wind-up completion and tucks as **named events inside a step** (`('preparation_complete', t)`, `('tuck', t)`), and C3a2 stopped rounding preparation to the step. A whole-tick inclusive rule would be coarser than the physics it governs. **Recommendation: withdraw my v2 B2 "inclusive at the tick" and define commitment by ordered events.**
- Each intent kind names its **commitment event** (for a pass: `prep_started`, so cognition cannot revoke; for a locomotion command: none, always revocable; for a jump: `takeoff`; for an arrow: `draw_started`; per Codex's extraction).
- Canonical order is `(sim_ms, stage, actor_rank, local_seq)` with stages observe, belief, decide, intent, command, physics, rules. An intent is revocable-over iff the commitment event is **later** in canonical order than the intent's own issue point. Because decisions sort before physics within a millisecond, a commitment reached by physics in tick t binds decisions from t+1; one reached in t−1 binds decisions at t. This gives a unique answer without a tick rule and without ties.
- Sub-step physical events keep their integer-millisecond instants (`at`); two events in one ms are ordered by event rank (preparation_complete before release, contact before possession change), a table to be supplied by Codex.

## 9. Is queue depth one still sufficient?
**Yes, provided plan stages are modeled separately (§3), with three conditions:**
1. one active plan per athlete (a second plan replaces the first; owner approval AP-5);
2. a plan activates at most one stage at a time (`requires` edges, no parallel branches);
3. decisions outrank plan stage commands on conflict (S9).
Walkthrough: during the wind-up, `ball_release` is committed; A cannot make carrier decisions; locomotion is a different channel, so nothing queues. After release, the 400 ms recovery occupies `hands_reach`: a catch intention for the return would queue behind it at most once (depth 1); a newer intention replaces it. No scenario in §6 needs two queued commands on one channel, because chained futures live in the plan, and a cognitive replacement supersedes rather than stacks. Keeping depth 1 is therefore supported by this test, and any increase is a data change needing approval (GG-10 fails if any scenario would overflow).

## 10. Illustrative timeline (B0 formulas, invented ratings)
Assume: A ball_handling 0.6, so wind-up 250 × (1.35 − 0.3) = 262.5 ms; B ball_handling 0.5, so 275 ms; A cadence slots every 280 ms; B perception-plus-cadence delay after catch 180 ms; pass flight 450 ms; return flight 370 ms; plan expiry 2,000 ms.
| t (ms) | Actor | Event | Class |
|---|---|---|---|
| 0 | A | cadence slot; decision D1 chooses give-and-go: plan G (stage 1 pass(B)+run_to(R); stage 2 await_return, expiry 2,000) | decision |
| 0 | A | intents I1 pass(B), I2 run_to(R), bundle `b1`, plan stage order | intent |
| 0 | MC | accepts C1 (`ball_release`) and C2 (`locomotion`); no conflict | acceptance |
| 0 | A | C1 `prep_started` | **commitment** (cognition can no longer revoke C1) |
| 0 | A | communication to B (optional, latency L) | message |
| 0–263 | A | runs toward R while winding up | locomotion overlap |
| 263 | A | `release` (ball leaves A's position at 263); stage 2 activates (own event, no delay) | physics, outcome O1 |
| 263–663 | A | hands recovery (`hands_reach` occupied); running continues | resource |
| 280, 560, 840… | A | cadence slots; A may decide again, which supersedes only conflicting plan commands | decisions |
| 713 | B | catches; becomes carrier | outcome O2 |
| 893 | B | B's cadence slot; D2 chooses a pass to A from B's view (A observed cutting) | decision (independent) |
| 893 | MC | accepts C3 `ball_release` for B | acceptance and commitment |
| 1168 | B | release (275 ms wind-up) | outcome O3 |
| 1538 | A | catches the return (his hands ready by perception); plan G completes | outcome O4 |
Variants by delta: **S2** interception at ≈ 600: possession changes, G aborted at 600, A decides at next slot (840). **S3** B has moved 4 m: release at 263 re-aimed to belief of B; if infeasible, abort at 263 with reason, ball retained. **S4** change B's decision to 1,600 ms: arrival 2,345 > 2,000, plan expired at 2,000, A holds last target until next slot, catch still possible by readiness. **S5** A contacted at 700: locomotion interrupted, G aborted, B's view at 893 shows A delayed or grounded. **S6** tuck at 180: C1 interrupted, G aborted, no release.

## 11. Acceptance tests (proposed)
| ID | Check |
|---|---|
| GG-1 | independence: unplanned identical A movement, poisoned A plan, no communication → B's decision identical or changed only via B's observations |
| GG-2 | no recipient substitution at release; infeasible pass yields `execution_inability`, ball retained |
| GG-3 | decision-budget invariant: decision counts per cadence period equal with and without a plan; sentinels not triggered by stage activation |
| GG-4 | stage predicates on others' events use delayed beliefs (perturb truth, hold belief → no activation change) |
| GG-5 | locomotion overlaps wind-up and release; with ρ restraint the wind-up stalls and tucks per B0 numbers |
| GG-6 | commitment by event order: intents at t−1, t, t+1 relative to the commitment event, plus two events in one ms in table order |
| GG-7 | cancellation: before `prep_started` revocable; after, only physics/rules end it |
| GG-8 | interception, possession change and contact abort the plan with the specified reasons; no fabricated chain |
| GG-9 | late return: catch depends on readiness, not on plan; expiry creates no decision |
| GG-10 | queue depth 1 sufficient across S1–S9; overflow fails the test |
| GG-11 | one active plan per athlete; second plan replaces first with edge |
| GG-12 | plan content is private: removing it from the view store leaves all other athletes' views unchanged |
| GG-13 | B0 adapter reproduces the B0 give-and-go trace unchanged (Gate A) |

## 12. Recommendation and owner approvals
**Recommendation:** adopt the plan/stage/bundle/resource/queue vocabulary (§3); keep queue depth 1; replace the inclusive-tick commitment rule with ordered physical events (§8); remove recipient substitution at release; keep the pass wind-up non-revocable by cognition as in B0.
**Approvals needed from you (none assumed):**
- **AP-1** plans are athlete-private memory objects and stage activation is decision-free (§7).
- **AP-2** withdraw v2 B2 and use ordered-event commitment (§8).
- **AP-3** wind-up is non-revocable by cognition (B0 fact), or allow an abort (changes B0).
- **AP-4** remove recipient substitution at release (changes B0; Gate C).
- **AP-5** one active plan per athlete, one active stage per plan, queue depth 1.
- **AP-6** stage predicates may use others' events through delayed beliefs.
- **AP-7** keep the 400 ms post-release recovery as `hands_reach` occupancy, and no movement accuracy penalty (B0 simplifications).
**Needed from Codex (not yet obtained):** the extraction of commitment events and event-rank table per action; the carrier-decision cadence on the controller path; confirmation that `next_action` does not gate locomotion; confirmation that sub-step event ordering can serve as the commitment order; concurrence or objections on AP-1…7.
