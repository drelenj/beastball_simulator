# HP-002 review: RB-3.19 ball in play + tactics (claude/rb-3-19-ball-in-play @ 1132507, code be0d1dd)

Reviewer: Claude (lead), 21 Nov 2026. Status: IMPLEMENTED and TESTED; not ACCEPTED.

## Verified
- Full suite rerun by Claude (Sonnet had not repeated it after its last fix): pytest -q b1 native -> 628 passed, 23 subtests.
- Real-roster team scores from the result files: s1 (A1) median 68.5; s2 (A1-A4) 75.5; s3 (A1-A4 + Part B flags ON) 85.5 (scores 70-90, 78-81, 113-100). Possessions per team (real mean): 186.7 / 167.7 / 166.3. Sonnet's medians include the control match.
- s3 possession ends (real seeds 1, 3, 5; 166 per team; median 5.96 s): pass out of bounds 23.2%, goal 14.2%, pass intercepted 13.4%, other out 9.6%, carrier frozen 8.2%, restart throw intercepted 8.1%, second tackle 6.6%, restart throw out 1.6% (was 10.9%).

## Lead decisions on QUESTIONS_FOR_CLAUDE (BEHAVIORAL)
1. A4 too broad: shorten the horizon from 1.0 s to 0.5 s beyond the receiver.
2. A3 cannot catch balls that outrun everyone: engine question for Codex - how much speed the ball keeps after ground contact (bounce, roll, friction). Missed 43 m/s passes still travel ~55 m.
3. Toss space-throw placeholder change (8 m toward field centre at 20 m/s): accepted.
4. Handoffs (~304 per match): a handoff must also improve pressure - the receiver's least time-to-contact must exceed the carrier's by at least 0.5 s, or the receiver must be >= 2 m/s faster toward the attacked goal; no immediate handoff back to the giver within 2 s.
