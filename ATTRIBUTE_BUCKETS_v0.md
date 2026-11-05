# Attribute buckets v0 (DreLen, 3–4 Nov 2026)
Rating scale for every attribute and every test sweep: 40, 50, 60, 70, 80, 90, 100.  40 = worst player ever, 70 = league average, 100 = best ever.
Four capabilities (know, decide, technique, body) and the buckets that carry them:
- PHYSICAL (gross athleticism): height, mass, reach, max speed, acceleration, braking, turning, agility, endurance, strength, balance, contact resistance, jump height, THROW POWER (new: release speed, peak speed, max distance).
- TECHNICAL (sport-specific fine motor, repeatable form): tackling, blocking, ball handling, catching, archery accuracy, keeper skill, THROW ACCURACY (new: direction error to the intended target), TOUCH (new: choosing the right velocity; used by passes, lobs, later shots).
- COGNITIVE (perceive and process): awareness (PRISM perception), judgment split by situation: SCORING, PLAYMAKING, MARKING (guarding a player), ZONE READS (guarding an area; may be dropped later if zone is not viable).
Rule: velocity is inversely proportional to precision (harder throw, bigger error).
Test rule: each mechanic is tested with the other two throwing stats at 100 (present but irrelevant).
Size must matter: height -> release/contest/jump-reach height; reach -> block, tackle-wrap, catch radius; mass -> collisions.
## Throw lab v0 (throw_lab_v0.py, provisional dials)
POWER: v_rel = 40*(0.5+0.5x), x=(R-40)/60.  ACCURACY: sigma_dir = max(.15, 3(1-x)) deg * speed/30.  TOUCH: speed sigma = max(.003, .10(1-x)).
Not yet wired into the match: Pocket 4 already has Throw Power/Throw Accuracy (throwing_v1.py via the 'throw' system); Touch and the full speed-precision coupling are new.
## Throw lab v1 (4 Nov): no speed caps; Throw Power 100 = 3 x 44.7 = 134.1 m/s (NFL ratio vs a 100-speed athlete)
release speed = 134.1*(0.5+0.5x);  accuracy sigma_dir = max(.15, 3(1-x)) deg * speed/67 (67 = weakest thrower's maximum);  touch speed sigma = max(.003, .10(1-x)).  throw_lab_v1.py -> throw_lab_v1.json
Finding: max distance (418 m at rating 40, 1537 m at 100) no longer discriminates on a 100 m field; power matters through flight time/speed instead.
## Wired into the engine (4 Nov): THROW_SPLIT=1 (default; THROW_SPLIT=0 = old model; backups throwing_v1_before_split.py, pocket4_proto_before_split.py)
- throwing_v1.py: V_POWER=134.1 (Throw Power 100), no rule cap, release direction sigma = max(.15, 3(1-acc)) deg x multipliers(no effort term) x hand speed/67, new Thrower.touch with speed sigma = max(.003, .10(1-touch)). T.RATINGS[pid]=(power, accuracy, touch) ratings 40..100 overrides for tests.
- pocket4_proto.py: thrower() reads extras (generator 0..1 values map linearly onto 40..100: .5 = 70); touch = the athlete's passing attribute until the generator has its own; ball_limit set to 1e9; passers choose speed = clamp(distance/PASS_FLIGHT_S (0.9), pass_speed, 0.98 x vmax), shooters clamp(distance/SHOT_FLIGHT_S (0.4), SHOT_MIN_SPEED (45), 0.98 x vmax); all env-tunable.
- Verified: sample_release matches the lab formulas (direction sigma and touch sigma within ~2%).
- Smoke test, 8 games of 60 s, default roster/keeper: shots 2.6 -> 3.5 per game, shot success 83% -> 99%, goals 1.9 -> 2.0, carry goals 0.4 -> 0.
- Not done: height/reach roles, judgment split (scoring / playmaking / marking / zone reads), generator ratings for touch, catch physics at 134 m/s.

## Reach is its own body number (4 Nov)
Athletes now have height, mass and reach. Roster sheets take an optional `reach_m` column; when it is absent reach = 0.46 x height (unchanged for every existing roster).
`player_gen_v1.generate` writes `reach_m`; env `REACH_SD` (default 0) draws reach/height from N(0.46, REACH_SD) clipped to 0.40-0.52 on its own random stream so no roster changes unless asked.
Keeper height set by KEEPER_FT still uses reach = 0.46 x height unless a sheet overrides it.

## Catch lab v0 (current catch model, receiver stationary 20 m away, pass aimed at his hands, 20 seeds per cell)
P(secure catch), reach 1.173 m, miss 0:  speed 20: .80 | 30: .80-.90 | 45: .35-.70 | 67: .20-.30 | 100: 0-.10 | 134: 0 (rating 40 to 100).
Rating moves it only at 30-67 m/s; reach and height do not move it when the pass is aimed at the hands; at 134 m/s nothing is caught at any rating.
Open: ~10-20% of low-speed passes end loose or back with the passer in the lab (unexplained, lab artifact until shown otherwise).
Files: catch_lab_v0.py, catch_lab_v0.json.

## Catch model v2 (CATCH_V2=1; catch_v2.py) - 5 Nov
Design decisions (DreLen): a 100 Catcher secures the fastest 100-Throw-Power pass (134.1 m/s) every time, a 40 never; reach sets the catch zone in absolute metres; height places the hands (z + .62 height) and Jump rating sets feet-to-ground clearance; one model for Keepers and field players.
Rule: P(secure) = 1/(1+(E/cap)^8), cap = (400 + (2.5 x E_max - 400) x x^3.6) x (1-(miss/R)^2), x=(catching-.4)/.6, E_max = .5 x 0.4 kg x 134.1^2 = 3.6 kJ; R = 0.9 x reach for everyone; hands-set time constant = PRISM Reaction latency x att_lat; field players jump for balls above standing reach (apex timed to the ball), Keepers keep the engine's planner.
Lab (stationary receiver 20 m, reach 1.17, aimed at hands): at 134 m/s rating 40-70: 0%, 80: 5%, 90: 85%, 100: 100%; at 100 m/s: 80: 75%, 90+: 100%; at 67 m/s: 70: 75%, 80+: 95%; at 45 m/s: 40: 30%, 60: 80%, 70+: 95%.
Jump (30 m/s pass, dz above the hands): dz 2.0 needs Jump >= ~90; dz 2.6 not reachable even at 100 (hand sphere 1.05 + jump 1.3 = 2.35).
Known: forced-release lab loses 10-15% at low speed (thrower re-takes ball / late hands-set); parameters CAP_LO, CAP_P, K, CAP_HI_X are [P]; the field-jump decision still reads the true ball path.
Sources: the three links (PubMed 16871010, PMC4368737, PMC4938428) could not be fetched (bot checks); the two PMC titles seen in search were one-handed catching gaze and grasping studies (human timing, not impact force).

## Hand contest v0 (ball first) and PRISM jump
- Field-player jump decision now reads the PRISM belief of the ball path (delayed, noisy), not the true path; feasibility rule uses t1,t2 from the belief.
- Two players reaching the same ball resolve by a logit over four balanced pillars: physical (reach/mass/strength), technical (Catching), contact resistance (balance), PRISM perception (hands-set tau). Caps ±2; exact ties fall to the existing contested hold. Lawful in front, foul from behind (existing blindside rule).
- Lab (hand_contest_lab.py, N=40): reach 1.40v1.00 P=.74; mass 330v150 .59; strength 100v40 .56; catching 100v40 .82; resistance 100v40 .79; PRISM Reaction .98v.40 .53 (weakest pillar, within the allowed "one pillar weighs less"). Even matchup: all ties.
- PRISM_OFFBALL=1: remaining field players re-pick their own targets from their own beliefs (with_view). Off-ball hand fighting (stage 2: blocks, jams, shedding) not built yet.

## Off-ball hand fighting v0 (HAND_FIGHT=1, hand_fight_v0.py)
- Who fights: any two opposing field athletes, neither the carrier, both upright in live play, whose hands can reach each other (engine contact range .7 x (reach_a + reach_b) between surfaces). No outcome is scripted.
- Contest: the same four balanced pillars as the ball hand contest (reach/mass/strength, technical, contact resistance + balance, PRISM perception). s = tanh(z/2). Exact ties lock the grip: no net force.
- Physics: the leader puts F = HF_FG (.5) x his own weight x |s| on the other along the line between them; impulse J = F dt moves the loser by J/m_loser away and the leader by -HF_REACT (.6) J/m_leader (action/reaction), recorded through c3_push, and loads the loser's balance exactly like a collision (so a strong shove on weak balance can ground him).
- Legality: lawful in front, foul from behind. A 'blindside' foul is called only when the athlete inside the other's rear cone is closing (>= .5 m/s) with his hands actually on him (surface gap <= .3 m); once per pair per 2 s. First version called it at full hand range (~1.2 m) and fouled every trailing defender (10 fouls/game vs 1, and play collapsed) -> fixed.
- Lab (hand_fight_lab.py: blocker in front of a defender driving past, 4 s): defender advance without fighting .74 m; blocker ahead on reach .63, mass .51, strength .67, catching .56, resistance .62; defender ahead on reach .77, mass .98, strength .71, resistance .77; perception .72. Direction right for every pillar; perception smallest; body block still does most of the stopping.
- Limitations [P]: every hand-reach pair fights (engaging is not a decision on beliefs yet); the force scale (.5 body weight) is a guess; no strip/swat of a contested ball by hand fighting yet.
