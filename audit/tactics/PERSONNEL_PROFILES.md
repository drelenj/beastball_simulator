# TACTICS-0: personnel profiles (amended D2)
Claude (Fable), 2026-11-15. Status: **DESIGN COMPLETE**. Not IMPLEMENTED, not TESTED, not ACCEPTED. Generated from `audit/tactics/tools/tactics_src.py` by `build.py`.

## OWNER BRIEFING
1. **Accomplished.** For each of the eight styles, every slot now states the rating bands it needs, how candidates are ranked, and what happens when a weaker player fills it: a graceful degrade or a failure. A general rule assigns any supplied roster to any style by rating band.
2. **What the simulator can do now.** Nothing with this. Native v0/3 gives every athlete the same body and rating, so a slot's bands change nothing yet.
3. **Unimplemented or unproven.** Every band is a reasoned first value against a PLACEHOLDER envelope. "Failure" and "graceful" are predictions about play, not observations. The staffing figures are arithmetic on the bands, not results.
4. **Blocking.** The attribute step (`ATTRIBUTE_STEP_SPEC.md`). Until ratings reach the engine no profile can be tested.
5. **Recommended action.** None for the owner beyond the envelope itself: confirm or replace the usual ranges when you are ready to make them canon.

## 1. Scope
- By the owner amendment of 14 Nov 2026 22:42 this file replaces roster fit. The Ala and Xenar rosters were not read. There are no named players, no roster fit scores and no "best styles for a team".
- **Design envelope (PLACEHOLDER, not canon):** ratings 0 to 1, typical professionals 0.60 to 1.00 on every rating; heights about 2.40 to 2.95 m; masses about 155 to 285 kg. Canon: a speed rating of 1.0 is 44.704 m/s. All bands below are written against this envelope.
- **Bands.** ELITE 0.90 or more; KEY 0.85 or more; SUPPORT 0.75 to 0.80; BASE 0.70. The slots that define a style gate one rating at KEY or above, or two where the method needs both in one body; the other slots gate at SUPPORT and BASE. Body gates sit near the middle of the range.
- **Failure or graceful.** A slot is marked FAILURE when the style's method stops existing without it: the number given is how many in-band players the slot needs for the method to exist at all (usually a pair, or one). Every other shortfall is graceful: the style still runs and does that job less well, roughly in proportion to the shortfall.
- **Keeper and Archer** are fixed roles by canon and are filled only from the roster's Keepers and Archers.

## 2. Assignment rule: assign by rating band from a supplied roster
Input: any roster table with an id, a role (field, keeper, archer), the ratings on a 0 to 1 scale, height and mass. The rule is the same for every style and every roster.

1. Keeper and Archer slots take an in-band athlete of that role if there is one, otherwise the highest-scoring.
2. Field slot instances are taken in the style's slot order, which is its priority order.
3. An athlete is **in band** for a slot if he meets every minimum.
4. In-band placement is a maximum matching between instances and in-band athletes, so no in-band placement is lost to an earlier choice. Candidates are tried in descending slot score; ties go to roster order.
5. Slot score is the weighted sum in the "Ranked by" column, with height and mass rescaled onto the 0.60 to 1.00 band.
6. An instance still empty takes the highest-scoring unassigned field athlete and is flagged **under band**, with each shortfall listed.
7. Status: **BROKEN** if any FAILURE slot has fewer in-band players than it needs; **FULL** if every instance is in band; otherwise **DEGRADED**.
8. The rest are the bench. A substitute takes the slot of the athlete he replaces.

Reference implementation: `audit/tactics/tools/roster_tools.py`, function `assign`. It is deterministic. It reports a status (FULL, DEGRADED, BROKEN) and the shortfalls for whatever roster it is given. That is a staffing check, not a ranking of styles for a team, but applied to a real roster it would say which styles that roster can staff; whether that is wanted is for the owner.

## 3. Profiles by style

### 1. Arc Siege (ARC)

