# HP-002 — Independent review of Codex's M1 candidate (packet 1) — R1
Claude, 2026-11-11. Reviewed: `HP-001_B1_M1_EVIDENCE_PACKET.zip` (copy and SHA256 in `baseline/codex_evidence/M1/`). Verdict: **M1 NOT ACCEPTED YET. Candidate is a sound partial; three blocking findings concern where the athlete's information comes from.**

## OWNER BRIEFING
1. **Accomplished.** Codex delivered the first running B1 code: one athlete perceives, chooses pass or keep, winds up, and the real ball physics releases the ball. I rebuilt the workspace myself, re-ran everything, and got byte-identical results. I then ran my own probes.
2. **What B1 can do now.** The decision function is clean: it sees only what it is handed, and I could replay its decisions from the saved trace in a process with no simulator loaded. Motor Control throws at where the athlete *believes* the teammate is, so perception error shows up in the throw. Legacy controllers are trapped. B0 is untouched.
3. **Unimplemented or unproven.** The athlete is not yet looking at the simulated world. What it "sees" is a hand-typed list, its own position is a typed-in constant, and its eyes are pointed at the teammate by the test script. There is no receiver, catch, defender body, interception, tackle, movement or second decision. So "the athlete owns its decision" is proven only for the last step (belief → choice → throw), not for the whole chain.
4. **Blocking M1 acceptance.** Findings F1–F5 below. None needs an owner decision; they are engineering corrections for Codex.
5. **Recommended action.** Send this review to Codex. Keep M1 open; no M2. Nothing for you to decide.

## 1. Reproduction (TESTED by me)
| Check | Result |
|---|---|
| 8 Codex tests | pass, 6.7 s |
| pass / retain / interrupted re-run | execution hash, state hash and RNG signatures identical to Codex's files |
| B0 files | 212 files common to Codex's tree and my `git archive 2abe497`: all identical. Codex's tree has 23 extra evidence files I do not have; no B0 source differs |
| BR-4 serialization replay | decisions rebuilt from JSON trace alone, no simulator modules loaded: intent and option scores identical |
| OWN-3 sensitivity | believed defender 0–3.4 m off the lane → retain; ≥3.5 m → pass. Choice follows the stated scoring rule |
| Belief → throw | seed 8: teammate believed at y=49.74 → throw vy=−0.47. Perception error propagates to the physical throw |

## 2. BLOCKING findings (failure scenario / requirement / minimum correction)
**F1. The sensor reads a hand-written fixture, not the physical world.** `run.py` passes `bodies=[dict(id='A1',x=55,y=50…)]` to the sensor. In the physics, A1 is at (29, 28) and inactive; only A0 is active. The "defender" in the retain case exists only in that list. *Requirement:* real PRISM decisions with authoritative physical outcomes (directive req. 2), BLK-01, BLK-03. *Correction:* the projector builds sensor input from a read-only projection of the physical state; teammate and defender are real active bodies.

**F2. The athlete's self-knowledge is a constant.** `AthleteView(…,40.,50.,holds_ball,…)` and the eye position `(40,50,1.8)` are literals; `holds_ball` defaults to True. Probe: I moved the physical A0 to (70, 20); the view still said (40, 50), the athlete chose the same pass, and Motor Control threw from (70, 20) toward the old aim. *Requirement:* SelfView from proprioception (T6, D6). *Correction:* derive self position and ball possession from the athlete's own body projection.

**F3. Attention and sensor ratings are scripted.** The sensor is told to look at `(55,50)`, the teammate's exact fixture position, so the athlete finds the teammate because the test aims its eyes there. The sensor is built with awareness 0.5 while A0's rating is 0.82, and `apply_ratings` is never called (no radar, no rating-driven cone). *Requirement:* BA-M1-3/4, no outside-assigned targets. *Correction:* gaze driven by the athlete's own belief or facing; sensor parameters from the athlete's ratings.

**F4. The isolation ("poison") test proves nothing.** `test_hidden_state_cannot_enter_decision` changes a local dict that is never passed to anything. *Requirement:* BLK-01, OWN-1/OWN-2. *Correction:* after F1, perturb true state with the delivered frame held fixed and assert identical decisions; perturb the frame and assert change.

**F5. When and how often the athlete decides is fixed by the script.** One decision at 1500 ms; time is set by assignment (`s.now = 1500`), not advanced. Outcome feedback is returned to the runner and never reaches belief or a later decision. *Requirement:* OWN-6, decision-to-outcome cycle. *Correction:* a stepped loop (sense → deliver → decide at cadence → command → physics → feedback into the next view) with at least two decisions in one run.

## 3. NONBLOCKING findings
- F6 Telemetry-off test compares the same computation (Codex says so).
- F7 Import test inspects `from … import` only; I read `core.py` by hand and it is clean.
- F8 View and belief carry identical contacts; observation age (`captured_ms`) is ignored. A 100-second-old sighting is treated as current.
- F9 The option rule uses no athlete rating, so every athlete decides identically. Acceptable for M1 if stated; BA-M1-3 cannot be shown until it changes.
- F10 Wind-up uses literal 250 rather than `assume['pass_release_ms']`, and truncates to whole ms. Desired speed 27 m/s: I could not locate its source in B0 `match.py`/`policies.py`; Codex to cite.
- F11 IDs are not yet `beastball-causal-v1` (Codex says so).
- F12 Codex's `M0_CLOSURE.md` says M0 is closed but records no contract hashes and cites IMPL-01..10 without text. There are now two conformance profiles (Codex `m1-pass-flight-v1`, mine `v1-m1`). Proposal: Codex's profile is M1 step a (pass-flight); mine is the M1 completion target (real teammate and defender, catch/intercept/tackle outcomes). I accept Codex's integer-ms, UInt64 choices as the M0 engineering defaults.
- Legacy traps are a name list; sufficient now because `step` is trapped and only `advance_ball`, `release`, `eligible`, `follow_carrier` are called. BR-7 (unimportable legacy controllers) still to do.

## 4. Gate status (titles from Codex's report; I still have not seen the BLK text itself)
| Gate | Status |
|---|---|
| BLK-01 information isolation | Decision function: TESTED (mine). Sensor boundary: NOT MET (F1–F4) |
| BLK-02 no legacy override | TESTED for pass path; movement path not implemented |
| BLK-03 typed physical port | IMPLEMENTED for release/interrupt; inputs not from physical world (F1) |
| BLK-04 deterministic arbitration | TESTED single resource only |
| BLK-05 preservation | TESTED (file identity, mine and Codex's); T1 ten-case rerun not done |
ACCEPTED: none.
