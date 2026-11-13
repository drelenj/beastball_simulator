# EMERGENCE1 IMPLEMENTATION REPORT

- Branch `experiment/emergence-1` (https://github.com/drelenj/beastball_simulator/tree/experiment/emergence-1); source commit `c64d92e` (`experiment/prism-sprint-45`); reports generated from commit `2e354573fe1e16ccae28c626d4ed2f56c476406a` (the report commit follows it; see `git log`)
- Clock (`EMERGENCE1_TIMING.log`): first `2026-11-13T13:24:23Z PHASE_A_START`, last `2026-11-13T14:02:18Z PHASE_E_FINAL_COMMIT_PUSH`; cores: 4 (`nproc`)
- Matches: attempted 460, completed 460, failed 0 (search 392, held-out 40, symmetry 20, full-length 8)
- Status words: IMPLEMENTED / TESTED only. **Nothing here is ACCEPTED.** Quality is judged by match results only.

## Existing files and functions edited (for the merge with Codex)

- `b1/cognition.py`: imports of `emergence.params` / `emergence.positioning`; new field `AthleteView.policy`; new helper `_position(...)`; in `decide(...)` the four call sites that produced `home` / `support` / `mark` now call `_position` (dead-ball non-taker, loose-ball fallback, team-mate carrier, opponent carrier); `32` -> `view.policy.shot_range`; a bias / risk block immediately before `chosen = max(...)`; `policy` added to the decision record; `view_from_json` restores `policy`. `home_position` is left in the file but is unreachable from `decide` (tested).
- `b1/matchport.py`: `MatchPort.__init__(..., policies=None, period_seconds=None)` (validation, settings copy); `deliver` passes `policy=self.policies[a.team]`; `run_match(..., policies, period_seconds, on_decision, on_step)` and the two hook calls; parameters and settings hashed into the trace hash; `policy_params` in the result; `position` added to `LOCOMOTION`.
- `b1/test_sprint.py`: BR-1 import allow-list extended by the two pure emergence modules.
- NOT touched: `b1/core.py`, `b1/runtime.py`, `b1/possession.py`, Keeper save (`_keeper_motor`), restart taker (`_ready`, `_restart_receiver`), Archer movement, release withholding, any B0 file.

## New files

- `b1/emergence/params.py`, `positioning.py`, `harness.py`, `search.py`, `final.py`, `metrics.py`, `readout.py`, `report.py`, tests, `results/`.

## Changed files (vs source commit)

```
A	EMERGENCE1_NEXT_STEPS.md
A	EMERGENCE1_TIMING.log
M	b1/cognition.py
A	b1/emergence/ENGINE_CONSTRAINTS.md
A	b1/emergence/OWN_BR_FOR_POSITIONING.md
A	b1/emergence/README.md
A	b1/emergence/__init__.py
A	b1/emergence/final.py
A	b1/emergence/harness.py
A	b1/emergence/metrics.py
A	b1/emergence/params.py
A	b1/emergence/positioning.py
A	b1/emergence/readout.py
A	b1/emergence/report.py
A	b1/emergence/results/INDEPENDENT_REVIEW.md
A	b1/emergence/results/final_summary.json
A	b1/emergence/results/full_length.jsonl
A	b1/emergence/results/heldout.jsonl
A	b1/emergence/results/search/matches.jsonl
A	b1/emergence/results/search/search_state.json
A	b1/emergence/results/search_stdout.txt
A	b1/emergence/results/symmetry.jsonl
A	b1/emergence/results/tests_pytest_b1.txt
A	b1/emergence/results/tests_summary.json
A	b1/emergence/results/trace_evolved_vs_baseline_seed9000.json
A	b1/emergence/run_tests.py
A	b1/emergence/search.py
A	b1/emergence/test_emergence.py
A	b1/emergence/test_metrics.py
M	b1/matchport.py
M	b1/test_sprint.py
M	b1/test_sprint45.py
```

## Architectural decisions

1. `PolicyParams`: 16 bounded numbers, frozen, validated at construction; one vector per team, fixed before the match, carried in each athlete's own view; logged in the match result, every decision record and the trace hash.
2. Positioning: 9 candidate points (stay or 6 m in 8 directions) scored from the athlete's belief; offence/defence mode comes only from the public passive-possession signal; no slot or formation input.
3. Option biases are additive on the existing option values; risk parameters filter options (lane clearance, shot range).
4. Harness: one process-local engine per match, parallel pool, rows keyed and sorted by job id; both side assignments on every seed.
5. Search: population with a fixed baseline anchor, round-robin, results-only fitness, time-boxed; proxy 2 x 45 s.

## Deviations

- Parameters are per team, not per role. `match_run` CLI has no parameter flags (use the harness).
- The search started at minute 5 (earlier than the planned minute 20) to gain generations and was time-boxed to 25 minutes.
- "Mark" and "support" no longer exist as option kinds; they are absorbed into positioning weights (`pos_opp_def`, `pos_lane`, ...).

## Known defects

See `EMERGENCE1_LIMITATIONS.md` and the independent review.

## Reproduce

```
pip install scipy numpy pytest
python -m b1.match_run --seed 1                                  # one full match, default parameters
python -m b1.emergence.harness --seeds 1 --period-s 45           # one paired, side-swapped PROXY match
python -m b1.emergence.search --minutes 15 --pop 8 --out b1/emergence/results/search
python -m b1.emergence.final && python -m b1.emergence.report    # held-out, symmetry, full-length sample, reports
python3 -m pytest -q b1
```