| Slot | Rating bands needed | Ranked by | Mode | If filled by a weaker player |
| --- | --- | --- | --- | --- |
| GUN x3 | throw power 0.85 or more, throw accuracy 0.80 or more, catching 0.70 or more | throw power 0.4, throw accuracy 0.4, catching 0.1, height 0.1 | FAILURE below 2 in band | FAILURE below two in band: a slower or less accurate deep throw gives the Keeper time and the style has no other scoring route. With two of three in band one arc sector goes unused (graceful). |
| FEED x2 | throw accuracy 0.80 or more, awareness 0.75 or more, ball handling 0.70 or more | throw accuracy 0.4, awareness 0.4, ball handling 0.2 | graceful | Graceful: circulation slows, ball holders keep the ball longer than the Archer needs between arrows, and more freezes are taken. |
| SCREEN x3 | blocking 0.75 or more, strength 0.70 or more, mass 220 kg or more | blocking 0.3, strength 0.3, mass 0.2, height 0.2 | graceful | Graceful: a smaller or weaker screener hides less of the thrower from the Archer and gives the marker an easier path to the release. |
| SAFETY x2 | speed 0.85 or more, tackling 0.70 or more | speed 0.5, tackling 0.3, awareness 0.2 | graceful | Graceful: a slower SAFETY concedes more runs after a saved or missed throw. |
| KEEPER x1 | keeper skill 0.80 or more, catching 0.70 or more | keeper skill 0.5, catching 0.2, jump 0.15, height 0.15 | graceful | Graceful: a weaker Keeper concedes more of the throws that reach the goal; no part of the plan stops working. |
| ARCHER x1 | archery accuracy 0.75 or more, awareness 0.70 or more | archery accuracy 0.7, awareness 0.3 | graceful | Graceful: fewer freezes per opposing possession; no part of the plan stops working. |

Staffing arithmetic over 2000 generated rosters: not broken 75%, fully in band 13%, mean field slots in band 8.61 of 10. Broken by slot: GUN 25%. All-average roster: BROKEN at GUN, 5 of 10 field slots in band.

### 2. Zone Waves (WAVE)

| Slot | Rating bands needed | Ranked by | Mode | If filled by a weaker player |
| --- | --- | --- | --- | --- |
| HUB x2 | awareness 0.85 or more, throw accuracy 0.75 or more, ball handling 0.70 or more | awareness 0.4, throw accuracy 0.4, ball handling 0.2 | FAILURE below 1 in band | FAILURE with none in band: entries are fed late or to the wrong man and attackers burn their 5 s without the ball. With one in band the feed comes from one side only (graceful). |
| DART x4 | agility 0.85 or more, speed 0.75 or more, catching 0.70 or more | agility 0.35, speed 0.25, catching 0.25, throw accuracy 0.15 | FAILURE below 2 in band | FAILURE below two in band: there is no pair quick enough to get in and out inside the limit; either the zone empties or residence turnovers rise. With two or three the weaker pair makes shorter, shallower visits (graceful). |
| PIVOT x2 | strength 0.80 or more, balance 0.75 or more, catching 0.70 or more | strength 0.3, balance 0.3, catching 0.2, height 0.2 | graceful | Graceful: a lighter or shorter PIVOT is moved off his spot and the team loses the target at the goal front; DARTs still rotate. |
| ANCHOR x2 | speed 0.80 or more, tackling 0.70 or more | speed 0.5, tackling 0.3, awareness 0.2 | graceful | Graceful: a slower ANCHOR concedes more runs after a save. |
| KEEPER x1 | keeper skill 0.80 or more, catching 0.70 or more | keeper skill 0.5, catching 0.2, jump 0.15, height 0.15 | graceful | Graceful: a weaker Keeper concedes more of the throws that reach the goal; no part of the plan stops working. |
| ARCHER x1 | archery accuracy 0.75 or more, awareness 0.70 or more | archery accuracy 0.7, awareness 0.3 | graceful | Graceful: fewer freezes per opposing possession; no part of the plan stops working. |

