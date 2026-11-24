# OWNER BRIEFING

1. RB-3.26 fixes Reaction timing and adds a separate ORACLE package for replay, physical rollouts and grading.
2. An offline scenario can resume a saved match or start from an authored field state. It can expose a selected athlete's menu and grade a forced choice without changing the other players' decision logic.
3. The value tables and Gauge results below measure this sample. Calibration across other teams and match conditions remains unproven.
4. No canon question is pending.
5. Review the replay and grading evidence before using any learned value in PRISM.

## Revisions and status

- Owner's RB-3.25 baseline `2612256e1beab3477c58866d8878882c60abf70f`
- Task 0 clock correction `d7ab3eb`
- Snapshot, scene and force harness `1c5f563`
- Rollout, mining, fitting and gauge code `c0f8970`

| Task | Status | Evidence |
|---|---|---|
| 0. Reaction | DESIGN COMPLETE, IMPLEMENTED, TESTED | 10,000-decision sweep at each level, compatibility and new seed-1 fingerprints |
| 1. Harness | DESIGN COMPLETE, IMPLEMENTED, TESTED | Full and prepared snapshots, true-state scenes, firewall test |
| 2. Rollouts | DESIGN COMPLETE, IMPLEMENTED | One forced option, independent branch seeds and stage horizons |
| 3. Drill | DESIGN COMPLETE, IMPLEMENTED | Sampled carrier and commitment decisions, held-out table fit |
| 4. Gauge | DESIGN COMPLETE, IMPLEMENTED | Three paired Playmaking levels with belief and rollout regret |

## Standing gates

 a) pytest -q b1 native, full suite, after the last change.

 b) Legacy hash guards unchanged (native-v0/2, v0/3, rb/2; seeds 1 and 3, 3000 steps; native/evidence/rb3-reach/legacy-hashes.txt).

 c) Determinism: same code + roster + seed gives identical trace and state hashes.

 d) Compatibility (individuation off): real seed 1 = 57-76, trace 44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072, state 046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d.

 e) CORE identity: individuation on, all ratings 0.70, real bodies (neutral-real), seed 1 = 87-79, trace 317d40ba3cbfd5409bec2f39075ced1122e73c7e1fd1ce4ff0dd7a65c2af7b01, state 26d9d339aa4c80c2956731948d25c7dbe93e9bb8ed152af124d706bd75ee85ef - EXCEPT after Task 0, which changes CORE on purpose: report the new CORE hashes from then on.

 f) Speed: individuation-on at most 15% slower per step than RB-3.22; ORACLE code must add nothing to a normal match run.

## Task 0 Reaction timing

| Reaction | Requested ms | Old mean ms | New mean ms |
|---:|---:|---:|---:|
| .40 | 560 | 600 | 560 |
| .50 | 540 | 600 | 540 |
| .60 | 520 | 600 | 520 |
| .70 | 500 | 500 | 500 |
| .80 | 480 | 500 | 480 |
| .90 | 460 | 500 | 460 |
| 1.00 | 440 | 500 | 440 |
| .783 | 483.4 | 500 | 483.4 |

Decisions still happen at a Native boundary. Each consecutive deliberate decision advances the previous deadline by its requested interval. The scheduler resets after a missed whole interval or a Reflex-controlled commitment. The millisecond means above use a 100 ms grid with 10,000 consecutive decisions. The clock does not change the fixed observation schedule or Ball Handling's release clock.

Task 0 alone reported `753 passed, 1 warning, 23 subtests passed in 646.56s (0:10:46)`. All six legacy rows matched. The compatibility run reproduced gate d. CORE seed 1 finished **61–80** in **32,509 steps**.

- CORE trace `c1a578db3f2754d3f69b47ba81a1f9d5b9336e1d87f496de2fa8dc3daee7a256`
- CORE state `c517e00f864f1438705cdd1d9768d61523ee1aaac69746f57a2e9f1f4adf2745`
- CORE config `e3eb027d0506db1297def02bb74924cb9c3878fa17226ffb6a47e56722976835`

## Replay and firewall

The snapshot extends the rulebook review boundary to the full running graph, including clocks, field bodies, possession, rules and counters, active motor commitments, observation delivery and MESH queues. A captured decision stores the delivered view and the turn's position in the tick. The state aliases and private physics namespace are rebound in a newly booted driver. RNGs are restored with their stream states. The trace prefix is captured as the original hashed bytes.

The static firewall test checks live Native, frozen substrate and B1 source for ORACLE imports. The regular runner has no ORACLE import or snapshot work. A fresh-process restore runs the normal continuation path. The saved fit stays in `native/oracle/artifacts/`.

Every continuation reproduced the uninterrupted final score, steps, config, trace and state. Compatibility also reproduced the owner hashes in gate d. The uninterrupted CORE fingerprint matched Task 0.

| Capture step | CORE continuation CPU s | Compatibility continuation CPU s |
|---:|---:|---:|
| 4,000 | 129.9 | 122.2 |
| 14,000 | 87.9 | 83.0 |
| 25,000 | 35.9 | 34.2 |

See `rb326/README.md` for commands and `rb326/evidence/` for raw results.
