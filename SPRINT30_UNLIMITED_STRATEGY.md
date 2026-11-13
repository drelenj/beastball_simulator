# SPRINT-30: Fastest Credible Path to a Complete, Validated PRISM (no time limit)

Status words: DESIGN COMPLETE = specified on paper. IMPLEMENTED = code exists. TESTED = automated tests pass with evidence. ACCEPTED = the owner accepted the evidence. **Nothing in B1 is ACCEPTED**, and this document does not ask for acceptance.

Basis: `audit/HP-002_B1_IMPLEMENTATION_READINESS_AND_MILESTONE_PLAN_CLAUDE_HALF.md` (milestones M0–M5), the O4 and O5 v3.5 drafts, `TYPED_CONTRACTS.md` and the rc2 approval candidate, on branch `claude/hp002-audit`. The specs were skimmed, not re-audited.

All durations are **ESTIMATES** in focused work sessions, taken from the milestone plan's cognition-side ranges. That plan calls them low-confidence, and the engine-side (Codex) estimates were never supplied.

## 1. What the sprint leaves behind

The sprint build is a connected sketch: every stage exists and runs through real physics, but most stages are primitives. It is evidence about feasibility. It is not a shortcut past M1–M5 acceptance. The fastest path is to keep the sprint's skeleton and boundary tests, and replace primitives in milestone order.

## 2. Owner decisions needed first

These are canon questions. Engineering cannot settle them, and M3 and M4 cannot be accepted without them. Deciding them early is the largest single time saver, because the Keeper, Archer and rules work otherwise has to be built twice.

| Item | Decision needed | Blocks |
|---|---|---|
| U-1 | Keeper protection from tackles, incidental arrows and other contact (cells KP-01…KP-14) | M3 |
| U-3 | Keeper Zone geometry: reference point for ball and athlete, edge inclusivity (G-1…G-6) | M3 |
| R-RS | Ruleset 1.0.1 or 1.0.2 for Archer freeze eligibility | M3 |
| U-2 | Zone 5-second clock: attribution basis and reset rule; Keeper phase basis (KP-12) | M4 |
| U-4 | Bounce, deflection, out-of-play and restart transitions (U4-01…U4-13) | M4 |
| SELF-1 | Whether an athlete knows its own capabilities exactly | Non-blocking; default exact, swept later |

Until each is decided, the dependent path should fail configuration validation (rc2 test CFG-5) or run under a provisional label.

## 3. Milestone path

| M | Work | Exit evidence | ESTIMATE |
|---|---|---|---|
| M0 | Freeze Contract v1-core hash (typed boundary, O4 seven-resource model, O5 structured `CausalId`); conformance profile and scenarios as data | Schema validation; B0 hashes verify | 1–2 sessions |
| M1 | Reconcile the sprint's G1 handling with the governed G1 scenario at `c083ae9`; one-athlete cycle with full trace | 100 seeds with completed, intercepted and tackled outcomes, each traced to an observation; OWN-1..7, BR-1..7 | 3–5 sessions (partly done on `b1/m1-decision-outcome`) |
| M2 | Plan layer, `PlanStageActivation`, `ReactionGate`, communication channel, receiver cognition, give-and-go | Combination completes and fails for traceable reasons; no activation before delivery | 5–8 sessions |
| M3 | All roles under the boundary: field players, Keepers, Archers; no legacy controller | Per-role trace sets; Keeper conformance per decided KP cell; zero true-state reads | 10–15 sessions |
| M4 | Rules-state transition table, restarts, zone clock, scoring, fouls under the chosen ruleset | Reproducible full matches; rule-event ledger; U4 scenario tests | 8–15 sessions (widest uncertainty) |
| M5 | Gates A/B/C, performance, formation-free arm | Acceptance bundle with all hashes | 5–10 sessions |

Total: roughly 32–55 sessions (ESTIMATE, cognition side only). M1 and M2 need no canon decision and can start at once. The M3 engineering can run in parallel with the owner's U-1, U-3 and R-RS decisions if those cells are kept as data.

## 4. Replacing each sprint PRIMITIVE

