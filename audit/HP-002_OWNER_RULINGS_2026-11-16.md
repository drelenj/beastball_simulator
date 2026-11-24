# HP-002: owner rulings, 16 Nov 2026 (America/Chicago)
Status: CANON (owner). Nothing here is implemented, tested or accepted.
- F2 (CANON): a defender's deflection of a shot into his own goal is credited to the shooter's team as an ordinary goal, not an own goal. An own goal needs the defending team to be the holder or deliberate releaser at the goal event.
- F5 (CANON): a hold by a non-carrier defender is a defence minor: count -1, or a half goal at 0 (same as other defence minors).
- Physical attributes: the nine natural physical attributes (phys-1.0) are in the roster workbook; the neutral secondary-slot shortfall for 4 infeasible ancestry combinations (33 players) is accepted (Option A).
- Kamasi Sinella physical lock: +14 mu on every attribute and a rating floor of 85, added to the size baseline before tribal bonus.
- ACCEPTED (owner, 16 Nov 2026 18:39 America/Chicago): RB-2.1 (codex/rulebook-2 @ b4cd38d, config native-rb/2, banded-only) as the rulebook measurement baseline. Reviewed by Claude (HP-002_RB2_REVIEW.md and addendum). Acceptance covers the rules implementation and counters only; it makes no claim about gameplay quality or balance.
- AUTHORIZED (owner, same time): RB-2.1 banded soak, 10 seeds, measurement only; no tuning during or between seeds.
- A-4 (CANON, owner, 16 Nov 2026 19:53): replaces the forfeit placeholder (Q-ATTR-7). It applies to Keepers as well as Archers: a field player may replace a specialist (Keeper or Archer) only once the designated starter AND the designated backup have both been ruled ineligible to play. No forfeit for lack of a specialist; a field player takes the role.
- Deceleration (owner, 16 Nov 2026 20:25): covered by Agility; no separate Deceleration rating. Braking and turning stay derived from Agility; revisit only if duel tests show they must decouple.
- PRISM, judgment and Touch ratings (owner, same time): add to the roster and attribute schema now, INERT (carried, validated and recorded, but read by no cognition, motor or engine path) until separately activated.
- R3-3 (CANON, owner, 16 Nov 2026 22:02): Güunlekia Serpents (one KPR, three ARC): the lowest-rated Archer becomes the backup Keeper. Applied: Zuberi Ibe (NBL24-09-16) ARC -> KPR in the roster workbook; the three Archers tied at Opening-day OVR 81, broken by Pre-camp OVR (Ibe 81, Sunblade 83, Swiftarrow 88). Ratings, size and ancestry unchanged.

## 17 Nov 2026 - Kamasi Sinella final canonical profile (owner-supplied)
Locked: Ala Marauders Hunter, OVR 98, ancestry Ly'Kun/Shynän/Dryqona (Tri-blood), height 9'8.1", 1,018 lb, wingspan 10'7.7", standing reach 12'6.9", physique Rangy. Physical ratings: Speed 94, Strength 96, Jumping 93, Acceleration 91, Agility 94, Balance 93, Throw Power 95, Stamina 97, Durability 96. Supersedes the earlier +14 mu / floor 85 generated values. Applied by audit/arcade/morphology/apply_profile_locks.py.

## 17 Nov 2026 - Dante Sinella (Bloodravens) and OVR sync
Owner: Dante Sinella was last season's league MVP and Archer of the Year for the title-winning Bloodravens, so he is the highest-rated Archer in the league. Applied: OVR 95 -> 99 and physical ratings raised (Spd 80, Str 95, Jmp 99, Acc 95, Agi 87, Bal 93, Thr 86, Sta 100, Dur 91; +12 mu shift, floor 80, same per-athlete RNG). Size, ancestry, physique unchanged. Also: All 712 Players Opening-day OVR synced to the team sheets (canonical) for all players that differed.

## 17 Nov 2026 - Toss timeout placement (CANON; supersedes the RB-2 goal-line toss-timeout rule)
Owner: when a toss times out, the other team is awarded the ball at its own 40 or the spot of the ball, whichever is closer to the attack goal. This applies to every toss timeout (end line and side boundary) and replaces the RB-2 special case that placed the scrimmage 5 m into the field after an end-line toss timeout. It is the same normalization the engine already uses for ordinary turnovers (x = max(spot, own end + 40) in the attack direction; y = spot y). Reason: the 5 m placement was the trigger of the RB-3.1 restart loop.

