# Defender Judgment in a 1v2 (carrier + off-ball threat vs one defender), Stage A
Files: scenario_1v2_v0.py (harness, real Match), probe_1v2.py (paired runs), calib_1v2.py (calibration + held-out scoring), probe_1v2_A*.json, probe_1v2_B*.json (Stage B, in progress).

## Why this test
Pursuit and contain/drive gave no usable Judgment signal: pursuit is dominated by prediction, contain happens about once per two games. The 1v2 has a real tradeoff: commit to the carrier or cover the threat.

## Harness (all numbers [P])
Carrier A0 runs at goal (real policy, his first decision delayed to 1.5/1.8/2.2 s), threat A1 runs alongside (fixed route, the only possible receiver), tested defender B0 starts 18-28 m ahead and holds still for 0.4 s so his perception warms up, then plays a fixed option for 3.8 s: lane fraction f = 0 (go at the carrier), .35 (shade), .7 (sit in the lane), 1 (mark the threat). Everyone else is parked; archery is off. Every option is played from identical starts (deterministic; state that leaked between scenarios, the perception tick clock and the PRISM tables, is reset per scenario).
Outcome (attack gain, lower is better for the defender): 0 = stopped (hold on the carrier, tackle, strip, turnover), .4 = attack kept the ball but the ball is not past the defender, 1 = kept it and got past him.

## What the world looks like
Going at the carrier stops him when the defender arrives before the carrier acts (gain about .1-.2 when he acts at 1.8 or 2.2 s) and loses when the carrier acts first (.68 at 1.5 s). Sitting in the lane or marking the threat is safe (.4-.6). Shading is the worst (about .6): neither stops the carrier nor takes the pass. Best fixed option: chase (.31). Choosing the best option per scenario in hindsight: .12.

## Judgment = quality of the choice, Inference separate
- Inference: the defender's predicted gain per option from his own beliefs (believed carrier position and velocity -> time to contact; prior over when the carrier acts, uniform over the three levels). First version (hand-built P(arrive first) from the believed contact time) was miscalibrated: it always chose cover (.42, worse than always chasing) because the believed contact time was about 2.9 s, longer than the real contact. That is an Inference error, and Judgment cannot repair it. The second version is a least-squares fit of realised gain per option on (carrier act time, believed contact time, their product, square), fitted on 160 training scenarios and averaged over the prior on the carrier's act time.
- Judgment: the same menu for everyone; choice noise (1-J) x .5 and a pull toward the habitual option (chase) of (1-J) x .3.

## Result, held-out test set of 100 scenarios (calibration fitted on a different 160), mean attack gain
| | gain |
|---|---|
| Judgment 0 | .392 |
| Judgment .1 / .3 / .5 / .7 | .384 / .362 / .352 / .340 |
| Judgment .95 / 1.0 | .294 / .286 |
| always chase (best fixed option) | .310 |
| hindsight best option | .124 |
Paired bootstrap (same scenarios): J=1 vs J=0 -.106 [-.170, -.036]; J=.5 vs J=0 -.040 [-.076, -.008]; J=1 vs always-chase -.024 [-.080, +.030] (not distinguishable); hindsight best vs J=1 -.162 [-.212, -.114].
Reading: Judgment is monotone and the effect is real (about a quarter of the gain at J=0 versus J=1). A perfect chooser still beats simple "always chase" only slightly, and the .16 gap to hindsight is information the defender lacks (when the carrier will act). That gap is where Anticipation (reading the carrier's tell / timing) belongs, and where a teammate's call could help (PRISM II).

## Caveats
Hidden carrier act time has three discrete levels and the defender is given the true prior; the outcome scale (0/.4/1) is a placeholder; one geometry family; the calibration is fitted in the same simulator it is scored on (train/test split on scenarios, not a different engine); the choice-noise and habit scale (.5, .3) are untuned. Judgment is not tied to a rating's numeric scale beyond J in [0, 1].

## Next
Stage B (teammate marks the threat; the defender may or may not see him through his own perception) is running with the same train/test split. Stage C (teammate calls "I've got him") is the first PRISM II message.
