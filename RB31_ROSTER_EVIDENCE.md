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
