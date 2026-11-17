# OWNER BRIEFING

1. Accomplished: RB-2 corrections F1–F14 and RB-2.1 corrections R2-1–R2-3 are IMPLEMENTED and TESTED on `codex/rulebook-2`. Own-flight provenance now survives an opponent's redirect without changing the F2 shot-deflection ruling, and failed carry attempts are measurable.
2. Native now defaults every Rulebook runner and validation path to the working-canon banded basis: carry5; throws2/3/4; half goal1; full-goal award3; own goal2. Flat scoring is rejected for current measurement. Reports provide shot-only attempts, goals, points and points per attempt by band, plus independent carry counters.
3. Unimplemented or unproven: no RB-2 full match was run. RT3, RT6, RS6, RA2, RA4 and RO6 remain forced-scenario evidence only; no final-source RB-1 full match reached overtime. Natural review calls do not demonstrate reversal because natural evidence always records `called == actual`; only forced-call hooks exercise wrong-call reversal. Anatomical strike panels and inherited placeholders remain unchanged.
4. Blocking: none. Existing RB-1 match evidence shows a rules-outcome concentration that must be stated plainly: penalty awards are about78% of all points and about two thirds of arrows are illegal. RB-2 corrects classification/reporting but does not claim that those distributions are improved.
5. Recommended action: Claude independently reviews the focused diff and DreLen decides acceptance. If further match evidence is wanted, authorize an RB-2 budget explicitly; do not reinterpret the retained RB-1 full-match artifacts as RB-2 results.

RB-2 was DESIGN COMPLETE in the change request. It is now IMPLEMENTED and TESTED. It is not ACCEPTED until DreLen accepts it. No gameplay-quality, balance or emergence claim is made.

Validation: `292 passed, 23 subtests passed` in the complete `b1 native` suite; `95 passed` in the focused Rulebook suite. All 427 frozen B0 blobs verify, and `b1/core.py`, `b1/runtime.py`, `b1/g1.py`, and `native/cognition.py` are byte-identical to the RB-1 base. The banded 100-step replay matched serial, two parallel workers and M2-absent execution with trace `936c588ffec65c3a77362d67b31a12ea4b5e086536dd53df1d59eee075027d93` and state `9381cfee32ce7ef5ef9d9ba854a29175be62f9eb62bba404ceb0867e2a456239`. The bounded blocker run passed 5,375 live ms and reached 151,963 live ms without a restart stall.

## Corrections

| Finding | Result | Evidence |
|---|---|---|
| F1/F2/R2-1 own goal and deflection | A release-only team marker survives touches and clears on acquire/award. Its flight entering its releasing team's goal is an own goal worth2, even after an opponent redirect. A shot entering the defending team's goal after a defender deflection remains an ordinary shooter-team goal. | `test_interception_carry_is_not_stale_own_goal`; `test_own_team_pass_flight_redirected_by_opponent_into_own_goal_is_own_goal_two`; `test_defender_deflection_of_shot_is_ordinary_shooter_goal` |
| F3 full-goal award | Period4/OT award is3 under the required banded basis | `test_bands_and_carry_own_awards` |
| F4 goal-line toss timeout | Turnover scrimmage is spotted5m into field | `test_goal_line_toss_timeout_restarts_five_metres_out` |
| F5 defender hold | Defence minor: count-1, or award at0 | `test_defender_noncarrier_hold_is_defence_minor_and_offside_no_award` |
| F6/R2-2 counters | `shot_bands` excludes passes/restarts; `carry_attempts`, `own_goals`, and `release_ledger` are separate. A carry attempt is first controlled field-carrier entry strictly inside the attacked20m zone, once per control; a carry that scores without a prior observed entry records its attempt at the goal. | scoring tests, including `test_failed_carry_attempt_counts_once_on_first_entry_inside_twenty_metres`, and bounded report output |
| F7 evidence wording | Six named matrix rows say forced scenario only; no final-source full match reached overtime | `RB1_RULE_MATRIX.json` |
| F8 distribution disclosure | About78% of points were penalty awards; 532/818 recorded arrows (65.0%) were illegal in the six unique RB-1 validation seeds | retained RB-1 evidence, read only |
| F9 ruling publication | One authority goal/no-goal ruling per natural goal event | `test_goal_publishes_one_official_ruling_and_shot_counter_excludes_passes` |
| F10 natural review | Natural evidence always has `called == actual`; disagreements come only from forced test hooks | `test_natural_review_evidence_always_calls_actual_state` |
| F11 RO1 | Matrix points to engine `rb_review` path | `test_wrong_goal_threshold_and_corrected_restart` |
| F12 arrow speed | Config stores `arrow_speed:250.0`; no player-speed ratio fields | `test_arrow_speed_is_stored_as_fixed_value_not_ratio` |
| F13 quota reset | Possession change resets only the opposing Archer newly eligible against the ball-owning team | authority and Archer turnover tests |
| F14 check output | `check_replay` and `reproduce_blocker` default to the OS temporary directory | `test_check_tools_default_to_temp_not_committed_evidence` |

## Configuration and reporting

- Active configuration: `native-rb/2`, banded only, digest `383e127fa59b439efb51cce2fbc42351beb9e01e8f94bf28d5af70274b07c1f5`.
- Output tables: `shot_bands` includes attempts, goals, points, success rate and points per attempt; `carry_attempts` reports the same measures independently, including unsuccessful zone entries; `own_goals` and `release_ledger` remain separate.
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
