# RB-3.9 offense fixes: evidence (claude/rb-3-9-offense-fixes)

Runs: real seeds 1, 3, 5 (Garvian Guardians v Ala Apex, roster ref 81f92e3) and control seed 1 (uniform athletes, all ratings 0.70, 2.39 m, 226 kg, reach 3.05 m), native/run.py::run_match via `tools/soak_driver3.py`, native-rb/3, banded scoring. "Before" = the RB-3.8 soak logs of the same seeds (same base code 185b557). Measurements: `tools/measure.py` (raw logs only), all four matches final at every stage.

### Possessions per team

| Match | before | stage 1 | stage 2 | stage 3 |
|---|---|---|---|---|
| real-seed01 | 357.5 | 319.0 | 262.0 | 248.0 |
| real-seed03 | 339.0 | 295.5 | 251.5 | 256.5 |
| real-seed05 | 352.5 | 320.5 | 246.0 | 256.5 |
| control-seed01 | 328.5 | 351.0 | 244.5 | 263.5 |

### Share ending in an attempt

| Match | before | stage 1 | stage 2 | stage 3 |
|---|---|---|---|---|
| real-seed01 | 6.6% | 10.0% | 9.9% | 13.3% |
| real-seed03 | 6.9% | 10.3% | 12.7% | 12.9% |
| real-seed05 | 7.8% | 8.4% | 11.8% | 13.8% |
| control-seed01 | 2.1% | 7.8% | 8.0% | 11.2% |

### Scrimmage snap interception

| Match | before | stage 1 | stage 2 | stage 3 |
|---|---|---|---|---|
| real-seed01 | 48.7% | 44.9% | 49.7% | 48.8% |
| real-seed03 | 40.0% | 41.7% | 48.2% | 48.5% |
| real-seed05 | 45.2% | 43.1% | 41.6% | 52.3% |
| control-seed01 | 26.9% | 36.4% | 38.1% | 49.1% |

### Snap completion (scrim + snap40)

| Match | before | stage 1 | stage 2 | stage 3 |
|---|---|---|---|---|
| real-seed01 | 48.8% | 58.3% | 53.5% | 52.9% |
| real-seed03 | 57.3% | 61.4% | 54.1% | 54.0% |
| real-seed05 | 56.4% | 60.0% | 61.1% | 51.1% |
| control-seed01 | 66.8% | 65.2% | 63.6% | 53.0% |

### Nose-tackle interceptions

| Match | before | stage 1 | stage 2 | stage 3 |
|---|---|---|---|---|
| real-seed01 | 0 | 140 | 178 | 159 |
| real-seed03 | 0 | 104 | 145 | 142 |
| real-seed05 | 0 | 112 | 121 | 138 |
| control-seed01 | 0 | 133 | 130 | 170 |

### Restarts lost within 5 s

| Match | before | stage 1 | stage 2 | stage 3 |
|---|---|---|---|---|
| real-seed01 | 443 | 399 | 329 | 329 |
| real-seed03 | 425 | 355 | 305 | 334 |
| real-seed05 | 440 | 381 | 289 | 299 |
| control-seed01 | 423 | 420 | 307 | 345 |

### Open-play pass completion

| Match | before | stage 1 | stage 2 | stage 3 |
|---|---|---|---|---|
| real-seed01 | 71.3% | 73.1% | 76.0% | 76.3% |
| real-seed03 | 72.2% | 71.6% | 75.8% | 75.9% |
| real-seed05 | 69.3% | 72.6% | 75.9% | 71.2% |
| control-seed01 | 66.2% | 72.3% | 76.0% | 75.6% |

### Carry attempts

| Match | before | stage 1 | stage 2 | stage 3 |
|---|---|---|---|---|
| real-seed01 | 129 | 149 | 117 | 137 |
| real-seed03 | 132 | 167 | 156 | 167 |
| real-seed05 | 111 | 134 | 147 | 127 |
| control-seed01 | 45 | 164 | 97 | 124 |

### Carry goals

