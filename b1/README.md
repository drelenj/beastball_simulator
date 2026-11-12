# HP-001 B1 M1 candidate

M0 contract freeze is recorded in `M0_CLOSURE.md` and its hash manifest.
Implementation lives only in this package; it does not modify the accepted B0
source snapshot or T1–T5 evidence.

This candidate runs one athlete through actual PRISM sensing from active physical
bodies, individual beliefs, pass/retain/no-action evaluation, intent, motor
preparation, authoritative pass release/flight/contact, and own-action feedback.
PRISM sensing and rating mappings are reused; the field decision evaluator is a
new, limited B1 policy. No claim of full M1 acceptance is made.

## Reproduction

```bash
python3 -m b1.m0_manifest
python3 -m unittest b1.test_m1 -v
python3 -m b1.evidence
python3 -m b1.run --case pass --seed 1 --out b1/evidence/pass.json
```

Run these commands from the repository root at the pinned baseline or the B1
branch. Each physical runtime must be initialized in its own process because
the historical loader installs runtime classes. The runner avoids the match-step
loop and traps known legacy decision and target methods. Physical kernel release,
ball flight, and contact behavior are invoked directly. A1 and B0 are real
active engine bodies configured at scenario start; they do not decide or receive
B1-generated movement commands.

## Evidence boundary

Tests cover immutability, observation-sensitive choices, stale beliefs,
physical-state projection, true-state poison, cadence stepping and feedback,
target fidelity, command replay without cognition, interruption, deterministic
single-resource arbitration, repeated hashes, telemetry-off neutrality, and
B0 file hash preservation. Full multi-athlete cognition, locomotion, general
queues, final causal schema, and full T1 rerun remain outstanding.

The accepted T3 and T5 verification scripts in the original evidence workspace
check their stored packets; they are not vendored into this source branch and do
not rerun historical simulation cases. No full match throughput is claimed.
