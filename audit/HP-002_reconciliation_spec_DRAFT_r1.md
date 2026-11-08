> **SUPERSEDED (2026-11-08) by HP-002_B1_FINAL_APPROVAL_CANDIDATE_v1.0-rc1.md. Historical evidence only; not governing. See HP-002_SPEC_MANIFEST.json.**

# HP-002 Reconciliation Specification — DRAFT r1 (Claude side)
Claude, 2026-11-06. Branch `claude/hp002-audit`. **Status: proposal. No behaviour change implemented. B0 (2abe497) and all evidence untouched.**
**Codex T2 not yet available to me** (not in repo or uploads). Everything below is from HP-002 Stages A/B only. §9 lists exactly what must be checked against T2 before this is final; nothing here is claimed as reconciled.

Evidence labels used throughout: **[M]** confirmed measurement (Stage A/B data) · **[S]** source-derived · **[P]** proposed architecture · **[C]** unresolved canon decision (yours).

---
## 1. Ownership model (req 1)
Five layers, each with one owner. Rule: a layer may consume only the outputs of the layer above, plus the information classes allowed by §2.
- **G** option generation (what can I do) · **E** evaluation (how good) · **S** selection (which one) · **MC** Motor Control (how to execute: steering, timing, limb commands) · **PHY** physical resolution (contact, flight, catch, tackle).
Cognition (PRISM) = G+E+S on information of class O/K/I only. MC = motor. PHY = engine, deterministic given commands.

| Behaviour | G | E | S | MC | PHY | Today [S/M] | Gap |
|---|---|---|---|---|---|---|---|
| Carrier shoot/carry/continue/pass | Cognition | Cognition (belief view) | Cognition | MC (throw/shot execution incl. error model) | PHY | G,E,S legacy on true state; PRISM advisory [M: 47.5% of decisions have hidden opponent] | E moves into belief view (R1) |
| Pass-target menu | Cognition | Cognition | Cognition | – | – | filtered by perception | ok after R1 |
| Receiver run to pass | Cognition: "I am/am not the target; where do I think the ball goes" | – | – | **MC: interception geometry** | PHY | fused, true ball [M: 18–26% calls no belief] | split (§3) |
| Off-ball movement | Cognition (OFFACT actions) | Cognition | Cognition | MC | PHY | OFFACT cognition; base targets from slot rules [S] | formation-free arm (§5) |
| Pursuit / marking | Cognition | Cognition (Marking) | Cognition | MC | PHY | belief-based targets | ok |
| Contain vs drive, hand region | Cognition | Cognition (observed state only) | Cognition | MC | PHY | legacy rules; `duel_flip` advisory | R12, deferred |
| Jump to ball | Cognition (belief path) | Cognition | Cognition (one owner, §4) | MC (take-off timing/feet) | PHY | two planners [M] | §4 |
| Catch | – | – | none (automatic) | MC (hand placement) | PHY | automatic | no change |
| Block/screen, bounce | Cognition | Cognition | Cognition | MC | PHY | block from true positions [S] | deferred past B1 |
| Restarts | Rules (placements) / Cognition (tactical spots) | | | MC | PHY | mixed | §5 catalogue |
| Substitution | Rules/team management | | | – | – | automatic thresholds | out of scope |
| Keeper, Archer | §6 | | | | | | |

[C-1] Whether evaluation may use **known ratings** of others is a canon question (§2).

## 2. Information-access contract (req 2)
Every read a decision function makes is classified. [P]
- **O Observable**: what the athlete can perceive through PRISM: positions/velocities of seen players and ball (belief), publicly visible state (score, clock, phase, possession, posture of seen players, whistle/rules status), and communicated call-channel information.
- **K Known/previously known**: stable facts the athlete is entitled to hold without seeing now: own full state; own ratings; team roster and slot; rules; **[C-2]** others' ratings (league knowledge); last-seen values (stale belief, with age).
- **I Inferred**: derived by the athlete from O/K (predicted path, estimated fatigue from observed effort, intent estimates). Inference must use only O/K inputs and its own error model.
- **H Hidden engine state**: true positions of unseen players, true ball state to a non-sighted athlete, others' current fatigue, internal timers (`next_action`, `freeze_until`, `unmarked_ms`, `zone_ms`), intended-receiver flag, planned paths, `_path_cache`, RNG state. **Forbidden to cognition (G/E/S).** Allowed to PHY, and to MC only as the executing athlete's own command state.
Enforcement [P]: a typed `AthleteView` object built per decision, exposing only O/K/I fields; decision functions receive it instead of Player/Ball objects. Violations fail loudly in test mode. Existing `with_view` (position substitution) is insufficient because other fields remain live [M1].
Field classification of Stage B's M1 list:
| Field read on others | Class proposed | Note |
|---|---|---|
| position/velocity, facing | O (seen) | belief |
| posture, frozen/ejected/injured status | O if visible, else H | visibility rule needed [C-3] |
| fatigue | H, or I from observed effort | [C-2] |
| `next_action`/recovery timer | H | replace by inference from observed action |
| ratings (speed, mass, reach, height…) | K or I | [C-2] |
| `unmarked_ms`, `zone_ms`, `slot` of others | H (slot: K if teammates) | |
| ball `vz`,`z`,`_path_cache`,`intended` | O (ball belief) / H (`intended`,`_path_cache`) | |
| `last_releaser`, `release_time` | O if seen | |

