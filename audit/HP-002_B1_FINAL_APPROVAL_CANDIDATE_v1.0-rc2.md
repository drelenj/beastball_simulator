# HP-002 — B1 Final Approval Candidate · Specification v1.0-rc2
Claude, 2026-11-08. Branch `claude/hp002-audit`. **Self-contained: implementation relies only on the documents in `audit/HP-002_SPEC_MANIFEST.json`.** rc1, the earlier "final candidate" and r1–r3 are SUPERSEDED (historical, non-governing). **Candidate only. No B1 implementation, native rewrite, Keeper optimization, rating recalibration or unauthorized rules change is authorized.** B0-P4-DEFAULT (commit 2abe497) and all accepted T1–T6 evidence are untouched.

## 0. Status, review record, change log
**Review of rc1:** conditionally accepted (IA-001, C-7, five-layer ownership, restricted Motor Control, three-stage catching, AthleteView boundary, formation-free provenance, Gates A/B/C, and RST-1 for both approved violations accepted at specification level). rc2 answers the remaining conditions.

**T5 and T6 are now reviewed, not just received.** What I actually did:
- Read in full: the T5 report, telemetry schema, runner source (`run_match.py`, `common.py`) and sample outputs; all eleven T6 documents.
- Integrity: every entry in the T6 `MANIFEST.sha256` verifies; the T5 zip hash equals the value T6 records in `SOURCE_PROVENANCE.md`; T5's preserved T2 and T3 report hashes equal the copies I hold.
- Re-executed here: T5 unit suite 15/15 pass; T5 short seed-1 control and fully instrumented runs under CPython 3.13.18 (Codex reference: 3.12.14): all 10 equivalence checks pass, and the event, execution-schedule, RNG-transition and final-RNG hashes equal Codex's values. Evidence: `audit/t5_replication/`.
- **Not reviewed:** the T4 report/packet (not received; the Keeper reverse-flight facts below come from T5's own diagnostic and T6's description). Not re-run: T5 regulation run, batch/resume demos, schema validation. T6 reconciled against my r3, so its list of "open" HP-002 decisions (O1–O10) predates your 2026-11-07 resolutions; §9 treats that list as stale, not as a conflict.

