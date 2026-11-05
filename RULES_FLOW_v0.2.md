# Beastball game flow: working rules v0.2 (1 Nov 2026)
Tags: [C] canon, stated by DreLen. [R] my reading of a [C] statement, to confirm. [P] provisional default I will use until told otherwise. [E] what the engine does today.
Sources: "Complete Flow of a Game" (31 Oct consolidation) + DreLen's answers of 1 Nov + the off-ball contact spec (OFFBALL_CONTACT_SPEC_v0.1.md).

## Keeper Zone [C]
- Attackers: 5 s of residence, expiry is a turnover (unchanged) [E kept].
- Keepers may stay in the zone indefinitely under all circumstances.
- Defenders may stay indefinitely while within **5 m** of an offensive player [C]. The engine's marking distance is 3 m (setting `marking_distance`), so this is a change.

## Tackle count and the Contact Scrimmage [C]
- First legal grounding tackle: offence keeps the ball. **Contact Scrimmage replaces the live recovery** (1 m disc, 3 s). The line of scrimmage is the spot of the tackle, also inside the Keeper Zone (the 8 m goal-line inbound and the "no goal until an attacker outside the zone touches it" aperture are dropped).
- The tackled carrier is the snapper. Tackler may align opposite him or 5 m behind (flow document).
- Snap window: **10 s after the referee sets the ball** [C]. The possession clock runs during the window only if more than 0:10 remained at the time of the tackle [R: otherwise it is held].
- Offside is judged against the scrimmage line, defined by the ball [C]. Offence offside: tackle count +1. Defence offside: tackle count -1. The count never goes below 0 [C].
- Second legal grounding tackle: turnover. The other team restarts with a scrimmage at the tackle spot or at its own 40 m line, whichever is closer to the goal it attacks [C] (so a team never restarts behind its own 40).
- Possession clock 45 s, fresh 45 s with zero tackles after a score (40 m scrimmage) or a turnover [flow document].

## Minor fouls [C]
- A minor foul by the **offence**: tackle count +1 (a second one at count 1 is a turnover).
- A minor foul by the **defence**: tackle count -1 (floor 0). If the count is already 0: the offence is awarded **half a goal in Q1-Q3 and a full goal in Q4 and overtime**, and keeps possession [C]. This is the whole of the "back-to-back" rule.
- Offside is treated as a minor foul [R].

## Major fouls and discipline [C]
- Majors: **intentional head contact**; **intentional tripping of an off-ball player**.
- First major: 120 s of game time, forces a substitution. Second major: disqualification.
- Minors: the **fourth** minor is a 60 s game-time exclusion; the **fifth** is disqualification.
- Counts per player [R, to confirm].

## Archers [C]
- Loaded arrows are dropped. **25 arrows per possession, up to five freezes per possession.** Freeze 5 s, post-freeze immunity 10 s, recovery protection 3 m / 2 s (flow document). Keeper Zone occupants are not legal targets.

## First Hunt [C]
- Replaces the engine's current opening procedure (not checked what the engine does). Each team picks **any** field player as its contestant. Begins the match and each quarter.

## Scoring for the self-play experiment [C]
- Flat: **any goal from any area is 2 points; a half goal is 1 point.** Goals may be thrown, kicked or carried in. A goal carried in is tracked as a **Carry**. For every other goal the release distance is tracked, with success rates. (The flow document's 5/4/3/2 hierarchy is not used in the experiment.)
- Track per team: goals, distance progressed, turnovers, minor and major fouls, half-goal awards.
- Exploits are flagged, not patched; suggested changes come later.

## Contact [C] (see the off-ball spec)
- Off-ball contact legal below the neck and above the hip (shoulders, arms), hip jockeying legal, push and stab legal, no pulling or gripping. Applies to both sides; violations are minor fouls; knockdowns allowed if the physics allow.
- Defender may wrap and grip the carrier from below the neck down.
- Targeting accuracy: Motor Control with Focus.

## What this changes in the engine (not yet implemented)
1. Contact Scrimmage after a tackle (new phase, snap clock, tackler alignment, offside line), replacing the live recovery and the zone inbound.
2. Turnover restart by scrimmage (spot or own 40, whichever is closer to the goal attacked).
3. Tackle count rules for minor fouls and offside; half-goal award by quarter.
4. Marking distance 3 m -> 5 m; Keeper stays indefinitely.
5. Foul ladder: majors (intentional head contact, intentional trip off-ball), minors (4th = 60 s, 5th = DQ), warnings dropped [R].
6. Archers: 25 arrows and five freezes per possession.
7. First Hunt opening. 8. Flat scoring in the experiment (a drill-level scorer; the engine's scoring is untouched).

## Open items
- Does the offside rule really count as a minor foul (so a defensive offside at count 0 is a half goal)?
- Counts of minors and majors per player or per team?
- Major foul: 120 s with the team playing a player short, or a forced substitution with no numbers disadvantage?
- Snap window: the possession-clock reading above, and the consequence of missing the 10 s.
- After a half-goal award: restart procedure (scrimmage at the foul spot with count 0?).
- Is knee and joint contact on the carrier now legal? Unintentional head contact: a minor?
- How is "intentional" defined for a simulated athlete? (proposal: a contact the athlete's own decision chose, as against an incidental collision.)
- Tackle inside the goal radius (6 m): where is the scrimmage line?
