# HP-002 Reconciliation Specification — DRAFT r3
Claude, 2026-11-07. Branch `claude/hp002-audit`. Supersedes r2 (r1, r2 left unchanged). **Proposal only. No B1 change, recalibration, physics change or native work implemented. B0-P4-DEFAULT (2abe497) and all T1–T3 evidence untouched.** Instruments in `tools/` are read-only; §7 measures that they are behaviour-neutral.
Labels: **[M]** measured · **[S]** source-derived · **[P]** proposed architecture · **[O]** open decision (§12). Provenance: my HP-002 audits; Codex T2 and T3 reports and packets (read; T3 trace files re-checked for byte-identity between each trace and its repeat; I did **not** recompute Codex's canonical hashes or re-run T3 generation, which depends on Codex's repository layout and Python/NumPy versions that differ from mine).

## 0. Change log r2 → r3
1. **Archer cognition is mandatory in B1 (C-7, decided).** All deferral language removed (old §8, §10, D11). New §8 gives Archer ownership, information, Motor Control and physical-outcome requirements; new AR-* tests; the dependency order phases Archer work but B1 acceptance requires full Archer coverage (§10, §11).
2. **Correction to my earlier reports.** Stage B and r1/r2 said the Archer is "shadow only." That is true of the default configuration, but the code has a second mode, `PRISM_DRIVE=1`, in which the archer decides from belief. I read the module docstring and did not test that mode. §8 now covers both.
3. **T3 incorporated (§5)**, with the distinction between historical physical preservation and canonical correctness, and an explicit list of physical behaviour for which no golden evidence exists (arrows, jump, Keeper, receiver rerouting).
4. **`next_decision` bypass audited (§6)** with measurements and a ruling proposal.
5. **Instrumentation neutrality measured and specified (§7).**
6. **DO-3 rewritten** around provenance of assignments (§9).
7. **Three separate acceptance gates (§11):** A unchanged-B0 replay, B identical-input physical parity, C intentionally changed B1 cognition.
8. **IA-001 tightened (§3):** no direct cognition or Motor Control access to hidden opponent attributes. This withdraws r2's option of declaring others' ratings "league-known" and settles r2 D5 (others' `braking` may not be read).
9. **Decision register (§12)** lists decided items separately; only genuinely open decisions remain (O1–O10).

## 1. Governing principles
**IA-001 (decided).** Athletes hold individual, imperfect knowledge that improves with realistic observation and experience; the engine keeps authoritative true state for physical resolution (PHY). Cognition and Motor Control never read hidden state; PHY may.
**P1 Determinism, qualified.** Physical resolution is a deterministic function of physical state, commands, environmental conditions and modelled randomness from named seeded streams. Replay tests fix all four; perturbation tests vary one and state which others were held.
**P2 Motor Control access.** MC reads: the executing athlete's own body, ratings and fatigue; physical constraints of the moment; the command it was given. MC reads nothing about other athletes or the ball that cognition was not entitled to, and no hidden opponent attribute. MC chooses no target.
**P3 Belief updating ≠ attribute progression.** Within-match belief change is allowed; **no rating or attribute development is authorized.**
**P4 Formation-free.** Prohibited: externally prescribed tactical assignments (positions, markers, receiver spots, restart tactics assigned by slot, role, row, line, formation table or a team-level planner). Allowed: tactical options an athlete generates and selects himself from his own beliefs and ratings, and any spatial organization that emerges. Emergent shape is reported, never required or penalised.
**P5 Preservation vs correctness.** Matching B0 (or T3) proves *historical physical preservation*. It says nothing about *canonical physical correctness*, which neither T3 nor this audit adjudicates (T3 §9.9).

## 2. Evidence status summary
| Area | Measured | Source-derived | Unavailable / not done |
|---|---|---|---|
| Carrier information | 47.5% of decisions with a hidden opponent; hide-only perturbation changes option values 19.1% (4 seeds) | C4c2 selects; PRISM advisory | — |
| Receiver routing | 18–26% of calls precede any ball belief; belief-vs-true target gap | §6 | no golden trace (T3 excludes rerouting) |
| Cadence bypass | §6 | `match.py:2517` | sibling sites (`match.py:378,381`) not measured |
| Jump | both planners fire; `update_jumps` poison probe identical on 3 seeds | residual reads | larger sample, other Ball fields; no jump golden trace |
| Archer | §8: shadow hash-identical to non-PRISM; belief errors; drive-mode outcome changes | prescriptions, true-ball positioning | arrow/hit/freeze golden trace absent; Archer IS tests not yet run |
| Keeper | omission-level (docstring) | triggers omniscient | not traced; no Keeper golden trace |
| Instrumentation neutrality | §7 | — | T1 canonical-hash gate not re-run with instruments |

## 3. Information-access contract (IA-001 applied)
Classes: **O** observable now (kinematics of players seen, visible morphology with perceptual error, visible posture/status, public rules state, communicated information) · **K** known (own state; roster; rules; physical constants; **population-level priors**, i.e. league-wide distributions, not any individual's attributes) · **I** inferred from O/K by the athlete's own error model, including within-match belief and estimates of others' tendencies from observed behaviour · **H** hidden: unseen true positions, true ball to an unsighted athlete, **every opponent rating, fatigue and recovery/timer value**, `next_action`, `freeze_until`, `unmarked_ms`, `zone_ms`, `intended`, `_path_cache`, RNG state.
Rules: cognition (G/E/S) reads O/K/I only; MC reads P2 only; PHY reads true state. **No direct read of a hidden opponent attribute** by cognition or MC. The Stage B reads of opponent `fatigue`, `next_action`, `maximum_speed`, `acceleration`, `braking`, `mass`, `reach` in carrier evaluation and of `braking` in `c3_desired` are therefore violations to be replaced by observation-based inference (e.g. estimated speed from observed motion) or removed. Physical resolution that uses both athletes' true ratings (contact, catch, hand fight, arrow hit) remains PHY and is not a violation. Mechanism [P, O8]: typed `AthleteView`; belief timing convention [O3].

## 4. Ownership model
G generation · E evaluation · S selection · MC Motor Control · PHY physical resolution. MC is a *to-be-documented* command surface (MC-0), not an existing component (Codex T2 §5.3).
| Behaviour | G | E | S | MC | PHY |
|---|---|---|---|---|---|
| Carrier choice | Cog (AthleteView) | Cog | Cog | throw/shot execution incl. error model | PHY |
| Off-ball movement | Cog | Cog | Cog | steering, cadence | PHY |
| Pursuit/marking | Cog | Cog | Cog | MC | PHY |
| Receiver | Cog (belief, intent) | Cog | Cog | intercept geometry on belief path | PHY |
| Jump | Cog (belief) | Cog | Cog (single owner) | take-off | PHY |
| Catch | none | none | automatic | hand placement | PHY |
| Keeper | Cog | Cog | Cog | MC (dive/step) | PHY |
| **Archer** | Cog: legal-looking targets from belief | Cog: hit probability and threat value from belief | Cog: choose target, fire or hold | MC: draw, aim solution, lane movement, release error | PHY: arrow flight, hit, freeze; rules engine resolves legality |
| Restarts | Rules for written placements; Cog for tactical spots | | | MC | PHY |

## 5. Codex T3 golden-trace evidence
**What T3 is [Codex, accepted].** Ten tick-level physical traces (sprint, brake/cut, tackle/contact, catch, ball flight, bounce, 30 s fatigue, sampled throw; plus two controlled feature studies, catch-v2 and prolate throw, that are *not* B0), each generated twice in fresh processes, byte-identical, B0 source unchanged. Decision modules are suppressed: explicit targets, no `Policy.targets`, no PRISM, no carrier/archer/receiver/C4c2 decisions. Retained: target acceptance and locomotion limits, C3 integration and contact, ball flight/bounce/catch, Pocket 4 release sampling, condition and capability refresh. Claude check: each of the ten trace files is byte-identical to its repeat copy (done); canonical hashes and regeneration not re-run by me.
**Use in B1.** T3 is the reference for *identical-input physical parity* (Gate B, §11). Same-environment gate is exact; Codex's cross-platform native tolerances (T3 §8) are proposals for a future native port and are not adopted for B1 (no native work authorized).
**Preservation vs correctness.** Everything T3 proves is that B0 physics is reproducible and can be held constant. It records e.g. a 30.48 m/s sprint maximum and a boundary dead-ball outcome as *preserved*, explicitly not adjudicated as canonical (T3 §9, items 8–9). B1 Gates A and B certify preservation only; canonical-correctness questions are separate lab/canon work that I will not fold into acceptance.
**What T3 does not cover (explicitly unavailable).** (a) Arrow release, flight, hit and freeze (no archery fixture) — needed for Archer PP tests; (b) jump take-off and airborne phase, and hand-contest/hand-fight outcomes (the HAND_FIGHT and CATCH_V2 jump paths are not exercised; catch-v2 is covered only for one catch); (c) Keeper save/dive; (d) receiver rerouting and any decision-dependent behaviour (excluded by design); (e) full-match parity (T1 only); (f) the T3 RNG-consumption order for catch and release is recorded as an obligation (T3 §9.7), not as an executed cross-check. Request: **T3A** supplemental golden fixtures (arrow→flight→hit/freeze; archer lane movement; jump take-off/flight; Keeper save) generated by Codex before the matching Gate B tests are claimed [O7].

## 6. Receiver routing and the `next_decision` bypass
**Mechanism [S].** `route_receiver` (`match.py:2508-2517`) computes the intended receiver's intercept from the **true** ball path, writes it to `targets[q.id]`, and sets `q.next_decision = s.now`. C3 adopts a new target only when `now >= p.next_decision` (`match.py:1300`) and then sets `next_decision = now + 1000·decision_speed·(1.3 − 0.4·awareness)` (~295 ms for the median athlete). Because the routine runs every tick of the flight and re-opens the gate each time, the receiver re-targets every tick (100 ms), not every rated interval. Sibling writes of `next_decision = s.now` occur at `match.py:378` and `:381` (Keeper flight-plan handling); not measured, covered by the same ruling.
**Measured** (`tools/audit_cadence.py`; logging around the original call; seeds listed):
| Run | Route calls | Flights | Calls with receiver's timer still pending | First call of a flight: pending (median remaining; p90) | Target moved >1 m vs held target |
|---|---|---|---|---|---|
| B0 seed 1 | 806 | 124 | 94.7% | 87/124 (61 ms; 191 ms) | 41% (p90 12.1 m) |
| B0 seed 2 | 576 | 85 | 95.5% | 60/85 (90 ms; 195 ms) | 45% (p90 8.1 m) |
| full seed 1 | 50 | 13 | 90.0% | 8/13 (53 ms; 153 ms) | 38% (p90 14.3 m) |
| full seed 2 | 552 | 128 | 90.2% | 83/128 (65 ms; 195 ms) | 37.5% (p90 18.5 m) |
Rated decision interval: median ~294 ms (p90 ~306 ms). (Call counts differ from my Stage B probe because that probe counted only calls with a target in the full stack.)
**Analysis.** *Legitimate execution scheduling* would be: given a decision the athlete has already made, delay motor onset by his reaction/motor latency. *Unauthorized decision override* would be: forcing a decision or changing its content or timing independently of the athlete's perception and ratings. The bypass does the second, in two ways. (1) **When:** it replaces the athlete's rating-driven decision cadence (decision_speed, awareness) with a fixed 100 ms update, so those ratings have no effect on how fast a receiver reacts to a pass, and at the first call the receiver starts moving at the release instant, 61–70% of the time before his own timer would allow it. (2) **What:** the target content is derived from H state (true ball, and knowledge that he is the target), so even a perfectly paced decision would be an omniscient one. Only the C3 gate itself (target acceptance with locomotion limits) is a physical-execution element, and T3 retains it. **Proposed ruling [P]:** classify the write as an unauthorized decision override and remove it from the routing path in B1; the receiver's reaction is governed by perception (his ball belief's reaction latency, as `CATCH_V2` readiness already does through PRISM Reaction latency) plus the normal decision cadence; if tracking a locked-on object should update faster than ordinary decisions, that is a *perception* parameter (PRISM already has an attention multiplier for a locked-on entity) rather than a scheduler write [O4]. Consequence: B0→B1 receiver and catch behaviour will change; recorded as an intentional Gate C change, not recalibrated.
**Split of the routine [P]** (unchanged from r2): perceptual part (ball belief; whether he knows he is the target [O2]); intent part (go/hold/abort); geometry part (MC: `intercept_xy` on the belief path with own limits). Acceptance: zero H reads in geometry; target = f(belief) exactly; no write to `next_decision` by cognition or routing.

## 7. Instrumentation neutrality (req 4)
**Requirements [P].** Tracing, decision IDs and sentinels must not change: random-stream consumption (every match stream, module RNGs, global `random`), event scheduling or the event log, wrapper installation order or identity of historical functions, or any B0/T1/T3 hash. Design rules: IDs and sentinel marks live in side tables keyed by object identity; never added as fields to Player/Ball/pending tuples; no RNG calls; no event emission; no state writes; wrappers outermost, pass-through, removable; profile hooks (`sys.setprofile`) preferred for observation.
**Measured** (`tools/audit_neutrality.py`; seed 1, B0 flags and full stack; plain vs instrumented in separate processes). Instrumented = decision-ID counter/sentinel wrappers on `step`, `carrier_decision`, `route_receiver`, `c4c2_targets`, `move_players`, `arrow_decisions`, `Policy.targets` (33,015 marks in B0; 2,013 in full) plus a `sys.setprofile` hook (38.7 M and 9.9 M calls observed).
| Check | B0 | Full stack |
|---|---|---|
| score identical | yes | yes |
| log hash identical (event log with times) | yes (8993883f…) | yes (b020f0a1…) |
| all 5 match RNG streams (`arrow, ball, contact, policy, roster`) end state identical | yes | yes |
| module RNG `S.arng` identical; global `random` consumed | identical; not consumed (either run) | identical; not consumed |
| match stats hash identical | yes | yes |
| historical wrapper chains identical before and after removal | yes | yes |
| each wrapper sat outside the unmodified historical function | yes (7 of 7) | yes (7 of 7) |
Also [M]: the shipped Archer shadow layer (`PRISM=1`) produced event-log hashes identical to the non-PRISM full stack on seeds 1, 2 and 3, i.e. it is behaviour-neutral. **Limits:** my digest is not the T1 canonical hash; running the T1 ten-case canonical-hash gate with instruments installed is specified (NI-4) but not yet done; one seed per mode; pass-through counters only (a real decision-ID carrier is untested).

## 8. Archer: full PRISM cognition in B1
**Measured / source-derived facts.**
- **Default (B0 and shadow).** Archer decides from true state [S]. In ruleset 1.0.1 (the literal default) the target is always the ball carrier, so there is no option generation or evaluation; in 1.0.2 'structure' policy target value uses authored weights (2.2 carrier, 1.1 base, +1.2 engaged, +0.8 near-support) [S]. B0's own `arrowlead` system re-solves the aim from the **true** target position and velocity [S].
- **Shadow (`PRISM=1`).** Perception layer runs and logs; no decision changes [M: log hashes identical to the non-PRISM full stack on 3 seeds]. Logged against the true state over 28 releases (3 short seeds): belief position error median 1.3–2.7 m (p90 2.7–3.5 m); distance between the aim point computed from belief and from true state median 13.7–28.2 m (p90 18.5–37.5 m). I have not investigated why aim divergence is so much larger than position error (likely velocity-estimate error multiplied by flight time); treat as unvalidated.
- **Drive (`PRISM_DRIVE=1`, default off).** `arrow_decisions` runs on belief positions and velocities; players the archer has no confident belief of are deactivated for the call (cannot be targets or obstacles); `arrowlead` runs inside the same swapped state so the aim is from belief; a 5 m authored range margin and a judgment gate (options considered, look-ahead, decision interval from ratings) apply; hold-fire threshold is 0 (always fires) [S]. Outcomes differ from shadow: releases logged 2/7/5 (seeds 1–3) vs 2/21/7 shadow, scores differ on seeds 2 and 3 [M]. My belief-error log reads 0.0 in this mode because it is sampled while state is swapped (instrument artefact, not evidence of perfect belief).
- **Still omniscient or prescribed even in drive mode [S].** Lane movement `update_archers` follows the **true** ball x (`match.py:813`); freeze/immunity/eligibility read true (recorded in code as public information); `s.engagements` true; `mass` and `height` of others read (115 and ~5,000 reads; origin of the `mass` reads not explained); range margin, structure weights and judgment constants are authored placeholders. Engine `shoot_arrow` decrements ammunition before checking lane, early release and target legality, so a misjudged shot costs an arrow (a natural consequence of imperfect information, to be preserved).
**Required B1 end state [P].** Archer follows §4: Cog generates targets from observed, plausibly legal opponents; evaluates hit probability and threat from belief (including flight time and the athlete's own aim error); selects target and fire/hold; chooses lateral lane position from his ball belief. MC draws, solves the ballistic aim on the belief lead, applies release error from `archery_accuracy`, and moves in the lane within physical limits. PHY resolves arrow flight, hits, freeze and legality with true state. Only ratings are knobs (awareness, decision_speed, archery_accuracy). Authored constants (range margin, structure weights, hold threshold) are either removed, or catalogued as PLACEHOLDER pending your calibration; none is silently retained as a tactic.
**Phasing allowed; acceptance requires all of it.** A-0 neutral instrumentation (done for shadow, §7) → A-1 aim solution on belief (remove true-target `arrowlead` path) → A-2 target selection and fire/hold on belief → A-3 lane positioning on ball belief → A-4 classify/remove authored constants; target-policy ruleset per [O6] → A-5 full Archer acceptance (AR-1…AR-6, Gate A/B/C evidence).
**Archer tests (also in §9):** AR-1 information isolation (poison true target kinematics during aim; poison true ball x during lane movement; hide-only perturbation of players the archer cannot see); AR-2 ownership (Cog owns target/fire/hold; MC owns aim execution; legacy `arrow_decisions`, `arrowlead` and `update_archers` not decision owners); AR-3 Motor Control fidelity (same decision → same draw time, aim solution given belief, release distribution; MC reads only P2 fields); AR-4 physical-outcome preservation (T3A arrow fixtures; identical release state → identical flight/hit/freeze); AR-5 legality (illegal attempts consume ammunition and are recorded; no cognition read of true legality); AR-6 B1 outcome envelope vs B0/shadow (accuracy, freezes, ammunition use) with pre-registered tolerances [O5].

## 9. Prescription catalogue and DO-3
Catalogue as r2 §7 (RULE / TACTIC / PLACEHOLDER / INFO), with these additions from Codex T2 and this audit: Archer target `target_value` weights (TACTIC/PLACEHOLDER), Archer range margin (PLACEHOLDER), `update_archers` lane-tracks-ball (INFO + prescription), OFFACT candidate set anchored on the legacy target (TACTIC), pose-maneuver threat on true nearest opponent (INFO). RULE items are retained as legality constraints, never as assignments.
**DO-3 (rewritten).** Every target or assignment consumed by Motor Control carries a provenance tag in a side table (neutrality rules of §7): `athlete` (generated and selected by the athlete from his beliefs/ratings), `rule` (a legality constraint such as an offside line or restart line), `team-planner` or `legacy-table` (slot rows, zones/lines, man-by-slot, escort shapes, receiver spots, formation tables, restart tactics). In the formation-free arm the test **fails if any assignment has provenance `team-planner` or `legacy-table`**, or if a `rule` tag is used to assign (rather than bound) a position. It **does not** fail on option vocabularies the athlete generates himself (including geometric families such as lanes or arcs) or on any resulting spatial organization. Emergent organization is measured and reported (occupancy, spacing, role persistence) with no pass/fail.

## 10. Dependency order (Archer included)
0. **Preservation:** hash B0, T1, T2, T3 and this audit; no code.
1. **Neutral harness (no behaviour change):** CFG-1…4, NI-1…4, ID-1, DO-1/2 and IS-1/2 in log-only mode including Archer (AR-1 log-only), Gate A and Gate B runners; red-baseline ledger against B0. In parallel request **T3A** fixtures [O7].
2. **MC-0:** document the actual command surface for carrier release, receiver, jump, Keeper, **Archer (draw, aim, release, lane movement)** — documentation only.
3. **Rules audit and RL gates:** kicking at the engine boundary; Archer legality and target-policy ruleset [O6]; RULE vs TACTIC for restarts.
4. **Cadence/receiver (§6)** after [O2–O4]: remove the bypass, split routing.
5. **Jump single owner** after §6 preconditions of r2 (extended poison coverage, larger sample, jump golden trace).
6. **Information core:** `AthleteView`; carrier decision; pose threat; reflex avoidance (no opponent `braking`); belief timing [O3].
7. **Archer A-1 → A-4** (depends on AthleteView and MC-0; A-1 can start once MC-0 and T3A exist).
8. **Keeper triggers on belief.**
9. **Formation-free arm** (separate experimental mode; formation arm bit-identical to B1).
10. **B1 acceptance:** Gates A, B, C plus the coverage checklist: carrier, receiver, jump, Keeper, **Archer (all of A-1…A-5)**. Not authorized in any phase: native rewrite, recalibration, rating development. Deferred beyond B1 (unchanged from r2, not new): Keeper-to-Keeper communication, block option, defensive zone organisation.
Gate between steps: your approval; Gate A green; Gate B unchanged for untouched physics.

## 11. Acceptance gates and revised validation matrix
**Gate A — unchanged B0 replay (historical preservation).** Build with no B1 switches, flags cleared, instrumentation absent *and* present. The ten accepted T1 cases reproduce exactly: scores, event counts, canonical event-log hashes, result hashes. Required after every change; any difference blocks.
**Gate B — identical-input physical parity.** For identical physical state, commands, environment and RNG streams, B1 physics reproduces the T3 traces **exactly** in the reference environment (and T3A traces once supplied). Verifies that no B1 change reaches PHY. Covers only what the golden fixtures cover (§5); anything outside is marked uncovered, not assumed.
**Gate C — intentionally changed B1 cognitive behaviour.** No bit-identity expectation. Required: every intended change is in a change register (what, why, expected direction); ownership, information, MC-fidelity and Archer tests pass (below); B1-vs-B0 outcome envelope reported against pre-registered metrics and tolerances [O5]; no recalibration to hit a target; correctness questions escalated separately (P5).
| Test | Family | Checks | Expected at B0 | Pass at B1 | Gate |
|---|---|---|---|---|---|
| CFG-1…4 | config | exact patch match counts/sites; frozen config object + hash; invalid flag combinations fail loudly; install-chain snapshot, no double-install | red | green | A prerequisite |
| NI-1 | neutrality | decision-ID/tracing/sentinels: score, log hash, event times unchanged | measured green (§7) | green | A |
| NI-2 | neutrality | every RNG stream (match, module, global) end-state identical with/without instruments | measured green | green | A |
| NI-3 | neutrality | wrapper chains identical after removal; instruments only outermost | measured green | green | A |
| NI-4 | neutrality | T1 ten-case canonical-hash gate with instruments installed | not yet run | green | A |
| ID-1 | trace | decision ID carried choice → pending action → release/contact → outcome | n/a | all executed actions traceable | C |
| IS-1/2 | info | hide-only perturbation of H state; per-field poison for every §3 H field | red | zero change | C |
| IS-3 | info | receiver geometry: zero H reads, target = f(belief), no `next_decision` write by cognition/routing | red | exact | C |
| IS-4 | info | pose threat, `c3_desired` reflex, block option read only AthleteView fields; no hidden opponent attributes | red | holds | C |
| IS-5 | info | belief timing convention fixed [O3] | undefined | enforced | C |
| IS-6 | info | multi-match and parallel isolation | partly red | clean | C |
| DO-1 | ownership | unique marker per layer; final precedence at policy → C4c2 → routing → cadence → `p.target` → C3 | records owner | owner = §4 | C |
| DO-2 | ownership | exactly one jump planner | red (two) | one | C |
| DO-3 | ownership | provenance rule of §9 (no `team-planner`/`legacy-table` assignment in formation-free arm; emergent organization reported only) | n/a | zero prescriptive assignments | C |
| MF-1 | MC | MC reads only P2 fields; same cognitive output → same command | undefined until MC-0 | holds | C |
| MF-2/3 | MC | throw/shot and jump command → release/take-off match error model and window | baseline | within [O5] | C |
| AR-1…6 | Archer | §8 (isolation, ownership, MC fidelity, physical preservation, legality, envelope) | red (AR-1,2) | green | C (AR-4 also B) |
| PP-1 | physical | T3/T3A golden traces exact | green (T3); T3A pending | green | B |
| PP-2 | physical | T1 ten-case B0 replay | green | green | A |
| PP-3 | physical | B1 outcome envelope vs B0 (scoring, fouls, pace, catch rate, arrows/freezes) | n/a | within [O5] or documented change | C |
| RL-1/2 | rules | engine-boundary no-kick gate with positive control; rules-flag matrix | red | green | C |

## 12. Decision register
**Decided / previously approved (not reopened):** IA-001; C-7 Archer full PRISM cognition in B1 (phasing allowed, final acceptance requires full coverage); separate experimental formation-free mode preserving the formation comparison; B0 and B1 as separate baselines, B0 = commit 2abe497 with RULES_V03=0 and historical kicking; kicking must be eliminated in B1 without auto-enabling RULES_V03=1; Motor Control documentation/interface design only; calibration freeze; no rating or attribute progression; no native rewrite; prohibited-prescription / allowed-emergence distinction (P4). **Accepted in direction (r1/r2 reviews):** five-layer ownership; information-access contract with observable/known/inferred/hidden; receiver perception/geometry split; qualified determinism; MC access limits; configuration controls; test-first plan; single-owner jump direction (still subject to its preconditions).
**Genuinely open (need your approval):**
- **O1 Visible morphology.** Which opponent properties count as visible body (e.g. height, build, reach) observable with perceptual error, versus hidden (all skill and athletic ratings, fatigue, timers)? Default proposal: body dimensions observable with error; everything else hidden; population-level priors permitted.
- **O2 Receiver target knowledge.** How the intended receiver learns he is the target: pass call/pre-signal, inference from the ball's course, or neither.
- **O3 Belief timing.** Decisions use the belief from the start of the 100 ms interval, or after the step's perception update.
- **O4 In-flight tracking cadence.** Approve the §6 ruling (bypass is a decision override; removed in B1) and choose how a locked-on receiver/Keeper updates: ordinary decision cadence, or a perception attention parameter (PRISM-style lock-on latency multiplier).
- **O5 Gate C tolerances.** Pre-registered metrics and tolerances for MF/PP envelopes (Gates A and B are exact and need none).
- **O6 Archer rules.** Which target policy governs Archers in B1 (carrier-only 1.0.1 or structure policy 1.0.2), the status of the 5 m range margin and other authored Archer constants, and whether freeze/immunity/eligibility are treated as public observables.
- **O7 Supplemental golden evidence.** Authorize Codex to produce T3A fixtures (arrow→flight→hit/freeze, archer lane movement, jump take-off/flight, Keeper save) and to cross-replicate my canary, jump-poison, cadence and neutrality probes; I spot-check Codex's patch-map counts.
- **O8 Isolation mechanism.** Approve `AthleteView` (typed per-decision view) as the isolation mechanism.
- **O9 Rules audit and dead balls.** Schedule the rules audit (kicking at the engine boundary, RULE vs TACTIC placements) and decide whether restart formations get a set-piece exception in formation-free mode.
- **O10 Carrier archetype biases.** In the formation-free arm, are position/archetype carrier biases kept as preferences or removed.
Also for approval: the §10 dependency order and §11 gates.

## Reproduce
`python3 tools/audit_archer.py <seed> out.json b0|shadow|drive`; `tools/audit_cadence.py <seed> out.json full|b0`; `tools/audit_neutrality.py <seed> out.json b0|full plain|instr`; earlier: `audit_update_jumps.py`, `audit_fields.py`, `audit_probes.py`. Data under `audit/`: `archer_*`, `cadence_*`, `neut_*`, `fields_drive_s1.json`, `ujump_*`.
## Limits
Short games and 1–3 seeds per probe; Archer samples are small (28 releases); drive-mode belief error not measurable with the current logger; Keeper and block-option internals not traced; T3 canonical hashes and regeneration not replicated by me.