**Change log (rc1 → rc2)**
1. T5/T6 reconciled; focused agreement/conflict matrix in §9 (six areas plus sequencing, 47 rows: 32 resolved, 15 by an already accepted decision and 17 by adoption or precedence with Codex acknowledgment requested; 4 need your decision; 4 need Codex or joint design work; 7 are informational).
2. U-1…U-4 kept **UNRESOLVED**. Your stated approach for each is recorded as direction only. Required inputs are listed as numbered cells and scenarios (§5, §6a, §12), including bounce-pass and control-at-release cases (U-4).
3. §11 refined: rules-state contract and typed AthleteView schema are one contract, frozen together (Contract v1), before any behavioural replacement; rules implementation is the first behavioural step.
4. NI: existing NI-4 is a result about the pass-through counters only. §8 lists exactly which changes trigger NI re-runs, and adds a coverage gap neither T5 nor my NI closes (per-step PRISM per-athlete RNG streams).
5. T6 command lifecycle and no-silent-replacement rule adopted (§3a); T6 validation IDs mapped to rc2 tests (§10).
6. Manifest regenerated with T5/T6 hashes, the conflict register, and unresolved-decision list. Codex's reports are now copied read-only under `baseline/codex_evidence/`.
7. Two new unresolved items surfaced by this review: SELF-1 (exactness of an athlete's knowledge of his own capabilities) and R-RS (ruleset 1.0.1 vs 1.0.2 for Archer freeze eligibility).
8. No implementation changes.

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
| SPEC-1 | IA-001, C-7, five-layer ownership, restricted MC, three-stage catching, AthleteView boundary, formation-free provenance, Gates A/B/C accepted at specification level; RST-1 accepted for both approved violations | 2026-11-08 |

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

### 3a. Command lifecycle and supersession (T6 adopted; RES-P)
- **Chain:** observation frame → belief revision → decision (options, evaluations, selection) → `ActionIntent` → Motor Control → `MotorCommand` (accepted, queued or rejected) → PHY and rules → `PhysicalOutcome`. Every link carries a deterministic, draw-free identifier; wall-clock time, UUIDs, hash-map order and RNG draws are prohibited as ID sources. Encoding is pending approval (T6-O5).
- **Timing fields kept separate, never merged into one "action tick":** `captured_at`, `delivered_at`, `decision_opened_at`, `decided_at`, `not_before`, `accepted_at`, `execution_started_at`, `release_or_contact_at`, `resolved_at`. Reaction, preparation, pose, wind-up, draw and release delays are retained.
- **No silent replacement.** MC may reject, queue, scale or physically realize an intent; it may not change its semantic target or action type. A replacement is a new intent with a new ID and a `supersedes` edge. Allowed interruption causes: (1) a later intent by the same authorized decision owner; (2) rule rejection or administrative stoppage; (3) physical impossibility or authoritative state change (loss of possession, contact, freeze, incapacitation); (4) expiration encoded in the intent. Each interruption produces an outcome with a reason. A legacy controller may not silently overwrite a selected intent.
- **Simultaneous commands:** priority rules are **not decided** (T6-O4, OPEN-D); the command surface cannot be frozen until they are.
- **Acceptance is not legality.** MC acceptance means well-formed and schedulable. Apparent legality is estimated from the athlete's view; actual legality is adjudicated by rules and PHY from true state, so a mistaken attempt can be accepted and then ruled illegal (B0 consequences preserved, nothing inferred for new cases).
- **Focus** is a perception and attention input. B1 adds no motor effect for it (standing prohibition on rating changes).
- **Unavailable data** use `Availability<T>` with a reason (`not_observed`, `occluded`, `outside_attention`, `not_yet_delivered`, `unknown_to_athlete`, `prohibited_by_ia001`, `not_applicable`, `legacy_not_exposed`, `instrumentation_disabled`, `not_computed`); never a zero or null placeholder.
- **B0 tier:** legacy overrides (receiver `next_decision = now`, Pocket 4 carrier-target override, true-threat pose lookup) are preserved only inside the B0 adapter and tagged `legacy_table` or `legacy_not_exposed`; the B1 path may not use the adapter to recover true state.
- **Keeper:** no clamp, loop cap, clock mutation or changed observation to hide the seed-2 reverse-flight pathology; any algorithm replacement needs separate authorization and proven identical output first; incomplete runs never count as completed-match throughput.

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


## 5. Keeper protection matrix and zone geometry (U-1 and U-3 UNRESOLVED)
Legend: **A** approved (DreLen, date) · **B0** observed in B0 source, not canon · **U** unresolved, cell ID given; no test or implementation exists for a U cell and any code path needing one fails configuration validation (CFG-5). Offense and defense are the Keeper's team's phase; the basis during loose and airborne states is itself open (KP-12).
| Aspect | In own zone, offense | In own zone, defense | Outside own zone, offense | Outside own zone, defense |
|---|---|---|---|---|
| Archer targeting | **A** never a target (Keepers are not field players, ARC-1) | **A** same | **A** same | **A** same |
| Incidental arrow impact or freeze | KP-01 (B0: not freeze-eligible inside own zone in any phase, `engine.py:1008-1010`) | KP-02 (same B0 fact) | KP-03 (B0: eligible if ruleset and carrier status allow) | KP-04 (same) |
| Tackle | **A** cannot be contacted on offense | KP-05 | KP-06 (stated "can't be contacted on offense" is unqualified by location; whether it persists after leaving is not stated) | KP-07 ("loses immunities once he leaves"; whether tackle is one of them is not stated) |
| Other contact (blocking, screening, incidental) | **A** same statement; Keeper-initiated contact: KP-08 | KP-09 | KP-10 | KP-11 |
| Phase basis during loose or airborne ball | KP-12 | | | |
| Which "immunities" exist, and the list lost on leaving | KP-13 | | | |
| Persistence of offensive no-contact after leaving the zone | KP-14 | | | |
| Stay duration | **A** indefinite as an individual (the ball is limited by ZR-1) | **A** same | n/a | n/a |
| Scoring | **A** not eligible to score except own goals (exact meaning of "own goals" to be confirmed by you) | | | |
| Exclusivity | **A** no other player receives this protection (KP-A) | | | |
**Direction recorded in your review (not a canon rule):** "Resolve explicitly." Required to close U-1: a decision for each of KP-01…KP-14.

**Zone geometry (U-3).** Direction recorded: "define geometrically, with separate rules for ball and athlete location." Two predicates, `athlete_in_zone` and `ball_in_zone`, each needs its own definition. B0 `zone(x,y,R)` is a circle of radius `keeper_zone_radius` (default 20, `engine.py:23`) around the goal center, using a point position (`engine.py:44-45`). A separate decided ruling (C4c2, 9 October) governs release territory only (`engine.py:51-55`: a line belongs to the farther scoring territory; the Keeper Zone arc counts as an outside release); I do not extend it to the rules below.
| Slot | Question | Status |
|---|---|---|
| G-1 | athlete reference point (body center, footprint, any body part) | U |
| G-2 | ball reference (2-D position, or 3-D so an airborne ball above the zone counts) | U |
| G-3 | edge inclusivity (inside means `<` or `<=` R) | U |
| G-4 | whether the boundary line, end line and goal aperture belong to the zone | U |
| G-5 | radius source (fixed 20 or pocket parameter) and whether both zones are identical | U |
| G-6 | which predicate each rule uses | see below |
| Rule | Predicate | Status |
|---|---|---|
| Keeper protection | `athlete_in_zone` | A (text: "inside his own Keeper Zone"), reference point U (G-1) |
| Archer legal range | `athlete_in_zone` of the target | A (ARC-1: any spot outside the Keeper Zones), reference point U (G-1) |
| ZR-T first touch | `ball_in_zone` at first touch or landing | A (ZR-2), reference U (G-2) |
| ZR-1 five-second clock | `ball_in_zone` | A (text: "ball in own Keeper Zone"), reference U (G-2) |
| ZR-C carrier crossing | athlete or ball, not stated | U (G-6) |

## 6. Zone rules contract (RULE class: adjudicated by the rules engine, never by cognition or MC)
**ZR-1 Five-second limit:** the ball may not remain in the possessing team's own Keeper Zone for more than 5 consecutive seconds, regardless of who holds it. Consequence per RST-1. *Basis and reset rule UNRESOLVED (U-2):* your direction is that the clock follows possession attribution subject to a precise reset rule; the reset rule has not been supplied. B0 only limits the Keeper carrying the ball (`keeper_hold_ms >= 5000`, `engine.py:1714`), resets it on any non-forced release (`engine.py:355`); its legacy controller distributes after 0.4 s (`match.py:949`), so parking never arises in B0 play and becomes reachable in B1.
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

### 6a. Rules-state contract and transition table (skeleton; U-4 UNRESOLVED)
**Public rules state** (exposed to every athlete through `PublicMatchState`): `ball_status` ∈ {carried, pass_in_flight, shot_in_flight, loose_ground, loose_airborne, out_of_play, restart_pending}; `PA` (possession attribution, §4); `TC` (team control, §4); `origin` (whether the current control sequence began outside or inside the relevant own zone — **definition pending, U-4**); `last_toucher` and team; per-team own-zone ball clock; status indicators (freeze, immunity, eligibility; R1); `phase` (offense or defense per team — **basis pending, U-1/U-2**). Internal-only rule state (not visible): none declared yet.
**Transition table.** Rows are (state, event); a cell is APPROVED only where an approved rule text decides it. Everything else is PENDING, with no default.
| Row | State → event | Outcome | Status |
|---|---|---|---|
| T-01 | carried by team T, T in control; carrier crosses from outside into T's own zone | ZR-C violation at the instant of crossing → RST-1 | APPROVED (ZR-2) |
| T-02 | deliberate pass of T in flight, caused to enter T's own zone from outside; a T player is first to touch it after entry (including T's Keeper) | ZR-T violation → RST-1 | APPROVED (ZR-2) |
| T-03 | same, but a defender touches first, or a defender caused the ball to enter | no violation; TC ends at the defender's touch | APPROVED (ZR-2, defender-deflection clause) |
| T-04 | shot of T in flight enters T's own zone | no violation; TC ended at release | APPROVED (ZR-2: "in control" excludes a shot) |
| T-05 | loose ball (fumble or drop) of T enters T's own zone; T player first to touch | no violation | APPROVED (ZR-2: excludes a loose ball) |
| T-06 | RST-1 restart | turnover; center-line opening contact scrimmage; possession to the opposing team | APPROVED (RST-1) |
| T-07 | ball in a team's own zone for 5 consecutive seconds, any holder | ZR-1 violation → RST-1 | APPROVED (ZR-1) for the count; **basis and reset PENDING** |
| T-08 … T-n | every other (state, event) pair, including those in the scenario list below | — | PENDING |
**U-4 scenarios requiring a decision** (questions only; no answer is assumed):
| ID | Class | Scenario | What must be decided |
|---|---|---|---|
| U4-01 | bounce pass | pass of T released outside T's zone, bounces on the ground outside the zone, then enters the zone and is first touched inside by T | does ground contact end TC or keep the pass "deliberate, in flight"? (a bounce option exists in the repository, `bounce_option_v0.py`; whether it is active in B0 is not verified here) |
| U4-02 | bounce pass | pass released outside, first ground contact inside T's zone | does the ground landing count as "lands" (inside) and does a later T touch then count as a first touch? |
| U4-03 | bounce pass | pass released inside T's zone, bounces, leaves and returns | "started inside, left, returned": is it caused to enter by T while in control? |
| U4-04 | control at release | carrier releases a pass at the instant of crossing the boundary, or from the boundary line | which tick order decides ZR-C versus ZR-T, and does the release position or the ball position count? |
| U4-05 | control at release | release under hand contact: strip attempt, tip, or contested release | is the ball a deliberate pass (TC kept), a loose ball, or a deflection; which event types (`release`, `strip`, `grounded`) define it? |
| U4-06 | control at release | pass released by T, defender touches it in the air without gaining control, ball continues into T's zone | does TC end at the touch; who has PA; is a later T touch a first touch? |
| U4-07 | regained control | T regains control inside its own zone after a defender deflection | is `origin` inside (starting a fresh zone-clock sequence) and does the zone-return rule apply later to a carry out and back? |
| U4-08 | Keeper | Keeper catches the opponent's shot inside his own zone | does PA flip at the catch; does the 5-second clock start then; what is the Keeper's phase? |
| U4-09 | out of play | ball goes out of play after a touch or over the boundary | who holds PA at the restart; is the restart governed by RST-1 or an ordinary restart? |
| U4-10 | clock | dead ball, timeout, period break, restart | does the zone clock run, pause or reset? |
| U4-11 | airborne | ball over the zone when 5 seconds expire | does an airborne ball over the zone count (depends on U-3 ball predicate)? |
| U4-12 | simultaneity | offense and defender touch in the same tick | who is "first"? |
| U4-13 | restart | after RST-1, does the opponent's restart possession set PA, `origin` and the clock? | initial values at the scrimmage |
**U-2 candidate reset triggers** (listed only so you can choose; none is assumed): ball leaves the zone; PA changes; a defender touches the ball; a restart; dead ball. **Keeper phase basis** (offense or defense during loose and airborne states) is a separate open item (KP-12) not covered by the U-2 direction.

