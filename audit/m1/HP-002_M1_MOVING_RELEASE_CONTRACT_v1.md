# HP-002 M1 — Moving pass-release contract v1 (action-specific separability)
Claude, 2026-11-13. Status: **DESIGN COMPLETE (draft)**. Codex's recompute-at-release is **IMPLEMENTED, TESTED on one seed, not ACCEPTED**. This is an ENGINEERING contract, not canon; no owner decision needed.

## Why it exists
O4 v3.5 lists `locomotion + ball_control_release` as `YES*`: allowed only under an action-specific separability contract. None existed, so Codex's report called the overlap "approved". This is that contract, scoped to M1.

## Contract `pass-release-v1`
**Scope.** Pass release only. Shots, kicks and held-ball kicks stay NO until each has its own contract.
**Concurrency.** A carrier may keep a `locomotion` command running while a `ball_control_release` pass command is pending, wound up and released. Neither command revokes the other. Contact resources stay exclusive (NO).
**Aim.** The intent carries a semantic aim fixed at decision time: target entity, aim point, admitted release speed. The aim is not refreshed from later beliefs; a changed aim requires a new decision.
**Motor Control may.** At the release tick, recompute only the horizontal direction from the authoritative own-body release origin toward the semantic aim. Preserve admitted speed and vertical component.
**Motor Control may not.** Change action type, target entity, receiver or aim point; read opponent or receiver true state; lead the receiver. Anything beyond direction recomputation is cognition's job.
**Information.** The own-body release origin is own proprioception (allowed under SELF-1). The boundary reviewer's checks BR-1..7 still apply.
**Bound (provisional default, to be tested).** If the required direction correction exceeds 60 degrees, reject the release as `rejected_geometry` and feed that back to cognition. Codex currently has no bound; the 60 degree value is my proposal and must be confirmed against traces.
**Engine check (open).** Codex must confirm whether the engine's release adds the carrier's velocity to the ball. If it does, recompute before adding, and the test below must hold on the final ball velocity.

## Trace requirements
Release outcome records: release origin, semantic aim, recomputed flag, **correction angle in degrees** (missing today), admitted speed, final ball velocity.

## Failure attribution
With this contract on, `carrier_motion_during_windup` cannot occur and must not be used. Flight error is then belief aim error, receiver catch failure, defender contact, or a residual that is labeled `unknown` unless positive evidence exists.

## Acceptance tests
- MR-1: carrier moving at wind-up start; final ball direction within 8 degrees of the semantic aim from the release origin (existing test covers seed 1 only; extend to at least 20 seeds).
- MR-2: action type, target and aim in the outcome equal those in the intent.
- MR-3: perturbing hidden receiver/opponent true state with the view fixed leaves release direction unchanged.
- MR-4: correction above the bound produces `rejected_geometry` and next-decision feedback.
- MR-5: contract off (locomotion held) reproduces the earlier behavior.

## Registry entry
`ball_control_release+locomotion: YES* [pass-release-v1]` as a versioned contract, per O4-3. All other pairs unchanged.
