# Beastball game flow: working rules v0.3 (1 Nov 2026)
Tags: [C] canon, stated by DreLen. [R] my reading of a [C] statement, to confirm. [P] provisional default. [E] what the engine does today.
Sources: "Complete Flow of a Game" (31 Oct consolidation) + DreLen's answers of 1 Nov + the off-ball contact spec (OFFBALL_CONTACT_SPEC_v0.1.md). Supersedes RULES_FLOW_v0.2.md.

## Keeper Zone [C]
- Attackers: 5 s of residence; expiry is a turnover [E kept].
- Keepers may stay in the zone indefinitely under all circumstances.
- Defenders may stay indefinitely while within **5 m** of an offensive player. (Engine `marking_distance` is 3 m: change.)

## Tackle count and the Contact Scrimmage [C]
- First legal grounding tackle: the offence keeps the ball. A **Contact Scrimmage** replaces the live recovery (1 m disc, 3 s). The line of scrimmage is the spot of the tackle, also inside the Keeper Zone (the 8 m goal-line inbound and the "no goal until an attacker outside the zone touches it" aperture are dropped).
- The tackled carrier is the snapper. The tackler may align opposite him or 5 m behind (flow document).
- **Snap window: 10 s after the referee sets the ball.** The possession clock runs during the window only if more than 0:10 remained at the time of the tackle [R: otherwise held].
- **Missing the snap window: tackle count +1 and the spot moves 5 m back** [C]. (At count 1 that is a second tackle, a turnover [R].)
- Offside is judged against the scrimmage line, defined by the ball. **Offside moves the spot of the ball 5 m closer to the goal being attacked** [C; I read it as the defence's offside]. Tackle count: offence offside +1, defence offside -1; the count never goes below 0 [flow document + C]. Offence offside also moves the spot 5 m back [R, same as missing the snap window].
- **Offside is not a minor foul** [R]: it is its own procedural penalty, so a defensive offside at count 0 does NOT give a half goal.
- Second legal grounding tackle: turnover. The other team restarts with a scrimmage at the tackle spot or at its own 40 m line, whichever is closer to the goal it attacks (so a team never restarts behind its own 40).
- Possession clock 45 s; fresh 45 s with zero tackles after a score (40 m scrimmage) or a turnover.

## Minor fouls [C]
- By the **offence**: tackle count +1 (a minor at count 1 is a turnover [R]).
- By the **defence**: tackle count -1 (floor 0). If the count is already 0: the offence is awarded **half a goal in Q1-Q3 and a full goal in Q4 and overtime**, and keeps possession. This is the whole of the "back-to-back" rule.
- After an award: the offence restarts with a scrimmage at the spot of the ball or of the foul, whichever is closer to the goal it attacks [C]; tackle count stays 0 [R].
- Unintentional head contact is a minor foul [C]. Knee and joint contact on the carrier is now legal [C].

## Major fouls and discipline [C]
- Majors: **intentional head contact**; **intentional tripping of an off-ball player**. "Intentional" = a contact the athlete's own decision chose, as against an incidental collision [C].
- First major: 120 s of game time, forces a substitution. Second major: disqualification.
- Minors: the **fourth** minor is a 60 s game-time exclusion; the **fifth** is disqualification.
- Counts are **per player** [C].
- **Teams always have their 12 players in the game**: every exclusion or disqualification is covered by a substitute. A team forfeits only if fewer than 12 of its 22 gameday players are available (11 ruled out by injury or disqualification) [C]. An excluded player is not eligible to play for the exclusion time [R]; may return afterwards [R].

## Archers [C]
- Loaded arrows dropped. **25 arrows per possession, up to five freezes per possession.** Freeze 5 s, post-freeze immunity 10 s, recovery protection 3 m / 2 s (flow document). Keeper Zone occupants are not legal targets.

## First Hunt [C]
- Replaces the engine's current opening procedure (not checked what the engine does). Each team picks any field player as its contestant. Begins the match and each quarter.

## Scoring for the self-play experiment [C]
- Flat: **any goal from any area is 2 points; a half goal is 1 point.** A ball may be thrown, kicked or carried into the goal. A goal carried in is tracked as a **Carry**. For every other goal the release distance is tracked, with success rates. (The flow document's 5/4/3/2 hierarchy is not used in the experiment.)
- Track per team: goals, distance progressed, turnovers, minor and major fouls, half-goal awards.
- Exploits are flagged, not patched; suggested changes come later.

## Contact [C] (see the off-ball spec)
- Off-ball contact legal below the neck and above the hip (shoulders, arms), hip jockeying legal, push and stab legal, no pulling or gripping. Applies to both sides; violations are minor fouls; knockdowns allowed if the physics allow.
- Defender may wrap and grip the carrier from below the neck down.
- Targeting accuracy: Motor Control with Focus.

## What this changes in the engine (not yet implemented)
1. Contact Scrimmage after a tackle (new phase, snap clock, tackler alignment, offside line, 5 m penalties), replacing the live recovery and the zone inbound.
2. Turnover restart by scrimmage (spot or own 40 m, whichever is closer to the goal attacked).
3. Tackle count rules for minor fouls, delay of game and offside; half-goal award by quarter; scrimmage restart after an award.
4. Marking distance 3 m -> 5 m.
5. Foul ladder: majors (intentional head contact, intentional off-ball trip), minors (4th = 60 s, 5th = DQ), per player; warnings dropped [R]; exclusions always covered by a substitute (the engine currently plays a player short); forfeit below 12 available players.
6. Archers: 25 arrows and five freezes per possession.
7. First Hunt opening. 8. Flat scoring in the experiment (a drill-level scorer; the engine's scoring is untouched).
9. Off-ball contact legality (legal band, no gripping, intent defined by the athlete's own decision).

## Open items
- None open. Confirmed by DreLen 1 Nov: offence offside = count +1 and spot 5 m back [C]; possession clock runs in the snap window only if more than 0:10 remained at the tackle [C]; excluded player may return as a substitute after his time [C].
- Goal plane is at 0 m; the "6 m" refers to the physical net width, not a radius [C]. A first tackle within 10 m of the goal plane resets the scrimmage line to 10 m [C]. Confirmed 1 Nov: the 10 m is just the x measurement (distance from the goal plane along the field, any lateral position), and it applies to first tackles only; turnover restarts stay at the spot or own 40 m [C].

## Amendment 3 Nov: no kicking [C, DreLen]
- Kicking is removed from the game: the ball is thrown or carried.  All rules about kicking fall away (kick releases, kick-based shots, the kicking attribute in play).  Same game ball.
- The foot-play rule's logic (one sequence of contacts with the ball, then no more until a reset) moves to throwing, where it governs a **dribble**: a player throws the ball ahead of himself and plays it again.  A player may **dribble once while in possession of the ball**.  [R: a second self-throw-and-replay in the same possession spell is a foul, like the old second ground kick; the spell ends when another player touches the ball, a dead ball or a play reset; to confirm.]
- Engine (RULES_V03=1, RV03_NOKICK=1): kick releases become throws; shots use the passing skill instead of kicking.  No controller dribbles yet: the dribble is a rule without a decision, as the kick and dribble decisions were never wired in the prototype.