## 7. Formation-based and formation-free arms
Same architecture (AthleteView, five-layer ownership, MC, instrumentation) and same physical model; they differ only in which assignment providers are enabled. They need not be bit-identical to each other. The formation-based arm is B1 itself and must be reproducible. DO-3 (provenance): every target consumed by MC carries a provenance tag in a side table (`athlete`, `rule`, `team-planner`, `legacy-table`); in the formation-free arm the test fails if any assignment is `team-planner` or `legacy-table` or if a `rule` tag assigns rather than bounds a position; athlete-generated options and emergent organization pass and are only reported. Restarts in that arm: rule-required placement only (O9). Position/archetype carrier biases removed (O10).


## 8. Instrumentation neutrality and NI re-run triggers
**What has been shown.**
- *Claude NI (current instruments):* decision-ID/sentinel wrappers on seven decision entry points plus a `sys.setprofile` counter leave score, event log, the five match RNG streams, module RNG, stats and wrapper chains unchanged (seed 1, B0 and full stack). NI-4: the ten accepted T1 cases replayed with the instruments installed; all ten match.
- *Codex T5 observer:* external step loop, `Policy.targets` wrapper and read-only state and RNG hashing leave every score, event, schedule and RNG signature unchanged (short seed 1; regulation seed 1 matches T1). **Replicated here** under CPython 3.13.18: 10 of 10 checks pass and the hashes equal Codex's 3.12.14 values.
- *Limits, stated plainly:* each result certifies only the instrument it exercised. **The existing NI-4 result is not certification of the T5 observer, of any decision-ID carrier, of DecisionTrace emission, or of the AthleteView adapter.** Neither instrument covers per-athlete PRISM RNG streams per step (CT-4).

