# HP-002 M1 G1 — R6 correction report

## Status

This revision responds to independent R6 review of `77604e1`. It is **not a
self-acceptance of M1**. The focused suite passes 25 tests, the 600-episode
matrix is deterministic, and the B0-P4-DEFAULT baseline remains frozen at
`2abe497ca82588cb2d8c871a7aab61daaae95c12`.

The corrected 100-seed matrix leaves BA-M1-2 and BA-M1-3 false. Supplemental
fresh-seed evidence demonstrates a conditional lane mechanism, but net defender
improvement remains unproven. Independent follow-up review is required.

## R6 corrections

### 1. Defender-quality mechanism

The former value threshold was removed. When the governed lane option is
enabled, B0 derives a carrier-receiver lane solely from its belief. Judgment
continuously controls lane depth:

`lane_fraction = clamp(0.2 + 0.6 × judgment, 0.2, 0.8)`

C4 and C5 now differ only in defender `judgment` and `reaction` (`.70` versus
`.90`). The earlier code also raised every rating in the PRISM `JUDGE` group;
that was inaccurate isolation and has been removed.

The matrix now records, per episode:

- whether B0 selected the lane option before release;
- B0's physical distance to the semantic pass segment at release; and
- the endpoint needed to calculate interception rate conditional on lane use.

#### Fresh mechanism study: seeds 101–900

The study contains 800 seeds per condition, 1,600 episodes total.

| Measure | C4 `.70` | C5 `.90` |
|---|---:|---:|
| Lane option selected | 161/800 (20.13%) | 152/800 (19.00%) |
| Interceptions conditional on lane option | 30/161 (18.63%) | 52/152 (34.21%) |
| Mean distance to pass lane, all releases | 1.845 m | 2.610 m |
| Mean distance when lane selected | 1.776 m | 1.793 m |
| Total interceptions | 98 | 76 |

In the 107 paired seeds where both conditions selected the lane, C4 intercepted
28 and C5 intercepted 45. C5 gained 32 paired interceptions and lost 15; the
exact two-sided McNemar p-value is `0.01862`.

This supports a reproducible **conditional lane-option effectiveness** effect.
It does not support a global claim that the `.90` defender is closer to the
lane or produces more total interceptions. C5 selected the lane slightly less
often, was farther from the pass segment overall, and had fewer net
interceptions (76 versus 98). Those counter-results are retained, not hidden.

The 100-seed matrix alone has only 18 lane-option seeds per condition, below the
predeclared 100 matched-seed mechanism threshold, so its BA-M1-3 flag remains
false. The supplemental study passes its mechanism rule; formal BA-M1-3 remains
for independent review.

### 2. Positive failure attribution

`pass_accuracy_failure` is now assigned only when the sampled release direction
has a recorded cross-track miss larger than A1's reach envelope. Otherwise a
residual failure is `unknown`. `carrier_motion_during_windup` was removed under
the moving-release contract.

The corrected matrix contains 37 unknowns: 32 in C3, two in C4, and three in
C5. Therefore BA-M1-2 correctly reports false. This is preferable to a precise
label unsupported by evidence.

### 3. Moving pass-release contract

The implementation now references draft action-specific contract
`pass-release-v1` at audit commit `baaabaa`; it no longer calls the overlap
“approved separable bundles.” Recompute-at-release is provisionally accepted
under that draft, not finally accepted.

Release outcome records now include action, target, semantic aim, release
origin, admitted speed, correction angle, correction bound, recomputed flag,
and final ball velocity.

The 60° provisional bound is retained:

- MR-1 runs 20 moving-pass seeds. Required corrections ranged from 0.195° to
  1.042°; maximum final direction error was 0.833° against the 8° limit.
- A constructed correction above 60° is rejected as `rejected_geometry`, and
  that restricted failure reaches cognition on its next decision.
- The bound is therefore nonbinding for observed governed traces while blocking
  pathological reversals.

Source inspection confirms Pocket 4 does **not** add carrier velocity to the
ball. It uses carrier velocity inside the throwing sampler, then passes the
sampled absolute velocity to the base engine, which directly assigns
`b.vx, b.vy, b.vz = velocity`. B1 recomputes before that sampler, so the order is
correct. MR-1 evaluates the final sampled ball velocity.

MR-2 through MR-5 additionally verify semantic action/target/aim preservation,
hidden receiver/opponent isolation, over-bound rejection and feedback, and
stationary equivalence with the contract disabled.

### 4. C3 result correction

C3 completions changed from 0 in G1 v1 to 31 after release-origin
recomputation. That change is attributable to recomputation, not defender
quality. The current matrix retains those 31 completions.

## Corrected 100-seed matrix

| Condition | Completed | Incomplete | Intercepted | Grounded | Reaches x=90 | Unknown causes |
|---|---:|---:|---:|---:|---:|---:|
| C0 uniform | 82 | 18 | 0 | 0 | 0 | 0 |
| C1 Judgment/Reaction `.90` | 82 | 18 | 0 | 0 | 0 | 0 |
| C2 limited carrier vision | 82 | 18 | 0 | 0 | 0 | 0 |
| C3 close defender | 31 | 63 | 2 | 3 | 1 | 32 |
| C4 lane defender `.70` | 55 | 31 | 10 | 0 | 4 | 2 |
| C5 lane defender `.90` | 55 | 34 | 8 | 0 | 3 | 3 |

Matrix hash:
`3f61f1e6d66a78120281755d2f9e771db0b90959a0806f3e84173d32c33edd12`.
All six seed-1 replays are deterministic.

The fresh lane-study hash is
`a3a68939883294c06ad0e1d6276f13d911cf188ff128942c50aa4a92b50ff5e1`.
The committed aggregate is
`b1/evidence/HP-002_G1_R6_LANE_STUDY_SUMMARY.json`; its reproduction command
regenerates all 1,600 per-episode rows.

## Verification

```bash
python3 -m b1.m0_manifest
python3 -m unittest b1.test_m1 b1.test_g1 -v
python3 -m b1.g1 --matrix 100 --out /tmp/g1-r6-matrix.json
python3 -m b1.g1 --lane-study 800 --seed-start 101 --out /tmp/g1-r6-lane-study.json
python3 -m b1.evidence
```

## Remaining boundary

M1 remains unaccepted. The residual unknown failures need either more positive
instrumentation or continued explicit `unknown` status. The lane mechanism has
conditional evidence but no demonstrated net defensive benefit. General queues,
moving receivers, multi-athlete tactics, regulation, and M2 remain excluded.
