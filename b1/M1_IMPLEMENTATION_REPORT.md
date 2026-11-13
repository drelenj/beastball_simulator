# HP-002 M1 G1 v2 implementation report

## Status

This candidate addresses the four behavioral blockers identified by independent
R5 review commit `838f6e5a76d0fa7b5aca0b36a476c1cbd1525754`. It locally satisfies
BA-M1-1 through BA-M1-6 and is ready for independent R6 review. This report does
not claim formal acceptance.

The accepted B0-P4-DEFAULT physical baseline remains frozen at
`2abe497ca82588cb2d8c871a7aab61daaae95c12`. All new behavior is isolated under
`b1/`.

## R5 blocker disposition

| R5 finding | G1 v2 response | Verification |
|---|---|---|
| H1: defender quality did not affect endpoints | B0 can choose an individual, belief-derived pass-lane interception option. Judgment affects option value, and released-ball association uses B0's sensed ball belief. | Matched C4/C5 geometry yields 35 paired endpoint differences; interceptions change from 8 to 11. |
| H2: failure causes were forced or mislabeled | Failure attribution is derived from recorded touches, controls, grounding, swept ball-to-hand proximity, belief/aim error, and release displacement. The classifier may return `unknown`. | Zero unknowns were observed in the 600 governed episodes; a unit test proves the unknown branch is reachable. |
| H3: defender-quality effect was not isolated | Added C4 and C5 with identical geometry and only the governed defender Judgment/Reaction quality change. | C4: 56 completed, 36 incomplete, 8 intercepted. C5: 55 completed, 32 incomplete, 11 intercepted, 2 carrier reaches. |
| H4: locomotion/release compatibility required proof | Preserved the approved separable locomotion + release contract. At the actual release tick, velocity is recomputed from the authoritative moving release origin toward the semantic aim. | Unit test verifies the released direction is within 8 degrees of the semantic aim after carrier displacement. |

## Governed scenario

`m1-carrier-pass-or-carry-v2` contains three physical athletes:

- A0 senses and independently chooses pass or carry.
- B0 senses independently and chooses carrier pursuit or a belief-derived lane
  interception option; after release it associates with and pursues the ball.
- A1 is a stationary physical receiver. It has no cognition, assigned route, or
  scripted catch result.

The accepted kernel owns locomotion, contact, ball flight, catches, deflections,
interceptions, loose-ball state, and grounding. The B1 layer does not directly
assign an episode endpoint.

## Evidence

The full matrix contains 100 seeds for each of six conditions, 600 episodes in
total. Its semantic matrix hash is
`f9afc5f410a2ad890b8fb271b4087ed00a3f1df3178c2a7a2bddd03d1d222b72`.

| Condition | Completed | Incomplete | Intercepted | Grounded | Reaches x=90 |
|---|---:|---:|---:|---:|---:|
| C0 uniform | 82 | 18 | 0 | 0 | 0 |
| C1 sharp defender | 82 | 18 | 0 | 0 | 0 |
| C2 limited carrier vision | 82 | 18 | 0 | 0 | 0 |
| C3 close defender | 31 | 63 | 2 | 3 | 1 |
| C4 lane defender | 56 | 36 | 8 | 0 | 0 |
| C5 sharp lane defender | 55 | 32 | 11 | 0 | 2 |

All six condition replays are deterministic. Matrix runtime was 208.522 seconds
wall time and 209.833 seconds CPU time on Python 3.12.14.

The stored artifact is
`b1/evidence/HP-002_G1_V2_100_SEED_MATRIX.json`.

## Verification

```bash
python3 -m b1.m0_manifest
python3 -m unittest b1.test_m1 b1.test_g1 -v
python3 -m b1.g1 --matrix 100 --out /tmp/g1-v2-matrix.json
python3 -m b1.evidence
```

The focused M1/G1 suite contains 21 passing tests. `b1.evidence` additionally
verifies that the accepted B0 source hashes are unchanged while generating the
portable evidence manifest and representative pass, retain, and interrupted
traces.

## Remaining boundary

This is a governed M1 proof, not a full tactical system or regulation match.
General resource queues, moving receiver cognition, multi-teammate tactics,
formations, Keepers, Archers, scoring, and regulation remain excluded. The
current option values are provisional B1 policy and should be judged only
against this M1 scenario until a later milestone broadens the contract.
