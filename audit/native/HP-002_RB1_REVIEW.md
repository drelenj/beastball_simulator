# HP-002: independent review of RB-1 (codex/rulebook-1, engine 881d212, report ebce209)
Reviewer: a separate Claude agent that did not write the code (15 Nov 2026). Status: REVIEW COMPLETE. RB-1 is IMPLEMENTED and TESTED by Codex's account; nothing is ACCEPTED.
Verified by running: 282 tests passed (23 subtests) in 175 s; check_replay and reproduce_blocker pass; report hashes match evidence files; accepted files byte-identical to base; budget 17/20 honest; revoked 'marking_pre_live' foul fully removed; no hidden-state channel to athletes. Not verified: Rulebook Draft 1.0 text (F5), per-goal own-goal attribution, full v0/2 replay, natural overtime.
Verdicts: conformance PASS WITH FINDINGS; revoked foul PASS; suspicious numbers FAIL for own goals and band counter; determinism/honesty PASS WITH FINDINGS; information boundary PASS.

## Findings
| # | Sev | Where | Finding | Fix |
| --- | --- | --- | --- | --- |
| F1 | High | scoring.py:32,40; rb_deliberate_team set at :17,24,62 | Own goal is true if holder, last deliberate releaser/toucher, or releaser is the defending team; the field is never cleared on acquire. Reproduced: B passes, A intercepts and carries into B's goal = own goal (2) instead of a carry (5 banded). Reproduced: A shoots, a B defender touches it, goal = own goal. | Derive own goal from ball state at the goal event; reset on acquire and award |
| F2 | Medium | scoring.py:32 | A defender's deflection of a shot into his own goal is counted as an own goal. Canon silent (CANON question) | Owner ruling needed |
| F3 | Medium | authorities.py:94-96, config.py:15 | Full-goal award returns 3 in period 4 and overtime in flat mode; flat canon is goal 2 | Flat returns 2; 3 only in banded; add a flat period-4 test |
| F4 | Medium | native/rules.py:393-394 | Ratified goal-line toss-timeout restart (5 m out) not implemented or tested; reproduced restart at x=0.5 | Implement, test, matrix row |
| F5 | Medium | discipline.py:57; test RD4 | Non-carrier hold routed to the offence branch (count +1) whichever team fouled; defence minors elsewhere are count -1 / half goal at 0 | Route defender holds through the defence branch (ruling below) |
| F6 | Medium | RB1_REPORT counters, scoring.py:44-46 | Band counters count every release (passes, restart throws, dribbles), not shots; seed 6: 573 pass, 442 restart_pass, 26 shot, 20 dribble. Own/carry attempts only increment on a goal, so carry attempts cannot be recorded | Shot-only counter; independent carry-attempt counter; rename table |
| F7 | Medium | matrix notes RT3, RT6, RS6, RA2, RA4, RO6 | Say 'full-match validation reported separately' but all six final seeds ended in regulation; overtime never exercised in a final-source full match | Reword to 'forced scenario only' |
| F8 | Medium | owner briefing | Omits that penalty awards are about 78% of all points (seed 6: 111 half-goal awards vs 17 goals) and that about two thirds of arrows are illegal | Add to briefing |
| F9 | Low | scoring.py, review.py:59-61 | Goal ruling emitted twice | Publish once |
| F10 | Low | review.py:44-46 | Natural review evidence always called==actual, so a natural review can never be won | State plainly in report |
| F11 | Low | authorities.py:79-92 vs review.py:56 | RO1 tests Authorities.review, not the engine's rb_review | Point RO1 at rb_review |
| F12 | Low | config.py | Arrow speed stored as ratio 5.5928 x 44.7; canon is fixed 250 | Store 250 |
| F13 | Low | authorities.py:49-53 | Turnover resets both teams' quota | Document, or reset the other team only |
| F14 | Low | check_replay, reproduce_blocker | Write into tracked evidence files | Default to a temp path |

## The numbers the owner flagged
- Own goals about a quarter to a third of goals: partly F1 (RB-1 bug), partly F2 (unratified interpretation); true share not measurable from stored counts.
- Zero carries: a measurement artifact (F6); athlete behaviour also gives none.
- About 550 'quota resets' per match: correct definition (possession changes); volume inherited from athlete behaviour (273+275 turnovers; 141 toss timeouts and 40 snap timeouts are themselves turnovers).
- Band counters about 1,000 per match: F6, passes and restart throws, not shots (only 3 shots at 20 m or more in seed 6).
- Minors, majors, DQs: inherited athlete behaviour amplified by RB-1. 64 to 101 of the minors are illegal arrows (archery_target); 12 to 23 of 17 to 27 DQs are Archers collecting five illegal-arrow minors. In a probe, 20 of 25 illegal arrows failed only the own-half clause; the Archer does not know the rule. Penalty awards are about 78% of all points, so match scores mostly measure penalties, not play.
