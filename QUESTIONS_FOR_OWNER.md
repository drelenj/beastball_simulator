OWNER BRIEFING
1. Native build uses the following smallest working PLACEHOLDERs where implementation or canon detail is incomplete.
2. These are explicit defaults, not accepted canon or evidence of good play.
3. No question here currently blocks engineering. Acceptance and baseline designation remain the owner's decision.

| ID | Question / replaceable default | Class and current handling |
|---|---|---|
| Q-HUNT-1 | Centre-circle radius and setup distances are not specified numerically in the build prompt. | CANON detail; PLACEHOLDER keep restarts_v1's 5 m radius, contestants approach physically from legal initial scatter. No assigned formation or role-ranked contestant. |
| Q-HUNT-2 | Exact clock activation within the First Hunt is not specified in the authoritative prompt. | CANON detail; PLACEHOLDER clock runs in the opening phase, including approaches; false start retakes and no Archer until whole ball exits circle. |
| Q-ZONE-1 | Unmarked defenders cannot remain indefinitely, but the permitted grace interval is not stated. | CANON detail; PLACEHOLDER 5 s unmarked residence, inherited duration; marked defenders exempt, Keepers exempt. |
| Q-FLIGHT-1 | Maximum shot finishing-flight duration is not stated. | CANON detail; PLACEHOLDER 10 s safety tail, normally ends on ground/control/out/goal. Only shots get an exception. |
| Q-BOUNDARY-1 | Exact anatomical witnesses for every touching body part need more motor integration. | ENGINEERING; PLACEHOLDER ground body-cylinder envelope with airborne exemption. Native v1 replaces it with support/anatomical witnesses. Goal whole-ball test is separate. |
| Q-COVER-1 | If simultaneous exclusions temporarily leave fewer than 12 eligible among 22, does "available" include excluded athletes? | CANON edge case; PLACEHOLDER excluded athletes are unavailable until their exclusion expires, so fewer than 12 currently eligible causes a forfeit. No unavailable athlete is fielded to hide this case. |
| Q-SIMULT-1 | Simultaneous offsetting minor fouls outside the three specified exact ties have no explicit procedure. | CANON detail; PLACEHOLDER retain B0 neutral offset: record each sanction and restart with existing possession/count, no automatic major classification. |
| Q-HELD-1 | Unresolved physical joint-ball control has no resolution duration in the prompt. | CANON detail; PLACEHOLDER retain B0 one-second held-ball reset/alternating scrimmage; Hunt joint control retakes without a penalty. |
| Q-SENSOR-1 | Native sensor cadence/noise constants are not canon. | ENGINEERING; PLACEHOLDER immutable delayed/noisy cone/occlusion observations with independent per-athlete RNG, no true fallback. Claude replaces/takes ownership. |
| Q-THROW-1 | Full THROW_SPLIT mechanics and arbitrary-speed error calibration are not yet ported. | ENGINEERING; PLACEHOLDER explicit intent speed/height, drag-aware arc, 60-degree moving-release bound, uniform accuracy error. Do not claim full throwing_v1 equivalence. |
| Q-HAND-1 | Full voluntary off-ball hand-fight repertoire is not yet ported. | BEHAVIORAL/ENGINEERING; PLACEHOLDER retained incidental contact physics, intent-gated carrier wraps, no automatic random gripping. Native v1 adds PRISM-owned off-ball actions. |
| Q-CONTACT-1 | B0 automatic containment/descent choices used true-state tactical triggers. | ENGINEERING; disabled in Native. Motor may retain already admitted Keeper commitments; new semantic choices come from decide(). |
| Q-CATCH-1 | CATCH_V2 shared energy kernel is ported; automatic jump/hand-contest overlay is not installed. | ENGINEERING; PLACEHOLDER B0 simultaneous secure-contact handling plus shared threshold kernel. No second Keeper decider. |
| Q-BEHAVIOR-1 | Minimal Hunt claims, restart claims/alignment/wait/snap, dribble and cover policies need replacement. | BEHAVIORAL; PLACEHOLDER procedural decisions in the same view/belief/intent pipeline, canonical admission, no quality claim. Claude owns their later cognition replacements. |

Explicit DEFERRED: breaks, timeouts, Hunt penalties beyond false-start retake, standard scoring, fatigue, injury, rating development, adaptive learning, M2 plan/message content. No implementation of those deferred features is authorized by this baseline.

PH3 implementation limit (ENGINEERING, not a canon escalation): the current defender-marking exemption checks offensive field players. Keeper-as-marker coverage is not established by the conformance test. Native v1 must cover every offensive-player role permitted by the rule. This residence model remains PLACEHOLDER; the five-second attacker rule and field-player marking case are tested.

## native-v0/3 (FAB-1, Claude, 2026-11-15)
These apply to config `native-v0/3` only. None blocks engineering; each has the smallest working default in place.

