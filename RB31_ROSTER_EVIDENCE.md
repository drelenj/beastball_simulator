# RB-3.1 roster update and readiness evidence

Status: IMPLEMENTED and TESTED; not ACCEPTED. Soak runs are separate from this roster checkpoint.

Source: `claude/hp002-audit` at `81f92e3`, `audit/arcade/morphology/NBL_2026-27_Opening_Night_Rosters_CANON_OVR_morphology_physical.xlsx`, sheet `All 712 Players`. The loader reads fields by header and has no Python read of the removed camp, contract or pre-camp OVR columns. The default ref is `81f92e3`.

All 26 franchises select exactly 2 KPR, 2 ARC and 18 field. Güunlekia Serpents was unselectable at `d85e790`; the corrected workbook lists Zuberi Ibe as KPR, resolving Q-RB3-1. Among the 25 previously selectable franchises, the membership of the selected 22 is unchanged. The ranking order within that selection changes in 21 franchises, affecting who starts or is designated backup:

Ala Apex; Ala Marauders; Ashkara Ignivars; Bibi Nupi Barbarians; Dōmyu Dominators; Garahviq Immortals; Garvian Guardians; G’Yanka Vanagu; Hina’sola Hunters; Isu’Kari Sirenwings; Kalundu Shockwave; Kasuf Bloodravens; Lykessia Wolverines; Mbuya Ïmu Moonhawks; Nuk’yl Chiefs; Priya Arpaqu; Ursiria 65ers; Wibatu Rangers; Xenar Ignite; Yukïma Cowhands; Zafiren Tidewings.

The updated OVR changes derived technical ratings and digests even where selected IDs do not change. Dante Sinella (`NBL24-11-12`, Kasuf Bloodravens) ranks first among Archers at OVR 99. Kamasi Sinella (`NBL24-02-04`, Ala Marauders) reads into the engine at mass 461.8 kg and standing reach 3.833 m.

The 400-step Garvian–Ala smoke that used `d85e790` is historical and is not evidence of the revised roster. Repeated with `81f92e3`, seed 1 reached 17,354 live ms, six of six restarts released, with trace `05968d33fb9e349e852520b2e33bd93345140df70537ccb5934b5dee37da5741`, state `7c1ea489023f22e3f9acf923a3707a58d5f6bc102800aaea878032b960508f1a`, and config digest `a8605d5677cebdc95a5516cc49bd8a5d522aac90b52803f48ab0093393d8c921`.

A full real-roster readiness match, seed 1, finished 2,400,000 live ms: Garvian 82, Ala 114, 739/739 restarts closed, invariants passed, runtime 250.337 s. Trace `9218c1769d3b3f9c8235eb6681475e259ba48bf9b7e310f647fbde8af8401055`, state `3907ff3af24d0df2d0a141908d87d268a9aa057f21c97c097c2775fc5ff93837`. This match lacks the later soak measurement hooks and is not counted in the soak.

RB-2.1's previously authorized banded 10-seed soak did not run; its budget has zero native-rb/2 entries. The RB-1 historical results use the older flat basis and are not RB-2.1 measurement. The source-head v0/2 and v0/3 replays use no workbook and remain unaffected.

`native/rulebook/test_rb31_original_regressions.py` runs the original RB-2.1 scoring test bodies (with roster-qualified player-ID strings) and F5 defender-hold body on RB/3: 16 passed. Separate RB/3 banded/F2/F5 and workbook tests also pass. The broader existing Rulebook suite passes on its existing profiles; it has not all been parameterized to RB/3.

The control specification requires an owner choice: the RB-2.1 physical profile uses 44.7 m/s maximum speed with 0.70 skills, while RB/3 maps a 0.70 Speed rating to 31.2928 m/s. The two requirements cannot both hold for the same athlete. The control block remains pending that choice.

## Soak interruption and reproducible blocker

The real-roster block completed seeds 1, 2, 4, 5 and 6; details and hashes are in `RB31_REAL_PARTIAL_RESULTS.json`. Each completed 2,400,000 live ms, closed every restart and passed the existing invariant checks. Seeds 3 and 7 were interrupted after a repeated restart cycle was observed; seeds 8–10 have not run. The ten-seed soak has not passed, and the control block has not started.

Seed 3 was independently reproduced with a 36,000-step limit. In period 3, at x=0, y=70, a B toss timed out. Rulebook awarded A a scrimmage at x=5. With no believed target, the restart cognition selected its fallback throw toward space behind the line. At 4,453,834 simulated ms the scrimmage released at velocity approximately (-53.553, 0, 3.053) m/s. The ball crossed x=-0.1075 in 95 ms; a B toss was awarded at the same point and timed out, repeating the cycle. Similar cycles in seed 7 consumed approximately 8.8 million ms simulated wall time and 88,000 steps for 60 seconds of live-clock advance. The existing dead-progress watchdog does not catch the cycle because the game clock advances briefly on each throw. These are non-finishing/near-stall observations, not completed seed results.

The throw is selected by athlete restart cognition; changing its fallback aim or release speed is a behavioral change. The rules layer must not invent a prohibition on that legal throw. The reproducible case is handed to cognition lead Claude for a proposed intent-owned correction and independent review; engineering can then verify the whole sequence and rerun the interrupted seeds.

The partial-results collector defines a possession using changes in passive possession and restart awards. `ending_in_attempt` means its last recorded offensive ball action was a shot or an entry-based carry attempt; `with_attempt` is separately retained. `points.play` means recorded goals; `points.penalty_awards` means foul awards. Those categories do not yet attribute goals to a preceding restart, so they are not a full play-versus-restart scoring breakdown.
