# PRISM v0.1.1 - Draft Specification: Perception and Information (draft for DreLen and the lead)
Status: DRAFT, revised after Codex review (changes in section 13). Every number marked **[P]** is a provisional placeholder so the stage can be built and tested; none is canon. Ratings are the only per-athlete knobs. Physical quantities (eye height, body size, positions) come from the engine.

## 1. Principles
1. No athlete reads the engine's true state. It acts on its own belief, built from what its two sensors return.
2. Two sensors: a **cone** (vision: detailed, directional, blocked by bodies) and a **radar** (awareness: coarse, all-around, short range).
3. Vision and Awareness set the **size** of the cone and radar. The other ratings set **how well each works**.
4. Public information is exempt from sensing (rule, DreLen 30 Oct): freeze status and immunity status of any player are known to everyone.
5. The same code path serves all 12 athletes. Role changes the viewpoint, the facing and the available actions, not the model.
6. PRISM decides what is attempted. The physical solver decides what happens.

## 2. Rating set (0-1 scale, your naming)
| Rating | Controls | Sensor |
|---|---|---|
| Vision | Cone angle and reach | cone size |
| Awareness | Radar radius | radar size |
| Clarity | Reading accuracy inside the cone; how gradually the cone edge fades | cone quality |
| Reaction | Delay before cone or radar information arrives | both |
| Focus | Number of players tracked sharply; radar pulse rate; gaze shift speed; how long beliefs last (memory folded in) | both |
| Instinct | How fast a sighting or blip is recognised as a threat, opening or nothing | recognition |
| Anticipation | How well it predicts movement and intent | inference |
| Judgment | Quality and speed of choosing an action | strategy |
`awareness` in today's roster files becomes the Radar-size rating; `decision_speed` (engine only) folds into Reaction and Judgment. Rating to parameter mapping is linear unless stated (curves are an open question, section 12).

