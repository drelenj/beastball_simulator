# HP-002 — Independent review of Codex's M1 candidate, packet 2 — R2
Claude, 2026-11-11 evening. Reviewed: packet 2 (`baseline/codex_evidence/M1/HP-001_B1_M1_EVIDENCE_PACKET_p2.zip`). Verdict: **R1 findings F1–F5 are fixed. M1 is NOT YET ACCEPTED: the athlete now senses the real world and decides honestly, but the slice is too thin to show the behavior M1 exists to show.**

## OWNER BRIEFING
1. **Accomplished.** Codex fixed all five blocking problems from my first review. The athlete now senses real bodies in the physics, knows where it actually is, looks where its own body faces, uses its own ratings, and decides six times in a run. I rebuilt it independently and got byte-identical results (10 tests pass; three sample runs match Codex's hashes).
2. **What B1 can do now.** A stationary carrier looks at a stationary teammate and a stationary defender through noisy, delayed perception, chooses pass or keep, winds up, and the real ball physics throws it. The throw goes where the athlete *believed* the teammate was. If the defender is not yet seen, the athlete passes into a blocked lane. If it is seen, the athlete keeps the ball. Moving the real athlete moves what it believes about itself. Scrambling every hidden attribute of other players, or moving a defender where it can't be sensed, changes nothing the athlete decides.
3. **Unimplemented or unproven.** Nobody moves. The defender never threatens the pass, the teammate cannot catch (the ball touches him and keeps going), so the run cannot produce completed, intercepted, dropped or tackled outcomes. The athlete is told what happened to its own action but does not use it. It also cannot tell that it is already winding up, so it re-decides "pass" every cycle and gets "busy" rejections.
4. **Blocking M1 acceptance.** Three things: (G1) the slice has no outcome diversity (no contest, no catch); (G2) the athlete has no knowledge of its own pending action and its feedback is not used; (G3) the claimed isolation test is still a tautology (my own physical version passes, so the code is sound; the test is not). None needs an owner decision.
5. **Recommended action.** Relay R2 to Codex. The next engineering step is a closing defender that moves under its own B1 decisions plus a catch path for the receiver, then the 100-seed outcome run. Keep M2 closed.

## 1. Reproduction (TESTED by me)
| Check | Result |
|---|---|
| Codex tests | 10 pass |
| pass / retain / interrupted re-run | execution hash, state hash, RNG signatures identical to Codex's files |
| M0 manifest | O4 v3.5, O5 v3.5 and V3.5 disposition hashes match my files exactly. The readiness-plan hash is of the joint document, which I cannot check |
| B0 | unchanged (same file-identity check as R1) |

## 2. R1 findings: disposition by me
| R1 | Status | My evidence |
|---|---|---|
| F1 sensor fixture | **CLOSED** | Bodies come from `s.players`. Physically moving B0 changes what is sensed |
| F2 constant self | **CLOSED** | Moved A0 to (70,20): view says (70,20); athlete sees 34 m to the teammate, beyond its 30 m limit, and keeps the ball |
| F3 scripted gaze/ratings | **CLOSED** | Ratings from `prism_ratings_v0`; eye and facing from the body |
| F4 poison test | **CODE CLOSED, TEST NOT** | My probe `audit/m1/m1_review_probe2.py`: sentinel every hidden attribute of A1 and B0 → identical view and decision. Move B0 to (2,95) → identical. Codex's test still cannot fail: `decide` takes only (view, belief), so mutating the engine afterward proves nothing, and the "changed" assertion compares a call to itself |
| F5 timing/feedback | **PARTLY** | Six decisions, stepped. Feedback reaches `BeliefState.own_feedback`, but `decide()` never reads it (see G2) |
| F8 stale beliefs | CLOSED (unit-tested, age rule works) |
| F10 constants | CLOSED (derived from config) |

## 3. Behavioral observations (what the traces show)
- **Honest belief.** I placed the defender physically at y = 50.8, 52, 53, 54, 55, 58 over 4 seeds. At the first decision (1300 ms) the defender is not yet in the athlete's belief in most seeds when 2 m or more off the lane (e.g. y=52: pass in seeds 1, 3, 4; keep only in seed 2, where the sensor happened to catch him). The athlete commits to a pass into a lane the defender physically blocks. That is correct information-limited behavior and a good demonstration of OWN-3. It is also why outcome diversity matters: nothing happens to that pass afterward.
- **Direction of effect.** When the defender is believed on the lane (y≈50.8) the athlete keeps the ball in all four seeds; when believed 4+ m off, passes. Matches the scoring rule.
- **Perception error reaches the throw** (seed-by-seed target differs by fractions of a metre).
- **Timing.** Actual decisions occur on a 100 ms grid (1300, 1500, 1700…), i.e. every 200 ms, while the trace reports `decision_period_ms=163` and `first_decision_ms=1222`. A decision is never earlier than delivery, so it is legal; the trace metadata misdescribes it (F14).

## 4. Blocking findings
**G1. No outcome diversity.** Teammate and defender are stationary. After release the ball reaches A1 at ~2050 ms and registers `physical_contact`; no catch is modeled, so `carrier` stays empty and the ball continues past him. Only three outcomes are reachable: released, interrupted, physical contact. The interrupted case is produced by the runner writing `freeze_until` on the athlete, not by anything in the world. *Requirement:* M1 outcome set (completed / intercepted / dropped / tackled), BA-M1-1/2. *Minimum correction:* (a) a defender body driven by its own B1 decision path (same boundary) that closes on the lane or the carrier; (b) the receiver's catch through the existing physical kernel so completion and interception are physical results; (c) the 100-seed × 4-condition run of `M1_SCENARIO_v1.json` with a failure-cause trace.

**G2. The athlete cannot tell what it is already doing.** `AthleteView` has no own-action state. In the pass run the athlete issues a second pass at 1500 while the first is winding up; ingress returns `resource_busy`, and nothing tells the athlete. In the interrupted run it simply re-passes at 1700 and succeeds — a retry that looks purposeful but is the same stateless rule firing again. `own_feedback` is stored but unused. *Requirement:* OWN-5/OWN-6, D1 (one plan at a time), directive "athlete owns its decisions". *Minimum correction:* SelfView carries pending-command state (id, release time); `decide` treats "continue current plan" as an explicit option; rejections and interruptions are delivered as feedback and the next decision visibly depends on them (counterfactual test: same view, different feedback → different intent).

**G3. The isolation test must be able to fail.** Replace it with the physical-state perturbation in my probe (sentinel hidden attributes; relocate an unsensed entity; hold the delivered frame fixed) and add the converse (change the delivered frame → decision changes). Test, don't claim.

## 5. Nonblocking findings
- F13 Feedback status `physical_contact` reports at the instant the ball touches A1, 15 m away, with no perception delay or range. Harmless while unused; once G2 makes feedback decisive, events about the ball far from the athlete must reach it through its sensor, not the feedback channel. Becomes blocking at that point.
- F14 Trace timing metadata (above).
- F15 The decision rule still uses no athlete rating, so ratings affect sensing only. Acceptable now; BA-M1-3 can only be shown through sensor-rating conditions.
- F16 Cognition is imported only through `from` statements; guard still `ast` of `ImportFrom`. Add `Import` nodes and the symbol scan BR-2 to the test.
- F17 Conformance profile `m1-pass-flight-v1` correctly lists nothing for catch/contest. Keep it as M1 step a; my `v1-m1` stays the completion target (decision still stands).
- F18 `M0_CLOSURE.md` / manifest: good. IMPL-04 widths and IMPL-05 EventTime unit are accepted by me as the M0 engineering defaults. IMPL-01..10 text is Codex's; I have not seen a prior version, so I record "reviewed, no objection" rather than authorship.
- Retain case holds forever at a defender 7 m away and does nothing; fine for M1 because movement is excluded.

## 6. Gate status
| Gate | Status |
|---|---|
| BLK-01 information isolation | Code TESTED by me (probe). Codex's own test is deficient (G3). Gate not yet met |
| BLK-02 no legacy override | TESTED, pass path |
| BLK-03 typed port | TESTED, release / interrupt / contact. Catch path absent (G1) |
| BLK-04 arbitration | TESTED, single resource |
| BLK-05 preservation | TESTED (file identity). T1 ten-case rerun not done |
ACCEPTED: none. (I still have only the gate titles, not the BLK text.)

## 7. Next steps (engineering only)
Order: G3 (small), G2, then G1. Report with OWNER BRIEFING; I will rerun the same independent checks plus OWN-3 physical sweeps and BR-4/BR-7.
