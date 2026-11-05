# T1 evidence packet (executed by Claude, in Claude's sandbox)
Executed on request from DreLen. Codex should treat this as an independent cross-check and still run T1 in its own environment (HP-001 clarification 9). Branch `claude/t1-b0-evidence`, built on commit 2abe497. No source modified; backups untouched.

## 1. Repository verification (confirmed)
- `git ls-remote`: `refs/heads/main`, `refs/heads/claude/baseline`, `HEAD` and tag `refs/tags/baseline-p4-2026-11-05` all = `2abe497ca82588cb2d8c871a7aab61daaae95c12`. Other branch: `claude/codex-work-package` (HP-001 rev B + regression test).
- Commit 2abe497 contains 427 files; checked out clean (0 modified). Only added files here: `tools/`, `baseline/b0_claude_env/`, and (for one run) `test_perception_multimatch.py`.
- Environment: Python 3.13.16, numpy 2.5.3, Linux 6.18, 2 CPUs. pytest not installable (no matching distribution through the package proxy); tests were run as scripts.

## 2. B0 definition and effective configuration (confirmed)
- Every PRISM/HAND_FIGHT/CATCH_V2/KP_* env flag unset; recorded flags per run: `{}`.
- **Finding: B0 is not stock Pocket 3.** `patch_source` rewrites the Pocket file even with default knobs (KSTEP default .5 differs from its trigger .95). Effective diff (`b0_effective_patches.txt`, original sha256 a078e6b7…, patched b97f9256…): (1) line 3219 Keeper step-on-feet fraction `.95*R` → `0.5*R` (**behaviour change**); (2) lines 1780 and 2400: platform wrappers, inert unless `platform` set. Defaults: NET_R 6, KEEPER_FT 0 (engine default), RULESET 1.0.1, ARCH 10–70 m, ARCH_NEAR 9.
- Also hooked in B0 (always on): throwing, carry-pose release delay, ball shape, condition layer, jump decision, foot rule, roster, tendencies, restarts, rules v0.3, block and bounce options (`install()` order in `pocket4_proto.py`). The env flags the code reads are listed in `env_flags_read.txt` (135 names; includes non-behavioural ones).

## 3. Deterministic replay (confirmed)
Each game run twice, fresh process each (`tools/t1_capture.py`). Hash = SHA-256 of the canonical event log (keys sorted as strings, floats via repr) and of the result dict with wall/cpu fields removed. **All 10 seed/mode pairs replay identically** (log and result hashes equal).
| seed | mode | score A:B | events | log sha256 (first 12) |
|---|---|---|---|---|
| 1 | short | 7:3 | 3789 | 0cc709124037 |
| 2 | short | 3:4 | 2928 | ac1807d2b2c6 |
| 3 | short | 3:4 | 3029 | 262039da9869 |
| 4 | short | 0:10 | 2987 | 9d6f5148b9c9 |
| 5 | short | 2:14 | 2888 | 7d1ca6d1e23d |
| 1 | reg | 49:50 | 27323 | 9194161ec278 |
| 2 | reg | 61:60 | 27677 | 61316a47fe34 |
| 3 | reg | 61:52 | 27752 | 77742297918d |
| 4 | reg | 54:49 | 28041 | 4240279f4364 |
| 5 | reg | 60:26 | 27982 | 6315522c80ae |
Full hashes, flags, per-run wall times: `MANIFEST.json`, `runs/*.json`. Wall time: short 15–19 s; regulation 150–300 s (2 games in parallel on 2 CPUs).
Limits: same-environment replay only. Cross-platform equality not tested.
Observation (not repaired): regulation scores are about 105–120 combined per game, above the flow target of 80–85 averages DreLen set; seed 5 is 60:26.

## 4. Test results (17 files, each as a script, fresh process; logs in `tests2/`)
**Pass (14):** locomotion v32 (OK, 5 expected failures), v33 (3 xfail), v34 (2), v35 (2), v36 (2), v37, unified v30, pocket4_proto (5 tests, 74 s), pose_engine, pose_maneuvers, prism_archer, prism_comms, prism_install (189 s), prism_v012.
**Fail / error (3), all caused by files missing from the repo (not by simulation behaviour):**
1. `test_beastball_locomotion_v31.py::test_v30_unchanged_vs_shipped_results` — FileNotFoundError `baseline_v30_shipped/beastball_v30_results.csv`.
2. `test_locomotion_freeze_1_0.py::test_files_match_manifest` — FileNotFoundError `LOCOMOTION_1_0_MANIFEST.json`.
3. `test_pocket_capability_v37.py` — FileNotFoundError `results_v37/capability_table_v37.json` (module import fails; no tests run).
Consequence: the v3.7 capability table and the locomotion 1.0 freeze manifest cannot be verified from this repo. **Action for DreLen/Codex: locate those files** (they may exist in the earlier locomotion packages) and add them without edits. Several "expected failures" in locomotion tests are declared in the tests themselves.
Not verified: whether the "expected failures" are still the right ones; that is for the physics owner.

