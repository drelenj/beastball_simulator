# HP-002 — Claude review of experiment/prism-sprint-30 (commit 99cf83a)
Claude, 2026-11-12. Source: Claude Code sprint run, branch `experiment/prism-sprint-30`, based on 8d98234. Experimental; nothing ACCEPTED.

## OWNER BRIEFING
1. **Accomplished.** The sprint produced a complete primitive pipeline in 28 min 23 s (its timing log: 00:20:55Z → 00:49:18Z). I rebuilt it independently: 38 of 39 tests pass (the one error is a known inventory-file problem), and a full seed-1 match ran to the final whistle twice with identical hashes, also identical to the committed evidence (9–3, 42,143 decisions, ~43 s per match on my machine).
2. **What B1 can do now.** 24 athletes (field, Keeper, Archer) each decide from their own delayed, noisy perception and the frozen B0 engine executes and judges everything. Goals, tackles, interceptions, restarts and the clock come from the engine's rules, not the decision code. Seed 1 produced 4 goals (3 points each), 71 passes, 17 shot intents, 52 arrows.
3. **Unimplemented or unproven.** No plans, no communication, no give-and-go (M2 mostly missing). No behavioral gates, no calibration, no performance budget (M5 missing). Team shape is imposed from outside (slot grid). The sprint's briefing marks M3 "IMPLEMENTED, TESTED"; I rate it **PARTIAL**: Keeper saves are planned by the old B0 engine planner, Archer movement is engine-owned, and the Archer legality check reads true state. Without that check every match ended early in a forfeit after Archer fouls.
4. **Blocking.** Your canon decisions (Keeper zone, zone clock, restarts, ruleset version, Archer foul mapping) still gate real M3/M4. The sprint's own independent review rated most isolation/ownership tests WEAK; fixes after it were not re-reviewed. Also the inventory guard fails on a clean checkout.
5. **Recommended action.** Treat this as a proof that the skeleton works, not as acceptance. Do not merge it. Next: I review Codex's governed G1 (c083ae9, 100-seed matrix) and re-review the sprint's strengthened tests; then replace primitives in milestone order.

## Independently verified (TESTED by me)
| Claim | Result |
|---|---|
| Tests | `b1.test_sprint` + `b1.test_m1`: 39 run, 38 pass, 1 error (`test_frozen_B0_file_identity`, 23 inventory files never committed). Same as sprint reported |
| Determinism | seed 1 twice: trace and state hashes identical, equal to committed evidence |
| Full match | `status final`, 2 periods, score 9–3, regulation method, no early forfeit |
| Boundary reads (I read `matchport.py` deliver) | Tracks come from the delayed, noisy PRISM sensor; self position, possession, clock and restart signals come from a snapshot delayed by perception latency (exact, no noise); Archer quiver count likewise |
| B0 | `git diff 2abe497` shows additions only |

## Where I disagree with the sprint's own briefing
- M3 "IMPLEMENTED, TESTED" → **PARTIAL**: Keeper save execution and Archer platform movement are B0 engine procedures (disclosed in limitations); the Archer interlock aborts releases using true range/state.
- BA-7 violated (assigned formation positions); BR-3 deviation (two-argument `decide`); legacy `c4c_keepers`, `targets_dead`, `make_pass`, `make_shot`, `auto_substitutions` still run underneath. The trap covers only five Match methods and three Policy methods.
- Ingress rejections (`infeasible`, `unknown_target`) are derived from true state and fed back as own feedback.
- The sprint's G1 is not the governed 100-seed matrix. Codex's `c083ae9` is.

## What is genuinely valuable
A working end-to-end skeleton on the real engine, honest limitation files, reproducible evidence, and a registry of every primitive. This is the right shape to deepen module by module.