| Match | before | stage 1 | stage 2 | stage 3 |
|---|---|---|---|---|
| real-seed01 | 0 | 0 | 0 | 4 |
| real-seed03 | 0 | 0 | 0 | 2 |
| real-seed05 | 0 | 0 | 0 | 2 |
| control-seed01 | 0 | 0 | 0 | 2 |

### Tackles

| Match | before | stage 1 | stage 2 | stage 3 |
|---|---|---|---|---|
| real-seed01 | 201 | 240 | 323 | 285 |
| real-seed03 | 219 | 187 | 244 | 256 |
| real-seed05 | 202 | 195 | 244 | 219 |
| control-seed01 | 232 | 256 | 291 | 312 |

### zone_residence calls

| Match | before | stage 1 | stage 2 | stage 3 |
|---|---|---|---|---|
| real-seed01 | 6 | 13 | 6 | 14 |
| real-seed03 | 7 | 11 | 15 | 9 |
| real-seed05 | 2 | 7 | 14 | 9 |
| control-seed01 | 5 | 13 | 9 | 9 |

### Points from play

| Match | before | stage 1 | stage 2 | stage 3 |
|---|---|---|---|---|
| real-seed01 | 36 | 52 | 58 | 39 |
| real-seed03 | 33 | 43 | 29 | 39 |
| real-seed05 | 64 | 45 | 48 | 39 |
| control-seed01 | 5 | 43 | 31 | 43 |

### Points from foul awards

| Match | before | stage 1 | stage 2 | stage 3 |
|---|---|---|---|---|
| real-seed01 | 6 | 2 | 10 | 19 |
| real-seed03 | 13 | 14 | 12 | 9 |
| real-seed05 | 5 | 7 | 14 | 16 |
| control-seed01 | 5 | 25 | 6 | 11 |

### Score

| Match | before | stage 1 | stage 2 | stage 3 |
|---|---|---|---|---|
| real-seed01 | 15-27 | 20-34 | 25-43 | 26-32 |
| real-seed03 | 18-28 | 23-34 | 19-22 | 25-23 |
| real-seed05 | 21-48 | 19-33 | 25-37 | 32-23 |
| control-seed01 | 1-9 | 31-37 | 16-21 | 30-24 |

### Carry outcomes

| Match | before | stage 1 | stage 2 | stage 3 |
|---|---|---|---|---|
| real-seed01 | {'grounded': 7, 'stopped_short': 104, 'turnover': 17} | {'grounded': 5, 'stopped_short': 138, 'turnover': 6} | {'grounded': 13, 'stopped_short': 99, 'turnover': 5} | {'goal': 4, 'grounded': 19, 'stopped_short': 91, 'turnover': 23} |
| real-seed03 | {'grounded': 13, 'stopped_short': 108, 'turnover': 11} | {'grounded': 14, 'stopped_short': 144, 'turnover': 8} | {'grounded': 13, 'stopped_short': 137, 'turnover': 6} | {'goal': 2, 'grounded': 24, 'stopped_short': 129, 'turnover': 12} |
| real-seed05 | {'grounded': 8, 'stopped_short': 85, 'turnover': 17} | {'grounded': 6, 'stopped_short': 119, 'turnover': 9} | {'grounded': 10, 'stopped_short': 127, 'turnover': 10} | {'goal': 2, 'grounded': 8, 'stopped_short': 100, 'turnover': 17} |
| control-seed01 | {'grounded': 4, 'stopped_short': 34, 'turnover': 6} | {'grounded': 14, 'stopped_short': 143, 'turnover': 7} | {'grounded': 10, 'stopped_short': 81, 'turnover': 6} | {'goal': 2, 'grounded': 25, 'stopped_short': 86, 'turnover': 11} |

## Hashes and raw logs