**rc2 changes no instrumentation, so no NI re-run is triggered by this document.** The following changes do trigger re-runs and are test obligations:
| Trigger | Re-run | Gate |
|---|---|---|
| any new or changed wrapper, observer or hook, including adopting the T5 observer into the harness | NI-1…3 on seeds 1–3, B0 and full stack; NI-4 on the ten T1 cases; T5 equivalence control-versus-full | A |
| any decision-ID or causal-ID carrier, or DecisionTrace emission | NI-1…4 and ID-2 (replay identity), with telemetry off, minimal and full (C-18) | A, C |
| the AthleteView enforcement layer or identity adapter | IS-7 and NI-4 (identity adapter leaves B0 hashes unchanged) | A |
| any change to cognition RNG use | RNG-1 and RNG-2 (per-step PRISM-stream transitions) | C |
| change of interpreter or platform | Gate A hashes in the new environment, compared against both recorded reference environments | A |
Telemetry consumes no random draw, schedules nothing, iterates no live entity, and mutates nothing.

## 9. T5/T6 agreement and conflict matrix
**Evidence tiers.** *B0 observer tier* = T5 as delivered (external observer on the unchanged B0 engine; correlation only). *B1 contract tier* = T6 typed contracts (causal, per-athlete, per-domain). rc2 adopts both and forbids using the first as proof of what only the second can show.
**Dispositions.** `RES-A` resolved by an already accepted decision · `RES-P` resolved by adoption or precedence (Codex acknowledgment requested) · `OPEN-D` needs your decision · `OPEN-C` needs Codex or joint design work, no canon decision · `INFO` limit or observation, no decision. Nothing marked OPEN is assumed.
Sources: T5 = Codex T5 report and telemetry schema; T6 = Codex T6 packet; Claude = my audit; rc1 = previous candidate.

