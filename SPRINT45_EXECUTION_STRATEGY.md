# SPRINT45 EXECUTION STRATEGY

Experimental sprint, 45 minutes, autonomous. **Nothing is ACCEPTED.** M1 is not accepted (open item H3).

## Bases and branch

- Branch `experiment/prism-sprint-45`, created from `4b19719` (`b1/m1-decision-outcome`, G1 after R6) and pushed empty first to prove push access.
- **Deviation note:** the prompt's Phase A names `77604e1`; section 2 and Phase B step 0 name `4b19719`. `77604e1` is the parent of `4b19719`, so `4b19719` contains it. `4b19719` was used.
- `git merge --no-ff origin/experiment/prism-sprint-30` (Round 1, `99cf83a`): conflict-free. Before any change, the seed-1 match on the merged tree reproduced Round 1's trace hash `02b95a47…` (A 9 – B 3, 42,143 decisions).
- Frozen B0 `2abe497` is not edited. No merge into `main`, `b1/m1-decision-outcome` or `experiment/prism-sprint-30`.

## What Round 2 builds

1. **`b1/possession.py`** — new pure rules-state layer (direct / passive / contested possession, P-1 timer, team control, zone clocks, restarts) per the owner decision record, fed only by authoritative engine events (touch, control, release, restart), never by athlete beliefs.
2. **Rules signals through the view** — athletes learn possession and phase only from perception and from rules signals delivered through the latency-delayed `AthleteView`.
3. **One pipeline** — the N-athlete loop reuses Base A's pass-lane decision and the `pass-release-v1` contract (direction recomputation only, 60 degree bound) instead of Round 1's release planning on true receiver state.
4. **Ruleset 1.0.2 for the B1 match instance** (B0 stays 1.0.1): an arrow freezes any eligible player; a Keeper inside own zone stays protected (KP rules).
5. **Archer release legality from the Archer's own belief** — the Round 1 true-state interlock is removed.
6. Anything the decision record does not settle is a labeled provisional primitive or raises `UnresolvedOutcome`.

## Phases (real clock, `SPRINT45_TIMING.log` at each boundary)

| Phase | Minutes | Work |
|---|---|---|
| A | 0–3 | Clock, branch, empty push |
| B | 3–20 | Integrate (target minute 9), then skeleton on the real engine: one pipeline, possession layer, field players, Keeper and Archer, full 2 x 120 s match |
| C | 20–33 | Deepen the weakest connected stage; fix failures; tighten the boundary |
| D | 33–40 | Validation; hard stop on features at minute 38 |
| E | 40–45 | Reports generated from recorded evidence by script; commit; push |

If time runs short: stop features, keep the strongest working build, run the highest-priority checks, report accurately, commit, push.

## Evidence rules being followed

- Every test must be able to fail; boundary tests come with their failing counterpart.
- No effect claims from outcome counts alone: mechanism in traces plus paired gains, losses and a sign-test p-value, seed count stated.
- Failure causes come from recorded events; residuals are `unknown` and counted.
- "Approved", "accepted" and "canon" are used only for items in the owner decision record.
- Status words: DESIGN COMPLETE / IMPLEMENTED / TESTED / ACCEPTED.
- Required: frozen-B0 identity check, existing B1 tests, one seed replayed twice, one end-to-end match with causal trace, possession tests (P-1 at 250/500/1000 ms, C-1..C-3, zone-clock resets), a fresh agent running OWN-1..7 and BR-1..7. Extra seeds only if time remains.
- Extracted review findings: `b1/sprint45/REVIEW_FINDINGS.md`.

Actual outcomes: see SPRINT45_IMPLEMENTATION_REPORT.md
