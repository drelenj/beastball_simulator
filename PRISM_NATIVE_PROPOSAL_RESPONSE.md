# Claude's assessment of the PRISM Native Architecture Initiative — 2026-11-05
Status: review and plan for DreLen's approval. No rewrite started. Findings marked **[confirmed]** come from the code as it stands today; **[assumed]** means not yet verified.

## 1. Verdict
I agree with the objective, the incremental strategy, and the "no success claims from unit tests" rule. I disagree with three things: (a) there is no source-of-truth repository yet, so the plan's foundation doesn't exist; (b) the "PRISM decides, engine resolves" line leaves out a motor-control layer that DreLen's own rulings require; (c) the plan treats the current runtime as a stable baseline when PRISM I has open defects. Details below.

## 2. Does the responsibility split match the codebase?
Mostly yes.
- **Lineage [confirmed]:** Pocket 4 (`pocket4_proto.py`, 668 lines) loads `Beastball Pocket 2 0(1).py` (10,277 lines, engine/match/policies embedded) and patches it in memory. The v3.7 capability table and the condition layer are wired in unchanged. Pocket 4 rewrote no physics or anatomy.
- **Correction to section 2:** the "Pocket 4" change list should also name hand fighting, the split Judgement ratings, off-ball actions, teammate/free-ball perception, and the Keeper on PRISM. The patch chain is longer than "selected modifications".
- **Unverified:** I can't confirm who authored the v3.x anatomy/locomotion/capability layers. The agreement should say "provenance unknown" rather than assign it.
- **Codex's side:** I have not read Codex's physics code in this session, so I'm not judging what Codex owns, only that the split is plausible.
- **Practical gap:** DreLen relays between us by hand. "Cross-review" and "separate branches" therefore need to be file-packet based (one self-contained file per handoff), or review becomes the bottleneck.

## 3. What the decision-ownership audit should also catch
These are concerns I already know of, not guesses. Each is a candidate audit row.
1. **Hard-coded formation anchors [confirmed].** `positional_tendencies_v1.py` and the engine's `Policy.targets` give every player a role-based base position. My off-ball scoring includes a "stay near base" term. This prescribes tactical structure and directly conflicts with section 8. It is the single biggest threat to the emergence experiment.
2. **Layered last-writer-wins targets [confirmed].** Policy targets → PRISM wrappers → `c4c2_targets` → `route_receiver` → off-ball overrides re-applied. Ownership depends on wrapper order, and the engine only adopts targets after a `next_decision` gate. The audit must list the order and who wins.
3. **Embedded drill tables [confirmed].** `pocket_decide` values shoot/carry/pass from `C4C2_EST` tables measured on the old physics and old controller. They act as shared "game knowledge" identical for every player. I have **not verified** whether `pocket_decide` reads true opponent positions or only the swapped belief world. That is audit row one for the cognition side **[assumed: possible leak]**.
4. **Known true-state leaks [confirmed]:** kick-off teammate prior (`mate_prior_true`, counted); rules/referee/restarts read true state (legitimate, but must be listed); Keeper and Archer paths not yet audited line by line.
5. **Global constants as culture.** Thresholds and noise strengths are the same for every player. Acceptable, but they are authored behaviour; they need a registry (section 7).
6. **Rating jitter [confirmed].** `derive()` applies independent jitter to each rating. The uniform-0.70 control experiment needs this off, or it isn't uniform.
7. **Stale state across matches [confirmed, fixed].** Perception state persisted between matches in one process and disabled all perception minds in later matches. Any earlier multi-match-per-process result is suspect and should be re-run.

## 4. What must be validated before migration
Minimum gate (all on a frozen, tagged baseline):
- **Information-integrity canary test (new):** perturb the true positions of every entity a player cannot perceive; assert that player's decisions are bit-identical. This turns "no unauthorized state access" from a review claim into a test. Run it per decision site.
- **Determinism test:** same seed, same config, identical event log; per-agent RNG streams.
- **Physics golden traces:** with PRISM off, tick-level traces of locomotion, ball flight, contact and condition, to hash and compare.
- **PRISM I matrix, current state:** working: perception, teammate/free-ball views, call channel, Keeper, catch, hand fight (probes), Playmaking/Finishing/Goalkeeping/pursuit effects (scenario level). **Incomplete/failing:** Carrier/Defender Duel lab (saturated), Marking and Zone Reads effect tests, contact band at match level, ENGAGE essentially never chosen, no full-match paired runs on the full stack.
- **Calibration:** DreLen's. Nothing recalibrated silently; all noise strengths stay marked [P].