### 9.1 Typed interfaces
| ID | Topic | T5 | T6 | Claude / rc1 | Verdict | Disposition |
|---|---|---|---|---|---|---|
| TI-1 | AthleteView composition | only reserved extension fields, `not_implemented_t5` | ObservationFrame + SelfView + Knowledge + belief revision + apparent legal actions, immutable value copies | typed per-athlete boundary; public rules-state fields named but not enumerated | AGREE | RES-P: T6 types are the base schema; rules-state members enumerated in §4 and §6a; frozen together (Contract v1, §11) |
| TI-2 | Unavailable data | `null` plus capture_status text | `Availability<T>` with reason enum; never null or zero | hidden and unknown classes | CLARIFY | RES-P: T5 format is the B0 tier; B1 tier uses `Availability` |
| TI-3 | Athlete's knowledge of own capabilities | none | SelfView "accurate … according to approved self-knowledge" (approval gate) | rc1 treated own state as Known (exact); IA-001 says knowledge is individual and imperfect and is silent on own capabilities | CONFLICT | OPEN-D: SELF-1 |
| TI-4 | MC state access | none | own true body and capability plus a command-local constraint projection; no live ball or opponent (R-03) | own body, constraints, command | AGREE | RES-A: restricted MC accepted; T6 wording adopted |
| TI-5 | MC acceptance vs legality | none | acceptance means schedulable only; rules and PHY adjudicate; rejected commands still traced (R-04) | MC reports infeasibility; rules engine adjudicates with true state | AGREE | RES-P: infeasibility is a `rejected` disposition with reason; apparent legality lives in the view |
| TI-6 | Focus rating | none | perception and attention only; any motor effect is a new rating mapping (R-02, T6-O2) | silent | AGREE | RES-A: standing prohibition on rating changes; no Focus motor effect in B1 |
| TI-7 | Catch ownership | none | prepare / MC / PHY; B0 automatic catch kept in adapter (R-01, T6-O1); r3 table said automatic | rc1 §3 already three-stage | AGREE | RES-A: three-stage catching accepted; automatic catch only in the B0 adapter |
| TI-8 | Who may write an athlete's destination | none | §2: team planning must not write a selected intent, legacy tables only propose options; but its DecisionTrace allows owner `team_planner` or `legacy_table` | rc1 §7: formation-based arm keeps assignment providers (tagged), formation-free forbids them | CONFLICT (wording) | RES-P: accepted §7 governs; provider output is admitted with a non-athlete owner tag in the formation-based arm and forbidden in the formation-free arm; Codex to acknowledge |
| TI-9 | Keeper intent modes and arbitration | none | modes listed in §6.3; arbitration policy open (T6-O3) | Keeper triggers | GAP | OPEN-C: mode enum enters the schema; arbitration policy needed before Keeper migration, not before freeze |
| TI-10 | Identifier encoding, schema version | `run:event:id` for historical events | conceptual form in §10 of contracts, encoding open (T6-O5) | decision-ID trace (ID-1) | GAP | OPEN-D: T6-O5, required before Contract v1 freeze |

### 9.2 Causal telemetry
| ID | Topic | T5 | T6 | Claude / rc1 | Verdict | Disposition |
|---|---|---|---|---|---|---|
| CT-1 | Causation vs correlation | outcome linked to latest same-athlete controller event; "not proof of causation" | draw-free deterministic IDs linking observation, belief, options, intent, command, outcome | ID-1 | CONFLICT (capability) | RES-P: two tiers; no IS, DO or ID acceptance test may rely on T5 correlation |
| CT-2 | Decision-domain coverage | sample (short seed 1): 332 decision records, all carrier-controller events; 7,358 team target maps; 543 outcomes of which 105 (19%) have no correlated decision; nothing for receiver, jump, Keeper, Archer, off-ball, hand contest | all domains | DO tests across domains | GAP | INFO: B0 tier is not extended (would need behavioural patching, per T5); B1 tier emits per-athlete per-domain traces |
| CT-3 | Neutrality evidence | external step loop, `Policy.targets` wrapper, state and RNG hashing; passes; replicated here | observer must not schedule, mutate or draw | wrappers at seven decision entry points plus profiler counter; NI-4 10 of 10 | AGREE | INFO: two independent pass-through instruments each pass; an ID-carrying or combined instrument is untested, see re-run triggers in §8 |
| CT-4 | RNG coverage in neutrality tests | per-step transitions cover engine streams only; per-athlete PRISM streams hashed at checkpoints and final | B-09, C-18 | my NI covered the five match streams and module RNG, not per-athlete PRISM streams | GAP | OPEN-C: add per-step or per-decision PRISM-stream transition hashing (test RNG-2) before NI is claimed for any cognition change |
| CT-5 | Python-global RNG | never consumed; compared as changed or unchanged | prohibits global draws | same finding | AGREE | RES-A: consistent, no action |
| CT-6 | Option menus and raw draws | unavailable without behavioural patching | `legacy_not_exposed` | none | AGREE | RES-P: B0 tier records them unavailable; B1 tier exposes them by design |
| CT-7 | Telemetry as pure observer | yes | yes | NI | AGREE | RES-A |

### 9.3 Command supersession
| ID | Topic | T5 | T6 | Claude / rc1 | Verdict | Disposition |
|---|---|---|---|---|---|---|
| CS-1 | No silent replacement | no intent layer | a legacy controller may not overwrite a selected intent | remove the `next_decision = now` bypass (`match.py:2517`); DO-1 | AGREE | RES-A: cadence-bypass removal accepted |
| CS-2 | Interruption causes, supersession edge | none | four allowed causes; replacement is a new intent with `supersedes` | DO-1 only | GAP in rc1 | RES-P: adopted, §3a; test SUP-1 |
| CS-3 | Priority among simultaneous commands | none | open (T6-O4) | none | GAP | OPEN-D: T6-O4, required to freeze the MC-0 command surface |
| CS-4 | Supersession visible in B0 | records decisions, `ball_action_prepared`, outcomes only | preserve pending-action delay | none | GAP | INFO: not verifiable on the B0 tier; verified in B1 only (SUP-1) |
| CS-5 | Single jump owner | none | one takeoff decision, no cadence bypass (§6.2, C-08) | DO-2; both planners fire in the full stack today | AGREE | RES-A: accepted, subject to validation |
| CS-6 | Delays retained | `ball_action_prepared` event | nine separate timing fields | IS-5 | AGREE | RES-P: T6 timing fields adopted (TM-1) |