Staffing arithmetic over 2000 generated rosters: not broken 82%, fully in band 13%, mean field slots in band 8.46 of 10. Broken by slot: DART 16%, HUB 3%. All-average roster: BROKEN at HUB, DART, 4 of 10 field slots in band.

### 3. Carry Train (RAM)

| Slot | Rating bands needed | Ranked by | Mode | If filled by a weaker player |
| --- | --- | --- | --- | --- |
| RAM x2 | strength 0.85 or more, balance 0.75 or more, ball handling 0.70 or more, mass 220 kg or more | strength 0.25, balance 0.25, ball handling 0.15, contact resistance 0.15, mass 0.2 | FAILURE below 2 in band | FAILURE below two in band: by rule the tackled carrier is the snapper, so after the first tackle the other RAM makes the scoring run. One strong carrier is half a plan. |
| PLOW x4 | blocking 0.85 or more, strength 0.75 or more, mass 220 kg or more | blocking 0.4, strength 0.3, mass 0.3 | FAILURE below 2 in band | FAILURE below two in band: no wedge forms and the carrier meets the first tackler alone. With two or three the wedge covers one side only (graceful). |
| FLANK x2 | speed 0.80 or more, catching 0.75 or more, ball handling 0.70 or more | speed 0.4, catching 0.3, ball handling 0.3 | graceful | Graceful: without a reliable outlet the carrier has no pass when the wedge stalls. |
| TAIL x2 | tackling 0.80 or more, speed 0.70 or more | tackling 0.5, speed 0.3, awareness 0.2 | graceful | Graceful: loose balls behind the wedge are lost more often. |
| KEEPER x1 | keeper skill 0.80 or more, catching 0.70 or more | keeper skill 0.5, catching 0.2, jump 0.15, height 0.15 | graceful | Graceful: a weaker Keeper concedes more of the throws that reach the goal; no part of the plan stops working. |
| ARCHER x1 | archery accuracy 0.75 or more, awareness 0.70 or more | archery accuracy 0.7, awareness 0.3 | graceful | Graceful: fewer freezes per opposing possession; no part of the plan stops working. |

Staffing arithmetic over 2000 generated rosters: not broken 26%, fully in band 2%, mean field slots in band 6.85 of 10. Broken by slot: PLOW 47%, RAM 53%. All-average roster: BROKEN at RAM, PLOW, 4 of 10 field slots in band.

### 4. Archer's Anvil (ANVIL)

| Slot | Rating bands needed | Ranked by | Mode | If filled by a weaker player |
| --- | --- | --- | --- | --- |
| ARCHER x1 | archery accuracy 0.85 or more, awareness 0.75 or more | archery accuracy 0.7, awareness 0.3 | FAILURE below 1 in band | FAILURE out of band: the defence has given up tackling in midfield to feed the Archer; an Archer who misses leaves a carrier nobody is trying to stop. |
| SHADOW x3 | speed 0.85 or more, agility 0.80 or more, awareness 0.70 or more | speed 0.35, agility 0.35, awareness 0.3 | FAILURE below 2 in band | FAILURE below two in band: a carrier who runs past his shadows reaches the zone, where he cannot be frozen. With two the weak side is open (graceful). |
| RING x4 | tackling 0.80 or more, ball handling 0.70 or more, speed 0.70 or more | tackling 0.4, ball handling 0.3, speed 0.3 | graceful | Graceful: more carriers get through the arc and fewer loose balls are picked up. |
| LID x3 | awareness 0.80 or more, speed 0.75 or more | awareness 0.5, speed 0.5 | graceful | Graceful: receivers get free more often and the ball leaves the Archer's lane by pass. |
| KEEPER x1 | keeper skill 0.80 or more, catching 0.70 or more | keeper skill 0.5, catching 0.2, jump 0.15, height 0.15 | graceful | Graceful: a weaker Keeper concedes more of the throws that reach the goal; no part of the plan stops working. |

