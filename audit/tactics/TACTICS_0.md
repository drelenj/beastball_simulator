# TACTICS-0: eight team styles for Beastball (hypotheses)
Claude (Fable), 2026-11-15. Branch `claude/tactics-0`, from `claude/hp002-audit` @ 8d95bf2. Classified against Native v0/3 (`claude/native-v0-3-handoff-69stxd` @ 8613280).
Status: **DESIGN COMPLETE**. Not IMPLEMENTED, not TESTED, not ACCEPTED. Generated from `audit/tactics/tools/tactics_src.py` by `build.py`; edit the source, not this file.

## OWNER BRIEFING
1. **Accomplished.** Eight ways to play are written down as formations of role slots, the rating bands each slot needs, numeric tendencies, restart and Hunt plans, and a prediction for 19 of the 28 pairings. One exploits the 5 s Keeper Zone limit in attack and one in defence, one is built on deep throws, one on carries, one leans on the Archer.
2. **What the simulator can do now.** Nothing new. Native v0/3 can express 17 of the 61 tactic parameters, and only as one value for the whole team. It has no slots and ignores ratings, so it cannot play any of these styles as written.
3. **Unimplemented or unproven.** All of it. These are reasoned guesses about play. No value was searched or tuned and no match was run. Predictions are there to be checked, and several rest on engine behaviour nobody has measured (for example whether a wrap can hold a carrier for seconds).
4. **Blocking.** Two builds must exist before any style can be tested: the attribute step (`ATTRIBUTE_STEP_SPEC.md`, Codex) and the playbook interface (`TACTIC_INTERFACE.md`, Codex and Claude). Five canon questions are open in `QUESTIONS_FOR_OWNER.md`; each has a placeholder, so none blocks the design.
5. **Recommended action.** Relay the attribute step spec to Codex. Answer Q-TAC-1 to Q-TAC-5 when convenient.

## 1. How to read this
- **Hypotheses.** A style here is a guess that a method could work under the rules. Match results decide, later. Nothing below is called good.
- **Generic personnel.** By the owner amendment of 14 Nov 2026 22:42 the Ala and Xenar rosters were not read and are not used. Every slot is described by rating bands only. There are no player names.
- **Design envelope (PLACEHOLDER, not canon).** Ratings run 0 to 1 and a typical professional sits at 0.60 to 1.00 on every rating. Heights are about 2.40 to 2.95 m and masses about 155 to 285 kg. The one canon number is that a speed rating of 1.0 is 44.704 m/s. Every band below is written against this envelope and moves if the envelope moves.
- **Bands.** ELITE 0.90 or more (the top quarter of the professional band); KEY 0.85 or more (top three eighths); SUPPORT 0.75 to 0.80; BASE 0.70. Body gates sit near the middle of the range. A slot has one KEY rating, or two where the method needs both in one body.
- **Three tags on every parameter** (full definitions in section 6): NOW = Native v0/3 can run it today; COORD = the mechanics exist but athletes need a shared pre-match plan; ENGINE = the engine, port or rules layer lacks something.
- **Personnel profiles** (the amended D2) are in `PERSONNEL_PROFILES.md`. The machine-readable form is `tactics_0.json`.

## 2. What the styles are built on
Each line is tagged CANON (ruled or ratified by DreLen), AS BUILT (what Native v0/3 does; not Rulebook text) or PLACEHOLDER.

| Fact | Tag | Used by |
| --- | --- | --- |
| 12 a side: 10 field players, 1 Keeper, 1 Archer. Keeper and Archer are fixed roles. 22 on the gameday roster | CANON | all |
| 30 s play clock, carried through a tackle; expiry is a turnover | CANON | Long Count, High Press |
| First grounding tackle: offence keeps the ball, scrimmage at the spot. Second: turnover | CANON | Carry Train, High Press, Zone Lock |
| A first tackle less than 10 m from the goal plane is re-spotted at 10 m | CANON | Carry Train |
| A turnover is scrimmaged at the spot, or at the gaining team's own 40 m line if that is closer to the goal it attacks | CANON | High Press |
| After a score: scrimmage at the conceding team's own 40 m line, every athlete at or behind his own 40 m line | CANON | First Strike |
| An attacker may be in the Keeper Zone (20 m) for at most 5 s at a time; expiry is a turnover | CANON | Zone Waves, Zone Lock |
| A defender may stay in the zone only while within 5 m of an offensive player | CANON | Arc Siege, Zone Waves |
| How long an unmarked defender may stay before it is a foul: 5 s | PLACEHOLDER (Q-ZONE-1) | Zone Waves |
| No minimum time outside before an attacker may re-enter | AS BUILT; canon is silent (Q-TAC-1) | Zone Waves |
| The Archer may shoot only opposing field players whose team has control of the ball, outside both zones, not frozen or immune, after the Hunt has cleared | CANON, AS BUILT | Archer's Anvil, Zone Waves |
| No arrow at a player outside the Archer's own half | CANON (ratified); not built in v0/3 | Long Count |
| 15 arrows and 5 freezes per opposing possession; freeze 5 s, then 10 s immunity; arrow 250 m/s | CANON (v0/3 still allows 25 arrows; RB-1 item) | Archer's Anvil |
| A frozen ball holder drops the ball; a tackle on a frozen player is cancelled | AS BUILT (Q-TAC-2) | Archer's Anvil |
| The Archer releases at most one arrow every 2.6 s | AS BUILT (a constant in cognition; Q-TAC-3) | Arc Siege, First Strike |
| No offside in live play; offside is judged at scrimmages against the ball line | CANON | First Strike |
| No defender within 5 m of an opponent before the ball is live | CANON | all restarts |
| A carrier may not carry, and a team may not pass to a teammate, from outside into its own Keeper Zone; a ball in the own zone must leave within 5 s | CANON (D1 record R-11 to R-13) | Long Count |
| A defender may wrap the carrier from below the neck down. Two opponents holding the ball itself for 1 s is a held ball | CANON | Zone Lock |
| Off-ball contact is legal below the neck and above the hip, with no grip; tripping or tackling a player without the ball is a major foul | CANON | Carry Train, High Press |
| A defensive minor foul at tackle count 0 is a half goal (a full goal in period 4 and overtime) | CANON | High Press |
| One dribble per possession; no kicking | CANON | First Strike |
| Scoring: flat (goal 2, half goal 1) in force; the banded scale (carry 5, throws 2/3/4, half goal 1, award 3, own goal 2) is PROVISIONAL | CANON | all |
| Every athlete has the same body (2.55 m, 230 kg, 27 m/s) and rating 0.70; every pass and shot leaves at 27 m/s; fatigue is off; there are no slots | AS BUILT | all |

Substitutions are unlimited at dead balls by canon, but TACTICS-0 does not use them tactically: the same ten field starters play attack and defence, which is why each slot's bands cover both. Timeouts follow the canon default coach policy and are not a tactic parameter.

## 3. Conventions
- **Frame.** Each team reads the field in its own frame: distance from its own goal line toward the goal it attacks (0 to 100 m), and lateral distance from the centre line.
- **Slots.** A slot is a job, not a player. "GUN x3" means three athletes hold that job. Ten field instances per style, plus KEEPER and ARCHER.
- **Five situations.** Offence (own team has passive possession), defence, own restart, opponent restart, Hunt. At a toss-in slots use their live-play positions with opponents 3 m clear.
- **Positions are beliefs.** Every position is evaluated by the athlete from what he himself believes about the ball and the other players. The engine places nobody.
- **"Behind the line"** at a restart means on the athlete's own side of the restraining line: the ball line at a tackle or turnover scrimmage; at a 40 m scrimmage, the ball line for the restarting team and its own 40 m line for the defending team.
- **Rules every restart plan keeps:** the tackled carrier is the snapper and the tackler stands opposite him or 5 m behind; everyone else starts onside; no defender within 5 m of an opponent before the ball is live, so defensive positions are 5.5 m or more behind the line; snap inside 10 s; toss within 4 s of ready.
- **Hunt.** One contestant per team; the ball is live when it has left the centre circle; Archers hold until then. Everyone else waits in his own half at least 7 m from the centre spot (PLACEHOLDER, as built: canon gives no set-up distances, Q-HUNT-1).

### Neutral default
Where a style has no opinion it uses the neutral value, which is Native v0/3's present behaviour wherever one exists. Substitutions are `cover only` for every style.

| Area | Parameter | Neutral value | Tag |
| --- | --- | --- | --- |
| Ball movement | bias pass | 0 | NOW |
| Ball movement | pass min clearance m | 0 | NOW |
| Ball movement | pass len band m | 4 to 34 | ENGINE |
| Ball movement | touch time max s | 30 | COORD |
| Ball movement | dribble use | none | COORD |
| Scoring method | finish pref | carry 0.3, close 0.3, mid 0.25, deep 0.15 | COORD |
| Scoring method | bias shoot | 0 | NOW |
| Scoring method | shot range min m | 0 | COORD |
| Scoring method | shot range max m | 32 | NOW |
| Scoring method | shot speed frac | 0.9 | ENGINE |
| Tempo and clock | shot window s | 0 to 26 | COORD |
| Tempo and clock | must shoot remaining s | 4 | COORD |
| Tempo and clock | snap delay s | leading 0, otherwise 0 | COORD |
| Tempo and clock | hold own half until remaining s | 30 | COORD |
| Tempo and clock | first action max s | 10 | COORD |
| Tempo and clock | short field trigger m | 0 | COORD |
| Carrier in contact | contact response | run through 0.5, dodge 0.3, brace 0.2 | COORD |
| Carrier in contact | first tackle bank m | 100 | ENGINE |
| Keeper Zone (attack) | entry mode | late only | COORD |
| Keeper Zone (attack) | dwell max s | 3 | COORD |
| Keeper Zone (attack) | occupancy target | 1 | COORD |
| Keeper Zone (attack) | min outside s | 1 | COORD |
| Keeper Zone (attack) | entry stagger s | 0 | COORD |
| Keeper Zone (attack) | wedge | no | ENGINE |
| Keeper Zone (attack) | arrow screen | no | COORD |
| Tackle aggression | scheme | arc shell | COORD |
| Tackle aggression | bias press | 0 | NOW |
| Tackle aggression | pressers max | 2 | COORD |
| Tackle aggression | press line m | 100 | COORD |
| Tackle aggression | commit gap m | 6 | COORD |
| Tackle aggression | contain gap m | 5 to 7 | COORD |
| Tackle aggression | takedown line m | 100 | COORD |
| Tackle aggression | contact by area | midfield takedown, arc takedown, zone takedown | COORD |
| Tackle aggression | contact at count1 | same as area | ENGINE |
| Tackle aggression | holdup drive | none | COORD |
| Tackle aggression | bias pursue | 0 | NOW |
| Archer | eagerness | 0 | NOW |
| Archer | target priority | carrier 1, receiver near goal 0.5, other 0.3 | COORD |
| Keeper | depth m | 1.5 to 4 | COORD |
| Keeper | distribution | short | COORD |
| Restarts | scrim play | default | COORD |
| Restarts | snap40 play | default | COORD |
| Restarts | toss play | short toss | COORD |
| Restarts | def alignment | shell | COORD |
| Restarts | taker slot | nearest | COORD |
| Hunt | contestant slot | none | COORD |
| Hunt | win action | tip out | COORD |
| Positioning weights | ball att | 0.6 | NOW |
| Positioning weights | ball def | 1.2 | NOW |
| Positioning weights | goal att | 1 | NOW |
| Positioning weights | goal def | 1 | NOW |
| Positioning weights | spread | 1 | NOW |
| Positioning weights | opp att | 0.6 | NOW |
| Positioning weights | opp def | 0.6 | NOW |
| Positioning weights | lane | 0.8 | NOW |
| Positioning weights | edge zone | 1 | NOW |

## 4. The eight styles

### 1. Arc Siege (ARC)

**Idea.** Keep every attacker outside the Keeper Zone on the 21 to 24 m arc, move the ball by quick passes, and score with hard throws released from 20 m or more. The bet is that a fast, accurate deep throw beats a Keeper who has no help, because defenders may not wait inside the zone without an attacker to mark.

**Formation.** 3 GUN on the arc, 3 SCREEN paired goal-side of them, 2 FEED behind, 2 SAFETY held back.

**Slots and what each needs.**

