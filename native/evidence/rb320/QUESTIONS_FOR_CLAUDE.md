# RB-3.20 BEHAVIORAL questions for Claude (lead). No CANON questions.
1. Part 2 made the targets worse on this sample: real median 88.0 -> 68.5, possessions 166.7 -> 178.5, pass-out-of-bounds
   20.2% -> 25.9% of possessions. The A4 horizon 0.5 s lets more corner passes through (passes 795 -> 954 real) and B1 handoffs
   fell 297 -> 67 per match. Keep, revert one of the two, or measure more seeds?
2. B1 kept the RB-3.19 rule "never hand off backward unless pressured" alongside the new relief/faster clause (the new spec
   did not revoke it). Correct?
3. The ball travel distance is now flight-dominated (missed passes still exit ~53-55 m from release). The calibration
   proposals in PHYSICS.md (quadratic drag) would shorten it; they need an owner/lead decision (engine calibration is not a defect).
4. predict_path was fixed the same way as the step (it is documented as using "the same rules as the match"); c4c_path (5 ms)
   was left (error .05 m/s). Agree?
