# HP-002: RB-3.38 review (Claude, 27 Nov 2026)

Reviewed `codex/rb-3-38-archer` @ f64b9ab4836885ba6936aaaa3d57d61e37a7eebd (8 games per arm).
Independent rerun: R3 seed 1 64-123, trace ec8cfaf2...0c09, state 2eada874...d909, digest dbbc7a4f...8126. Matches.
Status: IMPLEMENTED, TESTED.

- Archer budgets (per team per game): R0 296 arrows / 96 freezes / 21.3 carrier-freeze fumbles / 140.6 possessions;
  R2 match budget 17 / 4.8 / 2.5 / 119.9 (freezes exhausted in period 1 by 14 of 16 teams); R3 period budget
  39 / 9.3 / 4.5 / 125.8, points 87.2. The cycle alone cut freezes 96 -> 60 but not possessions.
- Carrier body-outs: "steering overshoot with aim inside" is 13.9 of 19.2 (R0). The 20 sampled histories show the
  same mechanism: the carrier is moving toward a line (outward velocity component +0.5 to +1.0 of speed), his
  locomotion target sits only about 2 m inside the line (keep_in margin) and 90-180 degrees behind his heading, and
  the controller turns the short way or decelerates too slowly, sweeping him across the line; speed often rises
  again during the turn. Locomotion has no edge control: the stop/turn distance (v^2 / 2 x braking, turning
  radius v^2 / turning) is not compared with the distance to the line.
