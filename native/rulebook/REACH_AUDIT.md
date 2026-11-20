# R-1 | RB/3 reach and release clock

Engine commit `a56098640435ee73621a0ec2aac0d407bb3ab64a`, based on scoring
audit `60a11bb66a383c8bd1795b99dd8a44d02d5623da`. Roster source `81f92e3`.

## IMPLEMENTED

The NBL adapter stores half of workbook **Arm span (m)** as arm reach and
preserves **Standing reach (m)** separately. The RB/3 control body is
2.39 m tall and 226 kg, with 1.26431 m arm reach and 3.05 m standing reach.
CSV arm reach retains its existing meaning and default. The optional
standing measure stays in the roster record and the RB/3 engine body.
No collision, motor, rules, or cognition path consumes it in this change.

| Consumer | Reach semantics |
| --- | --- |
| `core_src/match.py` C1 and fallback catches, and pocket catch forecast | Arm reach around the hand point. Native uses a 0.9 multiplier for field athletes and Keepers. |
| `c4c_reach`, `native/port.py::body`, `b1/emergence_intents.py::plan_keeper_motor` | Arm reach for the intercept sphere, combined with the audited lean, push and jump geometry. The separate Keeper body capsule uses height and radius. |
| `core_src/match.py` lane pressure, C3 broad phase and hold reach; `core_src/engine.py::contact_legal` | Arm reach combined across two bodies, at 0.7 times summed arm reach plus radii in the contact gate. |
| `core_src/engine.py::acquire`, `strike`, `follow_carrier` | Arm reach for horizontal acquisition clearance, legacy strike clearance, and held-ball offset. The broad vertical acquire sanity check uses height plus arm reach. Native hands contacts also have to pass the narrower, swept hand-sphere test. |
| `core_src/match.py::update_keepers_jump`, legacy pocket setup and `core_src/policies.py` interception forecast | Arm reach as a height-relative offset or reach around hands. Legacy paths keep their own configured values. |
| `native/rulebook/formation.py::acquisition_radius` | Actual arm reach plus radius plus 0.2 m. Corridor half-width is the largest active field acquisition radius plus 1 m, with the existing 2 m floor. |
| `RulebookView.body_reach`, `AthleteBody.reach`, RB-3.14 lane estimates | Public perceived-opponent arm reach and own arm reach. Values are delivered through the existing view fields. Cognition retains its old body-less synthetic fallback and typical-opponent speed estimate. |
| `native/rulebook/scoring_audit.py`, B1 drill and emergence adapters | The audit reports both measures. Acquisition and adapter thresholds use arm reach. |

The shared clock is `NativePort.own_release_ms`. For RB/3 open-play passes
and shots it returns `round(pass_release_ms * (1.35 - .5 * ball_handling))`.
This adopts the throw-specific handling formula and nearest-millisecond
rounding used by Sonnet's view at `9fc4f51`. The legacy shot wind-up
references kicking and is outside this path. Both RB/3 view spellings
(`own_release_ms` and the RB-3.14 compatibility field `pass_release_ms`)
read the shared answer. The motor stops the physics interval at the due
time so it does not quantize execution to the next 100 ms tick.
Other action timings and historical profiles keep their existing behavior.
Tests compare the serialized view, scheduled command, and emitted event
for 278, 250, and 230 ms delays, for both action kinds.

## TESTED | forced scenarios

The 58 m/s shot starts 12 m away, with a set Keeper at 3 m depth. Reaction
at awareness 0.50 / 0.70 / 0.90 is 200 / 176 / 152 ms. The ball crosses
Keeper depth at 155–159 ms and the goal plane at 207–212 ms. Both bodies
showed zero lateral displacement or dive in all three awareness cases,
including the injected immediate-save intent. Centre aim uses 1.5 m height.

| Aim | Control (1.137879 m hand radius) | Garvian Keeper A:NBL24-07-11 (1.12815 m radius) |
| --- | --- | --- |
| Centre | Catch at 145 ms | Catch at 146 ms |
| 2.4 m wide, 0.4 m high | Goal at 213 ms | Goal at 213 ms |
| 2.4 m wide, 2.0 m high | Frame at 213 ms | Frame at 213 ms |

The Garvian Keeper's standing reach is 2.963 m and arm reach is 1.2535 m.
The prior audit's 2.667 m hand sphere reached all three paths. The high
aim itself is outside the whole-ball aperture. The corrected Garvian
Keeper's lateral/vertical demands at depth are 0.00/0.10, 1.80/0.72, and
1.80/0.48 m.

| Field lane | 22 m/s, three seeds | 58 m/s, three seeds |
| --- | --- | --- |
| 1 m, control | 2 catches, 1 untouched | 2 deflections, 1 untouched |
| 1 m, Garvian field athlete | 2 catches, 1 untouched | 2 catches, 1 untouched |
| 2 or 3 m, either body | All untouched | All untouched |

The 2 m and 3 m paths also stayed untouched in the primed-hands control
test. The forced Keeper body hit still deflected at 55 ms (about −17.4 m/s
horizontally, no holder). The running lab still reached 8.75, 17.50 and
26.25 m/s at 1, 2 and 3 s, and 31.2928 m/s at 5 s, with and without the ball.

Catch capacity, readiness/reaction, body restitution, and play policy
remain at the scoring-audit values. If post-integration evidence still
shows frequent early acquisition, compare separate readiness and secure
control curves before proposing changes to either.

## Reproduce

```sh
python -m native.rulebook.scoring_audit
python -m native.rulebook.scoring_audit --real
python -m native.rulebook.scoring_audit --legacy
python -m pytest -q b1 native
python -m native.rulebook.reach_run --block real --seed 1 --outdir /tmp/rb3-reach/real
```

Repeat the match command for real seeds 3, 5 and control seed 1 (use
`--block control --outdir /tmp/rb3-reach/control`). Both match blocks call
`native/run.py::run_match`. Real-roster commands need `openpyxl` and the
roster Git object.
