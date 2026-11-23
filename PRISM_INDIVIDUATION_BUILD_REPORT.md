# RB‑3.23 PRISM individuation build report

## Owner briefing

1. An opt-in experimental rating path now runs through the existing PRISM view, belief, decision, motor and physical execution stages.
2. All 18 draft ratings have separate first-pass mechanisms and isolated causal checks. The canonical workbook is unchanged. Independently authored inputs are supported when available.
3. The limits are in the design record. Several cognition tests establish a change in option valuation or aim, and full-match replay establishes repeatability for one fixture. Performance and tactical effects across the league remain unproven. Injury susceptibility and generation remain staged.
4. No canon change is requested by this work. The source workbook lacks the independently authored technical and mental ratings.
5. Give the independent reviewer the handoff and compare selected-action and physical effects under one-rating experiments before considering promotion.

## Source and status

- Authorized, verified parent `eb30f605f24b906777b88d6cb3a552b3584639ef`. It has the exact tracked tree of Claude's RB‑3.22 tip `e6ca6a4e3bc7e76493d6aa2999acb48f4bf9dcc5`. Owner authorization established the experimental parent.
- Implemented source and developer tests `32ef9dad14ee9407e32d4214edd541867c9b7a6e` on `codex/rb-3-23-prism-individuation`. The implementation file list is `git diff --name-only eb30f60 32ef9da`. No frozen engine source, historical replay fixtures or accepted B1 files were edited.
- Consumer registry `audit/native/rb323/rating-consumers.json`. Candidate references refer to parent line numbers. The runtime annotations distinguish matches found by static search from confirmed active reads. The registry is a static cross-reference with targeted runtime validation.
- Mechanisms, data provenance and behavioral limits `audit/native/rb323/DESIGN.md`.
- Independent executable checks `PRISM_INDIVIDUATION_TEST_HANDOFF.md`.

## Compatibility and replay evidence

The default config omits the new mode key from its record. The explicit compatibility runner selects that same configuration. The experimental config records its mapping version and effective fatigue coefficient. The behavioral fingerprint includes the active ratings and excludes staged Durability/Injury. Roster config fingerprints still record externally supplied metadata.

Two real-roster seed 1 matches with individuation enabled finished, each with every restart closed. Both scored 67–123 in 34,354 steps. Their trace was `da8e42307e99a2bab2d7925c5903664fd617d19b9b441a1ce49530ff3b1f219d`, state was `291c0baff747503c522643fc0c86f57b0403365c6f1bda481c51eb8a08a20d14`, and config was `51362523dadf2ddcfd41a2af08b3e7da9f579f2819511df309dd00436ab44c4b`. Full-match results are in `audit/native/rb323/evidence/`. The difference from RB‑3.22 is a single-fixture observation.

## Tests and performance

The 37 focused checks passed. The suite includes draft loading and validation, one-rating options and selected actions, seeded sensor errors, deterministic replay, release vectors, stamina, opponent-view isolation, fingerprinting and rejection of kicking. Existing regulation fixtures cover restarts, freeze, immunity and substitutions. Coverage in the enabled mode is limited to the new scenarios and the full-match fixture.

The six 3,000-step historical cases matched their archived trace, state and configuration hashes. Standalone compatibility-mode real and control seed 1 both finished and matched the original RB‑3.22 gate hashes. The full match files and the six legacy rows are committed in the evidence directory.

The bounded same-machine comparison alternated mode order over seeds 1 and 3 at 1,500 executed steps per case. Median process CPU was 5.00 ms per step in compatibility and 4.73 ms with individuation enabled. Different decisions produce different event loads. This is evidence that the tested windows showed no per-step slowdown, with no general speedup claim. The enabled full-match runs took 181.997 and 176.068 wall seconds each. The full compatibility runs and the benchmark's raw inputs, hashes and process times are in the evidence directory.

The first full suite identified a v3 cognition import allowlist violation. Commit `32ef9da` keeps the rating access inside the existing cognition interface. The original purity test and all 37 individuation tests passed after that correction. The two full enabled replays on the corrected commit reproduced the pre-correction hashes. The full suite rerun (`python -m pytest -q b1 native`) finished with **699 passed, 1 warning, 23 subtests passed in 810.59s (0:13:30)**. Raw outputs are `initial-pytest.txt`, `focused-pytest.txt`, and `pytest.txt` in the evidence directory.
