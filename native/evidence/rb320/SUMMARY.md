# RB-3.20 evidence (PROVISIONAL, claude/rb-3-20-physics-tactics; Part 1 code 014f774 (RB-3.20a), Part 2 code 7b0e2ee (RB-3.20b); baseline RB-3.19 s3 1132507)
Runs: real seeds 1/3/5 and control 1, python -m native.rulebook.reach_run with rb3_carrier_moves_enabled, rb3_handoff_block_enabled and
rb319_ball_in_play_enabled ON. p1 = after Part 1 (worktree at 014f774), p2 = after Part 2 (worktree at 7b0e2ee). Raw logs (gzipped):
native/evidence/rb320/runs/{p1,p2,identity_fixoff,identity_fixon}/{real,control}/raw-*.json.gz. Metrics: diag/metrics.py -> metrics.txt / metrics.json.

## OWNER BRIEFING
1. Accomplished: Part 1 (IMPLEMENTED, TESTED) - physics scenario and real-ball comparison (PHYSICS.md); one DEFECT found and fixed for
   native-rb/3: bounces delivered a restitution of .84-1.06 against the stated .7746 because the 100 ms step reflected the end-of-step
   velocity; now the contact instant is solved and the stated rules apply there (.772 measured). Calibration items listed, not changed.
   Part 2 (IMPLEMENTED, TESTED) - A4 horizon 0.5 s; B1 handoff only if the receiver is >= 0.5 s freer (time-to-contact) or >= 2 m/s
   faster, never back to the giver within 2 s.
2. Can do now: after Part 1 the real median team score is 88.0 (inside 75-90) and pass-out-of-bounds ends 20.2% of possessions (was
   23.2%); missed-ball recovery by the passer's team 27% -> 30%.
3. Unproven / worse: possessions per team stay ~167 (target 100-150). Part 2 made the targets worse on this sample: median 68.5,
   possessions 178.5, pass out 25.9%. Missed-pass exit distance barely changed (55.8 -> 55.1 -> 52.8 m): travel is flight-dominated
   (calibration, not a defect). One 4-match sample per stage.
4. Blocking: BEHAVIORAL questions for Claude (QUESTIONS_FOR_CLAUDE.md). No owner questions. For Codex: the c4c_path forecast keeps the
   end-of-step reflection (negligible at 5 ms); the fix is a source patch in native/substrate.py (ball_ground.PATCHES).
5. Recommended: the lead decides whether to keep Part 2 (question 1) and whether to calibrate air drag (PHYSICS.md proposal 1).

## Identity and guards
- native-v0/2, native-v0/3, native-rb/2: trace/state/config hashes identical to 185b557 (all six rows of native/evidence/rb3-reach/legacy-hashes.txt), after Part 1 and after Part 2.
- Flags off, rb319 off, carry_release_radius_m=0.0, rb320_exact_bounce=false: real seed 1 = 93b1f57e268ee6c4... / b9962ddfb23dbc96... (RB-3.16, exact).
- Same with the DEFECT fix ON (default): 9117aa82e02248cb12f9f2b78abedae098e79348a06bf444a32de22cbf1f1e12 / 37c9cd57bb79b3426f4869d7de7ba177c63759c132779123854351bd550bd9fc, 56-69, 38928 steps (changed because bounces now keep the stated restitution).
- Full suite after the last code change: 641 passed (13 new in test_rb320.py; one RB-3.19 test, test_b1_pressured_carrier_may_hand_off_even_backward..., re-staged so the backward receiver is also >= 0.5 s freer, per the new B1 rule).