Staffing arithmetic over 2000 generated rosters: not broken 30%, fully in band 5%, mean field slots in band 8.21 of 10. Broken by slot: ARCHER 59%, SHADOW 25%. All-average roster: BROKEN at ARCHER, SHADOW, 7 of 10 field slots in band.

### 5. High Press (PRESS)

| Slot | Rating bands needed | Ranked by | Mode | If filled by a weaker player |
| --- | --- | --- | --- | --- |
| SWEEP x2 | speed 0.85 or more, tackling 0.75 or more, awareness 0.70 or more | speed 0.5, tackling 0.3, awareness 0.2 | FAILURE below 1 in band | FAILURE with none in band: one missed tackle or one long pass is a free run at the Keeper. With one in band half the field is uncovered (graceful). |
| HOUND x4 | tackling 0.85 or more, speed 0.80 or more, stamina 0.70 or more | speed 0.35, tackling 0.45, stamina 0.2 | FAILURE below 2 in band | FAILURE below two in band: two go to the ball every time; if they miss or arrive late the press is open behind them. With two or three the outlets are pressed by weaker tacklers (graceful). |
| MARK x4 | speed 0.80 or more, agility 0.75 or more, awareness 0.70 or more | speed 0.35, agility 0.35, awareness 0.3 | graceful | Graceful: receivers get open more often and the carrier has a pass before the tackle arrives. |
| KEEPER x1 | keeper skill 0.80 or more, catching 0.70 or more | keeper skill 0.5, catching 0.2, jump 0.15, height 0.15 | graceful | Graceful: a weaker Keeper concedes more of the throws that reach the goal; no part of the plan stops working. |
| ARCHER x1 | archery accuracy 0.75 or more, awareness 0.70 or more | archery accuracy 0.7, awareness 0.3 | graceful | Graceful: fewer freezes per opposing possession; no part of the plan stops working. |

Staffing arithmetic over 2000 generated rosters: not broken 62%, fully in band 2%, mean field slots in band 6.13 of 10. Broken by slot: HOUND 36%, SWEEP 4%. All-average roster: BROKEN at SWEEP, HOUND, 4 of 10 field slots in band.

### 6. Long Count (COUNT)

| Slot | Rating bands needed | Ranked by | Mode | If filled by a weaker player |
| --- | --- | --- | --- | --- |
| METRONOME x3 | ball handling 0.85 or more, throw accuracy 0.75 or more, awareness 0.75 or more | ball handling 0.35, throw accuracy 0.35, awareness 0.3 | FAILURE below 2 in band | FAILURE below two in band: a 20 s possession is 8 or more passes; with weak handlers one of them is lost. With two the third handler is a risk the others pass around (graceful). |
| LINK x4 | catching 0.80 or more, agility 0.70 or more, awareness 0.70 or more | catching 0.4, agility 0.3, awareness 0.3 | graceful | Graceful: more passes are dropped or cut out, in proportion. A dropped short pass is a loose ball with three REST players behind it; a handler who loses the ball under pressure is not covered that way, which is why METRONOME is the failure slot. |
| REST x3 | tackling 0.75 or more, speed 0.75 or more | tackling 0.4, speed 0.4, awareness 0.2 | graceful | Graceful: a lost ball is more often a goal against. |
| KEEPER x1 | keeper skill 0.80 or more, catching 0.70 or more | keeper skill 0.5, catching 0.2, jump 0.15, height 0.15 | graceful | Graceful: a weaker Keeper concedes more of the throws that reach the goal; no part of the plan stops working. |
| ARCHER x1 | archery accuracy 0.75 or more, awareness 0.70 or more | archery accuracy 0.7, awareness 0.3 | graceful | Graceful: fewer freezes per opposing possession; no part of the plan stops working. |

Staffing arithmetic over 2000 generated rosters: not broken 77%, fully in band 15%, mean field slots in band 8.65 of 10. Broken by slot: METRONOME 23%. All-average roster: BROKEN at METRONOME, 7 of 10 field slots in band.

