# EMERGENCE1 OWNER BRIEFING

**Nothing is ACCEPTED. Experiment evidence only.**

- Branch `experiment/emergence-1` (https://github.com/drelenj/beastball_simulator/tree/experiment/emergence-1); source commit `c64d92e` (`experiment/prism-sprint-45`); reports generated from commit `2e354573fe1e16ccae28c626d4ed2f56c476406a` (the report commit follows it; see `git log`)
- Clock (`EMERGENCE1_TIMING.log`): first `2026-11-13T13:24:23Z PHASE_A_START`, last `2026-11-13T14:02:18Z PHASE_E_FINAL_COMMIT_PUSH`; cores: 4 (`nproc`)
- Matches: attempted 460, completed 460, failed 0 (search 392, held-out 40, symmetry 20, full-length 8)
- Status words: IMPLEMENTED / TESTED only. **Nothing here is ACCEPTED.** Quality is judged by match results only.

## 1. Accomplished

A complete loop runs: parametrized athletes -> parallel paired matches -> search -> held-out comparison -> read-out. The `home` formation grid is gone from decisions; athletes choose positions from their own belief with searched weights.

## 2. What B1 can do now

- One match: `python -m b1.match_run --seed 1`; one paired proxy match: `python -m b1.emergence.harness --seeds 1 --period-s 45`; one search: `python -m b1.emergence.search --minutes 15 --pop 8`.

## 3. Unimplemented or unproven

- Held-out result: evolved better on 19 of 20 held-out paired seeds, worse on 1, tied 0; mean goal difference 9.6; exact sign-test p = 4e-05.
- See `EMERGENCE1_RESULTS.md` for what the read-out shows and `EMERGENCE1_LIMITATIONS.md` for what constrains it.

## 4. Blocking

- Compute (4 cores, minutes of search) and the engine-owned choices listed in the limitations.

## 5. Recommended action

- Review the exploit log; merge Codex's ownership enablers; rerun the search with far more paired seeds (`EMERGENCE1_NEXT_STEPS.md`).

## Links

- https://github.com/drelenj/beastball_simulator/blob/experiment/emergence-1/EMERGENCE1_RESULTS.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/emergence-1/EMERGENCE1_EXPLOIT_LOG.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/emergence-1/EMERGENCE1_LIMITATIONS.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/emergence-1/EMERGENCE1_IMPLEMENTATION_REPORT.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/emergence-1/EMERGENCE1_TEST_REPORT.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/emergence-1/EMERGENCE1_NEXT_STEPS.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/emergence-1/b1/emergence/README.md
- https://github.com/drelenj/beastball_simulator/blob/experiment/emergence-1/b1/emergence/results/INDEPENDENT_REVIEW.md