| Slot | Job | Needs (minimum bands) | If filled by a weaker player |
| --- | --- | --- | --- |
| GUN x3 | Deep thrower: catches on the arc and throws at goal from 20 m or more. | throw power 0.85 or more, throw accuracy 0.80 or more, catching 0.70 or more | FAILURE below two in band: a slower or less accurate deep throw gives the Keeper time and the style has no other scoring route. With two of three in band one arc sector goes unused (graceful). |
| FEED x2 | Distributor: stands behind the arc and moves the ball from side to side. | throw accuracy 0.80 or more, awareness 0.75 or more, ball handling 0.70 or more | Graceful: circulation slows, ball holders keep the ball longer than the Archer needs between arrows, and more freezes are taken. |
| SCREEN x3 | Screener: stands goal-side of a GUN, in the marker's path and on the Archer's sight line. | blocking 0.75 or more, strength 0.70 or more, mass 220 kg or more | Graceful: a smaller or weaker screener hides less of the thrower from the Archer and gives the marker an easier path to the release. |
| SAFETY x2 | Last line in attack, ball pressure in defence, Hunt contestant. | speed 0.85 or more, tackling 0.70 or more | Graceful: a slower SAFETY concedes more runs after a saved or missed throw. |
| KEEPER x1 | Goalkeeper (fixed role by canon). | keeper skill 0.80 or more, catching 0.70 or more | Graceful: a weaker Keeper concedes more of the throws that reach the goal; no part of the plan stops working. |
| ARCHER x1 | Archer (fixed role by canon). | archery accuracy 0.75 or more, awareness 0.70 or more | Graceful: fewer freezes per opposing possession; no part of the plan stops working. |

**Where each slot stands.**

| Slot | Offence | Defence | Own restart | Opponent restart | Hunt |
| --- | --- | --- | --- | --- | --- |
| GUN | 21 to 24 m from the attacked goal, bearings -55 to 55 degrees, spread evenly | 21 to 24 m from the own goal, bearings -40 to 40 degrees, spread evenly | 6 to 10 m behind the line, lateral -16 to 16 m (spread behind the ball, ready to run to the arc) | 5.5 to 8 m behind the line, lateral -12 to 12 m | 25 to 40 m from the own goal line, lateral -25 to 25 m (own half, outside the centre circle) |
| FEED | 28 to 32 m from the attacked goal, 8 to 20 degrees off centre, one each side | 27 to 31 m from the own goal, 10 to 25 degrees off centre, one each side | 6 to 8 m behind the line, 3.2 to 8 m to each side (takes the quick_swing throw) | 7 to 10 m behind the line, 3.2 to 8 m to each side | 38 to 45 m from the own goal line, 7 to 14 m off the centre line, one each side (own half, at least 7 m from the centre spot, to take a tip-out) |
| SCREEN | 1.5 to 2.5 m goal-side of a paired GUN, never closer than 20.5 m to the goal (between the paired GUN and the goal, never inside the zone) | 21 to 23 m from the own goal, bearings -60 to 60 degrees, spread evenly | 0.8 to 3 m behind the line, lateral -10 to 10 m (on the ball line, first to the arc) | 5.5 to 6.5 m behind the line, lateral -10 to 10 m | 25 to 40 m from the own goal line, lateral -25 to 25 m (own half, outside the centre circle) |
| SAFETY | 45 to 58 m from the own goal line, 4.8 to 12 m off the centre line, one each side (stays back against the break) | marks the ball carrier, goal side, at 0 to 6 m (the two who close on the carrier) | 14 to 22 m behind the line, 4 to 10 m to each side | 10 to 16 m behind the line, 4 to 10 m to each side | The faster SAFETY is the contestant; the other stands 12 m behind the centre spot. |

Keeper and Archer hold their fixed posts (Keeper inside his zone, Archer on the platform).

**Tendencies.** The core parameters, plus every other parameter that differs from the neutral default of section 3 (differences in bold). Anything not listed is the neutral default. Tag: NOW = expressible now, COORD = needs coordination, ENGINE = needs engine work.

| Area | Parameter | Value | Tag |
| --- | --- | --- | --- |
| Ball movement | bias pass | **1.5** | NOW |
| Ball movement | pass min clearance m | **2** | NOW |
| Ball movement | pass len band m | **8 to 30** | ENGINE |
| Ball movement | touch time max s | **1.5** | COORD |
| Scoring method | finish pref | **carry 0.1, close 0.05, mid 0.15, deep 0.7** | COORD |
| Scoring method | bias shoot | **3** | NOW |
| Scoring method | shot range min m | **20** | COORD |
| Scoring method | shot range max m | **27** | NOW |
| Scoring method | shot speed frac | **1** | ENGINE |
| Tempo and clock | shot window s | **8 to 22** | COORD |
| Tempo and clock | must shoot remaining s | **5** | COORD |
| Carrier in contact | contact response | **run through 0.2, dodge 0.6, brace 0.2** | COORD |
| Keeper Zone (attack) | entry mode | **rebound only** | COORD |
| Keeper Zone (attack) | dwell max s | **2** | COORD |
| Keeper Zone (attack) | occupancy target | **0** | COORD |
| Keeper Zone (attack) | arrow screen | **yes** | COORD |
| Tackle aggression | scheme | arc shell | COORD |
| Tackle aggression | pressers max | 2 | COORD |
| Tackle aggression | press line m | **45** | COORD |
| Tackle aggression | commit gap m | 6 | COORD |
| Tackle aggression | contact by area | midfield takedown, arc takedown, zone takedown | COORD |
| Archer | eagerness | 0 | NOW |
| Archer | target priority | carrier 1, receiver near goal 0.5, other 0.3 | COORD |
| Restarts | scrim play | **quick swing** | COORD |
| Restarts | snap40 play | **quick swing** | COORD |
| Restarts | toss play | short toss | COORD |
| Restarts | def alignment | shell | COORD |
| Restarts | taker slot | **FEED** | COORD |
| Hunt | contestant slot | **SAFETY** | COORD |
| Hunt | win action | tip out | COORD |
| Positioning weights | ball att | **0.3** | NOW |
| Positioning weights | spread | **1.5** | NOW |
| Positioning weights | lane | **1.5** | NOW |
| Positioning weights | edge zone | **3** | NOW |

**Plays named above.** *quick swing*: The taker throws 6 to 8 m back and to one side to a named handler slot, who starts the normal offence. All teammates start behind the ball line. *short toss*: The thrower tosses 6 to 10 m infield to the nearest named handler slot. The thrower may not recover the ball himself and the ball cannot score until another player controls it.
*Defensive alignment (shell)*: All field defenders stand 5.5 m or more on their own side of the restraining line, between ball and goal.

**What the style should look like if it is being played** (checked before any result is read):

- shots released 20m plus share: >= 0.6
- attacker zone seconds per possession: <= 2
- ball holder touch time s median: <= 1.8

**Strengths (reasoned, untested).**

- Never puts an attacker on the 5 s zone limit.
- Keeps the defence out of the zone by rule: a defender may stay there only within 5 m of an attacker.
- Deep throws are the highest-valued throws on the provisional scale (4).

**Weaknesses (reasoned, untested).**

- Every attacker is a legal arrow target for the whole possession.
- Needs two rare players: high throw power and high accuracy together.
- A saved or missed throw is a live ball with eight attackers 70 m or more from their own goal.
- Under the flat scoring now in force a deep goal is worth no more than a close one.

**Canon check.**

- No attacker waits inside the zone; a rebound chase leaves within 2 s (limit 5 s).
- Screens are stationary bodies; any contact stays in the legal band (below the neck, above the hip, no grip).
- No pass or carry goes back into the own Keeper Zone (ZR-C, ZR-T).

**Against the other seven (predictions to be tested, not results).**

| Opponent | Prediction | Why |
| --- | --- | --- |
| Long Count | edge to Arc Siege | Count's shell waits on the arc and commits late (4 m). In-band GUNs release from 21 to 24 m over it, and Count's long possessions do not lower the quality of Arc's attempts. |
| Zone Lock | edge to Arc Siege | Lock's trap needs a zone entry and Arc does not enter. Lock contains outside its takedown line, so GUNs release unhurried. |
| Archer's Anvil | edge to Archer's Anvil | Arc's throwers and feeders stand outside the zone in the Archer's half for the whole possession: up to five freezes on near-stationary targets, and as built a frozen ball holder drops the ball. |
| High Press | edge to High Press | Arc needs time to set five players on the arc and circulate. The press tackles the first receiver before the arc forms, and GUN and SCREEN profiles are not chosen for escaping pressure. |
| Zone Waves | none | Neither method touches the other's. Outside finishing against man marking, inside finishing against an arc shell: no prediction. |
| Carry Train | none | Ram's Wall stands at 24 to 28 m, right where GUNs release, but its heavy profiles are slow to close: no prediction. |
| First Strike | none | Arc attacks ten against seven, but every saved throw is a live ball with BOLTs already high. Which is larger is the question. |

### 2. Zone Waves (WAVE)

**Idea.** The 5 s limit is counted per attacker and "at a time", so the team rotates attackers through the Keeper Zone in short visits of 3.5 s and always has fresh ones inside. Attackers inside the zone are not legal arrow targets, and they finish with close and mid throws or a carry.

**Formation.** 2 HUB outside the arc, 4 DART in two alternating pairs, 2 PIVOT alternating at the goal front, 2 ANCHOR held back.

**Slots and what each needs.**

| Slot | Job | Needs (minimum bands) | If filled by a weaker player |
| --- | --- | --- | --- |
| HUB x2 | Feeder: holds the ball outside the arc and passes to attackers as they enter. | awareness 0.85 or more, throw accuracy 0.75 or more, ball handling 0.70 or more | FAILURE with none in band: entries are fed late or to the wrong man and attackers burn their 5 s without the ball. With one in band the feed comes from one side only (graceful). |
| DART x4 | In-and-out runner: enters the zone, receives, finishes or leaves before 3.5 s. | agility 0.85 or more, speed 0.75 or more, catching 0.70 or more | FAILURE below two in band: there is no pair quick enough to get in and out inside 3.5 s; either the zone empties or residence turnovers rise. With two or three the weaker pair makes shorter, shallower visits (graceful). |
| PIVOT x2 | Target at the goal front: receives with his back to goal, turns and throws or hands off. | strength 0.80 or more, balance 0.75 or more, catching 0.70 or more | Graceful: a lighter or shorter PIVOT is moved off his spot and the team loses the target at the goal front; DARTs still rotate. |
| ANCHOR x2 | Last line in attack, ball pressure in defence, Hunt contestant. | speed 0.80 or more, tackling 0.70 or more | Graceful: a slower ANCHOR concedes more runs after a save. |
| KEEPER x1 | Goalkeeper (fixed role by canon). | keeper skill 0.80 or more, catching 0.70 or more | Graceful: a weaker Keeper concedes more of the throws that reach the goal; no part of the plan stops working. |
| ARCHER x1 | Archer (fixed role by canon). | archery accuracy 0.75 or more, awareness 0.70 or more | Graceful: fewer freezes per opposing possession; no part of the plan stops working. |

**Where each slot stands.**

| Slot | Offence | Defence | Own restart | Opponent restart | Hunt |
| --- | --- | --- | --- | --- | --- |
| HUB | 24 to 30 m from the attacked goal, 12 to 30 degrees off centre, one each side | marks the nearest unmarked opponent, goal side, at 1.5 to 3 m | 6 to 8 m behind the line, 2.4 to 6 m to each side (takes the zone_stack throw) | 5.5 to 7 m behind the line, 4 to 10 m to each side | 38 to 45 m from the own goal line, 7 to 14 m off the centre line, one each side (own half, at least 7 m from the centre spot, to take a tip-out) |
| DART | in and out: inside at 6 to 13 m from the attacked goal (bearings -60 to 60 degrees) for at most the dwell time, then out to 21 to 24 m (two pairs; one pair inside while the other is out) | marks the nearest unmarked opponent, goal side, at 1.5 to 3 m | 0.8 to 1.5 m behind the line, lateral -22 to 22 m (wide on the ball line) | 5.5 to 6.5 m behind the line, lateral -20 to 20 m | 25 to 40 m from the own goal line, lateral -25 to 25 m (own half, outside the centre circle) |
| PIVOT | in and out: inside at 8 to 14 m from the attacked goal (bearings -25 to 25 degrees) for at most the dwell time, then out to 21 to 23 m (the two PIVOTs alternate: one inside, one out) | marks the nearest unmarked opponent, goal side, at 1.5 to 3 m | 0.8 to 2 m behind the line, 1.6 to 4 m to each side | 5.5 to 6.5 m behind the line, 1.6 to 4 m to each side | 25 to 40 m from the own goal line, lateral -25 to 25 m (own half, outside the centre circle) |
| ANCHOR | 45 to 55 m from the own goal line, 4.8 to 12 m off the centre line, one each side | marks the ball carrier, goal side, at 0 to 6 m | 14 to 22 m behind the line, 4 to 10 m to each side | 10 to 16 m behind the line, 4 to 10 m to each side | The faster ANCHOR is the contestant; the other stands 12 m behind the centre spot. |

