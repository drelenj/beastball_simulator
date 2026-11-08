# HP-002 — Codex coordination request (round 2) and refined behavior specifications
Claude, 2026-11-08. Non-governing. rc2 and manifest v2 unchanged; Contract v1 NOT FROZEN; B1 not authorized; frozen B0 preserved. This document keeps three things apart: **VERIFIED B0 EVIDENCE** (read from frozen source, unchanged), **PROPOSED B1 BEHAVIOR** (nothing implemented or run), and **ACCEPTANCE CRITERIA** (how each proposal would be judged). Governance classes follow the 2026-11-08 rules; nothing here is an owner decision.

## A. What was accomplished
- Relay-ready Codex request covering J-7, J-4 consistency, J-5 abort costs, commitment events, command resources and coincident-event precedence, with a response slot for every item (§1).
- Refined specifications for J-4, J-5, J-7 and SELF-1 incorporating your five review points (§2–§5).
- **T6-O4 v3 and T6-O5 v3 are NOT written.** You asked for them after Codex responds; I have no Codex response. §6 lists the exact inputs each needs.

## 1. Codex request (please relay; answer ACCEPT / ACCEPT-WITH-CHANGE / DISAGREE per item, with reasons and evidence)
| ID | Item | My proposed position | Codex to provide |
|---|---|---|---|
| X-1 | **J-7** active executable plans vs deliberation | limit applies only to executable plans (default one per athlete); alternatives held in cognition are unbounded by this limit (§4) | agreement, or a scenario that needs two executable plans |
| X-2 | **J-4** activation consistency | activation requires delivery of the observation, then the experimental reaction time; corridor-consistency check; no cadence wait (§2) | check that this fits the T6 observation-delivery and reaction-gate contract; identify any timing field it would violate |
| X-3 | **J-5** abort physics | abort forfeits wind-up progress and locks `ball_release` for a recovery tied to the time spent (§3) | confirm B0 `c3_tuck` is the right physical precedent (what it does and does not reset), and any engine state an abort must also touch |
| X-4 | **Commitment events** | per action, a named commitment event after which cognition cannot revoke | table: action, commitment event, evidence (file, line, trace), B0 behavior, and your classification KEEP / CHANGE / UNDECIDED against B1 requirements (not against B0 existence) |
| X-5 | **Command resources** | `locomotion`, `ball_release`, `hands_reach`, `contact`, `takeoff`, `archer_draw` as exclusive resources | confirm or correct the set; which actions occupy which; compatibility pairs; atomic multi-resource bundles that exist |
| X-6 | **Coincident-event precedence** | one pre-event snapshot, causal dependencies, then an approved precedence table; `batch_seq` in the order key | the table: pairs of simultaneous event types (for example contact vs release, grounding vs release, interception vs catch), the precedence, rationale, evidence |
| X-7 | Outstanding earlier items | TI-9 Keeper modes; CT-4 per-step PRISM-stream hashing; RN-3 fixed-draw fixtures; SQ-1 phase 4 | responses as requested in the round-1 form |
Response record: all seven are **AWAITING CODEX**. No agreement is assumed.

