# FAB-1 status (resume file; newest section last)
Branch: `claude/native-v0-3-handoff-69stxd` (the session's designated branch; stands in for `claude/native-v0-3`), based on `codex/native-v0` @ a1b1313.
Full matches used so far are counted here against the cap of 40.

## FAB-1a arrow speed: IMPLEMENTED, TESTED (not ACCEPTED). Code commit 3d26f4f.
1. `native/config.py`: `NativeConfigV3` (`native-v0/3`) adds `arrow_speed_ratio` (default 250/27, i.e. 250 m/s at the engine's 27 m/s top speed) and no cap; `NativeConfig` (`native-v0/2`) is untouched and still the default (digest f31b44a1...). Select with `python -m native.run --config-version native-v0/3 [--arrow-speed-ratio X]`.
2. `native/rules.py` shoot_arrow: speed foul only when the config has a cap (v0/2: 30; v0/3: none). `native/port.py` archer motor releases at the config speed (v0/2 literal 29 kept).
3. Tests: `native/test_v3.py` (24 FAB-1a cases: swept collision at 0.3 to 60 m, radius/height/order, step-length independence, loose ball, drag/gravity, end-to-end freeze). Engine flight needed no change: the swept segment test does not tunnel at 250 m/s.
4. Seed 1 full match, arrows only changed (`native/evidence/v0-3/fab1a/seed-001-arrow-only.json`): released 503, missed 244, freezes 161, inert impacts 97. Before (v0/2): 435 / 385 / 14 / 35.
5. Open: QUESTIONS Q-FAB1-1 (is canon the 250 m/s figure or the 5.6 ratio? at 27 m/s they differ: 250 vs 151 m/s). Full matches used: 1 of 40. Next: FAB-1b.