Keeper and Archer hold their fixed posts (Keeper inside his zone, Archer on the platform).

**Tendencies.** The core parameters, plus every other parameter that differs from the neutral default of section 3 (differences in bold). Anything not listed is the neutral default. Tag: NOW = expressible now, COORD = needs coordination, ENGINE = needs engine work.

| Area | Parameter | Value | Tag |
| --- | --- | --- | --- |
| Ball movement | bias pass | **1** | NOW |
| Ball movement | pass len band m | **6 to 22** | ENGINE |
| Ball movement | touch time max s | **2.5** | COORD |
| Scoring method | finish pref | **carry 0.2, close 0.5, mid 0.25, deep 0.05** | COORD |
| Scoring method | bias shoot | **1** | NOW |
| Scoring method | shot range min m | 0 | COORD |
| Scoring method | shot range max m | **18** | NOW |
| Scoring method | shot speed frac | **0.8** | ENGINE |
| Tempo and clock | shot window s | **6 to 20** | COORD |
| Tempo and clock | must shoot remaining s | 4 | COORD |
| Carrier in contact | contact response | **run through 0.2, dodge 0.6, brace 0.2** | COORD |
| Keeper Zone (attack) | entry mode | **rotation** | COORD |
| Keeper Zone (attack) | dwell max s | **3.5** | COORD |
| Keeper Zone (attack) | occupancy target | **3** | COORD |
| Keeper Zone (attack) | entry stagger s | **1.75** | COORD |
| Tackle aggression | scheme | **man** | COORD |
| Tackle aggression | pressers max | **1** | COORD |
| Tackle aggression | press line m | **40** | COORD |
| Tackle aggression | commit gap m | 6 | COORD |
| Tackle aggression | contact by area | midfield takedown, arc takedown, zone takedown | COORD |
| Archer | eagerness | 0 | NOW |
| Archer | target priority | carrier 1, receiver near goal 0.5, other 0.3 | COORD |
| Restarts | scrim play | **zone stack** | COORD |
| Restarts | snap40 play | **quick swing** | COORD |
| Restarts | toss play | short toss | COORD |
| Restarts | def alignment | **man up** | COORD |
| Restarts | taker slot | **HUB** | COORD |
| Hunt | contestant slot | **ANCHOR** | COORD |
| Hunt | win action | tip out | COORD |
| Positioning weights | goal att | **2** | NOW |
| Positioning weights | lane | **1.2** | NOW |
| Positioning weights | edge zone | **0** | NOW |

**Plays named above.** *zone stack*: The taker throws 7 m back to a HUB. DARTs stand wide on the ball line and enter the zone on the release, in their rotation order. *quick swing*: The taker throws 6 to 8 m back and to one side to a named handler slot, who starts the normal offence. All teammates start behind the ball line. *short toss*: The thrower tosses 6 to 10 m infield to the nearest named handler slot. The thrower may not recover the ball himself and the ball cannot score until another player controls it.
*Defensive alignment (man up)*: Each field defender stands 5.5 m on his own side of the restraining line, opposite one attacker, and closes on the release.

**What the style should look like if it is being played** (checked before any result is read):

- shots released inside zone share: >= 0.65
- attackers in zone mean settled: between 2 to 3
- attacker zone dwell s p95: <= 4
- zone residence turnovers per possession: <= 0.05

**Strengths (reasoned, untested).**

- Finishers are sheltered from the Archer while inside the zone.
- Close and mid throws give the Keeper the least time.
- Defenders who follow an attacker in must leave again when he leaves, or become unmarked.

**Weaknesses (reasoned, untested).**

- The rotation is a timing agreement with no live channel; each athlete acts on his own belief of where his partner is.
- Only 1.5 s of margin on the limit: any hold-up inside the zone risks a turnover.
- Close and mid throws are the lowest-valued throws on the provisional scale (2 and 3).
- HUBs outside the arc remain arrow targets.

**Canon check.**

- Every visit ends at 3.5 s, inside the 5 s limit; expiry would be a turnover.
- Reads the Rulebook wording "at most 5 seconds at a time" as a fresh 5 s on re-entry. Canon states no minimum time outside; the plan imposes 1.0 s on itself (PLACEHOLDER, Q-TAC-1).
- No contact on the Keeper inside his zone.

**Against the other seven (predictions to be tested, not results).**

| Opponent | Prediction | Why |
| --- | --- | --- |
| Archer's Anvil | edge to Zone Waves | Attackers inside the zone are not legal arrow targets and Wave keeps its finishers there. Anvil's shadows contain without tackling, which gives the rotation time. |
| Carry Train | edge to Zone Waves | Ram's Wall is staffed by heavy RAM and PLOW profiles. A rotation every 3.5 s makes them follow attackers in and out of the zone or stand unmarked. |
| Zone Lock | edge to Zone Lock | Wave enters the zone by design with 1.5 s of margin. A hold-up of 1.5 s turns a visit into a residence turnover. |
| Arc Siege | none | Neither method touches the other's. Outside finishing against man marking, inside finishing against an arc shell: no prediction. |
| High Press | none | The press may break the rotation before it forms, or its man marking may be dragged in and out of the zone: no prediction. |
| Long Count | none | Count's shell must follow attackers into the zone or leave them free; whether it copes is not something reasoning settles. |
| First Strike | none | Wave commits five or six attackers deep, but many of its turnovers are dead balls (residence): no prediction. |

### 3. Carry Train (RAM)

**Idea.** One power carrier runs behind a wedge of blockers and the team spends its one free tackle on purpose, close to goal. From the scrimmage that follows, a second wedge run from 10 to 20 m carries the ball over the goal plane in under 5 s.

**Formation.** 2 RAM (carrier and relief), 4 PLOW in a V ahead of the ball, 2 FLANK wide, 2 TAIL behind.

**Slots and what each needs.**

| Slot | Job | Needs (minimum bands) | If filled by a weaker player |
| --- | --- | --- | --- |
| RAM x2 | Power carrier: carries into contact and stays up. | strength 0.85 or more, balance 0.75 or more, ball handling 0.70 or more, mass 220 kg or more | FAILURE with none in band: a carrier who goes down on first contact uses both tackles before the arc. With one in band there is no relief carrier (graceful). |
| PLOW x4 | Lead blocker: clears the carrier's path by legal off-ball contact. | blocking 0.85 or more, strength 0.75 or more, mass 220 kg or more | FAILURE below two in band: no wedge forms and the carrier meets the first tackler alone. With two or three the wedge covers one side only (graceful). |
| FLANK x2 | Wide outlet level with the ball. | speed 0.80 or more, catching 0.75 or more, ball handling 0.70 or more | Graceful: without a reliable outlet the carrier has no pass when the wedge stalls. |
| TAIL x2 | Trailer: recovers loose balls and is the last line. | tackling 0.80 or more, speed 0.70 or more | Graceful: loose balls behind the wedge are lost more often. |
| KEEPER x1 | Goalkeeper (fixed role by canon). | keeper skill 0.80 or more, catching 0.70 or more | Graceful: a weaker Keeper concedes more of the throws that reach the goal; no part of the plan stops working. |
| ARCHER x1 | Archer (fixed role by canon). | archery accuracy 0.75 or more, awareness 0.70 or more | Graceful: fewer freezes per opposing possession; no part of the plan stops working. |

**Where each slot stands.**

| Slot | Offence | Defence | Own restart | Opponent restart | Hunt |
| --- | --- | --- | --- | --- | --- |
| RAM | 0 to 6 m behind the ball, within 1 m laterally (one carries; the other trails 4 to 6 m behind as relief) | 24 to 28 m from the own goal, 4.8 to 12 degrees off centre, one each side | 4 to 6 m behind the line, lateral -1 to 1 m (takes the wedge_snap throw 5 m behind the ball) | 5.5 to 6.5 m behind the line, 1.2 to 3 m to each side | One RAM is the contestant and carries the ball out; the other stands 12 m behind the centre spot. |
| PLOW | 2 to 4.5 m ahead of the ball, within 4 m laterally (V ahead of the carrier, never more than 5 m from him) | 24 to 28 m from the own goal, bearings -45 to 45 degrees, spread evenly | 0.8 to 1.5 m behind the line, lateral -4 to 4 m (on the ball line in a V) | 5.5 to 6.5 m behind the line, lateral -8 to 8 m | 38 to 45 m from the own goal line, 7 to 14 m off the centre line, one each side (own half, at least 7 m from the centre spot, to take a tip-out) |
| FLANK | 1 m behind to 1 m ahead of the ball, 8 to 12 m to each side | marks the nearest unmarked opponent, goal side, at 1.5 to 3 m | 0.8 to 2 m behind the line, 10 to 14 m to each side | 5.5 to 7 m behind the line, 12 to 18 m to each side | 25 to 40 m from the own goal line, lateral -25 to 25 m (own half, outside the centre circle) |
| TAIL | 6 to 10 m behind the ball, 2.4 to 6 m to each side | marks the ball carrier, goal side, at 0 to 5 m | 9 to 14 m behind the line, 2.4 to 6 m to each side | 8 to 12 m behind the line, 2.4 to 6 m to each side | 25 to 40 m from the own goal line, lateral -25 to 25 m (own half, outside the centre circle) |

Keeper and Archer hold their fixed posts (Keeper inside his zone, Archer on the platform).

**Tendencies.** The core parameters, plus every other parameter that differs from the neutral default of section 3 (differences in bold). Anything not listed is the neutral default. Tag: NOW = expressible now, COORD = needs coordination, ENGINE = needs engine work.

| Area | Parameter | Value | Tag |
| --- | --- | --- | --- |
| Ball movement | bias pass | **-4** | NOW |
| Ball movement | pass len band m | **4 to 12** | ENGINE |
| Scoring method | finish pref | **carry 0.75, close 0.2, mid 0.05, deep 0** | COORD |
| Scoring method | bias shoot | **-1** | NOW |
| Scoring method | shot range min m | 0 | COORD |
| Scoring method | shot range max m | **12** | NOW |
| Scoring method | shot speed frac | **0.7** | ENGINE |
| Tempo and clock | shot window s | **6 to 24** | COORD |
| Tempo and clock | must shoot remaining s | **3** | COORD |
| Carrier in contact | contact response | **run through 0.7, dodge 0.1, brace 0.2** | COORD |
| Carrier in contact | first tackle bank m | **30** | ENGINE |
| Keeper Zone (attack) | entry mode | **drive** | COORD |
| Keeper Zone (attack) | dwell max s | **4** | COORD |
| Keeper Zone (attack) | occupancy target | **5** | COORD |
| Keeper Zone (attack) | wedge | **yes** | ENGINE |
| Tackle aggression | scheme | **wall** | COORD |
| Tackle aggression | bias press | **1** | NOW |
| Tackle aggression | pressers max | 2 | COORD |
| Tackle aggression | press line m | **35** | COORD |
| Tackle aggression | commit gap m | **5** | COORD |
| Tackle aggression | contact by area | midfield takedown, arc takedown, zone takedown | COORD |
| Archer | eagerness | 0 | NOW |
| Archer | target priority | carrier 1, receiver near goal 0.5, other 0.3 | COORD |
| Restarts | scrim play | **wedge snap** | COORD |
| Restarts | snap40 play | **wedge snap** | COORD |
| Restarts | toss play | short toss | COORD |
| Restarts | def alignment | **wall** | COORD |
| Restarts | taker slot | **TAIL** | COORD |
| Hunt | contestant slot | **RAM** | COORD |
| Hunt | win action | **carry out** | COORD |
| Positioning weights | ball att | **2** | NOW |
| Positioning weights | spread | **0.2** | NOW |
| Positioning weights | edge zone | **0.5** | NOW |

**Plays named above.** *wedge snap*: The taker throws 5 m straight back to a RAM. The PLOWs stand 0.8 to 1.5 m behind the ball line in a V and move on the release. All teammates start behind the ball line. *short toss*: The thrower tosses 6 to 10 m infield to the nearest named handler slot. The thrower may not recover the ball himself and the ball cannot score until another player controls it.
*Defensive alignment (wall)*: RAMs and PLOWs stand shoulder to shoulder 5.5 m behind the restraining line; FLANKs and TAILs outside them.

