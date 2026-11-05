# Restarts v1 (Pocket 4.0 prototype)

Module `restarts_v1.py`, system `restarts` (on by default). Individual off-flags: `rs_no_hunt`, `rs_no_scrim`, `rs_no_snap40`, `rs_no_toss` (pass in `off=(...)`; `--off restarts` turns all four off and gives the old Pocket 2.0 restarts).
All numbers are working values from the rules discussion, not canon. They live in `restarts_v1.SET`.

## What each restart does here
| | First Hunt | Scrimmage restart (first tackle) | 40 m Scrimmage Snap (after a score) | Toss-in |
|---|---|---|---|---|
| Trigger | start of every quarter (old engine only hunted in Q1; Q2-4 were a free pass) | first legal tackle outside the attacked Keeper Zone | any goal | ball fully crosses a boundary |
| Ball | centre, stationary | tackle spot (pushed out of a Keeper Zone only) | centre of the conceding team's own 40 m line | crossing point on the line (slid to the edge of a Keeper Zone on the goal line) |
| Who | one field player per team, 1.5 m from the ball; picked per quarter, rotating among the top three by role (Hunter/Tracker first) | tackled player snaps; tackler "nose" (1.2 m across the LOS) if mass >= 205 kg else upright 5 m back | a Sentinel/Pathfinder/Hunter-type field player snaps | thrower is a field player, feet outside the line |
| Others | support players start in their own half outside the circle (placed before the whistle) | free behind their own side of the LOS; they physically run there | everyone at or behind their own 40 m line (20 m corridor), moving there in the dead interval | opponents >= 3 m away |
| Live when | the ball's whole body leaves the 10 m circle, however it leaves | snap (pass to another player) | snap (pass to another player) | released ball enters the field |
| Counts | possession clock and tackle count start at activation; quarter clock starts at activation | tackle count carries (1), clock carries | tackle count 0, fresh 45 s | possession to the other team, fresh |
| Limits | 6 s, then repeat (2 failures: old fallback free pass) | ready 2 s after the tackle at the earliest, 6 s at the latest | ready 3 s at the earliest, 12 s at the latest | ready 1.5 s, throw within 4 s of ready |
| Offside | - | offence: tackle count +1 (2 = turnover); defence: count reset to 0; a second defensive offside = warning, third = minor | either side: retake; defence repeat = warning/minor; offence twice = turnover | existing encroachment rule (retake + warning) |

Already enforced by the engine and kept: the thrower cannot recover his own toss; a toss cannot score directly (a released ball is not scoring until another player controls it); archers cannot fire in a dead ball. **Hunt rule (added): Archers cannot draw or fire until the ball has left the centre circle** (blocked at the decision and at the shot; nothing drawn, no ammunition spent, no foul).

## How the Hunt is decided
Both contestants start inside reach, so the outcome comes from reaction: each may not touch the ball until his own decision speed (+ seeded 30 ms jitter) has passed; a simultaneous touch goes to the faster reaction instead of failing. Mirrored teams split first possession 38-37 over 80 Hunts (equal athletes, no side bias); with the Ala-Xenar rosters the faster contestant wins most.

## Measured (short games and 2 regulation games, Ala vs Xenar, tendencies on)
- Per regulation game: about 160-175 scrimmage restarts, 80-90 toss-ins, 35-39 snaps, 4 Hunts.
- Dead time to the snap/toss: scrimmage 2.3-6 s (mostly 2.3-3), toss 1.8-3.2 s, snap 3.7-4.1 s.
- Hunt: median 1.4 s to go live, p95 about 4 s, about 10% repeat after the 6 s limit; every live Hunt so far ended in a carry out of the circle.
- Fouls fell from 23-32 to 6-8 per game (the recovery-disc fouls no longer exist).
- Scoring is lower: 110 and 97 total points in the two regulation games vs about 145-165 before. Not calibrated: the set-piece structure gives defenders time to set, and the snap/scrimmage dead time is not yet tuned.
- Offside never occurred in normal play because the AI waits for legal positions; the offside paths were exercised by shortening the waits (a defensive offside reset the count, as specified).

## Not built yet
- Hunt strategies (Power / Precision / Disruption) as separate controller policies; no tap, deflect or loose-ball exits happen, only carries. Hunt violations (false start, early entry) and the delay penalty.
- Contestant choice by tactics beyond role order; opening deployments (central surge, wide spread...).
- Attacker offside at the scrimmage was only tested through the shared code path, not forced.
- Penalty for failing to snap in time (the old 5 s fault still stands for tosses, now 4 s), game-clock treatment of the dead interval beyond "quarter clock stops".
