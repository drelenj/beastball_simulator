# HP-002 Reconciliation Specification — DRAFT r2
Claude, 2026-11-07. Branch `claude/hp002-audit`. Supersedes r1 (r1 file left unchanged). **Proposal only. No B1 change implemented. B0-P4-DEFAULT (2abe497) and all T1–T3 evidence untouched.**

**Provenance of this revision.** Inputs: my HP-002 Stage A/B measurements and r1; Codex `HP-001_T2_EVIDENCE_REPORT.md` and `HP-001_T2_EVIDENCE_PACKET.zip` (read in full, report plus inventory/trace files spot-checked); DreLen's r1 review including **IA-001**. **I did not receive Codex's T3 golden-trace evidence** (not in the packet, the repository branches I can see, or the attachments). Every row that depends on T3 is marked `T3-PENDING`; I have not inferred what T3 shows. I have not independently replicated Codex's patch-map match counts or wrapper-chain inventory (accepted as Codex-verified, not Claude-verified); I did replicate the 30-override B0 total in T1.

Labels: **[M]** confirmed measurement · **[S]** source-derived · **[P]** proposed architecture · **[C]** unresolved design/canon decision (yours). Changes from r1 are called out in §10.

---
## 1. Governing principles (revised)
**IA-001 (confirmed).** Athletes hold individual, imperfect knowledge that improves with realistic observation and experience; the engine keeps authoritative true state for physical resolution.
**P1 Determinism, qualified (rev. req 2).** Physical resolution is a deterministic function of: (a) physical state, (b) commands issued to it, (c) environmental conditions, and (d) modelled randomness drawn from named, seeded streams. Replay tests hold all four fixed; perturbation tests change exactly one and report which others were controlled. "Identical for identical commands" is claimed only when (a), (c), (d) are also identical.
**P2 Motor Control access (rev. req 3).** MC may read: the executing athlete's own body state, ratings and fatigue; the physical constraints of the moment (contact geometry, surface, limits); and the command it was given (target, intent, timing). MC may **not** read anything about other athletes or the ball that the cognition layer was not itself entitled to (class H, §3). No tactical information may enter through MC. MC may not choose a target; it may only execute and report feasibility back as an observable of the athlete's own body.
**P3 Belief updating vs attribute progression (rev. req 4).** *Within-match belief updating* = the athlete's observation history, estimates and call-channel information changing as play proceeds. *Attribute progression* = any change to ratings or physical attributes. **No attribute progression is authorized**; ratings are fixed inputs. Whether belief or learned knowledge persists *across* matches is [C] D4; none is implemented or assumed.
**P4 Formation-free criteria (rev. req 5).** *Prohibited:* prescribed tactical assignments, i.e. any structure that tells an athlete where to stand or whom to mark by role, slot, row, line or pre-set shape (slot-based rows, zone lines placed by slot, man-by-slot, centralised receiver placement, escort shapes, authored restart tactics beyond written rules). *Allowed:* tactical behaviour an athlete selects independently from his own beliefs, ratings and the authored utilities (drill tables, goal factors), including behaviour that happens to look like a line, a role or a wedge. Pass/fail tests are tripwires on prescriptions and information isolation; **emergent shape is reported, never required or penalised**.
**P5 Evidence discipline.** B0 and B1 are separate configurations; B0 hashes (T1) are a standing non-regression gate.

