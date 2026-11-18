# HP-002 independent review: RB-3.5 zone diagnosis (claude/rb-3-5-zone-diagnosis @ 60e127f)

Reviewer: Claude. 18 Nov 2026. Provisional measurements; nothing ACCEPTED. Recomputed from the raw diagnosis events (real seeds 1 and 3, control seed 1; 150 zone_unmarked fouls); Opus's table reproduced.

## Verified
- Fouler's distance to his own goal centre (zone radius 20 m): quartiles 12.3 / 16.9 / 18.8 m; 47% are 17 m or more from the goal centre, i.e. within 3 m of the arc; 15% under 10 m.
- Ball distance to the fouler's zone centre: quartiles 37.5 / 54.2 / 74.5 m; only 15% under 30 m. Ball status at the call: 76 pass in flight, 73 carried, 1 loose.
- Nearest off-ball attacker, distance to the zone centre: quartiles 23.3 / 33.8 / 46.9 m; only 5% inside the zone, 44% under 30 m.
- Time in zone at the foul: quartiles 5.04 / 5.08 / 10.05 s, max 30.1 s; 31% were in the zone 8 s or more. Half of all fouls fall at 5.04-5.08 s, so the 3 s exit rule (native/cognition.py about line 555) is not firing before the 5 s deadline for at least half of them.
- Time since the fouler's last exit: quartiles 8.0 / 11.8 / 18.3 s (148 of 150 had left before); he comes back within seconds to a dozen seconds.
- Alone in the zone: 89 of 150 (the fouler himself is the only teammate counted).

## Finding R35-1: this is positioning, not the rule
Defenders idle near the arc of a 20 m zone while the play is 40-75 m away, with no attacker within marking range. The rule (5 s unmarked, 5 m marked) is working as ruled.

## Finding R35-2: the exit placeholder is not working as written
Before changing positioning, find why the 3 s exit does not fire (RB/3 routes to cognition_v3; the exit may sit only on the v0/2 cognition path, or zone_elapsed_ms may not match the engine's clock).

## Notes
- Rule restriction to the defended zone cut seed 1 from 82 to 50 zone_unmarked; seed 3 stayed at 57-58.
- Removing the freeze range limit also removed the engine's 10 m minimum (Q-RB35-3); consistent with "legal anywhere".
- zone_residence: 10 calls, all attackers just inside the arc of the attacked zone, close to the ball.
