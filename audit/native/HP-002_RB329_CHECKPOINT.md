# OWNER BRIEFING

1. **IMPLEMENTED.** RB-3.29 adds a read-only player ledger, five individual rotation profiles and the possession-swing analysis.
2. The simulator can emit reconciled JSON and CSV box scores. The R1 seed-1 check reproduced 85–86 and both RB-3.28 hashes with observation on.
3. The 150-game soak is in progress. All regression and identity gates passed.
4. Completion depends on the remaining match evidence. No canon question is pending.
5. Review the measured rotation rhythms and swing drivers before choosing a profile.

## Standing gates

 a) pytest -q b1 native, full suite, after the last change.

 b) Legacy hash guards unchanged (six rows).

 c) Determinism.

 d) Compatibility: real seed 1 = 57-76, trace 44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072, state 046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d.

 e) CORE identity (fatigue off): neutral-real seed 1 = 61-80, trace c1a578db3f2754d3f69b47ba81a1f9d5b9336e1d87f496de2fa8dc3daee7a256, state c517e00f864f1438705cdd1d9768d61523ee1aaac69746f57a2e9f1f4adf2745.

 f) RB-3.28 identity (fatigue ON at RB-3.28 rates): ratings 0.4, Garvian Guardians vs Ala Apex seed 1 = 85-86, trace a399f74f81d891c8a0cd4014fc5d10bc5623ad835c448932a94cd50ffac7ac4b, state bc4898a8229d147bd60defdc623db55fac13a3845fb5f29f812198b4bf5f61d4.

 g) Speed: the stats ledger adds at most 3% per step.

## Revisions and scope

- Branch `codex/rb-3-29-stats-rotation-swing`
- Lead-verified parent `49447ae7861d01e0f7a96e62db8b05ae6c838efc`
- Implementation `0dc9bf9` and final individual credit correction `010e47b`.
- [Reproduction, box-score definitions and denominators](rb329/README.md)

| Task | Status |
|---|---|
| 1. Player stats ledger | DESIGN COMPLETE, IMPLEMENTED, TESTED. Identity and timing gates passed. |
| 2. Rotation rhythm options | DESIGN COMPLETE, IMPLEMENTED. Variant rate and minimum-stint scenarios passed. Soak underway. |
| 3. Possession swing diagnosis | DESIGN COMPLETE, IMPLEMENTED. Aggregate script is ready for the full soak. |

The workload uses the ratings 0.4 workbook and the established on-field selection from OVR 0.422. All five profiles use hand-set values and individual substitutions. The thresholds and position preference stay fixed. The soak reports a starter-minute drift greater than 1.5 minutes from 32.

## Regression evidence

The maintained suite reported `779 passed, 1 warning, 23 subtests passed in 641.04s (0:10:41)`. The warning was the pytest dependency deprecation. The six legacy rows matched exactly.

The compatibility and CORE identity matches used the ledger. Both reproduced the exact scores, configuration, trace and state in the parent evidence. The two full observed R1 seed-1 games also reproduced the parent fingerprints, covering gates c through f.

| Seed | Ledger off, CPU ms/step | Ledger on, CPU ms/step |
|---:|---:|---:|
| 1 | 4.143 | 4.167 |
| 3 | 3.815 | 3.912 |

In the two paired 1,500-step windows, the score and all fingerprints matched. Ledger cost was **+1.52%**, within the 3% gate. The timings include box-score reconciliation at the end of the window.
