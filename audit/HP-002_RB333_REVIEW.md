# HP-002: RB-3.33 build review (Claude, 25 Nov 2026)

Reviewed `codex/rb-3-33-ladder` @ bbd5335ef5233905ff085ea6d5dc09a45fe27d95 (one game per arm, Garvian-Ala seed 1).

## Independent reruns (CPython 3.13, this sandbox)
- RB332 arm: 99-74, trace 0045e62d...2601, state b2b68575...d9de, digest 374ab384...434d. Gate h matches.
- A5 arm: 45-47, trace fd752565...c194, state 1a3a61bd...a4a8, digest 6cc2cb42...47e2. Matches the report.

## Status
IMPLEMENTED and TESTED (smoke level). Not judged: one game per arm. Not ready for the soak: A5 carries a valuation defect.

## Finding 1 (blocking): A5 values every near-goal continuation as a sure 7-point carry
`native/prism_core.py` carrier(), branch `if routes:` with `carry_seven`: shots get
`release_points(d) x sigmoid((u-3)/2)` (2-4 x sigmoid) while EVERY non-shot option (pass, carry diversion, evade,
retain) gets `7 x sigmoid((u-3)/2)`. A pass near the goal is therefore worth up to 7 and a shot at most 4, so shots
lose. Evidence: near-goal shots 62 -> 21 (A4 -> A5), throw-3 points 55.5 -> 9 per team, 2-point throws to 0,
attempt share 29.8% -> 26.3%, points per team 100 -> 46. Cause: the lead's spec ("all valuations read the scoring
table; remove the 1.55 cap and the shot heuristic") did not say that a continuation is not a carry. Lead's error.
Fix: carry = 7 changes only carry-derived values (x 7/5): route options 7 x P(route), continuation 1.55 x 7/5 = 2.17
x sigmoid, stretch 3.75 x 7/5 = 5.25; shots keep the RB-3.32 expected-value form with bands from the rulebook.

## Finding 2: Keeper settle does not settle
Unset incidence (Keeper above keeper_set_mps at shot release) rose from 26% (A0) to 34% (A2) and 41-48% (A3+). The
settle target follows the ball on the ball-to-goal line; with 31.3 m/s carriers (speed = 44.704 x rating) the
target moves several m/s, so the Keeper must move faster than 1.5 m/s to follow it. keeper_set_mps (1.5) is a
human-scale constant in a league whose athletes are ~3x human speed. Needs diagnosis before a change. Any change to a
Keeper-only constant goes to the owner (canon: no Keeper-only boost).

## Finding 3: faster cadence raised phantom commitments
Non-carrier share 21% (A2) -> 31% (A3) -> 29% (A5) -> 35% (A5'). Aborts work (about 240 per team per game) but do
not prevent new commitments on non-carriers. Diagnose with samples before fixing.

## Other notes
- CPU: A3 (sense 100 ms) costs 1.54x A0; A5 227 s, A5' 270 s per game. Within the 2.5x guard. A 210-game soak at
  A5 is about 13 CPU-hours.
- Pass speed rule: 50-65 m/s releases +66.5 per team at A4; drops 3.5 -> 7.5 per team; lateral miss did not grow.
  "2 x typical run speed" is 62.6 m/s because typical top speed is 31.3 m/s.
- Carry goals were 0-0.5 per team in every arm, including RB332, on this seed.
- Cadence: accept the builder's choice of 300 ms (A5' costs 19% more CPU; the gameplay difference is not separable on one game).
