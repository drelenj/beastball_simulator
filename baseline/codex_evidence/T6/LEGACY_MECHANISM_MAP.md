# Legacy Mechanism to Native Interface Map

This is a design crosswalk, not an implementation plan. “Preserve in B0” means
the legacy adapter retains current behavior and call order for Gate A. “Future
boundary” describes B1/native ownership and is not authorized by T6.

## 1. Mechanism crosswalk

| Existing mechanism | Current effective ownership | Future interface boundary | B0 preservation rule |
|---|---|---|---|
| Carrier option/policy selection | PRISM/legacy policies, with final carrier-target override in Pocket 4 | cognition emits `CarryIntent`, `PassIntent`, or `ShotIntent`; MC cannot retarget | Keep historical wrapper/override order and RNG consumption |
| Pass and shot preparation | `make_pass` / `make_shot`, pending-action pose delay | cognition selects action; MC emits pose/preparation and scheduled release commands | Preserve delay and pending action exactly |
| Throw/release sampling | Pocket 4 `Engine.release` wrapper plus legacy release | MC computes action-specific execution/error from own state; PHY creates ball release | Preserve sampled values, call order, and ball state |
| Historical kick | legacy action path; RULES_V03 is off in B0 | typed kick intent/command only if an approved ruleset includes it | Do not remove or suppress in B0 |
| Locomotion target | stacked position/route wrappers, legacy positions, Pocket 4 targets | cognition emits movement destination/route belief | Preserve target chain for Gate A |
| Desired velocity, acceleration, brake, turn | C3 `c3_desired` / `c3_move`, capability data | MC converts movement intent to locomotor command; PHY integrates | Replay current values/order through adapter |
| Receiver routing | `route_receiver` uses true ball path and can force immediate decision | receiver cognition estimates intercept; MC executes route; PHY resolves intersection | Preserve true-state reroute only in B0 adapter |
| Automatic catch | legacy `catch_contacts` physical check | B1 `CatchPrepareIntent` → reach/takeoff commands → PHY grasp/contact | Keep automatic B0 catch behavior |
| CATCH_V2 readiness/security | optional catch capacity/security and jump hooks | readiness is cognitive/motor; capacity and grasp are PHY | Separate feature config from historical B0 |
| Jump | optional hook can alter movement and cadence | cognition owns takeoff choice, MC command, PHY trajectory/landing | Preserve only in its controlled feature configuration |
| Hand fight | optional hand-contact contest wrapped around movement | deliberate reach/position is intent/MC; contact and rating contest are PHY | Preserve optional flag and resolution order |
| Carry pose/maneuver | optional pose engine mixes threat lookup, motion, tackle/strip | cognition chooses maneuver; MC owns pose transition; PHY owns tackle/strip | True-threat lookup remains only in legacy adapter |
| Tackle/contact | intent/policy mixed with C3/engine collision | cognition selects attempt; MC prepares region/brace; PHY resolves contact | Preserve contact kernels and event order |
| Fatigue/condition | authoritative state updates and capability limits | PHY owns accumulation/recovery; MC reads true self limitations; cognition sees approved self view | Preserve equations and update order |
| Ball flight/bounce | legacy/Pocket 4 physical advance and bounce hooks | PHY exclusively owns release-to-rest trajectory and collision | Exact command replay target for Gate B |
| Carry pose attachment | engine ball/carry attachment | PHY owns ball attachment to body and state transitions | Preserve placement/order |
| Archer lane choice | current wrappers include true ball/engagement access | Archer cognition emits lane intent from view/belief | Preserve legacy behavior only in B0 adapter |
| Archer load/draw/aim/release | partly automatic and partly wrapper-driven | separate load, draw, aim, hold/release intents; MC execution; PHY arrow creation | Preserve ammo/draw/release ordering in B0 |
| Arrow flight/hit/freeze | engine `advance_arrows` / impact processing | PHY and rules own flight, hit, freeze/immunity, legality | Exact physical fixture required before parity claim |
| Keeper positioning/interception | PRISM Keeper wrapper uses beliefs but retains true-state paths | Keeper cognition selects intent; MC step/dive/jump; PHY contact | Preserve reverse-flight pathology in bounded B0 diagnostic |
| Substitution/team management | match/rules logic and legacy hooks | rules/team-management service, not athlete MC | Preserve accepted schedule and events |
| Restarts/dead-ball positions | rules plus positional controllers | rules service owns constraints; cognition owns choices within them | Formation-free work cannot weaken rule-required placement |

## 2. Verified source anchors

Line numbers refer to the accepted `2abe497` source snapshot in this workspace.
They identify implementation evidence; they do not imply that the function is a
clean owner today.

| Mechanism | File and line |
|---|---|
| Base release | `repo2abe497/Beastball Pocket 2 0(1).py:1077` |
| Arrow shoot / impact | same file `:1756`, `:1785` |
| Legacy position target | same file `:3294` |
| Pocket target override | same file `:3470` |
| Move players | same file `:3521` |
| Pass / shot / carrier decision | same file `:3645`, `:3683`, `:3703` |
| Arrow decision | same file `:3757` |
| C3 desired / move | same file `:3990`, `:4059` |
| Ball / catch / arrow advance | same file `:4877`, `:4956`, `:5119` |
| Receiver reroute | same file `:5294` |
| Pocket 4 release wrapper | `repo2abe497/pocket4_proto.py:168` |
| Pocket 4 step / Arrow / shot hooks | same file `:363`, `:412`, `:506`, `:551` |
| Catch feature | `repo2abe497/catch_v2.py:21`, `:24`, `:35`, `:62` |
| Hand fight feature | `repo2abe497/hand_fight_v0.py:24`, `:50`, `:91` |
| Pose feature | `repo2abe497/pose_engine_v0.py:69`, `:87`, `:104`, `:143`, `:161` |
| Condition feature | `repo2abe497/condition_layer_v2.py:45`, `:53`, `:58`, `:68` |
| Locomotion/fatigue advance | `repo2abe497/beastball_locomotion_v37.py:95` |
| Capability-to-Pocket bridge | `repo2abe497/locomotion_bridge_v1.py:46`, `:55` |

## 3. Focus and rating boundary

Current PRISM Focus controls attention, perception, memory, or belief behavior.
T6 does not assign Focus a motor-accuracy effect. MC uses the action-specific
physical inputs already used by the historical path when operating in B0 mode.
Giving Focus a release, catch, aim, or locomotor error effect would change rating
semantics and requires explicit canon approval, calibration, and Gate C tests.

True opponent ratings may affect PHY when two bodies or implements interact.
They may not be exposed as cognition or MC targeting inputs. Population priors
and observed morphology remain separate from individual true attributes.

## 4. Adapter discipline

The historical adapter may invoke legacy functions and record unavailable
details, but it MUST expose that provenance as `legacy_table` or
`legacy_not_exposed`. It MUST NOT pretend a legacy automatic choice was an
athlete-authored B1 intent. Conversely, the future B1 path MUST NOT use the
adapter as a backdoor to recover true state.
