OWNER BRIEFING — RB-1 BLOCKED CHECKPOINT
1. Implemented and pushed rules/engine checkpoints for steps1–6, with61 passing RB forced-scenario tests. Step7 supplies this blocked report and manifest. RB-1 is not complete or ACCEPTED.
2. Native v0/2 still runs and replays its exact required hashes. RB can exercise clocks/breaks/timeouts, roster/injury hooks, shorthanded discipline, arrows, scoring and review in forced scenarios and bounded windows.
3. Full RB replay and the five full-match seeds are not proven. The scoped matrix records incomplete coverage and workflow gaps, including final/break review windows, natural contact paths, recovery execution and major goal-line restart liveness.
4. Blocking: unchanged Native v0/2 restart intents remain inside the placeholder ball-centred witness used to enforce ratified5m pre-live marking. The seed1 bounded run stops advancing after5.375 live seconds and trips the120s dead-progress watchdog. Changing athlete decisions is explicitly outside RB-1 scope.
5. Recommended: first confirm the marking witness. If correct, authorize a narrow restart-legality intent change or have Claude supply it now without waiting for full FAB-1. Keep the5m rule and intent ownership intact; then finish uncovered scenarios and full validation. No full RB batches were launched against the known failure.

## Source and scope

Branch:codex/rulebook-1, based on a1b131379845322bbc9970ad667a6d68dec10dd7.
Implementation freeze:cd22294 (restart admission freeze; full SHA in manifest).
FAB-1 was neither awaited nor rebased; it is not built. All policy/decide code and accepted b1/core.py/runtime.py/g1.py are unchanged. Frozen B0 hashes pass427/427. Shared Native changes are only explicit profile installation and driver factory/planned-pause hooks; RB rules live in native/rulebook.

| Step | Pushed checkpoint | Evidence / limits |
|---|---|---|
|1 clocks/breaks/ends/timeouts|8da72c1; planned-pause audit a3b583a|Real break/Hunt/snap/timeout scenarios;135s of legal consecutive timeouts does not falsely trip watchdog.|
|2 substitutions/injury hook|e7de7b6|Dead-ball admission, returning players,12-field limit plus Archer, forced injury/head evaluation, named reserve and fallback.|
|3 exclusions/discipline|4086634; admission audit0efe481|Game-time windows, shorthanded play, delayed DQ replacement, injury exception and bypass rejection.|
|4 Archer quota/execution|b8d22a8|250m/s ratio, swept impacts,15 arrows, own-half admission, resource reset and captured indicators. Some complete recovery/freeze sequences remain unproven.|
|5 scoring|85f0e90; fixture correction d4a2318; restart-attempt accounting602a766|Flat default, banded switch and exact10/20m boundaries, carry/own-goal rules and attempt records. Initial fixture failures retained, not hidden.|
|6 review|9bdfbcd; corrections48e578f|Strict>5cm, binary Keeper protection, won/lost resources, corrected restarts including own goals and out-of-bounds corrections. Review-window workflow remains incomplete.|
|7 report/manifest|This delivery|BLOCKED evidence, not an acceptance manifest.|
|Restart admission audit|cd22294|Readiness before marking; distance from ball, not moving taker; explicit placeholder witness.|

The initial scoring test failure used body-centre distance rather than the actual hand/ball release point. Fixtures were corrected; expected point values were not weakened. Raw initial and corrected logs are retained.

## Exact blocker

The ratified distance is5m. PLACEHOLDER witness: opponent proximity to the restart ball, excluding the designated tackler. The unchanged restart branch produces `restart_position` intents inside that ball-centred radius. This witness is an implementation assumption, not additional canon. Existing snap-readiness checks now run before marking admission, fixing an engine ordering error. The bounded reproduction still stalls after that fix. RB release admission sanctions `marking_pre_live`. Repeated retakes produce exclusions while the game clock is stopped, so their game-time exclusion windows cannot expire. No autonomous repositioning, early substitution, clock advancement or forced release was used to escape.

