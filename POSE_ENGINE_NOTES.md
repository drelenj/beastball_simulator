# Poses + maneuvers in the Pocket 4.0 engine (v0.3, flag PRISM_MANEUVERS=1)

`PRISM_MANEUVERS=1 python3 pocket4_proto.py ...` installs `pose_engine_v0.py`. Flag off: nothing is installed, the engine is untouched.

## What is wired [all numbers P]
- **Pose FSM** per ball carrier (`pose_maneuvers_v0.Carrier`): loaded/extended/exposed/tucked/braced, adjacent steps, tell then execution. The throw-release delay (POSE system) now reads this pose. Policy outside maneuvers: tucked with a defender inside 8 m, else exposed.
- **Maneuver policy** (placeholder, own ratings only, no PRISM belief yet): 10 Hz, a defender inside 7 m and closing at 6+ m/s; choose none / juke / spin / stiff-arm / truck by a rating-weighted value; 1.2 s cooldown. Legal poses and tells follow spec v0.1.1.
- **Motion**: juke and spin move the carrier laterally (agility) over the execution time with a speed cost. This is a position nudge, not a steering command: the engine's controllers re-set targets each step. Knob `PM_NUDGE`.
- **Tackle** (grounding commit, `Engine.tackle`): an executing maneuver can defeat it with a rating-contest probability (juke/spin agility, stiff-arm and truck strength/mass). Logged as `maneuver_evade`.
- **Strip** (`Engine.strip`): a kernel-scheduled strip is accepted with (1-resist[pose])/(1-resist[tucked]), floor .1, cap 1. So Braced reduces strips; Exposed/Extended/Loaded cannot raise them above what the kernel scheduled (limit of filtering a scheduled event).
- **Contact** aborts transitions, tells and pending maneuvers.

## First numbers (short games, seeds 1-12, generated teams)
| | goals | tackles | strips | poss. changes |
|---|---|---|---|---|
| flag off | 131 | 356 | 42 | 474 |
| on, nudge 0 | 121 | 348 | 33 | 474 |
| on, nudge 1 | 156 | 390 | 43 | 499 |
Carrier cleared (no grounding within 1.5 s of the start): juke 73%, spin 73%, stiff-arm 83%, truck 71%, vs 44% in the few 'no maneuver' control cases at the same trigger (n=9; too small). Goals +19% at nudge 1 is at the edge of game-to-game noise (+-10%). Nudge 0 clears as often as nudge 1, so most of the survival comes from the tackle-evade contest and the short maneuver window, not the displacement.

## Limits / open
- Defender engine controllers do not read tells or use PRISM (carrier-only). Defender PRISM is the next step; the lab's defender layer is the model.
- Motion is a position nudge; a steering-level juke needs the c3 controller targets.
- Maneuver policy is a placeholder; Judgment/Instinct should drive it with the carrier's beliefs (PRISM_FIELD).
- Poses do not yet change grip/wrap quality or the kernel's contact impulse; only strips and groundings are filtered.
- Control sample is small; run more seeds before reading the goal effect.

Files: `pose_engine_v0.py`, `pocket4_proto.py` (hooks), `test_pose_engine.py` (5 checks, flag-off determinism + flag-on state), `sweep_maneuvers_engine.py`.
