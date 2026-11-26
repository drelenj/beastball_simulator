# HP-002: RB-3.35 review (Claude, 26 Nov 2026)

Reviewed `codex/rb-3-35-turnovers` @ 07cf88fe623f1ac63bfdf96068ce3303986c5f3b (Garvian-Ala 1-5 per arm).
Independent rerun: B4 seed 1 57-112, trace f424c4ee...e9c9, state 1d701334...8d82, digest a3b387b7...dbe1. Matches.
Status: IMPLEMENTED, TESTED (5 games per arm).

## Keep
- B1 projected beliefs: interceptions -6.3 +/- 1.4 (B4 vs A6 -9.0 +/- 2.2), median aim error 2.72 -> 1.75 m, completion
  +5.1 pp (B4 vs A6).
- B4 takedown gate: non-carrier share 30.6% -> 21.2%, success 10.7% -> 14.2%. All gated commands came from the
  "other" fallback path; the defender baseline issued none (RB-3.34 hypothesis about the baseline was wrong).

## Defect: B2 carrier_boundary suppresses carry goals
`native/turnovers.py boundary_risk` exempts an end-line crossing only if the CURRENT y, the aim y and the stop y are
all inside the goal section at hand height (3 m half-disc). At carry speed the stop point is beyond the end line, so
any angled approach to the mouth is valued as a lost possession. Points from carries 13.3 -> 7.7 at B2 (-5.6 +/- 1.8);
B4 vs A6 -9.1 +/- 2.4. Fix: judge the y where the planned path crosses the end-line plane.

## Not working: Keeper plant
65 plant choices, 0 active at shot release: the wind-up cue arrives after perception latency, too late. Behaviour
alone cannot plant in time; remaining levers are Keeper-only constants (owner).

## Lead error corrected
The A6 soak's 10.3 "held_ball" crossings per team per game were END-line crossings (8.4 of them more than 15 m wide of
the goal centre), not sideline; sideline held-ball crossings were 0.02. The 26 Nov sideline ruling stands but
addresses almost none of them. RB-3.35: held-ball end-line crossings 11.7 -> 7.5.

## Structural: possessions vs the two-tackle set
A6 soak: possessions ending on the second tackle last 15.9 s on average vs 11.1 s overall. Even if every possession
ran to the second tackle, about 112 per team (rough estimate). The 80-110 range needs longer sets or longer phases.
B4: possessions 149.4, first-tackle share 27.9% -> 34.9%, points 77.3 (inside 75-90), carry share down (defect above).
