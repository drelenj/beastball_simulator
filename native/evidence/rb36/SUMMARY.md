# RB-3.6 defender baseline evidence (claude/rb-3-6-defender-zone)

Harness: `tools/soak_driver3.py` = r2 driver plus `--override` and `--tag` (native-rb/3, banded scoring, real rosters Garvian Guardians v Ala Apex from roster ref 81f92e3; control uniform athletes, all ratings 0.70, 2.39 m, 226 kg, reach 3.05 m). All six runs on the same code (commit 3c26b3d); fix-off and leash variants differ only by RulebookConfigV3 overrides. Report: `tools/rb36_report.py`.

| Run | Finished | Score A-B | zone_unmarked (RB-3.5) | zone_residence | Defender time in own zone A/B | ...unmarked A/B | Defender time meeting baseline A/B (per-defender median) | DQs A/B | Play / foul-award points (share fouls) | Possessions A/B | Ending in attempt A/B | Carry attempts A/B, outcomes | Tackles | Restart timeouts | Runtime s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| real-seed01 | yes | 15-10 | 12 (50) | 0 | 4.4%/4.3% | 3.2%/3.1% | 78.9%/79.9% (80.0%) | 1/1 | 7 / 18 (72%) | 295/295 | 2.4%/2.0% | 14/9, {'grounded': 7, 'stopped_short': 14, 'turnover': 2} | 208 | 67 | 230.94 |
| real-seed03 | yes | 6-7 | 9 (58) | 2 | 3.0%/5.1% | 1.8%/3.2% | 77.5%/76.5% (77.8%) | 0/1 | 3 / 10 (77%) | 303/303 | 2.3%/2.3% | 11/5, {'grounded': 1, 'stopped_short': 14, 'turnover': 1} | 183 | 50 | 221.92 |
| control-seed01 | yes | 36-11 | 18 (42) | 3 | 3.5%/5.9% | 2.3%/3.8% | 76.2%/76.6% (76.6%) | 1/2 | 14 / 33 (70%) | 308/308 | 1.9%/2.3% | 13/11, {'grounded': 5, 'stopped_short': 17, 'turnover': 2} | 228 | 86 | 238.52 |
| real-seed01-fixoff | yes | 34-45 | 50 (50) | 4 | 5.8%/9.2% | 5.3%/7.5% | 68.4%/69.8% (69.7%) | 5/5 | 5 / 74 (94%) | 307/307 | 1.6%/1.6% | 8/10, {'grounded': 1, 'stopped_short': 16, 'turnover': 1} | 169 | 68 | 213.63 |
| real-seed01-leash15 | yes | 9-13 | 20 (50) | 2 | 5.5%/3.6% | 4.0%/2.9% | 66.9%/66.4% (67.8%) | 2/0 | 2 / 20 (91%) | 322/323 | 1.6%/1.6% | 10/7, {'grounded': 4, 'stopped_short': 11, 'turnover': 2} | 213 | 63 | 227.63 |
| real-seed01-leash35 | yes | 6-15 | 24 (50) | 3 | 4.8%/4.6% | 3.7%/3.3% | 85.2%/85.8% (85.9%) | 4/1 | 2 / 19 (90%) | 303/303 | 1.7%/0.3% | 6/3, {'grounded': 1, 'stopped_short': 8} | 210 | 67 | 226.21 |

Remaining zone_unmarked calls (fix on, 39 over three matches): 32 by previously frozen players standing within 4 m of their own end line (frozen within 3 m of it, they can never retreat the 3 m the recovery rule requires), 5 by other previously frozen players, 2 by never-frozen players. 3-8 distinct players per match account for them (up to 5 calls each).

Per-run hashes and fouls by reason are in `rb36_table.json`. The first pass (commit cc9590d) is under `superseded-first-pass/` and not cited.
