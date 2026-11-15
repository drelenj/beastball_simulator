# ATTR-1 conformance matrix

Status is implementation evidence only. Nothing here is owner ACCEPTED.

| ID | Requirement | Forced evidence | Status |
|---|---|---|---|
| AT-1 | 1.0 speed is exactly 44.704 m/s and measurable within 0.5% | `test_at1_at2_speed_curve_and_measured_top_speed`: 400 m-equivalent no-boundary treadmill | IMPLEMENTED + TESTED |
| AT-2 | 0, 0.60, 0.80 speed curve | Same test asserts 0, 26.8224, 35.7632 | IMPLEMENTED + TESTED |
| AT-3 | No-roster v0/2 and v0/3 unchanged | Budget attempts 1–2 reproduce both published trace/state pairs | IMPLEMENTED + TESTED |
| AT-4 | Formula table at 0, .40, .60, .80, 1.0 | `test_at4_mapping_table` | IMPLEMENTED + TESTED |
| AT-5 | Mappings monotone | `test_at5_monotone_and_at6_independence` sweeps 0..1 by .05 | IMPLEMENTED + TESTED |
| AT-6 | One-rating independence | Same test diffs every engine-facing mapping | IMPLEMENTED + TESTED |
| AT-7 | 200 paired sensitivity trials per rating | `test_at7_sensitivity_audit_200_paired_trials_per_rating`; `AT7_SENSITIVITY.md` | IMPLEMENTED + TESTED |
| AT-8 | Body, eye, radius, reach readback | `test_at8_body_readback_and_own_view_only` | IMPLEMENTED + TESTED |
| AT-9 | Arrow stays 250 m/s across rosters | `test_at9_arrow_speed_fixed_for_different_rosters` | IMPLEMENTED + TESTED |
| AT-10 | Strict validation with row/column | `test_at10_validation_names_row_and_column`; alias-map test | IMPLEMENTED + TESTED |
| AT-11 | Labels never read | `test_at11_labels_never_read_and_digest_identical` | IMPLEMENTED + TESTED |
| AT-12 | 22-player shape and fixed roles | Shape/fixed-role tests plus role-exhaustion regression | IMPLEMENTED + TESTED; exhaustion outcome PLACEHOLDER |
| AT-13 | Determinism, serial/parallel, roster digest | Unit parallel window plus full seed-1 identical hashes | IMPLEMENTED + TESTED |
| AT-14 | Own attributes only; teammate poison excluded | `test_at14_teammate_rating_poison_does_not_enter_equal_position_view` | IMPLEMENTED + TESTED |

Additional timestep evidence: `test_e8_fast_closing_sweep_detects_contact_and_boundary_endpoint` checks a 100 ms step at 44.704 m/s and a two-athlete 8.9408 m/s closing displacement without tunnelling.