| Sprint primitive | Why it limits validity | Replacement | Milestone |
|---|---|---|---|
| Rule-based option scoring for cognition | Fixed hand-set weights; no plans, no anticipation, no rating-driven judgment. Behavior says little about the intended game | Option generation and scoring from belief with the Judgment ratings; athlete-owned multi-stage plans; `OptionTrace` with named cognition-stream draws | M2 (plans), M3 (all roles) |
| Ball perceived as a sensor body | The ball goes through the body tracker, so its noise, occlusion and flight read are not the ball's own model | A ball channel in `ObservationFrame` with its own latency and flight estimate; public ball status per the rules-state contract | M2 |
| Keeper save motor delegates to the B0 C4c kernel under a B1 save intent | The Keeper decides *whether* to save from its own view, but the kernel's dive plan reads the true flight. The save is partly outside the boundary | Keeper belief of the flight feeds a Motor Control dive command; the kernel only executes it. TI-9 Keeper intents; KP cells from U-1 | M3 |
| Dead-ball restart placement and substitutions left to B0 engine procedures | Athletes do not choose their restart positions or who takes it; rotation is not a coach or athlete decision | Restart states exposed in `PublicMatchState`; athletes decide positions; substitutions through a coach-level contract or an explicit out-of-scope ruling | M4 |
| Archer primitive draw and release | Target choice and lead are minimal; freeze eligibility follows B0 1.0.1 provisionally | Archer belief model (C-7), target-set rule O6, draw and release as resource commands with commitment boundaries; R-RS decided | M3 |
| Slot-grid home positions | Positions are assigned from outside the athlete, which BA-7 forbids ("no receiving position, formation or role is assigned from outside") | Positions emerge from each athlete's own space and marking evaluation; formation-free arm tested | M2–M3, proven in M5 |

Two structural items from the specs are also absent from the sprint and must be built, not patched: the O4 action-resource model (seven resources, default-NO compatibility table, atomic bundles, queue depth one, commitment boundaries, coincident-event ordering) and the O5 structured `CausalId` with registries. The sprint uses string IDs and a single pending action per athlete.

## 5. Validation plan

1. **Boundary, every milestone, every role.** OWN-1..7 and BR-1..7 as automated tests that can fail: poison true state with the delivered view fixed (decision byte-identical); alter the view (decision changes as the scoring predicts); JSON replay of cognition in a process with no simulator loaded (BR-4); import and symbol scans (BR-1, BR-2); legacy controllers unimportable (BR-7).
2. **Determinism.** Same seed and configuration give identical trace and state hashes, at scenario level and for a full match, on two runs and across a process restart.
3. **Physical parity (Gate B).** Pass, flight, catch, tackle, shot and arrow fixtures give the same physics under B1 commands as in frozen B0.
4. **Multi-seed matrices.** 100+ seeds per condition for scenarios (the M1 plan's figure); a full-match matrix sized after measuring run time. Report attempted, completed and failed, and the outcome mix with a traced cause for each failure class.
5. **Behavior (Gate C).** Latency and outcome distributions for B0 versus B1. The owner deferred the numeric tolerances; set them from M1–M4 distributions before M5.
6. **Independent review.** Each milestone candidate is checked by a reviewer who did not write the code and who reruns the tests and writes their own probes, as in M1 reviews R1–R3. The owner alone accepts.

## 6. Risks

- **Canon delay.** U-1 to U-4 and R-RS undecided stalls M3 and M4. Mitigation: decide early; keep cells as data.
- **Engine coupling.** B0's stepper mixes tactical decisions with physics. The sprint replaces hooks at run time, which is fragile; a missed hook is a silent boundary leak. Mitigation: a dedicated physical execution port with a closed method list, and traps on everything else.
- **Rules gaps.** `RULES_V03` notes list items not implemented in B0 (offside, Contact Scrimmage, First Hunt, 25-arrow limit). M4 may need engine work outside PRISM.
- **Keeper and Archer belief models.** Each needs its own model; the milestone plan names this as the M3 risk.
- **Performance.** One sensor per athlete each tick may be too slow for full-match matrices or the phone target. Measure in M3, not M5.
- **Behavior quality.** Athletes limited to their own knowledge may not produce the intended game. This is the central unproven claim and only M2 onward can test it.
- **Primitive drift.** A sprint primitive that works well enough may be left in place. Mitigation: the limitations list is a gate; no milestone is proposed for acceptance while one of its primitives remains.

## 7. Recommended order of action

1. Owner reviews the sprint evidence as an experiment only.
2. Owner decides U-1, U-3 and R-RS (needed for M3), then U-2 and U-4 (needed for M4).
3. Finish M1 through the normal review path, reusing the sprint's boundary tests.
4. M2 give-and-go with real plans, then M3, M4, M5 in order, replacing primitives per §4.
