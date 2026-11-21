# RB-3.19 evidence (PROVISIONAL, claude/rb-3-19-ball-in-play; code be0d1dd; baseline RB-3.18 5e1917d)
Stages are config selections of one code version: s1 = rb319_ball_in_play_enabled=true rb319_parts="A1"; s2 = all of A (A1A2A3A4); s3 = s2 + rb3_handoff_block_enabled + rb3_carrier_moves_enabled. "rule" = RB-3.18 rule only (carry_release_radius 3.0, all flags off; baseline, native/evidence/rb318/runs/rule). Per-stage raw logs: native/evidence/rb319/runs/{s1,s2,s3}/{real,control}/raw-*.json.

## OWNER BRIEFING
1. Accomplished (IMPLEMENTED, TESTED): A1 toss speed by distance + release-time lane check + in-field space throw; A2 carry/escape/truck aims 2 m inside every line (goal mouth exempt); A3 two-nearest-teammate pursuit of a loose ball; A4 pass depth safety; B1 handoff rule; B2 up-to-two blockers; B3 truck/stiff-arm gating by tackler time-to-contact, stretch unchanged. Full suite 628 passed (15 new in test_rb319.py; one RB-3.17 block test fixture moved the blocker ahead of the carrier to follow the new B2 rule). Flags off + rb319 off + carry_release_radius_m=0.0: real seed 1 reproduces 93b1f57e268e.../b9962ddfb23d... (score 74-92, 40468 steps). native-v0/2, v0/3, native-rb/2 hashes identical to 185b557.
2. Can do now: boundaries per match fell 244 -> 176 (A1) -> 130 (A1-A4); tosses leaving the field 50 -> 7 per match; median team score 71 (rule) -> 59.5 (A1) -> 71 (A1-A4) -> 80.5 (with Part B, inside 75-90).
3. Unproven / short: possessions per team 158-170 (target 100-150) even with Part B; open-play completion 0.44-0.55, no better than baseline; missed-ball recovery by the passer's team barely moved (26% -> 28%); handoffs about 304 per match; single measured run per stage (4 matches), the 80.5 median has a wide spread (63-113).
4. Blocking: BEHAVIORAL questions for Claude in QUESTIONS_FOR_CLAUDE.md. No owner questions. Engine issues for Codex: none found.
5. Recommended: lead rules on A4 breadth (question 1) and the possession target; consider more soak seeds before treating 80.5 as stable.

## Per-stage before/after (real seeds 1/3/5 and control 1)
| metric | rule (RB-3.18) | s1 A1 | s2 A1-A4 | s3 + Part B |
|---|---|---|---|---|
| team scores | 74-92, 42-92, 84-60, 68-55 | 78-50, 54-84, 81-59, 53-60 | 73-92, 100-78, 66-51, 69-45 | 70-90, 78-81, 113-100, 63-80 |
| median team score (8 teams) | 71.0 | 59.5 | 71.0 | 80.5 |
| possessions per team | 227/217/201/206 | 184/186.5/189.5/180.5 | 165.5/162/175.5/151 | 170/163/166/158.5 |
| boundaries per match (real mean) | 244.3 | 175.7 | 130.3 | 130.3 |
| of which after pass / toss / carrier / shot | 110.7 / 50.3 / 74.0 / 9.3 | 106.0 / 7.0 / 57.7 / 5.0 | 78.0 / 4.7 / 39.7 / 8.0 | 79.0 / 5.3 / 36.3 / 9.7 |
| end line / side line | 170.7 / 73.7 | 113.0 / 62.7 | 80.7 / 49.7 | 79.3 / 51.0 |
| passes (real 3) / missed / recovered by passer team | 954 / 661 / 173 | 999 / 707 / 208 | 779 / 544 / 153 | 761 / 543 / 149 |
| open-play completion | .50/.44/.524/.421 | .569/.44/.484/.493 | .492/.55/.442/.535 | .514/.477/.451/.51 |
| carry attempts | 118/99/111/92 | 130/83/117/81 | 105/117/105/93 | 114/104/114/83 |
| carry goals | 4/2/1/2 | 0/1/3/0 | 4/2/1/3 | 5/8/8/3 |
| points by method (real 3): carry / release | 35 / 369 | 20 / 359 | 35 / 395 | 105 / 408 |
| Part B actions (real 3): handoffs / blocks / trucks (broken) / stiff-arms / stretch goals | - | - | - | 911 / 139 / 154 (22) / 313 / 19 |
Tables: diag_stages.txt (per match), tools/measure.py (possession causes and completion).

