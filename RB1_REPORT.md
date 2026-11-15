OWNER BRIEFING
1. Accomplished: resolved the owner-revoked pre-live marking foul without replacement, retained Keeper-zone5m marking/readiness/watchdog, completed the execution/review gaps and fixed validation defects. Rules/engine changes are IMPLEMENTED and TESTED on source881d212; nothing is ACCEPTED.
2. Native can complete full RB matches with clocks/breaks/ends/timeouts, substitutions/forced injuries, shorthanded discipline, canonical arrows, optional bands and recorded-state review. Six unique final-source seeds finish; seed2 serial/parallel hashes agree.
3. Unimplemented/unproven: anatomical strike panels remain PLACEHOLDER; no stochastic injury/fatigue model, new athlete policy, autonomous review policy, FAB-1 or M2 content is added. Forced scenarios establish rules not encountered naturally in every match. Historical Native procedural/body-boundary placeholders remain documented.
4. Blocking: none observed in final validation. The former seed2 period-reset failure is fixed; failed/stopped attempts remain logged. Budget17/20 including conservative reservations; no further batch is needed or planned.
5. Recommended: Claude independently reviews the source/evidence, then DreLen decides acceptance. Do not infer gameplay quality from this functional validation.

Branch:codex/rulebook-1. Engine/rules source:881d212e372b312d5e0fec73653cfc6a7f6876b1. Native v0/2 base:a1b131379845322bbc9970ad667a6d68dec10dd7. Report/evidence commit follows this source freeze.

Owner canon update:2026-11-15 pre-live marking foul/witness/sanction/tests are removed, without a replacement. marking_distance=5 remains for Keeper-zone defender residence. See the committed owner record; no new sport rule was invented.

Validation:282 tests +23 subtests passed in651.40s;85 RB cases +197 existing cases. All427 frozen B0 blobs pass. b1/core.py/runtime.py/g1.py and native/cognition.py are byte-identical to the requested base. Every full-run athlete command links to an intent; no kick appears; per-step/end invariants pass.

Seed1 bounded4000-step regression reaches146329 live ms; blocked=false. Repeated stopped-clock foul test warns/corrects the offender without repeated discipline or retakes and then snaps. Dead-progress watchdog remains enabled.

Full validation seeds (source881d212):

| Seed | breaks | timeouts | minors | majors | exclusions | DQs | quota_resets | reviews | injuries | substitutions | Restart completion | Runtime s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 3 | 8 | 94 | 8 | 43 | 17 | 591 | 0 | 0 | 43 | 1.000 | 667.87 |
| 6 | 3 | 8 | 127 | 5 | 51 | 23 | 551 | 0 | 0 | 49 | 1.000 | 649.188 |
| 7 | 3 | 8 | 121 | 20 | 66 | 25 | 505 | 0 | 0 | 62 | 1.000 | 675.809 |
| 8 | 3 | 8 | 146 | 10 | 63 | 27 | 574 | 0 | 0 | 58 | 1.000 | 375.462 |
| 9 | 3 | 8 | 137 | 7 | 58 | 25 | 567 | 0 | 0 | 54 | 1.000 | 378.23 |
| 10 | 3 | 8 | 136 | 11 | 62 | 26 | 564 | 0 | 0 | 57 | 1.000 | 358.146 |

All restart records close by release or an explicit timeout/retake/end-of-play status; completion ratio is not release ratio. Wall runtimes include concurrent match/suite CPU load, not a standalone benchmark. Full artifacts retain the status breakdown and release ratios.

Band release counters, teams combined; A/G=attempts/goals with success rate. Per-team values are in each full match JSON. Passes/bounces/restart throws are counted once alongside shots; carry/own are separate. No shot-only or quality interpretation is implied.

