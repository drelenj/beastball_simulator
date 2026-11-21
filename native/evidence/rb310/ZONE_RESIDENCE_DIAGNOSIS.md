# Why zone_residence calls and foul-award points rose in RB-3.9 (diagnosis only; no code change)

Data: a read-only re-run of the RB-3.9 stage-3 matches (code 6a328bf; real seeds 1, 3, 5 and control seed 1) by `tools/zr_observe.py`. Each re-run reproduced the stored stage-3 trace and state hashes. Records per call: `zr_diag/zr-*.json`.

## The calls
There were 41 zone_residence calls (14 / 9 / 9 / 9). Distributions below are min / q1 / median / q3 / max.

| Measure | Value |
|---|---|
| Offender | off-ball attacker 37, carrier 4 |
| Distance from the centre of the goal he attacks | 6.0 / 9.9 / 12.2 / 15.5 / 19.6 m |
| Distance to the ball | 1.3 / 10.9 / 21.4 / 31.8 / 86.2 m |
| Nearest teammate | 1.9 / 5.7 / 9.3 / 13.1 / 19.8 m |
| Nearest defender | 0.9 / 2.6 / 4.4 / 6.5 / 11.8 m (the marking exemption applies to defenders only) |
| Live time in the zone | 5.00 / 5.03 / 5.05 / 5.09 / 9.44 s |
| Previous formation was his team's | 26 of 41 (first tackle 21, ZR-T 5, second tackle 4, turnover 3, other 8) |
| That formation placed him inside the zone he attacks | 17 of 41 |
| Live time since that formation | 5.0 / 5.07 / 9.1 / 12.7 / 33.9 s |
| Award given | turnover scrimmage to the other team, 0 points, in all 41 |

## What raised it
- **Counts by stage, four matches:**

  | RB-3.8 | Stage 1 (formation) | Stage 2 (passes) | Stage 3 (4 s exit + carrier) |
  |---|---|---|---|
  | 20 | 44 | 44 | 41 |

  The rise comes with the formation (stage 1). The 4 s exit and the carrier change (stage 3) did not raise it.
- **Mechanism.** At a scrimmage within about 20 m of the goal attacked, the formation puts the offence 1 m behind the ball line, which is inside the zone they attack. The 5 s live residence clock starts at the snap.
  - 17 of 41 calls were players placed there; the quartile of 5.07 s since the formation means the call came 5 s after the snap.
  - The exit placeholder (4 s since stage 3, 3 s before it) cannot get a player deep in the zone out in time.
  - The rest are attackers who later drift into the zone without the ball.
- **Foul-award points come only from defensive fouls at tackle count 0; zone_residence itself awards no points.** By originating foul, summed over the four matches:

  | Stage | archery_target | zone_unmarked | Total |
  |---|---|---|---|
  | RB-3.8 | 24 | 5 | 29 |
  | Stage 1 | 31 | 17 | 48 |
  | Stage 2 | 30 | 12 | 42 |
  | Stage 3 | 34 | 21 | 55 |

  The zone_unmarked rise also starts with the formation. The defence is placed 0.5 m beyond the neutral zone, which near its own goal is inside its own zone, often unmarked.

## Recommended fixes (DESIGN COMPLETE; not implemented)
| ID | Class | Fix | Evidence | Risk |
|---|---|---|---|---|
| Z-1 | CANON | Decide how residence works around a scrimmage near a goal. Options: the 5 s clocks of players the formation placed inside a zone start only when the snap hold ends; or such players get the full 5 s from the trigger; or the formation never places a player inside a Keeper Zone except as rules require | 17 of 41 zone_residence calls and the zone_unmarked rise follow formation placement | Changes the rule; affects goal-line play |
| Z-2 | BEHAVIORAL | The zone exit is chosen by the time an athlete needs to get out (distance to the arc ÷ speed), not a fixed 3 s / 4 s, for attackers and unmarked defenders | Calls at 5.0-5.1 s with offenders a median 12 m from the goal centre, about 8 m from the arc | More early exits; may thin goal-line attacks |
| Z-3 | BEHAVIORAL | Off-ball attackers not involved in the play stay out of the zone they attack (they drift in later) | 37 of 41 offenders are off-ball, a median 21 m from the ball | Fewer bodies near goal for passes |
