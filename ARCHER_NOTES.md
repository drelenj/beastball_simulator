# Archer investigation (Pocket 4.0 proto)

## Finding 1 - Team B archer never fired (BUG, fixed: `archerfix`)
Pocket 2.0 `Match.arrow_decisions` loops over teams A then B but uses `return` (not `continue`) when team A's archer
is on cooldown / has no legal target, so team B's archer was starved. Ala (A) fired ~80 arrows in a game, Xenar (B) 0.
Fix: run the original routine once per team with the other team's archer temporarily inactive.
Check (6 short seeds): original B arrows 0; fixed A 9-14, B 9-13.

## Finding 2 - Arrows almost never freeze anyone at stock speed (CALIBRATION, not changed by default)
Stock arrow speed = min(`arrow_limit` 30, `archery_release_speed` 28-29) m/s, i.e. slower than a 44.7 m/s sprinter.
Flight times are 1.3-2.2 s, aim only leads with constant velocity, so targets are gone before arrival.
Sweep, 4 short games per speed (~105 arrows each, both archers firing):

| arrow speed m/s | freezes | on-target impacts | blocked by other body | misses |
|---|---|---|---|---|
| 30 (stock) | 0 | 0 | 8 | 72 |
| 60 | 4 | 4 | 20 | 44 |
| 90 | 9 | 10 | 22 | 45 |
| 120 | 15 | 21 | 16 | 42 |

Also: freeze needs the target to be the ball carrier (ruleset 1.0.1) and in range; non-carrier hits are `inert_impact`.
Many arrows are intercepted by other bodies in the line.
Knob: env `ARROW_V=<m/s>` (default 0 = stock). Setting it also raises the engine's arrow_limit.
Needs a canon call on arrow speed relative to the 100 mph athlete scale.

## Drag-aware lead (v7, flag `arrowlead`, ON by default; turn off with `--off arrowlead` / off=('arrowlead',))
Pocket 2.0 leads a moving target with a drag-free flight time and corrects drag only along the archer-target line, so the decelerating arrow
arrives late and lands behind a sideways runner. `arrowlead` wraps `Engine.shoot_arrow`: re-solves the launch against the real dragged flight time
(8 lead iterations, gravity drop re-aimed each time), same low/high arc the engine chose, then applies the engine's own aim noise. Falls back to the
engine aim if there is no solution. Event `arrow_lead` logs real flight time, range, speed per arrow.

Standalone 45 m/s sprinter at 95 m, acc .86 (`arrow_intercept.py [aware]`): crossing runner 0-55% engine lead (100-175 m/s) vs 97-99.5% drag-aware.

Short games (4 seeds, ~95 arrows): freezes engine -> lead: 100 m/s 7 -> 7, 150 m/s 14 -> 20; on-target impacts 8 -> 10, 14 -> 28.
In games hits stay far below the straight-line test: runners turn and accelerate, other bodies sit in the line, and freezes only count on the ball carrier.

Full regulation Ala-Xenar, seed 1 (80-arrow quivers fully spent each game; ~20 arrows are cancelled by stoppages so outcomes sum to < 80):

| arrow speed | score A-B | freezes A/B | on-target A/B | blocked A/B | inert non-carrier A/B | inert own teammate A/B | misses A/B |
|---|---|---|---|---|---|---|---|
| 30 (stock) | 42-76 | 0/0 | 1/1 | 5/4 | 2/1 | 4/4 | 47/50 |
| 100 | 36-90 | 6/12 | 10/15 | 28/24 | 22/13 | 10/14 | 35/29 |
| 150 | 23-72 | 10/16 | 12/19 | 25/23 | 19/12 | 8/14 | 33/31 |

Single games: scores are noise-level evidence, not a balance reading.
Env knob `ARROW_V` (m/s) still defaults to stock 30. Box score now has the arrow rows (`game_stats.py`).
