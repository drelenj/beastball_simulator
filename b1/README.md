# HP-002 B1 M1 candidate

M0 remains frozen at B0 commit
`2abe497ca82588cb2d8c871a7aab61daaae95c12`. The B1 implementation is isolated
to this package and does not modify the accepted physical kernel or T1–T5
evidence.

G1 implements the governed `m1-carrier-pass-or-carry-v1` scenario:

- A0 senses through PRISM, chooses pass or carry, and owns only its belief.
- B0 has an independent PRISM view and pursues/intercepts from its own belief.
- A1 is a real, stationary physical receiver with no cognition or assigned route.
- Pass release, locomotion, contact, catch, interception, loose-ball, and
  grounding outcomes come from the accepted Pocket C3/C1 kernel.
- Legacy match tactics, route assignment, formation anchors, receiver scripts,
  and scripted defender failure are trapped or bypassed.

## Reproduction

```bash
python3 -m b1.m0_manifest
python3 -m unittest b1.test_m1 b1.test_g1 -v
python3 -m b1.g1 --seed 1 --condition C0_uniform --out /tmp/g1-seed-1.json
python3 -m b1.g1 --matrix 100 --out /tmp/g1-matrix.json
python3 -m b1.evidence
```

The stored 400-episode matrix is
`b1/evidence/HP-002_G1_100_SEED_MATRIX.json`. It passed BA-M1-1 through
BA-M1-6 with matrix hash
`bd3237e392ede5d7e861dd5486b7879667896bc4affebc1e8d711a198f82e452`.

## Scope boundary

G1 proves the required carrier/receiver/defender episode, not a full team or
regulation match. A1 has no catch intent; the physical catch model acts on the
stationary receiver. General resource queues, multi-teammate tactics, Keepers,
Archers, formations, and the final cross-language causal schema remain outside
this slice. The field option and pursuit rules are provisional B1 policy;
physical ratings and constants are unchanged.