| ID | Question / replaceable default | Class and current handling |
|---|---|---|
| Q-FAB1-1 | Canon gives arrow speed as 250 m/s and as "about 5.6 times a 100 mph (44.7 m/s) top speed". The engine's fastest player runs 27 m/s, so the two readings differ: 250 m/s (ratio 9.26) or 151 m/s (ratio 5.59). Which is the invariant? | CANON; PLACEHOLDER 250 m/s as confirmed (`arrow_speed_ratio = 250/27`). One number changes it: `--arrow-speed-ratio 5.59`. |
| Q-FAB1-2 | Does a team keep "team control" while its pass is in flight? The rules layer as built says no, so an arrow released at an opposing field player during a pass is an `archery_target` minor (and a half goal at tackle count 0). Under native-v0/2 this produced 64 such fouls and 62 foul awards in seed 1. | CANON, rules layer is Codex's; PLACEHOLDER the v0/3 Archer does not choose a release during a pass in flight. If canon keeps team control in flight, the rules check widens and this Archer predicate is reverted. |
| Q-FAB1-3 | A defender may hold a carrier up (wrap) or bring him down (takedown); a carrier may run through, brace or dodge. The values that choose between them are unsearched (commit to a takedown inside a believed 6 m gap; brace above 0.7 balance load; dodge with 0.3 s or more of warning). | BEHAVIORAL; PRIMITIVE functional defaults, no quality claim. Brace has no physical benefit in the present engine beyond not prying at the grip (engine fidelity is Codex's). |
| Q-FAB1-4 | Restart claims: the believed-nearest teammate claims, and each athlete delays his own claim by 25 ms per metre from the spot. Two nearest teammates stand 8 m from the spot so a legal throw exists. With no believed target the taker throws to legal space only in the last 1.5 s. | BEHAVIORAL; PRIMITIVE / PLACEHOLDER defaults replacing Q-BEHAVIOR-1 for restarts under v0/3. Hunt claims, dribble and cover policies stay as in v0/2. |
| Q-FAB1-5 | A toss timeout on the goal line is followed by a scrimmage placed 0.5 m from the goal line, leaving the defence half a metre of legal ground. | CANON / rules detail for Codex (RB-1): where does a turnover scrimmage go when the spot is on or near a goal line? Unchanged here; v0/3 athletes stand in the half metre. |

## TACTICS-0 (Claude, 2026-11-15)
Everything above this heading is copied unchanged from `claude/native-v0-3-handoff-69stxd` @ 8613280, so that a merge keeps one file. None of the questions below blocks the design; each has the smallest placeholder in force. The usual ranges (ratings 0 to 1 with professionals at 0.60 to 1.00, heights about 2.40 to 2.95 m, masses about 155 to 285 kg) are the design envelope and are themselves PLACEHOLDER, by the owner amendment of 14 Nov 2026 22:42.

| ID | Question | Class and placeholder in force | Styles or files it moves |
|---|---|---|---|
| Q-TAC-1 | Keeper Zone re-entry. The Rulebook says an attacker may be in the zone "at most 5 seconds at a time". Does he get a fresh 5 s as soon as he re-enters, or must he stay out for a minimum time first? | CANON detail; PLACEHOLDER fresh 5 s at once (as built in Native); Zone Waves imposes 1.0 s outside on itself | Zone Waves depends on it |
| Q-TAC-2 | A frozen ball holder drops the ball, and a tackle on a frozen player is cancelled. Both are engine behaviour; the Rulebook text says neither. Canon? | CANON; PLACEHOLDER as built | Archer's Anvil is stronger with the drop; it does not need it |
| Q-TAC-3 | How often may an Archer release? Native allows one arrow every 2.6 s (a constant in cognition). Canon gives the quota (15 and 5) and the speed, not a rate | CANON detail; PLACEHOLDER 2.6 s as built | Arc Siege, First Strike, Archer's Anvil |
| Q-TAC-4 | Is waiting on purpose inside the legal 10 s snap window "delay of game" (a minor foul after a warning)? | CANON detail; PLACEHOLDER legal inside the window | Long Count waits 8 s when leading |
| Q-TAC-5 | Do Keepers and Archers share the usual body ranges? Older generator notes give Keepers 2.74 to 3.66 m | CANON; PLACEHOLDER yes, one envelope for all | Personnel profiles, attribute step |
| Q-TAC-6 | May a team change its plan at a period break or a timeout? | CANON / BEHAVIORAL; PLACEHOLDER no, one playbook per match | Tactic interface |
| Q-ATTR-1 | What top speed does a speed rating below 1.0 give? Is 0.60 = 80 mph canon? A comment in `player_gen_v1.py` says so; I was given only 1.0 = 44.704 m/s as canon | CANON; PLACEHOLDER mph = 50 + 50 x rating. The alternative, proportional to the rating, gives 26.8 m/s at 0.60 against 35.8 | Attribute step: every athlete's top speed |
| Q-ATTR-2 | Is throw power 1.0 = 134.1 m/s (three times the top running speed) canon? It is in the 4 Nov attribute notes | CANON; treated as PLACEHOLDER | Attribute step; Arc Siege, First Strike |
| Q-ATTR-3 | How quickly should an athlete reach top speed? With today's acceleration a 40 m/s top speed takes about 4 s and 80 m, so on a 100 m field it would rarely be reached | CANON / BEHAVIORAL; PLACEHOLDER today's acceleration at rating 0.80 | Attribute step; every speed band |
