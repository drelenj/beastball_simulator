# Beastball - Carry Poses, Evasion Maneuvers and Throw Transitions - spec v0.1.1 (DRAFT; DreLen's rulings of 31 Oct folded in)

Status: design rules only, nothing built. **[C]** = DreLen canon (his rulings), **[P]** = provisional number or choice for the simulator to tune. Ratings stay the only knobs; no maneuver has a hidden bonus.

## 1. Carry poses  [C]
| Pose | Definition |
|---|---|
| Exposed | ball secured by arm and hand only |
| Tucked | arm and hand, pinned to the torso |
| Braced | arm and hand, pinned to the torso, covered by the off arm |
| Loaded | ready to throw (formerly "cocked") |
| Extended | between Loaded and Exposed: more exposed than Exposed, but a quicker transition to a throw. May bypass Loaded for a quicker, weaker, less accurate pass (basketball touch-pass feel) |

Two ladders share the same five poses:
- **Security (strip/fumble resistance), best to worst:** Braced > Tucked > Exposed > Extended > Loaded.
- **Throw readiness, fastest to slowest:** Loaded > Extended > Exposed > Tucked > Braced.
- The carry-to-throw transition is a **cost** (possibly small) [C]. Provisional: each step between adjacent poses takes ~0.15 s [P], so Braced to Loaded is ~0.6 s and Extended to a touch pass is one step. The athlete is more strippable, and slower to turn, during a transition [P].
- Extended pass: **no distance restriction [C]**; no Loaded step required [C]. Power is the meaningful penalty: power x0.6 versus a Loaded pass [P]. Accuracy penalty is negligible for naturally accurate throwers [C]: modelled as reduced available impulse plus a small rise in release variability, sigma x (1 + 0.25 x (1 - Accuracy)) [P], so a high-Accuracy thrower is barely affected and a long touch pass is riskier only through its lower power (flight time, trajectory, interception window).
- A high wrap that pins the arms stops a throw not already started; the runner goes down or coughs it up [C]. Holds are split by the 10 anatomy parts: an arm pin hurts throws, a leg pin hurts kicks [C].

Which pose a carrier is in is public information to anyone who can see him; it is also a perception cue (section 5).

## 2. The three contact responses  [C, Oct 28]
The carrier's old native brake-before-contact is replaced by a **choice** of: **dodge / run through / brace**. This spec fills those three:
- **Dodge:** cut (exists), juke, spin.
- **Run through:** truck, stiff-arm.
- **Brace:** exists (set feet, slower, harder to put down).

A single defender must still be able to tackle a carrier in open space (strip from behind, ankle wrap, drag from behind, "hit sticking" with no grip) [C]; evasion changes the odds, never removes the threat.

## 3. Maneuvers (all numbers [P])
Each maneuver: pose requirement, physical effect, cost, counter, tell (what an observer can perceive before it resolves), rating link.

**Cut** (exists): hard plant-and-turn, grip x1.6, costs speed (cut_cost). Cooldown. Tell: low, plant foot ~0.1 s.

**Juke:** a lateral jink: path offset ~1.0 m over ~0.25 s, then resume. Pose **[C/draft]**: Exposed, Extended or Tucked. From Loaded he must first go to Extended **[C]** (0.15 s [P]); from Braced he must first go to Tucked (hips/shoulders need freedom). The transition completes before the maneuver begins. Cost: speed ~ the cut cost, plus a short exposed window while the feet re-plant. Counter: a defender who has NOT committed to a lateral line (low closing speed or already braking) simply stays on him; a fully committed defender at speed cannot re-angle in time. Tell: shoulder/hip dip ~0.15-0.25 s before the offset; a small tell for high Technique. Rating link: Agility (offset speed), Technique (smaller tell, cleaner re-plant).

**Spin:** a 360 deg rotation turning the back to the defender while the ball is shielded. Pose **[C]**: at least Exposed: Exposed, Tucked or Braced. From Loaded he must go through Extended to Exposed **[C]** (0.30 s [P]); Extended alone is not enough. (Supersedes v0.1, which required Tucked or Braced.) Cost: larger speed loss than a juke; ~0.35 s during which the carrier cannot see behind (his cone sweeps with the body: a PRISM interaction); a loose-grip contact during the spin has a chance to slip a light wrap (wrap quality x0.5 in the front zone) but a hard contact during the spin is a hit from the side/behind (more knock). Counter: contact timed before or after the rotation, or a second defender. Tell: a deep plant ~0.2 s before. Rating link: Agility, Balance, Technique.

