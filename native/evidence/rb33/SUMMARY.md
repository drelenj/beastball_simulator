# RB-3.3 provisional evidence (claude/rb-3-3-archer-flip)

Harness: `native/evidence/rb33/tools/soak_driver2.py` (copied unchanged from claude/soak-rb-3-2-r2: native/run.py::run_match via the rb31_soak path, banded scoring, real rosters from roster ref 81f92e3; control = uniform athletes, all ratings 0.70, 2.39 m, 226 kg, reach 3.05 m). Table built by `tools/rb33_report.py` from the stored result and raw log files.

| Match | Finished | Score A-B | Coin flip | archery_target fouls (by role) | DQs A/B | Archer DQs | Legal/illegal arrows | Points: play / foul awards (share from fouls) | Possessions A/B | Restart timeouts | Runtime s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| real-seed01 | yes | 32-38 | B | 54 (archer 54) | 21/9 | 10 | 306/54 | 8 / 62 (89%) | 567/568 | 595 | 200.11 |
| real-seed03 | yes | 27-32 | A | 48 (archer 48) | 21/11 | 9 | 237/48 | 8 / 51 (86%) | 423/423 | 292 | 142.65 |
| real-seed10 | yes | 27-60 | A | 55 (archer 55) | 21/8 | 11 | 318/55 | 27 / 60 (69%) | 355/355 | 117 | 155.16 |
| control-seed01 | yes | 52-37 | B | 57 (archer 57) | 13/21 | 13 | 316/57 | 4 / 85 (96%) | 358/356 | 220 | 153.22 |
| control-seed02 | yes | 45-78 | A | 77 (archer 77) | 21/16 | 17 | 286/77 | 8 / 115 (94%) | 319/320 | 135 | 151.88 |
| control-seed03 | yes | 41-39 | A | 67 (archer 67) | 14/21 | 14 | 240/67 | 6 / 74 (92%) | 385/383 | 231 | 150.98 |

## r2 comparison (claude/soak-rb-3-2-r2, same seeds)

| Match | r2 score | r2 archery_target | r2 DQs A/B | r2 share from fouls | r2 possessions | r2 restart timeouts | r2 legal/illegal |
|---|---|---|---|---|---|---|---|
| real-seed01 | 92-143 | 135 | 19/17 | 93% | 324/325 | 79 | 89/224 |
| real-seed03 | 99-63 | 88 | 14/15 | 86% | 317/317 | 54 | 86/174 |
| real-seed10 | 68-71 | 104 | 21/13 | 91% | 403/405 | 284 | 72/176 |
| control-seed01 | 0-0 (non-finish, step cap) | - | - | - | - | - | - |
| control-seed02 | 0-0 (non-finish, step cap) | - | - | - | - | - | - |
| control-seed03 | 0-0 (non-finish, step cap) | - | - | - | - | - | - |

## Per-match detail

- **real-seed01**: DQ offences {'archery_target': 10, 'frozen_contact': 16, 'zone_unmarked': 4}; foul-award origins {'archery_target': 29, 'zone_unmarked': 33}; arrow outcomes {'hit': 131, 'hit_other': 6, 'inert': 54, 'miss': 115}; carry outcomes {'grounded': 3, 'stopped_short': 15, 'turnover': 6}; restart statuses {'released': 747, 'snap_timeout': 334, 'superseded:defence_minor': 9, 'superseded:major': 4, 'superseded:minor_count_plus': 14, 'toss_timeout': 261}; trace 89540ab367a8a5eecc4138fcc8c4d8dc533151f6dc8a3f4de721652087cf5109, state 67fd047634506aa1f0cbaec3f01bcc15cd3f3b2055643b24c68842c7734e89e9.
- **real-seed03**: DQ offences {'archery_target': 9, 'frozen_contact': 20, 'immune_contact': 1, 'zone_unmarked': 2}; foul-award origins {'archery_target': 28, 'zone_unmarked': 23}; arrow outcomes {'hit': 93, 'hit_other': 11, 'inert': 46, 'miss': 87}; carry outcomes {'stopped_short': 20, 'turnover': 3}; restart statuses {'released': 624, 'snap_timeout': 72, 'superseded:defence_minor': 11, 'superseded:major': 3, 'superseded:minor_count_plus': 8, 'toss_timeout': 220}; trace 76de75fccf2bef807135acd98f9e48cd576da21226249b869d374566825aeea4, state e7f3115b2b660de8f06501019c706b9dda0ef417a5ef87d1685bccc36807fa21.
- **real-seed10**: DQ offences {'archery_target': 11, 'frozen_contact': 17, 'zone_unmarked': 1}; foul-award origins {'archery_target': 25, 'zone_unmarked': 17}; arrow outcomes {'hit': 103, 'hit_other': 19, 'inert': 96, 'miss': 100}; carry outcomes {'stopped_short': 22, 'turnover': 1}; restart statuses {'released': 600, 'snap_timeout': 13, 'superseded:defence_minor': 7, 'superseded:major': 1, 'superseded:minor_count_plus': 14, 'toss_timeout': 104}; trace 5cba07e9b7cdb1f13602be6060c5c65dfd9d558a35f0daae496aaebd38daee82, state 19cca8eb01634c7618c625809ce92728b072dd570fa1b60749774d8757c5afe5.
- **control-seed01**: DQ offences {'archery_target': 13, 'frozen_contact': 15, 'zone_unmarked': 6}; foul-award origins {'archery_target': 38, 'zone_unmarked': 43}; arrow outcomes {'hit': 116, 'hit_other': 14, 'inert': 62, 'miss': 124}; carry outcomes {'grounded': 1, 'stopped_short': 20, 'turnover': 4}; restart statuses {'released': 610, 'snap_timeout': 57, 'superseded:defence_minor': 7, 'superseded:major': 3, 'superseded:minor_count_plus': 7, 'toss_timeout': 163}; trace 7f07b77aec3b3520278784f1d1e4fb656a1c289682b34f386a3a438b285d4901, state a63b9b4d21ca705804d04d7dead5f9b936b72a0bd621c9e1f8050c4e23b49365.
- **control-seed02**: DQ offences {'archery_target': 17, 'frozen_contact': 17, 'zone_unmarked': 3}; foul-award origins {'archery_target': 44, 'zone_unmarked': 39}; arrow outcomes {'hit': 97, 'hit_other': 7, 'inert': 77, 'miss': 105}; carry outcomes {'grounded': 1, 'stopped_short': 12}; restart statuses {'released': 616, 'snap_timeout': 34, 'superseded:defence_minor': 12, 'superseded:major': 1, 'superseded:minor_count_plus': 9, 'toss_timeout': 101}; trace 78de4e74b6ca6a9956e8a01d6c774afd778e1a4a68fcdd8402e88944fb177896, state 7d8e8ff49ed6a91f4308e0bb2e7974e735b14d6792fec33f4d84c206a5d8b823.
- **control-seed03**: DQ offences {'archery_target': 14, 'frozen_contact': 15, 'zone_unmarked': 6}; foul-award origins {'archery_target': 36, 'zone_unmarked': 38}; arrow outcomes {'hit': 102, 'hit_other': 11, 'inert': 38, 'miss': 89}; carry outcomes {'stopped_short': 16}; restart statuses {'released': 645, 'snap_timeout': 46, 'superseded:defence_minor': 10, 'superseded:major': 1, 'superseded:minor_count_plus': 11, 'toss_timeout': 185}; trace 011a206139e720ac38d9a563a3269c1848f68deedad41101f1e8af58bd19bf8e, state 102ec5d1855ec964d8627197c66f443a5e5be57778c73224ed9768047f534968.
