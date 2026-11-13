# HP-002 B1 M1 candidate — R6 correction

M0 remains frozen at B0 commit
`2abe497ca82588cb2d8c871a7aab61daaae95c12`. All implementation changes are
isolated under `b1/`; the accepted physical kernel and historical T1–T5
evidence are unchanged.

This revision responds to R6 on commit `77604e1`:

- B0's belief-derived lane aim changes continuously with Judgment. C4 and C5
  share geometry and policy; only defender Judgment and Reaction change from
  `.70` to `.90`.
- The matrix reports lane-option selection, distance to the semantic pass lane
  at release, and interception rate conditional on lane selection.
- Failure causes require positive recorded evidence. Residual misses are
  `unknown`; they are not assigned `pass_accuracy_failure` by elimination.
- Moving passes implement the draft `pass-release-v1` contract at audit commit
  `baaabaa`: release-origin recomputation, correction-angle telemetry, a 60°
  `rejected_geometry` bound, and restricted failure feedback.

M1 is **not accepted** by this package. The 100-seed matrix leaves BA-M1-2 and
BA-M1-3 false. A separate 800-seed C4/C5 mechanism study supports a conditional
lane-interception effect, but it does not establish net defensive improvement.

## Reproduction

```bash
python3 -m b1.m0_manifest
python3 -m unittest b1.test_m1 b1.test_g1 -v
python3 -m b1.g1 --matrix 100 --out /tmp/g1-r6-matrix.json
python3 -m b1.g1 --lane-study 800 --seed-start 101 --out /tmp/g1-r6-lane-study.json
python3 -m b1.evidence
```

Stored evidence:

- `b1/evidence/HP-002_G1_R6_100_SEED_MATRIX.json`
  (`3f61f1e6d66a78120281755d2f9e771db0b90959a0806f3e84173d32c33edd12`)
- `b1/evidence/HP-002_G1_R6_LANE_STUDY_SUMMARY.json`
  (`a3a68939883294c06ad0e1d6276f13d911cf188ff128942c50aa4a92b50ff5e1`)

## Scope boundary

This is a governed M1 episode, not a full team or regulation match. A1 is a
stationary physical receiver without cognition. General queues, moving-receiver
cognition, multi-teammate tactics, Keepers, Archers, formations, scoring, and
regulation remain outside this slice. M2 is not authorized.
