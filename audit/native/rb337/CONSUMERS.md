## Traction implementation and consumer audit

DESIGN COMPLETE and IMPLEMENTED in `570fd12`. The three-tackle T3 rules and the same planned-rotation settings apply in all arms. The trial changes braking and lateral acceleration for all bodies, from field players to Keepers and Archers, wherever their movement uses those parameters. Traction is applied once when constructing the body from the roster. It leaves acceleration, top speed, Agility itself, ratings data and sport rules unchanged.

- Turning = 16.25 × Agility × traction scale (m/s²).
- Braking = 16.875 × Agility × traction scale (m/s²).
- L0 uses 1×, L1 uses 1.5×, and L2 uses 2×. The default value is omitted from the serialized config so historical config digests remain replayable.
- At 0.70 Agility, braking is 11.81, 17.72 and 23.63 m/s². The corresponding reactive set speeds, braking × 0.40 s, are 4.73, 7.09 and 9.45 m/s. Fresh-body turning radius is v² ÷ turning. Fatigue still acts on the mapped body during play.

| Consumer | Source of braking or turning |
| --- | --- |
| `core_src/match.py`: `move_players`, `update_archers`, `c3_desired`, `c3_move`, `c3_free`, `c3_run` | Desired speeds, lateral steering, slowing for contact, player-motion bounds and braking. The contact solver caches mapped body values for the current step. |
| `core_src/match.py`: `c4c2_engage_s`, `c3_driven`, `c3_no_time`, `pocket_receiver_position` | Tackle, reach and receiver motion estimates use the participating body's value. |
| `core_src/engine.py`: `recovery_committed`, `exit_run`, `zone_compliance_time`; `core_src/geometry.py`: `intercept_xy` | Recovery and zone-exit timing, steering and receiver lead use body values. |
| `native/port.py`: `body`; `native/cognition_rb3.py`: `time_to_cover`, `typical_time_to` | Own-body braking feeds stopping and reversal estimates. On scaled arms, the nominal opponent reversal estimate is derived from the same mapping at 0.70 Agility and passed as a public constant. It has no access to opponent attributes. |
| `native/turnovers.py`: `boundary_risk`; `native/paired_policy.py`: `boundary_aim`; `native/ladder.py`: `brake_target` and its clamp | Projected stops, legal aim and reactive locomotion braking read the mapped braking value through the athlete view or engine body. |
| `native/reaction_clock.py`: `set_speed`; `native/substrate.py` Keeper unset patch | The threshold reads the body's braking. The 0.40 s multiplier remains the same for everybody. |
| `native/restart_metric.py`: `observe`; `native/rulebook/fatigue_rotation.py`: `advance` | Restart timing estimates and fatigue work read mapped braking. The fatigue baseline caches the mapped values once, before applying existing fatigue multipliers. |
| `core_src/policies.py` history and marking helpers; `core_src/match.py`: `pocket_init` | The legacy readers consume their body values. The old roster initializers and optional Pocket Keeper override are bypassed on the Native roster path. They retain their historical settings for older profiles. |
| `native/roster.py`, `native/port.py`, `core_src/types.py`, `native/attr_sensitivity.py`, `native/prism_lab.py` | Mapping, attribute validation and diagnostic readbacks. |

The RB/3 trial uses one body source for braking and turning. Historical profiles still use their historical defaults. The second pairing's signed margin is Isu’Kari minus Yukïma, and the first pairing's signed margin is Ala minus Garvian.
