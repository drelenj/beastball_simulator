# Player generation handoff: names, positions and overalls to playable athletes

You have: name, position, overall. The simulator needs: height, mass, speed, 19 other ratings. `player_gen_v1.py` fills the gap deterministically. Every number it invents is a provisional dial, not canon.

## Run it
```
python3 make_sample_rosters.py                 # writes sample_roster_A/B.csv (name,position,overall) and generated_players_A/B.csv (the full sheet)
python3 pocket4_proto.py --a sample_roster_A.csv --b sample_roster_B.csv
```
CSV columns: `name`, `position`, `overall` (0-100 or 0-1; `pos`, `player`, `ovr`, `rating` also accepted). Put one row per player; any number of rows. The best ten field players by overall start, then the keeper (position K/GK), the archer (A), and the rest sit on the bench. Missing slots are filled with 'Reserve n' players at 0.60.

## What the generator does, in order
1. **Position -> archetype** (table below). An unrecognised label becomes `utility` and writes a note on the player. Add the label to `ALIASES` in one line.
2. **Seed** = hash of `name|position`. The same row always produces the same athlete, on any machine. Change the name's spelling and you get a different athlete. Re-running never re-rolls a roster.
3. **Ratings.** Each rating starts at overall + the archetype bias (a passer is +0.14 on throw accuracy, -0.15 on tackling), plus a small personal noise (sd 0.035).
4. **The overall is exact.** The archetype names which ratings make up the overall and their weights; every rating is then shifted until that weighted mean equals the overall you gave. So a 78 QB is built from throw accuracy, throw power, awareness, handling, speed, agility and balance averaging 0.78, and is allowed to be weak at tackling. A rating that hits its clamp reports a note rather than silently missing.
5. **Durability and injury** are drawn around 0.70 and do not follow overall. A star is not tougher than a role player unless you set it.
6. **Body.** Height and mass are drawn per archetype, correlated (taller = heavier, 120 kg per metre). Field athletes are clamped 2.20-3.10 m and 120-330 kg (canon mean 2.54 m / 197 kg). The Keeper is 2.74-3.66 m (mean 3.20) and 270-305 kg. The Archer is unconstrained.
7. **Floors.** Ratings are clamped to 0.40-1.00. Speed is clamped to 0.60-1.00 because speed 0.6 is 80 mph and 1.0 is 100 mph (Table A: mph = 50 + 50 x rating).
8. **Pocket attributes** (`pocket_attributes`): speed -> top speed, acceleration, braking and cut times via the locomotion capability table; the other ratings go in as 40-100; `passing`/`kicking` come from throw and kick accuracy; reach is 0.46 x height; jump is carried alongside.

## Archetype table (means; overall shifts everything)
| Archetype | Labels accepted | Height m | Mass kg | Strong at | Weak at |
|---|---|---|---|---|---|
| passer | QB, PM, thrower | 2.54 | 190 | throw acc/power, awareness | tackling, blocking |
| runner | RB, HB, FB | 2.50 | 197 | speed, agility, handling, balance | throwing |
| receiver | WR, wing, slot | 2.58 | 182 | catching, speed, jump | blocking, tackling |
| forward | TE, FW, striker | 2.62 | 225 | strength, blocking, catching | throw accuracy |
| lineman | OL, DL, C, lock | 2.58 | 255 | strength, blocking, contact | speed, jump, catching |
| backer | LB, mid | 2.56 | 212 | tackling, strength | catching, throwing |
| corner | CB, DB | 2.52 | 188 | speed, agility, jump | blocking, strength |
| safety | S, FS, SS | 2.55 | 200 | awareness, tackling | throwing |
| utility | anything else | 2.54 | 197 | flat | flat |
| keeper | K, GK | 3.20 (sd 0.20) | 285 | keeper skill, catching, jump, kicks | speed |
| archer | A, bow | 2.42 | 168 | archery, awareness | contact work |

**The position labels are my guess.** You said you have positions, but not which. Tell me your real list and I will map it (or edit `ALIASES`: one line per label).

## What each rating drives in the simulator
| Rating | Used by |
|---|---|
| speed | top mph, acceleration, braking, cutting (locomotion table) |
| agility, balance, strength, contact resistance, tackling, blocking, ball handling, catching, awareness | Pocket's own attributes (tackles, strips, catches, reads) |
| throw power, throw accuracy | throwing model: release speed, error, wind-up |
| kick power, kick accuracy | punts, shots |
| jump | jump rise (1.0 = 1.3 m) |
| stamina | fatigue valve |
| durability | wear valve |
| injury | injury thresholds and hazard |
| keeper skill, archery accuracy | Keeper and Archer only |

## Things to know before trusting a roster
- **A 70 is not a 70 at everything.** The overall is the weighted mean of that position's key ratings. A lineman rated 78 has speed near 0.6.
- **Heights are mostly decided by position.** Overall barely moves height. If you have real heights for some players, override them: pass `overrides` to `to_pocket_overrides`, or edit `generated_players_X.csv` and I will add a loader.
- **Seeds are by name.** Two players with the same name and position get the same athlete. Add a suffix.
- **Dials that are mine, not canon:** archetype means and spreads, biases, key weights, durability/injury centre (0.70), noise (0.035), the mass-height slope.
- Self-test: 300 random players per archetype, no unmatched overalls; same input -> same output.

## If you later get real data
Any of height, mass, or a rating can be pinned per player and the generator fills only the rest. That is a ten-line addition; say the word.
