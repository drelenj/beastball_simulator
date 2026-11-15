# TACTICS-0: eight team styles for Beastball (hypotheses)
Claude (Fable), 2026-11-15. Branch `claude/tactics-0`, from `claude/hp002-audit` @ 8d95bf2. Classified against Native v0/3 (`claude/native-v0-3-handoff-69stxd` @ 8613280).
Status: **DESIGN COMPLETE**. Not IMPLEMENTED, not TESTED, not ACCEPTED. Generated from `audit/tactics/tools/tactics_src.py` by `build.py`; edit the source, not this file.

## OWNER BRIEFING
1. **Accomplished.** Eight ways to play are written down as formations of role slots, the rating bands each slot needs, numeric tendencies, restart and Hunt plans, and a prediction for {{N_PRED}} of the 28 pairings. One exploits the 5 s Keeper Zone limit in attack and one in defence, one is built on deep throws, one on carries, one leans on the Archer.
2. **What the simulator can do now.** Nothing new. Native v0/3 can express {{N_NOW}} of the {{N_PARAMS}} tactic parameters, and only as one value for the whole team. It has no slots and ignores ratings, so it cannot play any of these styles as written.
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

{{NEUTRAL}}

## 4. The eight styles

{{STYLES}}

## 5. Prediction matrix
`+` row is predicted to have the edge over column, `-` the reverse, `?` no prediction. {{N_PRED}} pairings carry a prediction and {{N_OPEN}} do not. A prediction is a reason to expect a sign, written before any match. The test plan counts how many hold.

{{MATRIX}}

Reading it as a whole says something about the reasoning, not about the styles. On paper Long Count has one predicted edge and five predicted deficits, because slowing the game changes how many possessions there are and not what each is worth; an equal-roster round-robin is the least favourable test for it. Nothing here says the eight are evenly matched, and nothing was adjusted to make them so.

## 6. Parameter catalogue and classification
{{N_PARAMS}} parameters. {{N_NOW}} are EXPRESSIBLE NOW, {{N_COORD}} NEED COORDINATION, {{N_ENGINE}} NEED ENGINE WORK.

- **EXPRESSIBLE NOW.** Native v0/3 can run it today with no code change. In practice the parameter is one of the 16 team-wide `PolicyParams` fields (or a behaviour that is already the only one built), with one value for every teammate.
- **NEEDS COORDINATION.** The engine mechanics, intent kinds and view fields exist, but the athlete does not hold the value: it differs by slot, replaces a constant in cognition, or works only if teammates hold the same plan. It needs the pre-match playbook of `TACTIC_INTERFACE.md` and cognition that reads it. No physics or rules change.
- **NEEDS ENGINE WORK.** The engine, port or rules layer lacks something: ratings and bodies per athlete, athlete-chosen release speed, voluntary off-ball contact, or a public signal missing from the view.

{{CATALOG}}

Every style's `policy_params_projection` in `tactics_0.json` holds its 16 EXPRESSIBLE NOW values. Running a projection in Native v0/3 would show a team-wide lean, not the style.

## 7. Limits of this document
- No style has been played. Strengths, weaknesses and predictions are reasoning.
- The numbers are first values chosen by reasoning from the rules and from Native v0/3's defaults. None was searched.
- Several styles rest on mechanics that Native v0/3 has but nobody has measured: how long a wrap holds, whether a body screens an arrow, how often a fast long pass is caught.
- The bands depend on the PLACEHOLDER envelope and on how ratings will map to bodies and skills, which `ATTRIBUTE_STEP_SPEC.md` leaves as placeholders except for speed.
- A rule reading that turns out wrong (Q-TAC-1 to Q-TAC-5) changes the style that leans on it; each such reading is marked in that style's canon check.
