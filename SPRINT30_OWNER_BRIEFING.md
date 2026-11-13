# SPRINT30 OWNER BRIEFING

**Nothing is ACCEPTED. This is experiment evidence for your review.**

- Branch: `experiment/prism-sprint-30` (https://github.com/drelenj/beastball_simulator/tree/experiment/prism-sprint-30)
- Source commit: `8d98234` (branch `b1/m1-decision-outcome`; its tip had moved to `c083ae9`, not used)
- Code+evidence commit these reports were generated from: `879857be1dbc5b6dc52cff0a214650603509e27f` (the report commit follows it; see `git log`)
- Frozen B0: `2abe497`, no B0 file changed (`git diff --name-status 2abe497 HEAD -- . ':!b1'` shows additions only)
- Measured clock (`SPRINT30_TIMING.log`): first `2026-11-13T00:20:55Z PHASE_A_START`, last `2026-11-13T00:45:25Z PHASE_E_FINAL_EVIDENCE_AND_REPORTS`

## 1. What was accomplished

A complete, runnable, primitive PRISM pipeline: all 24 on-field athletes (10 field players, Keeper, Archer per side, plus substitutes as they enter) each decide from their own delayed, noisy, field-of-view-limited perception, and the frozen B0 engine executes their commands. One full match ran to the final whistle: {'winner': 'A', 'method': 'regulation', 'score': {'A': 9, 'B': 3}, 'shootout': None} with 42143 athlete decisions. The same seed run twice gave identical hashes: True.

Run it: `pip install scipy numpy && python -m b1.match_run --seed 1 --out /tmp/match_seed1.json`

## 2. What B1 can actually do now

- Field players carry, pass, shoot, press the carrier, pursue loose balls and receive passes; catches, interceptions, tackles, goals and fouls are decided by the B0 physics and rules, never by the decision code.
- Keepers position and can issue a save intent; Archers draw and release at the believed opposing carrier (both PROVISIONAL).
- The legacy tactical controller is trapped: calling it raises an error, and the match completes without it.

## 3. What remains unimplemented or unproven

| milestone | status | notes |
|---|---|---|
| M1 decision-to-outcome (one athlete + G1) | IMPLEMENTED as PRIMITIVE, TESTED (sprint tests) | Existing M1 slice reused unchanged. G1 closed by a new 3-athlete scenario where carrier, receiver and defender all decide through the same boundary; catch/interception/out-of-play decided by engine physics. Not the governed 100-seed G1 matrix (that exists separately at c083ae9 and was not used). |
| M2 plans, communication, receiver cognition | PARTIAL (PRIMITIVE) / mostly MISSING | Receivers and loose-ball pursuit decide from own perception. Plan layer, PlanStageActivation, ReactionGate, communication channel, give-and-go: MISSING. |
| M3 all roles under the boundary | IMPLEMENTED as PRIMITIVE, TESTED (sprint tests) | Field, Keeper and Archer cognition all run from own AthleteView/BeliefState; legacy controller trapped at class level. Keeper/Archer are PROVISIONAL; Keeper save execution delegates to the B0 kernel; no per-role conformance sets. |
| M4 rules state, restarts, full match | PARTIAL (PRIMITIVE) | Full B0-P4-DEFAULT match (2 x 120 s, ruleset 1.0.1) runs to FINAL with scoring, clock, periods, restarts, fouls all enforced by the frozen B0 engine. No B1 rules-state table or rule-event ledger; restart placement and substitutions are engine procedures; canon gates U-1..U-4, R-RS, SELF-1 open. 4 x 600 s league profile not run. |
| M5 gates A/B/C, performance, acceptance bundle | MISSING | Only determinism replay and a small multi-seed smoke run exist. No behavioural gates, no B0-vs-B1 distributions, no performance budget. |

Every decision rule is a hand-set primitive, so the scores say nothing yet about how real PRISM athletes would play. Seed-1 match physical outcomes: {'arrow_released': 52, 'goal_for:shoot': 4, 'interrupted': 54, 'keeper_save_plan:launch': 1, 'pass_completed': 17, 'pass_completed_other': 4, 'pass_dead:boundary': 4, 'pass_intercepted': 7, 'rejected_not_prepared': 7, 'rejected_out_of_range': 5, 'release_failed': 3, 'released': 81}. The independent review rated most boundary tests WEAK when it ran; fixes made afterwards are not re-reviewed.

## 4. What is blocking the next step

- Your canon decisions: U-1..U-4 (Keeper zone, zone clock, restarts), R-RS (ruleset 1.0.1 vs 1.0.2), SELF-1 (Archer foul mapping).
- Reconciling this sprint with the governed G1 work at `c083ae9`.
- The B0 inventory guard lists 23 files that are not in git, so it fails on any clean checkout.

## 5. Recommended action

Review `SPRINT30_LIMITATIONS.md` and the independent review; decide the canon items; then follow `SPRINT30_UNLIMITED_STRATEGY.md` (keep the skeleton and boundary tests, replace primitives in milestone order). Do not merge this branch.

## Tests

- `b1.test_m1`: Ran 12 tests in 8.070s -> OK; `b1.test_sprint`: Ran 27 tests in 23.925s -> FAILED (errors=1) (not ok: 1)
  - NOT OK: `test_frozen_B0_file_identity (b1.test_sprint.EngineIntegration.test_frozen_B0_file_identity) ... ERROR`
- Matches: seed 1 completed; additional seeds attempted 3, completed 3, failed 0.

## Reports

- https://github.com/drelenj/beastball_simulator/blob/experiment/prism-sprint-30/SPRINT30_OWNER_BRIEFING.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/prism-sprint-30/SPRINT30_IMPLEMENTATION_REPORT.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/prism-sprint-30/SPRINT30_TEST_REPORT.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/prism-sprint-30/SPRINT30_LIMITATIONS.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/prism-sprint-30/SPRINT30_UNLIMITED_STRATEGY.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/prism-sprint-30/SPRINT30_EXECUTION_STRATEGY.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/prism-sprint-30/b1/evidence_sprint30/INDEPENDENT_REVIEW.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/prism-sprint-30/b1/SPRINT30_README.md
