# EMERGENCE1 TEST REPORT

- Branch `experiment/emergence-1` (https://github.com/drelenj/beastball_simulator/tree/experiment/emergence-1); source commit `c64d92e` (`experiment/prism-sprint-45`); reports generated from commit `2e354573fe1e16ccae28c626d4ed2f56c476406a` (the report commit follows it; see `git log`)
- Clock (`EMERGENCE1_TIMING.log`): first `2026-11-13T13:24:23Z PHASE_A_START`, last `2026-11-13T14:02:18Z PHASE_E_FINAL_COMMIT_PUSH`; cores: 4 (`nproc`)
- Matches: attempted 460, completed 460, failed 0 (search 392, held-out 40, symmetry 20, full-length 8)
- Status words: IMPLEMENTED / TESTED only. **Nothing here is ACCEPTED.** Quality is judged by match results only.

## Suites run

- `python3 -m pytest -q b1` -> **1 failed, 110 passed, 23 subtests passed in 140.46s (0:02:20)**; passed per file {'b1/emergence/test_emergence.py': 12, 'b1/emergence/test_metrics.py': 5, 'b1/test_g1.py': 7, 'b1/test_m1.py': 18, 'b1/test_possession.py': 30, 'b1/test_sprint.py': 29, 'b1/test_sprint45.py': 9}
  - NOT OK: `FAILED b1/test_sprint.py::EngineIntegration::test_frozen_B0_file_identity - R...`

## Required checks

- Existing suite: see above (known failing test: `test_frozen_B0_file_identity`, 23 inventory files never committed).
- Poison / perturbation test for positioning: `test_poison_hidden_state_and_other_team_params_do_not_reach_decisions` (all live bodies, ball and carrier poisoned after capture; views and decisions identical; other team's vector never reaches an athlete). Failing case shown by `test_weights_drive_the_choice_view_change_changes_decision`.
- Determinism: `test_determinism_same_seed_same_params`, `test_parallel_and_serial_and_order_give_identical_hashes` (4 matches serial vs 2 workers in reversed order).
- Parameter bounds and logging: `test_bounds_validation_and_size`, `test_params_are_per_team_fixed_and_logged`, `test_bias_and_risk_parameters_change_ball_decisions`.
- Side-swap symmetry: {'A_goal_diff_mean': 1.35, 'A_wins': 13, 'B_wins': 7, 'draws': 0, 'matches': 20} (identical parameters, seeds 7000+).
- Metrics collector is read-only: `test_metrics.py` (hash identical with and without the collector).
- Independent boundary / ownership check by a fresh agent: `b1/emergence/results/INDEPENDENT_REVIEW.md`.

## Not run

- No 4 x 600 s matches; no search on full-length matches; no per-role parameter search; metric differences are descriptive (no significance test).

## Reproduce

```
pip install scipy numpy pytest
python -m b1.match_run --seed 1                                  # one full match, default parameters
python -m b1.emergence.harness --seeds 1 --period-s 45           # one paired, side-swapped PROXY match
python -m b1.emergence.search --minutes 15 --pop 8 --out b1/emergence/results/search
python -m b1.emergence.final && python -m b1.emergence.report    # held-out, symmetry, full-length sample, reports
python3 -m pytest -q b1
```