## Constants: native/cognition_rb3.py (RB-3.19 sections: BOUNDARY_MARGIN_M 2.0, PURSUERS 2, PURSUIT_STEP_S .1, PASS_EXIT_MIN_S 1.0, HANDOFF_FASTER_MS 2.0, BLOCKERS 2, BLOCK_NEAR_M 8, BLOCK_FAR_M 10, BLOCK_THREAT_S 1.5, MOVE_REACT_S .5, FACING_GOAL_COS .5); config rb319_ball_in_play_enabled (default False), rb319_parts.
## Scenario results (all paired controls pass): toss 12 m uses 30.0 m/s (old 50.3); missed toss stays in at 30 m/s and leaves at 50.3; no safe toss target -> 20 m/s in-field space throw; carrier 3 m from the side line keeps aims y >= 2; two nearest teammates pursue, third does not; corner pass excluded; handoff to a 6 m/s faster teammate offered, 1 m/s faster and backward-unpressured not; block engages the closing defender at 10 m, not at 14 m, not from behind; truck vs light, stiff-arm vs heavy; stretch from 1 m short scores (stretch_goal event).
## Per-match hashes (trace / state), stage s1, s2, s3
- s1 real-seed01 {'A': 78, 'B': 50} d86d4920ba39a25ef40b775cd3228dc46074cd6c3a59bea79834c85af258c9a0 / 930c480bb1efd45c5246fe60b2448ac1560f5ba5d2b43c470ab5eede462fb169
- s1 real-seed03 {'A': 54, 'B': 84} c1480b536c1bdac5628cc41091ec70b4a1faaa02e8332d8140861c007e5d89cf / b2669329ea65613b85b97530d1d5807911d8441d3f49bb241cd8475bde659ab4
- s1 real-seed05 {'A': 81, 'B': 59} 345a8f12f859446868c434e8546774696a748d585b4d3f017350a6777d7e2cdb / 30b8f379e73699bd4c721ab5150baf9a79f8feda9085f5b815c68d200b64f16d
- s1 control-seed01 {'A': 53, 'B': 60} 4a462b03ffcbd84c04cb674bca076eeb6e0725c114b2000f94f0bc263c34480b / 321c709f32113789cf041d182b4606cd8b29348f04b91e585e479d64e87b7fbd
- s2 real-seed01 {'A': 73, 'B': 92} 4c3628ca1cbf4af8d7a2de3287e769e5bd061463957d95ee37ee973de0f0ed60 / 1b22d189d5dc624b0514111d94f72379aedb7fd9d1f741aaf6ef3a2cc40d8586
- s2 real-seed03 {'A': 100, 'B': 78} 5feebf4b37bf819334e2daa55cecb9a05ac039bb10ddcb9f7ecdb8310197e7fd / 71937d598376c1ca053cfb30c7a4bcc487f50496924d598eb1f29451266054df
- s2 real-seed05 {'A': 66, 'B': 51} 58599150d4ce7c4d70f7244d1ec9a05882229542c2d2a77ef008090dbe6b4e74 / 7c18d3010aeb38dcdcd494f681fee67a79d7b2e4d869bc585ffe690726dfc443
- s2 control-seed01 {'A': 69, 'B': 45} 8908dce8061d3910a0b31582c5a789eb7c70274d54f2d01eea315ca659138bdd / d906efd72e23bc7e7f6ea600624d403143e31dd933541de50e737e6cc2ac7440
- s3 real-seed01 {'A': 70, 'B': 90} 0337601a57af314e275e731d85ad598ebd8a5ad6f2c00fd2ea962ee2c20ccc81 / 2624bf6c10ecd923c2cf2004bc54764fba8108e2456e7d330672cd260ea3e629
- s3 real-seed03 {'A': 78, 'B': 81} 485f897d41ee26bd833ad59d712d813c4a101d2cff58a1a4c8a9707c92e7bb42 / ce2f90cc3cc21d5b4327ec1e0c84ebe3b25454c3c6c82c2361e2be39cf258f09
- s3 real-seed05 {'A': 113, 'B': 100} 54b0c7ce7eb3de1514f97a861405a4b104b0b735286de13a78f620af7e98703b / d4f95f1865164c871720a57b348641e2f09c555533b3f30e9042731af37330ed
- s3 control-seed01 {'A': 63, 'B': 80} 35957e7c34014f0ff341acf07fda75fa5708209406ff5c3a81b8692ea905d54c / 03df724c1d45d680cb780db4273bab6aea57ac241d298b12a7027416844f31f3