### 9.4 Physical outcomes
| ID | Topic | T5 | T6 | Claude / rc1 | Verdict | Disposition |
|---|---|---|---|---|---|---|
| PO-1 | Outcome record | `execution_outcome` for 19 event types, correlated | status enum, causal intent and commands, state revisions, rule events, draws | none | CLARIFY | RES-P: tiering as CT-1 |
| PO-2 | Rule events vs physical events | none | rules layer separate; `rules_events` on outcome | RULE class | AGREE | RES-A; detail is the rules-state table (§6a), pending U-4 |
| PO-3 | Gate B tolerance | none | proposes numeric tolerances for native and cross-platform | exact in reference environment | CLARIFY | RES-P: Python B1 stays exact; T6 table is native-track and unratified (T6-O6 deferred) |
| PO-4 | T3 gaps and T3A | none | lists same gaps, says T3A "remains blocked" | O7 approved 2026-11-07 | CLARIFY | RES-A: O7 approved; T6 text predates it |
| PO-5 | Consequences of illegal attempts | none | preserve B0 (for example ammo consumed on an illegal Archer attempt) | ARC-1 removes the B0 10–70 m window | CLARIFY | INFO: consequences for newly illegal cases are not specified by canon; B0 behaviour preserved, nothing inferred |
| PO-6 | Freeze eligibility vs ruleset | none | none | B0 config ruleset is 1.0.1 (verified this session); freeze is valid only for the ball carrier unless ruleset 1.0.2 (`engine.py:1009-1010`), while O6 lets the Archer target all opposing field players | GAP (new) | OPEN-D: R-RS |
| PO-7 | Keeper reverse-flight | seed-2 diagnostic reproduces the T4 state, nothing repaired | no clamp, cap, clock mutation or changed observation | no Keeper optimization | AGREE | RES-A |
| PO-8 | Termination classes | classes and denominators; paired sample: full-PRISM short seed 1 forfeits at 19.2 live s, A 5–0 | retained | my full-stack seed-1 short run also ended A 5–0 (cause not examined) | AGREE | INFO: Gate C uses T5 denominators; forfeit cause not investigated |

### 9.5 RNG ownership
| ID | Topic | T5 | T6 | Claude / rc1 | Verdict | Disposition |
|---|---|---|---|---|---|---|
| RN-1 | B0 stream preservation | exact, hashed per step | adapter preserves generator, order, consumption | NI | AGREE | RES-A |
| RN-2 | Where streams live | engine streams in `match.rng`; PRISM streams in module-level state | `MatchRandomContext`, no module globals | IS-6 isolation test | CLARIFY | RES-P: documented as-is for Python B1; `MatchRandomContext` is native-track |
| RN-3 | Draw ledger and injection | state hashes only; raw draws unavailable | `RandomDrawRecord`; B-09 fixed-draw replay | r3 recorded T3's RNG-order obligation as not executed | GAP | OPEN-C: T3A scope must include fixed-draw fixtures |
| RN-4 | RNG redesign, new substreams | not authorized | needs separate approval (MR-16) | prohibited | AGREE | RES-A |
| RN-5 | Cognition draws vs physics streams | none | stochastic belief updates draw from named cognition streams | silent | GAP in rc1 | RES-P: adopted invariant, cognition draws never advance a PHY or match stream (test RNG-1); Codex to acknowledge |
| RN-6 | Cross-environment reproducibility | CPython 3.12.14 | portable numerics proposed | CPython 3.13.16/18 | AGREE | INFO: schedule, RNG and event hashes equal across the two environments on short seed 1 |

### 9.6 Validation gates
| ID | Topic | T5 | T6 | Claude / rc1 | Verdict | Disposition |
|---|---|---|---|---|---|---|
| VG-1 | Gate definitions A, B, C | equivalence = Gate A | same three gates | same | AGREE | RES-A |
| VG-2 | Test inventory | 15 unit tests; 10 equivalence checks | 9 A or B, 18 C, 3 P tests | rc1 matrix | CLARIFY | RES-P: mapping and 14 new tests in §10 |
| VG-3 | Reference environment | 3.12.14 | none | 3.13.16/18 | AGREE | INFO: both recorded; Gate A requires identical hashes in each |
| VG-4 | Portability tests P-01 to P-03 | SIGALRM supervision | out-of-process supervisor | Python only | CLARIFY | RES-A: native-track, outside B1 (no native rewrite) |
| VG-5 | Gate mislabeling | none | a Gate C difference is never a Gate A or B failure | same | AGREE | RES-A |

