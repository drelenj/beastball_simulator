# HP-002 B1 M1 candidate — scenario v2

M0 remains frozen at B0 commit
`2abe497ca82588cb2d8c871a7aab61daaae95c12`. The B1 implementation is isolated
to this package and does not modify the accepted physical kernel or T1–T5
evidence.

This revision responds to R5 (`838f6e5`) and implements the revised governed
`m1-carrier-pass-or-carry-v2` scenario:

- A0 independently senses and chooses pass or carry from its belief.
- B0 independently tracks the carrier, pass lane, and released ball from its
  own PRISM belief. Judgment changes its individual lane-interception choice.
- A1 is a real stationary physical receiver with no cognition or assigned route.
- The accepted C3/C1 kernel owns movement, contact, catches, deflections,
  interceptions, loose balls, and grounding.
- Moving pass preparation uses the approved separability contract: locomotion
  may continue, while semantic aim is recomputed from the authoritative release
  origin.
- Failure causes come from recorded events and swept physical evidence;
  `unknown` is allowed and directly tested.

## Reproduction

```bash
python3 -m b1.m0_manifest
python3 -m unittest b1.test_m1 b1.test_g1 -v
python3 -m b1.g1 --seed 1 --condition C4_lane_defender --out /tmp/g1-v2-seed-1.json
python3 -m b1.g1 --matrix 100 --out /tmp/g1-v2-matrix.json
python3 -m b1.evidence
```

The stored 600-episode evidence is
`b1/evidence/HP-002_G1_V2_100_SEED_MATRIX.json`. All BA-M1-1 through BA-M1-6
checks pass. Matrix hash:
`f9afc5f410a2ad890b8fb271b4087ed00a3f1df3178c2a7a2bddd03d1d222b72`.

## Scope boundary

This proves the governed M1 episode, not a full team or regulation match. A1
has no catch intent; the physical catch model acts on the stationary receiver.
General queues, multi-teammate tactics, Keepers, Archers, formations, and the
final cross-language causal schema remain outside this slice. The option and
pursuit values remain provisional B1 policy, not a behavioral-quality claim.
