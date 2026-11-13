# SPRINT-45 independent review (reviewer did not write the code)

Time-boxed (~8 min). Read-only. Nothing here is an acceptance. Items marked "not verified" were not run or not read.

## Commands run
1. `python3 -m pytest -q b1 2>&1 | grep -v "Warning\|Pocket20\|^  d = " | tail -8`
2. Inline `python3 - <<EOF` probes against `b1.possession.PossessionTracker` (results below).
3. Inline probe: `run_match(5,None,15000,False)` twice; `type(port.m).carrier_decision(port.m)`; AST import scan of `b1/cognition.py`, `b1/possession.py`.
4. Reading: `b1/matchport.py` 25-624, `b1/possession.py` all, `b1/cognition.py` 180-205 + greps, `b1/test_sprint.py` 36-67, 157-182, 221-253, 283-400, `core_src/match.py` 104-122, 808-822, 859-910, `pocket4_proto.py` 431-440.

## Test counts (exact)
`1 failed, 92 passed, 23 subtests passed in 70.85s`

- FAILED `b1/test_sprint.py::EngineIntegration::test_frozen_B0_file_identity` — `RuntimeError: B0 baseline verification failed`, 23 x `missing: ...` (LOCOMOTION_1_0_MANIFEST.json, baseline/*, codex_runs/*, tools/t1_*.py, ...). Count of 23 missing files confirmed. All 23 are "missing", none "modified". Whether they were "never committed" was not checked against git history.
- `test_primitives_are_registered_and_listed` PASSES, but only because it is vacuous: `SPRINT45_LIMITATIONS.md` does not exist (checked repo root and b1/) and the test body is guarded by `if lim.exists()` (test_sprint.py:394-398). The stated explanation "may fail until the file exists" is backwards: it cannot fail until the file exists.

## Verdicts

| ID | Verdict | Basis |
|---|---|---|
| OWN-1 | WEAK | Test (test_sprint.py:221) poisons positions, ball, phase, clocks, score, restart, quivers. It does not poison `s.ends`, `p.active`, `p.role`, ratings, RNG state, or the snapshot-fallback paths, all of which `deliver` reads live (see leaks L1-L4). Not a byte-compare over "every field not in the view". |
| OWN-2 | WEAK | Same single test, single instant (`now` of a twin port). Same uncovered live reads. |
| OWN-3 | PASS (run only) | test_sprint.py:75 passes; pure-cognition only; body of test not audited by me. |
| OWN-4 | WEAK | test_sprint.py:283 replays the first 60 sampled decisions and re-applies `max`. Requirement is 100% of intents; ID linkage is checked by string prefix only (:381-389). |
| OWN-5 | FAIL | Test covers pass target / shooter / arrow_draw target only. Engine code still chooses for athletes: legacy `c4c_keepers` save planner runs on true ball state for a Keeper (matchport.py:76, :465); restart forced ready after 3000 ms with no athlete choice (:308); engine `c3_withhold` (c3c=True in my run) refuses a commanded wind-up (core_src/match.py:861, :901); engine `targets_dead` picks the restart taker and moves players (core_src/match.py:104-122). Release window is never diffed. Both keeper and restart items are labelled PROVISIONAL in code; that does not make them pass. |
| OWN-6 | WEAK | Test (:337) checks only `track.captured_ms <= delivered_ms` and unique observation IDs. No check of `decided_at >= delivered_at`, cadence, or `not_before`. (`submit` does require `decided_ms == s.now`, matchport.py:227.) |
| OWN-7 | PASS (one scenario) | test_sprint.py:345, g1 only, one teleport. Does not assert uncertainty grows; asserts no new capture and no jump. |
| BR-1 | PASS | My AST scan: cognition imports `dataclasses`, `math`, `.core`; possession imports `dataclasses`, `math`, `typing`. |
| BR-2 | PASS | Substring scan as specified (test_sprint.py:58); my grep found none either. |
| BR-3 | FAIL (as written) / NOT TESTED | `decide(view: AthleteView, belief: BeliefState)` (cognition.py:203) takes two arguments. `BeliefState` is assembled by the runtime (matchport.py:218), including feedback and last-ball memory held in `MatchPort`. Checklist says the arguments are an `AthleteView` and immutable config. No test addresses arity. |
| BR-4 | WEAK | 40 samples, not each view; simulator-absence is a module blacklist (test_sprint.py:301). |
| BR-5 | WEAK | Test (:63) only compares dataclass field names. No SelfView perturbation run. |
| BR-6 | PASS (not random) | First 60 samples, deterministic slice, not a random 50; reconstruction goes through `view_from_json` on trace data. |
| BR-7 | WEAK | Traps fire (`carrier_decision` raises `RuntimeError: legacy tactical controller reached`, confirmed by me). But legacy `c4c_keepers` and `e.ready` are kept and called (matchport.py:76-77, :309, :465), and `make_pass`/`make_shot` prep still run (:387-389). "B0 tactical controllers unimportable" is not what is tested. |

## Specific checks
(a) `deliver` reads from live state, not the delayed snapshot:
- L1 matchport.py:189 — `snap['self'].get(pid) or (a.x, a.y, a.posture)`: live own position/posture when the athlete is not in the chosen snapshot (e.g. just activated).
- L2 matchport.py:187 — fallback `self.snaps[0][1]` when no snapshot is old enough: delivers data younger than the athlete's latency.
- L3 matchport.py:207-208 — `attack_sign`, `own_goal_x` from live `s.attack_sign` / `s.ends`; :199, :206 `a.role`, `a.team`, `a.slot` live. Called "static identity" in the comment; ends are not static if sides swap. Not verified whether they swap in this build.
- L4 matchport.py:152, :194, :207 — `immune` (every player's true immunity/frozen state), `direct_holder`, and `carrier` are true state delivered to every athlete regardless of line of sight. Delayed, but not perceived.
- Tracks come from the sensor (`pr.bget`), fine. `own_release`, `pending` are own-action memory.
(b) `_archer_motor` (matchport.py:397-450): confirmed no target-legality check. Remaining true-state gates are non-target: live/owner/eligible (:407), quiver (:412), ballistic range (:438). `m.e.shoot_arrow` may still reject (`rejected_by_engine`, :450); engine body not read. Legality is in `cognition.archer_target_legal` (cognition.py:194) and the `abort_draw` option (cognition.py:242).
(c) `_ball_motor`: release goes through `PhysicalExecutionPort._release_due`; from a grep of that function only `s.players[c.intent.athlete]` is looked up and `c.intent.target` is passed to `e.release` (runtime.py ~100, ~139). Full function not read. Receiver change raises (matchport.py:365-366). `make_pass(..., execute=False)` uses only `recipient.id` (core_src/match.py:859-871). Kind cannot change in the code I read.
(d) `_feed_rules` reads no belief object. Touch source = carrier + CONTESTED set + `touch` events. Consequence found by probe: one opponent `touch` event while a carrier holds the ball is treated as a contest and wipes direct possession (see P2b). ZR-1/ZR-C/ZR-T violations are only ledger rows: `matchport.py` contains no reference to them, the return value of `rules.step` is discarded (:537). R-15 is `recorded_only` (:517).
(e) Still decided by engine code: Keeper save plan (:465), restart readiness timeout (:308), restart taker and clearance movement (`targets_dead`), wind-up withholding (`c3_withhold`), archer placement (`pocket4_proto.py:431`, fixed platform), substitutions. `make_shot` prep also applies a true-state zone gate when `zone_only` (False in my run).
(f) Confirmed two arguments.
(g) Confirmed: `submit` rejects on true carrier (matchport.py:255) and true target existence/activity (:257); the reason is fed back into the athlete's belief (matchport.py:616-618).

## Possession probes (own scripts, default P-1 = 500 ms)
- P1 R-03 threshold: touching at 0, 100, 499 -> no DP; at 500 -> DP. At 499 none, at 501 DP. With 250 ms config: 249 none, 250 DP. No off-by-one found (`>=`).
- P1b R-03: A1 touches 0-400, A2 (same team) from 400 -> DP at 500 with holder A2 after 100 ms of contact. Timer is per team, not per player. Not checked against canon wording.
- P1c one empty step (no toucher) resets the timer: DP at 900 not 600. 
- P2 R-04: A from 0, both teams at 400, A alone from 500 -> no DP at 899, DP at 1000. Contest resets the timer.
- P2b A has DP; a single `touch` event by B at 600 -> `R-22 contested`, DP cleared, timer restarts next step.
- P3 R-10: A has PP; loose; B touches from 700 -> PP still A at 1199, flips to B at 1200. B touch 400 ms then pass to B2 for 100 ms -> PP stays A. Could not flip PP without DP.
- P4 R-13: ball in own zone, clock starts at the PP step (500); no violation at 5499; `ZR-1` at 5500. Not repeated afterwards, but the clock keeps running (8500 ms at t=9000) unless a restart event is fed. Leave zone (x=20.0, exclusive edge) and re-enter -> clock restarts from 0. Defender touch at 4000 -> clock reset. Loose ball in zone with PP and nobody touching -> ZR-1 fires after 5000 ms.
- Time going backwards raises `ValueError`.

## Engine probes
- `run_match(5,None,15000,False)` twice: `trace_hash` f8f108725e1b... equal, `state_hash` f6cd9c78b2f7... equal.
- That 15 s run contains 1 pass release, 2 arrows, 1 athlete abort, 9 rules-ledger rows. Evidence volume per run is thin.
- `type(port.m).carrier_decision(port.m)` raises `RuntimeError: legacy tactical controller reached`.

## Not verified
- Why the 23 inventory files are missing (git history not inspected).
- `runtime._release_due` in full, the 60 degree bound logic, `engine.shoot_arrow`, `engine.ready`, behaviour when `_restart_receiver` returns None.
- `b1/test_sprint45.py`, `b1/test_possession.py`, `test_m1.py`, `test_g1.py` bodies (run, not read).
- Whether L1/L2/L3 are reachable in a real run (no failing probe was built).
- CANON_NOTES / REVIEW_FINDINGS were only grepped, not read in full; probe expectations come from the code docstrings.
