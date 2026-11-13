# OWN / BR checklist (extracted for SPRINT-30)

Source: `origin/claude/hp002-audit:audit/m1/M1_BEHAVIORAL_ACCEPTANCE_AND_BOUNDARY_REVIEW.md` (tables, lines 7-13 and 29-35).
Canon items: `audit/HP-002_B1_FINAL_APPROVAL_CANDIDATE_v1.0-rc2.md` §12 (lines 335-343) and row PO-6.
Wording is condensed; IDs are exact. "Falsified if" is how a test can fail.

## Ownership (does the athlete own its decisions?)

| ID | Requirement | Falsified if |
|---|---|---|
| OWN-1 Isolation (poison) | After perception, replace every authoritative field not present in `AthleteView` with sentinels (true positions, ratings, timers, RNG states outside cognition streams). Decision record (selected option, option scores, plan) must be byte-identical. | Any decision byte differs after poisoning. (R1 F4: poisoning a dict that is never passed anywhere proves nothing.) |
| OWN-2 True-state invariance | Perturb true state while the delivered `ObservationFrame` is held fixed. Decision unchanged. | Decision changes with the view fixed. |
| OWN-3 Counterfactual sensitivity | True state fixed; alter the delivered frame (defender seen farther, nearer, not seen). Decision changes in the direction the option scoring predicts; scores recompute from the altered belief. | Decision or scores do not move, or move against the scoring rule. |
| OWN-4 Provenance | Every `ActionIntent` resolves intent → decision → belief revision → observation(s); every decision lists options evaluated with scores and the selection rule; stochastic selection records its named draws. 100% resolvable; recorded rule reproduces the selection. | Any intent with a dangling ID, or re-applying the recorded rule to the recorded options picks a different option. |
| OWN-5 No override | Diff each `MotorCommand` against its `ActionIntent` (kind, semantic target, release window); static and runtime check that no legacy controller or tactical hook can set a target or action. Zero silent replacements; any change is a new intent with a `supersedes` edge; zero decisions tagged with a legacy source. | A command (or the physical release) has a kind/target/receiver different from its intent; a legacy hook is reachable. |
| OWN-6 Timing legitimacy | `decided_at >= delivered_at` of its observation; decisions only at cadence opportunities; `not_before` honored. Zero violations. | Any decision earlier than its observation's delivery, or off-cadence. |
| OWN-7 Belief honesty | Move a body out of the athlete's cone and radar. Belief age and uncertainty grow; no jump to the true position; unknown stays unavailable or stale, never silently corrected. | Believed position tracks the true position while unobserved. |

## Boundary review

| ID | Requirement | Falsified if |
|---|---|---|
| BR-1 Import graph | Cognition package imports only the typed boundary, sensor/belief components and math. No `engine`, `match`, legacy `types`, `pocket4_proto`, or anything exposing live state. | Static scan of `Import` and `ImportFrom` nodes finds a forbidden module. (R2 F16: scan both node kinds.) |
| BR-2 Symbol scan | Forbidden symbols in cognition code: `s.players`, `.ball.` on live state, `with_view`, `Policy`, `pol[`. | Static scan finds one. |
| BR-3 Single entry point | Cognition is called through one function whose arguments are an `AthleteView` and immutable config; no global or closure over the engine. | Entry point needs anything else, or module-level mutable/engine state exists. |
| BR-4 Serialization replay | Serialize each `AthleteView` to JSON, run cognition in a separate process with no access to the simulation; decisions byte-identical to the in-process run. | Any difference; or the replay process has simulator modules loaded. |
| BR-5 Motor Control boundary | MC accepts no `SelfView`, belief or option objects; perturbing `SelfView` leaves MC output unchanged for identical commands. | MC signature takes belief/options, or output changes under the perturbation. |
| BR-6 Trace audit | Random sample of 50 decisions: reconstruct the athlete's knowledge from the trace alone and confirm the chosen option follows. | Any sampled decision not reproducible from the trace. |
| BR-7 Legacy absence | Run with the B0 tactical controllers made unimportable/trapped; the slice still runs. | Run fails or a trap fires. |

## Open canon items (all UNRESOLVED; do not present any provisional handling as canon)

| ID | Open question |
|---|---|
| U-1 | Keeper protection against tackles, incidental arrows and other contact (cells KP-01…KP-14). |
| U-2 | Possession attribution vs. team control for the zone 5-second clock during loose/airborne states; the reset rule; Keeper phase basis (KP-12). |
| U-3 | Keeper Zone boundary geometry: reference point for ball and for athlete, edge inclusivity (G-1…G-6). B0 uses a point-position circle. |
| U-4 | Bounces, deflections, out-of-play and restarts: rules-state transition table (scenarios U4-01…U4-13). |
| R-RS | Ruleset 1.0.1 vs 1.0.2 for Archer freeze eligibility. B0 config is 1.0.1: a freeze is valid only against the ball carrier. |
| SELF-1 | Is an athlete's knowledge of its own capabilities exact, or an individual estimate? Plan default: exact (null case), not canon. |

rc2 test CFG-5: a required value that is unresolved should fail configuration validation, not default silently.