| Seed | <10m A/G | 10–20m A/G | >=20m A/G | Carry A/G | Own A/G |
|---|---:|---:|---:|---:|---:|
| 2 | 7/3 (42.86%) | 42/8 (19.05%) | 1009/0 (0.00%) | 0/0 (0%) | 4/4 (100.00%) |
| 6 | 8/3 (37.50%) | 44/7 (15.91%) | 1009/1 (0.10%) | 0/0 (0%) | 6/6 (100.00%) |
| 7 | 2/1 (50.00%) | 33/7 (21.21%) | 961/0 (0.00%) | 0/0 (0%) | 4/4 (100.00%) |
| 8 | 2/2 (100.00%) | 39/5 (12.82%) | 1055/1 (0.09%) | 0/0 (0%) | 4/4 (100.00%) |
| 9 | 2/0 (0.00%) | 23/5 (21.74%) | 1015/1 (0.10%) | 0/0 (0%) | 0/0 (0%) |
| 10 | 6/0 (0.00%) | 43/8 (18.60%) | 1068/2 (0.19%) | 0/0 (0%) | 1/1 (100.00%) |

Determinism:seed2 serial and parallel trace/state hashes agree; serial runtime 708.105s. Fixed final-source hashes:

Seed2 trace ea8c54b667afcbcb34f4fd111b5e9b5a94094b8b90ca098aa6fc43253989c066
Seed2 state 25b26381e3b71e42eebdebb851b823487eb789493ef1010bb7d64cc92033ecdf

Seed6 trace c120c6534113afcfde64ebb841ddd487703e89cd1a730c5a435ed9aebd7ea16d
Seed6 state a47e37ee03c3861222c65027ccf4df5795d6eec8f3eebb0beeaa9af0e52e12ab

Seed7 trace 43d0c8130f0c512ec6c0a8a45544341aaee9b97d17534c4e8a42639d6f2e84ae
Seed7 state 86f7dce94346d42f2e9ead25b43aeab5fc16911da8549a56da91e692e8166b35

Seed8 trace 3e980753d30da5ddeaa6de6b222840e84b8bfb269653078de899db41ece1699a
Seed8 state 4fb86c9ab01c3e53c3139392fff60d54054199a6073d8118650fb6e4cf7f3d81

Seed9 trace cff04fecc1c0e4f487623b7145ce5cae9f190ca147dfddde16d1c1e27831c919
Seed9 state 88e3f1b56434b1d327bed76eb70344a8405c19c4bfeb7982df1bca4c25b46882

Seed10 trace 8833a71252a4e44710c48c1b2fd0b29bbdd02054be4a72a01c0d30c315332a07
Seed10 state 383de354d3be0a7c9c61e634e0181272b6b18ebc8caa5029a3578681fc63bfb5

Flat default config digest:d1e04019fe9851d718c0ac116c109dd2e201f51202bfbb36367330dc63239e16
Banded switch config digest:9411f3771f349f8053eee3faba4e4e6c43455210cfafcc8d7a9af86a52b82127

Native v0/2 preservation:two full seed1 runs retain config f31b44a1eb787f14c9d606be74fa40658c6b7b9772ee1e882b075b856edc3035, trace3840682e22692e597bc1419aa298337201e86db2d35f7208c5c9e50e9a99a142, state411abb0a4bab0b812bc5e2e010f03d22f726ff32fdcebcb7df6c3a5beac8aec9. M2 null/absent100-step replay agrees; no communication benefit is claimed.

