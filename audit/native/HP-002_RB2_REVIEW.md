# HP-002: independent review of RB-2 (codex/rulebook-2 @ cff4b92)
Claude, 16 Nov 2026. Status: REVIEW COMPLETE. RB-2 is IMPLEMENTED and TESTED by Codex's account and by my reruns; nothing is ACCEPTED.
Verified by running: full suite 292 passed (23 subtests) in 126 s; focused Rulebook suite 95 passed; diff vs RB-1 shows no change to b1/*, native/cognition.py or committed evidence files; config rejects any scoring other than banded; six matrix rows (RT3, RT6, RS6, RA2, RA4, RO6) now say forced scenario only. Not verified: B0 blob count, replay hashes, RB-2 full matches (none were run).

## Findings
| ID | Sev | Finding | Fix |
| --- | --- | --- | --- |
| R2-1 | Medium (CANON conflict) | A team's own flight redirected into its own goal by an opponent no longer scores the flat own-goal value. Probe: A passes from 25 m toward its own goal, B touches it, it enters A's goal; B is credited 4 (a 20+ release band), no own goal recorded. Cause: engine touch clears last_releaser, and RB-2 removed rb_deliberate_team, so nothing remembers the releasing team. Owner ruling (Oct 2026): an own team's flight redirected into its own goal by an opponent scores a flat own-goal value regardless of where it was redirected from. | Keep a release-only team marker (set on release, never on touch; cleared on acquire and award). Own goal when the marker team is the team whose goal was entered. F2 stays correct (shooter's shot deflected by the defender into the defender's goal is an ordinary goal). Add the pass-deflection regression test. |
| R2-2 | Medium (F6 not met) | carry_attempts is incremented only inside goal() when a carry scores, so carry attempts always equal carry goals (the test asserts it). Success rate is 100% and points per attempt is always 5. This is the defect F6 named. | Define a carry attempt (for example: a carrier with the ball inside the scoring zone, or reaching the goal plane) and count it when it happens, scored or not; keep the independent counter; add a test with a failed carry. Define the term in the report. |
| R2-3 | Low | The RB-2 report says F6 corrected without noting R2-2, and "carries independent attempts" is overstated. | State plainly until R2-2 is fixed. |

## Per-finding verdicts (RB-1 F1-F14)
F1 PASS (stale own goal from interception covered and reproduced by test). F2 PASS for the ruled case (see R2-1 for the adjacent Oct case). F3 PASS (banded full award 3 in period 4 and OT; period 1-3 award 1). F4 PASS (toss timeout at the goal line spots 5 m in). F5 PASS (defender non-carrier hold routes to the defence branch). F6 PARTIAL (shot-only bands correct; carry attempts wrong, R2-2). F7 PASS. F8 PASS (78% penalty awards and 65% illegal arrows disclosed). F9 PASS by test, not independently probed for no-goal rulings. F10 PASS. F11 PASS. F12 PASS (arrow_speed 250.0 stored). F13 PASS and documented (possession change resets only the Archer newly eligible). F14 PASS.

## Verdict
Conformance PASS WITH FINDINGS. Banded basis PASS. Honesty of report: PASS WITH FINDINGS (R2-3). Recommend a small RB-2.1 (R2-1, R2-2) before any banded full-match soak, since both distort the scoring counters that soak will report.

## Addendum: RB-2.1 re-review (codex/rulebook-2 @ b4cd38d), 16 Nov 2026
Verified by running: full suite 294 passed (23 subtests); four probes.
- R2-1 CLOSED: A's pass deflected by B into A's goal = own goal, B credited 2, own_goals recorded. F2 intact: A's shot deflected into B's goal = ordinary 20+ band goal for A (4); mirror case for B also correct.
- R2-2 CLOSED: carry attempt = first time per secure control a field carrier's body centre is inside the attacked 20 m zone; two updates inside = 1 attempt; leave and re-enter during the same control = still 1; a scored carry not seen inside records at the goal. Counter is now independent of goals (bounded run: 3 and 8 attempts, 0 goals).
- R2-3 CLOSED: report, scoring basis, matrix and owner-questions ledger state the definition.
Note (ENGINEERING, not a defect): the attempt definition is Codex's operational proxy (entering the 20 m zone with control), not canon. A fumble recovery inside the zone starts a new control and can count again. Report points per attempt with that definition in view.
Not verified: B0 blob count, replay hashes, any full match (none run). Status: IMPLEMENTED and TESTED; not ACCEPTED.