## 3. Perception routing vs interception geometry (req 3)
Split `route_receiver` into three parts [P]:
1. **Perceptual (cognition):** the receiver's ball belief (position, velocity, age) and whether he knows he is the target. Input = O/K/I only. Knowledge of being the target requires a rule: either a **pass-call/pre-signal** (communication class O) or the receiver infers it from the ball course. [C-4]
2. **Intent (cognition):** choose "go to interception point P*, or hold/abort", from beliefs.
3. **Geometry (MC):** given target P*, compute reachable intercept under acceleration/braking/reach limits and issue the movement command. Geometry may use the athlete's own physical state and the belief path it was given, never the true ball.
`q.next_decision = now` forced reset is removed; routing obeys the athlete's own decision cadence unless a rules event (whistle) preempts. Acceptance (§7): zero reads of H from the geometry function; target equal to geometry(belief) bit-for-bit.

## 4. Jump-decision ownership (req 4)
Single owner for the B1 configuration [P]:
- Cognition owns **whether and when** to jump: `update_jumps` (belief-based, PRISM_JUMP).
- MC owns take-off execution (timing within the decision window, foot/lift mechanics).
- PHY owns the airborne trajectory and contact.
- Legacy `plan_jumps` is **disabled** in B1 (a switch, not deleted code; B0 retains it). Mutual exclusion enforced by an assertion at install: exactly one of {legacy, PRISM} registered; both → startup error. [M: both active in full stack, seed 2 legacy 2 vs PRISM 7.]
- Required before use: confirm `update_jumps` does not read H beyond the belief ball (field audit on that function; not yet done in Stage B) [S gap].
- B0 vs B1 catch-rate difference is expected and must be reported, not recalibrated [C-5: accept as a documented B1 change].

## 5. Legacy tactical prescriptions (req 5)
Classification key: **RULE** (required by the written rules; keep in all configs) · **TACTIC** (authored preference; a configuration choice) · **PLACEHOLDER** (authored constant of mine, no canon source).
| # | Item [S] | Class | Survives removal of tendency anchors? | Proposed treatment |
|---|---|---|---|---|
| 1 | Slot-based lateral rows `(slot%5−2)·w/2`, support lead offsets | TACTIC | yes | formation-free arm replaces |
| 2 | Escort ring/wedge/line shapes and spacing | TACTIC | yes | replace/option |
| 3 | Zone line at ball±12 m, lateral slots ±15 | TACTIC | yes | replace; zone *rule* (if any in the rules) stays |
| 4 | Man marking by `slot % n` | TACTIC | yes | replace with perception-based assignment |
| 5 | Hunt ranks, fixed lead/angle, chase top-3/4 | TACTIC | yes | replace/option |
| 6 | Carrier lane options dy∈{±14,±7,0}, 12 m look-ahead | TACTIC | yes | review; may stay as option generation (G) if framed as locomotion lanes |
| 7 | `c4c2_targets` 20 receiving spots, drive to goal centre | TACTIC (centralised receiver placement) | yes | remove from formation-free arm; receivers self-select |
| 8 | Position/archetype biases in carrier evaluation | TACTIC (authored preference) | yes | [C-6] keep as genes or drop |
| 9 | Restart: ball-taker nearest, others ball+8 m, ±7 m by parity | PLACEHOLDER/TACTIC | yes | replace |
| 10 | Restart: required lines, distances, who may be where | RULE | yes (must) | keep |
| 11 | `c4c2_inbound` short 6 m / entry 12 m options | TACTIC | yes | option generation, review |
| 12 | `restarts_v1` First Hunt/Scrimmage/40 m snap/toss-in placements | RULE where written, TACTIC where chosen | yes | audit item-by-item against rules (T-rules audit) |
| 13 | OFFACT constants (ENGAGE base, call bonus, stay-near-base, 8 m engage) | PLACEHOLDER | yes | pending calibration (yours) |
| 14 | `block_option` screening geometry (0.9 m front) | TACTIC | yes | deferred past B1 |
| 15 | `bounce_option` use rates | genes (TACTIC) | n/a | no change |
| 16 | Kickoff formation prior `mate_prior_true` | PLACEHOLDER; also true-state | yes | replace/remove (H read) |
| 17 | Roster/slot indexing as organisation | structure | yes | slot may remain as identity (K) but must not drive geometry |
Emergence reporting [P]: report role emergence relative to the remaining authored utilities (drill tables, goal factors), distinguishing situational emergence, rating-driven specialization, authored preferences.

