"""Generate the independent rating status and causal-evidence matrices.

This is an assessment script, not an implementation tool.  PASS means a
direct, isolated effect was exercised in a scenario; PARTIAL means the test
only establishes an intermediate option/aim change or has too narrow a probe.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

items = [
    # canonical ratings
    ("speed", "canonical", "PASS", "native/test_attr.py::test_at1_at2_speed_curve_and_measured_top_speed", "Run speed reaches mapped 44.704 m/s in the treadmill lab; low/mid/high curve is unit-tested."),
    ("agility", "canonical", "PASS", "native/test_attr.py::test_at4_mapping_table; test_at5_monotone_and_at6_independence", "Maps independently to braking and turning; no separate full-movement outcome sweep."),
    ("strength", "canonical", "PARTIAL", "native/test_attr.py mapping; native/rulebook/test_individuation.py::test_contact_choices_depend_on_own_duel_rating", "Mapped and used by contact physics; isolated contact outcome distributions by strength were not run here."),
    ("balance", "canonical", "PARTIAL", "native/test_attr.py mapping", "Mapped into contact/balance physics; no independent low-to-high outcome distribution in this validation."),
    ("stamina", "canonical", "PASS", "native/rulebook/test_individuation.py::test_existing_physics_fatigue_reads_stamina_in_experiment_only", "Paired physics fatigue test shows the experimental profile activates stamina."),
    ("tackling", "canonical", "PARTIAL", "native/test_attr.py mapping", "Reach/grip pathway is active; dedicated one-rating tackle outcome distribution not run."),
    ("blocking", "canonical", "PARTIAL", "native/test_attr.py mapping", "Mapped into physical block/contact path; no isolated block outcome distribution here."),
    ("contact_resistance", "canonical", "PARTIAL", "native/test_attr.py mapping; native/nbl_roster.py fallback", "Independent values can be loaded, but current workbook fallback is Balance; independent NBL values are unavailable."),
    ("ball_handling", "canonical", "PASS", "native/cognition_rb3.py::release_time_s; native/port.py::decision_interval_ms", "Release preparation and decision timing read Ball Handling; paired timing tests cover it."),
    ("catching", "canonical", "PARTIAL", "native/test_attr.py mapping; core_src/match.py catch kernel", "Catch/secure physical path is present; a paired catch outcome series was not run."),
    ("awareness", "canonical", "PASS", "native/roster.py::sensor_noise_scale; native/test_attr.py mapping", "Own XY sensor noise scale is separately mapped; kept distinct from Vision/Clarity."),
    ("throw_power", "canonical", "PASS", "native/test_attr.py::test_engine_and_ingress_use_thrower_maximum", "Thrower-specific feasible speed ceiling changes; no cognition release-speed tuning claim."),
    ("throw_accuracy", "canonical", "PASS", "native/test_attr.py mapping; native/rulebook/port.py release yaw", "Controls horizontal release error; Passing is the compatibility alias to this value."),
    ("jump", "canonical", "PARTIAL", "native/test_attr.py mapping", "Height parameter propagates; no isolated jump/catch/tackle outcome distribution here."),
    ("keeper_skill", "canonical", "PARTIAL", "native/rulebook/port.py::keeper_motor", "Changes available push-off fraction; only one keeper-motor context, not save-rate evidence."),
    ("archery_accuracy", "canonical", "PASS", "native/rulebook/test_individuation.py::test_archery_accuracy_changes_actual_release_vector", "Seeded release vector changes while arrow speed stays 250 m/s."),
    # draft ratings
    ("vision", "draft", "PASS", "native/rulebook/test_individuation.py::test_sensor_focus_and_reaction_live_port", "Changes legitimate detection in a controlled field-of-view scenario."),
    ("clarity", "draft", "PARTIAL", "native/rulebook/test_individuation.py::test_clarity_changes_only_vertical_sample_error", "One fixed random stream changes vertical observation error; distribution and cognition response remain untested."),
    ("reaction", "draft", "PASS", "native/port.py::decision_interval_ms; focused sensor test", "Changes scheduled cognitive interval; perceptual/motor clocks are not multiplied by this mechanism."),
    ("anticipation", "draft", "PARTIAL", "native/rulebook/test_individuation.py::test_existing_carrier_options_change_with_one_rating", "Changes receiver lead input; no multi-seed prediction-error distribution."),
    ("focus", "draft", "PASS", "native/rulebook/test_individuation.py::test_sensor_focus_and_reaction_live_port", "Changes track retention in the tested delayed-view scenario."),
    ("instinct", "draft", "PARTIAL", "native/rulebook/test_individuation.py::test_existing_carrier_options_change_with_one_rating", "Changes deadline shot option value; selected-action frequency not measured."),
    ("judgment", "draft", "PARTIAL", "native/rulebook/test_individuation.py::test_marking_and_judgment_influence_different_options", "Changes defensive lane option evaluation, not a general risk/legality model."),
    ("motor_control", "draft", "PASS", "native/individuation.py::movement_aim; focused motor test", "Changes feasible steering quantization without changing propulsion or collision physics."),
    ("touch", "draft", "PASS", "native/individuation.py::delivery_velocity; focused motor test", "Changes vertical release allocation while conserving speed; horizontal Throw Accuracy remains separate."),
    ("playmaking", "draft", "PARTIAL", "native/rulebook/test_individuation.py::test_existing_carrier_options_change_with_one_rating", "Changes pass receiver-space value; action selection and resulting team opportunity not measured."),
    ("finishing", "draft", "PARTIAL", "native/rulebook/test_individuation.py::test_existing_carrier_options_change_with_one_rating", "Changes shot valuation against keeper clearance; selected-shot outcome not measured."),
    ("marking", "draft", "PARTIAL", "native/rulebook/test_individuation.py::test_marking_and_judgment_influence_different_options", "Changes mark option target/aim; no tracking error or marking success series."),
    ("zone_reads", "draft", "PASS", "native/rulebook/test_individuation.py::test_zone_reads_change_exit_decision_without_changing_zone_limit", "Changes a lawful leave/hold choice while the five-second rule is unchanged."),
    ("goalkeeping", "draft", "PARTIAL", "native/rulebook/test_individuation.py::test_keeper_position_uses_delivered_course_and_own_rating_only", "Changes Keeper alignment from delivered course; save outcome effect not quantified."),
    ("in_air_ball_pursuit", "draft", "PARTIAL", "native/rulebook/test_individuation.py::test_pursuit_uses_only_matching_ball_context", "Changes option value/range for high-ball context only; selected pursuit outcomes not tested."),
    ("live_ball_pursuit", "draft", "PARTIAL", "native/rulebook/test_individuation.py::test_pursuit_uses_only_matching_ball_context", "Changes option value/range for low/unknown ball context only; selected pursuit outcomes not tested."),
    ("carrier_duel", "draft", "PASS", "native/rulebook/test_individuation.py::test_contact_choices_depend_on_own_duel_rating", "Changes own carrier contact choice in paired scenario; resulting escape/tackle distribution not tested."),
    ("defender_duel", "draft", "PASS", "native/rulebook/test_individuation.py::test_contact_choices_depend_on_own_duel_rating", "Changes defender contact choice in paired scenario; resulting tackle distribution not tested."),
    # optional / compatibility fields
    ("acceleration", "optional", "PASS", "native/roster.py::mapped_values; native/test_attr.py::test_at4_mapping_table", "Independent proportional acceleration mapping is accepted and validated."),
    ("durability", "optional", "BLOCKED", "native/roster.py; audit/native/rb323/DESIGN.md", "Validated/stored but staged; no authorized injury susceptibility semantics."),
    ("injury", "optional", "BLOCKED", "native/roster.py; audit/native/rb323/DESIGN.md", "Validated/stored only; active injury is a separate forced regulation state."),
]

with (OUT / "PRISM_RATING_TEST_MATRIX.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["rating", "class", "status", "evidence", "independent_finding"])
    w.writerows(items)

# The rows below intentionally distinguish precise transform readings from
# outcome distributions.  A function-level change is not reported as a match
# effect size.
causal = [
    ("agility", "braking + turning", "(16.875 + 16.25)*r", "8.28125 / 16.5625 / 31.46875 m/s²·unit", "PASS", "Exact mapped inputs; no isolated movement outcome sweep."),
    ("strength", "contact", "direct strength input to contact/grip formulas", "one-rating effect size not measured", "PARTIAL", "This audit did not vary .25/.50/.95 in physical contact scenes."),
    ("balance", "balance/recovery", "direct balance input to existing contact kernel", "one-rating effect size not measured", "PARTIAL", "This audit did not vary .25/.50/.95 in matched contact scenes."),
    ("stamina", "fatigue load", "experimental fatigue rate", "paired deterministic scenario; numeric summary in pytest only", "PASS", "Need multi-condition late-period validation."),
    ("tackling", "grip acquisition", "direct tackling input to grip formula", "one-rating effect size not measured", "PARTIAL", "Dedicated paired low/mid/high tackle outcomes not run."),
    ("blocking", "block/contact", "direct blocking input to block power", "one-rating effect size not measured", "PARTIAL", "Dedicated paired low/mid/high block outcomes not run."),
    ("contact_resistance", "grip resistance", "direct input; NBL compatibility fallback equals Balance", "one-rating effect size not measured", "PARTIAL", "Explicit independent source accepted but canonical workbook has no values."),
    ("ball_handling", "release delay", "round(250*(1.35-.5*r)) ms", "306.25 / 275 / 218.75 ms", "PASS", "Deterministic timing input; physical catch/secure effect not separately sampled."),
    ("catching", "catch arrest", "direct Catching input to secure/catch model", "one-rating effect size not measured", "PARTIAL", "No paired fast-ball acquisition distribution run."),
    ("awareness", "sensor noise scale", "2 - 1.25*r", "1.6875 / 1.375 / 0.8125", "PASS", "Direct mapping; separate from Vision and Clarity."),
    ("jump", "jump height", "1.3*r m", "0.325 / 0.65 / 1.235 m", "PASS", "Exact mapped height; no isolated jump outcome sweep."),
    ("keeper_skill", "Keeper push-off fraction", ".75 + .25*r", "0.8125 / 0.875 / 0.9875", "PASS", "Execution ceiling, not save probability."),
    ("archery_accuracy", "arrow yaw", "seeded yaw error scaled by (1-r)", "vector changed in fixed-seed scenario; no distribution", "PASS", "Speed magnitude preserved at 250 m/s."),
    ("vision", "field-of-view half-angle", "90 + 30*r degrees", "97.5 / 105 / 118.5 degrees", "PASS", "Direct sensor detection scenario; no CI (single controlled scenario)."),
    ("reaction", "decision interval", "round(500*(1.3-.4*r)) ms", "600 / 550 / 460 ms", "PASS", "Exact deterministic schedule transform; effective delays quantize to simulation steps."),
    ("focus", "track retention", "round(1400 + 600*r) ms", "1550 / 1700 / 1970 ms", "PASS", "Direct stale-track scenario; no repeated-seed CI."),
    ("motor_control", "heading grid", "6*(1-r) degrees", "4.5 / 3.0 / 0.3 degrees", "PASS", "Command precision changes; no physical outcome advantage asserted."),
    ("touch", "vertical pitch allocation", "2*(1-r)*draw degrees", "1.5 / 1.0 / 0.1 degrees at |draw|=1", "PASS", "Speed magnitude conserved in controlled vector test."),
    ("strength", "contact outcomes", "physics contact kernel", "not independently sampled", "PARTIAL", "No effect size or confidence interval computed."),
    ("balance", "contact/recovery outcomes", "existing balance kernel", "not independently sampled", "PARTIAL", "No effect size or confidence interval computed."),
    ("throw_power", "maximum feasible release speed", "134.1*(.5+.5*clamp((r-.4)/.6)) m/s", "67.05 / 78.225 / 128.5125 m/s", "PASS", "These are ceilings, not observed cognition choices or typical release speeds."),
    ("throw_accuracy", "horizontal yaw SD base", "max(.15,3*(1-clamp((r-.4)/.6))) degrees", "3.0 / 2.5 / 0.25 degrees", "PASS", "Engine samples a uniform half-width sqrt(3)*SD; no sampled distribution included here."),
    ("anticipation", "receiver velocity lead multiplier", "1 + .5*(r-.70)", "0.775 / 0.900 / 1.125", "PARTIAL", "Code input verified; no receiver prediction-error distribution."),
    ("instinct", "last-three-second shot value delta", "2*(r-.70)", "-0.90 / -0.40 / +0.50 option value", "PARTIAL", "Option value only; selected-action rates not sampled."),
    ("judgment", "defender lane-evaluation input", ".70 + .35*(r-.70)", "0.5425 / 0.6300 / 0.7875", "PARTIAL", "Defensive lane only; no general risk/legality effect claim."),
    ("playmaking", "receiver-space value coefficient delta", ".10*(r-.70)", "-0.045 / -0.020 / +0.025", "PARTIAL", "Option value only; selected-pass rate not sampled."),
    ("finishing", "shot-value delta", ".8*(r-.70) times clearance margin", "-0.36 / -0.16 / +0.20 per margin unit", "PARTIAL", "Option value only; no shot outcome distribution."),
    ("marking", "mark-position blend", ".4 + .5*(r-.70)", "0.175 / 0.300 / 0.525", "PARTIAL", "Aim/option changes tested; assignment success not sampled."),
    ("zone_reads", "exit margin delta", ".65*(r-.70) seconds", "-0.2925 / -0.1300 / +0.1625 s", "PASS", "Legal five-second zone clock is unchanged."),
    ("goalkeeping", "Keeper lateral alignment multiplier", "1 + .5*(r-.70)", "0.775 / 0.900 / 1.125", "PARTIAL", "Target-position change tested; save rate not sampled."),
    ("in_air_ball_pursuit", "nearby-pursuit threshold delta", "6*(r-.70) m", "-2.70 / -1.20 / +1.50 m", "PARTIAL", "Context separation tested; selected pursuit success not sampled."),
    ("live_ball_pursuit", "nearby-pursuit threshold delta", "6*(r-.70) m", "-2.70 / -1.20 / +1.50 m", "PARTIAL", "Context separation tested; selected pursuit success not sampled."),
    ("carrier_duel", "run-through value delta", ".5*(r-.70)", "-0.225 / -0.100 / +0.125 option value", "PARTIAL", "Contact choice changes tested; escape rate not sampled."),
    ("defender_duel", "tackle-commit threshold delta", "r-.70 metres", "-0.45 / -0.20 / +0.25 m", "PARTIAL", "Contact choice changes tested; tackle rate not sampled."),
]
with (OUT / "PRISM_CAUSAL_SENSITIVITY_RESULTS.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["rating", "observed_quantity", "mapping", "low_0.25_mid_0.50_high_0.95", "status", "interpretation"])
    w.writerows(causal)

registry = json.loads((ROOT / "audit/native/rb323/rating-consumers.json").read_text())
(OUT / "registry-rating-summary.txt").write_text(
    "Registry audit: " + str(len(registry.get("ratings", {}))) + " entries.\n" +
    "18 draft ratings still have status=inert and runtime_path/independent_measurement absent.\n" +
    "Stamina, Keeper Skill, and Archery Accuracy remain labeled inert in registry despite new-mode active consumers.\n" +
    "Optional acceleration has no runtime_path/independent_measurement entry.\n" +
    "This is a registry/documentation defect; executable tests and code contain corresponding mechanisms.\n"
)
