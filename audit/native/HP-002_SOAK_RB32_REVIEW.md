# HP-002 independent review: provisional RB-3.2 soak (claude/soak-rb-3-2-r2 @ 2543811, engine claude/rb-3-2-toss-timeout-provisional @ a8bda94)

Reviewer: Claude. Date: 17 Nov 2026. Measurements from a provisional branch; nothing ACCEPTED.

## Verified
- Diff of a8bda94 vs cfacd0b is the 29-line toss-timeout change only (rules.py + test_boundary.py).
- Determinism: seed 3 real roster reproduces trace e0d55c70... / state 6113fb26... (Opus's run and Haiku's run).
- Block A: 10 of 10 real-roster matches finish, 112-144 s each. Totals from the table: 1,841 points; goals from play 178 (9.7%); foul awards 1,663 (90.3%). Target T4 (>= 85% of points from play): FAIL.

## Finding S1 (main cause of the foul and DQ flood): Archer cognition shoots at targets the engine calls illegal
- Engine legality (native/rulebook/archery.py `shoot`): role archer, eligible, live, hunt cleared, target is an opposing field player, eligible, not immune, outside zones, `abs(t.x - own_end) <= 50` (target within 50 m of the SHOOTER's own end), and the target's team has possession and team control.
- Cognition (native/cognition.py `archer_target_legal`) has NO distance-from-own-end condition.
- Evidence (real seed 1, ends alternate each period): 109 of 135 `archery_target` fouls were released with the ball more than 50 m from the shooter's own end; only 4 of 89 legal arrows were. The other parity guess gives 26/135 and 85/89, which cannot be right because legal arrows must satisfy the engine test.
- Chain effect: `archery_target` is a minor, 5 minors = DQ. Every Archer is DQed once per match (20 minor Archer DQs per team over 10 matches, 50 fouls each). Field players then fill the Archer slot (A-4), 706 legal arrow releases come from them, and they too reach exactly 5 archery_target fouls and are DQed. archery_target = 1,125 of about 1,620 fouls; DQs per team per match 2-21 (target < 1).
- Open CANON confirmation: is "Archer may only target players within 50 m of the Archer's own end" canon? It is in the engine as built but not in the cognition predicate comment (Q-FAB1-2 text lists only: opposing field, on offence, team control, outside zones).

## Finding S2: control block stall is the known Q-HELD-1 placeholder, not a regression
- All 10 control seeds: OPENING phase, 0-0, identical hashes. Log: A:0 and B:0 reach the ball at the same instant (simultaneous_contact -> joint_control), the referee releases the hunt after about 1 s, hunt_retake, repeat (about 12,400 cycles; 58 period ends are overtime periods).
- Identical athletes arrive simultaneously every time and the seed has no effect (no per-athlete variation anywhere). Real matches have 4 hunt starts and no joint control. Real play is unaffected; the control as specified cannot run until joint control has a resolution (Q-HELD-1, CANON detail).

## Finding S3: report gaps (engineering)
Carry outcome (tackled/grounded/turnover/stopped short), foul-to-award link, DQ-to-rule link and arrow hit/miss are not recorded.

## Other measured facts
Possessions 310-405 per team (target ~100); possessions ending in an attempt 1.5-5.3% (target ~50%); carry goals 0 in 402 attempts; restart timeouts 45-284 per match (seed 10: 284, legal-arrow rate B 13.8%).
