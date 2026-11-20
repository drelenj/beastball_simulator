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

## TESTED | full-match comparison

Arrows show RB-3.14 → scoring audit → R-1. All four R-1 matches finished
in regulation. The real-roster R-1 median is 58.5 across six team scores
(RB-3.14 27, scoring audit 22). The owner target is a median of 76. These
matches measure both fixes together and do not establish the NBL spread.

| Run | Points A–B | Shots % goal/Keeper/field | Pass INT % (within 3 m) | Tackles | Possessions A/B | Carry attempts/goals |
| --- | --- | --- | --- | --- | --- | --- |
| real-seed01 | 24–16 → 26–18 → 43–66 | 10.5/36.8/45.6 → 10.8/41.0/28.9 → 35.0/36.7/18.3 | 22.5% (28) → 22.4% (28) → 18.3% (3) | 200 → 196 → 63 | 173/174 → 176/177 → 223/224 | 74/3 → 90/0 → 111/2 |
| real-seed03 | 30–43 → 10–37 → 57–88 | 15.5/36.2/25.9 → 4.5/38.6/38.6 → 37.0/38.0/14.1 | 21.3% (26) → 22.2% (17) → 18.7% (9) | 222 → 165 → 54 | 179/178 → 172/172 → 241/240 | 98/6 → 74/7 → 110/2 |
| real-seed05 | 15–35 → 5–33 → 51–60 | 12.0/41.3/33.3 → 11.3/49.1/26.4 → 41.3/36.5/9.5 | 26.0% (30) → 23.2% (33) → 17.8% (10) | 232 → 222 → 57 | 185/185 → 176/175 → 244/244 | 92/2 → 87/4 → 117/2 |
| control-seed01 | 10–13 → 13–27 → 59–83 | 1.9/50.9/24.5 → 13.0/37.0/38.9 → 41.9/32.3/12.9 | 26.9% (32) → 20.6% (23) → 16.6% (6) | 242 → 169 → 78 | 181/181 → 162/163 → 210/211 | 83/0 → 71/1 → 104/4 |

Shots are classified by first resolved outcome. Others are omitted.
Pass interception means first opposing control during the pass sequence.
The 3 m count uses logged release-to-control ball coordinates, a proxy
for the contact point. Tackles count `tackle_count` events. Carry
counters are summed across teams.

The corrected and prior-audit raw logs are compressed and committed
under `native/evidence/rb3-reach/{corrected,audit}/{real,control}`.
The three-build `comparison.json` gives full trace, state, and config
hashes, log paths, and outcome counts by match. The same directory has both
forced drill outputs and all six legacy hash rows. Rebuild the comparison
directly from the archived logs:

```sh
python -m native.rulebook.scoring_audit --matches native/evidence/rb314/runs native/evidence/rb3-reach/audit native/evidence/rb3-reach/corrected
```

The maintained `pytest -q b1 native` suite passed **579 tests and 23
subtests** with one AnyIO deprecation warning. The nine new tests include
six actual-timestamp checks for passes and shots. Existing lane and
pressure fixtures use distances appropriate to the corrected body. The
corridor-edge tests now compare in world coordinates to avoid loss of
precision at exactly legal placement. The production corridor code is
unchanged.

Every legacy trace hash, state hash, and config digest matched `185b557`
for 3,000 steps at seeds 1 and 3 on `native-v0/2`, `native-v0/3`, and
`native-rb/2`. All four R-1 runs recorded a restart-completion ratio of 1.0.
