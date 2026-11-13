# SPRINT45 OWNER BRIEFING

**Nothing is ACCEPTED. This is experiment evidence for review.**

- Branch: `experiment/prism-sprint-45` (https://github.com/drelenj/beastball_simulator/tree/experiment/prism-sprint-45)
- Source commits: Base A `4b19719` (`b1/m1-decision-outcome`) merged with Round 1 `99cf83a` (`experiment/prism-sprint-30`), `git merge --no-ff`, no conflicts
- Code+evidence commit these reports were generated from: `f59f6c06c990a09c3a26d1086791c59aca2a11d5` (the report commit follows it; see `git log`)
- Frozen B0 `2abe497`: no B0 file changed (`git diff --name-status 2abe497 HEAD -- . ':!b1'` shows additions only)
- Measured clock (`SPRINT45_TIMING.log`): first `2026-11-13T05:20:31Z PHASE_A_START`, last `2026-11-13T05:42:38Z PHASE_D_START_FEATURE_FREEZE_EVIDENCE_RUN`

## 1. What was accomplished

Round 2 merged the Round 1 build onto Codex's M1 code and replaced the weakest pieces. One full match (seed 1, ruleset 1.0.2) ran to the end: {'winner': 'A', 'method': 'shootout', 'score': {'A': 8, 'B': 8}, 'shootout': {'A': 1, 'B': 0}}, 56011 athlete decisions; the same seed replayed with identical hashes: True.

Run it: `pip install scipy numpy pytest && python -m b1.match_run --seed 1 --out /tmp/match_seed1.json`

## 2. What B1 can actually do now

- Tracks possession the way the decision record defines it (direct, passive, contested, 500 ms threshold, zone clock) from engine events, and tells athletes only through delayed rules signals.
- Uses one decision and pass-release path (Codex M1 code) for all field players; passes no longer read the receiver's true state.
- Archers judge legality from their own belief; Keepers inside their zone are not pressed or targeted; zone violations trigger a restart.

## 3. What remains unimplemented or unproven

| milestone | status | notes |
|---|---|---|
| M1 decision-to-outcome (one athlete + G1) | IMPLEMENTED (Base A, provisional; NOT accepted, H3 open) | Base A code and its 25 tests are kept unchanged and pass. Its `core.decide` and pass-release-v1 release code now also run inside the N-athlete loop. |
| M2 plans, communication, receiver cognition | PARTIAL (PRIMITIVE) | Receiver cognition (pass call, intercept of the believed ball path) and one lossless team shout exist. Plan layer, PlanStageActivation, ReactionGate, real communication channel, give-and-go: MISSING. |
| M3 all roles under the boundary | PARTIAL (PRIMITIVE) | Field, Keeper and Archer decide from own view/belief; Archer legality is belief-driven (true-state interlock removed); Keeper protection respected in cognition. Still engine-owned: Keeper save execution (C4c kernel), Archer platform movement, contact micro-behaviour, restart placement, substitutions. |
| M4 rules state, restarts, full match | PARTIAL (PRIMITIVE) | New authoritative possession/rules-state layer (R-01..R-22 as transitions, unit-tested) runs in every match and feeds zone violations to B0 restarts; ruleset 1.0.2 on the B1 instance. Scoring, fouls, other restarts and the clock remain B0 state; KP breaches recorded only; KP-08/KP-OG missing; 4 x 600 s profile not run. |
| M5 gates A/B/C, performance, acceptance bundle | MISSING | Only replay determinism and a small multi-seed smoke run. No behavioural gates, no paired statistics, no performance budget. |

Seed-1 pass outcomes: {'pass_completed': 9, 'pass_completed_other': 13, 'pass_dead:boundary': 15, 'pass_dead:restart_awarded': 3, 'pass_intercepted': 16}. Most passes still do not reach a teammate; this is one seed and no rate claim is made.

## 4. What is blocking the next step

- M1 is not accepted (H3 open).
- The engine still makes choices for athletes (Keeper save plan, restart taker and placement, Archer platform movement, wind-up refusal): the independent review rates OWN-5 FAIL for that reason.
- B0 has no hand-level touch model, so "contested" is under-detected.
- The B0 inventory guard fails on any clean checkout (23 files never committed).

## 5. Recommended action

Review `SPRINT45_LIMITATIONS.md` and the independent review; do not merge. Next engineering step: move restart, Keeper-save and Archer-movement choices behind athlete intents, then run paired multi-seed statistics per `SPRINT45_UNLIMITED_STRATEGY.md`.

## Tests and runs

- `python3 -m pytest -q b1`: **1 failed, 93 passed, 23 subtests passed in 73.62s (0:01:13)**; per file {'b1/test_g1.py': 7, 'b1/test_m1.py': 18, 'b1/test_possession.py': 30, 'b1/test_sprint.py': 29, 'b1/test_sprint45.py': 9}
  - NOT OK: `FAILED b1/test_sprint.py::EngineIntegration::test_frozen_B0_file_identity - R...`
- Full matches: seed 1 completed; additional seeds attempted 3, completed 3, failed 0.

## Reports

- https://github.com/drelenj/beastball_simulator/blob/experiment/prism-sprint-45/SPRINT45_OWNER_BRIEFING.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/prism-sprint-45/SPRINT45_IMPLEMENTATION_REPORT.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/prism-sprint-45/SPRINT45_TEST_REPORT.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/prism-sprint-45/SPRINT45_LIMITATIONS.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/prism-sprint-45/SPRINT45_UNLIMITED_STRATEGY.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/prism-sprint-45/SPRINT45_EXECUTION_STRATEGY.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/prism-sprint-45/b1/evidence_sprint45/INDEPENDENT_REVIEW.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/prism-sprint-45/b1/sprint45/CANON_NOTES.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/prism-sprint-45/b1/SPRINT45_README.md
