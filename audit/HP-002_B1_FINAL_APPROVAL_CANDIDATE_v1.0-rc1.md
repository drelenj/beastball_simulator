# HP-002 — B1 Final Approval Candidate · Specification v1.0-rc1
Claude, 2026-11-08. Branch `claude/hp002-audit`. **Self-contained: implementation must rely only on the documents listed in `HP-002_SPEC_MANIFEST.json`, not on earlier drafts (r1, r2, r3 and the earlier "final candidate" are SUPERSEDED, historical only).** Candidate only. **No B1 implementation, rating recalibration, Keeper optimization or native rewrite is authorized.** B0-P4-DEFAULT (commit 2abe497) and accepted T1–T3 evidence are untouched.

## 0. Read this first
**Blocking input not received: Codex T5 and T6 evidence.** I understand T5 and T6 are complete and accepted, and that they cover causal telemetry, typed interfaces, command supersession and physical outcome contracts. Neither report nor packet is in my attachments or in the repository branches I can see (only `claude/*` and `main`). I have not read them, so I have **not** incorporated their content and I will not describe it. Where this spec touches those four areas (§9) it states the requirement, names the slot, and **defers to T5/T6 for schema and contract detail**. This candidate cannot be called reconciled with T5/T6 until I have read them. Please send both reports and packets.

### Change log (against the previous final candidate)
1. **Possession attribution vs team control separated (§4).** Archer targeting uses attribution (persists through loose and airborne states); zone-return violations use current control.
2. **Five-second Keeper Zone violation restart: RESOLVED** (DreLen, 2026-11-08 11:39): center-line opening contact scrimmage, possession to the opposing team; identical to the zone-return restart. My earlier "assumed same" wording is withdrawn.
3. **Keeper protection matrix (§5)** with every cell marked approved, B0 fact, or unspecified. Nothing inferred. Four rule questions remain open.
4. **Carrier boundary-crossing (ZR-C) and first-touch (ZR-T) violations defined as two distinct violations (§6).**
5. **Dependency order reordered (§11):** the enforceable `AthleteView` boundary and typed interfaces now precede every behavioural replacement.
6. **T5/T6:** not incorporated (above); slots and deference rules in §9.
7. **Versioned manifest** (`HP-002_SPEC_MANIFEST.json`, verified by `tools/build_manifest.py verify`).
8. Self-contained: normative content from r3 folded in; r1–r3 superseded.

## 1. Authority and decision register
**Decided by DreLen, not reopened:** IA-001; C-7 (full PRISM Archer cognition in B1; phasing allowed, acceptance requires full coverage); five-layer ownership; restricted Motor Control boundary; three-stage catching; removal of the decision-cadence bypass; single-owner jump architecture (subject to validation); ban on externally prescribed tactical assignments in formation-free mode; formation-based and formation-free experimental arms; Gates A/B/C; T3 evidence and its coverage limits; neutral instrumentation; B0/B1 baselines; kicking eliminated in B1 without auto-enabling `RULES_V03=1`; calibration freeze; no rating or attribute progression; no native rewrite.
| ID | Resolution (his wording) | Date |
|---|---|---|
| O1 | Body dimensions observable with error; capabilities inferred | 11-07 |
| O2 | Explicit teammate communication and observable inference | 11-07 |
| O3 | Observe → update beliefs → decide, with modeled sensory latency | 11-07 |
| O4 | Permit attention-dependent tracking, not unrestricted decision-timer bypass | 11-07 |
| O5 | Defer numbers until metrics and distributions are established | 11-07 |
| O6 | Archer can target the ball-carrier and off-ball offensive players; clarified: all of the opposing team's field players while that team is on offense and in possession; the team that last had possession before the ball became loose or airborne is still the possessing team | 11-07 |
| O7 | T3A approved as separate read-only evidence work | 11-07 |
| O8 | Typed per-athlete isolation boundary (AthleteView) | 11-07 |
| O9 | Rule-required placement only; optional tactics must be athlete-selected | 11-07 |
| O10 | Remove externally assigned position biases in formation-free mode | 11-07 |
| R1 | Freeze, immunity and eligibility status are public to every athlete; indicators on uniforms | 11-08 |
| ARC-1 | Archer's legal range is any spot outside the Keeper Zones; Keepers are not field players | 11-07 |
| KP-A | Contact protection is exclusive to the Keeper | 11-07 |
| ZR-1 | Ball-in-own-Keeper-Zone limit: 5 consecutive seconds, regardless of who holds the ball | 11-07 |
| ZR-2 | Zone-return rule text (NBA language) with definitions: "inside" = where first touched or lands; "in control" excludes a shot or a loose ball such as a fumble; a carrier crossing in is a violation at the moment he crosses | 11-08 |
| **RST-1** | **Restart for the zone-return violation and for the 5-second violation: turnover; ball spotted at the center line for an opening contact scrimmage; possession to the opposing team. RESOLVED. Not reopened.** | 11-08 11:39 |

