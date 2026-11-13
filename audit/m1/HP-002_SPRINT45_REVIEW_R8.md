# HP-002 — Review R8 of SPRINT-45 (branch experiment/prism-sprint-45, head c64d92e)
Claude, 2026-11-13. Experiment evidence only. Nothing here is acceptance of any milestone. Do not merge.

## OWNER BRIEFING
1. **Accomplished.** The build merged Round 1 onto Codex's M1 code with no conflicts, then added the possession and rules-state layer you settled, ruleset 1.0.2, a belief-driven Archer legality check, receiver cognition and a pass call, all inside one full match run. It finished in 29 min 45 s by its own clock log (budget 45). I reproduced it: 93 of 94 tests pass (the one failure is the known inventory-guard problem, 23 files never committed), and the seed-1 match reproduces both its trace hash and state hash exactly (c6768026..., f24fd174...). No B0 file changed (checked by diff against 2abe497).
2. **What B1 can do now.** A complete 2 x 120 s match runs from start to finish with every athlete (field, Keeper, Archer) deciding through the view/belief boundary, possession tracked per your definitions (direct, passive, contested, 500 ms), and zone violations turned into restarts. Seed 1: 8-8, decided by shootout 1-0, 56,011 decisions.
3. **Unproven or weak.** (a) 26,941 of 56,011 decisions (48%) are `home`: athletes walking to a slot-grid formation assigned from outside. That is the formation control the M1 rules forbid; the report lists it as a deviation but not how large it is. (b) Real choices are few: 101 pass, 371 carry, 7 shoot decisions in a whole match. (c) Passes mostly fail: of 56 pass outcomes, 22 reach a teammate, 16 are intercepted, 15 go out. (d) The engine still makes choices for athletes (Keeper save plan, restart taker and spot, Archer platform movement, wind-up refusal): the independent review rates OWN-5 FAIL. (e) Zone violation enforcement is shown by a wiring test with a fake violation; in the real match one violation was enforced. (f) Keeper-protection contacts checked in the match: 0. (g) The receiver changes have no tests. (h) M5 (gates, paired statistics, performance) not started.
4. **Blocking the next step.** M1 formal acceptance (your call), the engine-owned choices (OWN-5), and the formation anchor.
5. **Recommended action.** Treat this as a working skeleton, not progress toward acceptance. Do not merge. Next work in this order: replace `home` with belief-driven positioning (or declare it as the future team-plan layer in M2), move the Keeper save, restart and Archer movement choices behind athlete intents, add an end-to-end test for a real zone violation, then run paired multi-seed statistics.

## Milestone status (my rating; Codex's briefing agrees)
| Milestone | Status |
|---|---|
| M1 | IMPLEMENTED, TESTED (provisional baseline; not accepted) |
| M2 plans, communication | PARTIAL: primitive receiver cognition and one lossless pass call; plan layer missing |
| M3 all roles | PARTIAL: decisions via view/belief; save, platform movement, contact, restarts still engine-owned |
| M4 rules state, full match | PARTIAL: possession layer IMPLEMENTED and TESTED (30 unit tests); enforcement partial; KP-08, KP-OG missing |
| M5 gates and acceptance bundle | MISSING |

## Verified by me
- `pytest b1`: 1 failed, 93 passed in 82 s; the failure is `test_frozen_B0_file_identity` (23 listed files missing on a clean checkout; engineering item, not a B0 change).
- `python3 -m b1.match_run --seed 1`: trace_hash and state_hash identical to the committed evidence; 56,011 decisions; 70 s.
- `git diff --name-status 2abe497 HEAD -- . ':!b1'`: additions only.
- `MatchPort.deliver` (read): the live-state fallbacks flagged in the first independent review are gone; it raises if no delayed snapshot exists. Remaining non-snapshot reads: `self.public` (other players' role label, refreshed live at each capture; minor).
- Decision mix and pass outcomes from the run output (counts above).
- Canon check on the possession layer: the per-team 500 ms timer matches the decision record (R-03 says "for team X"); the independent review's worry on this point is not a defect.

## Findings
- **F1 (new): `home` is 48% of all decisions.** It is a slot-grid anchor imposed from outside the athlete (BA-7 / forbidden formation anchor). Acceptable only as a labeled placeholder for the future plan layer; it dominates how every match looks, so team-shape and spacing results are artifacts.
- **F2 OWN-5 FAIL (agree with the independent review).** Engine code chooses for athletes: Keeper save planner on true flight, restart taker and spot, Archer platform follows the true ball, `c3_withhold`.
- **F3 information boundary: partly regressed, partly design.** The delayed signals every athlete receives regardless of line of sight include every player's frozen/immune state, direct holder, passive team, contested flag and restart taker. My recommended default (behavioral, no owner decision): possession state, restart and score are public officiating signals; the identity of the direct holder and each player's frozen state should arrive through perception, not as exact data. Codex or the next sprint should change or justify this.
- **F4 BR-3 FAIL as written (two-argument `decide(view, belief)`),** and OWN-1/2/4/6, BR-4/5/7 rated WEAK in review 1. Not re-run after the fixes.
- **F5 receiver and pass-call changes untested,** and the `released:*` override lasts one delivery only. `released:restart_pass` is not in the override list.
- **F6 enforcement.** Restart spot hard-coded to field centre; ZR-C and ZR-T untested; violations outside live play are dropped without a ledger note; R-15 is recorded only.
- **F7 evidence volume.** Three extra seeds completed (no failures) with wildly different scores; no effect sizes are claimed and none should be read from this.

## What was useful
A single pipeline now exists for all athletes (one decision path, one release contract, one possession layer), the full-match runner works on Codex's code, and the possession layer is real and tested against the decision record. That is the base the next milestone work can replace piece by piece.

## Gates
BLK-01..05 unchanged. Nothing ACCEPTED. Do not merge the branch.
