OWNER BRIEFING — FINAL INVENTORY
1. Native v0 is IMPLEMENTED and TESTED under the owner-amended A1–A8 gates. The pre-build inventory was committed first at 937c52b; the source inventory, final dispositions and engineering history follow.
2. Native PRISM 0 completes four periods of 600 seconds periods with uniform 0.70 ratings, explicit configuration, athlete intents, enforced possession and null M2. The first25 completed varied-seed results all pass.
3. Eleven placeholder groups and six deferred groups remain explicit. CATCH_V2, HAND_FIGHT and THROW_SPLIT are partial implementations, not full overlay equivalence. No quality result is claimed.
4. No engineering blocker remains. Canon details use the recorded placeholders; Claude review and DreLen acceptance are pending. Nothing is ACCEPTED.
5. Review simulation freeze ba568dc84299cc95f86eb83207e0533297569cd7 and the delivery commit, then accept or request changes. Follow ROADMAP_NATIVE_V1.md only after the appropriate entry gates.

The table inventories source evidence; current Native evidence is the 105-row rule matrix,197 passing tests plus23 passing subtests, full seed1 serial/null/absent replay and the selected 25 results. DreLen's 25-match amendment supersedes all historical50-match plans below. Historical failed/unfinished cohorts are retained and excluded from acceptance.


Engineering evidence

Branch: codex/native-v0. Simulation freeze: ba568dc84299cc95f86eb83207e0533297569cd7.
Inventory before build:937c52b; M2 merge4c5efd1 (source5c23fe8); profile mergeba92633 (sourcec339b01).
B0 at2abe497:427 frozen Git-blob hashes pass; accepted core.py/runtime.py/g1.py remain byte-identical to4b19719.
197 tests (123 B1,74 Native) and23 subtests pass in322.30s. Two existing packaging/null/harness tests reran and passed in6.27s; these are not additional unique tests. Harness config serialization was verified against an archived full-match output without rerunning a match.
Native match runner, cognition, perception, physical/rule adapters and config remain at the simulation freeze. Final Python packaging differences are harness result metadata and default soak seed-count25 only.

A1 TESTED: seed1 full2,400s serial/parallel trace and state hashes match.
A2 TESTED: forced whole300s first OT, later sudden death, full/half score endings, P4/OT full awards. Selected25 have no natural OT.
A3 TESTED:105 matrix rows;88 IMPLEMENTED+tested,11 PLACEHOLDER,6 DEFERRED.
A4 TESTED under owner amendment:25 full matches, zero crash/stall/invariant failure.
A5 TESTED: original B1 gates, view poison/JSON/intent provenance, no home grid/legacy layer/kick intent; ownership table below.
A6 TESTED: full seed1 null/plumbing-absent equality, including decisions; original M2 synthetic/order/capacity/serial-parallel tests.
A7 TESTED: manifest contains commit, full config/digest/readback,197 test nodes/results,25 trace/state hash pairs and per-match runtimes.
A8 TESTED: functional evidence only; no quality, balance, tactic or emergence result is claimed. Nothing is ACCEPTED.

Repository-wide historical collection at development revision1e7383c:444 collected,5 errors (block_test.py/rs_test.py are CLI scripts; two Playwright lab tests; absent results_v37/capability_table_v37.json). Retained log is excluded from the passing-suite claim. Preservation enumeration covers exactly the canonical427 paths; the frozen-path mutation regression still fails verification as required. No historical test was weakened.

