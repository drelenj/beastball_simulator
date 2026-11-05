# Handoff packet HP-001: Codex initial work package
From: Claude. To: Codex. Approved by: DreLen (2026-11-05, ten decisions). Date: 2026-11-05.
Scope: preparation only. **No native rewrite, no cognitive migration.**

## 1. Source revision
- Repo: `drelenj/beastball_simulator`. Baseline branch `claude/baseline`, commit `2abe497` (427 files). Intended tag: `baseline-p4-2026-11-05` (DreLen creates it; pushes to `main`/tags are not possible from Claude's session).
- Physics core: `Beastball Pocket 2 0(1).py` (called Pocket 3; unmodified). Hook layer: `pocket4_proto.py`. Capability layer: `pocket_capability_v37.py`. Condition: `condition_layer_v2.py`.
- Changed files in this packet: none beyond this document. Backup files (`*_before_*.py`) are **kept** until baseline outputs are verified (decision 3).
- Unresolved before you start: DreLen must create `main` and the tag. Until then, work from `claude/baseline`.

## 2. Two baselines (decision 5)
| ID | Definition | Status |
|---|---|---|
| **B0 historical** | commit 2abe497 run with every PRISM flag off (stock Pocket 4: Pocket 3 core + throwing, carry pose, ball shape, condition, jump, foot, roster hooks) | to be frozen by Task 1 |
| **B1 validated PRISM I** | commit TBD, full flag stack, after the validation gates in HP-002 (Claude) pass | **not yet existing**; native work must not target B1 behaviour until it does |
Full PRISM stack for reference (all provisional): `PRISM_I=1 PRISM_OFFBALL=1 PRISM_TEAMVIEW=1 PRISM_FREEVIEW=1 PRISM_JSPLIT=1 PRISM_OFFACT=1 CATCH_V2=1 PRISM_KEEPER=1 HAND_FIGHT=1`.

## 3. Tasks, files, acceptance criteria
**T1. Repo hygiene and B0 golden pack** (deliver first)
- Verify the clone builds and `python3 -m pytest` (or each `test_*.py`) runs; list failures and which pre-date this baseline. Do not fix behaviour.
- Freeze B0 outputs: seeds 1–5, `--short` and one regulation game each, PRISM flags off. Store event-log hash, score, key counts, wall time. Output: `baseline/b0/` + `baseline/b0/MANIFEST.json` (commit, command, seed, python version, hashes).
- Accept when: two runs per seed give identical hashes on the same machine; manifest lists every command; Python/numpy versions recorded.

**T2. Patch-chain and override map**
- From `pocket4_proto.py` (`patch_source`, `install()` order around lines 407–572, all `Match.*`/`Policy.*` assignments and wrappers), produce a table: target symbol, original location (core_src file/line), each wrapper in order, flag that enables it, final behaviour.
- Include wrapper order for `Policy.targets`, `Match.c4c2_targets`, `Match.route_receiver`, `Match.move_players`, `Match.c3_contain/c3_region`, and the `pocket_decide` source replacement.
- Accept when: every `reps` string in `patch_source` is listed and confirmed to match exactly once in the source; unmatched/silent no-op patches are flagged; a diagram or table of call order for one decision tick is included.

**T3. Physics golden traces**
- With PRISM flags off, record tick-level traces (positions, velocities, contact events, ball state, condition state) for fixed scenarios: sprint, cut, tackle, catch, ball flight, bounce, fatigue. Reuse `engine_check_v0.py`/existing drills where possible.
- Accept when: traces reproduce bit-for-bit on rerun; tolerance proposal (absolute and relative) written for later port comparison; scenarios listed with inputs.

**T4. Profiling and performance baseline**
- Profile B0 and the full PRISM stack (cProfile and a line/time breakdown). Known: full stack runs about 4–5× slower; suspected cause is `S.with_view` in `prism_field_v0.py` (world-state swap per perception tick) and ball-belief prediction. Confirm or refute with evidence.
- Accept when: per-function inclusive/exclusive times for one regulation game each; games/hour on stated hardware; memory peak; a ranked bottleneck list with measured share.

**T5. Experiment runner and telemetry spec**
- Design (spec first, small prototype allowed) a headless runner: config file + seed management, paired and independent runs, resumable batches, compact machine-readable telemetry, summary statistics with confidence intervals.
- Telemetry must include a per-decision trace slot (options, values, noise draws, ratings used) so cognition can fill it later.
- Accept when: spec reviewed by Claude; a prototype reproduces a B0 baseline run through the runner with identical results.

**T6. Native interface design (paper only)**
- Draft interface contracts: `SimState`, `Observation`, `BeliefState`, `ActionIntent`, `MotorCommand`, `PhysicalOutcome`, `DecisionTrace`. Three layers per decision 2: **cognitive selection (PRISM) → motor execution (Motor Control: aim, placement, execution error using ratings and Focus mechanics) → physical resolution (engine)**. Cognition receives only `Observation`/`BeliefState`, never `SimState`.
- Accept when: each existing mechanism is assigned to one layer in a mapping table (e.g. catch timing, hand landing in the contact band, throw release error, carry-pose transition cost) with open questions listed. **No code in the engine.**

## 4. Out of scope for this packet
Wholesale rewrite, porting any PRISM module, changing ratings/weights/noise strengths, removing backup files, deleting legacy tables, modifying `Beastball Pocket 2 0(1).py`.

## 5. Claude's parallel work (so we do not collide)
- **HP-002 (Claude):** decision-ownership audit plan and execution (cognition side), hidden-state perturbation tests with controlled random streams, PRISM I validation matrix, constants registry, formation-free experimental mode on branch `claude/formation-free`.
- Files Claude touches: `prism_field_v0.py`, `offball_actions_v0.py`, `positional_tendencies_v1.py` (formation-free flag only), `prism_*`, new test files. **Codex should not edit these** without a handoff.
- Codex-owned: `baseline/`, `tools/` (runner, profiling), `docs/native/`, golden-trace scripts.

## 6. Review requests back to Claude
1. Does the T2 map match my understanding of wrapper order (Policy.targets → PRISM wrappers → c4c2_targets → route_receiver → OFFACT re-apply)?
2. Are the T3 scenarios sufficient for the contact and catch paths I changed (CATCH_V2, HAND_FIGHT)?
3. Does T6 put hand-landing aim (Focus, Blocking technique) in Motor Control rather than cognition or engine?

## 7. Return packet format (Codex to Claude, same shape)
Source revision (commit), changed files, commands run, tests and results with hashes, unresolved issues, requested decisions. Per decision 9: link to results, not summaries alone.

## 8. Known defects at this revision (do not "fix" in the port)
S.fowner stale-state bug fixed in this revision (earlier multi-match-per-process results suspect); Duel lab saturated; ENGAGE almost never chosen; contact band unverified at match level; `mate_prior_true` kick-off leak; `derive()` per-rating jitter (blocks a true uniform-0.70 run). Details: `PRISM_STATUS_REPORT.md`.

## 9. Requires DreLen's approval before implementation
1. Create `main` and tag `baseline-p4-2026-11-05` on commit 2abe497.
2. Give Codex write access to the repo (collaborator invite or token) and agree the branch prefix `codex/`.
3. T4: permission to install profiling tools (e.g. `py-spy`) in Codex's environment.
4. T5: choice of telemetry format (proposal: JSON Lines plus a summary CSV) and whether Codex's environment may run regulation-length batches.
5. T6: any change to Motor Control semantics beyond what exists (the plan only documents the current mechanics).
6. Whether B0 should be run on the exact Python/numpy versions on DreLen's phone, or on Codex's.
