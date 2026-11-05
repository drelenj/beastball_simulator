# PRISM v0.1.2 - Draft Specification: Perception and Information (draft for DreLen and the lead)
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
- Edge softness: detection probability outside the fovea falls smoothly from 1 to 0 across the band between fovea and edge: `p(e) = clamp(1 - ((e - fovea) / (theta - fovea))^k)` with exponent `k = 1 + 2 x Clarity` **[P]** (v0.1.2, Codex fix of the reversed exponent: high Clarity = detail retained deep into the periphery, then a late, abrupt edge; low Clarity = early, gradual fade; p always reaches 0 at the cone edge). Today's code uses a flat `0.35 + 0.40 x awareness` outside the fovea; this replaces it.
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


## v0.1.2 resolutions (31 Oct 2026)
- **Radar is an abstraction** of hearing, nonvisual motion cues and spatial intuition, not a literal sense. Per-pulse probability uses Codex's reference function (range x motion x 0.7^blockers / (1+0.1 x crowd)). All constants remain [P].
- **Clarity exponent** fixed (above). Vision alone sets cone size; Awareness alone sets radar size.
- **Tracks are anonymous.** `Tracker2` (prism_perception_v012.py): predicted-position gating, optimal one-to-one assignment, ambiguity flag when a rival track is almost as plausible; confidence halves on ambiguous tracks. True player ids never reach the tracker. Fast crossings resolve via motion prediction; slow close pairs stay flagged ambiguous. Production still needs multi-hypothesis association for sustained pile-ups.
- **Rating isolation contract** (`OWNS`, tested): each rating may change only its listed profile parameters, every parameter has exactly one owner.
- **Not yet wired into the Archer**; the shadow module still uses the v0 cone. Gate passed: shadow on/off gives identical game results (seeds 1-3).

## Shadow wiring result (31 Oct)
Flags in prism_archer_v0.py: `PRISM_SOFT=1` (Codex cone, `PRISM_CLARITY` default .5), `PRISM_TRACK=1` (anonymous Tracker2 diagnostic, never feeds decisions). Defaults unchanged; 3-game results identical in all three configs.
Track identity swaps (seeds 1-3, ~240k observations): hard cone 4.4% (10,424), soft cone 2.5% (6,522). Ambiguity flag covers 8% of observations and catches 42% of swaps (hard) / 45% (soft). 

## Track-driven Archer (31 Oct, flags `PRISM_DRIVE=1 PRISM_SOFT=1 PRISM_TRACKID=1`)
The Archer no longer reads beliefs by true player id: sightings go through the anonymous tracker; a track takes an identity at first sighting, refreshed whenever a player is seen in the fovea (`PRISM_REIDENT`, default on). Tracks older than 4 s are dropped. `PRISM_AMBIG=hide` withholds ambiguous tracks from targeting.
Freezes over 6 full games (platform 15 m, 250 m/s): omniscient 33 | belief by true id 27 | tracks, no re-identification 14 | tracks + re-identification 25 | + hide ambiguous 24.
Wrong-identity sightings: 50% (no re-id) -> 5% (re-id). Non-carrier freezes fall (6 -> 2): identity doubt costs the non-carrier shots first. Hiding ambiguous tracks gained nothing.

## Rating sweep (31 Oct; track-driven Archer, platform 15 m, 250 m/s, 10 short games per cell, neutral = all .5)
Freezes (carrier + non-carrier): neutral 15 (8+7).
| Rating | 0.1 | 0.9 |
|---|---|---|
| Vision | 9 | 32 |
| Clarity | 12 | 29 |
| Reaction | 17 | 27 |
| Focus | 14 | 22 |
| Awareness | 20 | 18 |
Count noise is about +/-4 (Poisson), so only Vision, Clarity and Reaction(high) clearly separate. Awareness (radar) is flat: the platform sits 15 m up behind the goal, so few bodies are inside a 3-15 m radar, 20-480 blips per 10 games against ~480k cone detections. Instinct, Anticipation, Judgment have no Archer hook yet (not swept).

## Anticipation sweep (31 Oct; Archer, 16 short games per cell)
Hook: velocity blended toward "head for the goal you attack" (weight 0.7 x Anticipation x heading consistency, 0 at >=70 deg off).
Anticipation 0 / .25 / .5 / .75 / 1.0 -> freezes 21 / 32 / 23 / 16 / 21 (carrier 12/21/12/5/9). Mean belief-aim miss 3.88 / 3.59 / 3.51 / 3.66 / 3.67 m.
Non-monotone and inside count noise (about +/-5): NO measurable effect for the Archer. Aim error is ~3.5 m, set mostly by observation delay, which a heading prior cannot fix. Anticipation needs a role where intent beats delay (defenders reading cuts, Keepers reading shooters).

## Judgment sweep (31 Oct; Archer, Anticipation pinned at 0; flag PRISM_JUDGE=1)
Hook (all provisional): options kept = 2 + 4J (carrier always included, ranked by predicted distance to goal L seconds ahead, L = .5 + 1.5J); re-decides every .2(1.5 - J) s, holding fire between decisions.
Run 1 (seeds 1-16), freezes: no-Judgment 21 | J 0: 19 | .25: 34 | .5: 22 | .75: 28 | 1.0: 37.
Run 2 (new seeds 17-32): no-Judgment 28 | J 0: 26 | J 1: 28. Ablations at J=1: interval only 28 | options only 25 | options+lookahead 27.
The run-1 gap did not replicate. Pooled 32 seeds: no-Judgment 49, J 0: 45, J 1: 65 (difference ~1.6 sigma at count noise): NOT a reliable effect. Conclusion: like Anticipation and Awareness, Judgment is flat for the Archer, whose single repeated decision leaves little room for deliberation to pay off.
Method note: a 16-game cell has count noise of about +/-5-6, and one such gap vanished on replication; promote a rating effect only after replication on fresh seeds.

## Field players, step 1: the ball carrier (31 Oct; prism_field_v0.py, flag PRISM_FIELD=1, ratings via PRISM_FIELD_RATINGS)
Every field player has its own cone/radar perception; only the CARRIER's decisions read it (lane choice, pass ranking). Defenders, off-ball players, Keepers still omniscient; teammates, ball, public status true.
Game level (8 seeds): tackles ending carries 69 omniscient vs 75-101 (mean ~88) in all 11 perceiving configs; individual ratings not separable at game-level noise (+/-9).
Decision level (5 seeds, ~7.8k carrier decisions per cell; regret = true lane score of best lane - true score of lane chosen from beliefs, metres of room):
neutral .50 | Vision .1/.9: .56/.47 | Focus .1/.9: .57/.49 | Clarity .1/.9: .57/.53 | Reaction .1/.9: .51/.50 | Awareness .1/.9: .53/.56 (wrong way, noise).
Best-lane rate 58-63%; hidden-opponent share 17% (Vision/Focus .9) to 44% (Vision/Focus .1). Direction right for Vision, Focus, Clarity; effects are small (regret moves ~15%) because lane choice is coarse (5 lanes, 4 nearest opponents) and ~1 m position error rarely flips it.
Conclusion: carrier lane choice is robust to perception quality; the carrier is a weak lever. Defenders (pursuit angle, tackle timing, reading cuts and passes) are where the ratings should bite.