## 17 Nov 2026 - Archer targeting, and period starts by coin flip (CANON)
1. Archer targeting: an Archer may target ANY offensive player outside the Keeper Zones. The engine's extra condition (target within 50 m of the shooter's own end, native/rulebook/archery.py `shoot`) is NOT canon and is removed. Cognition's predicate (opposing field player on offence with team control, outside either Keeper Zone, not immune) already matches; no cognition change needed for this.
2. Period starts replace the opening Hunt (this also resolves Q-HELD-1 for period starts): a coin flip decides who gets the first offense. The winner starts periods 1 and 4 on offense; the loser starts periods 2 and 3. Each start is the same scrimmage as after a score (snap at the offense's own 40, y = 50). Another coin flip before overtime if needed. The flip is seeded so the match seed controls it.
Assumptions to confirm: "offensive player" = an opposing field player of the team with possession (Keepers and Archers are not targets); overtime periods after the first alternate the starting offense (placeholder).
Owner confirmed both assumptions above (17 Nov 2026): "offensive player" = opposing field player of the team with possession; overtime periods after the first alternate the starting offense.

## 17 Nov 2026 (evening) - Arrow legality timing and frozen players (CANON)
1. Arrow legality is judged at RELEASE (the arrow has left the bow). It is a foul only if the target was illegal to target at that instant: inside a Keeper Zone, already frozen, or immune. If the target becomes illegal AFTER release and before impact (steps into a Keeper Zone, is frozen by another arrow, becomes immune), the arrow is late and inert: no effect, but NOT illegal and no foul.
2. A frozen player is an obstacle to other players. Owner expects no in-game reason to touch a frozen player on purpose. Proposed and recorded as the working rule: contact with a frozen player is not a foul during the first 1.0 s after the freeze (buffer), in addition to the freeze immunity; after that the existing frozen-contact foul stands.
Open: arrows released within about 0.5 s AFTER the ball went dead or loose (about 70% of illegal arrows in RB-3.3). Working default pending owner confirmation: wasted (spent, no freeze), not a foul; parameter late_arrow_grace_ms = 500, settable to 0.

## 17 Nov 2026 (evening) - Arrow legality at release; frozen players are obstacles (CANON)
1. Arrow legality is judged at RELEASE (the arrow has left the bow). An arrow is illegal only if the target was illegal at release: inside a Keeper Zone, already frozen, or immune (plus the earlier rule: offensive player, outside Keeper Zones). If the target is legal at release but is inside a Keeper Zone, frozen or immune when the arrow arrives, the arrow is late and INERT, not illegal: no foul. An arrow that has not landed when the ball goes dead is INERT: no foul.
2. A frozen player is an obstacle: contact with him is not a foul (no advantage from touching him). Proposed in place of the frozen_contact major foul: a 1-second contact buffer once the player is unfrozen, alongside his freeze immunity.
Interpretation (owner to confirm): contact with a frozen player is not a foul (collision only); for 1 s after he thaws, contact with him is the existing immune_contact foul; after that, no contact protection beyond the arrow immunity.
Open: an arrow RELEASED while the ball is already dead or loose (about 70% of illegal arrows in RB-3.3). Default being tested: released within 500 ms of the ball going dead/loose = inert and spent, no foul; later = the existing archery_target foul.

## 17 Nov 2026 (late evening) - Dead-ball arrows are not spent; loose ball keeps offensive possession (CANON; replaces the 500 ms grace default)
1. An arrow that is inert because the ball is dead (released after the whistle, or still in flight when the ball goes dead) is not a foul and does NOT count against the Archer's quota: the Archer keeps his count as if he had not released it. No grace window is needed.
2. A loose ball is still in passive possession of the offense. Archers may therefore spend arrows and freezes on opposing offensive players pursuing the ball until possession changes. Team control is not required, only passive possession (this settles Q-FAB1-2: a pass in flight or a loose ball does not stop Archer targeting).
Assumption: an arrow released while live at a target that is legal at release but in a zone, frozen or immune on arrival is late and inert, no foul, and IS spent (it was released live).

## 17 Nov 2026 - Arrow quota (CANON confirmation)
15 arrows per team possession is the intended limit (resets on each possession change, as built). The 250+ arrows per Archer per match seen in RB-3.4 follow from about 330 possessions per team per match, not from the quota. No code change.
Open: strike-panel band (engine placeholder 20-80% of body height) and the zone rules for defenders (engine placeholder: a defending field player 5 s live in a Keeper Zone with no opposing field player within 5 m is a zone_unmarked foul).

## 17 Nov 2026 (night) - Freeze range, arrow limit, strike band (CANON)
1. No range limit on freezing: a legal target can be frozen at any distance. (Checked: native/rulebook/archery.py and native/rules.py pass in_range=True, so the RB path has no range limit; the 70 m limit existed only in the older Pocket/PRISM line. Add a test.)
2. The limit is 15 arrows per team possession (resets on every turnover); 5 freezes per possession as built.
3. The strike height band is kept: a hit freezes only if it lands between 20% and 80% of the target's body height, approximately from just below the knee to the upper chest. (Human proportions: knee about 28%, shoulders about 82%, chin about 87%; a literal "knee to neck" band would be about 28-85%. Owner kept 20-80%.) A hit between 12% and 20% or above 80% (to the top of the body) is off panel: inert, no foul, still counts against the quota.

## 17 Nov 2026 (night) - Keeper Zone residence and marking (CANON; settles Q-RB34-4 inputs)
1. Defender (team not in possession): the foul applies in the zone he is DEFENDING, his own Keeper Zone. A defender unmarked in his own zone for 5 s of live time is fouled (zone_unmarked).
2. Offense (team in possession): residence applies in the zone he is ATTACKING, the opposing team's Keeper Zone: 5 s of live time (existing zone_residence award to the other team).
3. "Marked" distance for a defender: an opposing field player within 2 m (was 5 m, a placeholder). The 5 s limit is kept. A field player in the other zone, or a defender in the zone his own team attacks, is not covered by these rules.
Owner's intent: tighter marking should allow more carries. Expected side effect to watch: the 2 m distance makes it harder to count as marked, so zone_unmarked fouls may rise until defenders either mark closely or leave their zone.

## 18 Nov 2026 - Edge cases (settles Q-RB34-1 and Q-RB34-2)
An arrow is INERT (no foul, no freeze) when (a) it is released while a shot is still in the air after the clock has expired, and (b) possession changes while the arrow is in flight. Defaults, not stated by the owner: (a) is a dead-ball case, so the arrow is refunded to the quota; (b) is a late-inert arrow released live, so it stays spent.

## 18 Nov 2026 - Marked distance stays 5 m (reverses the 17 Nov 2 m change)
Owner: keep the "marked" distance at 5 m (unchanged placeholder); the zone rules by zone defended/attacked and the 5 s limit stand. Before changing any behaviour, track at each zone foul where the ball and ball carrier are and where the nearest off-ball offensive player is, using a small soak.

## 18 Nov 2026 - Keeper Zone occupancy and marking distances (CANON)
Design intent (owner): the Keeper Zone is explosive, critical territory, which is why occupancy is limited. Marking distances: a defender in the zone he defends counts as marked (and is not called after 5 s) when an opposing offensive player is within 5 m of him OR the ball carrier is within 25 m of him. Starting values, tunable.
Interpretation (owner to confirm): the two distances are alternatives (either exempts him); "minimum" means the closest-approach distance that counts as marking. Data check on RB-3.5: of 150 zone_unmarked fouls, only 20 had a carrier within 25 m of the fouler, so the carrier distance alone would remove about 13% of the fouls; positioning has to do the rest.

## 18 Nov 2026 (correction) - Marking distances are BEHAVIORAL baseline, not a rule change
Owner: the 5 m / 25 m marking distances are default defender behavior, not a rule. The rule is unchanged from RB-3.5 (5 s in the zone he defends with no opposing field player within 5 m = zone_unmarked). Baseline behavior for defenders: at every moment, either be within 5 m of an opposing offensive player (marking) or within 25 m of the ball carrier, doing whichever is easier to reach. These distances are the baseline; tactics added later may change the ranges. Owner is set on the 5 m defender distance and open to alternatives for the carrier distance. Supersedes the "marked if carrier within 25 m" reading recorded earlier today; zone_carrier_distance_m is NOT a rule parameter.

## 18 Nov 2026 (refinement) - Defender leash is measured to the BALL
Owner: use the ball (not the ball carrier) as the anchor for the 25 m defender leash, so loose balls and passes in flight need no separate handling. Baseline defender behavior: be within 5 m of an opposing field player or within 25 m of the ball, whichever is easier. Constant: defender_ball_leash_m = 25 (replaces defender_carrier_leash_m).

## 18 Nov 2026 - Freeze recovery (CANON; resolves Q-RB36-1 and Q-RB36-2 by removal)
Owner: the "recovery protection 3 m / 2 s" in the rulebook was the original THAW BUFFER (protection for the thawed player), not a requirement that the frozen player retreat. A frozen player is in perfect stasis (zero velocity) and, once thawed, may move wherever he is programmed. Ruling: DROP the "be 3 m back toward own end before acting" condition and the 2 s action wait entirely. The thaw contact buffer (1 s, immune_contact, thaw_contact_buffer_ms=1000) and freeze immunity cover the protection intent. Q-RB36-1 (latching) and Q-RB36-2 (cap at room to end line) are moot.
Consequence: native/port.py freeze_recovery refusal is removed; no thawed player is ever blocked from acting. Add a test: a player frozen 2 m from his own end line can leave the field-side immediately after thaw and is never refused with freeze_recovery. Also remove the RB-3.6 cognition workaround for recovery if it only existed to route around this rule (keep any marking/leash behavior).

## 18 Nov 2026 - RB-3.8 ACCEPTED as the new baseline (owner)
Owner accepted claude/rb-3-8-drop-freeze-recovery @ 185b557 (native-rb/3, freeze recovery condition dropped; thaw buffer 1000 ms and immunity kept; defender baseline 5 m / 25 m-to-ball kept) as the new working baseline. Acceptance covers the freeze-recovery removal and the evidence that zone_unmarked and freeze_recovery refusals are gone (raw-log recompute by Claude agrees: 0 freeze_recovery mentions; discipline calls all archery_target). It does NOT accept the game's overall behaviour: scores 15-27, 18-28, 1-9 vs target 80-85 combined; ~340 possessions per team vs ~100; 5-8% possessions ending in an attempt; 0 carry goals. Those remain open (offense diagnosis next). native-rb/2 unchanged. Codex must reconcile the provisional claude/ branches onto this baseline.

## 18 Nov 2026 (evening) - Scrimmage set formation (CANON; resolves diagnosis item C-1)
Intent (owner): the scrimmage resembles a gridiron scrimmage: a set formation for offense and defense at the line; tactical differences come from what teams do after the snap.
1. Applies to scrimmages: after a first tackle, after a score, toss-timeout awards, and period starts (snap40). Tosses (boundary restarts) are NOT changed (3 m clearance as now) pending re-measurement. [default, owner did not object]
2. Ball spot: y = 50 always; the spot of the ball determines only x. Spot clamped to 10 m from either end line (x in [10, 90]).
3. Snap is straight back (never forward) to a DESIGNATED RECEIVER directly behind the snapper on y = 50. Receiver depth 5 m; on snap40 10 m.
4. Neutral zone (strip across the field, from the ball line toward the defense): 5 m deep; snap40 20 m (each team starts at its own 40). No player stands in it at the snap EXCEPT the nose tackle.
5. Nose tackle: on a first-tackle scrimmage the tackler lines up in the neutral zone directly across from the snapper (the tackled player, who is the snapper), in a nose-tackle / center stance. He is the only defender allowed in the neutral zone. On snap40 there is no nose tackle: all defenders are outside the zone. Default distance of the nose tackle from the ball: 2 m (tunable; owner did not specify).
6. Offense is behind the ball line at the snap. After the snap is released everyone is free to move and cross the zone.
7. Snapper = the tackled player if he is an eligible field player; otherwise the nearest eligible field player. [default, owner did not object]
8. Scrimmages inside the attacked Keeper Zone use the same formation (goal-line shotgun feel, receiver depth 5 m). Dead-ball formation time does not run residence clocks (live time only). [defaults]
Known consequence: a carrier tackled within 10 m of the attacked end line is spotted back at 10 m; one tackled within 10 m of his own end line is spotted forward to 10 m.
Status: DESIGN COMPLETE; not implemented. Supersedes the diagnosis proposal of a 3 m neutral zone.

## 18 Nov 2026 (night) - Scrimmage formation refinements after RB-3.9 (CANON; answers Q-RB39-1, -2, -3, -7)
1. (Q-RB39-1) ALL defenders stand outside the neutral zone; the nose-tackle exception is withdrawn. [Interpretation, owner to confirm: the tackler still lines up directly across the snapper at y = 50, at the near edge of the neutral zone, outside it.] NOBODY moves until the snap has travelled 5 m or the receiver touches it. A dropped or missed catch still counts as a touch/trigger. [Interpretation: "nobody" = every player except the snapper's throw and the receiver's own catch reaction; both teams are released at the trigger.]
2. (Q-RB39-2) Default receiver = the teammate nearest the receiver spot. A team may legally designate ANY eligible field player as the receiver (tactical choice; needs a cognition/tactic hook).
3. (Q-RB39-3) The snap lane between snapper and receiver is kept clear of players.
4. (Q-RB39-7) Frozen players are automatically unfrozen when the scrimmage formation is set. No thaw period, no thaw contact buffer, no freeze immunity after that auto-unfreeze.
Defaults standing unless the owner objects: Q-RB39-4 formation applies to every scrimmage; Q-RB39-5 majors spotted inside 10 m move to the 10 m clamp; Q-RB39-6 moot (no nose tackle); Q-RB39-8 tosses keep the old speed; Q-RB39-10 field length 100 m hard-coded.
RB-3.9 (claude/rb-3-9-offense-fixes @ 6a328bf) is IMPLEMENTED and TESTED, NOT ACCEPTED.

## 19 Nov 2026 (evening) - Zone-exit behaviour plan LOCKED (BEHAVIORAL default, owner-approved)
Owner: "lock in your recommended fix plan" after the zone-exit scenario (claude/rb-3-11-zone-scenario @ 8dbc031: a 0.70 athlete clears the zone from the goal mouth in 2.8 s if he simply leaves; the RB-3.11 Part A behaviour waited until 4.4-5.1 s).
1. The 5 s residence rule and the whole-zone extent are unchanged (no canon change). Inner restricted-area idea parked; revisit after the carry/pass fixes if attempts still fall short.
2. A player with NO reason to be in the zone leaves immediately: an unmarked defender with nobody he can reach to mark, and an off-ball attacker who is not involved in the play.
3. Last-moment (time-to-arc) timing is kept ONLY for players with a reason to stay: the carrier going to goal, a player with a real shot option, the designated receiver before the catch, and a defender actually marking someone (opposing field player within 5 m) or closing on one he can reach in time.
4. Safety margin for those players raised from 0.75 s to 1.5 s.
5. Q-RB311 defaults: an attacker chasing a loose ball counts as involved; passers may target a teammate in the zone but weigh his believed time left; when closing and leaving take similar time, take the faster with a small bias to leaving when the mark moves away.
Status: DESIGN COMPLETE; to be built with B-5.

## 19 Nov 2026 (night) - Scrimmage line rule, motion, eligibility (CANON)
Context: positions are deliberately absent from the rebuilt sport; archetypes should emerge before positions are reintroduced. Blocking is weakly coded and handoffs are not modelled yet (engine work before this is meaningful).
1. LINE RULE: yes. At the snap at least N offensive field players are "set" within about 1.5 m behind the ball line; everyone else is free behind the line. The rule constrains slots, not identities (no position labels). N to be tested between 4 and 6 before it is fixed. Defence unconstrained apart from the neutral zone.
2. MOTION: any player NOT on the line may be in motion at the snap, in any direction. [Implementation note: he must still be behind the ball line and outside the neutral zone at the snap.]
3. ELIGIBILITY: everyone is eligible (no ineligible line players).
Status: DESIGN COMPLETE; build after B-5 and after the engine models blocking contact and handoffs.

## 19 Nov 2026 (night) - Arrows during the snap hold (CANON; answers Q-RB310-2 arrow part)
No arrow may be released until the snap hold is over (the snap has travelled 5 m or the receiver has touched it). [Implementation default, owner to correct if wrong: an arrow released during the hold is treated like a dead-ball arrow - inert, no foul, refunded - and Archer cognition must not choose to release during the hold.]
Withdrawn suggestion: an Archer "alignment" rule is moot because Archers shoot from platforms off the field.
Owner expectation recorded: if Archers punish the receiver heavily, a deception-based attack (Wing-T style: motion, misdirection, handoffs, several possible ball carriers) should become the meta. That needs handoffs modelled and Archers acting on belief about who has the ball.

## 19 Nov 2026 (night) - Zone clock visibility (CANON; answers Q-RB312-2)
A teammate's (or opponent's) Keeper Zone residence clock is PUBLIC, exact information, but a player only knows it for players he currently perceives: a passer must observe the receiver to read that receiver's clock (exact value, gated by perception). Where vision/perception is not fully hooked up, treat it as plain public information for all players. [Implementation default: when the receiver is not in the passer's fresh perceived tracks, the passer has no clock reading for him and the zone-clock penalty does not apply from that reading.]