| Stage | SHA | Match | trace | state | raw log |
|---|---|---|---|---|---|
| stage1 | 054b204 | real-seed01 | b68e0c62eb1c2aaa22e0a03ac86d1da5183d282c12e2b7c3fda6032528eae507 | b24c4f3bf87e812a0e30ec09c5e2f0c11c8fc4a436108d406f27602f1c08bed8 | `native/evidence/rb39/stage1/real/raw-real-seed01.json` |
| stage1 | 054b204 | real-seed03 | bea2fc31d694f67f1078d7b38ea6acee8ac07ea43c646eaef5385ec3b1d34d2b | 3990af7e1ded0d80a30eec907af8d35e9502a0b5df9740c15d77499732ea6880 | `native/evidence/rb39/stage1/real/raw-real-seed03.json` |
| stage1 | 054b204 | real-seed05 | dd227f9b2eada1fe5d09840f6696c52aff7be99e0fea6860fc0a1bd753193e90 | 6014b09a33699cd96ccd561cc63827ef4054b7c82c293d6dd0e5f8840d846f6a | `native/evidence/rb39/stage1/real/raw-real-seed05.json` |
| stage1 | 054b204 | control-seed01 | 2d712ffe321d4c1d7410ddd4297fe1c9e02ad267c6ecbac2ea1645e65a9175cb | f89f696c7c56a3c34aa2f78d094286e1f81bdaf83c326154568774fe5d03efa2 | `native/evidence/rb39/stage1/control/raw-control-seed01.json` |
| stage2 | 57f8a8b | real-seed01 | 842e5d440a00cc0b417050d2d288b869d9c94624404b085bdc22b9d93a50ebde | e139e166c1f756724155cb4b662acbc1114f502ce4873b65dac6ad712f9bdcb5 | `native/evidence/rb39/stage2/real/raw-real-seed01.json` |
| stage2 | 57f8a8b | real-seed03 | 4573ed2e3ef1d518b18f5ef9919dadce915bd484546fea01ff66672bd4a0b200 | d6c208d7661ac7860945e11b45d2d654c0db22fcdb859c03356a801601a81adb | `native/evidence/rb39/stage2/real/raw-real-seed03.json` |
| stage2 | 57f8a8b | real-seed05 | c6396a23d166621b9dbf0619066036b82d0c5ab3534a5ec0808577e3d447a21f | c38b3006acf1e5ceb85cdab540e754492301a3094c953c5b0bd13dc2fffe2e69 | `native/evidence/rb39/stage2/real/raw-real-seed05.json` |
| stage2 | 57f8a8b | control-seed01 | f1f1261bef4185d083b96660ab406fd893e74c1765e0ad7dcbb84b58f01eccf6 | cf0a5b3af9529cb083c0f6ac35140346e74c2d9cb8ed15829239a32397d28fa8 | `native/evidence/rb39/stage2/control/raw-control-seed01.json` |
| stage3 | e9d61b2 | real-seed01 | feb2b88e3e18ab909b4d3708958fe5074d54af0f634076f6c07b7f5d7d60a94c | 88a3c583c8bae9774b40467d733a0e1b494877bf4e7b0b3a801742eebf5da1d1 | `native/evidence/rb39/stage3/real/raw-real-seed01.json` |
| stage3 | e9d61b2 | real-seed03 | f2f62d47133045b661100f52d04a765ea287de6c6f80663b740d6591e21f1014 | 75db2c0ff158d7f348db079b0faaf7bdbbf00718a918a58e4de1d162f1112245 | `native/evidence/rb39/stage3/real/raw-real-seed03.json` |
| stage3 | e9d61b2 | real-seed05 | beb2762d41e49c93cf6f9501a6ac4e32719b1ade5b5a2824454bd05b4235accf | ba78d16962602bd155c479de12fdf594df015f7560375bd139eb90e23749a593 | `native/evidence/rb39/stage3/real/raw-real-seed05.json` |
| stage3 | e9d61b2 | control-seed01 | eff18f2892756c2dd425df84f0d578cc70a6caed66f213293148cdc41f3d92f1 | 045b1f7ae822e94635eb5aa6d29896e11c161022e78f8d40ede43fd195ac2f42 | `native/evidence/rb39/stage3/control/raw-control-seed01.json` |