**What the style should look like if it is being played** (checked before any result is read):

- advance by carry share: >= 0.8
- passes per possession: <= 1.5
- carry goal share of goals: >= 0.6
- first tackles within 30m of goal share: >= 0.5

**Strengths (reasoned, untested).**

- A carry goal is the highest-valued score on the provisional scale (5).
- Few passes, so few interceptions and drops.
- Its turnovers are mostly dead balls (second tackle), which give the opponent no running start.
- A first tackle inside 10 m of the goal plane is re-spotted at 10 m with a fresh 5 s after the snap.

**Weaknesses (reasoned, untested).**

- Two tackles end the possession; a defence that grounds the carrier early and far out leaves a long second run.
- The carrier is the Archer's first target for the whole run outside the zone.
- Lead blocking cannot be expressed in Native v0/3 at all.
- Under flat scoring a carry goal is worth no more than a throw.

**Canon check.**

- Blocks are shoulder and push contact below the neck and above the hip, no grip, never on the Keeper in his zone; tripping or tackling a player without the ball is a major foul and is not used.
- Wedge and carrier leave the zone inside 4 s if the carry stalls.
- One dribble per possession is not used.

**Against the other seven (predictions to be tested, not results).**

| Opponent | Prediction | Why |
| --- | --- | --- |
| Long Count | edge to Carry Train | Count's shell commits late and avoids contact; a wedge reaches the arc at speed and needs under 2 s inside. Ram's Wall tackles hard and a 20 s possession offers it many chances. |
| First Strike | edge to Carry Train | Strike defends with seven, so the wedge meets fewer tacklers. Ram's turnovers are mostly dead balls, which deny Strike the live gain it needs. |
| Zone Lock | edge to Carry Train | The trap needs about 5 s of hold-up. A wedge-led carry needs under 2 s from arc to goal plane, and Lock chooses not to ground a carrier in the zone at count 0. |
| Zone Waves | edge to Zone Waves | Ram's Wall is staffed by heavy RAM and PLOW profiles. A rotation every 3.5 s makes them follow attackers in and out of the zone or stand unmarked. |
| Archer's Anvil | edge to Archer's Anvil | Ram puts the whole possession on one carrier who runs 40 m or more outside the zone: the Archer's first target. As built a freeze makes him drop the ball. |
| High Press | edge to High Press | Ram wants its free first tackle close to goal. The press forces it far out, leaving a second run of 50 m or more with no tackle left. |
| Arc Siege | none | Ram's Wall stands at 24 to 28 m, right where GUNs release, but its heavy profiles are slow to close: no prediction. |

### 4. Archer's Anvil (ANVIL)

**Idea.** The field defence does not try to win the ball itself. It contains the carrier in the Archer's lane, outside the Keeper Zone, and lets the Archer spend the full 15 arrows and 5 freezes; defenders then play the loose ball and break.

**Formation.** Archer as the stopper; 3 SHADOW containing the ball, 4 RING on the arc, 3 LID on the receivers.

**Slots and what each needs.**

| Slot | Job | Needs (minimum bands) | If filled by a weaker player |
| --- | --- | --- | --- |
| ARCHER x1 | Archer (fixed role by canon). | archery accuracy 0.85 or more, awareness 0.75 or more | FAILURE out of band: the defence has given up tackling in midfield to feed the Archer; an Archer who misses leaves a carrier nobody is trying to stop. |
| SHADOW x3 | Container: keeps the carrier in front and outside the zone without tackling. | speed 0.85 or more, agility 0.80 or more, awareness 0.70 or more | FAILURE below two in band: a carrier who runs past his shadows reaches the zone, where he cannot be frozen. With two the weak side is open (graceful). |
| RING x4 | Arc guard: tackles at the arc and picks up the ball a frozen carrier drops. | tackling 0.80 or more, ball handling 0.70 or more, speed 0.70 or more | Graceful: more carriers get through the arc and fewer loose balls are picked up. |
| LID x3 | Receiver cover that stays out of the Archer's sight line. | awareness 0.80 or more, speed 0.75 or more | Graceful: receivers get free more often and the ball leaves the Archer's lane by pass. |
| KEEPER x1 | Goalkeeper (fixed role by canon). | keeper skill 0.80 or more, catching 0.70 or more | Graceful: a weaker Keeper concedes more of the throws that reach the goal; no part of the plan stops working. |

**Where each slot stands.**

| Slot | Offence | Defence | Own restart | Opponent restart | Hunt |
| --- | --- | --- | --- | --- | --- |
| SHADOW | 4 to 10 m ahead of the ball, within 12 m laterally | marks the ball carrier, goal side, at 5 to 7 m (stays between carrier and goal without contact, steering him to the middle) | 6 to 9 m behind the line, lateral -8 to 8 m | 5.5 to 7 m behind the line, lateral -8 to 8 m | The fastest SHADOW is the contestant; the others stand 7 m from the centre spot in the own half. |
| RING | 22 to 30 m from the attacked goal, bearings -50 to 50 degrees, spread evenly | 21 to 25 m from the own goal, bearings -60 to 60 degrees, spread evenly (takes down anyone who tries to enter the zone) | 0.8 to 3 m behind the line, lateral -16 to 16 m | 5.5 to 6.5 m behind the line, lateral -16 to 16 m (or the arc posts if the spot is outside 25 m) | 25 to 40 m from the own goal line, lateral -25 to 25 m (own half, outside the centre circle) |
| LID | 40 to 55 m from the own goal line, lateral -20 to 20 m (stay behind the ball against the break) | marks the receiver nearest the goal, to one side, at 5.5 to 7 m (beside the receiver, off the line from the platform to him) | 10 to 18 m behind the line, lateral -14 to 14 m | 5.5 to 9 m behind the line, lateral -18 to 18 m | 25 to 40 m from the own goal line, lateral -25 to 25 m (own half, outside the centre circle) |

Keeper and Archer hold their fixed posts (Keeper inside his zone, Archer on the platform).

**Tendencies.** The core parameters, plus every other parameter that differs from the neutral default of section 3 (differences in bold). Anything not listed is the neutral default. Tag: NOW = expressible now, COORD = needs coordination, ENGINE = needs engine work.

| Area | Parameter | Value | Tag |
| --- | --- | --- | --- |
| Ball movement | bias pass | 0 | NOW |
| Ball movement | pass len band m | 4 to 34 | ENGINE |
| Scoring method | finish pref | carry 0.3, close 0.3, mid 0.25, deep 0.15 | COORD |
| Scoring method | shot range min m | 0 | COORD |
| Scoring method | shot range max m | **28** | NOW |
| Tempo and clock | shot window s | 0 to 26 | COORD |
| Tempo and clock | must shoot remaining s | 4 | COORD |
| Tempo and clock | first action max s | **1.5** | COORD |
| Keeper Zone (attack) | entry mode | late only | COORD |
| Keeper Zone (attack) | dwell max s | 3 | COORD |
| Keeper Zone (attack) | occupancy target | 1 | COORD |
| Tackle aggression | scheme | **contain funnel** | COORD |
| Tackle aggression | bias press | **-3** | NOW |
| Tackle aggression | pressers max | **3** | COORD |
| Tackle aggression | press line m | 100 | COORD |
| Tackle aggression | commit gap m | **3** | COORD |
| Tackle aggression | takedown line m | **25** | COORD |
| Tackle aggression | contact by area | **midfield contain, arc takedown, zone takedown** | COORD |
| Tackle aggression | bias pursue | **2** | NOW |
| Archer | eagerness | **3** | NOW |
| Archer | target priority | **carrier 1, receiver near goal 0.7, other 0.3** | COORD |
| Restarts | scrim play | default | COORD |
| Restarts | snap40 play | default | COORD |
| Restarts | toss play | short toss | COORD |
| Restarts | def alignment | **ring** | COORD |
| Restarts | taker slot | **RING** | COORD |
| Hunt | contestant slot | **SHADOW** | COORD |
| Hunt | win action | tip out | COORD |
| Positioning weights | ball def | **0.6** | NOW |
| Positioning weights | goal def | **1.8** | NOW |
| Positioning weights | opp def | **0.3** | NOW |

**Plays named above.** *default*: As built in Native v0/3: the taker throws to a believed teammate 4 to 34 m from the spot. *short toss*: The thrower tosses 6 to 10 m infield to the nearest named handler slot. The thrower may not recover the ball himself and the ball cannot score until another player controls it.
*Defensive alignment (ring)*: RINGs stand on the 21 to 25 m arc if the spot is outside it, otherwise 5.5 m behind the line; SHADOWs 5.5 m behind the line opposite the likely receivers.

**What the style should look like if it is being played** (checked before any result is read):

- freezes per opp possession vs neutral ratio: >= 1.5
- opp turnovers within 3s of freeze share: >= 0.3
- takedowns beyond 25m of own goal share: <= 0.3

**Strengths (reasoned, untested).**

- Uses the one defender the offence cannot block, tackle or outrun: the arrow flies at 250 m/s.
- Each freeze removes an attacker for 5 s of a 30 s clock.
- Field defenders stay on their feet and in shape, so few defensive fouls.
- As built, a frozen ball holder drops the ball (engine behaviour, not Rulebook text: Q-TAC-2).

**Weaknesses (reasoned, untested).**

- Rests on one athlete. The roster carries two Archers at most.
- Attackers inside the zone cannot be frozen.
- A quick score arrives before the Archer has released more than a few arrows.
- Arrows may not be shot at a player outside the Archer's own half (ratified, not built in v0/3).

**Canon check.**

- The Archer shoots only legal targets: opposing field players whose team has control, outside both zones, not frozen or immune, in the Archer's own half, after the Hunt has cleared; 15 arrows and 5 freezes per opposing possession.
- No defender touches a frozen or immune player in breach of the immunity rules (a major foul); RINGs play the ball, not the man.
- Containing is not marking inside 5 m before the ball is live: at restarts SHADOWs stand 5.5 m back.

**Against the other seven (predictions to be tested, not results).**

| Opponent | Prediction | Why |
| --- | --- | --- |
| Arc Siege | edge to Archer's Anvil | Arc's throwers and feeders stand outside the zone in the Archer's half for the whole possession: up to five freezes on near-stationary targets, and as built a frozen ball holder drops the ball. |
| Carry Train | edge to Archer's Anvil | Ram puts the whole possession on one carrier who runs 40 m or more outside the zone: the Archer's first target. As built a freeze makes him drop the ball. |
| Long Count | edge to Archer's Anvil | Once Count crosses halfway it still holds the ball for 10 s or more outside the zone, the longest exposure of any style. The edge is larger in Native v0/3, which does not enforce the own-half arrow rule. |
| Zone Waves | edge to Zone Waves | Attackers inside the zone are not legal arrow targets and Wave keeps its finishers there. Anvil's shadows contain without tackling, which gives the rotation time. |
| First Strike | edge to First Strike | Strike attempts within 8 s, before the Archer has released more than a few arrows, and its long passes travel over shadows who are containing, not tackling. |
| High Press | none | Two defensive styles with plain offences. The press shortens the field, which also shortens the Archer's time: no prediction. |
| Zone Lock | none | Two defensive styles with plain offences: no prediction. |

### 5. High Press (PRESS)

**Idea.** Mark every opponent everywhere and take the ball carrier down at first reach, as far from the own goal as possible. A turnover is scrimmaged where it happens, so winning the ball in the opponent's half starts the next attack close to goal.

**Formation.** 4 HOUND on and around the ball, 4 MARK on the receivers, 2 SWEEP behind.

**Slots and what each needs.**

| Slot | Job | Needs (minimum bands) | If filled by a weaker player |
| --- | --- | --- | --- |
| SWEEP x2 | Last line: covers the space behind the press. | speed 0.85 or more, tackling 0.75 or more, awareness 0.70 or more | FAILURE with none in band: one missed tackle or one long pass is a free run at the Keeper. With one in band half the field is uncovered (graceful). |
| HOUND x4 | Ball hunter: closes at full speed and tackles at first reach. | tackling 0.85 or more, speed 0.80 or more, stamina 0.70 or more | FAILURE below two in band: two go to the ball every time; if they miss or arrive late the press is open behind them. With two or three the outlets are pressed by weaker tacklers (graceful). |
| MARK x4 | Tight marker on a receiver. | speed 0.80 or more, agility 0.75 or more, awareness 0.70 or more | Graceful: receivers get open more often and the carrier has a pass before the tackle arrives. |
| KEEPER x1 | Goalkeeper (fixed role by canon). | keeper skill 0.80 or more, catching 0.70 or more | Graceful: a weaker Keeper concedes more of the throws that reach the goal; no part of the plan stops working. |
| ARCHER x1 | Archer (fixed role by canon). | archery accuracy 0.75 or more, awareness 0.70 or more | Graceful: fewer freezes per opposing possession; no part of the plan stops working. |

