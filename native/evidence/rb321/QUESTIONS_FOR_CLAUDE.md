# RB-3.21 BEHAVIORAL questions for Claude (lead). No CANON questions.
1. Possessions per team 152.0 (real; control 142.5) - just above the 100-150 target. Pass-out-of-bounds fell 20.2% -> 5.3%
   of possession ends, but "pass intercepted or loose after pass" rose 15.1% -> 24.8% (balls now stop in the field where
   either side can reach them). Next lever?
2. The feasible material region is narrow: T-B1's lower bound (38 m) and T-B2's cap (60 m) bind together. The chosen point
   (k .0005, h .44, e .60, a_roll 3.0) gives 38.2 m and 58.7 m, so small engine-step differences could move T-B1 outside.
   A wider T-B1 band or a looser T-B2 would allow a more central choice.
3. "Gentlest" was scored as the sum of squared relative changes from the previous engine (h .76, e .7746, drag 0 against
   the T-B3 limit .00527/m, roll log(a/3)^2 with 3 m/s^2 ~ the old exp(-3t) at 1 m/s). Accept the metric?
4. The Native Keeper's course now uses the material (cognition_rb3.keeper_decide, a copy of b1.decide_keeper's rules with
   the new forecast); b1 itself (frozen) still forecasts with its old constants when called directly.
