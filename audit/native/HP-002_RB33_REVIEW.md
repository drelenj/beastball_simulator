# HP-002 independent review: RB-3.3 provisional (claude/rb-3-3-archer-flip @ f28e68a, base a8bda94)

Reviewer: Claude. 17-18 Nov 2026. Provisional measurements; nothing ACCEPTED.

## Verified
- Six matches finish (real seeds 1, 3, 10; control seeds 1-3); control block no longer stalls (coin flip removes the tied opening Hunt).
- 50 m Archer condition removed from native/rulebook/archery.py only; v0/2 and v0/3 3,000-step hashes identical to base (Opus).
- Foul-award origins are only archery_target and zone_unmarked; DQ offences are frozen_contact (15-20/match), archery_target (9-17), zone_unmarked (1-6).

## Finding R33-1: the report's cause for illegal arrows is incomplete
Raw logs (real seeds 1/3/10, archery_target fouls 54/48/55): ball in flight at release 0/3/2; ball dead 23/19/21 (released 100-300 ms after the ball went dead); ball loose 20/14/15 (0-500 ms after it became loose); ball carried 11/12/17 (illegality reason not logged). About 70% are release-latency: the Archer committed while legal, the world changed before release. Q-FAB1-2 (team control in flight) explains at most 5%.

## Finding R33-2: frozen_contact is the largest DQ source and is mostly reaction lag
frozen_contact fouls are major (DQ): 44-55 per match. Time from the victim's freeze to the contact: median 0.75-0.86 s, quartiles 0.4-0.5 s and 1.2-1.4 s, max about 5 s. Contact is spread over the first 1.5 s, not over the 5 s freeze, so defenders are mostly late to react, not ignoring frozen players.

## Finding R33-3: DQ depletion drives the restart timeouts
Up to 21 DQs per team (of 22 on the roster); restart timeouts per period rise from tens to hundreds once a team passes about 20 DQs (seed 1: 13, 22, 184, 376 by period). Possessions 355-568 per team come from this, so every other metric is distorted until DQs are under control.
