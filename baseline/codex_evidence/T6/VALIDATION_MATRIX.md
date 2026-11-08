# Validation Matrix

## 1. Gate definitions

| Gate | Question | Required equality |
|---|---|---|
| A — Historical B0 preservation | Did the interface/telemetry wrapper leave accepted B0 behavior untouched? | Exact score, event count, canonical event-log hash, result hash, RNG consumption, and scheduling for all accepted cases |
| B — Identical-input physical parity | Given the same physical state, command, environment, and modeled draws, does PHY reproduce the reference? | Structural/event equality plus approved numeric tolerances |
| C — B1 cognitive correctness | Does future cognition use legitimate information and retain decision ownership? | Contract, property, leak, causal, and outcome-envelope tests; not B0 bit identity |

## 2. Required matrix

| ID | Requirement | Gate | Fixture/input | Acceptance |
|---|---|---|---|---|
| A-01 | T1 historical suite | A | ten accepted seed/mode cases at `2abe497` | scores, counts, event hashes, result hashes exact |
| A-02 | T5 observer neutrality | A | control vs full telemetry | event hash, score, count, schedule and RNG signatures exact |
| A-03 | B0 legacy kick retention | A | case exercising historical kick | identical action/event path with RULES_V03 off |
| A-04 | Wrapper installation/order | A | load audit | same match counts, flags, and effective wrapper chain |
| A-05 | Bounded-path classification | A | seed-2 Keeper diagnostic | same observed partial path; timeout not counted complete |
| B-01 | Sprint | B | accepted T3 sprint trace | exact structure; numeric tolerance below |
| B-02 | Braking/cutting | B | accepted T3 traces | same |
| B-03 | Tackle/contact | B | accepted T3 traces | same |
| B-04 | Catch | B | B0 and separately marked CATCH_V2 trace | feature provenance exact; same |
| B-05 | Ball flight | B | accepted T3 trace | same release inputs, events and flight samples |
| B-06 | Bounce | B | accepted T3 trace | same contact ordering and bounded numeric error |
| B-07 | Fatigue/condition | B | accepted T3 traces | same updates and tolerance |
| B-08 | Command isolation | B | replay trace with cognition disabled | cognition module cannot affect output |
| B-09 | RNG draw injection | B | fixed draw ledger | no implicit/global draw; same consumption |
| C-01 | True-state poison | C | alter hidden opponent/ball values without changing view | cognition options/values/intent unchanged |
| C-02 | Observation sensitivity | C | alter visible observation only | change permitted and causally traced |
| C-03 | Belief isolation | C | two athletes receive different views | beliefs and decisions remain individual |
| C-04 | No MC retarget | C | intent target conflicts with legacy preferred target | command keeps target or explicitly rejects |
| C-05 | Delay preservation | C | controlled perception/reaction/prep/release delays | all timing boundaries present and honored |
| C-06 | Supersession | C | new intent during queued execution | explicit new ID, edge, interruption outcome |
| C-07 | Catch preparation | C | catchable and deceptive trajectories | intent, reach/takeoff command, physical result separable |
| C-08 | Jump owner | C | catch/shot/Keeper jump | exactly one cognition decision; no cadence bypass |
| C-09 | Keeper ownership | C | step/dive/jump/gather/parry cases | view-based intent, MC execution, PHY outcome |
| C-10 | Archer information isolation | C | hidden target/ball variations | options and aim unaffected unless observed/believed |
| C-11 | Archer command fidelity | C | aim/release selections | MC does not substitute target/fire/hold decision |
| C-12 | Archer physical resolution | B/C | fixed release command/draws | PHY flight/hit/freeze parity; decision independently verified |
| C-13 | Apparent vs actual legality | C | mistaken view of legality | attempt can be accepted then adjudicated; no truth leak |
| C-14 | Unavailable semantics | C | each absence reason | correct enum; no null/zero substitution |
| C-15 | Formation-free constraint | C | neutral symmetric setup | no role/slot anchor unless rule-required or consciously selected |
| C-16 | Provenance | C | legacy, athlete, team, rule cases | correct owner tag and no forged option/value data |
| C-17 | Stable causal IDs | A/B/C | repeat/replay | identical execution yields identical IDs; telemetry level irrelevant |
| C-18 | Observer neutrality | A/C | telemetry off/min/full | no scheduling, RNG, state, or decision changes |
| P-01 | Supervisor portability | A/B | timeout and injected error | correct classification, atomic manifests, safe restart |
| P-02 | No SIGALRM dependency | B/C | platform without signals | external deadline and worker termination operate |
| P-03 | Numeric portability | B | cross-platform trace replay | structural equality and approved tolerances |

## 3. T3 tolerance proposal retained for future approval

| Quantity | Proposed comparison |
|---|---|
| Discrete states, owners, event types/order | exact |
| Tick-bound deadlines and integer millisecond times | exact |
| Swept/contact event time | ±1 ms only where native root solving crosses ticks |
| Non-contact position/velocity | absolute `1e-6`, relative `1e-9` |
| Contact/bounce position/velocity | absolute `1e-4`, relative `1e-8` |
| Acceleration | same class as the producing path; must be declared per trace |
| Fatigue/condition scalar | absolute `1e-8` |
| Damage/very small accumulators | absolute `1e-10` |

These are proposed parity thresholds, not physics-correctness tolerances. Native
acceptance requires cross-platform evidence before ratification.

## 4. T3 coverage gaps requiring T3A authorization

Accepted T3 does not support a complete native parity claim for:

- Archer load/draw/aim/release, flight, hit, freeze, immunity, and lane motion;
- Keeper set/step/dive/jump/gather/parry and reverse-flight interception;
- general jump takeoff, airborne state, contact, and landing;
- receiver reroute/interception;
- HAND_FIGHT contention;
- carry-pose transitions and pose-dependent tackle/strip;
- simultaneous or contested catch acquisition;
- an isolated historical kick physical trace;
- several internal C3 substep values not emitted by T3.

Proposed T3A fixtures must suppress cognition and inject explicit commands, use
independent feature configurations, record command/draw provenance, and remain
separate from B0. T6 does not authorize their creation.

## 5. Performance reporting

Every performance validation reports import/setup, simulation, instrumentation,
serialization, and supervisor overhead independently. Regulation completions,
forfeits, timeouts, errors, and censored runs use separate denominators. Keeper
pathology observations are diagnostic and never included as completed matches.
