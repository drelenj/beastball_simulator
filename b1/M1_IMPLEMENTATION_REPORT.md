# HP-002 B1 M1 implementation report

## Owner briefing

R3 at `claude/hp002-audit` commit `ffb5c07` closed G2 and G3 and identified G1
as the sole M1 blocker. G1 is now implemented and locally satisfies all six
behavioral acceptance checks. This is a candidate for independent review; it is
not self-declared milestone acceptance.

No canon decision was required. No physical rating, physical constant, accepted
B0 source file, or historical evidence file was changed.

## G1 implementation

The governed `m1-carrier-pass-or-carry-v1` episode uses three authoritative
engine bodies:

| Athlete | Control | Start |
|---|---|---|
| A0 carrier | independent PRISM belief; pass/carry cognition | (45, 50) |
| A1 receiver | stationary physical body; no cognition or route | (49, 62) |
| B0 defender | independent PRISM belief; pursuit/interception cognition | (53, 52), or (50, 51) in C3 |

`PhysicalExecutionPort.advance_world` invokes the accepted C3 locomotion/contact
and C1 ball/catch path with `scripted=True`. It supplies only admitted B1 motor
targets. The legacy carrier evaluator, route planner, team target policy, and
normal match step are trapped; automatic roster refill is disabled for this
controlled three-body slice.

The defender sees player and ball observations through its own noisy, delayed
PRISM instance. Ball sensing is projected separately so the ball cannot become
an artificial occluder. Carrier association and lead pursuit are computed from
delivered beliefs. A1 never receives a cognition tick or movement command.

The R3 N1 note is also corrected: a decision consumes all unconsidered
own-action failure feedback rather than inspecting only the newest item.

## 100-seed results

Each condition ran seeds 1–100. Stored evidence:
`b1/evidence/HP-002_G1_100_SEED_MATRIX.json`.

| Condition | Completed | Intercepted | Loose/incomplete | Grounded | Reached x=90 |
|---|---:|---:|---:|---:|---:|
| C0 uniform | 75 | 0 | 25 | 0 | 0 |
| C1 sharp defender | 75 | 0 | 25 | 0 | 0 |
| C2 limited carrier vision | 74 | 0 | 26 | 0 | 0 |
| C3 close defender | 0 | 1 | 89 | 3 | 7 |

Failure attribution contains only `belief_error`, `latency`, or
`physical_contest`; unknown count is zero in every condition. Exact mixes differ
by condition. Seed-1 replays for all four conditions reproduced both execution
and final-state hashes. The 400-episode run took 144.020 s wall / 145.796 s CPU
on Python 3.12.14. Matrix hash:
`bd3237e392ede5d7e861dd5486b7879667896bc4affebc1e8d711a198f82e452`.

## Gate disposition

| Gate | Evidence | Status |
|---|---|---|
| G1 governed outcome scenario | independent carrier/defender cognition, physical receiver, 400 episodes | Implemented; review pending |
| G2 own-action continuation/feedback | pending command state, `continue_current`, feedback reassessment | Closed in R3 |
| G3 information isolation | physical-world projection and hidden-state poison probe | Closed in R3 |
| BA-M1-1 outcome diversity | completed, intercepted, incomplete, and grounded all observed | Pass |
| BA-M1-2 traceable failure | three declared causes; zero unknown | Pass |
| BA-M1-3 condition sensitivity | differing exact outcome mixes | Pass |
| BA-M1-4 no team tactics | no formation, role assignment, or receiver route | Pass |
| BA-M1-5 determinism | four condition replays match execution/state hashes | Pass |
| BA-M1-6 performance | wall and CPU time recorded | Pass |

## Verification

```bash
python3 -m unittest b1.test_m1 b1.test_g1 -v
python3 -m b1.g1 --matrix 100 --out /tmp/g1-matrix.json
python3 -m b1.m0_manifest
```

Seventeen tests pass in a clean staging tree. Tests cover the earlier M1
boundary, independent defender belief pursuit, observer neutrality, deterministic
replay, stationary receiver ownership, and fixed real-kernel outcome fixtures
(completion seed 1, interception seed 10, grounding seed 35). The frozen B0
inventory verifier remains clean.

## Remaining limits

- G1 is one controlled episode, not full-team or regulation play.
- A1 catches physically but has no cognition or catch intent.
- General command queues, simultaneous multi-resource bundles, Keepers,
  Archers, formations, and multi-teammate tactics remain out of scope.
- The provisional option and pursuit policy is not a behavioral-quality claim.
- Current deterministic IDs are scoped to this Python candidate, not the final
  cross-language causal schema.
