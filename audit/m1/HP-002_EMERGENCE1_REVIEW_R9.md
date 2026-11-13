# HP-002 — Review R9 of EMERGENCE-1 (branch experiment/emergence-1, head 761dca5)
Claude, 2026-11-13. Experiment evidence only; nothing accepted; do not merge.

## OWNER BRIEFING
1. **Accomplished.** The full loop works and reproduces: parametrized athletes, belief-driven positioning (the `home` grid is gone), tournament harness, search, held-out test. I reproduced 110 of 111 tests (the one failure is the known B0 inventory guard), six held-out matches with identical trace and state hashes, the 19-of-20 paired result, and its p-value (exact sign test 42/2^20 = 0.00004).
2. **What B1 can do now.** Run paired, side-swapped tournaments in parallel and search team parameters. Evolved parameters beat the baseline on held-out seeds: 19 of 20 pairs.
3. **The finding is not usable as an answer yet.**
   - **Scoring confound.** The sprint ran before the flat-scoring requirement existed, so it used the B0 table: inner release 3, release 2, outside 1, carry 4. 76 of the evolved team's 82 held-out goals are `inner_release` (3 points). Across all 460 matches: 1,142 inner-release goals, 224 outside, 89 inside, 12 carries. Under your flat 2/2/2/2 the table changes the search's reward, so the search must be rerun. Goal counts (evolved 82 vs baseline 17) suggest part of the advantage would survive, but that is not shown.
   - **Single opponent.** The final test is evolved vs the fixed baseline only. A team that never passes beating a team that passes badly may be exploiting this baseline, not finding good play.
   - **Bounds saturated.** The evolved pass bias sits at its lower bound (-6.0) and the pull toward the ball at its upper bound (3.0): the search was limited by the allowed range, not by the game.
   - **Passes are crippled by the build.** One fixed pass speed, no loft, interception and out-of-bounds losses. "Never pass" therefore mostly says passing is poorly implemented. The sprint's own reading agrees and logs it as an exploit candidate (X-4).
   - **No structure emerged:** width, depth and spacing differ by under 10%; no formation, roles or pass network.
4. **Blocking.** Scoring profile, opponent pool, parameter bounds, and the pass physics. The independent review's failed item (the decision record keeps only the chosen position, so a positioning decision cannot be re-derived) should be fixed before relying on boundary claims.
5. **Recommended action.** Rerun the search under flat 2/2/2/2 with wider bounds and a cross-evaluation (evolved vs earlier generations and a hand-set pass-first vector). That is a small change plus compute; it does not need a new large sprint. Pass speed and loft as athlete choices are Codex's engineering item.

## Verified by me
- `pytest b1`: 1 failed, 110 passed, 23 subtests (225 s); the failure is the known `test_frozen_B0_file_identity`.
- Held-out seeds 9000-9002, baseline vs evolved both sides: all six matches match the committed trace_hash and state_hash and scores.
- Pairs from `heldout.jsonl`: evolved better 19, worse 1, tie 0.
- Scoring: `heldout.jsonl` goals by method per label (above); the exploit log lists "carry value 4"; match goals by method for the whole run: inner_release 1142, outside_release 224, inside_release 89, own_goal 47, carry 12.
- Not re-run: the 392-match search, the symmetry check, the full-length sample (4 pairs).

## Notes on the sprint's own report
- Honest throughout: it states nothing is accepted, labels the "never pass" result as exploit-candidate X-4, and lists engine limits and deviations. No overclaiming found.
- X-1: zone violations in 143 of 460 matches (571 `zone_expiry` fouls, 264 `zone_unmarked`) are high and need a rules/engine look before any search result is trusted.
- X-5: 47 own-goal scores across 460 matches; Keeper own-goal rule KP-OG is not implemented in B1.
- With identical parameters side A won 13 of 20; rosters differ per side. Side-swapped pairs cancel it.
- Parameters are per team, not per role, and hand-set option values still sit under the searched biases.

## Carry-forward for the next run (Emergence-1b)
1. Flat scoring 2/2/2/2 through an explicit profile setting, asserted and logged in every row (prompt section 2c).
2. Wider parameter bounds; stop-at-bound reported.
3. Cross-evaluation: evolved vs earlier-generation winners and vs a hand-set pass-first vector; report whether never-pass survives.
4. Record candidate scores of positioning decisions so they can be re-derived.
5. Merge Codex's ownership enablers and make pass speed and loft athlete choices before the large run.
