# HP-002 — M1 `AthleteView` subset (field by field)
Claude, 2026-11-11. Status: **DESIGN COMPLETE (draft for Codex confirmation)**. Based on T6 `TYPED_CONTRACTS.md` §3-§5 with the self-knowledge split Codex confirmed (`MotorFeedback` / `SelfView.proprioception` / `AthleteKnowledge.self`). Nothing implemented.

## 1. What the M1 carrier A may read
| Group | Fields | Source | Notes |
|---|---|---|---|
| `ObservationFrame` header | `observation_id, observer, captured_at, delivered_at, sensor_model_version, attention_state` | Sensor model (cone, radar, latency) | `delivered_at >= captured_at` always |
| `observed_entities` | for each entity inside A's cone or radar: `entity_id`, apparent position, apparent velocity, uncertainty, capture time, team (apparent) | Sensor model | Teammate T and defender D are observed, **not read true**. B0 read teammates true; that is a CHANGE |
| `observed_ball` | `Availability<ObservedBall>`: A's own carried ball is `own_carry` (via SelfView); otherwise observed like an entity | Sensor model | |
| `observed_arrows` | empty (no Archer in M1) | | |
| `public_match_state` | `ball_status`, `PA`, `TC`, `last_toucher`, tackle count if defined | Rules state | Fields depending on U-1..U-4 (zone clocks, `origin`, Keeper protection) are `unavailable(UNRESOLVED_RULES_STATE)` |
| `communications` | empty (no teammate cognition in M1) | | |
| `SelfView.proprioception` | own pose, velocity, carried-ball state, contact felt | Exact, zero latency (null case, D6) | Not the authoritative state object |
| `AthleteKnowledge.self` | stable estimates of own capabilities | Rating-derived, zero error (labelled placeholder) | Exact ratings are never exposed as such |
| `AthleteKnowledge.others` | learned estimates of other athletes' capabilities | **Starts uninformed**; inferred from observed body dimensions and behavior (owner ruling of 7 Nov) | No opponent ratings, no hidden timers |
| `belief_revision` | id of the latest belief revision | PRISM belief update | |
| `apparent_legal_actions` | advisory, view-relative | Rules summary | |

## 2. What A may not read (must be absent or fail a poison test)
Any live athlete object or engine handle; true positions or velocities of other athletes; any opponent rating, fatigue reserve, timer or intent; the true ball state when the ball is not A's own; B0's `with_view` patching surface; the full `SimState`.

## 3. D (defender) and T (teammate)
D uses the same boundary and the same field list (as a defender). T has no cognition: it is a physical body only and appears in A's view like any other observed entity.

## 4. Motor Control inputs
`MotorFeedback` (command-local authoritative body projection), `MotorCommand`-local constraint projection. MC never receives `SelfView`, beliefs or tactical state.

## 5. Open questions (none blocking M1)
Unavailable-field typing for U-dependent rules fields is the only place the schema is not final; it is frozen as `Availability::unavailable(reason)` in v1-core.