The regression `native/rulebook/test_boundary.py::test_restart_intent_inside_placeholder_ball_clearance` pins a selected illegal-clearance intent and its sanction. It is not a passing full-match test. The bounded integration reproduction independently hits the watchdog.

Current seed1 reproduction:4000-step ceiling;5,375 live ms;137,075 physical ms. Config digest matches the manifest.0 breaks and0 timeouts occur, so the stall is not a planned-pause false positive.

| Window | Breaks | Timeouts | Minors | Majors | Exclusions | DQs | Quota resets | Reviews | Injury flags | Substitutions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|Seed1, bounded, BLOCKED|0|0|55|0|13|0|27|0|0|2|

The2 substitutions are initial additional-field roster admissions, not in-play injury replacements. Fouls:53 marking_pre_live,1 illegal_release,1 archery_target. Bands:A no attempts;B two20plus attempts, zero goals. All other band counts zero. This table is diagnostic short-window evidence, not V5's five full-match table.

## Validation

Combined command:`.venv/bin/python -m pytest -q b1 native`.
258 tests passed (197 existing +61 RB),23 subtests passed,155.29s.
RB-only command:`.venv/bin/python -m pytest -q native/rulebook`.
61 passed,8.27s. Scoped rule matrix:RB1_RULE_MATRIX.json; original Native0 matrix remains explicitly scoped to native-v0/2.

V1:TESTED preservation. Native v0/2 config digest f31b44a1eb787f14c9d606be74fa40658c6b7b9772ee1e882b075b856edc3035.
Both full seed1 preservation replays match (final replay149.826s wall time):
Trace3840682e22692e597bc1419aa298337201e86db2d35f7208c5c9e50e9a99a142
State411abb0a4bab0b812bc5e2e010f03d22f726ff32fdcebcb7df6c3a5beac8aec9

V2:PARTIAL only.100-step RB serial/two-worker/plumbing-absent windows agree; no full RB serial/parallel proof.
V3:PARTIAL. Forced conformance exists, with coverage gaps and placeholders explicitly recorded; not every rule/workflow is established.
V4:TESTED forced view/belief poison, captured status and JSON replay; no new live callback or hidden-state channel is delivered.
V5:BLOCKED.0 full RB matches started; no five-match completion claim.
V6:This blocked owner report and manifest; no quality, balance or emergence claim. Nothing is ACCEPTED.

## Config and budget

native-rb/1 flat default digest:d1e04019fe9851d718c0ac116c109dd2e201f51202bfbb36367330dc63239e16.
Banded switch digest:9411f3771f349f8053eee3faba4e4e6c43455210cfafcc8d7a9af86a52b82127.
New immutable config includes ratio250/44.7, actual top-speed standards44.7,15 arrows,5 freezes, configured bands, break/timeout durations and5cm review tolerance. Complete config is in NATIVE_RB_1_MANIFEST.json.

Full-match budget:2/20, both successful Native v0/2 preservation replays.0 full RB starts. Bounded4000/100-step checks do not count as full matches. Failed full attempts would count before execution; none were concealed.

## Reproduce without full matches

```bash
.venv/bin/python -m pytest -q b1 native
.venv/bin/python -m native.rulebook.reproduce_blocker
.venv/bin/python -m native.rulebook.check_replay
.venv/bin/python -m native.rulebook.run --seed 1 --max-steps 1000 --out /tmp/rb-short.json
```

The structured blocker reproducer catches only the expected restart-stall failure and writes `blocked:true`; it does not declare a completed match. Native v0/2 remains available through the existing native.run entry point. No rule was relaxed to make the new build finish.

## Remaining limits

See the scoped matrix and QUESTIONS_FOR_OWNER.md for exact placeholders. These include panel anatomy, procedural setup/team nominations, unspecified DQ/overflow/review-budget details, and review windows at break/final completion. Natural frozen/dead-ball contact detection, complete recovery execution and major goal-line restart liveness require more work/evidence. The blocker does not imply that a cognition patch alone completes every acceptance item.

Implementation source freeze: cd22294b16ff30af9363edfffe27ed56d4800384. Report/manifest commit follows this source freeze. Matrix has43 rows; all non-null test references resolve to collected tests.
