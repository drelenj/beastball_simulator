# HP-002 — B1 Implementation Readiness & Milestone Plan (Claude's half; joint once Codex sections are added)
Claude, 2026-11-11, in response to the owner directive "Transition to B1 implementation". **No code was changed.** Frozen B0, rc2 (sha a95cdb05…) and manifest v2 are unchanged. Contract v1 is not frozen. M1 is not yet authorized.

# OWNER BRIEFING
1. **What was accomplished?** The design phase is closed on paper. The interface contracts (who may command what, how simultaneous events are settled, how every decision and outcome is traced) are reconciled with Codex in v3.5. Your rulings on shots at the buzzer, boundaries, goals and Archer ammunition are written into them. I did not start another review cycle.
2. **What can B1 actually do now?** Nothing yet. Every B1 item is DESIGN COMPLETE at most. The only IMPLEMENTED, TESTED and ACCEPTED thing is frozen B0.
3. **What remains unimplemented or unproven?** All of B1: the athlete's observation-to-belief-to-decision path behind a strict information boundary, athlete-owned plans, Motor Control, the typed command/outcome interface, and the trace. Unproven: that real athletes with only their own knowledge can complete a give-and-go in a way that looks like the intended game.
4. **What is blocking the next milestone?** I found **no genuine blocker** for M0, M1 or M2. Three things must happen before code starts: Codex confirms the v3.5 baseline (or names a blocker in the directive's format), the small M0 closure list below is done, and you authorize M1. The open canon items (Keeper protections, zone rules, ruleset choice) do not affect the first slice and are deferred to M3 and M4.
5. **What action is recommended?** CONDITIONAL GO. Relay §9 to Codex; Codex adds its implementation plan, estimates and sign-off. When the joint report is accepted, authorize M1.

**Needs you now:** only the acceptance of this report and the M1 authorization you already intend. **Needs you later (not now):** the Keeper and zone rules (U-1 to U-4) and the ruleset (R-RS), before M3. Nothing here asks you to settle an engineering question.

---
# DETAILED ENGINEERING EVIDENCE

## 0. Status vocabulary (used throughout)
DESIGN COMPLETE = specified and reconciled on paper. IMPLEMENTED = code exists. TESTED = automated acceptance tests pass with evidence artifacts. ACCEPTED = the owner has accepted the evidence.
| Item | Status |
|---|---|
| Frozen B0 (commit 2abe497) and its evidence | IMPLEMENTED, TESTED, ACCEPTED |
| T6 typed boundary, O4 v3.5, O5 v3.5, owner rulings S1-S8 | DESIGN COMPLETE (Codex confirmation of v3.5 pending) |
| Everything in B1 (cognition, MC, ingress, trace, slice) | not implemented |

## 1. Which contracts are ready to freeze (Contract v1-core)
**Ready now** (subject to Codex's confirmation and the M0 items in §3): the T6 typed boundary (`AthleteView`, `Availability<T>`, `ActionIntent`, `MotorCommand`, `PhysicalOutcome`, `DecisionTrace`, `OptionTrace`); O4 v3.5 (seven resources, 21-pair default-NO table, atomic bundles, queue depth one, commitment table with two boundaries, coincident-event algorithm, `EventTime`, `ReactionGate`, `PlanStageActivation`, extension points and conformance profile); O5 v3.5 (structured `CausalId`, 128-bit replay id, registries, allocation key); the three-way self-knowledge split.
**Not frozen in v1-core, carried as typed extensions with `UNRESOLVED_*` markers:** public rules-state fields that depend on U-1 to U-4 (zone clocks, `origin`, Keeper protection matrix), the ruleset binding (R-RS), tackle commitment, Arrow/ball/hand tie, same-team assignment.
**A deviation from rc2 that you should know about.** rc2 §11 asked for the rules-state contract and the typed `AthleteView` schema to be finalized together. I am proposing to freeze the `AthleteView` schema now with the U-dependent fields typed as `Availability::unavailable(reason = UNRESOLVED_RULES_STATE)`, and to finalize those fields before M3. This keeps the information boundary intact (an athlete cannot read a field that does not exist yet) and lets M1 and M2 start. I consider it an engineering default; tell me if you want rc2's ordering kept.

## 2. Genuine blockers
**None found for M0, M1 or M2.** I looked for a concrete failure scenario against canon, PRISM ownership, information boundaries, determinism or physical correctness and did not find one that the current design leaves open. The things that could look like blockers, classified:
| Issue | Class | Reason |
|---|---|---|
| U-1 Keeper protection (KP-01..14) | DEFERRED to M3 | No Keeper in the M1/M2 slice |
| U-2 zone clock reset rule | DEFERRED to M4 | Slice kept away from Keeper Zones |
| U-3 Keeper Zone geometry (G-1..6) | DEFERRED to M3 | same |
| U-4 bounce/out-of-play/restart table | DEFERRED to M4 | Slice has no restart; boundary and goal rulings are already in |
| R-RS ruleset | DEFERRED to M3 | No arrows in the slice. Provisional for M1/M2: B0 ruleset 1.0.1 physics only |
| SELF-1 self-knowledge error | NONBLOCKING | Default exact/null `SelfView`, swept later |
| Tackle commitment, Arrow/ball/hand tie, same-team tie | NONBLOCKING | Extension points; excluded scenarios in v1 profile |
| Advantage for an Archer foul (rulebook 11.2/11.3 unreadable) | DEFERRED to M3 | No Archers in slice; default none |
| Schema widths and enum spellings | NONBLOCKING, M0 deliverable | Proposed in O5 v3.5 |
| Codex confirmation of v3.5 | NONBLOCKING if Codex names no blocker | Directive: presumptive baseline |
| T3A fixtures | **Ask for clarification** | See below |
**T3A.** Codex has said freezing does not authorize "T3A fixture execution". Your 7 November ruling already approved supplemental T3A physical fixtures as separate read-only evidence work. The M1 pass/flight/catch fixtures are part of M0/M1 evidence. I ask that you or Codex confirm that ruling covers them, so no new approval is needed. If Codex reads it differently, that is its to state in the directive's blocker format.
**Biggest implementation risk (not a design blocker).** B0 cognition is not behind a boundary. `prism_field_v0.py` documents that only the carrier's decisions read beliefs, and that "teammates, ball and public status stay true". B1 must therefore build the observation, belief and decision path new, behind `AthleteView`, and must not wrap the legacy controllers. I can reuse the perception/tracker core (`prism_archer_v0`, `prism_perception_v012`, `prism_comms_v0`: about 570 lines) as components, re-hosted off the runtime-patch layer.

## 3. Engineering defaults accepted provisionally
| # | Default | Test that guards it |
|---|---|---|
| D1 | One foreground executable plan per athlete; one active stage; queue depth one per resource | AS-1..5, SUP-11 |
| D2 | Resource compatibility default NO, with the named overrides | SUP-15 |
| D3 | Wind-up non-revocable by cognition once preparation starts | AB arm kept experimental |
| D4 | `ReactionGate` v1 model is null: no extra delay beyond the perception latency B0 already models through the Reaction rating. Ordinary eligibility = max(gate, next slot); planned stage skips only the slot | RG-1, RX-1..9, latency distribution B0 vs B1 |
| D5 | Own-release cut activates at the actor's release outcome with no added delay | give-and-go timing metrics |
| D6 | `SelfView` is exact with zero latency (null case); hidden reserves and exact ratings not exposed | SELF-1..4 |
| D7 | Tackle, Arrow/ball/hand, same-team ties are in `excluded_scenario_classes` of the v1 profile | EXT-1..5 |
| D8 | Ruleset for M1/M2: B0 1.0.1 physics, no arrows, no kicking in B1 | Gate A/B |
| D9 | Widths: 16-digit and 10-digit zero-padded decimals; `EventTime` base unit and fixed-point source named by Codex in M0 | ID-18..21 |
All are behavioral or engineering defaults under your governance rule. None is a canon ruling, and none is presented as approved behavior.

## 4. Dependencies that must be completed before code starts (M0 closure list)
1. Codex confirms v3.5, or lists blockers in the directive's format. *(Codex)*
2. Contract v1-core hash recorded: the schema files for the typed boundary, O4 and O5 with final widths, enum spellings and `EventTime` base unit. *(Codex with me)*
3. `ConformanceProfile` v1-m2 written as data, with excluded scenario classes. *(Codex)*
4. M1/M2 scenario files as data (§5), including seeds and rating sets. *(me draft, Codex implements)*
5. The `AthleteView` subset for the slice listed field by field, with the U-dependent fields marked unavailable. *(me)*
6. M1 behavioral acceptance criteria and metrics list (§7). *(me)*
7. T3A pass/flight/catch fixtures confirmed in scope (§2). *(owner/Codex)*
8. Repository layout: B1 lives in its own package and branch, B0 untouched, a CI check that B0 hashes still verify. *(Codex)*
9. Owner authorization for M1 code.

## 5. Smallest safe B1 scope (the vertical slice)
**M1 (one athlete, complete cycle).** A ball carrier with a defender closing and one inert teammate (a physical body with no cognition, to be a pass target). The carrier alone is a PRISM athlete: it observes through its own cone and radar with latency, forms beliefs about the defender and teammate, decides to carry or pass, plans the pass, Motor Control executes the release, and the physics returns an outcome (completed, intercepted, dropped, or the carrier is tackled). Everything flows through `AthleteView → ActionIntent → MotorCommand → PhysicalOutcome` with causal IDs.
**M2 (give-and-go).** Two PRISM athletes A (carrier) and B (teammate) and two defenders. A passes to B and plans a cut; the plan is A's own. B receives, decides on the return pass independently from its own beliefs (it learns of A's pass through the explicit communication and observation channels the owner ruled on 7 November), and A's cut stage activates only at A's release and executes under arbitration. Defenders are PRISM athletes with the same boundary (they may be simple, but not scripted to fail). Outcomes must include completed combinations and failures.
**Out of slice (explicitly):** Keepers, Archers, restarts, zone rules, fouls, substitutions, fatigue changes, injuries, any formation structure.

## 6. Recommended implementation sequence and milestones
Effort is in focused work sessions and is a low-confidence range. **Codex supplies its own estimates; the figures below are only my cognition-side work.**
| M | Required work | Automated acceptance tests | Evidence artifacts | Dependencies | Completion criteria | My effort / main risk |
|---|---|---|---|---|---|---|
| **M0** Readiness | Close §4 items; freeze v1-core hash; profile and scenario files | schema validation; manifest verifies; B0 hashes unchanged; EXT-3/4 | Contract v1-core hash, profile, scenario files | Codex confirmation, owner authorization | Contract hash recorded and B0 verifies | 1-2 sessions. Risk: Codex raises a late blocker |
| **M1** One athlete cycle | Sensor→ObservationFrame→AthleteView→belief→decision→intent for the carrier; MC release; ingress; PHY outcome; trace and IDs | information-isolation poison tests; NI-1..4; ID-1..14; SUP-2..9; CE-1; AX not needed; Gate B parity on pass/flight/catch fixtures; determinism replay (same seed, same hashes) | trace JSONL, replay hashes, T3A parity report, M1 behavior report (outcome mix) | M0; T3A fixtures | all tests pass; 100 seeds produce at least completed, intercepted and tackled outcomes; every outcome resolves to an observation | 3-5 sessions. Risk: re-hosting the PRISM core off the patch layer hides a true-state read |
| **M2** Give-and-go | Plan layer, `PlanStageActivation`, `ReactionGate`, communication channel, receiver cognition, arbitration of locomotion + release, return-pass decision | RX-1..9; AS-1..5; SUP-8..18; CE-2..5; poison tests for B's view; formation-free provenance test; both-outcomes test | combination timeline traces, planned-vs-unplanned receiving report, latency B0 vs B1 | M1 | combination completes and fails for reasons traceable to athlete decisions or physics; no activation before delivery; B hears nothing it was not sent | 5-8 sessions. Risk: B0-equivalent latency drifts and makes athletes slower |
| **M3** Full athlete integration | Field players, Keepers (TI-9 intents), Archers (C-7), no legacy controllers; U-1, U-3, R-RS decided | AX-1..6; SELF-1..4; KP tests per decided cells; full information-isolation suite; Gate B on all roles | per-role trace sets, KP conformance report | M2; owner decisions U-1, U-3, R-RS | all roles run under B1 interfaces; zero true-state reads | 10-15 sessions. Risk: Keeper and Archer cognition each needs its own belief model |
| **M4** Regulation simulation | Rules-state transitions, restarts, zone clock, scoring, fouls under the chosen ruleset | rules-state transition table tests (U4 scenarios); full-match determinism; boundary/goal/clock rulings (S1-S4) | reproducible match logs, rule-event ledger | M3; U-2, U-4; rules engine work the ruleset needs | complete matches run reproducibly under the approved rules | 8-15 sessions, widest uncertainty. Risk: `RULES_V03` items the notes list as not implemented (offside, Contact Scrimmage, First Hunt, 25-arrow limit) |
| **M5** B1 acceptance | Gate A/B/C evidence, performance, formation-free arm | Gates A, B, C; NI-1..4; performance budget on the phone/headless target | acceptance bundle with all hashes | M4 | information isolation, physical correctness, determinism, behavioral quality, formation-free operation, acceptable performance | 5-10 sessions. Risk: numeric Gate C tolerances were deferred by the owner, so they must be set from M1-M4 distributions |

## 7. Behavioral acceptance criteria (my ownership)
| ID | Criterion | Milestone |
|---|---|---|
| BA-1 | Poison test: replacing every authoritative field a cognition module must not read leaves its decision unchanged | M1 |
| BA-2 | Each decision resolves to an observation, belief and option set held by that athlete at that time | M1 |
| BA-3 | The mix of outcomes over 100 seeds includes success and failure, and each failure has a traceable cause (belief error, latency, physical contest) | M1 |
| BA-4 | Cognition cannot see authoritative opponent ratings or timers; MC cannot see tactical state | M1 |
| BA-5 | A plan stage never activates before its triggering observation is delivered; activation shift equals delivery shift | M2 |
| BA-6 | B's return-pass decision is unchanged when A's hidden state is perturbed and B's delivered observations are not | M2 |
| BA-7 | No receiving position, formation or role is assigned from outside; positions emerge from athlete decisions | M2, M3 |
| BA-8 | Planned versus unplanned receiving, ordinary decision latency B0 versus B1: reported, with no pass/fail threshold set in advance (owner deferred Gate C tolerances) | M2 |
| BA-9 | Defenders in the slice use the same boundary and are not scripted to fail | M2 |
Scenario sketch as data (M2): field 100×100 m, A carrying with D1 pressing at 5-8 m, B 8-15 m laterally and 3-6 m behind A's line, D2 marking B at 4-8 m; ratings uniform 0.70 baseline with seeded variation; 100+ seeds per condition.

## 8. What I am not asking for
No new specification revision, no broad audit, no owner-level engineering question. Residual items stay engineering defaults tested in implementation. Tackle commitment, advantage for Archer fouls and similar come back only if a milestone test shows a real gameplay problem.

## 9. Codex joint sign-off checklist (please fill and return)
| ID | Codex to provide |
|---|---|
| CX-1 | Confirm v3.5 as the implementation baseline or list BLOCKING issues (failure scenario, affected requirement, minimum correction) |
| CX-2 | Final widths, enum spellings, `EventTime` base unit and fixed-point source for Contract v1-core |
| CX-3 | B1 implementation plan: package layout, typed Python `CommandIngress` / `PhysicalExecutionPort`, how PHY reuses the Pocket 3 core, branch strategy |
| CX-4 | Test infrastructure: poison-test harness, determinism replay, Gate B parity runner, CI check that B0 hashes verify |
| CX-5 | Your effort estimates for M0-M5 with the same fields as §6 |
| CX-6 | Agreement or objection on: the v1-core/extension split of rc2 §11 (§1); the null `ReactionGate` default (D4); T3A scope (§2); the slice definition (§5) |
| CX-7 | Performance measurement plan on the phone/headless target |
Disagreements will be resolved between Codex and me by evidence and tests. Only a genuine canon decision or a material gameplay choice reaches the owner.

## 10. Recommendation
**CONDITIONAL GO** to M0, then M1 on owner authorization. Conditions: CX-1 returns no blocker; the §4 items close; the owner authorizes M1. **NO-GO triggers:** a Codex blocker showing an information-boundary or determinism failure that the profile cannot contain, or a finding that the M1 slice cannot run the real interfaces without a legacy controller.
