# PRISM individuation ownership audit

Independent audit target: implementation commit `d1845d022625ddaf6d0f9d5ddc5e60179c63be34`.

## Data and view boundary

`native/roster.py` validates normalized own attributes and stores them in `AthleteAttributes`. `native/port.py` copies the allowed own ratings into `native_individual` only when the opt-in mapping is enabled. `RulebookPort.view()` sends the active athlete's own body/skills and draft ratings through the existing `AthleteView`; teammate/opponent private technical and mental ratings are not included in tracks. Position, body height, mass, and arm reach may be exposed as public physical facts through separate view fields. The focused poison test changes another athlete's rating at equal positions and confirms the receiver's view is unchanged.

The own ratings used by cognition are: anticipation, instinct, judgment, playmaking, finishing, marking, zone reads, goalkeeping, in-air/live-ball pursuit, carrier duel, defender duel, and goalkeeper positioning inputs. Vision, clarity, focus, reaction, touch, and motor control are applied by the existing sensor, scheduler, or motor interfaces. Physics reads the existing athlete physical record for motion, contact, fatigue, catch, and Keeper/Archer execution. I found no new cognition path that reads true opponent ratings, future positions, hidden ball state, another athlete's intention, or an RNG result.

## Decision-to-outcome chain

The implementation uses the established sequence: `ObservationFrame` → `AthleteView` → `BeliefState` → `decide()` / `ActionIntent` → admission and `MotorCommand` → execution by Native physics → rulebook outcome. The experimental code changes inputs already available to those stages. Motor steering quantization and touch pitch allocation act after a chosen intent and leave feasible physics to resolve the result. The rulebook's legality and scoring stay separate.

The evidence is incomplete for per-decision reconstruction requested by the audit: the match result contains decision-kind totals and replay events, but no compact, stable record for every decision linking raw observations, belief revision, every alternative, admitted motor command, and adjudication. Focused tests demonstrate the chain for selected scenarios, not for every decision in a match. Record this as UNVERIFIED for full decision provenance, not as proof of an ownership violation.

## Independence and collisions

| Pair / field | Finding |
|---|---|
| Throw Accuracy / `passing` | `mapped_values()` sets `passing = throw_accuracy`; Native release yaw reads the canonical throw error. This is a deliberate single-source compatibility alias, not two independent effects. |
| Kicking | The NBL adapter sets `kicking=0`; Native action vocabulary has no kick. Historical `core_src` retains legacy kicking expressions. The Native non-use test and obsolete `kick_power` rejection pass. |
| Awareness / Vision / Clarity | Awareness scales horizontal/position noise and retains legacy Keeper-response use; Vision sets field-of-view; Clarity changes vertical ball-sample noise. These are separate axes, but Awareness's Keeper timing and Reaction's general decision cadence are a conceptual overlap. No joint factorial test quantifies it. |
| Reaction / fixed timing | Reaction scales cognitive decision interval only. Release preparation, sensory delivery, Keeper course response and motor execution retain separate clocks. This distinction is documented and a scheduling test passes; dense restart scheduling and queue effects are not fully tested. |
| Anticipation / Judgment | Anticipation scales perceived receiver velocity used by the lead solver. Judgment changes defender lane evaluation. They are separate code paths; no factorial interaction or accuracy study was run. |
| Touch / Ball Handling | Touch changes the vertical allocation of an admitted in-play throw while conserving magnitude; Ball Handling controls release preparation and legacy secure/touch physics. The narrow vector test supports separation; broader ball-control interactions are unmeasured. |
| Finishing / Throw Accuracy | Finishing changes shot-option valuation through keeper clearance; Throw Accuracy changes release yaw. Tests show different option data and a different release vector, but no full shot-selection/outcome attribution. |
| Goalkeeping / Keeper Skill | Goalkeeping changes Keeper positioning from a delivered course. Keeper Skill changes available push-off fraction. They affect separate positioning and execution inputs; no Keeper save-rate factorial was run. |
| Contact Resistance / Balance | Loader accepts independent Contact Resistance. The current NBL workbook lacks it, so the documented compatibility fallback sets it equal to Balance. This is not independent in default roster data. |
| Motor Control / technical precision | Motor Control quantizes movement headings; Throw Accuracy and Touch shape release vectors. Existing tests confirm distinct interfaces, but not a full motor/contact interaction matrix. |
| Playmaking / passing decisions | Playmaking changes a carrier's receiver-space option value. It does not replace legal-lane filtering. Existing evidence establishes option-value change, not more or better passes. |

`native/individuation.py::effect()` is a shared bounded-linear helper, but effects are rating-specific and applied at separate named decision sites. It is not a universal multiplier. A remaining measurement gap is the probability that an option-value change changes the selected action under repeated matched seeds.

## Full input and shared-parameter inventory

| Input / parameter | Current handling |
|---|---|
| Height, mass, arm reach | Height and mass load directly to the body. `reach_m` is the engine arm-reach field; the NBL adapter converts Arm span to half-span. Standing reach is retained separately when present and is not substituted for arm reach. Body radius, eye/hand height and reach-derived physical geometry remain engine derivations. |
| Acceleration | Optional normalized rating; maps directly to acceleration with the RB/3 profile shape. Braking and turning remain agility-derived. |
| Durability, Injury | Optional normalized fields; validated and digested but not active. Durability susceptibility is not current injury state. Active injury is only the existing forced rulebook state; no stochastic model is introduced. |
| `passing` | Legacy field assigned from `throw_accuracy`; one canonical input, not independently configurable in the canonical roster schema. |
| `kicking` / `kick_power` / `kick_accuracy` | `kicking` remains in the shared substrate for compatibility, set to zero by Native roster mapping. Kick columns are not admitted as canonical roster attributes and no Native kick command exists. |
| `decision_speed` | Legacy fixed compatibility value `.3`; experimental `reaction` controls the Native decision interval through its separate mapping. |
| Arrow speed | Fixed universal `250 m/s`; independent of athlete speed and Archery Accuracy. |
| Throw speed ceiling | Athlete-specific from Throw Power; the speed unit and ball physics remain shared. The task does not change cognition's choice of release speed. |
| Simulation cadence, field/goal geometry, gravity, ball-material config | Shared configuration/physics values; they are not converted into athlete ratings. |
| Release clock base | Shared 250 ms base scaled by Ball Handling; this is separate from Reaction's decision cadence. |

Legacy and shared inputs were checked in the inspected Native path plus full test suite. No exhaustive static enumeration of every numeric constant in frozen `core_src` is asserted; historical code remains outside the active Native behavior where noted.

## Outcome caveats

High and low ratings remain fallible in the mechanics: every effect changes a perception, decision input, or feasible command; none writes a success result. However, the validation did not estimate low/high success probabilities for the full set of ratings, so the frequency of successful high-rated and low-rated outcomes remains UNVERIFIED. The workbook's draft ratings default to 0.70; real per-player differentiation in those fields is unavailable until independently authored data is supplied.