## 5. S.fowner regression (confirmed, PRISM_I=1, not B0)
`test_perception_multimatch.py`: match 1 hidden_opp 16517, mean view miss 12.2 m; match 2 13305 and 13.4 m. **PASS.** With the reset line disabled earlier: 1985 and 53.3 m, FAIL. The B0 captures are unaffected because perception is off, and each game ran in a fresh process anyway.

## 6. Not done / out of scope for T1
Golden physics traces (T3), patch-chain map (T2), profiling (T4). Python/numpy are those of this sandbox, not Codex's.

## 7. Requested review decisions
1. Accept B0 as "Pocket 4 defaults, including the Keeper step-fraction 0.5 patch"? Or should B0 also record a variant with stock .95 for comparison?
2. Authorise adding the three missing files once located.
3. Confirm Codex repeats T1 in its own environment and compares hashes (expect equality only if numpy/python behave identically).

## 8. Review decisions received (DreLen, 2026-11-05) and follow-up
1. B0 accepted as defined: Pocket 4 defaults including the Keeper step-fraction 0.5 patch. No stock-.95 variant recorded (can be added on request).
2. The three missing files (`baseline_v30_shipped/beastball_v30_results.csv`, `LOCOMOTION_1_0_MANIFEST.json`, `results_v37/capability_table_v37.json`) are not known to exist anywhere DreLen can reach. They stay missing; the three failing tests remain documented failures, not repaired.
3. Partial cross-check: DreLen's attached `beastball_locomotion_v37.py` is byte-identical to the repo copy (sha256 4668ba4e6a5829c05b112d35252eb04d2253f969c3705ad8a2cf6edcba91afd5). The v3.7 float-control-valve source is therefore confirmed as the one in commit 2abe497.
4. Note for Codex (T3): the capability table's *values* are still present, baked into `pocket_capability_v37.py` (generated from the missing JSON by `build_pocket_capability_v37.py`). Golden traces should treat that module as the authority, and the table can be regenerated from locomotion v3.7 only with DreLen's approval (a regenerated file would be new data, not the original).

## 9. Cross-check against Codex's T1 report (REPORT.md, Codex env: Python 3.12.14, NumPy 2.3.5)
- **Outcomes agree:** all 10 seed/mode scores are identical between Codex's table and mine (3.13.16/2.5.3), including 7–3, 3–4, 3–4, 0–10, 2–14 (short) and 49–50, 61–60, 61–52, 54–49, 60–26 (regulation). Strong sign of cross-version agreement of results. **Not yet established:** byte-level log equality across the two environments. Codex's report gives no hashes in its text; hash methods differ (Codex hashes canonical UTF-8 JSON, mine normalises mixed key types and floats via repr), so hashes are not comparable until one canonicaliser is chosen.
- **Test results agree:** same 14 pass, same 3 fail with the same missing paths.
- **Correction to my section 2 (erratum):** I recorded effective flags as `{}` because my capture filtered by name prefix and missed flags without a PRISM/HAND_/CATCH_ prefix. **Codex is right: `THROW_SPLIT` defaults to 1 (throwing_v1.py line 27, DreLen's 4 Nov throw split, no ball-speed cap).** Other flags whose code default is non-zero and may be active in B0: `BLOCK_OPTION=1`, `BOUNCE_OPTION=1`, `HAND_CONTEST=1` (activation depends on install path; T2 must confirm). Full list of non-zero defaults: `env_flags_nonzero_defaults.txt` (97 lines, includes lab parameters that are not B0 switches). The manifest's `flags: {}` therefore means "no env override set", not "all behaviour flags off".
- **Verification gaps, complementary:** Codex byte-checked 373 of 427 files via blob hashes with no git checkout; I used a git checkout of all 427 files (clean tree). Codex used PYTHONHASHSEED=0 and a cleared environment; I did not set PYTHONHASHSEED and still got identical replays (hash randomisation did not matter for 10 pairs).
- **Proposed closure of T1 acceptance (needs DreLen's approval):**
  1. Adopt one canonicaliser (mine: `tools/t1_capture.py`, functions `norm`/`canon`) and have Codex recompute log hashes in its environment, then compare to `MANIFEST.json`.
  2. T2 produces the verified effective-flag/patch inventory, including the defaults above.
  3. Record T1 as accepted for same-environment determinism; cross-version byte equality becomes a separate result.