## 5. What Codex can start now vs later
**Safe now (no dependence on PRISM behaviour):** git repo and baseline tag; headless runner, seed management, resumable batch, telemetry schema, statistics with uncertainty; profiling of the current simulator; the runtime patch-chain map; physics golden traces; native design for state/rules, geometry, ball flight.
**Later, behind golden traces:** locomotion/capability port, condition/injury, contact kernel, rules/restarts.
**Not yet:** anything cognitive (perception, hand fight, off-ball actions, Judgement hooks). They are still changing and need the validation gate first.
**Performance note [confirmed]:** the full stack is about 4–5× slower per game than stock. The cause is the world-state swap in `with_view` (see section 6). A native design should remove it rather than port it.
**Language:** decide after profiling. iPhone deployment constrains the choice; I'd not assume a speed gain from any language before the profile exists.

## 6. Risks to emergence and physics
1. **Prescribed structure** (section 3, items 1 and 3). Remove or neutralize the formation anchors for the control arm and keep a documented "formation-free" switch.
2. **"Emergent" means emergent from our utility function.** The action set and the value function are authored. Roles that appear are products of that utility plus physics, not discovery of the sport's optimum. Reports should say so.
3. **Uniform 0.70 teams are symmetric.** Identical cognition can herd or stay degenerate. The control tests whether *situational* roles emerge from geometry, ball and time, not whether rating-based archetypes emerge. Pre-register the role metrics (spatial occupancy, ball-distance rank, assignment persistence) before running.
4. **Information integrity by swap discipline is fragile.** Today policies see beliefs because the world is temporarily swapped. Native design should make it impossible by type: cognition receives only an `Observation`/`BeliefState`, never the world.
5. **Porting drift.** Float ordering, step order and RNG draws change behaviour silently. Equivalence needs both tick-level tolerances for physics and statistical tests for matches.
6. **Optimization pressure** to cache or batch perception could alter latency/confidence semantics. Perception timing is part of the rating model.

## 7. Recommended changes to the agreement
1. **Git first.** The working directory is not a repository; history is `_before_*.py` copies. Create the repo, tag the current runtime as `baseline-p4-2026-11-05`, retire the copies.
2. **Define the baseline** as the tagged runtime plus a golden-output pack (traces, scenario results, seeded matches). Migration acceptance is measured against it.
3. **Constants registry:** every tunable gets an ID, value, owner and status (canon, calibrated, [P] provisional). No silent changes.
4. **Add a Motor Control boundary.** PRISM includes Motor Control, but section 4 says the engine resolves physics. DreLen's ruling that contact landing is governed by Motor Control with Focus needs a layer between intent and physics (aim, hand placement, execution error). Define it explicitly and say who owns it.
5. **Interface contracts before code:** `Observation`, `BeliefState`, `ActionIntent`, `PhysicalOutcome`, `DecisionTrace`. PRISM emits intents and traces; the engine returns outcomes.
6. **Inspectability requirement:** every action selection logs its options, values, noise draws and ratings used (the "reasons for action" requirement in section 8).
7. **PRISM IV guard:** seeded noise, held misreads and per-run variation are not learning; state that so nobody confuses them.
8. **Deliverable order:** (1) repo + baseline, (4) benchmark, (2) patch-chain map + audit, (3) validation matrix, then (5)–(8).

## 8. Proposed initial task split
| Deliverable | Claude | Codex |
|---|---|---|
| Repo, baseline tag, golden pack | specify scenarios and seeds | create repo, traces, hashes |
| Runtime architecture map | wrapper order and cognition modules | full patch/override chain, dependency graph |
| Decision-ownership audit | cognition-side rows, leak/canary tests | physics-side rows, engine overrides |
| Validation matrix | write and run | review |
| Benchmark | `with_view` cost breakdown | whole-simulator profile |
| Interfaces (Observation/Belief/Intent) | draft | review for engine fit |
| Native core prototype | review | design and prototype physical layers |
| Risk register | draft cognition risks | draft engine risks |

## 9. Decisions needed from DreLen
1. Approve a formation-free control arm (remove base-position anchors for the uniform-0.70 run).
2. Approve the Motor Control boundary as a named layer.
3. Approve git as the source of truth and retiring `_before_` copies.
4. Confirm nothing further is recalibrated until the validation matrix is complete.
