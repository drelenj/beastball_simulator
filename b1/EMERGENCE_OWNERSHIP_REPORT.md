# Emergence ownership enablers

Baseline: accepted M1 commit `4b19719`. M2 remains unauthorized.

This change adds an opt-in, instance-local ownership overlay. It does not edit
the accepted `b1/core.py`, `b1/runtime.py`, historical engine source, or B0
loader behavior.

## Implemented seams

- **Keeper:** a delivered 3-D ball belief produces a typed `save`, `position`,
  or `hold` intent. Motor Control alone tests reachability and produces a
  step, approach, launch, or explicit `rejected_infeasible` result. Missing or
  stale belief has no true-ball fallback. Existing ball contact, catch,
  landing, recovery, locomotion limits, and goal rules remain authoritative.
- **Restart:** the legal mark, clearance, prescribed scrimmage snapper, timing,
  and any mandatory legal spots come from an immutable rules decision record.
  Athletes approach the spot, then emit taker claims and movement intents.
  The first valid claim is admitted; simultaneous claims use canonical intent
  ordering rather than an engine distance/role ranking. The prescribed snapper is
  exclusive until the accepted 3.5-second scrimmage fallback; this is distinct
  from the 3.0-second snap40 minimum. Motor Control receives targets without
  using either legacy `targets_dead` planner or formation tables.
- **Archer:** mobile-lane movement targets the delivered ball belief. Lane
  limits, acceleration, braking, eligibility, and reload validation remain
  physical/rules contracts. No belief means brake/hold, not true-ball follow.
- **Release withholding:** the legacy `c3_withhold` controller veto is disabled
  only in the opt-in overlay. Whether to attempt is an explicit athlete intent
  from its own restraint belief. Authoritative C3 restraint, preparation
  slowdown, tuck, release precedence, loss-of-control interruption, and final
  release physics are unchanged.

## Explicit temporary contracts and limits

- Sensors must supply already-delivered Keeper and Archer beliefs. This branch
  does not create a second perception system or use `prism_keeper_v0`'s true
  fallback.
- Rules still validate restart readiness, offside, retakes, deadlines, mark,
  and release. Legacy automatic restart recipient/trajectory selection remains
  a named temporary contract; replacing it would expand beyond the requested
  narrow taker/positioning seam.
- First Hunt contestant selection is outside this change.
- A fixed venue platform may be declared static by an experiment profile. The
  mobile-lane overlay must be installed after legacy platform hooks so a
  repeated teleport cannot overwrite it.
- There is no team plan, role-assignment, or communication layer here.

## Activation

An experiment worker constructs its normal Match, then installs
`EmergenceOwnershipOverlay` with two callbacks:

```python
overlay = EmergenceOwnershipOverlay(
    match,
    keeper_belief=lambda athlete, now_ms: delivered_keeper_belief(athlete),
    archer_ball_belief=lambda athlete, now_ms: delivered_ball_belief(athlete),
).install()
```

The callbacks must not return authoritative engine objects. They return frozen
`BallCourseBelief` values. Feature-off behavior retains the historical
controllers.

## Verification target

`python -m unittest b1.test_m1 b1.test_g1 b1.test_emergence_ownership -v`

The new tests cover belief-only Keeper and Archer decisions, stale-belief
handling, Motor Control rejection ownership, the scrimmage fallback boundary,
restart intent positioning, the explicit release choice, the complete
accepted-tree inventory, and untracked-file neutrality.
