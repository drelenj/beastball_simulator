# ATTR-1 speed-literal audit

Scope: active Native paths in `native/` and the privately loaded `core_src/` substrate. This is an engineering inventory, not a gameplay-quality claim.

| Location | Literal/coupling | ATTR-1 disposition |
|---|---|---|
| `native/config.py` legacy `POCKET`, `NativeConfig.body_standards` | 27 m/s player/pass, 40 m/s ball limit, 29/30 m/s arrow | KEPT byte-identical for native-v0/2. |
| `native/config.py` `NativeConfigV3` | 250/27 arrow ratio | KEPT byte-identical for native-v0/3. ATTR uses fixed 250 m/s and no ratio. |
| `AttrConfig` pocket | `player_speed=44.704`, `ball_limit=134.1`, no `pass_speed`, no arrow cap | CHANGED for ATTR. Per-athlete admission is narrower than the global substrate ceiling. |
| `native/cognition.py`, `native/cognition_v3.py` release intent | 27 m/s | KEPT as Claude-owned primitive choice. `min(27, own max)` means a larger maximum changes nothing until cognition chooses it. |
| `native/cognition.py` pass-flight heuristic | distance/27 | KEPT as Claude-owned decision heuristic; it does not constrain physical execution. |
| `native/cognition_v3.py` fallback movement speed | 27 m/s | KEPT only for views lacking a body. ATTR views always contain the athlete's own mapped body. |
| `native/port.py` ingress | historical 40 m/s | CHANGED for ATTR to the thrower's mapped maximum; legacy profiles retain 40 exactly. |
| `native/port.py` release execution | historical uniform-skill/Gaussian direction error | CHANGED for ATTR: uniform half-width is `sqrt(3) * requested_SD`, so the uniform distribution has the specified SD. Legacy path is unchanged. |
| `native/port.py` arrows | v0/3 config-derived speed | CHANGED for ATTR to fixed 250 m/s, independent of any roster. |
| `core_src/engine.py` release/restart ceiling | pocket `ball_limit` default 40 | KEPT substrate code; ATTR adds per-athlete engine wrappers and uses 134.1 only as the global ceiling. |
| `core_src/match.py` pass planners and 27 m/s recipient time | legacy controller paths | KEPT because Native traps/retires these tactical controllers. They do not execute in ATTR. |
| `core_src/match.py` player movement caps | per-athlete `maximum_speed`, acceleration, braking, turning | ADOPT mapped attributes. ATTR carrier lab uses pace normalization so the capability ceiling can be measured exactly. |
| `core_src/match.py` 40 m distances | field/restart geometry | KEPT; these are metres and rules geometry, not speed constants. |
| `core_src/match.py` conversion-table 40/50 m/s | retired controller drill table | KEPT; Native does not invoke that controller. |
| `core_src/engine.py` legacy arrow/equipment 30 m/s checks | legacy or bypassed by no-cap Native v0/3 rules adapter | KEPT in frozen substrate. ATTR's active arrow admission is fixed 250 m/s with no cap. |
| `core_src/types.py` `maximum_speed<=44.704` | engine limit | KEPT. ATTR private validation permits the canon zero endpoint while retaining the 44.704 ceiling. |

At 100 ms, one 44.704 m/s athlete can travel 4.4704 m and two can close 8.9408 m. ATTR conformance exercises the C3 swept contact kernel and a boundary-crossing endpoint. The engine detects the collision without relying only on final overlap, and boundary adjudication sees the out-of-bounds endpoint. No time-step change was required by these tests.

`passing` receives `throw_accuracy` for schema compatibility. The active Native ball motor does not read `passing`; ATTR applies throw accuracy once through its uniform direction error. The retired substrate pass planners remain trapped, so the rating is not applied twice.