Exact reproduction commands on Python3.12.14 / NumPy2.5.4 / pytest9.2.0 (instructions, not further runs):

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r native/requirements.txt
.venv/bin/python -m pytest -q b1 native
.venv/bin/python -m native.run --seed 1 --out /tmp/native-1a.json
.venv/bin/python -m native.run --seed 1 --out /tmp/native-1b.json
.venv/bin/python -m native.run --seed 1 --plumbing-absent --out /tmp/native-1absent.json
.venv/bin/python -m b1.match_run --profile legacy-b0 --seed 1 --telemetry-off
```

Native config is native-v0/2, profile native-v0:4x600s, first OT300s, play clock30s, goal radius/depth3m, strict zoneR20, platforms5m high/5m back, marking5m, arrows25/freezes5, freeze5s/immunity10s, direct-control500ms, uniform ratings0.70, M2null, no legacy layers/fatigue/injury/learning. Full physical assumptions/Pocket/body records and effective readback are in every match result and the manifest.

Config SHA-256: f31b44a1eb787f14c9d606be74fa40658c6b7b9772ee1e882b075b856edc3035

Fixed-seed hashes

| Seed | Trace SHA-256 | State SHA-256 |
|---|---|---|
| 1 | 3840682e22692e597bc1419aa298337201e86db2d35f7208c5c9e50e9a99a142 | 411abb0a4bab0b812bc5e2e010f03d22f726ff32fdcebcb7df6c3a5beac8aec9 |
| 2 | 284cbb6fdc2919b348fb051f25775c3ae52e1f733c205aa0f3daa8da4bfb66be | cf4c2ead63cb8b111e61d9c238868f5eed9630b3f0fd1c71b8c4d9f617c6557a |
| 8 | 71c711fe5922dee450b65da41ba9d121598bfe19234ef3ed9bfcc020ab1ab34a | daea1c9335ac91f95272da20cc2e20306f8ab36ffce2e11d693ad3d4ee5d48fc |

Owner-amended A4 seed log

Observed first25 completion order: 1, 8, 3, 2, 5, 4, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25. Seed set1..25 inclusive.
28 had completed at stop. Supplemental26–28 and interrupted29–30 are excluded and separated. No selected failure requires a rerun. No new batch was started. Every selected row completed2,400 live seconds.

| Seed | Closed/awarded | Completion ratio | Released | Runtime seconds | Crash/stall/invariant anomalies |
|---|---:|---:|---:|---:|---|
| 1 | 575/575 | 1.0000 | 419 | 319.054 | None |
| 8 | 561/561 | 1.0000 | 405 | 323.064 | None |
| 3 | 525/525 | 1.0000 | 384 | 359.734 | None |
| 2 | 581/581 | 1.0000 | 427 | 376.865 | None |
| 5 | 583/583 | 1.0000 | 427 | 262.142 | None |
| 4 | 582/582 | 1.0000 | 416 | 277.910 | None |
| 6 | 521/521 | 1.0000 | 390 | 189.132 | None |
| 7 | 611/611 | 1.0000 | 431 | 205.376 | None |
| 9 | 515/515 | 1.0000 | 370 | 193.552 | None |
| 10 | 504/504 | 1.0000 | 352 | 191.098 | None |
| 11 | 543/543 | 1.0000 | 393 | 200.746 | None |
| 12 | 586/586 | 1.0000 | 420 | 202.021 | None |
| 13 | 601/601 | 1.0000 | 429 | 187.325 | None |
| 14 | 581/581 | 1.0000 | 412 | 186.959 | None |
| 15 | 554/554 | 1.0000 | 394 | 191.080 | None |
| 16 | 596/596 | 1.0000 | 428 | 188.936 | None |
| 17 | 504/504 | 1.0000 | 351 | 200.168 | None |
| 18 | 542/542 | 1.0000 | 390 | 204.606 | None |
| 19 | 584/584 | 1.0000 | 421 | 197.450 | None |
| 20 | 522/522 | 1.0000 | 370 | 190.571 | None |
| 21 | 547/547 | 1.0000 | 406 | 186.544 | None |
| 22 | 554/554 | 1.0000 | 390 | 186.846 | None |
| 23 | 550/550 | 1.0000 | 402 | 176.692 | None |
| 24 | 601/601 | 1.0000 | 434 | 185.822 | None |
| 25 | 603/603 | 1.0000 | 413 | 191.493 | None |

Totals:14,026 awarded/closed (100%);10,074 released (71.8238%). Other closures:369 snap timeouts,3,309 toss timeouts,247 superseded by offence minor,27 by defence minor. These stated procedural outcomes are not releases. Earlier development failures remain recorded and excluded.
Runtime min176.692s, median193.552s, max376.865s, sum5,575.186s. These wall runtimes include two soak workers and overlapping validation/comparison jobs during part of the run, not isolated benchmarks.

Source inventory and final dispositions

| Mechanic | Source branch / commit | What it does | Existing evidence (not Native acceptance) | Disposition | Reason / planned change |
|---|---|---|---|---|---|
| Physical substrate, anatomy, locomotion, contacts, throws, arrows | frozen B0 2abe497 | event/substep engine, physical standards | b1 preservation: 427 frozen paths; M1/G1 engine tests | ADOPT-WITH-FIX | instance/source-isolated Native adapters; frozen files unchanged; no legacy tactical decisions |
| Typed pipeline and pass release v1 | b1/m1-decision-outcome 4b19719 | pure decide, delayed view, ingress, moving-release bound, feedback | test_m1/test_g1; accepted M1 record | ADOPT | core.py/runtime.py behavior unchanged; Native adds explicit speed/height/arc intents separately |
| Multi-athlete runtime | experiment/prism-sprint-30 99cf83a | sensors, N-athlete commands, feedback, pass calls | test_sprint; SPRINT30 reports | ADOPT through Sprint-45 | no unique additional mechanic needs duplication |
| Possession R-01–R-22 | experiment/prism-sprint-45 c64d92e | 500 ms direct/passive/contested state; ZR ledger | test_possession/test_sprint45 | ADOPT-WITH-FIX | enforce all resulting restarts and immunity in Native; synchronize end changes |
| Ownership primitives / commitments | b1/emergence-ownership-enablers b7670b7 | Keeper, restart, Archer movement, restraint intents | test_emergence_ownership | ADOPT-WITH-FIX | platform static; geometry configured; all semantic choices must be decide outputs |
| Ownership merge trial | experiment/emergence-ownership-integrated 146a444 | merges enablers into Sprint-45 | merge is conflict-free; no full-loop wiring in this commit | DROP duplicate | superseded by 7741539; not independent working integration |
| Delivered 3-D beliefs / ownership full loop | codex/b1-ownership-integrated 7741539 | installs overlay; no truth fallback; restraint in views | 111 tests + 23 subtests; seed1 twice same hash | ADOPT-WITH-FIX | separate sensor model parameters, configured goal radius, restart latching/alignment; old rules not current canon |
| M2 transport, inactive stages | codex/b1-m2-plumbing 5c23fe8 | bounded deterministic opaque delivery; no active plans | 117 tests + 23 subtests, focused seven; full match + 600 episodes replay | ADOPT | merge as is; NULL default; no content |
| Named profiles / effective readback | claude/experiment-profile-v1 c339b01 | v0.3 flat/mark/discipline plus CATCH_V2/HAND_FIGHT | test_profile; measured scrimmage stall 59 awards / 2 releases | ADOPT-WITH-FIX | merge requested profile code; Native replaces ambient env flags with immutable explicit config; legacy-b0 retained |
| Flat scoring / discipline / always12 / quivers | B0 rules_v03.py at 2abe497 | point bundle, per-player ladders, replacement cover, 25/5 caps | RULES_V03_IMPL_NOTES scratch tests / short runs | ADOPT-WITH-FIX | source contains dynamic env reads, fatigue-ranked substitution and some old exceptions; Native explicit rules and deterministic cover, intent provenance for intentional majors |
| Restart scaffold | B0 restarts_v1.py at 2abe497 | Hunt, snap40, scrimmage, toss | RESTARTS_NOTES, older full games | ADOPT-WITH-FIX | old role-picked contestants, formation tables, timing defaults and teleport setup cannot prescribe Native decisions; take rule transitions, replace tactical paths |
| CATCH_V2 | B0 catch_v2.py at 2abe497 | shared hand-energy threshold / contested acquisition | catch_lab_v0, earlier profile runs | PLACEHOLDER | shared energy/reach subset; automatic jump and hand-contest overlays absent; common field/Keeper kernel |
| HAND_FIGHT | B0 hand_fight_v0.py at 2abe497 | impulses, balance loads and band/grip fouls | hand_fight_lab; profile smoke | PLACEHOLDER | Native retains incidental physical contacts and intent-gated carrier wraps; full voluntary off-ball repertoire is absent |
| Bounce / dribble | B0 bounce_option_v0.py at 2abe497 | surface-target throw then physical bounce, skip planner | throw/bounce labs; rule notes | ADOPT-WITH-FIX | old second dribble is silently blocked; Native second is offence minor; self replay and stoppage/other-touch reset explicit |
| THROW_SPLIT / throw standards | B0 throwing_v1.py at 2abe497 | power, accuracy, touch, physical release cap | throw_lab_v1, throw_split_check | PLACEHOLDER | explicit 0.70 abilities, semantic speed/height, belief lead and drag-aware arc; full power/accuracy/touch chain remains unported |
| Formation-free positioning / 16 numbers | experiment/emergence-1 761dca5 | nine local candidates scored only from beliefs | test_emergence/test_metrics; old-score harness | ADOPT | default vector only; remove home formation anchors from Native; NO carried results, search or tuning |
| Paired/side-swap/held-out harness | experiment/emergence-1 761dca5 | isolated process jobs and canonical result order | run_tests, symmetry/held-out artifacts | ADOPT-WITH-FIX | full Native config/digest, 4x600; rerun results later; do not import evolved vector |
| Contact Scrimmage athlete behavior | Native PLACEHOLDER | snapper/tackler alignment, offside avoidance, chosen release inside window | Native tackle/offside/snap tests and amended25 full-match evidence | PLACEHOLDER | minimal public-rules-driven intents; replaceable by Claude; no formation or mass-selected tactical role |
| Hunt contestant / first touch | Native PLACEHOLDER | any eligible field athlete may claim, deterministic admission | Native Hunt/false-start/every-period tests | PLACEHOLDER | no role/attribute ranking; same intent pipeline |
| Dribble choice / toss taker / substitution cover | Native PLACEHOLDER | primitive explicit choices, rule eligibility only | Native dribble/toss/discipline/returning-bench and provenance tests | PLACEHOLDER | deterministic canonical admission of athlete claims; no hidden suitability scoring |
| Legacy tactical layers / home grid / kicking | all legacy experimental paths | field/pose/offact/Keeper overlays, role anchors, foot action | inspection shows separate deciders and env flags | DROP from Native | prohibited; legacy reproduction remains isolated |
| Breaks, timeouts, further Hunt penalties, standard scoring | owner prompt / 8e1e82a | not ruled / explicitly deferred | canon record | DROP / DEFERRED | no speculative rules |
| Fatigue/injury, ratings development, learning, M2 content | owner prompt | explicitly out of scope | no Native evidence claimed | DROP / DEFERRED | uniform 0.70 baseline; no quality tuning |


Native versus engine ownership

| Responsibility | Athlete-owned Native decision | Engine-owned execution / rule responsibility |
|---|---|---|
| Field play and positioning | pure decide(), B1 decision kinds and default Emergence-1 16-number belief policy | locomotion limits, collisions and physical feasibility; no home grid or external assignments |
| Keeper | belief-derived set/move/step/launch choice | own-body motor planning, committed flight/landing and physical catch/parry outcomes; no true-ball fallback |
| Archer | belief target, hold/draw, fresh release or abort | fixed configured platform, ballistic flight, ammunition and legality sanctions; no replacement target |
| Restart and Hunt | PLACEHOLDER claims, alignment, wait and release through decide() | eligibility and canonical claim ordering, compulsory snapper, line/clock/offside checks, public restart IDs |
| Substitution | PLACEHOLDER bench claim through current public-only view and decide() | exclusion/DQ timers, vacancy record, eligibility, role/equipment transfer; no ability ranking |
| Throw and bounce | explicit target, receiver, speed and height; belief lead; PLACEHOLDER parameter policy | moving-origin recomputation with 60-degree bound, primitive drag-aware arc, physical error/rebound; no receiver-truth lookup |
| Dribble | PLACEHOLDER explicit throw-and-replay decision | touch/stoppage allowance reset and second-dribble foul |
| Contact | admitted press/wrap intent; full voluntary off-ball repertoire is PLACEHOLDER | physical impulses, balance, legal bands, grounding and sanctions; intent provenance defines intentional majors |
| Catches | No explicit cognitive catch action (PLACEHOLDER); admitted movement places the body | shared energy/reach subset, secure/contested physical outcomes; no independent legacy Keeper decider |
| Officiating | public signals are delivered in views | clocks, possession R-01..22, zones, scoring, discipline, boundaries, restarts and overtime |
| Initial setup | no tactical role or formation choice is prescribed | PLACEHOLDER legal random scatter and canon-required roster roles; configured fixed platform |
| Information and randomness | cognition consumes immutable view and own belief | delayed/noisy visual sensor; independent per-athlete sensor RNG; physics RNG isolated from null M2 |
| Communication | no authored message/plan content; existing pass call only | merged M2 typed envelopes, bounded transport and inactive hooks; NULL default |


Rule-to-test matrix

N = native/test_rules.py; P = b1/test_possession.py::PossessionRows.
I = IMPLEMENTED+tested; PH = PLACEHOLDER; D = DEFERRED. A test alongside PH verifies only its current subset, not completion.

| ID | Rule | Status | Test / reason |
|---|---|---|---|
| S1 | Four 600-second periods, two rosters of 22 and 12 active | I | N::test_structure_configuration_and_effective_readback |
| S2 | First Hunt opens every regulation and overtime period; any field contestant | I | N::test_hunt_each_period_any_field_claim_and_false_start_retake |
| S3 | False start retaken | I | N::test_hunt_each_period_any_field_claim_and_false_start_retake |
| S4 | First tied overtime 300 s, runs whole period | I | N::test_first_overtime_is_whole_300s_and_later_is_sudden_death |
| S5 | Later sudden death ends on any score, full and half forced | I | N::test_sudden_death_ends_on_any_score |
| BALL1 | No kick releases or strike path | I | N::test_dribble_second_foul_reset_stoppage_and_other_touch |
| BALL2 | One throw-and-replay dribble; second offence minor; stoppage and other touch reset | I | N::test_dribble_second_foul_reset_stoppage_and_other_touch |
| CLOCK1 | 30 s fresh after score and turnover; carries tackle | I | N::test_clock_stops_dead_carries_first_tackle_and_expiry_turnover |
| CLOCK2 | Play expiry turnover spot or own 40 nearer attacked goal | I | N::test_clock_stops_dead_carries_first_tackle_and_expiry_turnover |
| CLOCK3 | Snap clock runs only when more than ten remained | I | N::test_clock_stops_dead_carries_first_tackle_and_expiry_turnover |
| CLOCK4 | Game clock stops every dead ball | I | N::test_clock_stops_dead_carries_first_tackle_and_expiry_turnover |
| G1 | 100x100 surface and strict 20 m configured zone arc | I | N::test_geometry_goal_semicircle_whole_ball_quadrant_and_platform |
| G2 | 3 m goal semicircle and 3 m quadrant depth | I | N::test_geometry_goal_semicircle_whole_ball_quadrant_and_platform |
| G3 | Whole ball crosses inside goal section | I | N::test_geometry_goal_semicircle_whole_ball_quadrant_and_platform |
| G4 | Platform fixed 5 m high / 5 m back, one per goal | I | N::test_geometry_goal_semicircle_whole_ball_quadrant_and_platform |
| G5 | Platform arrow ballistic reach tested | I | N::test_archer_illegal_release_spends_ammo_abort_does_not_and_platform_ballistic |
| SCORE1 | Flat two-point goal and one-point half goal | I | N::test_flat_goals_carry_distance_and_keeper_cannot_score |
| SCORE2 | Carry tracked separately | I | N::test_flat_goals_carry_distance_and_keeper_cannot_score |
| SCORE3 | Noncarry release distance and success counters | I | N::test_noncarry_goal_release_distance_attempts_and_success |
| SCORE4 | Keeper cannot score for own team, own goal for opponents | I | N::test_flat_goals_carry_distance_and_keeper_cannot_score |
| T1 | First tackle contact scrimmage inside zone; attacked goal x<10 resets to 10 | I | N::test_first_tackle_snapper_tackler_reset10_second_turnover |
| T2 | Tackled snapper and tackler recorded | I | N::test_first_tackle_snapper_tackler_reset10_second_turnover |
| T3 | Missed ten-second snap window count+1 and 5 m back | I | N::test_snap_window_missed_costs_count_and_spot |
| T4 | Offence offside count+1 and 5 m back; second turnover | I | N::test_scrimmage_offside_procedural |
| T5 | Defence offside count-1 floor zero, 5 m forward; no half goal | I | N::test_scrimmage_offside_procedural |
| T6 | Second tackle turnover spot or own40 nearer attacked goal | I | N::test_first_tackle_snapper_tackler_reset10_second_turnover |
| F1 | Offence minor count+1, second turnover | I | N::test_offence_minor_second_is_turnover_and_defence_costs_count |
| F2 | Defence minor decrements; count zero awards half P1-3 / full P4+ and retains | I | N::test_defensive_minor_awards_and_retains |
| F3 | Unintentional head minor; intent-chosen head/trip major | I | N::test_intent_defines_major_not_incidental_head |
| F4 | First major 120 s game-time exclusion, second DQ | I | N::test_discipline_ladder_cover_and_game_time_exclusion |
| F5 | Fourth minor 60 s exclusion, fifth DQ | I | N::test_discipline_ladder_cover_and_game_time_exclusion |
| F6 | Cover exclusions/DQ and eligible return after time | I | N::test_discipline_ladder_cover_and_game_time_exclusion |
| F7 | Forfeit only below 12 currently available of 22 | I | N::test_forfeit_only_below_twelve_currently_available |
| C1 | Off-ball legal band, hip push/stab; no pulling/gripping | I | N::test_contact_legal_band_grip_and_carrier_joints |
| C2 | Carrier wrap and knee/joint legal below neck | I | N::test_contact_legal_band_grip_and_carrier_joints |
| K1 | Keeper inside own zone protected from opponent initiation when PP own | I | N::test_keeper_immunity_position_at_contact_and_freeze_in_all_phases |
| K2 | Keeper never Archer target; inside-zone Keeper never freezes | I | N::test_keeper_immunity_position_at_contact_and_freeze_in_all_phases |
| K3 | ZR-1/C/T enforced as opponent RST-1 with clock reset | I | N::test_possession_zone_violations_are_enforced_as_rst1 |
| A1 | 25 arrows, illegal release spends ammo and minor, abort no spend | I | N::test_archer_illegal_release_spends_ammo_abort_does_not_and_platform_ballistic |
| A2 | At most five freezes, freeze5 plus immunity10 | I | N::test_freeze_cap_and_five_plus_ten_seconds |
| A3 | Recovery protection3m/2s | I | N::test_recovery_arrow_protection_three_metres_two_seconds |
| A4 | Targets opposing fields on offence with control, outside both zones | I | N::test_archer_illegal_release_spends_ammo_abort_does_not_and_platform_ballistic |
| TIE1 | Shot release at expiry counts, only shots retain flight | I | N::test_shot_release_at_expiry_precedes_clock |
| TIE2 | Goal wins coincident catch; boundary wins secure hold | I | N::test_exact_goal_catch_and_boundary_secure_ties |
| OUT1 | Toss crossing point, goal-line zone slide, thrower outside, 3 m clearance, ready1.5 | I | N::test_toss_crossing_arc_slide_clearance_ready_no_self_no_direct_score |
| OUT2 | Toss within4s of ready | I | N::test_toss_deadline_four_seconds_after_ready |
| OUT3 | Toss cannot score direct; taker cannot recover | I | N::test_toss_crossing_arc_slide_clearance_ready_no_self_no_direct_score |
| OWN1 | No hidden attributes in pure decide, commands retain intent IDs | I | N::test_information_boundary_and_all_commands_from_pure_decide |
| OWN2 | Formation-free parameter vector / residence compliance intent | I | N::test_formation_independent_of_slot_and_residence_exit_intent |
| OWN3 | Environment cannot turn on legacy layers or mix Native config | I | N::test_environment_flags_cannot_enable_a_native_legacy_layer |
| OWN4 | Serialized view+belief replays decision | I | N::test_native_view_json_replays_exact_decision |
| M2 | M2 null present equals absent; paired harness | I | N::test_m2_null_absent_short_replay_and_harness_pairs |
| R-01 | D1 possession row R-01 | I | P::test_R01_opening_no_possession_no_phase_empty_archer_target_set — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-02 | D1 possession row R-02 | I | P::test_R02_secured_timer_runs_possession_unchanged_before_threshold — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-03 | D1 possession row R-03 | I | P::test_R03_threshold_gives_direct_and_passive_possession — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-04 | D1 possession row R-04 | I | P::test_R04_C1_contest_lapses_direct_not_passive — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-05 | D1 possession row R-05 | I | P::test_R05_contest_ends_timer_restarts_at_zero — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-06 | D1 possession row R-06 | I | P::test_R06_pass_release_keeps_team_control_and_passive — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-07 | D1 possession row R-07 | I | P::test_R07_shot_release_ends_team_control_passive_unchanged — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-08 | D1 possession row R-08 | I | P::test_R08_defender_touch_ends_control_resets_zone_clock_passive_unchanged — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-09 | D1 possession row R-09 | I | P::test_R09_loose_ball_keeps_passive_possession — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-10 | D1 possession row R-10 | I | P::test_R10_opponent_uncontested_control_flips_passive_and_resets_clocks — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-11 | D1 possession row R-11 | I | P::test_R11_ZRC_carrier_crosses_from_outside_into_own_zone — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-12 | D1 possession row R-12 | I | P::test_R12_ZRT_pass_from_outside_into_own_zone_teammate_first_touch — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-13 | D1 possession row R-13 | I | P::test_R13_zone_clock_five_seconds_records_ZR1_once — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-14 | D1 possession row R-14 | I | P::test_R14_reset_trigger_ball_leaves_zone — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-15 | D1 possession row R-15 | I | P::test_R15_R16_keeper_protection_needs_passive_possession_and_position — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-16 | D1 possession row R-16 | I | P::test_R15_R16_keeper_protection_needs_passive_possession_and_position — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-17 | D1 possession row R-17 | I | P::test_R17_freeze_legal_ruleset_102 — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-18 | D1 possession row R-18 | I | P::test_R18_out_of_play_keeps_passive_until_restart_awards_it — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-19 | D1 possession row R-19 | I | P::test_R19_RST1_restart_passive_to_opponent_clock_zero_and_stopped — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-20 | D1 possession row R-20 | I | P::test_R14_R20_reset_trigger_dead_ball_stopped_until_live — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-21 | D1 possession row R-21 | I | P::test_R21_keeper_catch_passive_stays_with_shooter_until_threshold — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| R-22 | D1 possession row R-22 | I | P::test_R22_C3_same_instant_touches_contested_no_first_touch_violation — Native enforcement covered by K3 and Native direct/body-contact tests; pure kernel tests unchanged. |
| PH1 | Hunt choice and first-touch behavior | PH | N::test_hunt_each_period_any_field_claim_and_false_start_retake — Q-HUNT-1/2, canonical claim admission; radius/clock defaults |
| PH2 | Contact Scrimmage alignment, offside avoidance, snap and toss-taker decisions | PH | N::test_first_tackle_snapper_tackler_reset10_second_turnover — Q-BEHAVIOR-1, pure procedural intents; full-run stall checks required |
| PH3 | Attacker five-second residence and marked defender exemption | PH | N::test_zone_residence_enforced_marked_defender_and_keeper_exempt — own-clock exit primitive; unmarked defender grace Q-ZONE-1; current marking checks offensive field players; Keeper-as-marker coverage unproven |
| PH4 | Boundary touching body parts / airborne exemption | PH | N::test_boundary_contact_and_airborne_proxy — Q-BOUNDARY-1 body cylinder proxy; detailed anatomical contact deferred |
| PH5 | Shared CATCH_V2 energy kernel | PH | N::test_shared_catch_reach_and_heldout_partition — Q-CATCH-1: automatic jump/hand-contest extension not installed |
| PH6 | THROW_SPLIT mechanics | PH | N::test_primitive_throw_speed_height_arc_are_intent_owned — Q-THROW-1: explicit speed/height/arc, primitive accuracy; not full source-equivalent model |
| PH7 | Voluntary HAND_FIGHT repertoire | PH | N::test_contact_legal_band_grip_and_carrier_joints — Q-HAND-1: physical contacts and intent-gated carrier wrap; full off-ball choices absent |
| PH8 | Substitution cover admission | PH | N::test_discipline_ladder_cover_and_game_time_exclusion — Q-COVER-1 / Q-BEHAVIOR-1 canonical eligible athlete claim |
| PH9 | Shot finishing-flight maximum | PH | N::test_only_shots_get_clock_flight_exception — Q-FLIGHT-1 ten-second safety tail |
| PH10 | Dribble decision | PH | N::test_dribble_second_foul_reset_stoppage_and_other_touch — Q-BEHAVIOR-1 no fresh teammates -> trivial self throw choice |
| PH11 | Native delayed sensor | PH | N::test_information_boundary_and_all_commands_from_pure_decide — Q-SENSOR-1 immutable noisy cone/occlusion; Claude replacement later |
| D1 | Breaks and timeouts | D |  — Explicit owner deferral: do not build |
| D2 | Hunt penalties beyond false-start retake | D |  — Explicit owner deferral: do not build |
| D3 | Standard non-flat scoring | D |  — Explicit owner deferral: do not build |
| D4 | Fatigue and injury | D |  — Explicit owner deferral: do not build |
| D5 | Ratings development and adaptive learning | D |  — Explicit owner deferral: do not build |
| D6 | M2 plan and message content | D |  — Explicit owner deferral: do not build |
| CTX1 | Restart command cannot be rebound to a different rule record | I | N::test_stale_restart_cannot_be_rebound_to_another_rule_record — Native integration regression |
| CTX2 | Restart record outranks stale Hunt flag | I | N::test_restart_record_takes_precedence_over_uncleared_hunt_flag — Native integration regression |
| CTX3 | Period boundary cancels pending draws and rejects stale-period intents | I | N::test_period_end_cancels_pending_draw_and_rejects_stale_period_intents — Native integration regression |
| MOTOR1 | Keeper lands in dead time without a new decision | I | N::test_keeper_landing_completes_in_dead_ball_without_new_semantic_choice — Native integration regression |
| MOTOR2 | Completed match blocks further body movement or landings | I | N::test_physical_port_cannot_land_or_move_bodies_after_finality — Native integration regression |
| CLOCK5 | Offside retake retains the original tackle snap-clock run flag | I | N::test_defensive_offside_retake_preserves_tackle_clock_run_flag — Native integration regression |
| ARROW5 | Completed draw requires a fresh release/abort intent | I | N::test_archer_draw_requires_fresh_release_intent_before_ammo_spent — Native integration regression |
| G6 | Archer platform faces opposing goal before/after end exchange | I | N::test_platform_faces_opposing_goal_before_and_after_end_exchange — Configuration/clock conformance |
| CLOCK6 | Running snap clock expires in dead ball at the exact millisecond | I | N::test_running_snap_clock_expires_in_dead_ball_at_exact_millisecond — Configuration/clock conformance |
| CLOCK7 | Physical intervals slice at direct-possession, freeze and zone deadlines | I | N::test_physical_step_slices_at_direct_and_freeze_deadlines — Millisecond deadline integration |
| G7 | Platform readback covers the active replacement after end exchange; bench pose is not a platform | I | N::test_platform_readback_checks_active_replacement_not_benched_archer |
| BALL3 | Bounce option targets a surface spot then physical rebound | I | N::test_bounce_intent_targets_surface_then_uses_physical_rebound |
| T7 | Score restarts conceding team at own40 centre, fresh clock/count; all at or behind own40 | I | N::test_goal_restart_is_conceding_own40_and_requires_all_behind_own40 |
| F8 | Returning substitute receives current public period through AthleteView, not stale on-field vision | I | N::test_returning_bench_claim_has_current_public_period_not_old_visual_frame |

QUESTIONS_FOR_OWNER.md

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


Native v1 roadmap

OWNER BRIEFING — ROADMAP
1. The Native v1 roadmap is DESIGN COMPLETE: ordered milestones, owners, entry/exit gates, evidence, dependencies and risks are recorded below.
2. Native PRISM 0 supplies the TESTED functional baseline: four regulation periods, forced overtime cases, immutable-view decisions, null M2 and the owner-amended 25-match soak.
3. Native v1, new cognition, message/plan content, off-ball strategies and deferred rules are not implemented by this roadmap. Native v0's placeholders remain explicit.
4. No engineering question is escalated. The canon details and deferred rules below require DreLen's rulings before those rules are changed or built. Native PRISM 0 acceptance remains pending.
5. Recommend Claude's independent review, then DreLen acceptance of the frozen baseline; rerun Emergence-1 on that exact baseline while engine fidelity work proceeds on separate branches.

The owner's goal is to find the best way to play Beastball. Future policy comparisons use match results, with uncertainty reported. This roadmap specifies no preferred tactic, formation, style or hand-authored quality reward. No claim about quality, balance or emergence follows from Native v0's functional tests.

Effort sizes: S = one bounded change; M = several connected components; L = a substantial cross-component integration. They are relative sizes, not delivery dates.

| Milestone | Owner / effort | Entry | Work | Exit / evidence |
|---|---|---|---|---|
| V1-0: Review and freeze Native PRISM 0 | Codex engineering, Claude independent review, DreLen acceptance / S | Amended A1–A8 evidence available | Review simulation freeze ba568dc84299cc95f86eb83207e0533297569cd7 plus the delivery commit. Inspect all placeholders, preservation changes, raw failures and selected25 seed log. | DreLen explicitly accepts; record immutable commit/config and tag only after acceptance. Reproduction commands and both hashes remain available. No old experiment result enters this baseline. |
| V1-1: Rerun Emergence-1 on Native PRISM 0 | Claude cognition/experiment design; Codex harness support / M | V1-0 accepted; exact Native0 commit/config/policy defaults recorded | Rerun the 16-parameter belief policy experiment under Native0 flat scoring, uniform 0.70 ratings and null M2. Use paired seeds, both side assignments, isolated parallel jobs and held-out seeds fixed before selection. Keep all trials, errors and manifests. | A reproducible Native0-only result set with config digests, serial/parallel identity, paired comparisons and held-out match results. Do not carry over old-score rankings, evolved vectors or prior conclusions. This is an experiment gate, not a promised improvement. |
| V1-2: Close engine fidelity placeholders and ratified-rule edge cases | Codex engine; Claude owns intent/sensor contract input; DreLen supplies canon where needed / L | V1-0; explicit per-placeholder specification and frozen test cases | Complete the catch, throw, hand-contact and boundary mechanics below; finish residence-role coverage and procedural adjudication. Keep semantic choices in decide(), retain accepted core/runtime behavior and preserve frozen B0. Use a new config version for changed mechanics. | Each engine placeholder has a physical/conformance test and status change supported by evidence. New full-match replay and a fresh varied-seed functional soak pass on the integration candidate. Native0 remains reproducible; its experiment results are not treated as rankings for changed mechanics. |
| V1-3: Replace procedural cognition primitives | Claude cognition; Codex provides admissions, public views and motors / L | Stable typed interfaces from V1-2; scenario fixtures | Replace Hunt claims/first touch, restart claims/alignment/wait/snap, toss taker, dribble choice, cover claims and residence compliance with PRISM-owned decisions. No externally prescribed formation, hidden suitability ranking or engine-selected replacement target. | All commands retain view/belief/decision/intent provenance; JSON and hidden-state poison tests pass. Adversarial restart/period/exclusion cases finish, including seed8's returning-substitute regression. Functional completion establishes no quality claim. |
| V1-4: M2 content proposal and controlled trials | Claude authors cognition/content; Codex maintains transport and gates / L | V1-1 observations; explicit later authorization for content; Native0 still frozen | Derive proposed message/plan content from the Native0 experiment's observed coordination needs. Specify sender/receiver knowledge, causal IDs, stage activation and reaction behavior before implementation. Trial opt-in content on a separate versioned branch, with null controls and paired held-out matches. | Content has independent information-boundary review, causal replay, delay/loss/noise/capacity tests and reported match results. No live callback or transport rewrite of action type, target or receiver. Any proposed relaxation of the current no-influence bypass scope needs an explicit later scope decision; this roadmap does not grant it. NULL mode must still equal plumbing absent within each mechanics version. |
| V1-5: Off-ball actions and Hunt strategies | Claude cognition; Codex contact/Hunt execution / L | V1-4; V1-2 contact interfaces available | Add PRISM-owned voluntary off-ball actions and contestant/first-touch choices as explicit intents. Enforce contact bands, pulling/gripping sanctions, intentional head/trip classification, immunity, readiness and body limits. Explore choices through match-result experiments, not prescribed tactics. | Legality and intent-provenance tests pass for every new action. Paired, side-swapped and held-out results are reproduced on the exact relevant config. No online adaptation or rating development is introduced. |
| V1-6: Integrate and revalidate Native v1 candidate | Codex integration; Claude independent review / M | V1-2, V1-3 and V1-5 complete for the approved scope | Integrate one mechanic at a time with source provenance. Re-run relevant policy/content comparisons after mechanics changes; record that Native0 results apply only to Native0. Consolidate config/readback, schemas, rule matrix and performance records. | No unlabelled placeholder remains. Each remaining deferral is explicitly authorized. Full regulation/overtime/exact-tie scenarios, original B1 gates, preservation, null replay and the full varied-seed functional soak pass. A failure is retained, reproduced and repaired before release; no artificial winner or forced release masks it. |
| V1-7: Canon-dependent extensions | DreLen canon; Codex engine; Claude cognition / L for the bundle | A written ruling and separate scope authorization for that extension | Build only the ratified deferred rules listed below. Give every extension its own mechanics/config version and rule-to-test mapping. Maintain the Native0 control profile. | Forced boundary cases, view-only intake, rule conservation, deterministic replay and full-match evidence for the extension pass. Unruled extensions remain deferred; they are not silently inferred as requirements for the current-rules v1 release. |
| V1-8: Release Native v1 | Codex engineering, Claude review, DreLen acceptance / M | V1-6 and every extension included in v1's approved scope pass | Produce the final manifest, full rule matrix, source/provenance inventory, unresolved-canon record and exact reproduction commands. Review source, information boundaries and observed failures independently. | DreLen accepts the concrete commit/config. Fully functional means the ratified, in-scope mechanics and interfaces are complete and tested; it does not assert that any policy or communication scheme is good. |

Placeholder replacement ownership

| Native0 placeholder | Replacement and owner | Cheapest useful proof |
|---|---|---|
| Hunt contestant/first touch; circle/setup/clock details | DreLen ratifies missing setup/clock detail; Claude supplies decisions; Codex implements officiating/motors | Forced false starts, delayed/stale frames and every regulation/OT opening; no pre-exit draw/fire |
| Scrimmage/toss claims, alignment, wait, snap, offside avoidance | Claude cognition; Codex eligibility/clearance/deadlines | Forced first/second tackle, mandatory Keeper snapper, both offside sides, stale restart/period IDs, snap/toss timeout and goal own40 cases |
| Dribble decision | Claude cognition; Codex touch/stoppage ledger | First replay succeeds, second fouls, another touch/stoppage resets; surface bounce follows physics |
| Substitution cover and role transfer | Claude cover decisions; Codex availability, equipment and physical transfer | Fourth/fifth minor, first/second major, return after game-time exclusion, changing ends, returning-bench public period and fewer-than12 forfeit |
| Shared catch energy/reach subset | Codex full common physical model; Claude any deliberate catch/jump/hand choice | Same model across roles, speed/height/energy sweeps, contested contact, no second Keeper decider and no hidden-flight fallback |
| Primitive THROW_SPLIT, fixed decision speed/height defaults | Codex complete power/accuracy/touch and motor standards; Claude release parameters | Moving-origin lead/arc, chosen speed/height, bounce/angle paths, release bound and feedback; calibration against physical standards, not desired goal rates |
| Voluntary HAND_FIGHT repertoire | Claude explicit contact choices; Codex physical coupling and sanctions | All legal/illegal bands, wrap on carrier only, off-ball grip/pull, intentional head/trip, immunity and simultaneous contacts |
| Body-cylinder boundary witness | Codex anatomical/support witnesses | Touch exactly on line, airborne body/support transitions, secure-hold ties and whole-ball goal crossing |
| Residence/marking scope | Codex full role coverage; Claude legal movement choice; DreLen unmarked-defender grace ruling | Strict arc, attacker5s, marked/unmarked defenders, Keeper exemptions and every allowed offensive marker role |
| Delayed sensor constants | Claude cognition/sensing contract; Codex geometric sensor execution | Serialized view replay, true-state poison, missing/stale 3-D courses, occlusion reference and unblocked platform vision |
| Shot tail, held-ball and simultaneous-minor procedures | DreLen rules missing detail; Codex adjudication | Exact millisecond fixtures, shot-only exception, no unbounded phase or false major, invariant preservation |

Dependencies and parallel work

V1-0 precedes experiments and baseline-dependent changes. V1-1 runs on the immutable Native0 baseline; V1-2 engine work, V1-3 interface development and canon clarification may proceed in parallel on separate branches. V1-4 follows V1-1; V1-5 follows V1-4 and requires the relevant V1-2 motors. V1-6 joins the tested workstreams. V1-7 proceeds only after its canon ruling and joins V1-6 if included in v1. V1-8 follows the final integrated evidence. Never mix different mechanics/config digests in one policy comparison. Do not start additional Native0 soak batches merely to implement this roadmap; the amended A4 evidence is complete.

Canon required from DreLen before the relevant changes

- Existing questions: Hunt circle/setup and clock activation; unmarked-defender residence grace; maximum finishing-flight procedure; excluded-player availability at the forfeit boundary; simultaneous offsetting minors; unresolved held-ball procedure. Current defaults remain labelled placeholders until ruled.
- Breaks and timeouts: availability, duration, clock/possession/zone/reset behavior and restart procedure.
- Hunt penalties beyond the ratified retake: triggers, sanctions, clock and restart consequences.
- Standard scoring: the actual values and classification rules, plus when flat scoring is replaced. The old experiment table is not assumed to be current canon.
- Fatigue and injury: permitted effects, timing, recovery, replacement and stoppage rules before models are built.
- Ratings/development: what can vary or develop, visibility and lifecycle; no development or adaptive learning is authorized by Native0. Preserve the uniform 0.70 control.
- M2 content needs later scope authorization as well as Claude's design. This is a future behavioral/architecture scope decision, not a sport-canon ruling.

Engineering items in QUESTIONS_FOR_OWNER.md are backlog/accountability records, not escalations. Codex resolves those implementations with evidence. Behavioral defaults are tested; DreLen is asked only when a proposed difference materially changes gameplay or requires canon.

Risks and the cheapest way to retire them

| Risk | First evidence / mitigation |
|---|---|
| Old-score results or evolving code contaminate experiments | Reject mixed commit/config digests; retain every job and predeclare held-out seeds; run Native0 separately |
| Restart liveness regresses at a period/exclusion transition | Reuse the small stale-Hunt/record/period/bench regressions first, then full matches; retain the dead-progress watchdog |
| A physics helper becomes a hidden tactical decider | Keep retired-controller traps, controller/region switches off, view poison/serialization checks and intent IDs; review every new motor for target substitution |
| New content consumes unrelated RNG or changes null behavior | Independent streams, canonical batching/order and full null-versus-absent replay before content trials |
| Approximate body/catch/throw models give misleading comparisons | Close isolated physical-standard tests first; version mechanics; rerun comparisons after fidelity changes |
| Always12 fails after exclusion, return or end exchange | Force the vacancy/bench/period cases and active-platform readback before long runs; distinguish a legal forfeit from a crash |
| Parallel completion order changes a result | Isolated processes, deterministic seed/RNG use, sorted evidence and serial/parallel equality |
| Deferred canon leaks in as an engineering assumption | Maintain the question/matrix/config records; leave unruled features deferred rather than silently implementing them |

Every milestone retains failing artifacts and exact reproduction commands. Functional tests establish implementation behavior. Future match results, with their stated uncertainty and exact mechanics version, are the only basis for comparing policies.

