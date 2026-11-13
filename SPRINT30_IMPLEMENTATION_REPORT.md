# SPRINT30 IMPLEMENTATION REPORT

Experimental build. Status words used: DESIGN COMPLETE / IMPLEMENTED / TESTED / ACCEPTED. **Nothing is ACCEPTED.**

- Branch: `experiment/prism-sprint-30` (https://github.com/drelenj/beastball_simulator/tree/experiment/prism-sprint-30)
- Source commit: `8d98234` (branch `b1/m1-decision-outcome`; its tip had moved to `c083ae9`, not used)
- Code+evidence commit these reports were generated from: `879857be1dbc5b6dc52cff0a214650603509e27f` (the report commit follows it; see `git log`)
- Frozen B0: `2abe497`, no B0 file changed (`git diff --name-status 2abe497 HEAD -- . ':!b1'` shows additions only)
- Measured clock (`SPRINT30_TIMING.log`): first `2026-11-13T00:20:55Z PHASE_A_START`, last `2026-11-13T00:45:25Z PHASE_E_FINAL_EVIDENCE_AND_REPORTS`

## Changed files (vs source commit)

```
A	SPRINT30_EXECUTION_STRATEGY.md
A	SPRINT30_LIMITATIONS.md
A	SPRINT30_TIMING.log
A	SPRINT30_UNLIMITED_STRATEGY.md
A	b1/SPRINT30_README.md
A	b1/cognition.py
A	b1/match_run.py
A	b1/matchport.py
A	b1/registry.py
A	b1/sprint30/OWN_BR_CHECKLIST.md
A	b1/sprint_evidence.py
A	b1/sprint_reports.py
A	b1/test_sprint.py
(plus the report files committed after this was generated)
```

## Pipeline as built

`engine state -> PRISM sensor per athlete (B0 ArcherPrism: FOV, latency, noise, memory) -> AthleteView + BeliefState -> cognition.decide -> ActionIntent -> ingress -> MotorCommand -> B0 physics (Match.step) -> PhysicalOutcome -> own-action feedback into the next decision`

## Architectural decisions

1. **B0 `Match.step` is the physics/rules stepper.** It is not edited. Every legacy tactical entry point it calls is replaced on the instance by a B1 command reader (`_ball_motor`, `_archer_motor`, `_keeper_motor`, `_targets`, `_restart_receiver`) and the original functions are replaced by traps on the loaded classes (`carrier_decision`, `arrow_decisions`, `c4c2_decide`/`pocket_decide`, `c4c2_targets`, `route_receiver`, `c4c2_inbound`, `penalty_targets`, `Policy.targets/pass_choice/pass_ranked`).
2. **One sensor per athlete** (lazy, seeded by seed+athlete id), ticked every 100 ms; the ball is one more sensed body (PRIMITIVE). Decisions fire per athlete at its own perception latency and decision interval.
3. **Cognition is a pure module** (`b1/cognition.py`, imports only `dataclasses`, `math`); views/beliefs are frozen dataclasses and JSON round-trip.
4. **Motor cannot change kind/target/receiver:** `pass_ranked` returns `[]` so the engine cannot substitute a receiver; shot aim point and arrow aim come from the intent.
5. **Feedback:** released / interrupted / release_failed / rejected_* statuses return only to the acting athlete; a failed kind is excluded from its next decision. World results (pass_completed, pass_intercepted, goal_for, ...) are trace-only.
6. **Causal IDs:** `s30/<ms>/<athlete>/obs` -> `/decision` -> `/intent` -> `/command`; outcomes carry the command id.
7. **Determinism:** trace hash = SHA-256 over every decision row (id, kind, target, aim, admission, command id) and every outcome; state hash over final state.

## Milestone status (experiment evidence, not acceptance)

| milestone | status | notes |
|---|---|---|
| M1 decision-to-outcome (one athlete + G1) | IMPLEMENTED as PRIMITIVE, TESTED (sprint tests) | Existing M1 slice reused unchanged. G1 closed by a new 3-athlete scenario where carrier, receiver and defender all decide through the same boundary; catch/interception/out-of-play decided by engine physics. Not the governed 100-seed G1 matrix (that exists separately at c083ae9 and was not used). |
| M2 plans, communication, receiver cognition | PARTIAL (PRIMITIVE) / mostly MISSING | Receivers and loose-ball pursuit decide from own perception. Plan layer, PlanStageActivation, ReactionGate, communication channel, give-and-go: MISSING. |
| M3 all roles under the boundary | IMPLEMENTED as PRIMITIVE, TESTED (sprint tests) | Field, Keeper and Archer cognition all run from own AthleteView/BeliefState; legacy controller trapped at class level. Keeper/Archer are PROVISIONAL; Keeper save execution delegates to the B0 kernel; no per-role conformance sets. |
| M4 rules state, restarts, full match | PARTIAL (PRIMITIVE) | Full B0-P4-DEFAULT match (2 x 120 s, ruleset 1.0.1) runs to FINAL with scoring, clock, periods, restarts, fouls all enforced by the frozen B0 engine. No B1 rules-state table or rule-event ledger; restart placement and substitutions are engine procedures; canon gates U-1..U-4, R-RS, SELF-1 open. 4 x 600 s league profile not run. |
| M5 gates A/B/C, performance, acceptance bundle | MISSING | Only determinism replay and a small multi-seed smoke run exist. No behavioural gates, no B0-vs-B1 distributions, no performance budget. |

## Deviations from specs

- BR-3 (two-argument `decide`), BA-7 (slot-grid positions), O4 action-resource model reduced to ball/bow/locomotion with one pending command, O5 IDs simplified, CFG-5 (unresolved values) not implemented, public signals without latency. Full list: `SPRINT30_LIMITATIONS.md`.

## Tests run

- `b1.test_m1`: Ran 12 tests in 8.070s -> OK; `b1.test_sprint`: Ran 27 tests in 23.925s -> FAILED (errors=1) (not ok: 1)
  - NOT OK: `test_frozen_B0_file_identity (b1.test_sprint.EngineIntegration.test_frozen_B0_file_identity) ... ERROR`
- Deterministic replay seed 1 (two processes): identical = **True**
- End-to-end match seed 1: `final`, {'winner': 'A', 'method': 'regulation', 'score': {'A': 9, 'B': 3}, 'shootout': None}, 42143 decisions {'archer': 3287, 'field': 36213, 'keeper': 2643}
- Additional full-match seeds: attempted 3, completed 3, failed 0
- G1 scenarios (24 runs: 12 open + 12 contested) terminals: {'pass_completed': 19, 'pass_dead:boundary': 5}
- Independent review by a fresh agent: `b1/evidence_sprint30/INDEPENDENT_REVIEW.md`

## Tests not run

- 4 x 600 s league profile, RULES_V03 profile, 100-seed matrices, behavioural gates, performance budget, B0-vs-B1 comparison.

## Known defects / incomplete milestone requirements

See `SPRINT30_LIMITATIONS.md` (all PRIMITIVE modules, canon gates, defects) and the independent review.

## Reproduce

```
pip install scipy numpy
python -m b1.match_run --seed 1 --out /tmp/match_seed1.json
python -m b1.match_run --scenario g1 --seed 1
python -m unittest b1.test_sprint -v && python -m unittest b1.test_m1
python -m b1.sprint_evidence 2 3 4 && python -m b1.sprint_reports
```
