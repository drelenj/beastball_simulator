# RB-3.7 offense diagnosis: why the simulator does not produce Beastball offense
Branch `claude/rb-3-7-offense-diagnosis` from `claude/rb-3-8-drop-freeze-recovery` @ 185b557. Diagnosis only: no engine, rule, cognition or constant was changed. Status words: DESIGN COMPLETE for the recommendations; the measurements are TESTED (reproducible from logs). Nothing is ACCEPTED.

## OWNER BRIEFING
1. **Accomplished.** Every question answered from the 13 soak matches. The soak raw logs answered most; a read-only observer re-ran the same 13 matches to add player positions, ball flights and carrier decisions. All 13 reproduced the soak's trace and state hashes exactly.
2. **What it shows.** Possessions are short because the ball is lost on its first flight, not because defenders swarm the carrier.
   - About 45% of possessions end with an open-play pass that misses its receiver: it goes out of bounds or to a defender.
   - About 36% end with a restart throw that is lost, mostly the snap after a first tackle. Defenders legally stand at the ball line and take the snap about 2 m from the spot.
   - Every pass leaves at 50-64 m/s whatever its length, and the passer leads a moving receiver as if the ball travelled at 27 m/s.
   - Carries never score because carriers release the ball themselves within about 0.6 s of entering the Keeper Zone, usually with nobody within 5 m. The engine lets an unopposed carrier score.
3. **Unproven.** The effect of each fix is estimated, not measured; no fix was implemented, as instructed. The catch model's reaction behaviour was measured only in an isolated scenario. Control has 3 seeds.
4. **Blocking.** Nothing. One canon question decides the biggest restart cause: should defenders keep a distance from the ball at a scrimmage snap?
5. **Recommended action.** Rule on C-1 (scrimmage defensive clearance). Then implement B-1 (pass release speed chosen by distance) and E-1 (pass lead uses the real ball speed) together, and B-2 (carrier decision in the zone). Measure each on the same seeds.

## 9. Top three causes (real rosters, 6,817 possessions in 10 matches)
Full data for questions 1-8 is in `DIAGNOSIS_DATA.md`. Machine-readable: `offense_diagnosis.json`, `pass_aim.json`, `restart_lane.json`.

### Cause 1: open-play passes miss the receiver (about 45% of possessions)
- **Evidence.** Possessions end in three ways here: a pass goes out off the passer's own team (1,581, 23.2%), a pass is intercepted or left loose (1,070, 15.7%), or another ball goes out off own team (428, 6.3%).
  - Open-play completion is 71%: 1,625 passes went out of bounds and 1,145 were intercepted in 10 matches.
  - Failed passes leave with the receiver a median 1.97 m off the line of flight, against 0.84 m for completed passes. 26% of failed passes are thrown with the receiver behind the direction of the throw.
  - The receiver doesn't move during the flight, and failures almost never involve a touch by the passing team. The ball simply doesn't go where he is.
  - Release speed is 50-64 m/s (median 58) for every pass, with a median length of 8.5 m.
  - The lead on a moving receiver uses distance / 27 m/s (`native/cognition.py:351`), but RB/3 throws at min(80, 0.5 × max throw speed) (`native/cognition.py:577`). The lead is therefore about twice the real flight time.
  - In an isolated test, at 58 m/s a stationary receiver cannot set his hands for passes of 6 m or less (`core_src/match.py:2176`). 30% of match passes are shorter than 6 m.
- **Class.** ENGINEERING: the lead formula is inconsistent with the RB/3 release speed. BEHAVIORAL: release speed is not chosen by distance. Secondary ENGINEERING: the catch reaction model at very high speed.

### Cause 2: restart throws are lost straight away (about 36% of possessions)
- **Evidence.** Possessions end with a restart throw intercepted or loose (1,726, 25.3%), a restart throw out (286, 4.2%), or a restart that fails and is awarded as a turnover (419, 6.2%).
  - Per match there are 178.5 first-tackle restarts, and 156 of them lose the ball within 5 s. 187 of 224 boundary restarts do the same.
  - Scrimmage snaps: 1,209 of 2,624 (46%) were intercepted, at a median 2.3 m from the spot.
  - The nearest defender stood 2.1 m from the throwing line, with a median 4 opponents within 5 m of the spot.
  - Own-40 snaps, where defenders must be behind their own 40 (lane clearance 21 m), succeeded 131 of 138 (95%). Tosses, with a 3 m clearance, were intercepted 406 of 1,971 (21%).
  - So a first tackle effectively ends the possession, through the snap.
- **Class.**
  - CANON: a scrimmage has no defensive distance; defenders may stand at the ball line, within reach of the snap.
  - BEHAVIORAL: the RB/3 defender stance places them 0.8 m off the line, and the snapper throws past them at 2 m.

