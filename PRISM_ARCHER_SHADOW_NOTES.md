# PRISM v0 - Archer shadow mode (Perception + Information only)
Module `prism_archer_v0.py`, hooked in with env `PRISM=1`. Decisions are unchanged: the engine archer still decides from true state; the shadow archer builds its own belief and we log the gap. Run: `PRISM=1 ... python3 prism_study.py 1,2,3,4 short <tag>`; unit tests: `python3 test_prism_archer.py`.
All numbers in `PARAMS` are PROVISIONAL placeholders (tick 10 Hz, FOV +-100 deg, fovea +-15 deg, gaze slew 120 deg/s, position noise (0.01+0.0025 x range) m scaled by off-axis and (1.3-0.6 awareness), memory 2 s, velocity filter gain 0.4). Per-athlete inputs are ratings only: `awareness`, `decision_speed` (latency = decision_speed x (1.3 - 0.4 awareness)).
Model: platform eye point, line-of-sight against body cylinders (torso or head point), field of view, gaze that slews toward the believed carrier, per-tick detection probability outside the fovea, noisy delayed observations, per-player belief with timestamp, velocity estimate and confidence decay.

## Acceptance tests (unit, all pass)
1 occluded target never detected / 2 seen once blocker moves / 3 nothing detected behind the platform (outside FOV) / 4 beliefs are stale and wrong after the target moves / 5 higher awareness gives smaller error and shorter latency / 6 deterministic per seed.

## First shadow run (4 short games, platform defaults, 103 arrows)
| | awareness as rated | awareness forced to 0.5 |
|---|---|---|
| target known at release | 103/103 | 103/103 |
| target visible at release | 102/103 | 102/103 |
| belief age at release, median s | 0.40 | 0.50 |
| belief position error at release, median m (mean) | 1.67 (1.76) | 2.45 (3.42) |
| belief velocity error, mean m/s | 6.0 | 7.1 |
| aim from belief vs aim from truth, divergence median m | 4.5 | 5.6 |
| miss distance at arrival, belief aim / omniscient aim, median m | 5.5 / 2.0 | 6.0 / 2.0 |
| arrows whose aim point ends within body radius, belief / omniscient | 0 / 4 | 0 / 4 |
| opposing players in range / visible / known (mean per second) | 5.2 / 5.1 / 5.0 | 5.2 / 5.1 / 4.9 |
Identical release counts and omniscient columns in both runs confirm the shadow does not alter play.
Caveats: "aim point within body radius" is a strict proxy (the real arrow can also strike along its path), so only compare belief vs omniscient.

## Velocity estimator tuning (v0.1)
Estimators compared side by side on identical observations (same games, same noise draws), 8 short games, 212 arrows: finite-difference filter ('diff', the v0 default), alpha-beta, windowed linear regression (0.3-0.6 s) and quadratic fit with acceleration.
Findings: (1) a 0.4 s regression window is best of the realistic estimators (median position error 1.5 m vs 1.67, median miss of belief aim 5.3 m vs 5.65); longer windows lag, shorter ones are noisier; alpha-beta and quadratic fits did not beat it. (2) Bug fixed: observations were delivered one tick late when latency was shorter than a tick; this mattered only for zero-latency reference runs. (3) With zero noise and zero latency the error floor is ~2.3 m/s and the belief aim misses by 2.9 m (omniscient aim: 2.1 m): carriers accelerate hard, so even a perfect observer cannot read velocity exactly.
Default is now `vel_mode='lsq', win_s=0.4`.

## Drive mode and Inference v0 (v0.2)  - 250 m/s, platform 15 m / 5 m, ruleset 1.0.2, 8 short games each
`PRISM=1 PRISM_DRIVE=1`: the archer decides from its belief state (non-archer players are swapped to believed position/velocity and unknown players hidden for each arrow decision); freeze/immunity/eligibility stay true (public information, DreLen 30 Oct).
| archer | arrows | freezes (carrier/non) | on-target | blocked | inert | misses |
|---|---|---|---|---|---|---|
| omniscient | 214 | 51 (26/25) | 53 | 8 | 10 | 150 |
| belief-driven | 209 | 10 (2/8) | 8 | 23 | 21 | 172 |
| + attention lock (half latency on the player being drawn on / carrier) | 222 | 6 (4/2) | 15 | 10 | 19 | 194 |
| + attention lock, awareness 0.5 | 213 | 10 (6/4) | 14 | 15 | 19 | 183 |
Inference v0 pieces: self-assessed track error + hit-probability estimate + hold-fire gate (`PRISM_HOLD`, off by default). Calibration check: estimated hit probability 0.1-3% vs realised ~7% flat across quintiles = no discrimination, so the gate fires almost never (hold 0.1 -> 2 arrows in 8 games). Not useful; left off.
Conclusion: reaction latency dominates (noise alone 0.2 m position error, latency alone 1.5 m). Freezes stay at ~12-20% of omniscient and do not yet separate by awareness (6-10 freezes per 8 games is within noise). Open: 9 of 15 on-target impacts did not freeze (inert) - not yet explained (panel/angle/immunity conditions).

## Inert impacts and latency sweep (v0.3) - 250 m/s, platform 15 m / 5 m, ruleset 1.0.2, 8 short games each
Freeze-condition diagnostic (`FZ_DIAG=1`): impacts that reach the freeze rule fail on (a) body panel - arrow struck outside 20-80% of body height (5/60 omniscient, 6/17 belief) and (b) range - target had moved past the legal 70 m by arrival, since range is measured from release origin to impact (4/60 omniscient, 6/17 belief). Both are rules working as written; the belief archer fires at the range edge on stale information.
STRATEGY fix: keep a 5 m safety margin inside the legal range (`PRISM_RANGE_MARGIN`, default 5 in drive mode). This took belief-archer freezes from 6 to 36.
Latency multiplier sweep (1.0 = rated; attention lock on; margin 5 m); freezes, omniscient = 51:
| latency x | rated awareness | awareness 0.5 |
|---|---|---|
| 0 | 59 | 54 |
| 0.25 | 34 | 26 |
| 0.5 | 36 | 44 |
| 1.0 (default) | 36 | 23 |
Default latency already keeps ~70% of omniscient freezes (36/51); no latency retune needed. Awareness separates only at the default (36 vs 23); elsewhere it is inside noise (about +-8 per 8 games). Awareness is a weak lever today: it scales latency by (1.3-0.4 aw) and noise by (1.3-0.6 aw), so 0.89 vs 0.5 is only ~14% / 23%.
