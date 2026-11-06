# HP-002 Stage B — read-only audit, cognition side
Claude, 2026-11-06, branch `claude/hp002-audit`. Authorized by DreLen's Stage A disposition. **No behaviour, physics, rating, cognition or formation-free change was made or proposed for implementation.** Instruments are behaviour-neutral (scores and event counts identical with and without them in every run). Codex's T2 is independent; reconciliation precedes any change.
Structure per requirement 6: **Part M = measured** (instrument output), **Part S = source-derived** (read from code, not measured), **Part I = interpretation** (my architectural reading, open to challenge). Python 3.13.18, NumPy 2.5.3, commit 2abe497 + audit tools, short games, seeds 1–4 (probe runs 1–3).

---
## Part M — measured evidence
**M1. State fields read by decision functions (requirement 2).** `tools/audit_fields.py` logs every attribute read of Player, Attributes and Ball by each decision function, split by actor/other (self, mate, opp, ball). Full stack, seed 1 (`audit/fields_full_s1.json`, 790 rows). PRISM substitutes only x, y, vx, vy (and ball x/y/vx/vy when FREEVIEW/BALLVIEW). Other fields read **on other players** by decision functions:
| Function (all outside any belief view except where noted) | Non-position fields read on opponents/mates/ball |
|---|---|
| `c4c2_eval`, `pocket_eval`, `pocket_cont`, `c4c2_confront` (carrier shoot/carry/continue values; Keeper come-out) | opp: `fatigue`, `posture`, `frozen`/`freeze_until`, `next_action` (recovery timer), `radius`, `active`, `role`; opp ratings `maximum_speed`, `acceleration`, `braking`, `mass`, `reach`, `height` |
| `pocket_pass_option` | mate: `fatigue`, `target`, ratings `maximum_speed`, `acceleration`, `braking`, `kicking`; mate/opp: `eligible`, `available`, `exclusion_ms`, `injured`, `posture`, `freeze_until` |
| `pass_ranked` (core) | mate: `catching` rating, eligibility/status fields (runs in a view; status fields are not substituted) |
| `Policy.targets` (core, runs in a view) | other players: `slot`, `speed`, `unmarked_ms`, `zone_ms`, eligibility/status; ball: `vz`, `z`, `_path_cache`, `version` |
| `c4c2_targets` (team receiver placement) | carrier `c4c2_intent`, players' `zone_ms`, eligibility/status |
| `route_receiver` | ball `vz`, `z`, `_path_cache`, `intended`, `mode` (true ball state) |
| `c3_desired` (movement/avoidance, ~307k reads) | opp `facing`, opp `a.braking` |
| `catch_contacts`, `fight` (physical resolution) | opponents' physical ratings (catching, strength, balance, contact_resistance, blocking, reach, mass) — expected for resolution |
| `plan_jumps` (legacy jump) | ball `vz`, `z`, `_path_cache`, `intended`, `last_releaser`, `release_time` |
| `c4c_position` (Keeper) | ball `carrier`, `mode`, `z`; opp `id`, `team` plus true opponent/ball positions |
Reading: PRISM perceives kinematics only; every other field a decision reads about another player is true engine state.

**M2. Which decision functions run in a belief view** (Stage A, `audit/trace_full_s1.json`): in the full stack only `Policy.targets` (4,336 in-view calls) and `pass_ranked` (101) ran inside a `with_view`. All others, including carrier decisions (109), evaluation (1,534), `c4c2_confront` (1,481), `c3_contain` (247), `c4c2_targets` (225), `route_receiver` (225), `arrow_decisions` (422), ran on true state.

**M3. Carrier decision information dependence** (Stage A canary, 4 seeds, 2,209 decisions; probe neutral): ≥1 hidden opponent in 47.5% of decisions; belief-view recomputation changes action 5.2%, best pass target 42.8%; hidden-only perturbation changes some option value 19.1%, pass target 4.3%, action 0.6%.

**M4. Jump mechanisms** (`tools/audit_probes.py`, seeds 1–3, probes neutral). B0 flags: only the legacy omniscient `plan_jumps` runs (fired 1, 1, 6 jumps; true predicted ball path). Full stack: **both** mechanisms are active at once. Seed 2: legacy planner fired 2, PRISM-belief `update_jumps` 7; seed 3: legacy 0, PRISM 2; seed 1: none. The legacy planner is not disabled when `CATCH_V2` + `PRISM_JUMP` install the belief-based one.