**Where each slot stands.**

| Slot | Offence | Defence | Own restart | Opponent restart | Hunt |
| --- | --- | --- | --- | --- | --- |
| SWEEP | 40 to 50 m from the own goal line, 6 to 15 m off the centre line, one each side | 15 to 30 m behind the ball, 6 to 15 m to each side (always 15 m or more goal-side of the ball) | 14 to 22 m behind the line, 4 to 10 m to each side | 14 to 22 m behind the line, 4.8 to 12 m to each side | 30 to 38 m from the own goal line, 4.8 to 12 m off the centre line, one each side |
| HOUND | 3 to 12 m ahead of the ball, within 12 m laterally | marks the ball carrier, goal side, at 0 to 1.5 m (two nearest go to the ball; the others take the nearest outlets) | 0.8 to 3 m behind the line, lateral -12 to 12 m | 5.5 to 6 m behind the line, lateral -10 to 10 m | The fastest HOUND is the contestant; two others stand 7 m from the centre spot in the own half and close on the release. |
| MARK | 21 to 28 m from the attacked goal, bearings -55 to 55 degrees, spread evenly | marks the nearest unmarked opponent, ball side, at 1.5 to 3 m (denies the pass by position; never holds a player without the ball) | 0.8 to 2 m behind the line, lateral -25 to 25 m | 5.5 to 6 m behind the line, lateral -25 to 25 m | 25 to 40 m from the own goal line, lateral -25 to 25 m (own half, outside the centre circle) |

Keeper and Archer hold their fixed posts (Keeper inside his zone, Archer on the platform).

**Tendencies.** The core parameters, plus every other parameter that differs from the neutral default of section 3 (differences in bold). Anything not listed is the neutral default. Tag: NOW = expressible now, COORD = needs coordination, ENGINE = needs engine work.

| Area | Parameter | Value | Tag |
| --- | --- | --- | --- |
| Ball movement | bias pass | 0 | NOW |
| Ball movement | pass len band m | 4 to 34 | ENGINE |
| Scoring method | finish pref | carry 0.3, close 0.3, mid 0.25, deep 0.15 | COORD |
| Scoring method | bias shoot | **1** | NOW |
| Scoring method | shot range min m | 0 | COORD |
| Scoring method | shot range max m | **30** | NOW |
| Tempo and clock | shot window s | **2 to 14** | COORD |
| Tempo and clock | must shoot remaining s | 4 | COORD |
| Tempo and clock | first action max s | **2** | COORD |
| Tempo and clock | short field trigger m | **45** | COORD |
| Keeper Zone (attack) | entry mode | late only | COORD |
| Keeper Zone (attack) | dwell max s | 3 | COORD |
| Keeper Zone (attack) | occupancy target | 1 | COORD |
| Tackle aggression | scheme | **man press** | COORD |
| Tackle aggression | bias press | **5** | NOW |
| Tackle aggression | pressers max | 2 | COORD |
| Tackle aggression | press line m | 100 | COORD |
| Tackle aggression | commit gap m | **8** | COORD |
| Tackle aggression | contact by area | midfield takedown, arc takedown, zone takedown | COORD |
| Tackle aggression | bias pursue | **2** | NOW |
| Archer | eagerness | 0 | NOW |
| Archer | target priority | carrier 1, receiver near goal 0.5, other 0.3 | COORD |
| Restarts | scrim play | default | COORD |
| Restarts | snap40 play | default | COORD |
| Restarts | toss play | short toss | COORD |
| Restarts | def alignment | **man up** | COORD |
| Hunt | contestant slot | **HOUND** | COORD |
| Hunt | win action | **carry out** | COORD |
| Positioning weights | ball def | **2.5** | NOW |
| Positioning weights | goal def | **0** | NOW |
| Positioning weights | opp def | **2** | NOW |

Slot overrides: SWEEP uses press line m = 45; SWEEP uses commit gap m = 5.

**Plays named above.** *default*: As built in Native v0/3: the taker throws to a believed teammate 4 to 34 m from the spot. *short toss*: The thrower tosses 6 to 10 m infield to the nearest named handler slot. The thrower may not recover the ball himself and the ball cannot score until another player controls it.
*Defensive alignment (man up)*: Each field defender stands 5.5 m on his own side of the restraining line, opposite one attacker, and closes on the release.

**What the style should look like if it is being played** (checked before any result is read):

- tackles in opponent half share: >= 0.5
- turnover win distance from own goal m mean: >= 55
- time to first contact on carrier s median: <= 4

**Strengths (reasoned, untested).**

- Uses the two-tackle rule directly: each takedown is half of a turnover.
- A turnover high up the field is scrimmaged there, a short field for the next attack.
- Gives a slow-building opponent no time to set its shape.

**Weaknesses (reasoned, untested).**

- Ten players upfield; only two behind the ball.
- A defensive minor at tackle count 0 is a half goal (a full goal in period 4 and overtime), and tackling at first reach invites fouls.
- After the first tackle the scrimmage puts every defender back behind the ball line, so the press has to be rebuilt.
- Stamina cannot matter in Native v0/3: fatigue is off.

**Canon check.**

- Takedowns are on the ball carrier only, below the neck.
- MARKs deny by position. Holding or hooking a player without the ball is a minor foul and tackling him is a major foul; neither is used.
- At restarts every defender stands 5.5 m or more behind the restraining line (5 m marking).

**Against the other seven (predictions to be tested, not results).**

| Opponent | Prediction | Why |
| --- | --- | --- |
| Arc Siege | edge to High Press | Arc needs time to set five players on the arc and circulate. The press tackles the first receiver before the arc forms, and GUN and SCREEN profiles are not chosen for escaping pressure. |
| Carry Train | edge to High Press | Ram wants its free first tackle close to goal. The press forces it far out, leaving a second run of 50 m or more with no tackle left. |
| Long Count | edge to High Press | Count's short passes are exactly what man pressure contests, and Count may not retreat into its own zone, so the press compresses it against the arc. |
| First Strike | edge to First Strike | The press commits eight players upfield man to man. One completed long pass to a BOLT beats all of them, with two SWEEPs behind. |
| Zone Waves | none | The press may break the rotation before it forms, or its man marking may be dragged in and out of the zone: no prediction. |
| Archer's Anvil | none | Two defensive styles with plain offences. The press shortens the field, which also shortens the Archer's time: no prediction. |
| Zone Lock | none | Two defensive styles with plain offences: no prediction. |

### 6. Long Count (COUNT)

**Idea.** Keep the ball for most of the 30 s clock with short, safe passes and take one attempt in the last few seconds, so the match has fewer possessions. The ball is held in the own half, where no arrow may be shot, until 12 s remain.

**Formation.** 3 METRONOME around the ball, 4 LINK in a diamond, 3 REST behind the ball.

**Slots and what each needs.**

| Slot | Job | Needs (minimum bands) | If filled by a weaker player |
| --- | --- | --- | --- |
| METRONOME x3 | Handler: receives, protects and moves the ball without risk. | ball handling 0.85 or more, throw accuracy 0.75 or more, awareness 0.75 or more | FAILURE below two in band: a 20 s possession is 8 or more passes; with weak handlers one of them is lost. With two the third handler is a risk the others pass around (graceful). |
| LINK x4 | Receiver 8 to 15 m from the ball, always showing an open lane. | catching 0.80 or more, agility 0.70 or more, awareness 0.70 or more | Graceful: more passes are dropped or cut out, in proportion. |
| REST x3 | Stays behind the ball in attack so a lost ball meets defenders. | tackling 0.75 or more, speed 0.75 or more | Graceful: a lost ball is more often a goal against. |
| KEEPER x1 | Goalkeeper (fixed role by canon). | keeper skill 0.80 or more, catching 0.70 or more | Graceful: a weaker Keeper concedes more of the throws that reach the goal; no part of the plan stops working. |
| ARCHER x1 | Archer (fixed role by canon). | archery accuracy 0.75 or more, awareness 0.70 or more | Graceful: fewer freezes per opposing possession; no part of the plan stops working. |

**Where each slot stands.**

| Slot | Offence | Defence | Own restart | Opponent restart | Hunt |
| --- | --- | --- | --- | --- | --- |
| METRONOME | 3 to 8 m behind the ball, within 10 m laterally (the handlers stay within one short pass of the ball) | 28 to 32 m from the own goal, bearings -30 to 30 degrees, spread evenly | 7 to 9 m behind the line, lateral -6 to 6 m (takes the safe_reset throw) | 7 to 10 m behind the line, lateral -10 to 10 m | 38 to 45 m from the own goal line, 7 to 14 m off the centre line, one each side (own half, at least 7 m from the centre spot, to take a tip-out) |
| LINK | 2 m behind to 10 m ahead of the ball, 8 to 15 m to each side | 21 to 24 m from the own goal, bearings -60 to 60 degrees, spread evenly | 0.8 to 4 m behind the line, 8 to 15 m to each side | 5.5 to 6.5 m behind the line, lateral -18 to 18 m | 25 to 40 m from the own goal line, lateral -25 to 25 m (own half, outside the centre circle) |
| REST | 15 to 25 m behind the ball, within 15 m laterally | 21 to 24 m from the own goal, bearings -25 to 25 degrees, spread evenly | 15 to 25 m behind the line, lateral -15 to 15 m | 5.5 to 9 m behind the line, lateral -10 to 10 m | The fastest REST is the contestant; the others stand 12 m or more behind the centre spot. |

Keeper and Archer hold their fixed posts (Keeper inside his zone, Archer on the platform).

**Tendencies.** The core parameters, plus every other parameter that differs from the neutral default of section 3 (differences in bold). Anything not listed is the neutral default. Tag: NOW = expressible now, COORD = needs coordination, ENGINE = needs engine work.

| Area | Parameter | Value | Tag |
| --- | --- | --- | --- |
| Ball movement | bias pass | **3** | NOW |
| Ball movement | pass min clearance m | **4** | NOW |
| Ball movement | pass len band m | **6 to 15** | ENGINE |
| Ball movement | touch time max s | **3** | COORD |
| Scoring method | finish pref | **carry 0.1, close 0.3, mid 0.3, deep 0.3** | COORD |
| Scoring method | bias shoot | **-3** | NOW |
| Scoring method | shot range min m | 0 | COORD |
| Scoring method | shot range max m | **24** | NOW |
| Tempo and clock | shot window s | **22 to 27** | COORD |
| Tempo and clock | must shoot remaining s | **3** | COORD |
| Tempo and clock | snap delay s | **leading 8, otherwise 2** | COORD |
| Tempo and clock | hold own half until remaining s | **12** | COORD |
| Carrier in contact | contact response | **run through 0.1, dodge 0.7, brace 0.2** | COORD |
| Keeper Zone (attack) | entry mode | late only | COORD |
| Keeper Zone (attack) | dwell max s | 3 | COORD |
| Keeper Zone (attack) | occupancy target | 1 | COORD |
| Tackle aggression | scheme | **deep shell** | COORD |
| Tackle aggression | bias press | **-1** | NOW |
| Tackle aggression | pressers max | **1** | COORD |
| Tackle aggression | press line m | **30** | COORD |
| Tackle aggression | commit gap m | **4** | COORD |
| Tackle aggression | takedown line m | **30** | COORD |
| Tackle aggression | contact by area | **midfield contain, arc takedown, zone takedown** | COORD |
| Archer | eagerness | 0 | NOW |
| Archer | target priority | carrier 1, receiver near goal 0.5, other 0.3 | COORD |
| Restarts | scrim play | **safe reset** | COORD |
| Restarts | snap40 play | **safe reset** | COORD |
| Restarts | toss play | short toss | COORD |
| Restarts | def alignment | shell | COORD |
| Restarts | taker slot | **METRONOME** | COORD |
| Hunt | contestant slot | **REST** | COORD |
| Hunt | win action | tip out | COORD |
| Positioning weights | ball def | **0.6** | NOW |
| Positioning weights | goal att | **0.2** | NOW |
| Positioning weights | goal def | **2** | NOW |
| Positioning weights | spread | **2** | NOW |
| Positioning weights | opp att | **1.5** | NOW |
| Positioning weights | lane | **2** | NOW |

