# RB-3.8 evidence: freeze-recovery condition dropped (claude/rb-3-8-drop-freeze-recovery)

Runs: `tools/soak_driver3.py` (r2 harness: native/run.py::run_match, native-rb/3, banded scoring, real rosters Garvian Guardians v Ala Apex from roster ref 81f92e3; control uniform athletes, all ratings 0.70, 2.39 m, 226 kg, reach 3.05 m). Report: `tools/rb38_report.py`; every remaining call is listed in `rb38_table.json`.

| Match | Finished | Score A-B | zone_unmarked (RB-3.6) | freeze_recovery in raw log | Possessions A/B | Shot + carry attempts A/B | Attempts per possession A/B | Possessions ending in an attempt A/B | Points play / foul awards (share fouls) | Raw log | Runtime s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| real-seed01 | yes | 15-27 | 0 (12) | 0 | 357/358 | 13+53 / 28+76 | 0.185/0.290 | 5.0%/8.1% | 36 / 6 (14%) | `native/evidence/rb38/real/raw-real-seed01.json` | 217.49 |
| real-seed03 | yes | 18-28 | 1 (9) | 0 | 339/339 | 26+70 / 21+62 | 0.283/0.245 | 6.8%/7.1% | 33 / 13 (28%) | `native/evidence/rb38/real/raw-real-seed03.json` | 218.99 |
| control-seed01 | yes | 1-9 | 0 (18) | 0 | 328/329 | 1+24 / 6+21 | 0.076/0.082 | 0.9%/3.3% | 5 / 5 (50%) | `native/evidence/rb38/control/raw-control-seed01.json` | 223.5 |

## Remaining zone_unmarked calls

- real-seed03, period 3, live 1719539 ms: A:NBL24-07-10 at (10.18, 59.154), 13.69 m from his goal centre, 6.28 s in zone; nearest opposing field player B:NBL24-01-01 at 25.222 m; ball 50.081 m away (carried).

Hashes (trace / state): real-seed01 2579828021cf33701a0d433038a0e9e8858d5ddc06c98223f3ff1e13a53c04c9 / e272f807ecbde2e7d2b46d2bd97d433a9084f183ee0b12b1b3fb9b94d0a9a341; real-seed03 c0fe0826456c2456d7e771049d9dd22bb2226533a1712aa0eac4f93ab39c8e53 / d4255da16d0e5b64d7f30d59758f5e728500357a7e69ae1d1d6ff171a3660fe5; control-seed01 3cc853697eb613703869e87a64ccbecf407a0017ef4903ab22667074efcdad72 / 4f4169e7082dc4ada24d0dc2c3bc3621d59ace0804748be6b66ea7f1c9b2593a
