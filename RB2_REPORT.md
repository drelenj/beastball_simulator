# OWNER BRIEFING

1. Accomplished: RB-2 corrections F1–F14 are IMPLEMENTED and TESTED on `codex/rulebook-2`. The two 16 Nov owner rulings are encoded: a defender's shot deflection is an ordinary shooter-team goal, and a defender's non-carrier hold is a defence minor.
2. Native can now classify own goals from current holder/releaser state, award flat late-period defensive minors correctly, place goal-line toss timeouts5m out, publish one goal ruling, report shot-only bands and independent carries, retain only the dormant Archer quota across turnovers, and run check tools without overwriting committed evidence.
3. Unimplemented or unproven: no RB-2 full match was run. RT3, RT6, RS6, RA2, RA4 and RO6 remain forced-scenario evidence only; no final-source RB-1 full match reached overtime. Natural review calls do not demonstrate reversal because natural evidence always records `called == actual`; only forced-call hooks exercise wrong-call reversal. Anatomical strike panels and inherited placeholders remain unchanged.
4. Blocking: none. Existing RB-1 match evidence shows a rules-outcome concentration that must be stated plainly: penalty awards are about78% of all points and about two thirds of arrows are illegal. RB-2 corrects classification/reporting but does not claim that those distributions are improved.
5. Recommended action: Claude independently reviews the focused diff and DreLen decides acceptance. If further match evidence is wanted, authorize an RB-2 budget explicitly; do not reinterpret the retained RB-1 full-match artifacts as RB-2 results.

RB-2 was DESIGN COMPLETE in the change request. It is now IMPLEMENTED and TESTED. It is not ACCEPTED until DreLen accepts it. No gameplay-quality, balance or emergence claim is made.

Validation: `290 passed, 23 subtests passed` in the complete `b1 native` suite; `93 passed` in the focused Rulebook suite. All 427 frozen B0 blobs verify, and `b1/core.py`, `b1/runtime.py`, `b1/g1.py`, and `native/cognition.py` are byte-identical to the RB-1 base. The 100-step replay matched serial, two parallel workers and M2-absent execution with trace `3538d716077650608109acbe1ad6f0e244e9d4e165ce76535e4a2c6492d76175` and state `f3012eae049083fb7d101c9546ecbc028f8dfb9d221da51c470bf207c63278e2`. The bounded blocker run passed 5,375 live ms and reached 151,963 live ms without a restart stall.

## Corrections

| Finding | Result | Evidence |
|---|---|---|
| F1/F2 own goal and deflection | Own goal uses current defending holder or deliberate releaser; stale release state clears on acquire/award; defender shot deflection remains shooter-team goal | `test_interception_carry_is_not_stale_own_goal`; `test_defender_deflection_of_shot_is_ordinary_shooter_goal` |
| F3 flat full award | Period4/OT award is2 flat,3 banded | `test_flat_period_four_full_goal_award_is_two` |
| F4 goal-line toss timeout | Turnover scrimmage is spotted5m into field | `test_goal_line_toss_timeout_restarts_five_metres_out` |
| F5 defender hold | Defence minor: count-1, or award at0 | `test_defender_noncarrier_hold_is_defence_minor_and_offside_no_award` |
| F6 counters | `shot_bands` excludes passes/restarts; `carry_attempts`, `own_goals`, and `release_ledger` are separate | scoring tests and bounded report output |
| F7 evidence wording | Six named matrix rows say forced scenario only; no final-source full match reached overtime | `RB1_RULE_MATRIX.json` |
| F8 distribution disclosure | About78% of points were penalty awards; 532/818 recorded arrows (65.0%) were illegal in the six unique RB-1 validation seeds | retained RB-1 evidence, read only |
| F9 ruling publication | One authority goal/no-goal ruling per natural goal event | `test_goal_publishes_one_official_ruling_and_shot_counter_excludes_passes` |
| F10 natural review | Natural evidence always has `called == actual`; disagreements come only from forced test hooks | `test_natural_review_evidence_always_calls_actual_state` |
| F11 RO1 | Matrix points to engine `rb_review` path | `test_wrong_goal_threshold_and_corrected_restart` |
| F12 arrow speed | Config stores `arrow_speed:250.0`; no player-speed ratio fields | `test_arrow_speed_is_stored_as_fixed_value_not_ratio` |
| F13 quota reset | Possession change resets only the opposing Archer newly eligible against the ball-owning team | authority and Archer turnover tests |
| F14 check output | `check_replay` and `reproduce_blocker` default to the OS temporary directory | `test_check_tools_default_to_temp_not_committed_evidence` |

## Configuration and reporting

- Flat config digest: `3b00233cf337951415fe5ccfe1e8cf54c9eed2a7743c3ea6d129c748f4fb685c`
- Banded config digest: `1339a6ede686a0bae08fa5e2f961089b9fcbed464f53f5974fcafe5d78599fab`
- Output tables: `shot_bands`, `carry_attempts`, `own_goals`, `release_ledger`.
- Existing `native/rulebook/evidence/` files were not rewritten. Old RB-1 `bands` data include passes and restarts and are historical release-ledger evidence, not RB-2 shot-attempt counters.

## Roster handoff

The owner-supplied workbook at `d85e790` was inspected read-only. It has 712 unique athletes; height spans1.831–3.447m, mass91.7–753.3kg, arm span1.792–3.584m, and standing reach2.285–4.319m. The next attribute step must widen the old body envelope and avoid applying size twice because height/physique already influence the supplied nine ratings. RB-2 makes no roster or cognition change; details are in `RB2_ROSTER_HANDOFF.md`.

## Reproduction

```bash
git switch codex/rulebook-2
.venv/bin/python -m pytest -q native/rulebook
.venv/bin/python -m pytest -q b1 native
.venv/bin/python -m native.rulebook.check_replay
.venv/bin/python -m native.rulebook.reproduce_blocker
```

The two check commands write under the operating-system temporary directory by default. An explicit `--out` may be supplied when a caller intentionally wants another path.