### 9.7 Sequencing
| ID | Topic | T5 | T6 | Claude / rc1 | Verdict | Disposition |
|---|---|---|---|---|---|---|
| SQ-1 | Command-replay physical boundary (T6 phase 4) before AthleteView | none | phases 3 to 5 in that order | T3A in parallel with harness; no such boundary | CONFLICT (order) | OPEN-C: is phase 4 a B1 prerequisite or native-track? For Python B1, T3A fixtures (explicit commands, cognition suppressed) already provide command replay, so I treat phase 4 as native-track pending Codex confirmation |
| SQ-2 | Physical fixture before replacing its owner | none | sequencing rule 3 | jump-only precondition | CLARIFY | RES-P: generalized to every domain |
| SQ-3 | Never combine information-boundary and PHY change; no RNG redesign with migration | none | sequencing rules 1 and 2 | consistent | AGREE | RES-P: adopted |
| SQ-4 | Domain order for behavioural step | none | carrier, off-ball, receiver; then catch and jump; then Archer; then Keeper | unordered | CLARIFY | RES-P: proposed order, part of approval A-1 |
| SQ-5 | Undecided values | none | an undecided required value fails configuration validation rather than defaulting | silent | CLARIFY | RES-P: adopted as test CFG-5; this is how U-1 to U-4 behave until decided |

## 10. Validation matrix (T6 IDs mapped; 14 tests added)
Families: CFG configuration · NI neutrality · ID/telemetry · IS information isolation · DO ownership · MF motor fidelity · CT catching · PP physical · AR Archer · RL rules · KP Keeper protection · ARM arms · IQ information-quality sensitivity.
Gates: **A** unchanged B0 replay (the ten T1 cases, exact, instruments absent and present). **B** identical-input physical parity against T3 (and T3A) traces, exact in the reference environment, covering only what the fixtures cover. **C** intentionally changed B1 cognition: change register; IS/DO/MF/CT/AR/RL/KP tests pass; B1-versus-B0 envelope reported (tolerances deferred, O5); IQ-1…4; no recalibration.
| Test | Checks | Gate |
|---|---|---|
| CFG-1…4 | patch match counts and sites; frozen configuration object and hash; invalid flag combinations fail loudly; install-chain snapshot and idempotence | A prerequisite |
| NI-1…4 | score/log, all RNG streams, wrapper chains, T1 canonical replay with instruments (NI-4 done for current instruments) | A |
| ID-1 | B1-tier causal trace: observation → belief → choice → intent → command → release/contact → outcome, via deterministic IDs; T5 correlation is not acceptable evidence (CT-1) | C |
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
| CFG-5 | a required value marked `unapproved` or unresolved (U-1…U-4, SELF-1, R-RS, T6-O3/O4/O5) makes configuration validation fail; no implicit default | A prerequisite |
| IS-8 | two athletes given different views hold individual beliefs and decide individually (T6 C-03) | C |
| IS-9 | each unavailability reason maps to the correct `Availability` reason; no null or zero substitution (T6 C-14) | C |
| TM-1 | controlled perception, reaction, preparation, release delays: all nine timing fields present and honored (T6 C-05) | A, C |
| SUP-1 | new intent during a queued command yields a new ID, `supersedes` edge and interruption outcome; MC never retargets (T6 C-04, C-06) | C |
| DO-4 | Keeper step, dive, jump, gather, parry: view-based intent, MC execution, PHY outcome (T6 C-09) | C |
| RL-8 | mistaken apparent legality: attempt accepted by MC, then adjudicated; no truth leak (T6 C-13) | C |
| ID-2 | identical execution yields identical IDs at every telemetry level (T6 C-17); causal links complete from observation to outcome | A, C |
| RNG-1 | cognition draws never advance a PHY or match stream; every stochastic cognition draw has a named stream | C |
| RNG-2 | per-step (or per-decision) transition hashing of per-athlete PRISM streams in control versus instrumented runs | A, C |
| GB-1 | command isolation: replay with cognition disabled; the cognition module cannot affect output (T6 B-08) | B |
| GB-2 | fixed-draw replay: no implicit or global draw, identical consumption (T6 B-09); needs T3A fixed-draw fixtures | B |
| BK-1 | B0 adapter retains the historical kick with `RULES_V03` off (T6 A-03) | A |
| BP-1 | bounded-path classification: seed-2 Keeper diagnostic through the T5 runner reproduces the same partial path; timeout is not counted complete (T6 A-05) | A |
**T6 validation IDs → rc2 tests.** A-01→Gate A T1 suite · A-02→NI-4 and T5 equivalence · A-03→BK-1 · A-04→CFG-4 · A-05→BP-1 · B-01…B-07→PP-1/PP-2 (T3, then T3A) · B-08→GB-1 · B-09→GB-2 · C-01→IS-2 · C-02→IS-1 · C-03→IS-8 · C-04→MF-4, SUP-1 · C-05→TM-1 · C-06→SUP-1 · C-07→CT-1…3 · C-08→DO-2 · C-09→DO-4 · C-10→AR-1 · C-11→AR-3 · C-12→AR-4 · C-13→RL-8 · C-14→IS-9 · C-15→ARM-1…4 · C-16→DO-3 · C-17→ID-2 · C-18→NI-1…4 · P-01…P-03→native-track, outside B1.

