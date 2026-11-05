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