## 2. J-4 receive stage (BEHAVIORAL) — refined
**Verified B0 evidence (unchanged).** Decision cadence `decision_speed × (1.3 − 0.4 × awareness)`, `decision_speed` default 0.3 s in the type definition (uniformity across the roster unconfirmed). Receiver readiness follows elapsed observation (`match.py:2244-2254`). The intended receiver gets a hidden credit of up to 500 ms through `pass_signal` (`match.py:862, 2251`). The intended receiver is routed on the true ball path with `next_decision` reset (`route_receiver`).
**Proposed behavior.**
- A preselected receive stage (athlete-chosen at the source decision) may activate after: the observation of the return is *delivered* to A, plus an **experimental reaction time `ρ_plan`**, with no wait for a cadence slot.
- `ρ_plan` is a configuration value flagged `experimental: true`. Initial value: A's mean ordinary slot wait (half the cadence, about 0.15 s at B0 defaults). It is not a validated athletic constant and is not rating-calibrated; no rating is recalibrated.
- The observed return must be consistent with the preselected corridor; otherwise the stage is dropped and ordinary cognition continues.
**Acceptance criteria.**
| ID | Criterion |
|---|---|
| RX-1 | hard invariant: no activation before the observation's `delivered_at` + `ρ_plan`, over all runs; counterexample count must be 0 |
| RX-2 | shift the observation's delivery by Δ: activation shifts by Δ |
| RX-3 | no return, or a return outside the corridor: no activation |
| RX-4 | change the hidden truth (B's true release time or true A-view quantities) while holding delivered observations fixed: activation unchanged (information isolation) |
| RX-5 | planned versus unplanned receiving, same situations: report catch success, time from delivery to first motion, interception rate |
| RX-6 | sweep `ρ_plan` over {0, 0.5, 1, 1.5, 2} × initial value and report the dose-response, with no threshold set in advance |
| RX-7 | no hidden advantage equivalent to B0's 500 ms credit: with communication disabled, planned and unplanned readiness differ only through `ρ_plan` and the corridor |

## 3. J-5 wind-up abort (BEHAVIORAL) — refined
**Verified B0 evidence (unchanged).** Wind-up 250 × (1.35 − 0.5 × ball_handling) ms. While a pending action exists the carrier makes no new decisions. A defender hold stalls the wind-up; when the stall reaches `tuck_after_delay_frac` of its length the pending release is cancelled (`c3_tuck`): the ball is retained and "nothing else is reset" (`match.py:1479-1492`). No cognitive abort exists in B0.
**Proposed behavior (physically coherent abort).**
1. An athlete may revoke an uncommitted pass intent at a decision opportunity. Effect: the ball stays in hand; the wind-up progress is forfeited (a new pass needs a new full wind-up).
2. **Recovery:** the abort occupies `ball_release` for a recovery proportional to the wind-up already spent (experimental factor, initial 1.0). A new pass on any target can therefore not begin before that recovery ends.
3. A restart needs a fresh decision at a later slot; an abort and a new pass cannot be issued in the same slot.
4. An abort under restraint behaves as the restraint dictates (the hold already stalled or cancelled the wind-up); it does not remove the hold's effect.
5. Loop protection comes from physics and cadence, not a counter: each cycle costs at least one cadence period plus the forfeited wind-up, during which defenders keep acting.
**Acceptance criteria.**
| ID | Criterion |
|---|---|
| AB-1 | abort leaves the ball held, progress zero, `ball_release` occupied for the specified recovery; verified against the B0 tuck as the physical precedent |
| AB-2 | adversarial oscillation test: scripted belief alternating between two targets every slot; report aborts per second (must not exceed 1 per cadence period), releases per possession, and possession loss versus baseline |
| AB-3 | no abort and new pass in one slot; no abort by a plan guard from hidden state |
| AB-4 | ablation arm in Gate C: revocable with cost versus non-revocable; report abort rate, flip-flop rate (three or more consecutive aborts), pass completion, interception, time to release, tackles during wind-up |
| AB-5 | repeated-loop run of 10,000 possessions with ratings varied: no state in which a carrier neither releases nor loses the ball while time passes without physical consequence |
If AB-4 shows a material gameplay difference that existing requirements cannot resolve, I will report the numbers as a behavioral escalation.

## 4. J-7 plan limits (ENGINEERING) — refined
Two things are kept distinct:
- **Executable plan:** a selected plan whose stages can generate commands. Default limit: one per athlete (configuration). A newly selected plan replaces it with a recorded `supersedes` edge.
- **Opportunity assessment:** the athlete's evaluation of alternative future opportunities (other receivers, other cuts, shot or carry). It lives in cognition as beliefs and option sets, holds no resource, generates no command, and is **not limited by the executable-plan limit**. It is limited only by the existing attention and cadence model.
Acceptance: AS-1 an athlete evaluates N alternatives at a slot while holding an executable plan; decision counts and executable plans are unchanged. AS-2 selecting a new plan replaces the old one with an edge. AS-3 alternatives never appear in the command ingress. AS-4 evaluation functions raise if called from a stage activation (extends DO-1). AS-5 raising the limit to two executes without code change and changes no B0 hash (the limit is data).

## 5. SELF-1 (BEHAVIORAL) — refined: two different kinds of self-knowledge
**Verified evidence.** The accepted restricted Motor Control reads the athlete's own body and the command-local constraint projection (rc2 §3, T6 R-03). B0 cognition reads true own state because B0 policies run on true state outside a view (T1/T2 findings).
**Proposed.**
| | Motor-level proprioceptive feedback | Tactical access to own state |
|---|---|---|
| Consumer | Motor Control only | cognition through `SelfView` |
| Content | the athlete's own body signals needed to execute a command: velocity, balance, contact forces on the body, limb and ball-in-hand state, locally and with the control latency the model defines | what the athlete knows for deciding: own position and motion as perceived, felt fatigue and posture, own capabilities as an individual estimate |
| Exactness | exact for control purposes, restricted to the command-local projection | parameterized error and latency; the null case (exact) exists for testing |
| Not included | any other athlete, any hidden attribute | the authoritative physical state object, exact hidden values (true fatigue reserves, ratings, timers) |
Checks: type-level isolation (cognition cannot import or read `MotorFeedback` or the authoritative state); poison tests on the authoritative fields during cognition; MC fed a perturbed `SelfView` produces identical output (MC does not depend on tactical self-knowledge); an IQ sweep over own-state error. Initial tactical error values are experimental defaults, flagged as such.

## B. What changes for B1 athlete behavior
Receivers executing a planned give-and-go respond slightly earlier than unplanned ones, bounded by observation delivery and an experimental reaction time. Passers can abort a wind-up when their delivered information changes, at a cost in time and ball security, and cannot do so in a loop for free. Athletes can think about several futures at once but can only be executing one plan. Cognition no longer touches exact authoritative self-state; motor control keeps what it needs to move the body.

## C. Verified versus proposed
Verified (B0 evidence): cadence and wind-up formulas, pending-action behavior, tuck mechanics, `pass_signal` credit, receiver routing. Proposed (nothing run): `ρ_plan`, abort recovery rule and its factor, executable-plan limit, MotorFeedback/SelfView split and its defaults. Pending: every Codex response (X-1…X-7).

## D. What requires owner approval
Nothing. J-4 and J-5 would become behavioral escalations only if AB-4 or RX-5/6 show a material gameplay difference that existing requirements cannot resolve; I would bring the numbers.

## E. Recommended next action
1. Relay §1 to Codex and return its answers.
2. On receipt, write T6-O4 v3 and T6-O5 v3. **Inputs needed:** from X-4 the commitment-event table and from X-5 the resource and compatibility table (O4 v3); from X-6 the coincident-event table (O4 v3 and the `batch_seq` rule in O5 v3); from X-1 to X-3 the plan, activation and abort contracts; from X-7 the earlier items. Remaining disagreements will be reported with an engineering resolution proposed for acceptance by test, not escalated.
3. Contract v1 stays not frozen; no implementation begins.