Attempt history (all count against20; reservations are conservative):
- 1:seed1, native-v0/2, passed, V1 baseline preservation replay.
- 2:seed1, native-v0/2, passed, V1 final engine-integration preservation replay.
- 3:seed1, native-rb/1, passed, serial-seed1-0.
- 4:seed1, native-rb/1, passed, final-serial-seed1-0.
- 5:seed1, native-rb/1, aborted_engine_fix, rb-final-seed1-0.
- 6:seed1, native-rb/1, aborted_engine_fix, rb-final-seed1-1.
- 7:seed2, native-rb/1, failed, rb-final-seed2-2.
- 8:seed3, native-rb/1, aborted_engine_fix, rb-final-seed3-3.
- 9:seed4, native-rb/1, aborted_engine_fix, rb-final-seed4-4.
- 10:seed5, native-rb/1, aborted_engine_fix, rb-final-seed5-5.
- 11:seed2, native-rb/1, passed, rb-verified-seed2-0.
- 12:seed2, native-rb/1, passed, rb-verified-seed2-1.
- 13:seed6, native-rb/1, passed, rb-verified-seed6-2.
- 14:seed7, native-rb/1, passed, rb-verified-seed7-3.
- 15:seed8, native-rb/1, passed, rb-verified-seed8-4.
- 16:seed9, native-rb/1, passed, rb-verified-seed9-5.
- 17:seed10, native-rb/1, passed, rb-verified-seed10-6.

A previous full seed2 failed KeyError(A11): a former Archer field substitute lacked a period-reset entry. The all-roster reset cache and forced substitution/break test fix it. Other preliminary runs were stopped for the illegal-arrow sanction correction. That correction keeps arrow breaches minor even at contact-protected targets; physical contact remains major. Frozen-body swept contact, projectile-team freeze quotas, head evaluation and stale restart claims also have real-engine regressions. Test disk exhaustion from legacy/tmp/pk_* copies was cleaned up; raw failure logs are retained. A pre-freeze overlapping suite run is retained separately; final results above use the frozen source.

Exact reproduction from source881d212 (its pre-run budget permits the full command; the delivered post-run budget intentionally refuses another seven-run batch):
```bash
.venv/bin/python -m pytest -q b1 native
.venv/bin/python -m native.rulebook.reproduce_blocker
.venv/bin/python -m native.rulebook.check_replay
.venv/bin/python -m native.rulebook.validate_matches --seeds 2 6 7 8 9 10 --label rb-verified --workers 3 --serial-replay
```

Conformance matrix (exact collected references):

