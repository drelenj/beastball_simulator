# RB-3.10 formation hold: evidence (claude/rb-3-10-formation-hold)

Runs: real seeds 1, 3, 5 (Garvian Guardians v Ala Apex, roster ref 81f92e3) and control seed 1 (uniform athletes, all ratings 0.70, 2.39 m, 226 kg, reach 3.05 m), native/run.py::run_match via `tools/soak_driver3.py`, native-rb/3. Compared with RB-3.9 stage 3 (e9d61b2 code, logs `native/evidence/rb39/stage3/`). Measured with `tools/measure.py` from raw logs.

| Measure | Match | RB-3.9 stage 3 | RB-3.10 |
|---|---|---|---|
| Scrimmage snap interception | real-seed01 | 48.8% | 0.6% |
| Scrimmage snap interception | real-seed03 | 48.5% | 1.1% |
| Scrimmage snap interception | real-seed05 | 52.3% | 0.7% |
| Scrimmage snap interception | control-seed01 | 49.1% | 2.3% |
| Snap completion | real-seed01 | 52.9% | 99.1% |
| Snap completion | real-seed03 | 54.0% | 99.0% |
| Snap completion | real-seed05 | 51.1% | 99.3% |
| Snap completion | control-seed01 | 53.0% | 97.2% |
| Possessions per team | real-seed01 | 248.0 | 212.5 |
| Possessions per team | real-seed03 | 256.5 | 220.5 |
| Possessions per team | real-seed05 | 256.5 | 210.5 |
| Possessions per team | control-seed01 | 263.5 | 207.5 |
| Share ending in an attempt | real-seed01 | 13.3% | 15.3% |
| Share ending in an attempt | real-seed03 | 12.9% | 19.3% |
| Share ending in an attempt | real-seed05 | 13.8% | 18.8% |
| Share ending in an attempt | control-seed01 | 11.2% | 13.2% |
| Carry goals | real-seed01 | 4 | 0 |
| Carry goals | real-seed03 | 2 | 4 |
| Carry goals | real-seed05 | 2 | 4 |
| Carry goals | control-seed01 | 2 | 3 |
| Restarts lost within 5 s | real-seed01 | 329 | 251 |
| Restarts lost within 5 s | real-seed03 | 334 | 260 |
| Restarts lost within 5 s | real-seed05 | 299 | 218 |
| Restarts lost within 5 s | control-seed01 | 345 | 249 |
| Restart timeouts | real-seed01 | 5 | 9 |
| Restart timeouts | real-seed03 | 8 | 7 |
| Restart timeouts | real-seed05 | 10 | 5 |
| Restart timeouts | control-seed01 | 15 | 7 |
| Open-play completion | real-seed01 | 76.3% | 79.2% |
| Open-play completion | real-seed03 | 75.9% | 80.0% |
| Open-play completion | real-seed05 | 71.2% | 78.5% |
| Open-play completion | control-seed01 | 75.6% | 80.0% |
| zone_residence calls | real-seed01 | 14 | 15 |
| zone_residence calls | real-seed03 | 9 | 6 |
| zone_residence calls | real-seed05 | 9 | 15 |
| zone_residence calls | control-seed01 | 9 | 5 |
| Points from play | real-seed01 | 39 | 48 |
| Points from play | real-seed03 | 39 | 50 |
| Points from play | real-seed05 | 39 | 51 |
| Points from play | control-seed01 | 43 | 40 |
| Points from foul awards | real-seed01 | 19 | 7 |
| Points from foul awards | real-seed03 | 9 | 10 |
| Points from foul awards | real-seed05 | 16 | 22 |
| Points from foul awards | control-seed01 | 11 | 6 |

| Match | RB-3.9 stage 3 score | RB-3.10 score | RB-3.10 trace | RB-3.10 state | raw log |
|---|---|---|---|---|---|
| real-seed01 | 26-32 | 15-40 | 1dc6a157f6ee8a57181be2975df94b9bc2865c58a239adc99cdeb4c8f2db82f7 | 0e7dd0224cdcf5592ce7a9b02b530a2afe5d05a07c6a99ae2a2c4f210a7960bb | `native/evidence/rb310/runs/real/raw-real-seed01.json` |
| real-seed03 | 25-23 | 24-36 | 87cdbe6f2975a3a26c3674c140a7747ab613fb71c6ddb2ba5dec5176796c5a30 | 1ec24828fcb42d32dfe4d5fa853ec8b6698f01c402f8d615aeb6e273003b3142 | `native/evidence/rb310/runs/real/raw-real-seed03.json` |
| real-seed05 | 32-23 | 25-48 | 091d50626b7a19be073cba78dbf2da3ef2320d2c9ae62efb47b96d71448c9e7d | b78b9f9c9d07e5d08bf715bdfbc4e1697ebd34f1d398dfbbe6aa60f5199a1b6a | `native/evidence/rb310/runs/real/raw-real-seed05.json` |
| control-seed01 | 30-24 | 30-16 | f6a36c81aee88b045ccecd0d89e83d552633050a822cd377dfed20803e6c41a8 | 19aaa7d6824b1e01b88d23485c4e3c75ee59c4919e52ee86af5df51e10b4be03 | `native/evidence/rb310/runs/control/raw-control-seed01.json` |

Snap holds: real-seed01 340, real-seed03 302, real-seed05 289, control-seed01 359 (each ends with a snap_hold_released event naming its trigger).

