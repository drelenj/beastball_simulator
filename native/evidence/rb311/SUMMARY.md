# RB-3.11 Part A evidence: zone exit and marking behaviour (claude/rb-3-11-zone-behavior)

Runs: real seeds 1, 3, 5 (Garvian Guardians v Ala Apex, roster ref 81f92e3) and control seed 1 (uniform athletes, ratings 0.70, 2.39 m, 226 kg, reach 3.05 m), native/run.py::run_match via `tools/soak_driver3.py`, native-rb/3, banded scoring, step cap 200,000, two matches in parallel. Measured with `tools/measure.py` (raw logs only). All 16 matches finished.

The final code is the third version. The first two were corrected after tracing the calls they left (see the report): the RB-3.10 column is the previous behaviour on the same seeds, `first-pass/` and `second-pass/` keep the earlier runs.

### zone_residence calls

| Match | RB-3.10 (45a298c) | first pass (8c4310e) | second pass (62fd8ad: braking-aware estimate) | final (1e5d599: marked = tracks <= 600 ms) |
|---|---|---|---|---|
| real-seed01 | 15 | 1 | 0 | 0 |
| real-seed03 | 6 | 0 | 0 | 4 |
| real-seed05 | 15 | 2 | 1 | 0 |
| control-seed01 | 5 | 1 | 3 | 1 |
| total | 41 | 4 | 4 | 5 |

### zone_unmarked calls

| Match | RB-3.10 (45a298c) | first pass (8c4310e) | second pass (62fd8ad: braking-aware estimate) | final (1e5d599: marked = tracks <= 600 ms) |
|---|---|---|---|---|
| real-seed01 | 0 | 3 | 0 | 1 |
| real-seed03 | 5 | 2 | 2 | 2 |
| real-seed05 | 0 | 2 | 0 | 2 |
| control-seed01 | 0 | 4 | 3 | 7 |
| total | 5 | 11 | 5 | 12 |

### Points from play

| Match | RB-3.10 (45a298c) | first pass (8c4310e) | second pass (62fd8ad: braking-aware estimate) | final (1e5d599: marked = tracks <= 600 ms) |
|---|---|---|---|---|
| real-seed01 | 48 | 104 | 40 | 44 |
| real-seed03 | 50 | 52 | 52 | 58 |
| real-seed05 | 51 | 74 | 60 | 66 |
| control-seed01 | 40 | 42 | 30 | 28 |
| total | 189 | 272 | 182 | 196 |

### Points from foul awards

| Match | RB-3.10 (45a298c) | first pass (8c4310e) | second pass (62fd8ad: braking-aware estimate) | final (1e5d599: marked = tracks <= 600 ms) |
|---|---|---|---|---|
| real-seed01 | 7 | 11 | 6 | 10 |
| real-seed03 | 10 | 27 | 9 | 10 |
| real-seed05 | 22 | 8 | 2 | 8 |
| control-seed01 | 6 | 15 | 4 | 8 |
| total | 45 | 61 | 21 | 36 |

### Possessions per team

| Match | RB-3.10 (45a298c) | first pass (8c4310e) | second pass (62fd8ad: braking-aware estimate) | final (1e5d599: marked = tracks <= 600 ms) |
|---|---|---|---|---|
| real-seed01 | 212.5 | 210.0 | 211.0 | 223.5 |
| real-seed03 | 220.5 | 207.5 | 220.0 | 201.5 |
| real-seed05 | 210.5 | 216.0 | 224.5 | 225.0 |
| control-seed01 | 207.5 | 235.0 | 201.5 | 212.5 |

### Share ending in an attempt

| Match | RB-3.10 (45a298c) | first pass (8c4310e) | second pass (62fd8ad: braking-aware estimate) | final (1e5d599: marked = tracks <= 600 ms) |
|---|---|---|---|---|
| real-seed01 | 15.3% | 20.2% | 19.2% | 17.7% |
| real-seed03 | 19.3% | 16.9% | 15.0% | 20.1% |
| real-seed05 | 18.8% | 18.8% | 18.7% | 19.8% |
| control-seed01 | 13.2% | 13.0% | 13.2% | 12.7% |

### Carry goals

| Match | RB-3.10 (45a298c) | first pass (8c4310e) | second pass (62fd8ad: braking-aware estimate) | final (1e5d599: marked = tracks <= 600 ms) |
|---|---|---|---|---|
| real-seed01 | 0 | 5 | 2 | 1 |
| real-seed03 | 4 | 2 | 2 | 7 |
| real-seed05 | 4 | 3 | 2 | 3 |
| control-seed01 | 3 | 0 | 3 | 1 |
| total | 11 | 10 | 9 | 12 |

### Carry attempts

| Match | RB-3.10 (45a298c) | first pass (8c4310e) | second pass (62fd8ad: braking-aware estimate) | final (1e5d599: marked = tracks <= 600 ms) |
|---|---|---|---|---|
| real-seed01 | 144 | 154 | 143 | 159 |
| real-seed03 | 165 | 150 | 134 | 178 |
| real-seed05 | 192 | 125 | 152 | 167 |
| control-seed01 | 103 | 131 | 127 | 113 |

### Restart timeouts