| Rule | Status | Test |
|---|---|---|
| RT1 Regulation/OT breaks, end exchange and Hunt clock activation | IMPLEMENTED+tested | native/rulebook/test_clocks.py::test_real_break_clock_ends_and_hunt |
| RT2 Timeout freezes both clocks and shifts restart deadlines | IMPLEMENTED+tested | native/rulebook/test_clocks.py::test_timeout_freezes_both_clocks_and_restart_deadline |
| RT3 Tackle retains play clock; snap window runs only above10s | IMPLEMENTED+tested | native/rulebook/test_clocks.py::test_real_tackle_keeps_play_clock_and_snap_window_runs_only_above_ten |
| RT4 Ratified deterministic timeout policy, budgets and no sudden-death timeout | IMPLEMENTED+tested | native/rulebook/test_authorities.py::test_timeout_triggers_and_resources |
| RT5 Each simultaneous timeout trigger used once | IMPLEMENTED+tested | native/rulebook/test_authorities.py::test_each_simultaneous_timeout_trigger_can_be_consumed_once |
| RT6 Whole300s first OT; full/half/award scores end sudden death | IMPLEMENTED+tested | native/rulebook/test_clocks.py::test_whole_first_overtime_then_any_score_sudden_death |
| RS1 Provisional release bands and exact10m/20m boundaries | IMPLEMENTED+tested | native/rulebook/test_scoring.py::test_real_release_band_and_goal |
| RS2 Flat default, carry5 in banded, own goal2 including Keeper | IMPLEMENTED+tested | native/rulebook/test_scoring.py::test_flat_carry_banded_carry_and_keeper_own |
| RS3 Full award3 in P4/OT and half1 before P4 | IMPLEMENTED+tested | native/rulebook/test_authorities.py::test_bands_and_carry_own_awards |
| RS4 Restart throws recorded once at actual release | IMPLEMENTED+tested | native/rulebook/test_scoring.py::test_restart_throw_is_an_attempt_once_at_actual_release |
| RS5 Keeper cannot score at opposing goal; official no-goal ruling | IMPLEMENTED+tested | native/rulebook/test_scoring.py::test_keeper_opponent_goal_is_no_goal_ruling |
| RS6 Bounced shot uses original release-distance band | IMPLEMENTED+tested | native/rulebook/test_scoring.py::test_bounced_shot_keeps_original_release_band |
| RD1 Major shorthanded120s, score-independent; second-major DQ delayed cover | IMPLEMENTED+tested | native/rulebook/test_discipline.py::test_real_exclusion_shorthanded_until_dead_after_window |
| RD2 Fourth-minor60s/fifth DQ; injury replacement exception | IMPLEMENTED+tested | native/rulebook/test_discipline.py::test_minor_ladder_and_injury_exclusion_exemption |
| RD3 Delay warning then minor; kick minor; major goal-line award | IMPLEMENTED+tested | native/rulebook/test_discipline.py::test_delay_warning_kick_and_major_goal_line |
| RD4 Defensive holding count+1; procedural offside no half-goal | IMPLEMENTED+tested | native/rulebook/test_discipline.py::test_defensive_hold_count_plus_and_offside_no_award |
| RD5 Intentional head/neck/trip/off-ball tackle; striking/whistle/frozen/Keeper breach major | IMPLEMENTED+tested | native/rulebook/test_discipline.py::test_rule_layer_major_classification |
| RD6 Unintentional head minor plus mandatory evaluation | IMPLEMENTED+tested | native/rulebook/test_discipline.py::test_unintentional_head_is_minor_and_requires_evaluation |
| RD7 Attacker-zone expiry restart at20m line; Keeper-zone marking remains5m | IMPLEMENTED+tested | native/rulebook/test_boundary.py::test_zone_residence_restart_line |
| RD8 Exclusion cannot be bypassed by setup/empty-slot/role-change admission | IMPLEMENTED+tested | native/rulebook/test_substitutions.py::test_exclusion_cannot_be_bypassed_with_empty_slot_or_role_change |
| RD9 Physical-kernel Keeper contact and major goal-line restart release | IMPLEMENTED+tested | native/rulebook/test_execution.py::test_physical_kernel_contact_on_protected_keeper_emits_major |
| RA1 Ratio250m/s, own-half legality,15 arrows, illegal release spends, swept collision | IMPLEMENTED+tested | native/rulebook/test_archery.py::test_speed_quota_own_half_illegal_spends_and_no_tunnelling |
| RA2 Recovery admission at intent and execution, including queued release/movement | IMPLEMENTED+tested | native/rulebook/test_execution.py::test_recovery_execution_blocks_queued_release_and_forward_zone_entry |
| RA3 Captured red/amber observation cannot read poisoned live truth | IMPLEMENTED+tested | native/rulebook/test_archery.py::test_status_view_is_captured_not_live_truth |
| RA4 Five actual freezes then cap; turnover reset and amber phase | IMPLEMENTED+tested | native/rulebook/test_archery.py::test_five_actual_freezes_then_cap_and_captured_amber |
| RO1 Seven authority crew and stored-evidence review ledger | IMPLEMENTED+tested | native/rulebook/test_authorities.py::test_review_tolerance_and_stored_evidence_only |
| RO2 Strict>5cm, corrected restart, won/lost challenge resources | IMPLEMENTED+tested | native/rulebook/test_review.py::test_wrong_goal_threshold_and_corrected_restart |
| RO3 Eligible boundary scope and Keeper binary reversal restores exclusion | IMPLEMENTED+tested | native/rulebook/test_review.py::test_boundary_review_scope_and_keeper_binary |
| RO4 Wrong goal outside semicircle corrects to boundary toss | IMPLEMENTED+tested | native/rulebook/test_review.py::test_reversed_wrong_goal_outside_semicircle_is_toss_to_other_team |
| RO5 No-goal review can restore Keeper own goal | IMPLEMENTED+tested | native/rulebook/test_review.py::test_review_no_goal_reversed_to_keeper_own_goal |
| RO6 Review during breaks and after final; restore corrected result | IMPLEMENTED+tested | native/rulebook/test_review.py::test_review_reverses_wrong_goal_during_break_or_after_final |
| RE1 Strike panel anatomical outer-thigh witness | PLACEHOLDER | native/rulebook/test_archery.py::test_freeze_cap_panel_recovery_and_turnover |
| RE2 Captured amber indicator and no gameplay effect from lighter kit metadata | IMPLEMENTED+tested | native/rulebook/test_archery.py::test_five_actual_freezes_then_cap_and_captured_amber |
| RI1 Dead-only unlimited return substitutions; Archer outside field limit | IMPLEMENTED+tested | native/rulebook/test_substitutions.py::test_field_limit_archer_exempt_dead_only_and_returns |
| RI2 Forced injury stops clocks, immediate replacement, no timeout charge | IMPLEMENTED+tested | native/rulebook/test_substitutions.py::test_injury_stops_clocks_and_immediate_cover |
| RI3 Head evaluation period exclusion and named reserve Keeper | IMPLEMENTED+tested | native/rulebook/test_substitutions.py::test_head_evaluation_and_named_keeper |
| RI4 No reserve: field-player Keeper fallback | IMPLEMENTED+tested | native/rulebook/test_substitutions.py::test_keeper_fallback_without_reserve |
| RI5 No random injury model; forced head return next period | IMPLEMENTED+tested | native/rulebook/test_authorities.py::test_head_evaluation_next_period_and_injury_no_randomness |
| BOUND1 Extended view/belief JSON replay and hidden-state poison | IMPLEMENTED+tested | native/rulebook/test_boundary.py::test_extended_view_replay_and_poison |
| DET1 RB deterministic short replay | IMPLEMENTED+tested | native/rulebook/test_boundary.py::test_short_integrated_replay |
| RT7 Consecutive legal timeouts do not cause a false restart watchdog failure | IMPLEMENTED+tested | native/rulebook/test_clocks.py::test_consecutive_legal_timeouts_do_not_trigger_restart_watchdog |
| RD11 Repeated dead-ball foul resolves without repeated exclusions/retakes | IMPLEMENTED+tested | native/rulebook/test_boundary.py::test_repeated_dead_ball_foul_corrects_offender_without_retake_loop |
| RD12 Actual swept entry into frozen body is a major | IMPLEMENTED+tested | native/rulebook/test_execution.py::test_actual_swept_body_contact_with_frozen_player_is_major |
| RO7 Lost halftime review consumes old-half resources only | IMPLEMENTED+tested | native/rulebook/test_review.py::test_lost_review_in_halftime_costs_old_half_resources_only |
| RD13 Major goal-line scrimmage can snap | IMPLEMENTED+tested | native/rulebook/test_execution.py::test_major_goal_line_scrimmage_can_release |
| RA5 Illegal arrow is minor even at frozen, immune or Keeper target | IMPLEMENTED+tested | native/rulebook/test_archery.py::test_illegal_arrow_is_minor_even_if_target_has_contact_protection |
| RA6 Panel-hit freeze quota belongs to actual projectile team | IMPLEMENTED+tested | native/rulebook/test_archery.py::test_physical_friendly_panel_hit_spends_shooting_team_freeze_quota |
| RI6 Former Archer can substitute into field role and survive period reset | IMPLEMENTED+tested | native/rulebook/test_substitutions.py::test_former_archer_field_substitution_survives_period_reset |

