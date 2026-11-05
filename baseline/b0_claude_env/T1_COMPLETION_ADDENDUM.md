# T1 completion addendum — B0-P4-DEFAULT (Claude's environment)
Responds to DreLen's T1 conditional acceptance (2026-11-05). Source unchanged; no behaviour, physics, ratings or cognition modified. Branch `claude/t1-b0-evidence`. Status labels: **[confirmed]** measured here; **[unresolved]** discrepancy or open question; **[deferred T2]** intentionally left to T2.

## Item 1. Effective runtime patch and feature-flag inventory
**Source patches [confirmed]** (`source_patch.diff`): `patch_source` rewrites three lines of the Pocket file in B0. Line 3219 Keeper step-on-feet fraction `.95*R` → `0.5*R` (behaviour change, from default `KEEPER_STEP_FRAC=.5`); lines 1780 and 2400 platform wrappers (inert, `PLAT=0`). Original sha256 a078e6b7…, patched b97f9256…. `install()` itself does no further source rewriting (no `CORE_SOURCES`/`exec`/reload in the hook modules).
**Dynamically installed wrappers [confirmed]** (`runtime_install_inventory.txt`, `inventory/*.json`): measured by diffing recursive code hashes of every core class/module attribute between a pristine process (load only) and an installed process (load + install + one B0 game). **30 core attributes are wrapped**, each listed with its full closure chain down to the original:
- Engine (15): acquire, award, begin_hunt, c1_reason, discipline, elapse, first_tackle, foul, freeze, joint_control, new_owner, ready, restart_release, shoot_arrow, tackle, terminal_ground.
- Match (14): `__init__`, aim_error, arrow_decisions, auto_substitutions, c4c2_cont, c4c2_eval, carrier_decision, make_pass, make_shot, plan_pass, pocket_pass_option, step, targets_dead.
- Policy (1): targets — chain bounce_option → block_option → positional_tendencies → original.
- Installers present: pocket4_proto, positional_tendencies_v1, restarts_v1, rules_v03 (and its no-kick wrapper), block_option_v0, bounce_option_v0, plus the Pocket file's own `_final_guard`.
- Not wrapped in B0: `c4c2_decide` (pocket_decide; the Judgement hook is PRISM_JSPLIT-only), `c4c2_targets`, `route_receiver`, `move_players`, `c3_contain/region`. These are PRISM-only installs, as expected.
**Default-enabled systems [confirmed]:** SYSTEMS = roster, rotation, tendencies, restarts, archerfix, arrowlead, throw, pose, shape, condition, jump, windup, foot (13; none switched off). `THROW_SPLIT=1` active (`throwing_v1.SPLIT=True`). `BLOCK_OPTION=1`, `BOUNCE_OPTION=1` read as on.
**Flag reads [confirmed]:** 86 environment keys are read during import, install and a game; none is set in the environment, so all take defaults (full table in the inventory file). This replaces my earlier `flags: {}`, which was a prefix-filtered list.
**Discrepancy found [unresolved — canon]:** `RULES_V03` defaults to 0. Its wrappers are installed but pass through, and the no-kick wrapper is gated by it. **B0 therefore still contains kicking**: short game seed 1 has 3 `ball_action_prepared`, 2 `pass_plan` and 2 `release` events of kind `kick`. This conflicts with DreLen's 3 Nov ruling eliminating kicking. Preserved as executed (item 5); a canon-conformant variant would need DreLen's approval.
**Deferred [T2]:** whether each installed-but-gated wrapper (rules_v03 family, block/bounce options) is a strict pass-through when off; call order within one decision tick; wrapper behaviour under PRISM flags.

## Item 2. File verification [confirmed]
Full pinned git checkout of 2abe497 (worktree), 427 tracked files, `git diff` against the commit shows no changes outside the added `baseline/`, `tools/`, `test_perception_multimatch.py`. The complete tree with blob hashes is `commit_tree_2abe497.txt` (git ls-tree -r). Codex can close its 54-file gap by comparing its blob hashes against this list.

## Item 3. Missing fixtures: provenance found, not added
All three are in `Beastball_Locomotion_1_0_Frozen.zip` (sha256 92208136…, built 2026-10-28 in an earlier Claude session, the Locomotion 1.0 freeze package). Evidence:
- `LOCOMOTION_1_0_MANIFEST.json` (version locomotion-1.0, stack v3.2→v3.7, frozen 2026-10-28) lists 9 file hashes. **All 9 match the files in commit 2abe497**, including `pocket_capability_v37.py` and `beastball_locomotion_v37.py`.
- `results_v37/capability_table_v37.json` matches the manifest hash (8b6f00b1…). Running `build_pocket_capability_v37.py` on it in a throwaway copy reproduces `pocket_capability_v37.py` **byte-for-byte** (dad0b982…).
- `baseline_v30_shipped/beastball_v30_results.csv` (df1b4b92…) is byte-identical in eight archives, including DreLen's own uploaded `Beastball_v3_1_Work_Handoff.zip`.
- With the three fixtures placed in a throwaway copy (never in the repo): `test_beastball_locomotion_v31` OK (5 expected failures), `test_locomotion_freeze_1_0` OK, `test_pocket_capability_v37` OK.
**Requires approval:** adding the three files, unchanged, to the repo at their expected paths. Not done.

## Item 4. Artifacts for comparison (all in `baseline/b0_claude_env/`)
`MANIFEST.json` (environment, commands, source hashes, all 20 runs with log/result hashes), `source_patch.diff`, `runtime_install_inventory.txt`, `inventory/pristine.json`, `inventory/installed.json`, `tests2/*.log` + `tests2_summary.txt`, `runs/*.json`, `commit_tree_2abe497.txt`, `env_flags_nonzero_defaults.txt`, tools in `tools/`. Canonicaliser for log hashes: `tools/t1_capture.py` (`norm`/`canon`: dict keys sorted as strings, floats via repr, compact separators, UTF-8). Codex should recompute with it for a byte-level cross-environment comparison.

## Item 5. B0-P4-DEFAULT preserved exactly as executed [confirmed]
Name adopted: **B0-P4-DEFAULT** = commit 2abe497, no environment overrides, KEEPER_STEP_FRAC=0.5 patch, THROW_SPLIT=1, RULES_V03=0 (kicking present), 13 systems on, Python 3.13.16 / NumPy 2.5.3 here. No variant was substituted.

## Item 6. Summary of status
| Item | Status |
|---|---|
| Same-environment determinism (10/10 pairs) | confirmed (accepted) |
| Effective flags, source patches, wrapper inventory | confirmed by measurement |
| Kicking present in B0 vs 3 Nov ruling | **unresolved, needs DreLen** |
| Full file verification | confirmed here (427/427); Codex's 54-file gap closable via tree list |
| Missing fixtures | provenance confirmed; addition awaits approval |
| Cross-environment byte equality | unresolved; scores match across Python 3.12/3.13 and NumPy 2.3/2.5, hashes not yet compared with one canonicaliser |
| Wrapper pass-through when gated off; tick call order | deferred T2 |

## Decisions requested
1. Approve adding the three fixtures, unchanged, to the repo.
2. Kicking in B0: keep B0-P4-DEFAULT as the historical baseline (recommended), and decide whether the later validated baseline B1 runs with `RULES_V03=1` (no kicking, rules v0.3) or rules v0.3 is evaluated separately.
3. Accept this addendum as closing T1 on my side, with cross-environment hash comparison left to Codex's run.
Stopping here. T2 not started.
