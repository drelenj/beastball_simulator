# Beastball - Carry Poses, Evasion Maneuvers and Throw Transitions - spec v0.1 (DRAFT for Codex review)

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
- Extended pass: power x0.6, accuracy x0.7 versus a Loaded pass [P]; no Loaded step required [C].
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

**Juke:** a lateral jink: path offset ~1.0 m over ~0.25 s, then resume. Pose: any carry pose except Braced (hips/shoulders need freedom) and not mid-transition. Cost: speed ~ the cut cost, plus a short exposed window while the feet re-plant. Counter: a defender who has NOT committed to a lateral line (low closing speed or already braking) simply stays on him; a fully committed defender at speed cannot re-angle in time. Tell: shoulder/hip dip ~0.15-0.25 s before the offset; a small tell for high Technique. Rating link: Agility (offset speed), Technique (smaller tell, cleaner re-plant).

**Spin:** a 360 deg rotation turning the back to the defender while the ball is shielded. Pose: Tucked or Braced (Exposed or Extended would spill). Cost: larger speed loss than a juke; ~0.35 s during which the carrier cannot see behind (his cone sweeps with the body: a PRISM interaction); a loose-grip contact during the spin has a chance to slip a light wrap (wrap quality x0.5 in the front zone) but a hard contact during the spin is a hit from the side/behind (more knock). Counter: contact timed before or after the rotation, or a second defender. Tell: a deep plant ~0.2 s before. Rating link: Agility, Balance, Technique.

**Stiff-arm:** the off arm extends to hold the defender at arm's length. Pose: Exposed or Tucked on the ball arm; **not Braced** (the off arm is busy covering the ball). Effect: the contact begins at arm's length (no body impulse for the stiff-arm's duration), the tackler's grip quality x0.6, and the carrier keeps drive. Cost: ball arm pose is forced to Exposed/Tucked, a reach-limited window (~0.4 s), fatigue. Counter: a defender with longer reach, a second tackler, a hit from the side the arm is not covering. Tell: the off shoulder opens ~0.2 s before. Rating link: Strength, Technique, Reach (body size).

**Truck:** run through the defender with lowered shoulder. Pose: Braced or Tucked. Effect: the carrier's brace bonus (x1.6 today) applies and his delivered impulse is raised; outcome falls out of mass x velocity x brace (the existing contact model), no special rule. Cost: speed is NOT lost, but fatigue and an injury-load increase at the contact; a failed truck against a heavy, braced defender grounds the carrier. Tell: lowered shoulder ~0.2-0.3 s before contact. Rating link: Strength, Balance (sets what he absorbs), Technique (injury exposure).

Later candidates (not in v0.1): hurdle, dive for the line, swim/rip, one-hand carry transitions under a tackle.

## 4. Throw transition rules (Oct 29, restated)
- Power from the whole-body chain: **Throw Power** (strength side), **Throw Accuracy** (technique plus accuracy/precision) [C].
- Start with pass release, then shots; kicks keep their own foot-play rules [C].
- A carrier in Loaded cannot also juke or spin (a throwing posture): a maneuver forces at least one transition step first [P]. DreLen to confirm.
- A defender who reads Loaded or Extended knows a throw is coming (a tell for lane/intercept play).

## 5. Perception hooks (what makes PRISM bite)
- **Tells have a visible window.** Each maneuver is preceded by a cue window (0.15-0.3 s). Observers detect it only if the carrier is inside their cone or radar with enough resolution; Clarity scales the detail they read, Focus whether they are watching him at all, Reaction how fast they act on it.
- **Instinct** = classify the cue (juke or spin or truck or none) before it resolves; **Anticipation** = predict the carrier's chosen path/response from pose, speed and context before any cue; **Judgment** = the carrier's own choice among dodge/run through/brace/throw (option count, how far ahead he scores threats), and a defender's choice to commit.
- The carrier's choice is scored from his OWN beliefs about the defenders (the carrier PRISM step already built), with pose and maneuver availability as the option set.
- Defender commitment is physical: it is set by his velocity, braking and turn limits (existing locomotion), not by a rating.

## 6. Open questions for DreLen
1. Is a maneuver from Loaded allowed (with the cost), or must a carrier leave Loaded first?
2. Stiff-arm and Braced are mutually exclusive here (the off arm is covering the ball). Is that the intent?
3. Should the Extended touch pass be range-limited (short only) or is the lower power/accuracy penalty enough?

## 7. Proposed build order
1. Prototype juke, spin, stiff-arm, truck and the pose ladder in the chase lab (feel first, as before).
2. Port to the engine behind a flag; carrier option set = lane + maneuver + pose + pass.
3. Put defenders on PRISM, with decision regret on maneuver outcomes (the metric that separated ratings for the carrier).