QUESTIONS_FOR_OWNER.md (scope and recorded placeholders):

Scope notice: original sections describe historical Native v0/2. The Rulebook1.0 section below applies only to native-rb/1 and records its current blocker and limits.

OWNER BRIEFING
1. Native build uses the following smallest working PLACEHOLDERs where implementation or canon detail is incomplete.
2. These are explicit defaults, not accepted canon or evidence of good play.
3. Historical Native v0/2 questions did not block that baseline. The RB section records resolved canon updates and remaining placeholders. Acceptance remains the owner's decision.

| ID | Question / replaceable default | Class and current handling |
|---|---|---|
| Q-HUNT-1 | Centre-circle radius and setup distances are not specified numerically in the build prompt. | CANON detail; PLACEHOLDER keep restarts_v1's 5 m radius, contestants approach physically from legal initial scatter. No assigned formation or role-ranked contestant. |
| Q-HUNT-2 | Exact clock activation within the First Hunt is not specified in the authoritative prompt. | CANON detail; PLACEHOLDER clock runs in the opening phase, including approaches; false start retakes and no Archer until whole ball exits circle. |
| Q-ZONE-1 | Unmarked defenders cannot remain indefinitely, but the permitted grace interval is not stated. | CANON detail; PLACEHOLDER 5 s unmarked residence, inherited duration; marked defenders exempt, Keepers exempt. |
| Q-FLIGHT-1 | Maximum shot finishing-flight duration is not stated. | CANON detail; PLACEHOLDER 10 s safety tail, normally ends on ground/control/out/goal. Only shots get an exception. |
| Q-BOUNDARY-1 | Exact anatomical witnesses for every touching body part need more motor integration. | ENGINEERING; PLACEHOLDER ground body-cylinder envelope with airborne exemption. Native v1 replaces it with support/anatomical witnesses. Goal whole-ball test is separate. |
| Q-COVER-1 | If simultaneous exclusions temporarily leave fewer than 12 eligible among 22, does "available" include excluded athletes? | CANON edge case; PLACEHOLDER excluded athletes are unavailable until their exclusion expires, so fewer than 12 currently eligible causes a forfeit. No unavailable athlete is fielded to hide this case. |
| Q-SIMULT-1 | Simultaneous offsetting minor fouls outside the three specified exact ties have no explicit procedure. | CANON detail; PLACEHOLDER retain B0 neutral offset: record each sanction and restart with existing possession/count, no automatic major classification. |
| Q-HELD-1 | Unresolved physical joint-ball control has no resolution duration in the prompt. | CANON detail; PLACEHOLDER retain B0 one-second held-ball reset/alternating scrimmage; Hunt joint control retakes without a penalty. |
| Q-SENSOR-1 | Native sensor cadence/noise constants are not canon. | ENGINEERING; PLACEHOLDER immutable delayed/noisy cone/occlusion observations with independent per-athlete RNG, no true fallback. Claude replaces/takes ownership. |
| Q-THROW-1 | Full THROW_SPLIT mechanics and arbitrary-speed error calibration are not yet ported. | ENGINEERING; PLACEHOLDER explicit intent speed/height, drag-aware arc, 60-degree moving-release bound, uniform accuracy error. Do not claim full throwing_v1 equivalence. |
| Q-HAND-1 | Full voluntary off-ball hand-fight repertoire is not yet ported. | BEHAVIORAL/ENGINEERING; PLACEHOLDER retained incidental contact physics, intent-gated carrier wraps, no automatic random gripping. Native v1 adds PRISM-owned off-ball actions. |
| Q-CONTACT-1 | B0 automatic containment/descent choices used true-state tactical triggers. | ENGINEERING; disabled in Native. Motor may retain already admitted Keeper commitments; new semantic choices come from decide(). |
| Q-CATCH-1 | CATCH_V2 shared energy kernel is ported; automatic jump/hand-contest overlay is not installed. | ENGINEERING; PLACEHOLDER B0 simultaneous secure-contact handling plus shared threshold kernel. No second Keeper decider. |
| Q-BEHAVIOR-1 | Minimal Hunt claims, restart claims/alignment/wait/snap, dribble and cover policies need replacement. | BEHAVIORAL; PLACEHOLDER procedural decisions in the same view/belief/intent pipeline, canonical admission, no quality claim. Claude owns their later cognition replacements. |