**M5. Receiver routing information** (full stack, probe neutral). While a pass is in flight the intended receiver is routed from the release instant by `route_receiver` using the true ball:
| seed | route calls | calls where the receiver has no ball belief yet (<3 sightings) | median / p90 distance between true-ball target and his own-belief target |
|---|---|---|---|
| 1 | 50 | 13 (26%) | 0.31 m / 18.7 m |
| 2 | 652 | 157 (24%) | 4.38 m / 18.7 m |
| 3 | 1,032 | 187 (18%) | 8.25 m / 10.1 m |
So in roughly a fifth to a quarter of routing calls the receiver is steered to the interception point before his own perception has registered the course, and, where he has a belief, the true-ball target differs from his belief-based target by metres. (Belief position error itself is small in the median, 0.07–0.08 m, so the gap is dominated by velocity/path differences.)

---
## Part S — source-derived findings (not measured)
**S1. Option generation, evaluation, selection, execution — who owns each (requirement 1).**
| Action | Generates options | Evaluates | Selects | Executes | PRISM *influence* (what it actually changes) |
|---|---|---|---|---|---|
| Carrier choice shoot/carry/continue/pass | legacy: 4 fixed options in `pocket_decide`; pass menu from core `pass_ranked` | legacy: C4C2 drill tables on true state; position/archetype bias (tendencies) | legacy argmax with style band | engine (`make_pass`, `make_shot`, throwing_v1 error model) | menu **filter** (unseen mates removed), menu rank noise (Playmaking), value noise (`judge_opts`) — advisory, not ownership |
| Off-ball movement | core `Policy.targets` (slot-based rows, escorts, chase ranks, zone lines, man marking by slot) then tendencies re-election, then OFFACT five actions | core formulas on belief-swapped positions; OFFACT own scoring (placeholder weights) | engine adopts at `next_decision` cadence; `c4c2_targets`/`route_receiver` can overwrite; OFFACT overrides re-apply | `c3_move` physics | **PRISM owns** only the OFFACT action choice and the perception that feeds `Policy.targets` |
| Defender pursuit | core targets (hunt/man/zone) | `judge_target` (beliefs) | argmax noisy score | physics | Marking noise; belief positions |
| Contain vs drive | `c3_contain` | public state only (tackle count, zone time) — deliberately public | legacy | engine | `duel_flip` flips the answer with probability from Defender Duel |
| Hand region high/low | `c3_region` | uses carrier's preparation timestamp + defender decision_speed delay (approximates observation) | legacy | engine | `duel_flip` |
| Catch | none: catch is automatic acquisition when a hand sphere meets the ball | physics (energy vs `catching`, reach) | automatic | `catch_contacts` / CATCH_V2 | Reaction latency sets readiness; no decision |
| Jump to ball | legacy `plan_jumps` (true path) **and** `update_jumps` (belief) | trajectory/feet-lift feasibility | first to trigger | engine airborne | PRISM supplies belief for one of the two |
| Keeper position | `c4c_position` | true ball/carrier | legacy | physics | Keeper perception only for the *save plan* (flight read) |
| Keeper come-out | `c4c2_confront` | drill tables, true carrier and chasers | legacy boolean | physics | none |
| Keeper save/plan | C4c planner | belief fit (PRISM_KEEPER) | legacy | physics | perception delay and noise; trigger that a new course exists, wind-up and confront triggers stay omniscient (module docstring) |
| Archer shot | `arrow_decisions` | legacy | legacy | engine | none (shadow only, docstring) |
| Substitution | `auto_substitutions` rules | energy thresholds | automatic | engine | none |
| Restart set-up | rules + `restarts_v1`; inbound options in `c4c2_inbound` | room-to-opponent, lane clearance | legacy | engine | none |

