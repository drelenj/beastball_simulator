# HP-002 — Review R5 of Codex G1 candidate (commit c083ae9)
Claude, 2026-11-12. Clean checkout of `b1/m1-decision-outcome` at c083ae9.

## OWNER BRIEFING
1. **Accomplished.** Codex built the governed three-athlete scenario: a carrier and a defender who both decide from their own perception, and a receiver body who can catch. I reproduced everything: 17 tests pass, and the full 400-episode matrix reproduces Codex's matrix hash and every episode hash exactly (my run 134 s).
2. **What B1 can do now.** The carrier chooses between carrying and passing from its own belief, the defender pursues from its own belief, and the engine decides catch, drop, grounding and loose balls. Over 400 episodes the real physics produced completed passes, loose balls, carrier groundings, one interception and carries to the goal line.
3. **Unproven.** The matrix does not yet show what M1 exists to show. The defender's quality has **no effect**: sharp defender and uniform defender gave the same endpoint in all 100 seeds. The defender almost never intercepts (1 in 400). The "causes" of failures are assigned after the fact by a rule that can never answer "unknown", and two of the labels are wrong.
4. **Blocking M1 acceptance.** H1 (defender never meaningfully contests the pass), H2 (failure attribution is by construction), H3 (BA-M1-3 not actually shown). The scenario geometry I wrote contributed to H1; I have revised it.
5. **Recommended action.** Relay R5 to Codex with the revised scenario (`M1_SCENARIO_v2.json`). M1 is a small step from acceptance, not a rebuild. Nothing for you to decide.

## Verified (TESTED by me)
17 tests pass (13 s). Matrix: `matrix_hash` equal; all 400 execution and state hashes equal. Per condition: C0 75 completed / 25 loose; C1 75 / 25; C2 74 / 26; C3 0 completed, 86 + 2 + 1 loose, 7 reach x=90, 3 grounded, 1 intercepted.

## Findings
**H1. The defender cannot affect the pass in C0–C2.** C0 vs C1 end the same way in 100/100 seeds (execution hashes differ, so the rating change does something, but never the outcome). In seed 2 of C0 the defender walks toward the carrier's lane and never reaches the ball. The v1 geometry (defender at (53,52), receiver at (49,62)) leaves no time to intercept. That was my scenario design. Separately, I could not confirm from the trace that the defender tracks the ball once it is in flight: *Codex to show it does, or fix it.*
**H2. Failure attribution cannot say "unknown".** `_failure_cause` ends in a default `belief_error`, so "unknown = 0" holds by construction. Two labels mislead: in C0–C2 all 25 losses are `physical_contest: accepted catch kernel did not secure control`, a receiver catch failure with no contest (the defender never touches anything); in C3 86 of 100 are `latency: release origin shifted`, which is the carrier running during its wind-up (see H4). *Fix:* derive causes from recorded events, add `receiver_catch_failure` and `carrier_motion_during_windup`, allow `unknown`, and test that it can occur.
**H3. BA-M1-3 not shown.** Codex's check is "mixes are not all identical". It passes because C3 uses a different defender position. The criterion was that a sharper defender changes the outcome mix; C0→C1 changes nothing. With the revised scenario (C4 vs C5, same geometry, defender 4 m off the lane) the comparison becomes meaningful.
**H4 (verify; may be engineering).** In C3 the carrier keeps running while its pass winds up, so the release origin moves 2–3 m from where it aimed (seed 1: pass decided at (63.3, 40.9), released from about (69, 40.6)). Check the action-resource table: locomotion + ball_control_release compatibility defaults to NO unless an explicit override exists. If so, the carrier should not be running during wind-up, or the aim must be recomputed at release.

## Smaller notes
- Carry always scores 2.0 and defender "move" scores about 9.9 constant: placeholder values, acceptable for M1 but they carry no weighing. Not a behavioral-quality claim, as Codex says.
- `Contact.has_ball` exists and is always False (no leak). BR checks: cognition imports only `dataclasses` and `math`.
- The carrier's carry goal `(90, 50)` is supplied by configuration (an athlete goal, acceptable).

## Gates
BLK-01..05 unchanged from R3. BA-M1-1 pass (all four outcomes observed across the matrix, interception rare); BA-M1-2 partial; BA-M1-3 not shown; BA-M1-4 pass; BA-M1-5 pass (reproduced); BA-M1-6 pass (134 s). **M1 NOT YET ACCEPTED.**
