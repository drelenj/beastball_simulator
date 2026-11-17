# OWNER BRIEFING

1. Accomplished: native-rb/3 integrates the native-v0/3 contact and restart decision path with ATTR-2 roster bodies and Rulebook 1.0. The new profile is IMPLEMENTED and its focused conformance tests are TESTED; it is not ACCEPTED.
2. Native can now run a bounded banded-scoring match with two real NBL franchises, athlete-owned contact and restart choices, per-athlete body/skill mappings, and the RB-2.1 own-goal and carry-attempt rules. A 753.3 kg Garvian Archer was admitted and run in a forced active-platform scenario.
3. Unimplemented or unproven: no full native-rb/3 match or soak has run. The workbook has no technical skill source, so eight technical ratings use Opening-day OVR and contact resistance uses Balance as flagged PLACEHOLDER values. Newly carried ratings remain inert. Match quality, balance and emergence are unproven.
4. Blocking: Güunlekia Serpents has one KPR in the owner workbook, so a 2-Keeper/2-Archer/18-field roster cannot be selected for that franchise without an owner ruling. The adapter reports this shortage rather than inventing a backup.
5. Recommended action: owner resolves Q-RB3-1 for the Serpents; Claude reviews the integrated code and evidence; DreLen decides acceptance. No quality or tactical claim follows from this bounded smoke.

## Engineering evidence

The complete `b1 native` suite passed: 387 tests and 23 subtests. The two subsequently added RB/3 scoring and parallel-replay tests passed in the final focused RB/3 suite: 28 passed. A system-installed `openpyxl` was supplied to the venv by `PYTHONPATH`; `native/requirements.txt` now declares it directly. There was one external pytest plugin deprecation warning and no test failure.

Native-v0/2 seed 1 full replay retained trace `3840682e22692e597bc1419aa298337201e86db2d35f7208c5c9e50e9a99a142` and state `411abb0a4bab0b812bc5e2e010f03d22f726ff32fdcebcb7df6c3a5beac8aec9`. Native-v0/3 source-head seed 1 full replay retained trace `cacf24053a2fdfdcfecf64c376690651029c8094dd6488b864069b3c3baa74d2` and state `d688fcbb46b20830bc2ecbda35486bbee5720b8b7cf911f3403f12a9f13d0012`. The RB-2 bounded serial/parallel/M2-absent check retained its recorded hashes. Accepted `b1/core.py`, `b1/runtime.py`, `b1/g1.py` and the frozen B0 blobs were not modified.

The 400-step seed-1 Garvian Guardians (A) versus Ala Apex (B) bounded smoke reached 13,013 live ms with invariants passing. It ended at the requested partial cutoff with one restart pending (completion ratio 5/6). Trace: `f23d92d3d567ae7034103bd3fbc9f61e095f4157690bb89a309246740c85dd00`; state: `6aa1b0deda0c7c4fdc9725b292bb6f3f2370d94a8b8f23abc35092bf381e3cd6`; config digest: `4721bcc8ffbec470fa5061afde853312ad8b559c1664378fbdbc9341553c9ce2`. Roster digests: A `e95d361d060dbb4585672764835101924679da40b80c5c03530542d168d0d5cc`, B `949227f47a9647eff92b3c287dac2a5f60b57fd1e7d35315dd8cbaf25c9c0d42`. All 44 exact selected heights, masses, standing reaches and speed readbacks are in `RB3_NBL_BODY_READBACK.md`.

The adapter's 18/2/2 selection matches the Rulebook 22-player roster requirement: 18 field supplies 10 starters plus bench cover, two Keepers and two Archers provide a starter and designated backup. The Rulebook 12-person field limit excludes the active Archer, so one extra field player is admitted at setup. No full match with these real rosters has been proven.

Mapping changes: acceleration = 12.5 × Acceleration rating, independent of Speed and Agility; speed = 44.704 × Speed rating. Braking = 16.875 × Agility; turning = 16.25 × Agility. Height, mass and standing reach are read directly, with no second physique factor. The 3.447 m, 753.3 kg Garvian Archer reads back reach 4.319 m, speed 30.39872 m/s and acceleration 9.375 m/s². The old 2.40–2.95 m / 155–285 kg design warning is removed; engine limits remain 1.4–3.6576 m and positive mass.

Throw speed changed from the fixed 27 m/s athlete request to `min(80, 0.5 × own maximum throw speed)` in native-rb/3. The engine still caps physical release at that athlete's own maximum. The old native-v0/3 and native-v0/2 requests remain versioned. This is a primitive default, not tuned. The Archer pass-in-flight targeting predicate is restored for native-rb/3 because Rulebook team control persists during qualifying flight. Contact and takedown authorization ends on carrier change or at 500 ms after the athlete's decision. A-4 cover uses a field player only once both named specialists cannot enter; there is no specialist forfeit.

Technical-skill PLACEHOLDER mapping: tackling, blocking, ball_handling, catching, awareness, throw_accuracy, keeper_skill and archery_accuracy = Opening-day OVR / 100; contact_resistance = Balance / 100. `touch`, `vision`, `clarity`, `reaction`, `anticipation`, `focus`, `instinct`, `judgment`, `motor_control`, `playmaking`, `finishing`, `marking`, `zone_reads`, `goalkeeping`, `in_air_ball_pursuit`, `live_ball_pursuit`, `carrier_duel`, `defender_duel` are stored and validated in the roster attribute record, default to 0.70 with a DEFAULT marker when absent, and are included in the full roster/config digest. Read paths for each of those 18 ratings: none in cognition, motor, engine, rules or athlete views. Each was tested at 0.40/0.70/1.00 for identical short-window gameplay trace and state hashes despite distinct full config digests. The old kick_power/kick_accuracy columns are rejected.

Rule-to-test mapping: `NATIVE_RB_3_RULE_MATRIX.json`. Baseline and source-head hashes: `NATIVE_RB_3_MANIFEST.json` and `NATIVE_V0_3_MANIFEST.json`. Q-RB3-1 is recorded in `QUESTIONS_FOR_OWNER.md`.

Implementation commit: `72a171d`, following source-port commits `923eabe`, `3fcdd8d`, `9436d7a`, `c5233a4`. Documentation and manifest are committed separately. Branch: `codex/native-rb-3`.

Reproduce the real-roster smoke after installing `native/requirements.txt`:

```bash
python -m native.rulebook.run --seed 1 --max-steps 400 --nbl-a 'Garvian Guardians' --nbl-b 'Ala Apex' --out /tmp/native-rb3-garvian-ala.json
```

No result here measures gameplay quality, balance, tactics or emergence.