## 2. Codex T2 reconciliation table (rev. req 1)
Status keys: **AGREE** (same finding independently) · **EXTENDS** (Codex adds to mine) · **NEW-C** (new from Codex) · **NEW-CL** (Claude-only) · **TENSION** (needs resolution) · **T3-PENDING**. Basis: T2 = Codex source/runtime evidence; mine = Stage A/B.
| # | Topic | Claude HP-002 | Codex T2 | Status | Consequence for spec |
|---|---|---|---|---|---|
| 1 | Who owns carrier selection | PRISM influences; legacy C4c2 selects [S, Stage A trace] | §1, §5.2 step 6: legacy C4c2 selects `max(opts)`; PRISM does not own it | AGREE | Ownership end state in §4 unchanged |
| 2 | Carrier values on true state | 47.5% of decisions have a hidden opponent; belief view changes action 5.2%, best pass target 42.8% [M, 4 seeds, 2,209 decisions] | §7.3: C4c2 values "substantially omniscient" [S] | AGREE (mine is measured, Codex's source-derived) | R1 acceptance uses my canary method plus Codex test 7 (same idea) |
| 3 | `with_view` mechanism | in-view only `Policy.targets`, `pass_ranked`; other fields live [M] | mutation-based, non-thread-safe, incomplete, restores in `finally` [S] | AGREE / EXTENDS | `AthleteView` replaces mutation; thread/multi-match isolation is a requirement (T2 test 11) |
| 4 | `route_receiver` | true ball; 18–26% of calls precede any ball belief; belief-vs-true target median 0.31–8.25 m, p90 10–18.7 m [M, 3 seeds] | explicitly actual ball, "no individual observation latency" [S] | AGREE | §5. I verified at source (`match.py:2517`) that it sets `q.next_decision=s.now`, which opens the C3 gate (`match.py:1300`) for that tick; Codex §5.3 describes the gate but not this bypass → EXTENDS (consistent) |
| 5 | Dual jump planners | both active in full stack; seed 2 legacy 2 vs PRISM 7 [M] | inventory shows `plan_jumps` in the `Match.step` chain and `update_jumps` in the `move_players` chain (`RUNTIME_OVERRIDE_INVENTORY.md`) but the report text does not flag the duplication | AGREE on presence (independent via inventory); firing counts NEW-CL | §6 |
| 6 | Unseen teammate prior | `mate_prior_true` reads true formation position [S] | §7.3 explicit true prior at `prism_field_v0.py:132` | AGREE | Remove in IS work (R-IS) |
| 7 | Target-adoption cadence | known only for `route_receiver` | C3 copies a new target to `p.target` only when `now >= p.next_decision` (`match.py:1298-1302`); "target returned by cognition ≠ target followed" (§7.2) | NEW-C | Ownership tests must assert at `p.target`/command level, not at policy output (§9 DO tests) |
| 8 | Motor Control as a layer | r1 treated MC as an existing layer | §5.3: no single MC API; distributed across wrappers and C3 | NEW-C → corrects r1 | Add **MC-0** (documentation of the actual command surface, no behaviour) before any MC access rule can be enforced (§8) |
| 9 | Pose-maneuver threat | not audited | uses true nearest opponent, distance, velocity; no belief yet (§7.3; `pose_engine_v0.py:87-127` nudges position/scales velocity post-integration) | NEW-C | Added to leak list and to P2 boundary cases; R-IS includes it |
| 10 | Hand fight / C3 true state | `c3_desired` reads opponents' `facing`, `braking` (~307k reads) [M] | correct for physics but must not feed private state back to cognition | AGREE | P2; reflex-avoidance radius/fields is [C] D5 |
| 11 | OFFACT candidates | OFFACT constants are placeholders [S] | candidate set centred on the legacy formation/lane target; "not formation-free" (§7.4) | EXTENDS | P4: OFFACT candidates must be re-anchored on athlete's own state/beliefs in the formation-free arm |
| 12 | Tendency / restart tables | depth tables, archetype biases, restart placements [S] | cites `rule_lane` tables, `DEF_FREEDOM` ("does not create formation-free"), `restarts_v1.py:23-61, 209-260` formation tables | AGREE | §7 catalogue; dead-ball exception [C] D8 |
| 13 | Kicking | RULES_V03 treatment deferred to rules audit | three legacy kick-choice paths (`match.py:680, 949, 969`) reach `Engine.release(kind='kick')`; **the no-kick shim wraps `make_pass`/`make_shot` only, not the engine boundary** (§8.3) | NEW-C | R10 rewritten: gate at engine boundary + positive control (§9) |
| 14 | `patch_source` cardinality | not examined | `replace` hits every occurrence; B0 index 1 matches 3 sites, maximal index 19 matches 2; `all_anchors_exactly_once` false in B0 | NEW-C | Config/cardinality contract is a precondition (CFG-1) |
| 15 | Import-time vs runtime flags; mixed rules state | not examined | `PRISM_JSPLIT`, `CATCH_V2`, `PRISM_KEEPER`, `PLAT`, range flags frozen at import; V03 flags read per call but settings applied at match setup | NEW-C | B1 is defined by a single frozen configuration object; config hash recorded in every run (CFG-2) |
| 16 | Silent flag dependencies | not examined | OFFACT without FIELD is a no-op; HAND_FIGHT without CATCH_V2 exits in `fight()` | NEW-C | Config validator fails loudly on these (CFG-3) |
| 17 | Install order, idempotence | `install()` order listed in my summary | 22-step order, double-install stacks closures, no guard | EXTENDS | Install-chain snapshot test (CFG-4) |
| 18 | First perception tick | not examined | field PRISM updates after wrapped step; first decision may use missing/prior beliefs; ambiguity start/end of 100 ms interval | NEW-C | Belief-timing decision [C] D3; IS test must fix the convention |
| 19 | Shared mutable globals / multi-match | I found and fixed `S.fowner` cross-match contamination earlier [M] | §9 item 9: `S`, gene tables, bounce state, caches at module scope | AGREE / EXTENDS | Multi-match isolation test (IS-6) |
| 20 | Block option, Archer shadow | true positions; shadow only [S] | same | AGREE | §8 |
| 21 | Decision-to-outcome trace | Stage A tracer (ownership by call) | full pass decision → pending action → release with option values (seed 1, t=1389 ms) | EXTENDS | Adopt **decision ID** carried through pending action, release and outcome (ID-1) |
| 22 | B0 override count | 30 total [T1] | 30, split 16 Engine / 13 Match / 1 Policy; my T1 class split was wrong | AGREE on total; **Codex correction accepted** | T1 inventory annotated, not rewritten |
| 23 | Claude-only measurements | canary, field reads, jump firing, receiver-gap, `update_jumps` poison probe (§6) | none (Codex had no access to HP-002) | NEW-CL | Request Codex independent replication of canary + poison probes (D13) |
| 24 | Codex-only items I have not replicated | — | patch-map counts, wrapper chains, V03 table, trace | accepted as Codex-verified | I will spot-check patch-map counts if you ask (D13) |
| 25 | Physical invariants / golden traces | PP column assumed | T3 golden traces | **T3-PENDING** | PP and MF acceptance numbers cannot be finalised until I see T3 |
**Direct contradictions found: none.** One correction to my own r1 (row 8: MC is not an existing layer). One factual precision from me (row 4). Open for T3: whether golden traces cover jump take-off and catch-contact commands with identical-command replay.

## 3. Information-access contract (revised)
Classes: **O** observable now (through PRISM: seen kinematics, visible posture/status, public rules state, communicated information) · **K** known (own state and ratings, roster, rules, physical constants, declared league knowledge) · **I** inferred (from O/K with the athlete's own error model; includes within-match belief) · **H** hidden engine state (unseen true positions, true ball to an unsighted athlete, others' fatigue/timers, `next_action`, `freeze_until`, `unmarked_ms`, `zone_ms`, `intended`, `_path_cache`, RNG state). Cognition (G/E/S) reads O/K/I only; MC reads only P2's list; PHY reads true state.
Mechanism [P, D10]: a typed `AthleteView` constructed per decision (and per MC command), exposing only O/K/I; decision code receives it instead of live Player/Ball objects. Belief timing convention fixed by D3.
Field proposal for approval (D1), from the Stage B field list: positions/velocities/facing of seen players = O; body size (height, reach, mass as visible build) = O; skill/physical ratings of others (`maximum_speed`, `acceleration`, `braking`, `catching`…) = I (estimated from observation) unless you declare league-known; fatigue = I from visible effort; posture/status = O if seen; `next_action`, timers, `slot` of opponents, `unmarked_ms`, `zone_ms`, `intended`, `_path_cache` = H; ball `vz`, `z` = O via ball belief; `last_releaser`, `release_time` = O only if the release was seen.

## 4. Ownership model (G generation, E evaluation, S selection, MC, PHY)
Unchanged from r1 §1 except: (i) MC is the *to-be-documented* command surface (MC-0), not an existing component; (ii) the receiver row follows §5; (iii) jump row follows §6; (iv) target adoption cadence (Codex row 7) belongs to MC and is a documented, test-visible part of its contract. End state: cognition owns G/E/S on O/K/I (IA-001); advisory-only PRISM influence on legacy decisions is the status quo, not the target.
| Behaviour | G | E | S | MC | PHY |
|---|---|---|---|---|---|
| Carrier choice | Cog | Cog (AthleteView) | Cog | throw/shot execution incl. error model | PHY |
| Off-ball movement | Cog | Cog | Cog | MC (cadence, steering) | PHY |
| Pursuit/marking | Cog | Cog | Cog | MC | PHY |
| Receiver | Cog (belief, intent) | Cog | Cog | MC (intercept geometry on belief path) | PHY |
| Jump | Cog (belief) | Cog | Cog (single owner) | MC (take-off) | PHY |
| Catch | none | none | automatic | MC (hand placement) | PHY |
| Keeper, Archer | §8 | | | | |
| Restarts | Rules for written placements; Cog for tactical spots | | | MC | PHY |

## 5. Perceptual routing vs interception geometry
Unchanged in structure from r1 §3, with Codex-driven additions: (a) perceptual part: receiver's ball belief and knowledge of being the target ([C] D2); (b) intent part: go/hold/abort; (c) geometry part (MC): `intercept_xy` on the belief path with the athlete's own limits; (d) the forced `q.next_decision = s.now` is removed from the routing path (it is the current cadence bypass); a rules event (whistle) may still preempt. Acceptance: geometry function has zero H reads and equals f(belief) exactly.

## 6. Jump ownership and the `update_jumps` field audit (rev. req 6)
**Measured (this revision).** `tools/audit_update_jumps.py` poisons the true ball's kinematic fields (x, y, z, vx, vy, vz → 1e6) *only for the duration of each `update_jumps` call*, restoring afterwards.
| Seed | Jump-firing calls | Plain vs poisoned: score | event-log hash | Result |
|---|---|---|---|---|
| 1 | 0 | identical (A5–B0) | identical | no information (no jumps) |
| 2 | 9 | identical (A8–B7) | identical | no dependence observed |
| 3 | 3 | identical (A0–B5) | identical | no dependence observed |
Positive control: with `PRISM_JUMP=0` (the function then reads the true ball) seed 2 plain vs poisoned **diverge** (score A5–B0 vs A0–B5, different log hashes), so the probe can detect the dependence it tests for. Data: `audit/ujump_*.json`.
**Source-derived [S] residual reads** in `update_jumps`: the athlete's own fields (jump height, reach, hand height, posture, eligibility, id, role); `self.assume['gravity']` (K); ball `carrier` (who holds the ball) and `last_releaser`, `radius`; the belief from `S.ball_belief`. Only ball kinematics were poisoned. `ball_belief` passes the live ball object into `kp_ball`; the poison shows no dependence on its six kinematic fields but did not test other Ball fields (`mode`, `intended`, `_path_cache`).
**Limits:** 12 jump-firing calls over three short games is a small sample. The in-game counter `stats['field_jumps']` (7 and 2) is lower than my count of firing calls (9 and 3); I have not resolved why (possibly per-period stats reset) and have not relied on it. Poisoning covers ball kinematics only.
**Also noted [S]:** `update_jumps` is invoked every physics step for all active field players and is not gated by the athlete's decision cadence; his latency is only the sighting threshold (`PRISM_JUMP_OBS=8`). Whether jump should instead pass through the decision cadence is a design question (D6).
**Single-owner design for B1 [P] (not authorized):** Cognition owns whether/when (`update_jumps`, belief-based); MC owns take-off execution; PHY the flight. Legacy `plan_jumps` disabled by configuration (code retained for B0); install-time assertion that exactly one planner is registered. **Preconditions before activation can be proposed for approval:** (1) extend poison coverage to all Ball fields and `b.carrier`/`last_releaser` classification (O only if seen); (2) larger sample (more seeds, targeted jump scenarios); (3) T3 evidence that take-off/airborne commands replay identically; (4) B0→B1 catch-rate change measured and reported, not recalibrated. Status: *conditionally promising, not yet sufficient.*

## 7. Legacy tactical prescriptions (catalogue; rule vs prescribed tactic)
Class: RULE (written rule, kept in all configs) · TACTIC (authored prescription) · PLACEHOLDER (authored constant, no canon source) · INFO (an information-access defect, not a tactic).
| # | Item | Class | Survives removal of tendency anchors | B1 / formation-free treatment |
|---|---|---|---|---|
| 1 | `Policy.targets` slot rows `(slot%5−2)·w/2`, lead offsets | TACTIC | yes | formation-free arm removes |
| 2 | Escort ring/wedge/line, spacing | TACTIC | yes | removes |
| 3 | Zone line ball±12 m, lateral slots | TACTIC (zone as a *rule* only if the rules write it) | yes | removes; rules audit decides any written zone |
| 4 | Man marking by `slot % n` | TACTIC | yes | replaced by perception-based assignment |
| 5 | Hunt ranks, chase top-3/4, fixed lead | TACTIC | yes | removes |
| 6 | Carrier lane menu dy ∈ {±14,±7,0}, 12 m look-ahead | TACTIC (option vocabulary) | yes | review: allowed only as athlete-generated options |
| 7 | `c4c2_targets` 20 receiving spots, goal-centre drive | TACTIC (centralised receiver placement) | yes | removes |
| 8 | Position/archetype carrier biases; `rule_lane`; `DEF_FREEDOM` | TACTIC | yes | [C] D12 (genes vs removed) |
| 9 | Award/restart "ball-taker nearest, others +8 m, ±7 m parity" | PLACEHOLDER/TACTIC | yes | replaced |
| 10 | Rule-required restart lines/distances/legal positions | RULE | yes | kept |
| 11 | `restarts_v1` formation tables, First Hunt, snap alignments | RULE where written, TACTIC where chosen | yes | item-by-item rules audit; dead-ball exception D8 |
| 12 | `c4c2_inbound` short/entry/arc options | TACTIC (option vocabulary) | yes | as item 6 |
| 13 | OFFACT candidate set anchored on legacy target; constants | TACTIC + PLACEHOLDER (Codex §7.4) | yes | re-anchor on own state/belief; constants await DreLen's calibration |
| 14 | `block_option` screening geometry | TACTIC; also INFO (true positions) | yes | deferred beyond B1 |
| 15 | `bounce_option` rates | genes | n/a | unchanged |
| 16 | Kickoff prior `mate_prior_true` | PLACEHOLDER + INFO | yes | removed |
| 17 | Pose-maneuver threat on true nearest opponent | INFO | n/a | AthleteView (R-IS) |
| 18 | Slot indexing as organising structure | structure | yes | identity only; may not drive geometry |
Reporting rule [P]: emergence is reported as situational emergence vs rating-driven specialization vs authored preference, relative to the remaining authored utilities.

## 8. Keeper and Archer (rev. req of r1 §6, unchanged in substance)
**B1 Keeper:** save-plan on belief (exists); triggers (course change, wind-up, confront), `c4c_position`, `c4c2_confront` move to AthleteView; catch/reach/dive stay MC/PHY. **Deferred past B1:** Keeper communication; zone organisation. **Archer:** unchanged legacy/shadow, labelled non-PRISM and excluded from every information-isolation claim; Archer cognition [C] D11. B1 reports must state Keeper-trigger status and Archer status.

## 9. Revised validation matrix and test-first plan (rev. req 7)
**Rule: tests are built and run against B0 *before* any behavioural change, producing a red-baseline ledger (the failures B0 is expected to show). A change is accepted only when its tests turn green and the B0 non-regression gate and T3 golden traces are unchanged. Ownership and information-access tests precede every replacement.** Families: **CFG** configuration · **ID** intent-to-outcome traceability · **IS** information isolation · **DO** decision ownership · **MF** motor-command fidelity · **PP** physical-outcome preservation.
| Test | Family | What it checks | Expected at B0 | Pass at B1 |
|---|---|---|---|---|
| CFG-1 | CFG | exact match count and site for every `patch_source` replacement (Codex T2 test 1) | red (index 1 = 3 sites) | each multi-site anchor split into explicit entries |
| CFG-2 | CFG | single frozen config object, config hash in every run; import-time flags checked | red | all runs carry hash; mixed rules state impossible |
| CFG-3 | CFG | invalid combinations fail loudly (OFFACT w/o FIELD, HAND_FIGHT w/o CATCH_V2) | red | fails at startup |
| CFG-4 | CFG | install-chain snapshot, double-install rejected | red | snapshot stable |
| ID-1 | ID | decision ID from choice → pending action → release/contact → outcome | n/a | 100% executed actions traceable or classified emergent contact |
| IS-1 | IS | hide-only perturbation of H state: option values/targets invariant | red (M3: 19.1% values change) | 0 change, controlled random streams |
| IS-2 | IS | per-field poison for every H/I field in §3 | red | each field perceived, declared known, or unread |
| IS-3 | IS | receiver geometry: 0 H reads, target = f(belief) | red (M5) | exact |
| IS-4 | IS | pose threat, `c3_desired` reflex, block option read only AthleteView fields | red | per D5 |
| IS-5 | IS | belief timing convention (start vs end of interval) fixed and tested | red/undefined | convention D3 enforced |
| IS-6 | IS | multi-match and parallel isolation (no leakage via `S`, caches, genes, bounce state) | partly red | clean |
| DO-1 | DO | ownership sentinels: unique marker per layer, assert final precedence at policy → C4c2 → routing → cadence → `p.target` → C3 | green/red per layer (records current owner) | owner = §4 |
| DO-2 | DO | exactly one jump planner registered/firing per jump | red (two) | one |
| DO-3 | DO | no TACTIC items in §7 invoked in the formation-free arm (tripwire) | n/a | zero calls |
| MF-1 | MF | MC command schema: same cognitive output → same command; MC reads only P2 fields | undefined (MC-0 first) | holds |
| MF-2 | MF | throw/shot command → release matches the error model distribution | baseline recorded | unchanged within D9 |
| MF-3 | MF | jump take-off timing vs commanded window | baseline | within D9 |
| PP-1 | PP | T3 golden traces: identical physical state + commands + environment + RNG streams → identical outcome (P1) | **T3-PENDING** | exact |
| PP-2 | PP | B0 non-regression: ten accepted T1 cases (score, events, canonical hashes) | green | green (B0 config) |
| PP-3 | PP | B1 outcome envelope vs B0 over N seeds (scoring, fouls, pace, catch rate) with pre-registered tolerances | n/a | within D9 or reported as a documented B1 change |
| RL-1 | rules | no legal kick reaches physics: force all three legacy kick paths plus direct `Engine.release(kind='kick')`/`strike`; positive control `RV03_NOKICK=0` | red (shim not at engine boundary) | green |
| RL-2 | rules | rules matrix `RULES_V03 × RV03_SCRIM × RV03_NOKICK × RV03_FLAT × RV03_MARK` | red/unknown | specified |
Not covered: Codex's V03 discipline table (T2 test 13) is rules-side and owned by the rules audit.

## 10. Dependency order (rev.)
0. **Preservation:** tag/hash B0 and T1–T3 packets; no code. 1. **Test harness only (no behaviour):** CFG-1..4, ID-1, DO-1, IS-1/2 run in log-only mode, PP-2; produce the red-baseline ledger. 2. **MC-0:** document the actual command surface (documentation, no behaviour). 3. **Rules audit and RL-1/RL-2** (decides the B1 baseline; independent of cognition; resolves kicking and RULE vs TACTIC for §7 items 10–11). 4. **Jump:** finish §6 preconditions, then request authorization for single-owner jump. 5. **Information isolation:** AthleteView, then carrier decision, receiver split, pose threat, reflex fields (each gated by its IS/DO tests). 6. **Keeper triggers.** 7. **Formation-free arm (separate experimental mode, formation arm bit-identical).** Deferred: Archer cognition, Keeper communication, block option, native rewrite, any recalibration, any rating development. Gate after every step: your approval + PP-2 green + T3 traces unchanged.

## 11. Decisions requiring your approval (rev.)
r1 items resolved or reframed: C-1 resolved in principle by IA-001; C-2 now D1.
- **D1** Approve or amend the §3 field-classification proposal (others' ratings/fatigue/posture/status, body size visible).
- **D2** How the intended receiver learns he is the target: pass call, inference from the ball's course, or neither.
- **D3** Belief timing: decisions use beliefs from the start of the 100 ms interval, or after the current step's perception update.
- **D4** Whether any knowledge persists across matches ("experience"). Within-match updating assumed; no rating development authorized.
- **D5** Reflex-avoidance (`c3_desired`) information limits: which observable neighbour fields and what radius; whether others' `braking` may be read.
- **D6** Jump: after §6 preconditions, authorize single belief-based owner for B1? and should jump decisions pass through the athlete's decision cadence?
- **D7** Rules audit schedule and engine-boundary no-kick gate (RL-1), including the B1 rules baseline (RULES_V03 treatment).
- **D8** Dead-ball formations in the formation-free mode: set-piece exception or prohibited anchors.
- **D9** Tolerances for MF/PP "preserved" (pre-registered before any run).
- **D10** Approve `AthleteView` as the isolation mechanism and a frozen config object (CFG-2).
- **D11** Archer cognition: in scope for PRISM, and when.
- **D12** Position/archetype carrier biases in the formation-free arm: genes or removed.
- **D13** Authorize cross-replication: Codex replicates the canary and jump-poison probes; I spot-check Codex's patch-map counts.
- **D14** Please send Codex's T3 golden-trace evidence (needed for PP-1, MF-2, MF-3).
- **D15** Approve the dependency order in §10 and the test-first rule in §9.

## Reproduce
`python3 tools/audit_update_jumps.py <seed> out.json plain|poison` (env `PRISM_JUMP=0` for the control). Data `audit/ujump_{plain,poison}_s{1,2,3}.json`, `audit/ujump_ctrl_{plain,poison}_s2.json`.
