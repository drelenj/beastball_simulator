# RB/3 scoring physics audit

Base: `3ba853af8dadc59e25ed05e7ed14edfd0a1178db` (RB-3.14). All engine
changes apply only to `native-rb/3`. Roster source: `81f92e3`.

## Reproduce

```sh
python -m native.rulebook.scoring_audit
python -m native.rulebook.scoring_audit --real
python -m native.rulebook.scoring_audit --legacy
python -m pytest -q b1 native
PYTHONPATH=. python native/evidence/rb314/tools/soak_driver3.py --block real --seed 1 --outdir /tmp/rb3-scoring-final/real
python -m native.rulebook.scoring_audit --matches native/evidence/rb314/runs /tmp/rb3-scoring-final
```

Repeat the match command for seeds 3 and 5 and for `--block control --seed 1`
(output in `/tmp/rb3-scoring-final/control`). Real runs and metrics require
`openpyxl` and the roster Git object. Use the same fixture script against the
base commit to get the before results. The fixtures use the actual swept
contact and locomotion kernels, fixed RNG, no other active athletes, and
direct ball injection to isolate release from aim and tactical choices.
The earliest proposed event is reported in the keeper/catch fixtures. The
body-block fixture also commits the event. The forced save intent is a motor
stress case with the course available at the instant of release. The passive
case isolates stationary reflex and body contact.

## A. Keeper

The ball starts 12 m from the plane at the Keeper's standing hand height.
The set Keeper is 3 m deep (the normal quarter-distance positioning from
`native/cognition.py`, supplied here as a fixture). Aiming at centre uses
1.5 m height. Reaction at awareness 0.50 / 0.70 / 0.90 is 200 / 176 / 152 ms
for a set player and 100 ms later for an unset one. Native's sensor latency
is 200 ms. Even an immediately delivered ideal read leaves only 7–60 ms
between reaction and the goal plane. The launch floor is 100 ms.

| 58 m/s aim | Time to depth / centre crossing | Lateral / vertical demand at depth, uniform body | Result after fix, all three awareness values |
| --- | --- | --- | --- |
| Centre (0, 1.5 m) | 155 / 207 ms | 0 / 0.02 m | Stationary reflex parry at 145 ms |
| Low (2.4, 0.4 m) | 159 / 212 ms | 1.80 / 0.84 m | Goal at 213 ms |
| High (2.4, 2.0 m) | 159 / 212 ms | 1.80 / 0.36 m | Frame at 213 ms |

Uniform fixture: 2.55 m height, 1.173 m mapped reach, 1.056 m effective hand
radius. Lateral displacement and airborne lift are zero after the fix in all
nine forced cases. Before it, the forced low shot produced a dive with
about 0.47 m lateral displacement and 0.38 m lift at awareness 0.70, yet
still scored. The high aim is 3.124 m from the centre of the half-disc.
With radius 0.1075 m, the ball centre must be at most 2.8925 m from the
centre for the whole ball to fit.

Real fixture: Garvian Keeper `A:NBL24-07-11`, height 2.279 m and mapped
standing reach 2.963 m, gives a 2.667 m hand radius at 1.413 m upright hand
height. The three event proposals after the fix are stationary catches at
146 / 151 / 152 ms, respectively, for all three awareness overrides with
this seed. The real keeper can catch the high ball before it reaches the
frame even though that trajectory would fail to score.

- DEFECT, fixed: `NativePort.keeper_motor` bypassed the course reaction
  and used old push-off, extension, reach and launch assumptions.
  RB/3 now gates deliberate steps and launches on the observed flight's
  reaction window, ages the forecast from its capture time, and supplies
  the physical geometry and launch limits to `plan_keeper_motor`. Its
  feasible launch geometry uses the same lean-dependent hand offset as
  `core_src/match.py::c4c_off`, and admitted impulses respect the combined
  push/jump budget. The keeper still uses delivered belief for aim.
- CORRECT: `catch_contacts` explicitly permits a stationary reflex before
  deliberate reaction. A centre-line body block also needs no reaction.
- CALIBRATION / mapping question: the workshop standing reach is a height
  above the ground. Its locked mapping (`native/nbl_roster.py` and
  `native/roster.py`) is also used as an isotropic reach around the hands.
  A separate arm-reach input or geometry based on arm span would likely
  reduce wide stationary saves and early field interceptions. It requires
  agreement on the morphology convention and affects multiple rule paths.

## B. Fast-ball acquisition

`core_src/match.py::catch_contacts` treats 120 ms as an exponential time
constant, scaled by awareness. At awareness 0.70, tau is 105.6 ms and hands
are set by 30 / 65 / 100 ms with probabilities 25% / 46% / 61%. The intended
receiver can start during preparation if the pass signal is populated.
The fixture has no intended receiver. At 22 and 58 m/s, seed 1 generates a
field hands acquisition at 64 ms on the central lane. Seed 2 leaves it
untouched. At 58 m/s and a 0.8 m hand offset, seed 1 instead generates a
deflection. There is no field-player body-versus-ball collider on this path.

At the same high speed with hands unavailable, the separate keeper capsule
commits a body touch at 55 ms. Horizontal speed reverses from 58 to about
-17.4 m/s with the 0.30 normal restitution. The flight remains a shot and
no player controls it (`c4c_body`, `catch_contacts`, `Engine.c1_commit`).
Field hands deflection uses 20% of incoming horizontal speed relative to the
player and a randomized direction. It cannot itself award control.

- CORRECT: early hands readiness and body-only rebounds match the specified
  catch kernel. Instant control is a secure hands event, separate from a body hit.
- CALIBRATION: Native's explicitly provisional catch model replaces
  `force × hand travel` with `native_catch_capacity` and changes the
  secure probability exponent from 2 to 8 (`native/substrate.py`,
  `native/rules.py`). At 58 m/s the ball carries about 673 J. Retuning that
  capacity curve or adding a minimum reaction floor would likely reduce
  early field takes and direct catches. Measure hands deflections and body
  rebounds separately before selecting a change. For example, at rating
  0.70 and zero miss the Native capacity is about 1,109 J, giving about 98%
  secure probability conditional on a central 58 m/s hands contact.

## C. Achieved running speeds

| 0.70 runner from rest | 1 s | 2 s | 3 s | 5 s |
| --- | ---: | ---: | ---: | ---: |
| Off ball, before | 8.75 | 17.50 | 26.25 | 27.54 |
| Off ball, after | 8.75 | 17.50 | 26.25 | 31.29 |
| Carrying, before and after | 8.75 | 17.50 | 26.25 | 31.29 |

All values are m/s. The lab uses the normal C3 motor and a virtual runway
with the boundary kept out of the test. Acceleration is 8.75 m/s². It takes
about 3.58 s and 56 m to reach 31.2928 m/s in an uninterrupted straight run.

- DEFECT, fixed: the inherited 0.88 off-ball ceiling in
  `core_src/match.py::c3_move` prevented reaching the mapped top speed even
  in an unobstructed sprint. Native corrects it at load time for RB/3.
- CORRECT: there is no unconditional carry speed penalty. Native already
  counteracted the legacy 0.90 carry multiplier via pace. Braking for near
  targets, holds, collision avoidance and waiting for a release can lower
  in-match speed. This lab does not apportion the observed in-match mean
  across those causes. RB-3.14's typical-opponent cognition estimate still
  uses 0.88 and needs separate cognition review.

The scoring target is a median 76 points per pro team with a realistic
spread. Four seeds are an audit sample. The fixes do not target a particular
shot/carry share or adjust catch parameters to reach a score.
