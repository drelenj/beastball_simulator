# RB-3.14 evidence (PROVISIONAL, claude/rb-3-14-release-timing; code eaf987e; baseline RB-3.13 3fd4843)

## OWNER BRIEFING
1. Accomplished (IMPLEMENTED, TESTED): (1) each perceived opponent's own acquisition reach (public body size exposed in the view as body_reach; unperceived opponents are not considered; fallback = own-reach estimate if absent); (2) lane check advanced over the release time (engine pass_release_ms, 250, exposed as pass_release_ms, plus any pending-command time left) and then the ball's travel, sampled from the release point; an opponent within reach of the release point makes every pass unsafe and counts as pressure; (3) escape carry (+-45, +-90 deg, 15 m) kept, with a tie-break away from the nearest opponent; (4) free run by typical-athlete kinematics (8.75 m/s^2, top 0.88 x 31.2928, from the opponent's believed velocity) minus a 1.0 m contact buffer. Full suite 562 passed (8 new in test_rb314.py); hashes of native-v0/2, v0/3, native-rb/2 identical to 185b557. No RB-3.12/3.13 test needed changes.
2. Can do now: a lane clear now but blocked at release is rejected (and passes under the old timing); a defender within reach of the release point blocks every pass and the carrier goes lateral; free run differs between a still and a closing defender and matches the kinematics; a tall perceived defender blocks a lane a control-sized one does not; unperceived is ignored.
3. Results are mixed and mostly short of the targets: interceptions within 3 m of release 111 -> 84 on real (overall rate 27-30% -> 21-26%); completion .59-.63 -> .61-.68; carry attempts 64-78 -> 74-98 but carry goals 3/3/1/5 -> 3/6/2/0 (control 5 -> 0); possessions per team 165 -> 174-185 (target ~100, wrong direction); scores lower (real 24-16, 30-43, 15-35; control 10-13); median interception distance up (2.4-3.0 m); second tackle on the receiver share ~.30 (was ~.27). Not tuned.
4. Blocking: BEHAVIORAL questions for Claude in QUESTIONS_FOR_CLAUDE.md. No owner questions.
5. Recommended: lead reviews questions 1 and 4; the remaining interceptions are no longer mostly adjacent-defender throws (84 of 168 are within 3 m), so more analysis of the interception cases is needed before more changes.

## Before/after (RB-3.13 -> RB-3.14), real 1/3/5, control 1
| metric | RB-3.13 | RB-3.14 |
|---|---|---|
| scores | 14-36, 14-39, 23-28, 26-40 | 24-16, 30-43, 15-35, 10-13 |
| open-play completion | .617/.588/.599/.629 | .678/.676/.639/.611 |
| passes / intercepted | 193/56, 211/63, 187/53, 221/59 | 236/53, 244/52, 227/59, 234/63 |
| intercept rate | .29/.30/.28/.27 | .23/.21/.26/.27 |
| intercepted within 3 m of release | 37/37/37/36 | 28/26/30/32 |
| median intercept distance m | 1.95/2.46/1.87/1.75 | 2.70/3.03/2.85/2.42 |
| carry attempts | 64/78/68/78 | 74/98/92/83 |
| carry goals | 3/3/1/5 | 3/6/2/0 |
| possessions per team | 165/165.5/164.5/167.5 | 173.5/178.5/185/181 |
| share ending in attempt | .246/.305/.264/.257 | .242/.238/.243/.210 |
| second tackle on receiver | 40/150, 46/173, 56/197, 63/260 | 60/200, 80/244, 75/253, 76/257 |
| wasted freezes (not carrier) | 96/94/101/92 | 85/111/99/89 |
| arrows during holds | 0 | 0 |
Tables: diag_extra.txt, diag_output.txt; tools/measure.py output reproduced from the raw logs.

## Constants: top of the B-5 section in native/cognition_rb3.py (new: TYPICAL_ACCEL 8.75, TYPICAL_TOP .88*31.2928, CARRY_CONTACT_BUFFER_M 1.0).
## Per-match hashes (trace / state)
- real1 24-16 steps 33888: 517baf322a9081ba159170848360425eb175e5ef3cbafaed022f229b66d1e8b2 / da85176ce1e2325dc3673b90791134146fee21a043d01188d21e7004fd99ac31
- real3 30-43 steps 35356: 02cbdb2ce8a7e725f7f0b2e4663859d0b854219cc801e9e5af6bd594073f5737 / fafe0d943e8eb513896954af4a5926bf3ce5100ea416dd590edfcf8fa33f0430
- real5 15-35 steps 34747: e28fffde303c84d1b3a1d2493aa30201cde65876c19ff6d822879a43b8e64b49 / 5c8114e1f591f350add62b7810b10fb1fbf78d373016a444a00281381610655c
- control1 10-13 steps 35116: e5308509d7f8e839439bcc7c5a77e5c899ec8e2d81300921dab6cf4b685258c6 / 86bbd6754ceecb774f7824b77987f5d370a4585303d289981679d8c889c7fe7e
Raw logs: native/evidence/rb314/runs/{real,control}/raw-*.json
