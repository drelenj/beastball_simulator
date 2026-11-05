# Positional tendencies v1 (Pocket 4.0 prototype)

Module: `positional_tendencies_v1.py`. Switch: system `tendencies` (off with `--off tendencies`). Strength dial: env `TEND_K` (default 0.5; 1 = full strength, 0 = lanes only).
The logic report supersedes the generator's old role labels: every player is classified into the closest *report* archetype from his own ratings (`classify`), see `archetype_mapping.csv` (margin = gap to the runner-up; small margin = close call).

## What a player does
Each player gets a `Tend(position, archetype)`:
1. **Off-ball target (Policy.targets override)** - own team has the ball: non-carrier attackers move to a position/archetype lane (depth relative to the ball, width from centre). Own team defending: Pocket still elects `hunt_count` chasers, but by *weighted* distance (position/archetype chase factor: Hunters/Trackers/Guards-on-interior keen, Predators/Strikers/Trappers-on-the-far-side less so), and everyone else takes a positional line. Skipped: man defence, non-live phases, loose ball, players inside the Keeper Zone, escorts within 6 m of the carrier.
2. **Carrier decisions** - multipliers on Pocket's own expected values: shoot / carry / pass / continue, shot-distance bands (Striker close, Scout mid-range, Sentinel/Guard/Trapper reluctant), and pass-receiver affinity by position (e.g. Pathfinder -> Striker/Scout, Sentinel -> Pathfinder/Hunter).

| Pos | Natural space (att / def) | Decision lean |
|---|---|---|
| PDR | weak side, ahead of ball | carry, finesse, some shot |
| STR | deepest, interior (narrow) | finish close, shoot-averse from range |
| SCT | wide outer channels, ahead of ball | mid-range shots, runs |
| PFD | follows ball laterally, a step behind | passes first |
| HNT | picks the emptiest spot (attack) / covers the gap (defence) | no preference |
| TRK | middle flanks, level with ball | support passes |
| SEN | defensive-midfield buffer behind ball | pass, rarely shoots |
| TRP | defensive flanks, behind ball | pass/contain |
| GRD | central, deepest | pass, never a shooter |
| KPR / ARC | untouched (Pocket's own keeper/archer logic) | - |

Archetype modifiers (lead, lane width, chase eagerness, bias) are listed in the `ARCH` table, one line each with the report's wording.

## Measured effect (Ala vs Xenar, calibrated rosters, rotation + low injuries)
- Shape: Guard defending sits ~10 m deeper vs. ball (u 45 vs 55), Scouts run ~22 m off centre (OFF 11-17), Pathfinder/Sentinel stay narrow (~10), Trappers wide (~17).
- Outcomes - **provisional**: full-strength biases cut scoring ~45% in regulation (22-109, 37-82 vs 112-106, 93-130 for the same seeds). Bias exponent 0.5: 43-122 and 27-122 (still ~30% below OFF; short games 15.1 vs 16.2 goals per game over 8 seeds). Lanes alone or biases alone each keep scoring at baseline; the combination compounds (more tackles/turnovers, fewer Keeper confrontations).
- It also widens the gap between stronger and weaker rosters (Xenar ~4:1 over Ala with tendencies on, ~even off) - only two regulation seeds, so treat as a hint.
- **Dials still to calibrate**: BIAS_K, STR/Scout attack depth leads, Trapper/Guard depth, chase factors. Nothing here was tuned to a target scoreline.

## Notes / gaps
- Sentinel, Keeper, Archer have no archetype list in the report: one default archetype each.
- Archetype classification is a weighted-deviation match on 16 ratings; Apex Hunter needs mean >= .88, sd <= .07, min >= .80 (all three Hunters in these rosters qualify).
- Unknown/other positions behave as Tracker.