## 11. Dependency order (refined)
Governing rules: never combine an information-boundary change with a PHY equation change; never combine RNG redesign with behavioural migration; a physical fixture (T3 or T3A) must exist before the owner it covers is replaced; B0 and B1 keep separate manifests and verdicts; a gate failure is never relabeled; no velocity clamp, loop cap or clock change as an optimization.
0. **Preservation and manifest.** Freeze B0, T1–T6 and this audit; publish the manifest.
1. **Neutral harness.** CFG tests, NI tests (including the T5 observer as the B0-tier runner and RNG-2), Gate A and B runners, red-baseline ledger against B0. T3A fixtures (O7, approved) proceed in parallel, including fixed-draw fixtures (RN-3).
2. **Contract v1: rules-state contract and typed AthleteView schema, finalized together.** One versioned contract with a single recorded hash. A read-only audit of how the engine represents the rules state feeds it. It contains: the public rules-state members and predicates (§4, §5 geometry, §6a), the transition table (§6a), the zone-clock basis and reset rule, the T6 typed contracts, the identifier encoding (T6-O5), the supersession priorities (T6-O4), the Keeper mode enumeration (T6-O3 policy excluded), and the self-knowledge rule (SELF-1). **Freeze requires** canon decisions for U-1…U-4, SELF-1, R-RS, T6-O4 and T6-O5. Any later change to either half reopens both. Until frozen, values that depend on unresolved items stay `unapproved` and fail validation (CFG-5); I am not proposing a partial freeze.
3. **Enforcement.** AthleteView boundary in test mode (any hidden-field access raises), identity adapter (B0 hashes unchanged, IS-7), typed MC-0 command surface, NI re-run per the §8 triggers. **Gate G-BOUNDARY: Contract v1 frozen, IS-1/2/7 and the NI re-runs green.** No behavioural replacement begins before it.
4. **Rules implementation (first behavioural step).** The rules the contract specifies: ARC-1 range, ZR-C/ZR-T/ZR-1, RST-1 vehicle, Keeper protections, ruleset selection. This is the only step that changes B0 rules, and only where canon says so. Tests RL, KP.
5. **Cognitive replacements, each gated by its IS/DO tests on the boundary and its physical fixture.** Proposed domain order (T6): carrier, off-ball and receiver split (cadence bypass removed); catch preparation and single-owner jump; Archer A-1…A-4; Keeper triggers.
6. **Formation-free arm** (separate experimental mode).
7. **B1 acceptance.** Gates A, B and C with full coverage of carrier, receiver, jump, Keeper and Archer (A-1…A-5).
Native track (T6 phases 4 and 13, `MatchRandomContext`, tolerance ratification, portable supervisor) is outside B1; SQ-1 asks Codex to confirm that phase 4 is not a B1 prerequisite. Deferred beyond B1 (unchanged): Keeper-to-Keeper communication, block option, defensive zone organisation. Not authorized at any step: native rewrite, recalibration, rating development, Keeper optimization.

## 12. Unresolved decisions (nothing here is assumed)
**U-1 to U-4 remain UNRESOLVED.** Your review recorded an approach for each; none is a canon rule yet. Until each closes, nothing that depends on it is specified, implemented or tested, and configuration validation fails if a path needs it.
| ID | Direction recorded in your review | Inputs still required |
|---|---|---|
| U-1 | Keeper protection against tackles, incidental arrows and other contact: resolve explicitly | a decision for each of KP-01…KP-14 (§5) |
| U-2 | possession attribution versus control: use possession attribution for the zone clock, subject to a precise reset rule | the reset rule (candidate triggers in §6a, none chosen); the Keeper phase basis (KP-12) is not covered by this direction and is still open |
| U-3 | Keeper Zone boundary: define geometrically, with separate rules for ball and athlete location | G-1…G-6 (§5) |
| U-4 | bounces, deflections, out-of-play and restarts: resolve through a rules-state transition table | the PENDING rows of the table and scenarios U4-01…U4-13 (§6a), including the bounce-pass cases (U4-01…03) and control-at-release cases (U4-04…06) |
**Other decisions needed from you**
- **SELF-1** (TI-3): is an athlete's knowledge of his own capabilities exact, or an individual estimate like his knowledge of others?
- **R-RS** (PO-6): which ruleset does B1 run under? B0 uses 1.0.1, where an arrow freezes only the ball carrier (`engine.py:1009-1010`); so an arrow hit on an off-ball player does not freeze him, and O6's off-ball targets only make sense under a wider freeze rule (1.0.2 widens freezing). I have not assumed one.
- **T6-O4 and T6-O5** (CS-3, TI-10): supersession priority among simultaneous commands, and the causal-ID encoding with schema version. Both are interface-design approvals; I recommend Codex and I draft them jointly and bring them to you, but the approval is yours.
- **A-1 (revised):** approve the §11 order and the measurement-first Gate C.
**Deferred, no decision needed now:** T6-O3 Keeper arbitration policy (before Keeper migration), T6-O6 native tolerances.
**Requested from Codex (acknowledgment, not canon):** TI-8 precedence reading; RN-5 cognition-draw invariant; T6's decision list is stale relative to O1–O10; SQ-1 phase-4 scope; RN-3 fixed-draw fixtures in T3A; T4 report and packet if you want me to review the Keeper pathology evidence directly.
