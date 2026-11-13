# SPRINT-30 (v2) Execution Strategy

This is the plan the sprint followed. **Actual outcomes: see SPRINT30_IMPLEMENTATION_REPORT.md.**
Nothing here is ACCEPTED. Everything built is an experiment for later review.

## Source and branch

- Branch: `experiment/prism-sprint-30`, created from commit `8d98234` and pushed empty first to prove push access.
- The tip of `b1/m1-decision-outcome` had moved to `c083ae9` ("M1 G1: add governed carrier-receiver-defender scenario") by the time the sprint started. The sprint started from `8d98234` exactly as instructed and did not use `c083ae9`. A later review should reconcile the sprint's G1 handling with that governed scenario.
- Frozen B0 (`2abe497`) is not edited. `b1/preservation.py` checks file identity.
- Specs were read from `claude/hp002-audit` only (read-only).

## Priority

A complete, connected, primitive pipeline for M1 to M5 comes before quality in any one stage. Each simplified module carries a `PRIMITIVE:` comment and is listed in `SPRINT30_LIMITATIONS.md`. A primitive may think badly, but it may not see true state, and physics decides every outcome.

## Architecture

| Module | Role |
|---|---|
| `b1/core.py` (existing) | Typed values: `AthleteView`, `BeliefState`, `ActionIntent`, `MotorCommand`, `PhysicalOutcome`; the M1 decision. Reused. |
| `b1/cognition.py` (new) | Pure per-athlete decision for field players, Keepers and Archers. Rule-based option scoring. No simulation imports. |
| `b1/matchport.py` (new) | One sensor per athlete built on the B0 PRISM perception tracker; command ingress; the B0 `Match.step` used as the physics and rules stepper. |
| `b1/match_run.py` (new) | Command line: run one match for a seed, write the trace, hashes and decision counts. |
| `b1/test_sprint.py` (new) | Boundary, ownership, determinism and legacy-trap tests. |

Flow per athlete: `ObservationFrame → AthleteView → BeliefState → ActionIntent → MotorCommand → B0 physics → PhysicalOutcome → own feedback into the next decision`.

How the legacy controller is kept out: `Match.step` normally asks the legacy tactical code where each athlete should move, whether the carrier passes or shoots, and whether an Archer draws. In `matchport.py` each of those hooks is replaced, either by a reader of the B1 command table or by a trap that raises if reached. The pass re-planner's fallback list of alternative receivers is emptied, so a pass that cannot reach its chosen receiver fails; it is never redirected.

Canon gates: where a rule is open (U-1 to U-4, R-RS, SELF-1) the build uses B0 1.0.1 behavior if B0 implements it, labeled provisional, and does not present it as canon.

## Phases (real clock, logged in `SPRINT30_TIMING.log`)

| Phase | Minutes | Work |
|---|---|---|
| A | 0–2 | Log the clock, create and push the branch. |
| B | 2–14 | Thin skeleton end to end: defender and receiver cognition (G1), N athletes, field actions, Keeper and Archer, full match run. |
| C | 14–22 | Deepen the weakest stage; fix failures; tighten the boundary. |
| D | 22–27 | Validation: B0 identity, existing B1 tests, boundary tests, replay hash, one end-to-end match, a fresh agent running OWN-1..7 and BR-1..7. Extra seeds only if time remains. |
| E | 27–30 | Reports from evidence files, commit, push. No new features after minute 26. |

## Parallel work

One forked worker wrote this file, `SPRINT30_UNLIMITED_STRATEGY.md` and `b1/sprint30/OWN_BR_CHECKLIST.md`, off the critical path. A fresh agent that did not write the code runs the ownership and boundary checks in Phase D.

## If time runs short

Stop features, keep the strongest working build, run the highest-priority remaining checks, report accurately, commit and push.