**Plays named above.** *safe reset*: The taker throws 8 m back to a METRONOME and the team re-forms its passing diamond. The taker waits tempo.snap_delay_s inside the legal window first. *short toss*: The thrower tosses 6 to 10 m infield to the nearest named handler slot. The thrower may not recover the ball himself and the ball cannot score until another player controls it.
*Defensive alignment (shell)*: All field defenders stand 5.5 m or more on their own side of the restraining line, between ball and goal.

**What the style should look like if it is being played** (checked before any result is read):

- own possession duration s mean unturned: >= 20
- passes per possession: >= 5
- shots with 8s or less left share: >= 0.6
- live ball turnovers per possession: <= 0.15

**Strengths (reasoned, untested).**

- Fewer possessions in the match; a lead is harder to overturn.
- No legal arrow target while the ball and the team are in their own half (ratified rule).
- Three players always behind the ball.

**Weaknesses (reasoned, untested).**

- Gains nothing per possession by itself: it changes how many possessions there are, not what each is worth.
- One attempt per possession, taken against a set defence with the clock nearly out.
- The longest exposure to the Archer of any style once it crosses halfway.
- May not retreat into its own Keeper Zone (ZR-C, ZR-T), so pressure can pin it at the arc.
- Play-clock expiry is a turnover.

**Canon check.**

- The attempt is released before the 30 s clock expires; a throw released as the clock expires counts.
- The snap is always inside the 10 s window. Waiting 8 s inside it is assumed legal; "delay of game" is a minor foul after a warning and its boundary is not stated (PLACEHOLDER, Q-TAC-4).
- No pass or carry goes back into the own Keeper Zone; a ball in the own zone leaves within 5 s (ZR-1).

**Against the other seven (predictions to be tested, not results).**

| Opponent | Prediction | Why |
| --- | --- | --- |
| First Strike | edge to Long Count | Count gives up few live turnovers and keeps three REST players behind the ball, so the BOLTs waiting high receive little; and Count attacks a seven-player defence. |
| Arc Siege | edge to Arc Siege | Count's shell waits on the arc and commits late (4 m). In-band GUNs release from 21 to 24 m over it, and Count's long possessions do not lower the quality of Arc's attempts. |
| Carry Train | edge to Carry Train | Count's shell commits late and avoids contact; a wedge reaches the arc at speed and needs under 2 s inside. Ram's Wall tackles hard and a 20 s possession offers it many chances. |
| Archer's Anvil | edge to Archer's Anvil | Once Count crosses halfway it still holds the ball for 10 s or more outside the zone, the longest exposure of any style. The edge is larger in Native v0/3, which does not enforce the own-half arrow rule. |
| High Press | edge to High Press | Count's short passes are exactly what man pressure contests, and Count may not retreat into its own zone, so the press compresses it against the arc. |
| Zone Lock | edge to Zone Lock | Count attempts with 3 to 8 s left. A hold-up at the door squeezes it between the zone limit and the play clock with no time to recycle. |
| Zone Waves | none | Count's shell must follow attackers into the zone or leave them free; whether it copes is not something reasoning settles. |

### 7. First Strike (STRIKE)

**Idea.** Score within 8 s of gaining the ball, before the defence is set and before the Archer has released more than a few arrows. Three sprinters stay high even in defence, and every restart and every gain of possession starts with a long pass to one of them.

**Formation.** 3 BOLT high, 2 CANNON as long passers, 5 HALF who defend seven-strong with the CANNONs.

**Slots and what each needs.**

| Slot | Job | Needs (minimum bands) | If filled by a weaker player |
| --- | --- | --- | --- |
| BOLT x3 | Sprinter: stays high and runs onto long passes. | speed 0.90 or more, catching 0.75 or more | FAILURE below two in band: a runner who is caught from behind, or who drops a fast long pass, turns the plan into three players missing from the defence. With two one channel is unused (graceful). |
| CANNON x2 | Long passer: first outlet on every gain and the thrower on every restart. | throw power 0.85 or more, throw accuracy 0.80 or more | FAILURE with none in band: a long pass that is slow or off line is intercepted or run down. With one in band every break starts from the same player (graceful). |
| HALF x5 | Defender: holds the arc with six others. | tackling 0.80 or more, speed 0.70 or more, awareness 0.70 or more | Graceful: a seven-player defence concedes more, in proportion. |
| KEEPER x1 | Goalkeeper (fixed role by canon). | keeper skill 0.80 or more, catching 0.70 or more, throw power 0.80 or more | Graceful: without the throw power the Keeper starts breaks with a short pass to a CANNON; the break starts later. |
| ARCHER x1 | Archer (fixed role by canon). | archery accuracy 0.75 or more, awareness 0.70 or more | Graceful: fewer freezes per opposing possession; no part of the plan stops working. |

**Where each slot stands.**

| Slot | Offence | Defence | Own restart | Opponent restart | Hunt |
| --- | --- | --- | --- | --- | --- |
| BOLT | 25 to 35 m from the attacked goal, bearings -50 to 50 degrees, spread evenly (the point each BOLT sprints to on a gain) | 45 to 60 m from the own goal line, lateral -25 to 25 m (stays high; legal, there is no offside in live play) | 0.8 to 1.5 m behind the line, lateral -22 to 22 m (on the ball line: wide, centre, wide) | 5.5 to 12 m behind the line, lateral -25 to 25 m (the shallowest legal position) | The fastest BOLT is the contestant and tips the ball out to a CANNON; the other two stand 7 m from the centre spot in the own half and sprint on the release. |
| CANNON | 3 to 8 m behind the ball, 3.2 to 8 m to each side | 26 to 32 m from the own goal, 8 to 20 degrees off centre, one each side (in the passing lanes; first outlet on a gain) | 6 to 8 m behind the line, 1.6 to 4 m to each side (takes the go_routes throw) | 7 to 10 m behind the line, 3.2 to 8 m to each side | 38 to 45 m from the own goal line, 7 to 14 m off the centre line, one each side (own half, at least 7 m from the centre spot, to take a tip-out) |
| HALF | 5 to 15 m behind the ball, within 18 m laterally | 21 to 26 m from the own goal, bearings -60 to 60 degrees, spread evenly | 6 to 14 m behind the line, lateral -18 to 18 m | 5.5 to 7 m behind the line, lateral -18 to 18 m | 25 to 40 m from the own goal line, lateral -25 to 25 m (own half, outside the centre circle) |

Keeper and Archer hold their fixed posts (Keeper inside his zone, Archer on the platform).

**Tendencies.** The core parameters, plus every other parameter that differs from the neutral default of section 3 (differences in bold). Anything not listed is the neutral default. Tag: NOW = expressible now, COORD = needs coordination, ENGINE = needs engine work.

| Area | Parameter | Value | Tag |
| --- | --- | --- | --- |
| Ball movement | bias pass | **2** | NOW |
| Ball movement | pass len band m | **20 to 50** | ENGINE |
| Ball movement | touch time max s | **2** | COORD |
| Ball movement | dribble use | **advance** | COORD |
| Scoring method | finish pref | **carry 0.35, close 0.35, mid 0.2, deep 0.1** | COORD |
| Scoring method | bias shoot | **2** | NOW |
| Scoring method | shot range min m | 0 | COORD |
| Scoring method | shot range max m | **30** | NOW |
| Tempo and clock | shot window s | **2 to 8** | COORD |
| Tempo and clock | must shoot remaining s | 4 | COORD |
| Tempo and clock | first action max s | **1.5** | COORD |
| Carrier in contact | contact response | **run through 0.2, dodge 0.7, brace 0.1** | COORD |
| Keeper Zone (attack) | entry mode | **drive** | COORD |
| Keeper Zone (attack) | dwell max s | 3 | COORD |
| Keeper Zone (attack) | occupancy target | **2** | COORD |
| Tackle aggression | scheme | **lane gamble** | COORD |
| Tackle aggression | bias press | **1** | NOW |
| Tackle aggression | pressers max | 2 | COORD |
| Tackle aggression | press line m | **40** | COORD |
| Tackle aggression | commit gap m | **7** | COORD |
| Tackle aggression | contact by area | midfield takedown, arc takedown, zone takedown | COORD |
| Tackle aggression | bias pursue | **2** | NOW |
| Archer | eagerness | 0 | NOW |
| Archer | target priority | carrier 1, receiver near goal 0.5, other 0.3 | COORD |
| Keeper | distribution | **long outlet** | COORD |
| Restarts | scrim play | **go routes** | COORD |
| Restarts | snap40 play | **go routes** | COORD |
| Restarts | toss play | **line toss** | COORD |
| Restarts | def alignment | shell | COORD |
| Restarts | taker slot | **CANNON** | COORD |
| Hunt | contestant slot | **BOLT** | COORD |
| Hunt | win action | tip out | COORD |
| Positioning weights | ball att | **-0.5** | NOW |
| Positioning weights | goal att | **3** | NOW |
| Positioning weights | goal def | **-0.5** | NOW |
| Positioning weights | spread | **1.5** | NOW |

**Plays named above.** *go routes*: The taker throws 7 m back to a CANNON. BOLTs stand on the ball line at wide, centre, wide and sprint on the release; the CANNON throws long into the space ahead of one of them. *line toss*: The thrower tosses up the boundary to a BOLT running into space. Same toss-in limits.
*Defensive alignment (shell)*: All field defenders stand 5.5 m or more on their own side of the restraining line, between ball and goal.

**What the style should look like if it is being played** (checked before any result is read):

- own shots within 8s of gain share: >= 0.5
- passes 30m plus per possession: >= 0.5
- bolt distance from own goal in defence m mean: >= 45

**Strengths (reasoned, untested).**

- The defence is not set and the Archer has had little time.
- At a 40 m scrimmage after a score the two teams start 20 m apart, a clear runway for a sprinter.
- A long pass covers the field faster than any runner.

**Weaknesses (reasoned, untested).**

- Defends with seven.
- Needs live turnovers; an opponent whose possessions end in dead balls gives it none.
- A fast long pass is hard to catch; the attempt is often a turnover.
- Long passes and chosen release speed cannot be expressed in Native v0/3.

**Canon check.**

- Staying high in live play is legal: offside is judged only at scrimmages, where BOLTs stand on their own side of the ball line.
- At a 40 m scrimmage BOLTs start at or behind their own 40 m line.
- One dribble per possession: a BOLT may throw the ball ahead of himself once and replay it; a second is a minor foul and is not used.
- A tossed ball cannot score until another player controls it.

**Against the other seven (predictions to be tested, not results).**

| Opponent | Prediction | Why |
| --- | --- | --- |
| Archer's Anvil | edge to First Strike | Strike attempts within 8 s, before the Archer has released more than a few arrows, and its long passes travel over shadows who are containing, not tackling. |
| High Press | edge to First Strike | The press commits eight players upfield man to man. One completed long pass to a BOLT beats all of them, with two SWEEPs behind. |
| Carry Train | edge to Carry Train | Strike defends with seven, so the wedge meets fewer tacklers. Ram's turnovers are mostly dead balls, which deny Strike the live gain it needs. |
| Long Count | edge to Long Count | Count gives up few live turnovers and keeps three REST players behind the ball, so the BOLTs waiting high receive little; and Count attacks a seven-player defence. |
| Zone Lock | edge to Zone Lock | Lock does not press upfield, so its defenders are at the arc when the long pass arrives. The break ends in a zone entry against a set trap. |
| Arc Siege | none | Arc attacks ten against seven, but every saved throw is a live ball with BOLTs already high. Which is larger is the question. |
| Zone Waves | none | Wave commits five or six attackers deep, but many of its turnovers are dead balls (residence): no prediction. |

### 8. Zone Lock (LOCK)

**Idea.** Turn the attacker's 5 s zone limit into the defence's weapon. Leave the middle of the arc open, and when the carrier enters, wrap him and hold him up inside the zone without grounding him, so his 5 s runs out and the ball turns over without a tackle being counted.

**Formation.** 2 CLAMP at the door, 4 GATE on the rest of the arc, 4 DENY on the outlets.

**Slots and what each needs.**