## 6. Keeper and Archer (req 6)
**Keeper [P].** B1 scope: (a) keep save-plan cognition on belief (exists); (b) move the *triggers* (course-change, wind-up, confront) to belief; (c) positioning `c4c_position` and come-out `c4c2_confront` onto AthleteView. Catch/reach/dive remain PHY/MC. Deferred beyond B1: Keeper-specific communication, defensive organisation of the zone in front of the goal.
**Archer [P].** B1: unchanged (shadow/legacy `arrow_decisions`), explicitly labelled as non-PRISM and excluded from information-isolation claims. Deferred: Archer perception, target choice, timing as cognition. [C-7] whether Archer cognition is in scope at all.
Reports on B1 results must state that Keeper triggers are/are not yet belief-based and that Archer is legacy.

## 7. Revised B1 remediation and acceptance matrix (req 7)
Test families: **IS** information isolation · **DO** decision ownership · **MF** motor-command fidelity · **PP** physical-outcome preservation. Common rule: fixed seeds, canonical hashing (T1 method), controlled random streams so perturbations do not shift RNG.
| ID | Change | Class | IS test | DO test | MF test | PP test | Pass criterion |
|---|---|---|---|---|---|---|---|
| T0 | Instrumentation as regression | A | tracer in CI | ownership table frozen | – | B0 hash match | B0 hashes unchanged |
| R1 | Carrier decision in AthleteView | B | hide-only perturbation of H/unseen: option values change = 0 | `pocket_decide` registered owner = Cognition | throw/shot command identical given same choice | scoring/foul/pace envelope vs B0 over N seeds with pre-registered tolerance | 0 value change; envelope within tolerance or reported |
| R2 | Non-position fields to O/K/I | C | field-poison probe per field class | – | – | – | each field classified & enforced |
| R3 | Receiver split | B/C | geometry function: 0 H reads; target = f(belief) | owner = Cognition (intent), MC (geometry) | MC emits same command for same target as B0 given same target | catch-rate vs B0 reported | no-belief share is rule-defined |
| R4 | Single jump owner | A/B | `update_jumps` field audit: 0 H reads | exactly one planner fires per jump | take-off command timing distribution vs spec | airborne trajectories identical for identical commands (T3 golden traces) | assertion + counters |
| R5–R7 | Formation-free arm | C | AthleteView only | no TACTIC items active in arm | – | arm vs formation arm both reported | selectable, formation arm bit-identical to B1 |
| R8 | Keeper triggers on belief | B | keeper canary | – | save command fidelity | save% sweep monotone in Goalkeeping | no leak |
| R10 | Kicking elimination | C | – | – | – | zero kick events over N seeds | rules audit decides |
| MC-1 | Motor Control interface (document only) | – | – | – | command schema, deterministic replay | physics golden traces unchanged | per Codex T3 |
Preserved-outcome tolerances must be set before running [C-8].

## 8. Decisions requiring your approval
- **C-1** Is evaluation by Cognition on AthleteView the intended end state (vs advisory PRISM)?
- **C-2** What do athletes know about others: ratings (speed, mass, reach, height…), fatigue, recovery state? Known / inferred / unavailable.
- **C-3** Visibility of posture/status of seen players.
- **C-4** How does the intended receiver learn he is the target (call, inference, none)?
- **C-5** Accept B0→B1 catch/jump differences as documented, not recalibrated?
- **C-6** Position/archetype carrier biases: genes or removed in formation-free?
- **C-7** Archer cognition in scope for PRISM at all, and when?
- **C-8** Tolerances for physical-outcome preservation.
- **C-9** Approve AthleteView as the isolation mechanism (vs more `with_view` fields).
- **C-10** Rules audit scheduling to resolve kicking and RULE vs TACTIC items 10/12.
- **C-11** Order: R11/T0 → R4 → R1/R2/R3 → R8 → formation-free.

## 9. Reconciliation with Codex HP-001 T2 — OPEN
Not performed: T2 report not received. Required checks:
1. Does T2's wrapper pass-through/call-order map agree with my in-view/out-of-view table (M2)? Any wrapper that drops or reorders my substitutions?
2. Does T2's decision-timing finding agree with `next_decision = now` in route_receiver?
3. Do T2's patch-chain results show any function that my tracer saw as one owner but is replaced/wrapped twice?
4. Does Codex's list of true-state accesses include any I did not find (esp. engine/native paths: `c3_desired`, catch contact code)?
5. Does T3 physics trace plan cover the invariants in §7 PP/MF columns (airborne identical for identical commands)?
6. Rules-v0.3 scope for kicking (R10).
Please send the T2 report (or push it on a `codex/` branch); I will return r2 with a conflict table: agree / disagree / new from Codex.

## Not covered
Short runs, 2–4 seeds; `update_jumps`, `block_option`, `bounce_option` not field-audited; Keeper/Archer internals from docstrings; B0 field-level run not done.