**Stiff-arm:** the off arm extends to hold the defender at arm's length. Pose: Exposed or Tucked on the ball arm; **not Braced [C]** (the off arm is busy covering the ball). From Braced he must first go to Tucked, which temporarily lowers ball security. Effect: the contact begins at arm's length (no body impulse for the stiff-arm's duration), the tackler's grip quality x0.6, and the carrier keeps drive. Cost: ball arm pose is forced to Exposed/Tucked, a reach-limited window (~0.4 s), fatigue. Counter: a defender with longer reach, a second tackler, a hit from the side the arm is not covering. Tell: the off shoulder opens ~0.2 s before. Rating link: Strength, Technique, Reach (body size).

**Truck:** run through the defender with lowered shoulder. Pose: Braced or Tucked. Effect: the carrier's brace bonus (x1.6 today) applies and his delivered impulse is raised; outcome falls out of mass x velocity x brace (the existing contact model), no special rule. Cost: speed is NOT lost, but fatigue and an injury-load increase at the contact; a failed truck against a heavy, braced defender grounds the carrier. Tell: lowered shoulder ~0.2-0.3 s before contact. Rating link: Strength, Balance (sets what he absorbs), Technique (injury exposure).

Later candidates (not in v0.1): hurdle, dive for the line, swim/rip, one-hand carry transitions under a tackle.

## 4. Throw transition rules (Oct 29, restated)
- Power from the whole-body chain: **Throw Power** (strength side), **Throw Accuracy** (technique plus accuracy/precision) [C].
- Start with pass release, then shots; kicks keep their own foot-play rules [C].
- A carrier in Loaded cannot juke or spin directly **[C]**: juke needs Extended first, spin needs at least Exposed. Transitions are preparation cost, separate from the maneuver's own execution time, and must finish before the maneuver starts.
- A defender seeing a carrier leave Loaded for Extended cannot tell a touch pass from a juke: the pose is informative without revealing intent (an ambiguity PRISM's Recognition and Inference stages must handle).
- A defender who reads Loaded or Extended knows a throw is coming (a tell for lane/intercept play).

## 5. Perception hooks (what makes PRISM bite)
- **Tells have a visible window.** Each maneuver is preceded by a cue window (0.15-0.3 s). Observers detect it only if the carrier is inside their cone or radar with enough resolution; Clarity scales the detail they read, Focus whether they are watching him at all, Reaction how fast they act on it.
- **Instinct** = classify the cue (juke or spin or truck or none) before it resolves; **Anticipation** = predict the carrier's chosen path/response from pose, speed and context before any cue; **Judgment** = the carrier's own choice among dodge/run through/brace/throw (option count, how far ahead he scores threats), and a defender's choice to commit.
- The carrier's choice is scored from his OWN beliefs about the defenders (the carrier PRISM step already built), with pose and maneuver availability as the option set.
- Defender commitment is physical: it is set by his velocity, braking and turn limits (existing locomotion), not by a rating.

## 6. Rulings (31 Oct) - all [C]
1. Juke from Loaded: must transition to Extended first. Spin from Loaded: at least Exposed first.
2. Stiff-arm and Braced are mutually exclusive (off arm occupied).
3. Extended touch pass: no artificial range limit; power penalised, accuracy penalty negligible at high Accuracy.

## 7. Proposed build order
0. **Acceptance test first (built):** every maneuver obeys its required pose transitions, including interruption by contact (pose_maneuvers_v0.py + test_pose_maneuvers.py). Effectiveness is tuned only after this passes.
1. Prototype juke, spin, stiff-arm, truck on top of that state machine in a 1v1 lab (feel first, as before).
2. Port to the engine behind a flag; carrier option set = lane + maneuver + pose + pass.
3. Put defenders on PRISM, with decision regret on maneuver outcomes (the metric that separated ratings for the carrier).