### 7. First Strike (STRIKE)

| Slot | Rating bands needed | Ranked by | Mode | If filled by a weaker player |
| --- | --- | --- | --- | --- |
| BOLT x3 | speed 0.90 or more, catching 0.75 or more | speed 0.5, catching 0.3, agility 0.2 | FAILURE below 2 in band | FAILURE below two in band: a runner who is caught from behind, or who drops a fast long pass, turns the plan into three players missing from the defence. With two one channel is unused (graceful). |
| CANNON x2 | throw power 0.85 or more, throw accuracy 0.80 or more | throw power 0.4, throw accuracy 0.4, awareness 0.2 | FAILURE below 1 in band | FAILURE with none in band: a long pass that is slow or off line is intercepted or run down. With one in band every break starts from the same player (graceful). |
| HALF x5 | tackling 0.80 or more, speed 0.70 or more, awareness 0.70 or more | tackling 0.4, speed 0.3, awareness 0.3 | graceful | Graceful: a seven-player defence concedes more, in proportion. |
| KEEPER x1 | keeper skill 0.80 or more, catching 0.70 or more, throw power 0.80 or more | keeper skill 0.4, catching 0.2, jump 0.1, throw power 0.2, height 0.1 | graceful | Graceful: without the throw power the Keeper starts breaks with a short pass to a CANNON; the break starts later. |
| ARCHER x1 | archery accuracy 0.75 or more, awareness 0.70 or more | archery accuracy 0.7, awareness 0.3 | graceful | Graceful: fewer freezes per opposing possession; no part of the plan stops working. |

Staffing arithmetic over 2000 generated rosters: not broken 78%, fully in band 5%, mean field slots in band 7.94 of 10. Broken by slot: BOLT 20%, CANNON 2%. All-average roster: BROKEN at BOLT, CANNON, 5 of 10 field slots in band.

### 8. Zone Lock (LOCK)

| Slot | Rating bands needed | Ranked by | Mode | If filled by a weaker player |
| --- | --- | --- | --- | --- |
| CLAMP x2 | strength 0.85 or more, tackling 0.80 or more, mass 230 kg or more | strength 0.3, tackling 0.3, balance 0.2, mass 0.2 | FAILURE below 2 in band | FAILURE below two in band: a carrier who breaks the wrap is 20 m from goal with no one in front of him but the Keeper. There is no graceful case: the door needs both jambs. |
| GATE x4 | tackling 0.80 or more, strength 0.70 or more, speed 0.70 or more | tackling 0.4, strength 0.3, speed 0.3 | graceful | Graceful: more entries are made away from the door, where no hold-up is waiting; the door itself still works for entries through it. |
| DENY x4 | speed 0.80 or more, awareness 0.75 or more, agility 0.70 or more | speed 0.35, awareness 0.35, agility 0.3 | graceful | Graceful: the held-up carrier finds a pass out more often, in proportion to how often his receiver gets free. |
| KEEPER x1 | keeper skill 0.80 or more, catching 0.70 or more | keeper skill 0.5, catching 0.2, jump 0.15, height 0.15 | graceful | Graceful: a weaker Keeper concedes more of the throws that reach the goal; no part of the plan stops working. |
| ARCHER x1 | archery accuracy 0.75 or more, awareness 0.70 or more | archery accuracy 0.7, awareness 0.3 | graceful | Graceful: fewer freezes per opposing possession; no part of the plan stops working. |

Staffing arithmetic over 2000 generated rosters: not broken 42%, fully in band 5%, mean field slots in band 7.54 of 10. Broken by slot: CLAMP 58%. All-average roster: BROKEN at CLAMP, 8 of 10 field slots in band.


## 4. Which style is most tolerant of an average roster
Two pieces of arithmetic, then a judgement.

**Arithmetic.** 2000 rosters were drawn from the seeded generator of the test plan (18 field athletes, 2 Keepers, 2 Archers; every rating independent and uniform on 0.60 to 1.00; height and mass uniform on the envelope) and assigned to each style. "All-average roster" is a roster where every rating is exactly 0.80 and every body is mid-range.

