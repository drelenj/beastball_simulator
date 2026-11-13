# SPRINT-45 — review findings to obey (extracted from R5, R6, pass-release-v1)

Sources (branch `claude/hp002-audit`, read-only): `audit/m1/HP-002_M1_G1_REVIEW_R5.md` (commit c083ae9),
`audit/m1/HP-002_M1_G1_V2_REVIEW_R6.md` (commit 77604e1), `audit/m1/HP-002_M1_MOVING_RELEASE_CONTRACT_v1.md`.
Extraction only; nothing here is ACCEPTED.

## (a) Evidence-honesty rules for reports

| # | Source | Finding | Rule |
|---|---|---|---|
| E1 | R6 H3 | "35 paired differences" was offered as a quality effect. C0 and C1 differ in 100/100 execution hashes; on fresh seeds 171/400 pairs end differently, in both directions. | DON'T cite "N paired endpoint/hash differences" as an effect. Any perturbation changes hashes. |
| E2 | R6 H3 | Interceptions 8 -> 11 on 100 seeds; on 400 fresh seeds 41 vs 44, gained 37, lost 34, sign test p about 0.81. | DO state seed count, paired gains vs losses and a sign-test p-value for any outcome comparison. DON'T claim an effect from counts alone. |
| E3 | R6 H3, ask 1 | Effect must be "demonstrated at mechanism level, not inferred from outcome counts". | DO show the mechanism in traces (option selected, distance to lane, rate conditional on the option) before any effect claim; otherwise write "not shown". |
| E4 | R5 H3, R6 H3 | Acceptance flag passed on "mixes are not all identical" / `c4 != c5 and paired > 0`, true for any perturbation. | DON'T write a check that cannot fail. For each test show the failing case. |
| E5 | R5 H2 | `_failure_cause` ended in a default label, so "unknown = 0" held by construction. | DO derive causes from recorded events; residuals are `unknown`; report the unknown count. Test that `unknown` can occur. |
| E6 | R6 H2 residual | `pass_accuracy_failure` is a by-elimination label (32 of 63 C3 failures). | DON'T name a cause without positive evidence; split it with evidence or call it `unknown`. |
| E7 | R5 H2 | Labels misled: `physical_contest` for a catch failure with no contest; `latency` for carrier motion in wind-up. | DO name a cause after the event actually recorded, not the nearest category. |
| E8 | R6 H4, ask 3 | Report called the release overlap an "approved separable bundle"; O4 v3.5 is a draft (`YES*`). | DON'T write "approved", "accepted" or "canon" for anything not in the owner decision record. |
| E9 | R6 H3 | "isolates only Judgment/Reaction" was inaccurate: C5 also raised all JUDGE ratings to 0.9. | DO list every variable a condition changes; don't claim isolation that the config does not give. |
| E10 | R5 notes, R6 H3 | Placeholder constants (carry 2.0, defender move about 9.9; step at judgment about 0.9). | DO label hand-set constants as provisional policy; no behavioural-quality claim from them. |
| E11 | R5/R6 gates | Both end "M1 NOT YET ACCEPTED". | DO separate DESIGN COMPLETE / IMPLEMENTED / TESTED / ACCEPTED. Nothing is ACCEPTED. |
| E12 | R6 H1 | A thin test (`{}` input) proves the branch exists, not the behaviour. | DO say when a test is thin; report what was reproduced versus only read. |

## (b) Moving pass-release contract `pass-release-v1` (DESIGN COMPLETE draft; engineering contract, not canon)

1. Scope: pass release only. A carrier may keep `locomotion` running while a `ball_control_release` pass is pending, wound up and released. Shots, kicks and held-ball kicks stay NO.
2. The intent carries a semantic aim fixed at decision time (target entity, aim point, admitted release speed); it is not refreshed from later beliefs.
3. Motor Control MAY, at the release tick, recompute only the horizontal direction from the authoritative own-body release origin toward the semantic aim, preserving admitted speed and vertical component.
4. Motor Control MAY NOT change action type, target entity, receiver or aim point, read opponent or receiver true state, or lead the receiver.
5. Bound (provisional default, "to be tested"): a required direction correction above 60 degrees is rejected as `rejected_geometry` and fed back to cognition. Trace must record release origin, semantic aim, recomputed flag, correction angle in degrees, admitted speed, final ball velocity. Tests MR-1..MR-5. With the contract on, `carrier_motion_during_windup` must not be used as a cause. Open: whether the engine adds carrier velocity to the ball.

Note for the sprint: the Round 1 motor (`motor.pass_release`) uses the B0 `plan_pass` on the receiver's true kinematics, which item 4 forbids (reads receiver true state, leads the receiver).

## (c) Open item H3 — why M1 is not accepted

- H3 = BA-M1-3: a sharper defender must measurably change the outcome mix.
- R5: "BA-M1-3 not shown" — C0 -> C1 changed nothing in 100/100 seeds; the check passed only because C3 used a different position.
- R6: "H3 NOT SHOWN (narrow)" — C4 vs C5 on fresh seeds 101-500: interceptions 41 vs 44, gained 37, lost 34, p about 0.81; completed 250 vs 244. The mechanism exists (3 of 12 traced seeds chose the lane option, all three intercepted) but is a step on a hand-set constant and fires in a minority of runs.
- R6 gate line: "BA-M1-3 mechanism present, outcome effect not distinguishable from noise … M1 NOT YET ACCEPTED (one narrow item)."
- Whether commit `4b19719` closes H3: NOT FOUND in the three documents read (they predate it).
- H1 CLOSED, H2 CLOSED with one residual, H4 CONDITIONALLY CLOSED (R6). BLK-01..05 "unchanged from R3".