Explicit DEFERRED: breaks, timeouts, Hunt penalties beyond false-start retake, standard scoring, fatigue, injury, rating development, adaptive learning, M2 plan/message content. No implementation of those deferred features is authorized by this baseline.

PH3 implementation limit (ENGINEERING, not a canon escalation): the current defender-marking exemption checks offensive field players. Keeper-as-marker coverage is not established by the conformance test. Native v1 must cover every offensive-player role permitted by the rule. This residence model remains PLACEHOLDER; the five-second attacker rule and field-player marking case are tested.

## Rulebook 1.0 / native-rb/1 scope (supersedes old defaults only for RB)

Breaks, timeout policy,>5cm review, shorthanded discipline, quotas and forced-injury/substitution mechanics are ratified for RB. They are not deferred in RB. Native v0/2 remains the historical profile above.

| ID | Class | Handling |
|---|---|---|
| RB-PH-1 | ENGINEERING placeholder | Period resets reuse initial legal scatter; no new formation. Added field-roster admission is procedural setup. Twelve non-Archer field-roster slots; the Archer is outside that limit;22 gameday players retained. |
| RB-PH-2 | Team setup placeholder | Reserve Keepers default to A13/B13. Eligible replacements use canonical ID order with named-reserve priority; fallback chooses an available field player. No ratings used. |
| RB-PH-3 | Equipment placeholder explicitly permitted | Torso/thigh cylinder-height band approximates strike panels. Outer/inner thigh cannot be distinguished. Lighter Archer kit is metadata only; no gameplay effect. |
| RB-PH-4 | Missing procedure detail | Fifth-minor DQ uses a60s replacement window; second-major DQ120s. These follow the respective foul-kind exclusion window. |
| RB-PH-5 | Missing procedure detail | A special defensive count+1 offence reuses the existing count1-to-turnover transition on overflow. No new tackle-count domain is invented. |
| RB-PH-6 | Missing review detail | A lost review with no timeout remaining consumes its challenge but does not create a negative timeout balance or future-half debt. |
| RB-PH-8 | Missing restart detail | Correcting a false goal while the recorded ball was still in bounds resumes by scrimmage for the recorded possessing team at the spot; a recorded out-of-bounds ball uses the corrected boundary restart. |
| RB-PH-9 | ENGINEERING ordering | Eligible simultaneous timeout triggers are consumed once each, team order A then B. No extra timeout is granted. |
| RB-PH-10 | Forced injury scope | No injury probability or recovery model is added. Ordinary forced injuries remain unavailable; head-evaluation players can return from the next period. |


RB-PH-11: inherited procedural illegal_release/otherwise unclassified legacy rule inputs currently default to minor adjudication. This is a labelled compatibility placeholder, not a newly ratified offence.
RB-PH-12: later sudden-death periods retain the inherited300s maximum period duration; any score ends them immediately. Their duration beyond the first overtime was not restated numerically in RB-1.

2026-11-15 owner update: RB-BLOCK-1 RESOLVED. Pre-live5m marking foul and its witness are REVOKED and removed with no replacement. Keeper-zone defender marking remains5m. Snap-readiness ordering remains. Repeated dead-ball foul retakes receive a procedural correction/warning without repeated stopped-clock discipline.

RB-PH-7 RESOLVED: recorded-evidence review now operates during period breaks and after final rulings; reversal restores prior state, and a lost halftime review charges the old half. No autonomous challenge policy is defined or invented.

No current canon question blocks RB integration. Remaining RB-PH defaults above are explicit implementation placeholders, not ratified additions.

RB-PH-13: band attempts retain the existing Native release-ledger convention: each deliberate shot/pass/bounce/restart release is counted once; carry and own-goal events have separate bands. Intent kind is retained so shot-only subsets can be extracted. The report labels these as release counters, not a quality metric.