### Cause 3 (missing attempts): possessions rarely reach the zone, and carriers release instead of carrying
- **Evidence.**
  - Of 6,817 possessions, 1,062 (15.6%) ever reach the Keeper Zone edge and 1,886 (27.7%) get within 32 m.
  - There were 1,098 carry attempts (entries into the attacked zone). The carrier starts a median 19.4 m from goal, carries for 2.7 m and 0.6 s, and gets no closer than 15.6 m (closest of any carry: 2.56 m).
  - 811 carries ended with his own pass or shot, 131 with a turnover and 73 with a grounding.
  - At the zone edge there are a median 0 defenders within 5 m, and the Keeper is 15 m away.
  - Inside 20 m the carrier chooses shoot 426, carry 414, pass 380, and the 3 s zone exit 59.
  - Shots: 385, from 10-15 m, with 98 scored (25%).
  - An unopposed carrier who keeps running scores 5 (forced scenario), so the block is the decision, not the physics.
- **Class.**
  - BEHAVIORAL: the carry/shoot/pass valuation near the goal, plus the 3 s zone-exit placeholder.
  - CANON check: how long may a carrier stay in the zone he attacks (zone_residence and the possession rules ZR-*)?

**Not the cause.**
- **Freezes** end 4.4% of possessions (299; 0.27 freezes per possession).
- **Second tackles** end 4.4%.
- **The baseline defence** is not overwhelming the ball at the moment of loss. At in-play turnovers there are a median 0 defenders within 5 m; at tackles, 2 within 5 m and 10 within 25 m.
- **Control rosters** look the same as real rosters on every measure. Control throws all leave at 50.3 m/s.

## Recommended fixes (not implemented)
| ID | Class | Fix | Evidence | Expected effect | Risk |
|---|---|---|---|---|---|
| C-1 | CANON | Owner ruling: at a scrimmage snap, defenders must stand a minimum distance from the ball (for example 3 m like the toss, or a neutral zone), or the snap cannot be intercepted within it | Scrimmage snaps 46% intercepted 2.3 m from the spot; own-40 snaps with defenders far away 95% completed; tosses with 3 m clearance 21% intercepted | Up to about 120 fewer lost snaps per match (about 60 fewer possessions per team); first tackles stop being turnovers in effect | Changes the sport; affects scrimmage, offside and second-tackle balance |
| E-1 | ENGINEERING | Lead a moving receiver with the flight time at the chosen release speed (distance / actual speed), not distance / 27 m/s | Lateral offset at release 1.97 m (failed) against 0.84 m (completed); lead constant is 27 m/s against a 58 m/s release | Fewer passes thrown past the receiver; a share of the 277 failed passes per match | Low; pure consistency fix |
| B-1 | BEHAVIORAL | Choose release speed by distance and receiver motion (slower for short passes, so his hands can be set), instead of a fixed min(80, 0.5 × max) | All passes 50-64 m/s; isolated test: 58 m/s fails at 6 m or less, 40 m/s succeeds from 4 m; 30% of passes are under 6 m | Higher completion for short passes and snaps | Slower balls give defenders more time to intercept; needs measurement |
| B-2 | BEHAVIORAL | Carrier near the goal: value carrying on to the goal when unopposed (no defender within a few metres, Keeper not in the lane) above passing or shooting; keep the 3 s exit only as rule compliance when he cannot reach the goal in time | 811 of 1,098 carries ended by own release after 0.6 s; median 0 defenders within 5 m; Keeper 15 m away; unopposed carries score | Carry goals (5 points) appear; more attempts per possession | Over-carrying into tackles; the zone-time rules may then bite (see C-2) |
| B-3 | BEHAVIORAL | Snapper and toss taker throw away from defenders' reach (lane clearance well above reach), and RB/3 defenders do not stand on the line within reach of the snap unless canon allows it | Interceptor in the lane at release 582 times; interception point 2.3 m from the spot | Fewer lost restarts even without C-1 | Partly overlaps C-1; defenders standing back is a tactical choice |
| C-2 | CANON | Confirm how long a carrier may be in the zone he attacks before zone_residence / ZR-C apply, so a carry from the zone edge (about 19 m, about 2.5-3 s) is legal | 130 possessions ended by zone rules; carriers exit at 3 s by placeholder | Clarifies whether B-2 can produce carry goals legally | None if confirmed |
| E-2 | ENGINEERING (Codex) | Review the catch hands-set model at release speeds above 50 m/s | Isolated test: stationary receiver fails at 6 m or less at 58 m/s | Only matters if B-1 keeps high speeds | Engine fidelity; Codex's lane |

## Reproduce
- Soak logs: `claude/soak-rb-3-8` @ 3364aa0, `native/evidence/rb38-soak/{real,control}/raw-*.json.gz`.
- Observer re-runs (positions, flights, decisions): `native/evidence/rb37/observe/observe-{real,control}-seedNN.json.gz`, produced by `tools/observe.py`. Each reproduced the soak hashes: see `observe/observe.log`.
- Report:
  - `python3 native/evidence/rb37/tools/offense_diagnosis.py --soak <dir containing real/ and control/> --observe native/evidence/rb37/observe --out native/evidence/rb37`
  - then `tools/pass_aim.py <soak dir> native/evidence/rb37/observe`
  - then `tools/restart_lane.py <soak dir> native/evidence/rb37/observe`
  - then `tools/write_data_section.py native/evidence/rb37`
