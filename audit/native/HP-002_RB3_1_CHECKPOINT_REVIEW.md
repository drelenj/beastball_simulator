# HP-002 independent review: RB-3.1 checkpoint (codex/native-rb-3-1 @ cfacd0b)

Reviewer: Claude (cognition lead). Date: 17 Nov 2026. Status of RB-3.1: IMPLEMENTED, partially TESTED, not ACCEPTED.

## Accepted as reported
- Roster ref 81f92e3; 26 franchises yield 2 KPR / 2 ARC / 18 field; Dante Sinella top Archer (99); Kamasi mass 461.8 kg and reach 3.833 m reach the engine.
- Garvian-Ala readiness match completes (82-114, 739 restarts closed). The R3-1 goal-line livelock is fixed for that case but a second restart cycle remains (below).

## Finding R31-1 (blocker): scrimmage "space" throw leaves the field
Code: native/cognition_v3.py `_taker`, the no-target branch (`restart_taker_space_placeholder`).
For a non-toss restart it aims 8 m straight back (`ux, uy = -attack_sign, 0`), clamped only to x >= 1. At a scrimmage 5 m from the team's own end line this aims 1 m from the line. The throw is then released at pass speed (about 53.6 m/s in the reproduction), so it does not stop at the aim point: it crosses the line about 95 ms later, the opponent's toss times out and the same scrimmage repeats.
Contributing: `_stand` puts supporters 8 m behind the ball line. Its fallback (`x + ux*8 + uy*lat`) gives the same x when uy = 0, so supporters are clamped onto the end line. That is why the taker has no believed target.

Required correction (behavioral default, intent-owned):
1. Space aim must be legal and inside the field with a margin: behind or level with the ball line, at least 3 m from every boundary. When the room behind the line is under 6 m, aim lateral along the ball line toward the field centre (y toward 50).
2. A space throw's release speed comes from the aim distance (a catchable ball that lands or is collected short of the aim plus 3 m), not from pass speed. Reject any release whose predicted path crosses a boundary before it lands.
3. Supporters: when the room behind the ball line is under 6 m, stand lateral at the ball line (plus or minus 8 m in y, inside 3-97), not behind it.
4. Watchdog: count restarts, not clock. If the same restart kind repeats at the same spot (within 1 m) 3 times without a change of possession or a completed live play, it is an invariant failure. Report it with the match state; never hang.

## Finding R31-2 (headline for the game, not a code defect): points are mostly foul awards
Five completed seeds: goal points 4-23 per team; foul-award points 58-110 per team (about 80-90% of all points). Possessions 338-387 per team (target ~100). Possessions ending in an attempt 1-6% (target ~50%). Carries 0 goals in 253 attempts. Legal-arrow rate 31-56% (target >= 90%). DQs 14-21 per team per match (target < 1 per match). Restart timeouts 53-131 per match.
Totals near the 80-85 target are therefore not evidence of a correct game. Needed before diagnosis: foul and DQ breakdown by rule, offender role and award value; restart-origin attribution of goals (play vs restart).

## Control block
Recommended (owner to confirm): the all-70 RB/3 mapping (31.29 m/s) governs the control, using the average body from the roster (height 2.39 m, mass 226 kg, reach 3.05 m). The 44.7 m/s RB-2.1 body is retired as a placeholder.