| Slot | Job | Needs (minimum bands) | If filled by a weaker player |
| --- | --- | --- | --- |
| CLAMP x2 | Door jamb: wraps the carrier as he enters and holds him up inside the zone. | strength 0.85 or more, tackling 0.80 or more, mass 230 kg or more | FAILURE below two in band: a carrier who breaks the wrap is 20 m from goal with no one in front of him but the Keeper. There is no graceful case: the door needs both jambs. |
| GATE x4 | Arc guard away from the door. | tackling 0.80 or more, strength 0.70 or more, speed 0.70 or more | Graceful: more entries are made away from the door, where no hold-up is waiting. |
| DENY x4 | Outlet cover: takes away the pass out of the zone. | speed 0.80 or more, awareness 0.75 or more, agility 0.70 or more | Graceful: the held-up carrier finds a pass out more often and the 5 s is not used up. |
| KEEPER x1 | Goalkeeper (fixed role by canon). | keeper skill 0.80 or more, catching 0.70 or more | Graceful: a weaker Keeper concedes more of the throws that reach the goal; no part of the plan stops working. |
| ARCHER x1 | Archer (fixed role by canon). | archery accuracy 0.75 or more, awareness 0.70 or more | Graceful: fewer freezes per opposing possession; no part of the plan stops working. |

**Where each slot stands.**

| Slot | Offence | Defence | Own restart | Opponent restart | Hunt |
| --- | --- | --- | --- | --- | --- |
| CLAMP | 21 to 25 m from the attacked goal, 8 to 20 degrees off centre, one each side | 20.5 to 22 m from the own goal, 9 to 14 degrees off centre, one each side (either side of the open lane; closes on the carrier as he enters) | 0.8 to 2 m behind the line, 1.6 to 4 m to each side | 5.5 to 6.5 m behind the line, 2 to 5 m to each side | 25 to 40 m from the own goal line, lateral -25 to 25 m (own half, outside the centre circle) |
| GATE | 22 to 30 m from the attacked goal, bearings -55 to 55 degrees, spread evenly | 20.5 to 23 m from the own goal, 25 to 60 degrees off centre, one each side (two each side; shuts the way out behind a carrier who has entered) | 0.8 to 3 m behind the line, lateral -16 to 16 m | 5.5 to 6.5 m behind the line, lateral -16 to 16 m | The fastest GATE is the contestant; the others stand in the own half 12 m or more behind the centre spot. |
| DENY | 10 m behind to 6 m ahead of the ball, within 18 m laterally | marks the nearest unmarked opponent, ball side, at 1.5 to 3 m (on the receivers outside the arc, 24 to 34 m from the own goal) | 6 to 12 m behind the line, lateral -18 to 18 m | 5.5 to 9 m behind the line, lateral -20 to 20 m | 38 to 45 m from the own goal line, 7 to 14 m off the centre line, one each side (own half, at least 7 m from the centre spot, to take a tip-out) |

Keeper and Archer hold their fixed posts (Keeper inside his zone, Archer on the platform).

**Tendencies.** The core parameters, plus every other parameter that differs from the neutral default of section 3 (differences in bold). Anything not listed is the neutral default. Tag: NOW = expressible now, COORD = needs coordination, ENGINE = needs engine work.

| Area | Parameter | Value | Tag |
| --- | --- | --- | --- |
| Ball movement | bias pass | 0 | NOW |
| Ball movement | pass len band m | 4 to 34 | ENGINE |
| Scoring method | finish pref | carry 0.3, close 0.3, mid 0.25, deep 0.15 | COORD |
| Scoring method | shot range min m | 0 | COORD |
| Scoring method | shot range max m | 32 | NOW |
| Tempo and clock | shot window s | 0 to 26 | COORD |
| Tempo and clock | must shoot remaining s | 4 | COORD |
| Keeper Zone (attack) | entry mode | late only | COORD |
| Keeper Zone (attack) | dwell max s | 3 | COORD |
| Keeper Zone (attack) | occupancy target | 1 | COORD |
| Tackle aggression | scheme | **zone trap** | COORD |
| Tackle aggression | bias press | **-1** | NOW |
| Tackle aggression | pressers max | 2 | COORD |
| Tackle aggression | press line m | **26** | COORD |
| Tackle aggression | commit gap m | **5** | COORD |
| Tackle aggression | takedown line m | **26** | COORD |
| Tackle aggression | contact by area | **midfield contain, arc wrap, zone wrap** | COORD |
| Tackle aggression | contact at count1 | **takedown** | ENGINE |
| Archer | eagerness | 0 | NOW |
| Archer | target priority | carrier 1, receiver near goal 0.5, other 0.3 | COORD |
| Restarts | scrim play | default | COORD |
| Restarts | snap40 play | default | COORD |
| Restarts | toss play | short toss | COORD |
| Restarts | def alignment | **gate** | COORD |
| Restarts | taker slot | **DENY** | COORD |
| Hunt | contestant slot | **GATE** | COORD |
| Hunt | win action | tip out | COORD |
| Positioning weights | ball def | **1** | NOW |
| Positioning weights | goal def | **2.5** | NOW |
| Positioning weights | opp def | **1.5** | NOW |

Slot overrides: CLAMP uses holdup drive = into zone.

**Plays named above.** *default*: As built in Native v0/3: the taker throws to a believed teammate 4 to 34 m from the spot. *short toss*: The thrower tosses 6 to 10 m infield to the nearest named handler slot. The thrower may not recover the ball himself and the ball cannot score until another player controls it.
*Defensive alignment (gate)*: CLAMPs and GATEs take their arc posts if the spot is outside the zone, otherwise 5.5 m behind the line; DENYs opposite the likely receivers at 5.5 m.

**What the style should look like if it is being played** (checked before any result is read):

- opp zone residence turnovers per zone entry vs neutral ratio: >= 3
- wrap share of contact in own zone at count0: >= 0.8
- takedowns in own zone at count0 share: <= 0.1

**Strengths (reasoned, untested).**

- A residence turnover costs the defence no tackle and gives the offence no scrimmage.
- A takedown inside the zone at count 0 would hand the offence a scrimmage near goal with a fresh 5 s; this plan never gives that.
- Defenders stay near their goal; little space behind them.

**Weaknesses (reasoned, untested).**

- Does nothing to a team that does not enter the zone.
- The carrier needs under 2 s from arc to goal plane; the hold-up must work at once.
- Whether a wrap can hold a carrier for seconds in the engine is unmeasured.
- The count-1 switch to takedown needs a tackle count the athlete cannot see in Native v0/3.

**Canon check.**

- A wrap is legal on the ball carrier from below the neck down.
- Hands go on the body, not the ball: two opponents holding the ball for 1 s is a held ball, play stops and the zone clock resets.
- Defenders wait outside the zone (20.5 m or more) and enter only with the carrier, within 5 m of him.
- No contact on a Keeper in his zone; the plan applies to the ball carrier only.

**Against the other seven (predictions to be tested, not results).**

| Opponent | Prediction | Why |
| --- | --- | --- |
| Zone Waves | edge to Zone Lock | Wave enters the zone by design with 1.5 s of margin. A hold-up of 1.5 s turns a visit into a residence turnover. |
| Long Count | edge to Zone Lock | Count attempts with 3 to 8 s left. A hold-up at the door squeezes it between the zone limit and the play clock with no time to recycle. |
| First Strike | edge to Zone Lock | Lock does not press upfield, so its defenders are at the arc when the long pass arrives. The break ends in a zone entry against a set trap. |
| Arc Siege | edge to Arc Siege | Lock's trap needs a zone entry and Arc does not enter. Lock contains outside its takedown line, so GUNs release unhurried. |
| Carry Train | edge to Carry Train | The trap needs about 5 s of hold-up. A wedge-led carry needs under 2 s from arc to goal plane, and Lock chooses not to ground a carrier in the zone at count 0. |
| Archer's Anvil | none | Two defensive styles with plain offences: no prediction. |
| High Press | none | Two defensive styles with plain offences: no prediction. |


## 5. Prediction matrix
`+` row is predicted to have the edge over column, `-` the reverse, `?` no prediction. 19 pairings carry a prediction and 9 do not. A prediction is a reason to expect a sign, written before any match. The test plan counts how many hold.

| Row against column | ARC | WAVE | RAM | ANVIL | PRESS | COUNT | STRIKE | LOCK |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARC | . | ? | ? | - | - | + | ? | + |
| WAVE | ? | . | + | + | ? | ? | ? | - |
| RAM | ? | - | . | - | - | + | + | + |
| ANVIL | + | - | + | . | ? | + | - | ? |
| PRESS | + | ? | + | ? | . | + | - | ? |
| COUNT | - | ? | - | - | - | . | + | - |
| STRIKE | ? | ? | - | + | + | - | . | - |
| LOCK | - | + | - | ? | ? | + | + | . |

Reading it as a whole says something about the reasoning, not about the styles. On paper Long Count has one predicted edge and five predicted deficits, because slowing the game changes how many possessions there are and not what each is worth; an equal-roster round-robin is the least favourable test for it. Nothing here says the eight are evenly matched, and nothing was adjusted to make them so.

## 6. Parameter catalogue and classification
61 parameters. 17 are EXPRESSIBLE NOW, 36 NEED COORDINATION, 8 NEED ENGINE WORK.

- **EXPRESSIBLE NOW.** Native v0/3 can run it today with no code change. In practice the parameter is one of the 16 team-wide `PolicyParams` fields (or a behaviour that is already the only one built), with one value for every teammate.
- **NEEDS COORDINATION.** The engine mechanics, intent kinds and view fields exist, but the athlete does not hold the value: it differs by slot, replaces a constant in cognition, or works only if teammates hold the same plan. It needs the pre-match playbook of `TACTIC_INTERFACE.md` and cognition that reads it. No physics or rules change.
- **NEEDS ENGINE WORK.** The engine, port or rules layer lacks something: ratings and bodies per athlete, athlete-chosen release speed, voluntary off-ball contact, or a public signal missing from the view.