## 20 Nov 2026 - Score targets (CANON; answers the scoring analysis confirmations)
1. Target the MEDIANS of the pro season logs (owner's Drive "NBL 25-26", "MBL 2026"): NBL men's median team score 76 (median game total 152); MBL women's median team score 87 (median game total 175). The simulator currently uses the NBL roster, so its working target is 76 per team.
2. Constrain the TOTALS AND THEIR SPREAD only; the split of points by method (carries, throws by band, half goals, awards) is left to emerge. Spread reference: NBL team-score sd 12.7, p5-p95 59-102, game-total sd 17.8; MBL team-score sd 11.9, p5-p95 66-104, game-total sd 16.8.
Supersedes the T3 working number (80-85 per team) for measurement purposes. Source: audit/HP-002_SCORING_ANALYSIS_2026-11-20.md.

## 20 Nov 2026 - RB-3.16 ACCEPTED as the new baseline (owner)
Owner accepted claude/rb-3-16-merge @ 9c37fd4 (R-1 arm reach = arm span / 2, one per-athlete release clock, keeper reaction gate, off-ball top speed; RB-3.15 shot aim/lane; lead integration fixes) as the new working baseline. Soak evidence: claude/soak-rb-3-16 @ 409135f (13 matches): real-roster team-score median 75 (owner target 76, NBL median), mean 76.5; per-team sd 12.7 / 14.0 (pro 12.7); shots 54% scored.
Open (not covered by acceptance): talent gap about twice the pro season (Ala Apex 88.5 vs Garvian 64.4 per game, B won 9 of 10; pro implies ~11-point gap) - side-swap test pending; possessions ~216 per team (target ~100); ~23% of possessions end in an attempt (target ~50%); carries produce little (175 of 1,919 points). Codex reconcile of the provisional stack still pending (Codex budget spent on building first).

## 20 Nov 2026 - Handoffs and blocking (CANON; confirmed by owner)
1. HANDOFF: a hand-to-hand exchange between teammates within reach (arm reach = arm span / 2), any direction, no ball flight; legal anywhere a pass is legal.
2. BLOCKING: body contact that impedes an opposing FIELD player who does not have the ball; legal once the snap hold has ended, like all contact.
3. No blocking a frozen player (frozen players are obstacles) or a player inside the 1000 ms thaw contact buffer.
4. No holding: a block may push and obstruct but may not grab or restrain; restraint stays reserved for tackling the ball carrier.
Build sent to Codex: RB-3.17 on codex/rb-3-17-handoff-block from claude/rb-3-16-merge @ 9c37fd4 (engine primitives + cognition hook behind a flag, default off).
Side-swap result (claude/soak-rb-3-16-swap @ 881d4f4): team effect +18.1 per game for Ala Apex (95% range ~5-31; pro ~11 lies inside), slot-B effect +6.0 (not significant). Identical-team control test pending.

## 20 Nov 2026 (evening) - Carrier moves and carry scoring (CANON)
1. The ball carrier may stiff-arm, truck, juke, spin, hurdle, etc., anywhere on the field (answers RB-3.17 question 2: yes, a carrier may fend/block deliberately; carrier contact follows the normal contact rules, no grip on a non-carrier).
2. Owner idea, to build: near the goal the carrier may STRETCH the ball out so it breaks the goal plane (like reaching for the pylon in football). A carried ball breaking the plane inside the goal mouth is a carry goal (5).
3. Proposed by the owner, distance pending (3 m or 5 m): broaden the carry definition so that a release that scores from within N m of the goal, or the ball breaking the plane in hand, counts as a carry (5) instead of a throw (2/3/4). [Status: owner to pick N; not yet canon.]
RB-3.17 question 1 (handoff entering the giver's own Keeper Zone from outside): no restriction found for passes or carries; default = treat a handoff exactly like a pass (allowed). Owner to correct if a back-zone restriction exists.

## 20 Nov 2026 (evening) - Carry definition distance and handoff into own zone (CANON)
1. BROADENED CARRY: a goal counts as a carry (5 points) if the ball breaks the goal plane while in hand (including a stretch) OR if it is released from within 3 m of the goal (inside the goal circle: the goal mouth radius is 3 m). Releases from 3 m or farther keep the throw bands (2/3/4).
2. HANDOFF INTO OWN KEEPER ZONE: allowed; a handoff is treated exactly like a pass (owner confirmed the default).

## 20 Nov 2026 (evening) - Acceptable target ranges (CANON)
- Team score: anywhere from 75 to 90 points per team (median team score) is acceptable. Point estimate remains the NBL median 76 for comparison; overshoot inside 90 is fine.
- Possessions: 100 to 150 per team is acceptable (was a ~100 point target).

## 20 Nov 2026 (night) - Stretch angles (CANON; answers the RB-3.18 owner question)
A carrier may choose the angle of a stretch (not only straight toward the plane: low, high or sideways, e.g. around the keeper). Engine work for a stretch direction convention goes to Codex phase 2 with juke, spin and hurdle.
RB-3.18 verification (claude/rb-3-18-verify @ 5e1917d): suite 613 passed, legacy identical, identity exact; rule only = RB-3.16 (0 release carries); all ON median 66.5 per team (below the 75-90 range) with a placeholder hook - keep the flags OFF until the tactics pass.

## 21 Nov 2026 - Ball material (CANON)
Owner: "You can throw in some magikal material science to make things realistic." The Beastball ball is a fictional material; its physical properties (air drag, bounce restitution, horizontal speed kept per bounce, rolling resistance) need not match a real football. They are set by the lead to make play feel realistic and to meet the owner's targets, provided they are stated in config with their design basis and applied consistently (engine and athlete forecasts alike).

## 21 Nov 2026 - RB-3.21 ACCEPTED as the new baseline; everything on by default (owner)
- Accepted: claude/rb-3-21-ball-material @ eb788ec (ball material, RB-3.17 handoff/block, RB-3.18 carrier moves and 3 m carry rule, RB-3.19 ball in play and tactics, RB-3.20 exact bounce; RB-3.20 Part 2 reverted except no hand-back). Soak claude/soak-rb-3-21 @ 9e66749: league median team score 84.5 (range 75-90), possessions 151.9 per team (range 100-150, median 150.5).
- Owner: EVERYTHING ON BY DEFAULT (rb3_carrier_moves_enabled, rb3_handoff_block_enabled, rb319_ball_in_play_enabled, exact bounce, ball material, carry radius 3 m) - builder change pending.
- Talent gap guidance (owner): do NOT calibrate against the pro season logs - different simulator, rosters and version of the sport; the season is a feel reference only. The question is whether the gap is right for the ACTUAL difference in talent. The Overall (OVR) rating is not formulated from anything, so it does not describe a player's actual skill set; judge talent from the ratings and bodies the simulator uses.

## 24 Nov 2026
- ACCEPTED: RB-3.25 PRISM CORE (codex/rb-3-25-prism-core @ 2612256) as the PRISM CORE baseline; individuation stays opt-in. Lead verification: audit/native/HP-002_RB325_REVIEW.md.
- PRISM rating rulings 21-23 Nov recorded in the Claude Doc "PRISM Ratings Registry (v0)": Reflex (motor) and Instinct (inference); Defending + Zone Coverage replace Marking/Zone Reads; Takedown, Evasion (absorbs Carrier Duel, Contact Resistance), Goalkeeping (absorbs Keeper Skill), Disruption; Motor Control rating into Agility; Ball Handling kept whole and executes Stretch (Finishing decides); maneuver ratings Juke, Spin, Hurdle, Stiff-arm, Truck; decision ratings measure decision quality, not tendency.
- ORACLE named as the true-state system (learner/tester per PRISM tier; PLURIBUS, EMERGENCE named; DRILL, GAUGE, UNUM, MENTOR proposed). Authorized: scenario harness and DRILL block.