| Match | RB-3.10 (45a298c) | first pass (8c4310e) | second pass (62fd8ad: braking-aware estimate) | final (1e5d599: marked = tracks <= 600 ms) |
|---|---|---|---|---|
| real-seed01 | 9 | 7 | 5 | 6 |
| real-seed03 | 7 | 4 | 9 | 5 |
| real-seed05 | 5 | 7 | 5 | 5 |
| control-seed01 | 7 | 14 | 17 | 14 |

### Restarts lost within 5 s

| Match | RB-3.10 (45a298c) | first pass (8c4310e) | second pass (62fd8ad: braking-aware estimate) | final (1e5d599: marked = tracks <= 600 ms) |
|---|---|---|---|---|
| real-seed01 | 251 | 234 | 246 | 236 |
| real-seed03 | 260 | 221 | 236 | 223 |
| real-seed05 | 218 | 239 | 250 | 261 |
| control-seed01 | 249 | 294 | 226 | 231 |

### Open-play completion

| Match | RB-3.10 (45a298c) | first pass (8c4310e) | second pass (62fd8ad: braking-aware estimate) | final (1e5d599: marked = tracks <= 600 ms) |
|---|---|---|---|---|
| real-seed01 | 79.2% | 79.6% | 81.4% | 78.3% |
| real-seed03 | 80.0% | 81.2% | 78.4% | 81.8% |
| real-seed05 | 78.5% | 80.8% | 78.2% | 79.8% |
| control-seed01 | 80.0% | 83.5% | 81.1% | 81.0% |

### Tackles

| Match | RB-3.10 (45a298c) | first pass (8c4310e) | second pass (62fd8ad: braking-aware estimate) | final (1e5d599: marked = tracks <= 600 ms) |
|---|---|---|---|---|
| real-seed01 | 270 | 250 | 279 | 222 |
| real-seed03 | 240 | 238 | 237 | 250 |
| real-seed05 | 213 | 246 | 240 | 268 |
| control-seed01 | 318 | 366 | 265 | 294 |

### Foul-award points by originating foul (zone_unmarked / archery_target) and DQs

| Match | RB-3.10 (45a298c) | first pass (8c4310e) | second pass (62fd8ad: braking-aware estimate) | final (1e5d599: marked = tracks <= 600 ms) |
|---|---|---|---|---|
| real-seed01 | 0 / 7, DQs 2 | 7 / 4, DQs 2 | 0 / 6, DQs 2 | 1 / 9, DQs 2 |
| real-seed03 | 4 / 6, DQs 3 | 4 / 23, DQs 2 | 1 / 8, DQs 2 | 3 / 7, DQs 3 |
| real-seed05 | 0 / 22, DQs 3 | 2 / 6, DQs 1 | 0 / 2, DQs 0 | 1 / 7, DQs 2 |
| control-seed01 | 0 / 6, DQs 1 | 5 / 10, DQs 2 | 1 / 3, DQs 0 | 4 / 4, DQs 1 |

### Score A-B

| Match | RB-3.10 (45a298c) | first pass (8c4310e) | second pass (62fd8ad: braking-aware estimate) | final (1e5d599: marked = tracks <= 600 ms) |
|---|---|---|---|---|
| real-seed01 | 15-40 | 18-97 | 19-27 | 21-33 |
| real-seed03 | 24-36 | 38-41 | 19-42 | 16-52 |
| real-seed05 | 25-48 | 35-47 | 22-40 | 34-40 |
| control-seed01 | 30-16 | 27-30 | 25-9 | 11-25 |

## Final run: hashes and raw logs

| Match | trace | state | raw log |
|---|---|---|---|
| real-seed01 | d743d1b5670d0bc48c9bc428320e7474efc49cb7245338b129e34fd4cb12b380 | fda009b8bdc0b53527793b3f8cf9936eb6e0dacb5f68bab73c8bb56d4f566810 | `native/evidence/rb311/runs/real/raw-real-seed01.json` |
| real-seed03 | f197bcc53fa21c4d4c5586e5af403dfcbba420fc218c97acdcbd474abf0e1814 | 6ab71bad93c31f0d07029ca5923809b2c5e02c8ec39e1ef7ae8bba722232bbba | `native/evidence/rb311/runs/real/raw-real-seed03.json` |
| real-seed05 | 5c45c4e6f9b79144a8b68f6c868647afe610e75bde3ae8b6490698659b9c3254 | 6d070ab6580294db30f047dd4f4471b1d4ff515750bf853b716ae91aae1e6309 | `native/evidence/rb311/runs/real/raw-real-seed05.json` |
| control-seed01 | 1dadc2b0c2c4f0f4aa72a1bd987a5ef25cd38ee01508439ceee8516e4a375820 | 188aff87a9db2f9927ea6f9ae3dd21d7c0c8c529e1c8bd63b99cb6b5e478f3e9 | `native/evidence/rb311/runs/control/raw-control-seed01.json` |

## Earlier passes: raw logs

- first pass: `native/evidence/rb311/first-pass/runs/{real,control}/raw-*.json`
- second pass: `native/evidence/rb311/second-pass/runs/{real,control}/raw-*.json`
- RB-3.10: `native/evidence/rb310/runs/{real,control}/raw-*.json`

