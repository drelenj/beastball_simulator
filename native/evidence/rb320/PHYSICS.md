# RB-3.20 Part 1 - ball ground physics (PROVISIONAL)

## A. Scenario (native/evidence/rb320/ball_scenario.py; outputs ball_scenario.out / .json)
Ball released from 1.5 m at 20, 35, 50 m/s, level and at the normal pass launch angle (launch_for to 1.6 m at speed x 0.4 s:
vz about 2.22 m/s), nobody near, stepped by the real native-rb/3 port (100 ms steps). "e from apex" = sqrt of the ratio of
successive bounce apex heights above the surface (exact from the post-contact state).

| speed, launch | build | first ground (s) | bounces | e from apex | distance at 1 / 2 / 3 s (m) | stops / leaves |
|---|---|---|---|---|---|---|
| 20 level | before fix | 0.6 | 7 | .899 .901 .879 .872 .844 | 18.0 / 31.4 / 41.2 | stops 54.5 m at 6.6 s |
| 20 level | fixed | 0.6 | 4 | .772 .772 .772 | 17.7 / 30.2 / 37.5 | stops 38.8 m at 4.3 s |
| 20 pass angle | before fix | 0.9 | 11 | .868 .775 .781 .932 1.056 ... (never rolls in 8 s) | 19.3 / 34.1 / 44.9 | still bouncing at 8 s |
| 20 pass angle | fixed | 0.9 | 5 | .772 .772 .772 .773 | 18.8 / 32.6 / 41.8 | stops 47.0 m at 5.0 s |
| 35 level | before fix | 0.6 | 7 | .899 ... | 31.4 / 55.0 / 72.1 | stops 95.4 m at 6.7 s |
| 35 level | fixed | 0.6 | 4 | .772 | 30.9 / 52.8 / 65.7 | stops 67.9 m at 4.4 s |
| 35 pass angle | before fix | 0.9 | 5 | .866 .776 .779 .934 | 33.9 / 59.8 / 78.8 | leaves at 4.67 s (98 m) |
| 35 pass angle | fixed | 0.9 | 5 | .772 | 33.1 / 57.2 / 73.5 | stops 82.6 m at 5.1 s |
| 50 level | before fix | 0.6 | 3 | .899 .901 | 44.9 / 78.5 / - | leaves at 2.77 s |
| 50 level | fixed | 0.6 | 4 | .772 | 44.1 / 75.5 / 93.8 | stops 97.0 m at 4.5 s |
| 50 pass angle | before / fixed | 0.9 | 2 / 3 | .866 / .772 | 48.4 / 85.6; 47.3 / 81.8 | leaves at 2.45 / 2.65 s |
Horizontal speed kept per bounce: 0.759 in every case (drag x .76). Height-vs-time samples (0.1 s) are in ball_scenario.json.

## Constants and their basis (code references)
| quantity | value | where | stated basis |
|---|---|---|---|
| gravity | 9.81 m/s^2 | core_src/match.py:15 DEFAULT_ASSUMPTIONS | standard |
| air drag | ball_drag .015 /s, LINEAR: v *= exp(-.015 dt) on all components | match.py:15, advance_ball match.py:2099 | none stated |
| ball radius / mass | .1075 m / .4 kg | engine.py:175 (Ball z), geometry.legal_goal; match.py:15 ball_mass_kg | none stated (football-like) |
| vertical restitution | .7745966692 (= sqrt .6) | match.py:15 ball_restitution; applied match.py:2105 | stated as the value itself |
| horizontal kept at a bounce | .76 (hard-coded) | match.py:2105 | none stated |
| bounce / roll threshold | |vz| > 2 m/s bounces, else rolls | match.py:2105-2106 | none stated |
| rolling decay | v *= max(0, 1 - 3 dt) per step (about exp(-3 t)) | match.py:2106 | none stated |
| engine step | 100 ms | native/config.py:44 dt_ms | Native default |
| forecasts | same rules: geometry.predict_path (50 ms), match.c4c_path (5 ms) | geometry.py:79-93, match.py:394-406 | "the same flight, bounce and roll rules as the match itself" |

## B. Real-ball comparison (real_ball_model.py / .out)
Assumption: a size-5 association-football ball (FIFA Laws of the Game, Law 2: 68-70 cm, 410-450 g; the engine's .1075 m / .4 kg)
on natural grass: quadratic air drag Cd .25 (supercritical) / .45, rho 1.2 (Asai et al. 2007, Sports Engineering 10:101);
vertical e .65 (FIFA Quality Programme rebound test, 0.6-1.0 m from 2 m); Coulomb friction .5 at impact limited to the rolling
speed 5/7 (Cross 2002, Am. J. Phys. 70:482); rolling resistance .8 m/s^2 (FIFA Quality Programme roll test, 4-10 m from ~3.1 m/s).
| speed (level) | real model 1 / 2 / 3 s, stop | engine fixed 1 / 2 / 3 s, stop |
|---|---|---|
| 20 | 16.0 / 24.4 / 28.1, 33 m at 6.4 s | 17.7 / 30.2 / 37.5, 38.8 m at 4.3 s |
| 35 | 27.1 / 42.8 / 52.1, 74 m at 9.8 s | 30.9 / 52.8 / 65.7, 67.9 m at 4.4 s |
| 50 | 36.7 / 57.3 / 70.7, 104 m at 11 s | 44.1 / 75.5 / 93.8, 97 m at 4.5 s |

Classification:
- DEFECT (fixed, RB-3.20a): restitution delivered above its stated value. The 100 ms step reflected the END-of-step vertical
  velocity (including fall below the surface) and the clamp added the penetration back as height: measured .84-1.06 against the
  stated .7746; a ball could bounce indefinitely above the 2 m/s roll threshold. Fixed by solving the contact instant within the
  step and applying the stated rules there (native/rulebook/ball_ground.py), and the same in predict_path. A ball already on the
  surface keeps the original rules. Fixed result: .772 (drag only).
- DEFECT, not fixed (minor, listed for Codex): c4c_path (Keeper forecast, 5 ms) has the same end-of-step reflection; the error
  is g x .005 = .05 m/s, negligible.
- CALIBRATION proposals (not changed): (1) air drag linear .015/s vs real quadratic: real distance at 2-3 s is about 20% shorter
  at 35-50 m/s (52.8 -> 42.8 m at 2 s for 35 m/s); expected effect: missed passes exit later or stop inside more often (the
  missed-pass exit distance, median 55 m, is mostly flight: about -15 to -20%). (2) horizontal kept .76 per bounce vs friction-
  limited (real ~.85-.9 for a fast low pass): the engine loses MORE than grass; raising it would lengthen travel. (3) rolling
  decay exp(-3 t) vs constant .8 m/s^2: the engine stops a slow ball far sooner (1 m vs 6 m from 3 m/s); raising realism would
  lengthen the roll. (4) vertical e .7746 vs grass .55-.71: lowering to .65 shortens bouncing time slightly. Net: only (1)
  shortens travel; (2) and (3) lengthen it.
