# HP-002 — M1 behavioral acceptance criteria and information-boundary review protocol
Claude, 2026-11-11. Status: **DESIGN COMPLETE (acceptance criteria and review protocol)**. Not implemented, not tested. Owner assigned me behavioral acceptance, information-boundary review, and the judgment of whether the implemented athlete genuinely owns its decisions. The five M1 safeguards BLK-01..BLK-05 are mandatory gates; **I have not received their text** (see the closure record), so they are not restated here and cannot be marked.

## 1. Does the athlete own its decisions? Seven tests (OWN-1 to OWN-7)
| ID | Test | Pass condition |
|---|---|---|
| OWN-1 Isolation (poison) | After perception, replace every authoritative field not present in `AthleteView` with sentinels (true entity positions, ratings, timers, RNG states outside the cognition streams) | Decision record (selected option, option scores, plan) byte-identical |
| OWN-2 True-state invariance | Perturb true state while the delivered `ObservationFrame` is held fixed | Decision unchanged |
| OWN-3 Counterfactual sensitivity | Hold true state fixed; alter the delivered frame (defender seen farther, nearer, or not seen) | Decision changes in the direction the option scoring predicts; scores recompute from the altered belief |
| OWN-4 Provenance | Every `ActionIntent` resolves `intent → decision → belief revision → observation(s)`; every decision lists the options evaluated with scores and the selection rule; stochastic selection records its named cognition-stream draws | 100% resolvable; recorded rule reproduces the selection |
| OWN-5 No override | Diff each `MotorCommand` against its `ActionIntent` (kind, semantic target, release window); static and runtime check that no legacy controller or tactical hook can set a target or action | Zero silent replacements; any change is a new intent with a `supersedes` edge and cause; zero decisions tagged with a legacy source |
| OWN-6 Timing legitimacy | `decided_at >= delivered_at` of its observation; decisions only at opportunities allowed by the cadence model; `not_before` honored | Zero violations |
| OWN-7 Belief honesty | Move D out of A's cone and radar | Belief age and uncertainty grow; no jump to the true position; unknown stays `unavailable` or stale, never silently corrected |

## 2. Behavioral outcome criteria (M1)
| ID | Criterion |
|---|---|
| BA-M1-1 | Over 100 seeds per condition of `M1_SCENARIO_v1.json`, the outcome set includes at least pass completed, pass intercepted or incomplete, and carrier grounded. Counts are reported per condition |
| BA-M1-2 | Every failure outcome resolves to a cause in the trace: belief error, latency, or physical contest. "Unknown cause" count is zero |
| BA-M1-3 | A carrier with limited vision (C2) shows a different decision mix from the uniform carrier (C0), and a sharper defender (C1) changes the outcome mix. Direction reported; no pass/fail threshold set in advance (owner deferred Gate C tolerances) |
| BA-M1-4 | No decision depends on a receiving position, formation or role assigned from outside the athlete (`formation_or_role_assignment` is an excluded class and a static check) |
| BA-M1-5 | Determinism: the same seed and configuration reproduce identical trace hashes and identical `CausalId`s; telemetry off, minimal and full give identical IDs |
| BA-M1-6 | Reported, not gated: decision latency distribution (observation delivery to decision), decisions per second, and run time per episode on the target |

## 3. Information-boundary review protocol (my independent review of Codex's code)
I review the merged candidate; I do not write the implementation. Review steps:
| Step | Check | Method |
|---|---|---|
| BR-1 Import graph | The B1 cognition package imports only the typed boundary, the sensor/belief components and math. No import of `engine`, `match`, `types` (legacy), `pocket4_proto`, or anything exposing live state | Static scan of imports and attribute names; fails the build |
| BR-2 Symbol scan | Forbidden symbols in cognition code: `s.players`, `.ball.` on the live state, `with_view`, `Policy`, `pol[` | Static scan |
| BR-3 Single entry point | Cognition is called through one function whose arguments are an `AthleteView` and immutable config; there is no global or closure over the engine | Code review plus a test that calls it with only those arguments |
| BR-4 Serialization-boundary replay | Serialize each `AthleteView` to JSON, run cognition in a separate process that has no access to the simulation, compare decisions with the in-process run | Byte-identical decisions. This proves no hidden shared state |
| BR-5 Motor Control boundary | MC accepts no `SelfView`, belief or option objects; perturbing `SelfView` leaves MC output unchanged for identical commands | Type check plus perturbation test |
| BR-6 Trace audit | Random sample of 50 decisions: reconstruct the athlete's knowledge at the decision time from the trace alone and confirm the chosen option follows | Manual and scripted |
| BR-7 Legacy absence | Run with the B0 tactical controllers made unimportable; the slice still runs | Import-block test |
Any failure is a BLOCKING finding in the directive's format: failure scenario, affected requirement, minimum correction.

## 4. Reporting to the owner
Each M1 report starts with the OWNER BRIEFING and then separates DESIGN COMPLETE, IMPLEMENTED, TESTED and ACCEPTED. A criterion is TESTED only when its automated test exists and passes with an evidence artifact; I mark OWN-n and BR-n individually.