**S2. Perfect-information routing: deliberate execution mechanism or cognitive advantage? Where the boundary is crossed (requirement 3).** Trace: (1) `make_pass` sets `ball.intended` (engine state, the passer's choice) → (2) `route_receiver` reads `intended` and the true ball path (`predict_path`) → (3) writes the receiver's target and sets `q.next_decision = now`, bypassing the cadence set by his decision_speed. The docstring says "The receiver uses only what is observable: the ball's current position and velocity". Three separable pieces:
 a. **Knowing he is the intended receiver** — acceptable only if a pass call/communication exists (PRISM II), otherwise it is information the receiver has not perceived.
 b. **Using the true ball state** — a cognitive/perceptual advantage; his own ball belief exists (`S.ball_belief`) but is not used (M5).
 c. **Interception geometry** (`intercept_xy`: reach, acceleration limits) — legitimate execution (physical/motor), independent of where the ball position comes from.
The boundary is crossed at step (2): perception input to an otherwise physical routine.

**S3. Legacy tactical prescriptions that survive a formation-free configuration (requirement 4).** Removing the positional anchors in `positional_tendencies_v1` would not remove these:
 1. Core `Policy.targets` (policies.py:83–194): slot-based lateral rows `(slot%5−2)·width/2` and support lead offsets for non-carriers on offence; escort ring/wedge shapes (`t.escort`, `escort_shape`, spacing); zone defence line at ball ± 12 m with lateral slots `(slot%5−2)·15`; man marking assigned by `slot % len(candidates)`; hunt ranks with fixed lead/angle; carrier lane options dy ∈ {−14,−7,0,7,14}, 12 m look-ahead, near-goal lane at ±3.8 m; chasers: top 3–4 by meeting point; fallback depth `x − sgn(6+rank)`.
 2. `c4c2_targets`: 20 fixed spots (8/12/16/19 m, ±45°…) with the nearest teammate sent; carry-intent drive to goal centre; `ctrl_receivers` count.
 3. Restart behaviour: `c4c2_inbound` (short option 6 m, entry option 12 m, Keeper-zone arc spots), core `award` phase positions (nearest to ball takes it, others at ball+8 m, ±7 m by slot parity), `restarts_v1` set-ups (First Hunt placement; scrimmage placements are rules).
 4. Tendencies: carrier-decision biases by position/archetype (apply to `c4c2_eval/cont/pass_option` independent of positional anchors).
 5. OFFACT authored constants (ENGAGE base, call bonus, stay-near-base term, defenders engage nearest attacker within 8 m) — mine; placeholders.
 6. Block/bounce options: `block_option_v0` prescribes where blockers stand (0.9 m in front of a defender on the carrier's side) and picks targets from true positions (stated limitation); `bounce_option` is a throw primitive (not a tactic) but its use rates are genes.
 7. Roster/slot structure itself (`slot` indexes drive items 1 and 3) and tactics tables `TACTICS`.

**S4. Characterization of the specific pathways (requirement 5)**
| Pathway | Automatic physical response | Athlete cognition | Legacy/omniscient part |
|---|---|---|---|
| Keeper | catch, reach, jump physics | save plan from belief (PRISM_KEEPER) | position vs true ball/carrier; course-change trigger; wind-up/confront triggers; come-out decision `c4c2_confront` |
| Archer | arrow flight and hit resolution | none (shadow) | all of `arrow_decisions` |
| Jump | airborne ballistic | belief-based timing in `update_jumps` | legacy `plan_jumps` still active (M4) |
| Catch | hand-sphere acquisition, energy capacity, hand contests | none (no choice to catch) | `route_receiver` supplies the position |
| Defence | tackle/contact physics; hand fight resolution | pursuit target (Marking), OFFACT engage | contain/region legacy; `c3_desired` avoidance reads true neighbours' `facing`, `braking` (reflexive layer) |

---
## Part I — interpretation (open to challenge)
**I1.** The architecture mixes three tiers: (i) a belief-based perception and a few belief-based decisions (policy targets, pass menu, OFFACT, Keeper save plan, jump), (ii) legacy decisions on true state whose *outputs* PRISM only perturbs, and (iii) physical resolution. Currently PRISM influences far more than it owns. The 0.6% action-flip figure underestimates dependence: pass targets (4.3% to 42.8% by method), option values (19.1%), and fields beyond position (M1) all flow in.
**I2.** `route_receiver` is best split into a *perceptual* part (where the ball is, who is the receiver) and a *motor* part (how to reach the point). Today they are fused. The motor part belongs in Motor Control; the perceptual part is cognition and needs PRISM input or an explicit rule that the pass call informs the receiver.
**I3.** Fields like opponent `fatigue`, `next_action`, ratings (`maximum_speed`, `mass`, …) in carrier evaluation are a different issue from positions: they could be treated as *knowledge* an athlete has about the league (known ratings), or as inference from observation. This is a canon decision, not an engineering one.
**I4.** A formation-free configuration must replace or disable at least S3 items 1–3 and 6 to honour "no prescribed formations"; S3 items 4–5 need a decision on whether position-specific carrier biases count as authored preference. The emergence claim should be reported as emergent from the remaining authored utilities (drill tables, goal factors).
**I5.** The dual jump mechanism (M4) means B0/PRISM comparisons of catching behaviour mix two decision owners; any catching result in the full stack is confounded.

---
## Proposed B1 remediation and validation matrix (requirement 7) — proposal only, nothing implemented
Legend: class = A (instrumentation/bug, no behaviour), B (behaviour change inside current intent), C (canon/rating-semantics decision). Every B/C needs your approval after T2 reconciliation.
| # | Issue | Proposed remediation | Class | Validation test | Acceptance criterion |
|---|---|---|---|---|---|
| R1 | Carrier values on true state (M3) | evaluate `pocket_decide` inside the carrier's belief view; opponents/receivers from beliefs | B | hidden-state canary (hide-only perturbation) + counterfactual probe | hide-only perturbation changes 0 option values; paired match comparison shows no collapse in fouls/score/pace |
| R2 | Non-position fields from true state (M1, I3) | decide canon: which opponent fields are known (ratings, fatigue, posture); add them to belief or to a declared knowledge table | C | field-level poison probe per field | each field either perceived, declared known, or removed from the evaluation |
| R3 | `route_receiver` true ball (S2, M5) | split perception/motor: receiver target from his ball belief; interception stays motor; require a pass-call rule for intended-receiver knowledge | B/C | route probe (gap, no-belief share) | gap to belief target = 0 by construction; no-belief routing share = rule-defined |
| R4 | Dual jump owner (M4) | disable legacy `plan_jumps` when `PRISM_JUMP` is on | A/B | jump counters per mechanism | exactly one mechanism fires; catch rates re-measured |
| R5 | `c4c2_targets` central receiver placement | formation-free: replace by receiver's own off-ball choice on beliefs, or keep as a named legacy arm | B/C | comparison arms (legacy vs removed) with occupancy metrics | pre-registered role metrics; both arms reported |
| R6 | Core `Policy.targets` slot/rows/lines/escort/man-by-slot (S3.1) | formation-free arm replaces the non-carrier branch; keep carrier, keeper, zone-rule branches | C | occupancy and assignment-persistence metrics | arm switch selectable; formation arm unchanged |
| R7 | Restart prescriptions (S3.3) | catalogue as rules vs tactics; keep rule placements, move tactical spots to cognition or mark legacy | C | restart replay | classified list approved |
| R8 | Keeper omniscient triggers (S4) | extend PRISM_KEEPER to positioning and come-out | B | keeper sweeps (existing) + canary | Goalkeeping sweep monotone; no new leak |
| R9 | Archer shadow only | out of scope for B1 unless you decide Archers get PRISM | C | n/a | decision |
| R10 | Kicking present (T1) | rules audit decides RULES_V03 treatment | C | rules audit | no kick events in B1 seeds |
| R11 | Instrumentation as regression | add the tracer, field logger and canary to the test suite with fixed expected outputs | A | run on each commit | in-view/out-of-view table stable or changes flagged |
| R12 | Defender `duel_flip` is advisory only | keep until a decision-ownership design for contain/region exists | C | Defender Duel lab (currently saturated) | monotone effect lab redesigned first |
Dependency order I suggest: R11 → R4 → R1/R2/R3 (information isolation, one canary suite) → R8 → formation-free arm (R5/R6/R7). Calibration of any rating effect stays DreLen's.

## Not covered / limits
Short games and two or three seeds per probe; B0 field-level run not done; the field logger shows which fields are *read*, not whether a read changes a decision; Keeper internals and Archer shadow not traced beyond source docstrings; `block_option` internals and `bounce_option` not instrumented; T2's wrapper pass-through and call-order work is Codex's.

## Reproduce
`python3 tools/audit_fields.py <seed> out.json full`, `python3 tools/audit_probes.py <seed> out.json full|b0`, plus Stage A tools. Data: `audit/fields_full_s1.json`, `audit/probes_*.json`.
