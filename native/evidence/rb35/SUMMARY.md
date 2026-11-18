# RB-3.5 zone diagnosis evidence (claude/rb-3-5-zone-diagnosis)

Harness: `tools/soak_driver2.py` (unchanged r2 driver, native-rb/3, banded scoring, real rosters Garvian Guardians v Ala Apex from roster ref 81f92e3; control = uniform athletes, all ratings 0.70, 2.39 m, 226 kg, reach 3.05 m). Report: `tools/rb35_report.py` over the raw logs. No cognition change from RB-3.4.

| Match | Finished | Score A-B | zone_unmarked | zone_residence | RB-3.4 zone_unmarked | Defender live time in own zone A / B | of which unmarked A / B | Runtime s |
|---|---|---|---|---|---|---|---|---|
| real-seed01 | yes | 34-45 | 50 | 4 | 82 | 5.8% / 9.2% | 5.3% / 7.5% | 206.12 |
| real-seed03 | yes | 40-45 | 58 | 3 | 57 | 8.5% / 7.5% | 7.5% / 6.7% | 216.01 |
| control-seed01 | yes | 21-19 | 42 | 3 | 85 | 2.9% / 6.6% | 2.6% / 5.5% | 213.53 |

## zone_unmarked fouls, all three matches (n = 150); min / q1 / median / q3 / max

| Measure | Value |
|---|---|
| Fouler distance from own goal centre (m; zone radius 20) | 3.07 / 12.31 / 16.86 / 18.8 / 19.99 |
| Fouler y (m) | 30.32 / 44.44 / 52.27 / 60.46 / 67.76 |
| Distance to ball (m) | 1.28 / 29.87 / 45.32 / 64.59 / 93.74 |
| Ball distance from the fouler's goal centre (m) | 9.12 / 37.53 / 54.0 / 74.53 / 105.19 |
| Distance to carrier (m; 32% of fouls had no carrier) | 5.89 / 29.85 / 47.83 / 63.61 / 92.96 |
| Distance to nearest off-ball offensive player (m) | 5.1 / 13.49 / 22.73 / 37.59 / 67.66 |
| That player's distance from the zone centre (m) | 14.81 / 23.3 / 33.21 / 46.95 / 66.85 |
| Nearest off-ball offensive player within 10 m / 10-20 m / over 20 m | 16% / 27% / 57% |
| Offensive players within 10 m / 20 m of the fouler | 0 / 0 / 0 / 0 / 5 ; 0 / 0 / 0 / 2 / 11 |
| Own teammates in the same zone (includes his Keeper) | 1 / 1 / 1 / 2 / 7 |
| Live time inside the zone at the call (s) | 5.0 / 5.04 / 5.08 / 10.05 / 30.1 |
| Re-entered in the previous 5 s | 0% (cannot occur: leaving resets the timer) |
| Last exit within the previous 10 s | 35% |
| Frozen or immune in the previous 10 s | 0% |
| Ball status | {'carried': 73, 'loose_ground': 1, 'pass_in_flight': 76} |

## zone_residence (attackers, n = 10)

Fouler distance from the attacked goal centre 16.63 / 18.45 / 19.35 / 19.69 / 19.7 m (just inside the arc), distance to ball 1.4 / 1.62 / 2.87 / 7.28 / 48.91 m, nearest off-ball team-mate in possession within 10 m in all cases, time in zone 5.0 / 5.04 / 5.08 / 5.1 / 6.83 s.

## Per-match detail

- **real-seed01**: fouls by reason {'archery_target': 14, 'freeze_recovery': 1, 'zone_unmarked': 50}; trace ac771a680ead5dcf234ff9c2291974c2ccffc88c4b6760ecde7a33ba7991c7e7, state 953e61fc6789e4db5eb02ca802ef70286e3e375f8352b279892644f089616114.
- **real-seed03**: fouls by reason {'archery_target': 4, 'zone_unmarked': 58}; trace 121ae54ca54bbf3a7661ddff7eed978c35419aab75785d106a7b0ae0c0052390, state fc3932ff517a9b50d5c4d4fee9a0f53bf980578d83abc5f61eec9dacc71dca52.
- **control-seed01**: fouls by reason {'archery_target': 4, 'zone_unmarked': 42}; trace 7b3b81fc81979b93aa92f0c6fbff67d523cfe29c115e9b6fc9b1568e72d04463, state 28a352ede72db1a339800bfee662e44a8705cc580759a0eedb20e0d0b51bd83b.
