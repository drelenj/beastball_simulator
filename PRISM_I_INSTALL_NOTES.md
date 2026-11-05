# PRISM I (individual layer) installed in the Pocket 4.0 prototype
Switch: `PRISM_I=1` (off by default; with it off nothing of the layer exists in the engine). It sets, unless you set them yourself: PRISM_FIELD (carrier on beliefs), PRISM_DEF (defenders on beliefs), PRISM_BOUNDED (stale beliefs decay), PRISM_MANEUVERS (poses + juke/spin/stiff-arm/truck). Always on inside the field layer: BALLVIEW and CARRIER_BELIEF (no free ball or carrier position for defenders).
Not in the switch: archers (still shadow/flag-only), pursuit Judgment (PRISM_JUDGE_DEF, effect about .15 m), the 1v2 chase-vs-cover Judgment (harness only, not wired into live play), communications (interfaces exist, inert).

## Ratings (the only per-athlete knobs)
`prism_ratings_v0.py`. For each athlete and rating: an authored roster column `prism_<name>` wins; otherwise base = .5 x overall + .5 x Pocket awareness; rating = .7 + 1.5 x (base - .85) + position offset + seeded jitter (sd .05), clamped .05-.98. Position offsets are EMPTY (which positions specialise in what is canon: DreLen). Deterministic per athlete. Pocket's own 'awareness' attribute is an input only; PRISM Awareness is the perception rating.
League-average rating = .7 [C] (DreLen, 1 Nov). Roster check: see the distribution table at the end.
`PRISM_RATING_CENTER` (default .7, canon) exists only for sweeps; `PRISM_FIELD_RATINGS` (json) overrides everyone with one set (sweeps).
Which ratings act in live play today: Vision, Awareness, Clarity, Reaction, Focus (perception and reaction, carrier and defenders); Instinct (reads the carrier's tell); Judgment only in the flagged pursuit choice; Anticipation not yet.

## Tests (test_prism_install.py, all pass)
Off = no PRISM state; PRISM_I=1 deterministic; 44 athletes x 8 ratings and they differ; perception and maneuvers active; defender (5,600 views) and carrier (1,900) decisions on beliefs; leak counters 0; sentinel audit 4,124 hidden-body views, 0 differences; an explicit flag overrides the switch; a global ratings override replaces per-athlete ratings. Earlier suites unchanged (test_pose_engine, test_pocket4_proto, test_prism_archer).

## One leak found and fixed while installing
In 0.5% of defender views (27-30 per game) the defender had never seen the carrier, and the true carrier and ball positions stayed in view (the sentinel audit only checks hidden bodies, so it missed it). A never-seen carrier now maps to an uninformative midfield placeholder (stat `carrier_unaware`).

## What the layer does to the game at league average .5 (12 games per row, same seeds; superseded by the canon .7, see the center sweep: tackles 334 vs 356 off)
| config | goals | tackles | strips | possession changes |
|---|---|---|---|---|
| layer off | 131 | 356 | 42 | 474 |
| PRISM_I (per-athlete ratings) | 139 | 294 | 38 | 476 |
| PRISM_I, no maneuvers | 177 | 300 | 35 | 476 |
| PRISM_I, no defender layer | 132 | 398 | 40 | 497 |
| maneuvers only | 156 | 390 | 43 | 499 |
Reading: the tackle drop (about 25%) comes from the defender layer (about 300 tackles whenever defenders run on beliefs, about 390 when they do not); maneuvers do not reduce tackles. Defenders pursue with about a 4 m target error and no longer know where the carrier is for free, so fewer wraps land. Goals swing 131-177 across configs, inside game-level noise; do not read them. Tackle volume was part of Pocket's calibrated balance, so this is a calibration decision for you: accept it, raise the league-level rating (PRISM_RATING_CENTER) or retune the engine's tackle rate. The sweep below shows the center's effect; the default is now the canon .7.

## Rating-center sweep (PRISM_RATING_CENTER, 12 games per row)
| center | goals | tackles | strips | possession changes | defender target error |
|---|---|---|---|---|---|
| .5 (default) | 139 | 294 | 38 | 476 | 4.12 m |
| .6 | 147 | 295 | 33 | 462 | 3.86 m |
| .7 | 122 | 334 | 42 | 473 | 3.66 m |
Layer off: 356 tackles, 42 strips. A league-average rating of about .7 brings tackle volume back to ~94% of the layer-off level and strips to the same level; .6 does not move tackles. Goals are within noise. The lever is global: it raises every athlete's perception and reaction together. A better-calibrated route may be retuning the engine's tackle rate at .5; that choice is yours.

## Rating distribution at the canon center (44 athletes, both rosters)
| rating | min | mean | max |
|---|---|---|---|
| vision | 0.27 | 0.69 | 0.91 |
| awareness | 0.28 | 0.70 | 0.96 |
| clarity | 0.22 | 0.69 | 0.98 |
| reaction | 0.27 | 0.69 | 0.98 |
| focus | 0.22 | 0.67 | 0.98 |
| instinct | 0.28 | 0.69 | 0.97 |
| anticipation | 0.23 | 0.69 | 0.95 |
| judgment | 0.28 | 0.70 | 0.93 |