## Before/after (real seeds 1/3/5 unless noted)
| metric | RB-3.19 s3 | after Part 1 (p1) | after Part 2 (p2) |
|---|---|---|---|
| team scores (real) | 70-90, 78-81, 113-100 | 95-84, 92-75, 82-109 | 60-100, 64-67, 70-106 |
| control score | 63-80 | 106-60 | 118-56 |
| median team score (real, 75-90) | 85.5 | 88.0 | 68.5 |
| possessions per team (100-150) | 166.0 | 166.7 | 178.5 |
| ends: pass out of bounds / intercepted / goal | 23.2 / 13.4 / 14.2 % | 20.2 / 15.1 / 14.1 % | 25.9 / 14.3 / 11.7 % |
| ends: other out / carrier frozen / restart throw lost / second tackle | 9.6 / 8.2 / 8.1 / 6.6 % | 11.6 / 8.5 / 7.3 / 6.2 % | 8.6 / 7.4 / 10.0 / 5.6 % |
| missed passes leaving untouched: median distance / time to exit | 55.8 m / 1.95 s | 55.1 m / 1.99 s | 52.8 m / 1.60 s |
| missed passes recovered by the passer's team | 149 / 543 (27%) | 157 / 529 (30%) | 220 / 692 (32%) |
| handoffs per match (real) | 304 | 297 | 67 |
| open-play completion | .514 / .477 / .451 | .526 / .548 / .523 | .492 / .497 / .525 |
| passes released (real, 3 matches) | 761 | 795 | 954 |
Full cause tables per stage: metrics.txt.

## Per-match hashes (trace / state): hashes.txt
p1 control-seed01 {'A': 106, 'B': 60} 6d60731dae1a61098925cbb4050bb71097fcab4048197a585e31cf92b3937c57 ba0bea18d76f64930527f40d6b91a10d63765ccf4118d09e65081266c5e6ffbf 34261
p1 real-seed01 {'A': 95, 'B': 84} 86d075ba218c54c04e35bdb19762c5099f42846fb967c97e091490a760953877 9b312336f5d2f77ba63a9e22c932e148801a19e4588c74806d3489aa2e095d2d 34724
p1 real-seed03 {'A': 92, 'B': 75} a8293ec5a7ab0e7271d1e1b5bee9bd0b1e28fdcbad874334552da64348a0b28f eb340b80b91a4aff6bb670e38c5143bcb225489230f0cc302e6516880ae60b69 34779
p1 real-seed05 {'A': 82, 'B': 109} 996b7c3c5e34c34a6563ecee25d399173e61349066c989d5e01babcd8842e57a c020727228862396e278ae8778446fbfc7984da887deac822804371181cdd49e 34708
p2 control-seed01 {'A': 118, 'B': 56} 2978c19338fbc1188ec34bb156ddf22babf0ee5d923638fcc5c0c9744cc4746a c95ab35d2c57719df50f3e212bf2d7397954a3325699f613f880e100fa9875be 35015
p2 real-seed01 {'A': 60, 'B': 100} f02275ee74f6aceb17478d59be3fc4a9d11d2d46a7e88474818d87f531dc4e8f 7197b4ee3f526889ddcdfc78ecee3ff35bb9d943dd7197848288c20aaf5ac31a 35744
p2 real-seed03 {'A': 64, 'B': 67} c6c3e0b58d9132c4e294d0822914ce49a420cca30dfe2953426fe3a27d28b26f 600f197a4b988ea3d5159fc72ef6c7c47f56b66da8ebc62ea61c56daca3e89ec 34550
p2 real-seed05 {'A': 70, 'B': 106} 451d907fcc298725b63fc8f8077d9603e54f9a2d765a269e9ada84f13f570a5f a67ad305c58ff39f41977498e2af438ff82342a14690b83d49a787dd9dd6aa05 35127
identity_fixoff real-seed01 {'A': 74, 'B': 92} 93b1f57e268ee6c436fae47109e4e2987cfdf7024df5575b6405e119c5ed32d7 b9962ddfb23dbc96551258ea6c2132565804d22ec1b0c87295e3f3ff37d59854 40468
identity_fixon real-seed01 {'A': 56, 'B': 69} 9117aa82e02248cb12f9f2b78abedae098e79348a06bf444a32de22cbf1f1e12 37c9cd57bb79b3426f4869d7de7ba177c63759c132779123854351bd550bd9fc 38928