## 3. Cone (vision)
- Eye point: the athlete's eye position (platform Archers: platform height + 0.72 x body height). Facing: body facing; gaze: a point inside the cone that moves toward whatever the athlete is attending to.
- Half-angle: `theta = 60 + 60 x Vision` degrees **[P]** (today's Archer: 100).
- Reach: `R_cone = 40 + 60 x Vision` m **[P]**. Beyond reach nothing is sensed through the cone.
- Fovea: inner cone of half-angle `15` degrees **[P]** around the gaze; full-quality detection there.
- Edge softness: detection probability outside the fovea falls smoothly from 1 to 0 across the band between fovea and edge: `p(e) = clamp(1 - ((e - fovea) / (theta - fovea))^k)` with softness exponent `k = 3 - 2 x Clarity` **[P]** (high Clarity = sharper edge, low Clarity = fuzzy, early fade). Today's code uses a flat `0.35 + 0.40 x awareness` outside the fovea; this replaces it.
- Reading noise (position sigma, m): `sigma = (0.01 + 0.0025 x range) x (1 + 2 x off_axis) x (1.6 - 1.2 x Clarity)` **[P]**, where `off_axis` = angle from gaze / half-angle. Velocity is derived from successive readings (section 7).
- Occlusion: a player is visible if a line from the eye to its torso (0.55 x height) or head (0.95 x height) is not blocked by another body's cylinder. Occluded players are never detected through the cone (tested).
- Tick: 10 Hz **[P]**.

### 3a. Detection is not identification (added v0.1.1)
Every sensor return creates a **contact**, not a known player. Contact states: `detected` (something is there: position blob, no identity, no class) -> `identified` (who it is, team, role) -> `classified` (threat / opening / neutral, section 6). Moving from detected to identified needs attention: the contact must be inside the fovea or among the K sharply tracked players (section 5), and identification takes `D_id = 0.15 x (1.5 - Focus)` s **[P]**. A wide Vision cone therefore lets an athlete notice many things but only identify K of them at a time. Peripheral and radar contacts stay `detected` until attended. Unidentified contacts can still drive coarse reactions (turning the gaze toward a contact that is closing).

## 4. Radar (awareness)
- Omnidirectional and not blocked by facing. **Interpretation (proposed, needs DreLen's decision, question 7): radar is an abstraction of hearing, peripheral motion cues and spatial intuition, not a literal sense.** So it is not supernatural: (a) detection probability per pulse rises with the contact's speed (a still body is quiet, a sprinter is loud); (b) bearing is noisier than range (`bearing sigma = 25 - 15 x Awareness` degrees **[P]**); (c) each body between sensor and contact attenuates detection probability by `x0.7` **[P]** (partial obstruction, never total); (d) crowding masks: noise grows `+10%` per additional contact inside the radius **[P]**.
- Radius: `R_radar = 3 + 12 x Awareness` m **[P]**.
- Pulse: one sweep every `T = 0.50 - 0.35 x Focus` s **[P]**. Each pulse returns a **blip** for every body inside the radius: coarse position (sigma = `0.5 + 0.1 x range` m, **[P]**, independent of Clarity), no identity beyond team side, no velocity from one pulse. Velocity comes only from two consecutive blips (so a low-Focus athlete knows someone is behind it, but not how fast it is closing).
- A blip that lands inside the cone's coverage is superseded by the cone reading.

## 5. Delay (Reaction) and attention (Focus)
- Delay: `L = L0 x (1.3 - 0.6 x Reaction)` s with `L0 = 0.25` **[P]** (Archer today: `decision_speed x (1.3 - 0.4 x awareness)`; the Keeper engine rule is `0.2 x (1.3 - 0.6 x awareness)`).
- Radar returns arrive `+0.1 s` after cone returns **[P]**.
- Attention lock: the athlete's current focus target (the player being drawn on, tracked, or the ball carrier) is processed at `0.5 x L` **[P]**. Sharply tracked count: `K = 1 + round(4 x Focus)` **[P]**; players beyond K are updated at the radar rate only.
- Gaze shift speed: `120 x (0.6 + 0.8 x Focus)` deg/s **[P]**.
- Belief persistence: confidence decays with time constant `tau = 1.0 + 3.0 x Focus` s **[P]** (memory folded into Focus).

## 6. Recognition (Instinct)
- Each new sighting or blip is classified by role context into threat, opening, or neutral, after `D = 0.30 x (1.4 - 0.8 x Instinct)` s **[P]**. Until then it is in the belief store as an unclassified contact. Examples: an unclassified body closing on the carrier from behind; a free receiver in a lane.

## 7. Inference (Anticipation) - what the stage must contain, from what we measured
- Belief record per contact: id (or blip), position, velocity, timestamp, source (cone, radar, communicated), confidence, class.
- Velocity: windowed regression over 0.4 s (best of nine estimators tested; windows of 0.3-1.0 s, alpha-beta and quadratic fits all did no better).
- Prediction: constant-velocity extrapolation through the delay and flight time, blended toward an intent model by Anticipation: `w = 0.7 x Anticipation`. The intent model is unbuilt (open item). **Do not** use a self-assessed hit-probability gate: the v0 one was uninformative (flat 7% hit rate across estimate quintiles).
- Measured anchors (Archer, 250 m/s arrows, 15 m platform): sensor noise alone leaves ~0.2 m median position error, delay alone ~1.5 m, so delay (Reaction) dominates aim quality; a 5 m margin inside legal range took belief-archer freezes from 6 to 36 (omniscient 51).

## 8. Strategy and Judgment (revised v0.1.1)
- Mistakes should come from imperfect beliefs, incomplete options and time pressure, not from injected random error. Judgment sets how well options are evaluated, not how often a coin is flipped.
- Options considered: `N = 2 + round(4 x Judgment)` candidates, chosen by a cheap ranking from the belief (nearest, most open, most valuable by simple heuristic); the rest are never evaluated. Evaluation horizon: `0.5 + 1.5 x Judgment` s of look-ahead **[P]**. Under time pressure (short clock, contact imminent) the athlete evaluates fewer options: `N_eff = min(N, floor(time_available / 0.15 s))`.
- Decision interval: `0.2 x (1.5 - Judgment)` s **[P]**.
- Tactics (formation, membrane duties) shape the option set and its priorities; they never override rules.
- Safety margins are Strategy: for example the Archer's 5 m inside the legal range.
- The additive noise model from v0.1 is kept only as a test switch for sensitivity runs, off by default.

## 9. Role adaptation
- **Archer**: platform eye point, cone faces downfield; radar sees only bodies inside its radius (rarely any), so the Archer is a cone athlete. Freeze and immunity status public.
- **Keeper**: cone centred on the ball; keeps the existing C4c ball-perception rule until PRISM replaces it; radar matters for attackers closing in the zone.
- **Field players**: facing from movement; radar sense of close contact; hearing a call (communication) is a third source with its own delay (open item).

## 10. Information model (all athletes)
Observed (cone), Sensed (radar blip), Remembered (decayed belief), Inferred (prediction), Communicated (calls). Each: timestamp, source, confidence. A belief may be wrong and is never silently corrected from engine state.

## 11. Acceptance tests (extends the 9 existing unit tests)
1. Raising Vision enlarges the cone and nothing else; raising Awareness enlarges the radar and nothing else (monotone, others fixed).
2. Clarity changes reading error and edge fade, not reach or angle.
3. Reaction changes delay only; Focus changes pulse rate, tracked count, gaze speed and persistence only.
4. A body behind an occluder is not detected by the cone; a body inside radar radius behind the athlete is sensed as a blip.
5. A blip carries no velocity until a second pulse.
6. Instinct changes classification time only.
7. All shadow-mode runs deterministic per seed; omniscient and shadow runs identical in play.
8. Calibration: belief error versus truth reported by rating band, in shadow mode before any decision uses the belief.

## 12. Open questions - status after Codex review (v0.1.1)
| # | Question | Recommendation (Codex, adopted as working default) | Status |
|---|---|---|---|
| 1 | Does radar partly block? | Test partial obstruction; never fully blocked | working default, see section 4 |
| 2 | Linear or curved ratings? | Linear first; test curves after calibration | working default |
| 3 | Minimum sensor sizes? | Yes, small physiological minimums (cone half-angle never below 60 deg, radar never below 3 m) | working default |
| 4 | Communication | Interface in v0.1 (a `communicated` source with its own delay), calls implemented in a later phase | working default |
| 5 | Existing `awareness` | Keep it; it maps directly to radar radius | working default (spec already does) |
| 6 | Public information | Score, game clocks, tackle count, freeze and immunity status; ammunition only when observably known or officially announced | working default |
| 7 | **Is radar literal or an abstraction?** | Abstraction (hearing + peripheral motion + spatial intuition) | **needs DreLen** |
Public status is separate from spatial knowledge: knowing a player is frozen or immune does not reveal where it is.

## 13. Change log
- v0.1.1: added section 3a (detection vs identification); radar interpretation, attenuation, bearing noise and crowding masking (section 4); Judgment rebuilt around option count, look-ahead and time pressure instead of random error (section 8); open questions answered with working defaults; minimum sensor sizes set; draft designated v0.1.1 pending the radar decision.
- Acceptance sequence (Codex): isolate each rating's effect; validate cone geometry, occlusion, radar pulses and latency; validate persistence, stale beliefs and velocity estimation; deterministic Archer shadow tests against the omniscient baseline; extend to field players and Keepers; only then replace omniscient decisions. Archer shadow and drive mode exist (9 unit tests); the rating-isolation tests wait for the new rating set.
