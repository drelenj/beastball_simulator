# Pocket 4.0 prototype: what is wired, what is not, what the first games show

Raw hookup, no tuning. `pocket4_proto.py` loads your `Beastball Pocket 2 0(1).py` untouched and patches it in memory. `--off a,b` switches any system off (throw, pose, shape, condition, jump, windup, foot, roster).

```
python3 pocket4_proto.py                                    # generated teams, regulation (4 x 600 s live), about 2.5 min wall
python3 pocket4_proto.py --short                            # 2 x 120 s, about 15 s
python3 pocket4_proto.py --a sample_roster_A.csv --b sample_roster_B.csv --seed 4
python3 pocket4_proto.py --off condition,jump               # compare
```

## Wired
| System | How it plugs into Pocket |
|---|---|
| Player generation | name/position/overall -> height, mass, 20 ratings -> Pocket's roster overrides (see PLAYER_GENERATION_HANDOFF.md) |
| Throwing | every voluntary pass/shot release: Throw Power caps speed, Throw Accuracy sets the error; Pocket's own aim error is replaced |
| Kicking | Pocket's long pass ('kick') goes through the punt model (power, accuracy, strike time) |
| Carry pose -> release delay | release delay = chain time + pose change: 'tucked' if an opponent is within 8 m, else 'exposed'. Replaces Pocket's 250 ms scaling |
| Ball shape | catch capacity divided by the shape's catch multiplier; default sphere (`--shape`) |
| Condition | one Condition2 per player: fatigue, wear, injury strain/hazard; speed/accel/braking/turning re-read from the capability table every 3 s; an athlete who reaches 'out' leaves through Pocket's injury and substitution path; bench players recover |
| Airborne | any athlete jumps for a ball above standing reach if he can get there 0.10 s sooner than staying down (jump 1.0 = 1.3 m); Pocket's own airborne motion and catch kernel resolve it |
| Wind-up read | defenders within 3 m of a shot line have hands set at release |
| Foot rule | legality monitor on every kick; Pocket's self-recontact foul waived for a legal foot sequence |

## Not wired
Ball-carry poses as strip resistance; per-part holds; the airborne contest module itself (limb spheres, body blocks, mid-air collisions: only the jump decision is used); kicks, dribbles and juggling as controller decisions (so the foot rule monitor has almost nothing to watch); the season layer; your Keeper's airborne dive uses Pocket's old logic.

## First games (seeds 1 and 3, regulation, generated teams, all systems on)
- Seed 1: 140-156, 190 possessions each, 105 goals; 16 injuries; 289+257 passes, 114 shots. Seed 3: 95-73, 8 injuries, 513 passes, 57 shots, 104 jumps, 29 kicks.
- Scoring is high: 73 % of finish attempts score in seed 1. Pass release speed averages 26.1 m/s (Pocket's plan was 27); about 24 % of passes are limited by Throw Power.
- Injuries are loose: 4 per team in seed 3, 8 per team in seed 1.

## Calibration findings (these matter more than the score)
1. **Pocket's controllers run its athletes at their limits all the time.** About half of all steps have lateral or braking load at 0.6-0.9 of the Pocket limit. Measured against the raw limits, Condition2 wrecked the roster: 19 injuries in a 2 x 120 s game and mean reserve 0.15 by the end. I added `LOAD_REF` = 1.6 (loads are measured against 1.6 x his Pocket limit): 2 injuries short-game, end reserve 0.48 at 5 min, 0.73 at the end of a regulation game. This is a dial, not a finding. The real choices are the controllers' effort policy or the condition layer's reference.
2. **The engine zeroes or resets velocity at tackles, restarts and period changes.** That is not athletic load. The bridge skips Condition steps when the implied acceleration is over 1.6 x LOAD_REF x limit, or the player is not upright, or play is not live (about half of all steps). Without this, 16 players were 'out' at the same tick at a period break.
3. **Overtime appeared in a 2 x 120 s game** (live 300 s): the first run tied. Not a bug here.
4. **Foot-rule log is empty**: nothing in the controllers kicks twice. Nothing to verify yet.
5. **Not verified:** that the jump hook produces airborne catches (104 jumps planned and fired per game, catch outcomes not yet split out); the pose delay's effect on completion; shot-lane blocks.

## Suggested next
Run 20 seeds per setting (`--off` each system in turn) to see what each system moves; decide LOAD_REF; add kick/dribble decisions; let the airborne contest module replace Pocket's catch sphere.

## Files
`pocket4_proto.py`, `test_pocket4_proto.py` (4 tests), `player_gen_v1.py`, `make_sample_rosters.py`, `sample_roster_A/B.csv`, `generated_players_A/B.csv`, `PLAYER_GENERATION_HANDOFF.md`, `rebase_results/pocket4_game_seed*.json`, plus the dependencies (throwing, kicking, ball handling, foot rule, airborne contest, condition layer, locomotion capability).

## Added after v1 (this package = v2)
- `rotation`: starters off at the next dead ball at reserve <= .60, back at >= .75, 32/40 min target; Keeper/Archer full game (Keeper >= 36). Settings in `ROT`.
- Injuries turned way down (`INJ_TH`, `INJ_HAZ`, discontinuity/lateral-spike guards).
- `rosters_from_generated(a.csv, b.csv)`, `run_mbl_match.py`, `game_stats.py` (team + individual box score).
- `tendencies`: positional and archetype play, see `TENDENCIES_NOTES.md`; `archetype_mapping.csv` maps each player to the closest logic-report archetype.
- `tendencies` v1.1: defenders join the offence (`DEFENDER_OFFENCE_NOTES.md`), dial `DEF_FREEDOM`. Rotation no longer subs out the restart taker.
- `restarts` (v4 package): First Hunt every quarter, scrimmage restart after the first tackle, 40 m snap after a score, toss-in. See `RESTARTS_NOTES.md`. Test scripts: `rs_test.py <seed> short|full [offflags]`, `rs_probe.py`, `hunt_study.py`, `rs_offside.py`.