## 2. Principles
- **P1** Physical resolution is a deterministic function of physical state, commands, environment and modelled randomness from named seeded streams.
- **P2** Cognition (generation, evaluation, selection) reads observable, known and inferred information only. Motor Control (MC) reads the athlete's own body, physical constraints and the command given. Neither reads a hidden opponent attribute. Physical resolution (PHY) uses true state.
- **P3** Belief updates within a match are allowed; no rating or attribute development is authorized.
- **P4** Matching B0 or T3 proves historical physical preservation, not canonical correctness.
- **P5** Formation-free: no externally prescribed tactical assignments; athlete-generated options and emergent organization are allowed.

## 3. Ownership, information, Motor Control, catching
**Layers:** G generation · E evaluation · S selection · MC Motor Control · PHY physical resolution.
| Behaviour | G/E/S | MC | PHY |
|---|---|---|---|
| Carrier choice | Cognition (AthleteView) | throw/shot execution incl. error model | PHY |
| Off-ball, pursuit, marking | Cognition | steering, cadence | PHY |
| Receiver | Cognition: belief, intent (including whether to go) | intercept geometry on the believed path | PHY |
| Jump | Cognition, single owner (belief-based `update_jumps`, subject to validation) | take-off | PHY |
| Catch | see below | hand placement, reach | grasp |
| Keeper | Cognition | dive/step | PHY |
| Archer | Cognition: targets, hit probability, fire/hold, arc choice, lane position, all from belief | draw, ballistic solution to the chosen target and arc, release error, lane movement | arrow flight, hit, freeze; rules engine adjudicates legality with true state |
| Restarts | Rules for written placements; athlete-selected otherwise | MC | PHY |
**Information classes.** *Observable:* seen kinematics, visible morphology with perceptual error, status indicators on uniforms (freeze, immunity, eligibility), public rules state (see §4), communication. *Known:* own state, rules, constants, population-level priors. *Inferred:* from observation (including opponents' capabilities and tendencies, within the match). *Hidden:* unseen true positions, opponent ratings, fatigue, timers, `next_action`, `intended`, caches, RNG. Cognition and MC read no hidden opponent attribute. PHY may use both athletes' true ratings.
**Motor Control boundary.** MC computes execution geometry for a destination or target it is given, from the intention and the athlete's beliefs (path and braking, intercept timing along a believed trajectory, ballistic aim, steering, take-off timing, release error). MC may not choose or improve a tactical destination, select among targets, re-pick a spot, pick an arc by weighing opponents or obstacles, or substitute a destination; if infeasible it reports infeasibility to cognition. *MC output = f(command, belief of the object to be met, own body and limits).* Tests MF-1 (field reads), MF-4 (endpoint fidelity), MF-5 (perturbation of other players leaves MC output unchanged).
**Catching:** (1) *Cognitive preparation:* tracking from belief, whether and where to move, readiness timing from perceptual latency, the decision to jump. (2) *Motor execution:* hand placement, reach, orientation, take-off within limits. (3) *Automatic grasp and contact:* hand meets ball, capacity versus energy, secure or fumble, hand contests; no choice involved. Cognition changes when and where hands are ready, never the outcome. Tests CT-1, CT-2, CT-3.
**Receiver:** perceptual part (ball belief; knowledge of being the target through explicit teammate communication and observable inference, O2), intent part, geometry part (MC). The `next_decision = now` write in `route_receiver` (`match.py:2517`) is classified an unauthorized decision override and removed in B1; locked-on tracking uses a perception attention parameter (O4). Measured basis (B0 and full stack, 4 runs): receiver's own decision timer still pending in 90–95% of routing calls; 61–70% of first calls; targets moved more than 1 m from the held target in 37–45% of calls.
**Jump:** single owner; legacy `plan_jumps` disabled by configuration in B1 (code retained for B0), install-time assertion that exactly one planner is registered. Measured: both planners fire in the full stack today. `update_jumps` poison probe (true ball kinematics poisoned during the call) gave identical games on seeds 1–3; control with the belief path off diverged. Preconditions before activation: poison coverage of all Ball fields and `carrier`/`last_releaser`; larger sample; jump golden fixtures (T3A); B0→B1 catch-rate change reported, not recalibrated.
**Archer (C-7), phased A-1…A-5:** A-1 aim from belief (removing the true-target `arrowlead` path); A-2 target selection and fire/hold from belief; A-3 lane positioning from the ball belief (today `update_archers` tracks the true ball x, `match.py:813`); A-4 classify or remove authored constants (the 5 m range margin is retired; ruleset target filters that conflict with ARC-1 go to the rules audit); A-5 full acceptance. Measured: the shipped shadow layer is behaviour-neutral (identical logs on seeds 1–3); `PRISM_DRIVE` mode changes outcomes (releases 2/7/5 vs 2/21/7).

## 4. Possession attribution vs team control (public rules state)
Two different public quantities, never interchanged:
- **Possession attribution (PA):** the team that last gained control of the ball. It persists through loose and airborne states (including a shot in flight) until the other team gains control. *Used for:* the Archer target set (O6), and wherever a rule refers to "the possessing team".
- **Team control (TC):** a team is in control while one of its players holds the ball (carry), and while a deliberate pass of that team is in flight to a teammate. TC ends on: shot release, the ball becoming loose (fumble, drop), a defender's touch, or the opposing team gaining control. *Used for:* the zone-return violation (ZR-2), "while his team was in control".
| Ball state | PA | TC | Archer target set (O6) | Zone-return rule applies |
|---|---|---|---|---|
| Carried | holder's team | holder's team | field players of the PA team | yes (ZR-C) |
| Deliberate pass in flight | passer's team | passer's team | field players of the PA team | yes (ZR-T) |
| Shot in flight | shooter's team | none | field players of the PA team | no |
| Loose after fumble/drop | last controlling team | none | field players of the PA team | no |
| After defender deflection | last controlling team (unchanged until the other team gains control) | none | field players of the PA team | no (TC ended) |
**Archer target set (O6):** an Archer of team X may target the field players of the opposing team Y while Y is on offense and in possession, i.e. while Y is the PA team. Keepers are not field players and are never targeted (ARC-1). The rules engine still adjudicates legality using true state; status indicators are public (R1). *Not inferred:* who holds PA after a ball goes out of play, at a restart before first control, or when a deflected ball is first gained by neither team (U-4).
The PA/TC pair, the possession-origin flag, who touched the ball last, and each team's own-zone ball clock are public state exposed in `AthleteView`.

## 5. Keeper protection matrix (nothing inferred)
Cell legend: **A** approved (DreLen, date) · **B0** observed in B0 source, not canon · **U** unspecified, pending (§12). "Offense/defense" for the Keeper's team is itself undefined during loose and airborne states (U-2).
| Aspect | Own zone, offense | Own zone, defense | Outside own zone, offense | Outside own zone, defense |
|---|---|---|---|---|
| Archer targeting | **A**: never a target (Keepers are not field players; target set is field players) | **A** same | **A** same | **A** same |
| Incidental arrow impact or freeze | U (B0: a Keeper in its own zone is not freeze-eligible, `engine.py:1008-1010`; under ruleset 1.0.1 an arrow freezes only the ball carrier, 1.0.2 widens it) | U (same B0 fact) | U | U (B0: eligible; immunity not enumerated by DreLen) |
| Tackle | **A**: cannot be contacted on offense | U ("immunities" held inside the zone; list not enumerated) | U (text "can't be contacted on offense" is unqualified by location; "pass freely out of the keeper zone" does not say whether it persists after leaving) | U ("loses immunities once they leave"; which immunities, and whether tackle is one, not stated) |
| Other contact (blocking, screening, hand contest, incidental) | **A** (same statement, "can't be contacted"); whether the Keeper may initiate contact is U | U | U | U |
| Stay duration | **A**: indefinite inside the zone as an individual (but the ball is subject to ZR-1) | **A** same | n/a | n/a |
| Scoring | **A**: not eligible to score outside of own goals | n/a | **A** same | n/a |
| Zone boundary | B0: circle of radius `keeper_zone_radius` (default 20, `engine.py:23`) around the goal center, point position (`engine.py:44-45`); canon boundary treatment for protection U (see detail below) | | | |
| Exclusivity | **A**: no other player receives this protection (KP-A) | | | |
**Zone boundary detail (U-3):** B0 `zone(x,y,R)` takes a point position (`engine.py:44-45`). A separate, already-decided canon ruling (C4c2, DreLen 9 October, `engine.py:51-55`) governs *release territory* only: a line belongs to the farther scoring territory, so the Keeper Zone arc counts as an outside release. I do **not** extend C4c2 to Keeper protection, zone-return or the 5-second clock. Canon is silent on reference point (center vs any body part vs ball), edge inclusivity, and whether lines or the goal aperture belong to the zone for those purposes. Archer legality (ARC-1), ZR-1 and ZR-2 depend on it.

## 6. Zone rules contract (RULE class: adjudicated by the rules engine, never by cognition or MC)
**ZR-1 Five-second limit:** the ball may not remain in the possessing team's own Keeper Zone for more than 5 consecutive seconds, regardless of who holds it. Consequence per RST-1. *Pending:* attribution basis during loose/airborne states (U-2). B0 only limits the Keeper carrying the ball (`keeper_hold_ms >= 5000`, `engine.py:1714`), resets it on any non-forced release (`engine.py:355`); its legacy controller distributes after 0.4 s (`match.py:949`), so parking never arises in B0 play and becomes reachable in B1.
**ZR-2 rule text:** *"A player shall not be the first to touch a ball which he or a teammate caused to go from outside the keeper zone to inside the keeper zone while his team was in control of the ball."* It subsumes "possession started outside" and "started inside, left, returned".
Two distinct violations:
| | **ZR-C carrier boundary crossing** | **ZR-T first-touch (airborne or loose ball)** |
|---|---|---|
| Trigger | a carrier of team T, with T in control, crosses with the ball from outside to inside T's own Keeper Zone | a deliberate pass by T (T in control at release) enters T's own zone and a T player is first to touch it after entry |
| Moment | the instant of crossing (approved) | the first T touch (a Keeper's touch counts) |
| "Inside" | position of the ball-carrying crossing (reference point U-3) | where the ball is first touched or lands (approved) |
| Cleared by | nothing; occurs at crossing | a defender touching first; a ball T did not cause to enter (e.g., defender deflection) |
| Does not apply | — | shots, loose balls (fumble, drop), balls after TC has ended |
| Consequence | RST-1 | RST-1 |
Automatic grasp (§3) means a T player cannot choose not to catch a ball that reaches his hands; avoidance lives in cognitive preparation (positioning, not going for the ball).
**Restart (RST-1, resolved):** turnover; ball spotted at the center line; opening contact scrimmage; possession to the opposing team. Implementation vehicle (`RULES_V03` contact scrimmage versus the older `restarts_v1` path) is a rules-audit task; B0 does not enable `RULES_V03`.
**Archer range (ARC-1):** B0 hard-codes a 10–70 m window (`engine.py:1034, 1056`; `match.py:988, 1008`) and a 9 m near-carrier filter in the structure policy (`match.py:988`); both conflict with ARC-1 and are rules-baseline items. Physical reach limits remain; with no ballistic solution, MC reports infeasibility.

## 7. Formation-based and formation-free arms
Same architecture (AthleteView, five-layer ownership, MC, instrumentation) and same physical model; they differ only in which assignment providers are enabled. They need not be bit-identical to each other. The formation-based arm is B1 itself and must be reproducible. DO-3 (provenance): every target consumed by MC carries a provenance tag in a side table (`athlete`, `rule`, `team-planner`, `legacy-table`); in the formation-free arm the test fails if any assignment is `team-planner` or `legacy-table` or if a `rule` tag assigns rather than bounds a position; athlete-generated options and emergent organization pass and are only reported. Restarts in that arm: rule-required placement only (O9). Position/archetype carrier biases removed (O10).

## 8. Instrumentation neutrality (measured)
Decision-ID/sentinel wrappers on seven decision entry points plus a `sys.setprofile` counter: identical score, event log, all five match RNG streams, module RNG, stats, and wrapper chains with and without instruments (seed 1, B0 and full stack). **NI-4: the ten accepted T1 cases replayed with instruments installed; all ten match the accepted hashes** (canonical event log, result, score, event counts, event types). Limits: compared with my environment's accepted runs (Python 3.13.16 then, 3.13.18 now); pass-through counters only, so any real ID carrier or T5 telemetry implementation must re-run NI-1…4.

## 9. Codex evidence and typed-interface slots
- **T1–T3 (read):** T1 B0 replay hashes; T2 patch-chain, wrapper-order and decision-ownership findings (adopted as CFG tests: patch cardinality, frozen configuration, install-chain snapshot, idempotence, silent flag dependencies); T3 ten golden physical traces (Gate B reference). T3 does not cover arrows, jump, hand contest, Keeper saves or receiver rerouting; **T3A** (approved, separate, read-only) supplies them.
- **T5/T6 (not received; see §0).** Slots reserved, governing detail deferred to T5/T6: **causal telemetry** (replaces my ID-1 decision-ID trace once read; must satisfy §8 neutrality); **typed interfaces** (govern the AthleteView schema and the MC command surface, MC-0); **command supersession** (the rule that a new command replaces a pending one; the ownership tests DO-1 assert precedence at the command level, not at policy output); **physical outcome contracts** (govern Gate B and the PP and MF tests). If T5/T6 conflict with anything here, the conflict is reported and not silently resolved.

## 10. Validation matrix
Families: CFG configuration · NI neutrality · ID/telemetry · IS information isolation · DO ownership · MF motor fidelity · CT catching · PP physical · AR Archer · RL rules · KP Keeper protection · ARM arms · IQ information-quality sensitivity.
Gates: **A** unchanged B0 replay (the ten T1 cases, exact, instruments absent and present). **B** identical-input physical parity against T3 (and T3A) traces, exact in the reference environment, covering only what the fixtures cover. **C** intentionally changed B1 cognition: change register; IS/DO/MF/CT/AR/RL/KP tests pass; B1-versus-B0 envelope reported (tolerances deferred, O5); IQ-1…4; no recalibration.
| Test | Checks | Gate |
|---|---|---|
| CFG-1…4 | patch match counts and sites; frozen configuration object and hash; invalid flag combinations fail loudly; install-chain snapshot and idempotence | A prerequisite |
| NI-1…4 | score/log, all RNG streams, wrapper chains, T1 canonical replay with instruments (NI-4 done for current instruments) | A |
| ID-1 (or T5 telemetry) | choice → pending command → release/contact → outcome traceable | C |
| IS-1/2 | hide-only perturbation; per-field poison for every hidden field | C |
| IS-3 | receiver geometry has no hidden reads, no `next_decision` write | C |
| IS-4 | pose threat, reflex avoidance, block option use AthleteView; no hidden opponent attribute | C |
| IS-5 | belief timing convention (O3) | C |
| IS-6 | multi-match and parallel isolation | C |
| IS-7 | boundary enforcement: any hidden-field access in test mode raises; identity adapter leaves B0 hashes unchanged | A, C |
| DO-1/2/3 | ownership sentinels and command-level precedence; one jump planner; provenance rule | C |
| MF-1/4/5, CT-1/2/3 | §3 | C (CT-3 also B) |
| AR-1…6 | Archer: isolation (true target kinematics poisoned during aim; true ball x during lane movement; hide-only perturbation); ownership; MC fidelity; physical preservation (T3A); legality per ARC-1; envelope vs B0/shadow | C (AR-4 also B) |
| RL-1/2 | engine-boundary no-kick gate with positive control; rules-flag matrix | C |
| RL-3 | ZR-C scenarios: carry crossing in; Keeper carrying out and back; reference-point cases (U-3 pending) | C |
| RL-4 | ZR-T scenarios: pass entering zone first touched by offense, by Keeper, by defender, untouched landing; deflection; shot and fumble exemptions; bounce-pass cases pending (U-4) | C |
| RL-5 | ZR-1: 5 consecutive seconds, resets, any holder, loose/airborne basis pending (U-2) | C |
| RL-6 | RST-1: both violations produce a turnover, center-line opening contact scrimmage, possession to the opposing team | C |
| RL-7 | PA versus TC: Archer target set follows PA through shot, fumble and deflection states while zone-return follows TC | C |
| KP-1 | Archer never targets a Keeper | C |
| KP-2…n | each **approved** cell of §5 (offense inside zone: no contact; scoring eligibility; exclusivity); cells marked U have no test until decided | C |
| ARM-1…4 | arms differ only in provider entries; Gate B for both; DO-3; emergence reported | C |
| IQ-1…4 | limit identities; isolation at every quality level; determinism at degraded limits; dose-response curves reported without effect-size thresholds | C |
| PP-1…3 | T3/T3A exact; T1 replay; B1-vs-B0 envelope (deferred tolerances) | B / A / C |

## 11. Dependency order (reordered)
0. **Preservation:** freeze B0, T1–T6, this audit; publish the manifest.
1. **Neutral harness:** CFG, NI, telemetry (T5), Gate A/B runners, red-baseline ledger against B0; T3A in parallel.
2. **Typed interfaces and the enforceable `AthleteView` boundary:** schema (T5/T6 types), MC-0 command surface, public rules-state fields declared (PA, TC, origin flag, last toucher, zone clock, status indicators); enforcement in test mode (hidden access raises); identity adapter must leave all B0 hashes unchanged (IS-7). **No behavioural replacement begins until IS-1/2/7 are green on this boundary.**
3. **Rules audit and rules contract:** Keeper protection, zone boundary, ZR-1/2, RST-1 vehicle, kicking, ARC-1 conflicts; fills the rules-state values the boundary exposes.
4. **Behavioural replacements, each gated by its IS/DO tests on the boundary:** receiver split and cadence removal; single-owner jump (after preconditions); carrier decision; Archer A-1…A-4; Keeper triggers.
5. **Formation-free arm** (separate experimental mode).
6. **B1 acceptance:** Gates A, B, C with full coverage of carrier, receiver, jump, Keeper and Archer (A-1…A-5).
Deferred beyond B1 (unchanged): Keeper-to-Keeper communication, block option, defensive zone organisation. Not authorized at any step: native rewrite, recalibration, rating development, Keeper optimization.

## 12. Genuinely unresolved decisions (need your approval; nothing here is assumed)
- **U-1 Keeper contact scope.** (a) Does "on offense they can't be contacted" continue after the Keeper has left his zone? (b) Which immunities does a Keeper hold inside his zone and lose outside, and is tackle or other contact protection among them on defense? (c) How is an arrow that hits a Keeper incidentally treated?
- **U-2 Attribution basis.** During loose and airborne states, do the Keeper's offense/defense phase (§5) and the 5-second clock (ZR-1) follow possession attribution or current team control?
- **U-3 Zone boundary.** Reference point (body center, any part of the body, or ball) for ZR-C and for Keeper rules; edge inclusivity; whether lines and goal aperture belong to the zone.
- **U-4 Control edge cases.** A deliberate pass that bounces or touches the ground before entering; a ball that enters the zone untouched and goes out of play; who holds possession attribution after out-of-play, at a restart before first control, or when neither team gains the ball after a deflection.
- **A-1 Approval:** the reordered dependency order (§11), which places the rules audit at step 3, and the measurement-first Gate C.
Required input, not a decision: the Codex T5 and T6 reports and packets.