| Style | Slots that can fail | Not broken | Fully in band | Mean field slots in band (of 10) | All-average roster |
| --- | --- | --- | --- | --- | --- |
| Zone Waves | HUB (needs 1), DART (needs 2) | 82% | 13% | 8.46 | 4 of 10 field slots in band; breaks at HUB, DART |
| First Strike | BOLT (needs 2), CANNON (needs 1) | 78% | 5% | 7.94 | 5 of 10 field slots in band; breaks at BOLT, CANNON |
| Long Count | METRONOME (needs 2) | 77% | 15% | 8.65 | 7 of 10 field slots in band; breaks at METRONOME |
| Arc Siege | GUN (needs 2) | 75% | 13% | 8.61 | 5 of 10 field slots in band; breaks at GUN |
| High Press | SWEEP (needs 1), HOUND (needs 2) | 62% | 2% | 6.13 | 4 of 10 field slots in band; breaks at SWEEP, HOUND |
| Zone Lock | CLAMP (needs 2) | 42% | 5% | 7.54 | 8 of 10 field slots in band; breaks at CLAMP |
| Archer's Anvil | ARCHER (needs 1), SHADOW (needs 2) | 30% | 5% | 8.21 | 7 of 10 field slots in band; breaks at ARCHER, SHADOW |
| Carry Train | RAM (needs 2), PLOW (needs 2) | 26% | 2% | 6.85 | 4 of 10 field slots in band; breaks at RAM, PLOW |

What the arithmetic shows:
- **No style is fully in band on the all-average roster.** Each has at least one slot gated at 0.85 or more, and an all-0.80 roster meets none of those. Every style as written needs above-average players in its defining job.
- By the share of random rosters that do not break, the order is the order of the table. Zone Waves breaks least often.
- The styles that break most often are those that need two heavy, strong specialists (Carry Train, Zone Lock) or that hang on one of only two Archers (Archer's Anvil).
- These rates come from a generator in which ratings are independent. Real rosters have correlated ratings (a strong player is often heavy), which would raise the rates for the power styles. The rates describe the bands under that generator and nothing else.

**Judgement (a hypothesis, to be tested in stage 3 of the test plan).** The arithmetic does not pick a winner: every style breaks on the all-average roster, and the top four are within a few points of each other, which is inside the sampling noise of the count. My pick, from reasoning about the method and not from the table, is **Long Count**:
- It has one FAILURE slot, and on the all-average roster that slot is short by 0.05 on a single rating (ball handling 0.80 against 0.85), with the other two bands met.
- Its method is low-risk by construction: short passes into open lanes, no contact sought, three players behind the ball. A handler slightly under band loses a few more passes; nothing collapses in one play.
- Arc Siege has the same number of FAILURE slots and near-identical arithmetic, so the table cannot separate the two. I rank Long Count ahead because a weak GUN removes Arc Siege's only scoring route, while a weak METRONOME costs Long Count some passes.
- Zone Waves breaks less often by count, but its method is the least forgiving of a slow player when it is staffed thin: one late exit from the zone is a turnover, not a slightly worse possession.

Least tolerant, by the same reasoning: **Archer's Anvil** (one athlete carries the method and a roster has two candidates) and **Zone Lock** (the door needs two players who are strong, heavy and sound tacklers at once, and a broken wrap is a free run at goal).

## 5. Limits
- Bands are first values. Whether 0.85 is the right gate for any job depends on how the attribute step maps ratings to bodies and skills, and all of that except speed is PLACEHOLDER.
- FAILURE and graceful are predictions. Stage 3 of the test plan weakens one slot at a time to check them.
- Stamina is gated for one slot (HOUND) but cannot matter in Native v0/3, where fatigue is off.
- Keeper bodies use the same envelope as everyone else. Older project notes give Keepers a larger body range; that is an open question (Q-TAC-5).
