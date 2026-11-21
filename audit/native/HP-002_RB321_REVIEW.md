# HP-002 review: RB-3.21 ball material + Part 2 revert (claude/rb-3-21-ball-material @ eb788ec, code bd1e481)

Reviewer: Claude (lead), 21 Nov 2026. Status: IMPLEMENTED and TESTED; not ACCEPTED.

## Verified from the result files
Real seeds 1/3/5: 57-76, 64-117, 99-95 -> median team score 85.5 (owner range 75-90). Possessions per team 145/144, 150/151, 163/163 -> mean 152.7 (owner range 100-150). Control 1: 55-79, 144 per team.
Material: drag k 0.0005/m quadratic, bounce h 0.44, restitution 0.60, roll decel 3.0 m/s^2 (owner CANON 21 Nov: fictional ball material). Pass out of bounds 20.2% -> 5.3% of possession ends; interceptions/loose 15.1% -> 24.8%.

## Lead decisions on QUESTIONS_FOR_CLAUDE (BEHAVIORAL)
1. Next lever for possessions: none yet - run the 13-match soak first; at ~153 the four-match mean is within sampling noise of the 150 limit.
2. T-B1/T-B2 bands: keep as is (targets met; no evidence a more central material plays better).
3. "Gentlest change" selection metric: accepted.
4. Frozen b1 Keeper code still using the old ball when called directly: accepted (b1 is frozen; Native paths use the material).