| Parameter | Meaning | Range | Class | Reason |
| --- | --- | --- | --- | --- |
| `carrier.bias_pass` | Added to the value of every pass option. | -6 to 6 | EXPRESSIBLE NOW | Is PolicyParams.bias_pass. |
| `carrier.bias_shoot` | Added to the value of the shoot option. | -6 to 6 | EXPRESSIBLE NOW | Is PolicyParams.bias_shoot. |
| `carrier.pass_min_clearance_m` | Pass options whose believed lane clearance is below this are dropped. | 0 to 6 m | EXPRESSIBLE NOW | Is PolicyParams.pass_min_clearance. |
| `carrier.shot_range_max_m` | Largest believed distance to goal at which a throw at goal is an option. | 8 to 60 m | EXPRESSIBLE NOW | Is PolicyParams.shot_range. |
| `carrier.shot_range_min_m` | Smallest believed distance to goal at which a throw at goal is an option. | 0 to 40 m | NEEDS COORDINATION | v0/3 cognition has no minimum-distance filter on the shoot option; the playbook value must be read in cognition. |
| `carrier.finish_pref` | Preference weights over scoring methods: carry in, close throw (under 10 m), mid throw (10 to 20 m), deep throw (20 m or more). | carry, close, mid, deep: each 0 to 1, sum 1 | NEEDS COORDINATION | v0/3 values one shoot option and one carry option with no distance bands; the bands need playbook weights in cognition. Release distance is the athlete's own believed distance. |
| `carrier.shot_speed_frac` | Release speed of a throw at goal as a fraction of the thrower's own maximum. | 0.3 to 1 | NEEDS ENGINE WORK | v0/3 releases every pass and shot at min(27, max) m/s and 1.6 m height (R10 F-4). Athlete-chosen release speed and a per-athlete maximum from throw_power are engine and attribute-step work. |
| `carrier.pass_len_band_m` | Preferred believed pass length. | 4 to 60 m | NEEDS ENGINE WORK | v0/3 pass options are fixed to a believed 4 to 34 m at 27 m/s. Bands beyond 34 m, or needing a faster ball, depend on athlete-chosen release speed. A band inside 4 to 34 m would need only the playbook. |
| `carrier.touch_time_max_s` | Longest time a ball holder outside the Keeper Zone keeps the ball before passing or throwing. 30 means no limit. | 0.5 to 30 s | NEEDS COORDINATION | v0/3 has no own-possession timer. Needs an own-action memory of when I gained the ball (own knowledge) and a playbook threshold. |
| `carrier.contact_response` | Preference weights among run through, dodge and brace when a tackler is believed to be arriving. | run_through, dodge, brace: each 0 to 1, sum 1 | NEEDS COORDINATION | The three intents exist in v0/3 but are chosen from constants (THREAT_HORIZON_S, DODGE_MIN_S, BRACE_LOAD). The playbook must replace them. |
| `carrier.first_tackle_bank_m` | While the tackle count is 0, the carrier accepts contact only inside this distance of the attacked goal; farther out he prefers to dodge or pass. 100 means anywhere. | 0 to 100 m | NEEDS ENGINE WORK | Needs the public tackle count in the athlete's view. v0/3 Signals carry no tackle count. |
| `carrier.dribble_use` | When the one dribble per possession is used. | none / escape / advance | NEEDS COORDINATION | The dribble intent exists; v0/3 uses it only when no teammate is believed visible. A playbook rule must choose it. |
| `tempo.shot_window_s` | Seconds into the 30 s play clock in which the team prefers to take its scoring attempt. | 0 to 30 s | NEEDS COORDINATION | The possession clock is a public signal in the view. v0/3 has only a fixed +5 shoot value in the first 5 s. Needs playbook values. |
| `tempo.must_shoot_remaining_s` | With this much play clock left, the ball holder attempts to score from where he is. | 0 to 10 s | NEEDS COORDINATION | Same public clock; no such rule in v0/3 cognition. |
| `tempo.snap_delay_s` | Seconds the snapper waits inside the legal 10 s snap window, when leading and otherwise. | leading, otherwise: each 0 to 8 | NEEDS COORDINATION | v0/3 releases as soon as a legal throw exists. Score is public. Assumes waiting inside the legal window is not delay of game (Q-TAC-4). |
| `tempo.hold_own_half_until_remaining_s` | The team keeps the ball in its own half until this much play clock remains. 30 means it does not hold. | 0 to 30 s | NEEDS COORDINATION | A position and hold rule from the public clock; needs the playbook. Its purpose (no legal arrow target outside the Archer's own half) rests on a ratified rule that v0/3 does not enforce. |
| `off.first_action_max_s` | After gaining a live ball, longest time before the first forward pass or carry. | 0.5 to 10 s | NEEDS COORDINATION | Needs an own-action memory of when I gained the ball and a playbook threshold. |
| `off.short_field_trigger_m` | If possession is gained within this distance of the attacked goal, the team attempts to score at once. 0 means never. | 0 to 100 m | NEEDS COORDINATION | Own believed position and a playbook threshold. |
| `pos.ball_att` | In possession: pull toward the believed ball. | -3 to 3 | EXPRESSIBLE NOW | Is PolicyParams.pos_ball_att. |
| `pos.ball_def` | Out of possession: pull toward the believed ball. | -3 to 3 | EXPRESSIBLE NOW | Is PolicyParams.pos_ball_def. |
| `pos.goal_att` | In possession: pull toward the attacked goal. | -3 to 3 | EXPRESSIBLE NOW | Is PolicyParams.pos_goal_att. |
| `pos.goal_def` | Out of possession: pull toward own goal. | -3 to 3 | EXPRESSIBLE NOW | Is PolicyParams.pos_goal_def. |
| `pos.spread` | Prefer distance from the nearest believed teammate. | -3 to 3 | EXPRESSIBLE NOW | Is PolicyParams.pos_spread. |
| `pos.opp_att` | In possession: prefer distance from the nearest believed opponent. | -3 to 3 | EXPRESSIBLE NOW | Is PolicyParams.pos_opp_att. |
| `pos.opp_def` | Out of possession: prefer closeness to the nearest believed opponent. | -3 to 3 | EXPRESSIBLE NOW | Is PolicyParams.pos_opp_def. |
| `pos.lane` | In possession: prefer an open believed lane from the carrier. | -3 to 3 | EXPRESSIBLE NOW | Is PolicyParams.pos_lane. |
| `pos.edge_zone` | Penalty for standing near a field edge or inside either Keeper Zone. | 0 to 3 | EXPRESSIBLE NOW | Is PolicyParams.pos_edge_zone. |
| `zone.entry_mode` | How attackers use the attacked Keeper Zone. | avoid / rebound_only / late_only / drive / rotation | NEEDS COORDINATION | v0/3 has one behaviour (a position penalty for zones). A mode needs the playbook. |
| `zone.dwell_max_s` | An attacker leaves the zone when his own residence reaches this. Canon limit is 5 s. | 0 to 4.5 s | NEEDS COORDINATION | v0/3 leaves at a fixed 3.0 s. Own residence time is already in the view; the playbook must supply the threshold. |
| `zone.occupancy_target` | Number of attackers the team tries to keep inside the zone in settled offence. | 0 to 6 | NEEDS COORDINATION | Each athlete can count believed teammates inside, but who goes in next is a shared arrangement held in the playbook. |
| `zone.min_outside_s` | Self-imposed minimum time outside before the same attacker re-enters. | 0 to 5 s | NEEDS COORDINATION | Own knowledge and a playbook value. Canon states no minimum time outside (Q-TAC-1). |
| `zone.entry_stagger_s` | Offset between the entries of paired attackers in a rotation. | 0 to 5 s | NEEDS COORDINATION | A timing agreement between teammates with no live channel: each acts on his own belief of the partner leaving. |
| `block.wedge` | Lead blockers make legal off-ball contact (shoulder, push; no grip) ahead of the carrier. | boolean | NEEDS ENGINE WORK | Native has no voluntary off-ball contact intents (Q-HAND-1). Without them the wedge is only bodies in the way. |
| `screen.arrow_screen` | A screener stands between the Archer platform and a paired thrower. | boolean | NEEDS COORDINATION | Position only, held in the playbook and paired with one teammate. Rests on arrow-body collision, which the engine has. Effect unmeasured. |
| `def.bias_press` | Added to the value of closing on the believed carrier. | -6 to 6 | EXPRESSIBLE NOW | Is PolicyParams.bias_press. |
| `def.bias_pursue` | Added to the value of pursuing a loose ball. | -6 to 6 | EXPRESSIBLE NOW | Is PolicyParams.bias_pursue. |
| `def.scheme` | Shape of the defence. | arc_shell / man / wall / contain_funnel / man_press / deep_shell / lane_gamble / zone_trap | NEEDS COORDINATION | A scheme is the set of slot anchors and marking rules below; it exists only if every teammate holds the same chart. |
| `def.pressers_max` | How many defenders close on the carrier at once. | 1 to 4 | NEEDS COORDINATION | v0/3 lets the two believed-nearest press (a constant). |
| `def.press_line_m` | The carrier is engaged only when he is within this distance of the defending goal. 100 means everywhere. | 0 to 100 m | NEEDS COORDINATION | Own believed positions and a playbook value; no such line in v0/3. |
| `def.commit_gap_m` | Believed gap at which a pressing defender commits to contact. | 1 to 10 m | NEEDS COORDINATION | TACKLE_COMMIT_M = 6.0 is a constant in v0/3. |
| `def.contain_gap_m` | Gap a containing defender keeps to the carrier. | 1 to 10 m | NEEDS COORDINATION | Containing without contact is a position choice; needs the playbook. |
| `def.takedown_line_m` | A takedown is chosen only when the carrier is within this distance of the defending goal. 100 means anywhere. | 0 to 100 m | NEEDS COORDINATION | Own believed positions and a playbook value. |
| `def.contact_by_area` | Contact a defender chooses by area: beyond the takedown line (midfield), inside it but outside the zone (arc), inside the own Keeper Zone (zone). | midfield, arc, zone: contain / wrap / takedown | NEEDS COORDINATION | Wrap and takedown intents exist in v0/3; the area is the athlete's own believed position. |
| `def.contact_at_count1` | Contact chosen once the offence has used its first tackle. | same_as_area / takedown | NEEDS ENGINE WORK | Needs the public tackle count in the athlete's view. v0/3 Signals carry none. |
| `def.holdup_drive` | Direction a wrapping defender drives the carrier. | none / into_zone | NEEDS COORDINATION | The aim of a wrapping defender is his own intent. Whether a wrap can move or hold a carrier is engine physics as built, unmeasured. |
| `archer.eagerness` | Added to the value of every draw-and-release option. | -3 to 3 | EXPRESSIBLE NOW | Is PolicyParams.archer_eager. |
| `archer.target_priority` | Relative value of legal targets: the believed carrier, the receiver nearest the goal, any other legal attacker. | carrier, receiver_near_goal, other: each 0 to 1 | NEEDS COORDINATION | v0/3 uses constants (carrier 3.0, others 1.6 minus 0.04 per metre from the ball). The Archer is one athlete, so no teammate is involved. |
| `keeper.depth_m` | How far off the goal line the Keeper sets. | 1 to 8 m | NEEDS COORDINATION | v0/3 Keeper depth is clamp(0.25 x distance, 1, 4), a constant rule. |
| `keeper.distribution` | What the Keeper does with a secured ball. | short / long_outlet | NEEDS COORDINATION | Target choice needs the slot chart. A long outlet beyond 34 m also depends on carrier.pass_len_band_m. |
| `restart.scrim_play` | Set play at a Contact Scrimmage with the ball. | default / quick_swing / wedge_snap / zone_stack / safe_reset / go_routes | NEEDS COORDINATION | v0/3 throws to a believed teammate 4 to 34 m away and two teammates make themselves throwable. A named play is a shared arrangement. |
| `restart.snap40_play` | Set play at the 40 m scrimmage after conceding. | default / quick_swing / wedge_snap / zone_stack / safe_reset / go_routes | NEEDS COORDINATION | As restart.scrim_play. |
| `restart.toss_play` | Set play at a toss-in. | short_toss / line_toss | NEEDS COORDINATION | As restart.scrim_play. A tossed ball cannot score until another player controls it. |
| `restart.def_alignment` | Defensive alignment at an opponent restart. | shell / man_up / ring / gate / wall | NEEDS COORDINATION | Slot anchors relative to the restraining line; shared chart. |
| `restart.taker_slot` | Slot that prefers to take 40 m scrimmages and toss-ins. The snapper after a tackle is fixed by rule. | slot_or_nearest | NEEDS COORDINATION | v0/3 claim goes to the believed-nearest teammate. A slot preference needs the others to hold back. |
| `hunt.contestant_slot` | Slot whose holder claims the Hunt. | slot | NEEDS COORDINATION | v0/3 admits a claim from any field player. Naming one slot needs the others to abstain. It matters only once athletes differ. |
| `hunt.win_action` | What the contestant does on winning the ball. | carry_out / tip_out | NEEDS COORDINATION | An individual choice of the contestant; needs the playbook. |
| `slot.anchor` | Where a slot stands in each situation (offence, defence, own restart, opponent restart, Hunt), relative to ball, field or goal. | anchor | NEEDS COORDINATION | v0/3 has no slots or anchors (native/README: no positional role or formation grid). Each athlete needs its own slot and anchor in a playbook, and the shape exists only if all teammates hold the same chart. |
| `slot.requires` | Minimum rating and body bands for a slot. | bands | NEEDS ENGINE WORK | Native v0/3 gives every athlete rating 0.70 and one body and reads no roster (ATTRIBUTE_STEP_SPEC.md). |
| `slot.prefers` | Weights used to rank candidates for a slot. | weights_open | NEEDS ENGINE WORK | As slot.requires. |
| `assignment.rule` | Pre-match rule that fills slots from a supplied roster by rating band. | rule | NEEDS ENGINE WORK | A step outside the engine, but there is nothing to assign until rosters carry ratings, and the harness has no per-athlete playbook input. |
| `subs.policy` | Use of substitutions. | cover_only | EXPRESSIBLE NOW | As built: substitutes only cover exclusions and disqualifications. TACTICS-0 keeps the same ten field starters in every phase. |

Every style's `policy_params_projection` in `tactics_0.json` holds its 16 EXPRESSIBLE NOW values. Running a projection in Native v0/3 would show a team-wide lean, not the style.

## 7. Limits of this document
- No style has been played. Strengths, weaknesses and predictions are reasoning.
- The numbers are first values chosen by reasoning from the rules and from Native v0/3's defaults. None was searched.
- Several styles rest on mechanics that Native v0/3 has but nobody has measured: how long a wrap holds, whether a body screens an arrow, how often a fast long pass is caught.
- The bands depend on the PLACEHOLDER envelope and on how ratings will map to bodies and skills, which `ATTRIBUTE_STEP_SPEC.md` leaves as placeholders except for speed.
- A rule reading that turns out wrong (Q-TAC-1 to Q-TAC-5) changes the style that leans on it; each such reading is marked in that style's canon check.
