# Migration Risk Register

Probability and impact are qualitative before implementation evidence exists.
“Control” is a design requirement, not a completed mitigation.

| ID | Risk | P | I | Required control / evidence | Gate / approval |
|---|---|---:|---:|---|---|
| MR-01 | B0 adapter changes event order or RNG consumption | M | Critical | T1 ten-case exact suite plus T5 observer-neutrality check on every adapter change | Gate A |
| MR-02 | A live object/callback bypasses AthleteView | H | Critical | type/module boundary, capability-denial test, true-state poison tests | Gate C |
| MR-03 | MC silently chooses a different action or target | H | Critical | intent-command target invariant; rejection/supersession trace | Gate C |
| MR-04 | Reaction/preparation delays collapse during interface split | H | High | independent timing fields; historical pending-action trace; delay properties | A/C |
| MR-05 | Automatic B0 catch is mistaken for B1 cognition | H | High | provenance tags; separate adapters and gates; prepared-catching approval | T6-O1 |
| MR-06 | Catch preparation changes physical grasp math | M | High | command replay isolates cognition/MC from PHY; T3/T3A parity | Gate B |
| MR-07 | Jump has multiple decision owners or cadence bypass | H | High | one root decision, one takeoff intent; no `next_decision=now` side channel | Gate C |
| MR-08 | Keeper rewrite hides seed-2 pathology | M | Critical | bounded B0 diagnostic; no clamp/cap; separate authorized algorithm work | Explicit approval |
| MR-09 | Archer cognition still uses true ball/opponent state | H | Critical | hidden-state poison, capability scan, option/aim invariance tests | Gate C |
| MR-10 | Undecided Archer rule becomes an implicit default | M | Critical | required versioned config with `unapproved` validation failure | Canon approval |
| MR-11 | Focus is repurposed as motor accuracy | M | High | typed rating use registry and source-to-contract review | T6-O2 |
| MR-12 | Rules constraints reintroduce positional formations | M | High | distinguish legality regions/restarts from assigned tactical anchors | Gate C / O9 |
| MR-13 | Apparent legality leaks authoritative legality | M | High | separate view estimate and rules result; mistaken-legality fixture | Gate C |
| MR-14 | Telemetry consumes RNG or changes iteration/scheduling | M | Critical | off/min/full equivalence; observer has no mutation capabilities | Gate A/C |
| MR-15 | Stable IDs depend on UUID, wall time, or container order | M | High | deterministic allocator and replay identity tests | T6-O5 |
| MR-16 | Named-stream redesign breaks B0 stochastic history | H | Critical | B0 uses historical generator/order; new substreams separately versioned | Explicit approval |
| MR-17 | Native numeric differences cause contact divergence | H | High | T3/T3A replay, stable ordering, binary64 policy, event-first comparison | Gate B/T6-O6 |
| MR-18 | Accepted T3 is treated as complete coverage | H | High | explicit gap register and T3A gate | O7 |
| MR-19 | Accepted physical magnitude is treated as canon | M | High | label parity evidence as preservation only | Governance |
| MR-20 | SIGALRM supervision is copied into native runtime | M | High | out-of-process portable supervisor tests | P-02 |
| MR-21 | Timeout resumes an uncommitted partial tick | M | High | atomic committed-tick checkpoints; partial capture diagnostic only | P-01 |
| MR-22 | Shared globals couple parallel matches | M | High | one `MatchContext` per match; concurrency/repeatability tests | B/C |
| MR-23 | Legacy option values are fabricated in telemetry | M | Medium | `legacy_not_exposed`; provenance and schema validation | C-16 |
| MR-24 | Team planner directly controls athlete action | M | High | communication/knowledge boundary; athlete owns selection | Gate C |
| MR-25 | Receiver reroute retains true-state/cadence override | H | High | belief-based intercept; cadence invariants; adapter isolation | Gate C |
| MR-26 | PHY begins making tactical choices through “feasibility” | M | Critical | PHY consumes commands only; infeasibility yields explicit outcome | Gate C |
| MR-27 | Configuration drifts during a match | L | Critical | immutable config hash; scheduled transitions only | A/B/C |
| MR-28 | Incomplete/pathological runs inflate throughput | M | High | T5 classification and denominators retained | Performance |

## Highest-priority controls

Before any B1 or native behavioral work, MR-01 through MR-04, MR-09, MR-14,
MR-16, and MR-18 must have automated evidence. These protect the historical
baseline, information boundary, decision ownership, RNG history, and adequacy of
the physical fixture set.
