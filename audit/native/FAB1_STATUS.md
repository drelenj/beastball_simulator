# FAB-1 status (resume file; newest section last)
Branch: `claude/native-v0-3-handoff-69stxd` (the session's designated branch; stands in for `claude/native-v0-3`), based on `codex/native-v0` @ a1b1313.
Full matches used so far are counted here against the cap of 40.

## FAB-1a arrow speed: IMPLEMENTED, TESTED (not ACCEPTED). Code commit 3d26f4f.
1. `native/config.py`: `NativeConfigV3` (`native-v0/3`) adds `arrow_speed_ratio` (default 250/27, i.e. 250 m/s at the engine's 27 m/s top speed) and no cap; `NativeConfig` (`native-v0/2`) is untouched and still the default (digest f31b44a1...). Select with `python -m native.run --config-version native-v0/3 [--arrow-speed-ratio X]`.
2. `native/rules.py` shoot_arrow: speed foul only when the config has a cap (v0/2: 30; v0/3: none). `native/port.py` archer motor releases at the config speed (v0/2 literal 29 kept).
3. Tests: `native/test_v3.py` (24 FAB-1a cases: swept collision at 0.3 to 60 m, radius/height/order, step-length independence, loose ball, drag/gravity, end-to-end freeze). Engine flight needed no change: the swept segment test does not tunnel at 250 m/s.
4. Seed 1 full match, arrows only changed (`native/evidence/v0-3/fab1a/seed-001-arrow-only.json`): released 503, missed 244, freezes 161, inert impacts 97. Before (v0/2): 435 / 385 / 14 / 35.
5. Open: QUESTIONS Q-FAB1-1 (is canon the 250 m/s figure or the 5.6 ratio? at 27 m/s they differ: 250 vs 151 m/s). Full matches used: 1 of 40. Next: FAB-1b.

## FAB-1b athlete-owned tackle-to-ground: IMPLEMENTED, TESTED on forced scenarios and short windows (not ACCEPTED).
1. New pure module `native/cognition_v3.py` (selected by `AthleteView.cognition == 'native-v0/3'`; `cognition.decide` dispatches, `decide_v2` is the unchanged v0/2 set). Defender: `press`+`contact='wrap'` (stay with him) or `tackle`+`contact='takedown'` once the believed gap is under 6 m. Carrier: `carry` with `contact` `run_through` / `brace` / `dodge` from believed threats and own-body touch/balance (SELF-1 view fields `own_held`, `own_balance_load`, `own_hold_target`).
2. `native/port.py` (v0/3 only): the engine's hold authorisation, hold mode (`c3_contain`) and escape effort (`c3_escape_effort`) read the athlete's own latest intent; automatic descent stays off; nothing grounds a carrier without a takedown intent. Engine physics, legality and tackle adjudication are untouched. Prior art checked: B0 and Sprint-45 (c64d92e) had no athlete tackle decision, only the engine's automatic hold plus the containment/descent placeholders, so only the engine hold/drive/topple mechanics were reused.
3. Tests in `native/test_v3.py`: takedown grounds the carrier (first_tackle scrim, snapper/tackler set); no contact intent means no hold; wrap contains without grounding; escape effort only on run_through; decision tests; three poison tests; purity (AST) test; 3000-step play window where every hold and tackle traces to a decide() intent.
4. Coverage on 600 s windows (not full matches): seed 1: 23 tackle-count events, seed 3: 12 (v0/2 seed 1 had 5 in a whole match). 10-seed full-match table still to run.
5. Also in the tree (FAB-1c, tests pending): belief-based restart claim/throw/stand decisions and `native/restart_metric.py`; v0/3 Archer no longer releases during a pass in flight (Q-FAB1-2). Full matches used: 1 of 40. Next: FAB-1c tests and checkpoint.

## FAB-1c restart cognition and metric: IMPLEMENTED, TESTED on forced scenarios and short windows (not ACCEPTED).
1. Causes found (seed 1, v0/2, 12000-step window, instrumented): toss timeouts = the claim went to whichever teammate decided first, typically 30 to 95 m from the spot while the nearest stood 2 to 30 m away, so the taker arrived after the 5.5 s window (26 of 26). `rejected:geometry` at admission = nearest-teammate target only 0.7 to 1.5 m away, impossible at the fixed 27 m/s and 1.6 m height, retried every tick until the snap window closed (3 of 3 snap timeouts). `rejected_taker_or_record` = a late throw resolved after the timeout had already replaced the restart. `rejected_by_engine` and most `rejected_geometry` in the match totals are not restarts: they are Archer releases (illegal target; out of range at 29 m/s) and a few live passes.
2. `native/cognition_v3.py` restart decisions (v0/3 only): believed-nearest claim with a per-metre backoff; taker goes to the spot, waits for a legal release, throws to a believed teammate 4 to 34 m from the spot (never the too-close one), last-call space throw stays PLACEHOLDER; opponents leave the 3 m toss clearance, everyone stands onside, two nearest teammates make themselves throwable.
3. `native/restart_metric.py` (read-only) + `restart_metric` in every run result: awarded / released / timeout / superseded per kind, release and timeout rates, and the eligible subset (a taker could reach the spot in the window and a teammate stood at throwable distance).
4. 12000-step windows under v0/3: seed 1 timeouts 3 of 121 (eligible 2 of 117), seed 3: 1 of 104, seed 4: 0 of 102, seed 5: 1 of 111. Same window under v0/2 seed 1: 29 of 115.
5. Also: v0/3 Archer no longer releases during a pass in flight (Q-FAB1-2). `RULE_TO_TEST_MATRIX.json` and `QUESTIONS_FOR_OWNER.md` updated. Full matches used: 1 of 40. Next: full b1+native suite, 10-seed table, replay checks, independent review, manifest.

## Verification state at stop (usage limit reached)
1. V1 met: 246 tests pass; `git diff a1b1313 -- b1 core_src` empty; native-v0/2 seed 1 replays trace 3840682e... / state 411abb0a... / digest f31b44a1...
2. V2 met for seed 1: native-v0/3 trace cacf2405... state d688fcbb..., serial = parallel, null M2 = plumbing absent. V3, V4 met by `native/test_v3.py` and the matrix rows. V5 met: 10 of 10 seeds final, no crash/stall/invariant failure (`native/evidence/v0-3/ten-seed-table.json`). V7: `NATIVE_V0_3_MANIFEST.json`.
3. V6 NOT met: the independent reviewer agent stopped on the usage limit before reporting. See `audit/native/HP-002_NATIVE_V0_3_REVIEW.md` for what remains. Resume there.
4. Not recorded: first/second tackle split (add restart award reasons to the run result, then rerun the table: 10 matches).
5. Full matches used: 14 of 40.
