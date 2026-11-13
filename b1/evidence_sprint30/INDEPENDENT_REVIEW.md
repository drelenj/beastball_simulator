# SPRINT-30 independent review

Reviewer did not write the code. Branch `experiment/prism-sprint-30`. No file other than this one was changed. Nothing here is "accepted"; verdicts are per requirement, from reading test + covered code and from the probes listed.

## Commands run and exact counts

| Command | Result |
|---|---|
| `python -m unittest b1.test_sprint -v` (filtered) | Ran 26, **25 ok, 0 failures, 1 error** (20.3 s). Error: `EngineIntegration.test_frozen_B0_file_identity` |
| `python -m unittest b1.test_m1` | Ran 12, **OK** (8.1 s) |

`test_frozen_B0_file_identity` error: `verify_baseline` reports 23 `missing:` files. Checked: `b1/evidence/b0_source_hashes.json` has 235 entries; 23 are absent from `git ls-tree -r 2abe497`, absent from HEAD, and absent on disk (e.g. `LOCOMOTION_1_0_MANIFEST.json`, `codex_runs/reg_s1..5.json`, `tools/t1_*.py`, `commit_tree_2abe497.txt`). The "inventory lists never-committed files" explanation is confirmed for the tree of 2abe497 and HEAD (other branches not searched). `git diff --name-status 2abe497 HEAD -- . ':!b1'` shows only 3 added files (`SPRINT30_*.md/.log`), no modified or deleted file. The test still errors; the hash check of those 23 files is unverifiable.

## Probes I ran (inline scripts)

- `run_match(5,None,15000,False)` twice: `trace_hash` and `state_hash` equal (`851a04beee0002fe…`, 1684 decisions).
- `type(port.m).carrier_decision(port.m)` raises `RuntimeError: legacy tactical controller reached`.
- Own AST scan of `b1/cognition.py`: imports `{dataclasses, math}`; no `global`/`nonlocal`, no `__import__/eval/exec/open`.
- `inspect.signature(decide)` = `(view: AthleteView, belief: BeliefState)`.
- `run_match(1,None,60000,True)`: 8 `restart_release` events, all (taker,target) match a `restart_pass` intent; 6 `pass_plan`/6 pass releases; **5 `shoot` intents, 0 shot releases** (7 `rejected_not_prepared`); 1 engine `release kind=loose forced=True` with no command; 5 engine substitutions; no archer ever in `port.move`.

## Verdicts

| ID | Verdict | Basis |
|---|---|---|
| OWN-1 | WEAK | `test_OWN1_OWN2…` poisons only 6 fields (strength, tackling, passing, fatigue, minor_count, immune_until) and post-capture x/y/v of `role=='field'` players. Not poisoned: keepers, archers, ball position, RNG states, timers, ratings, `s.restart`, quivers, posture. The ball carrier is skipped (`continue`, test_sprint.py:197-198). The fields that actually come straight from engine state in `deliver` are never poisoned, so the test cannot fail on them. |
| OWN-2 | WEAK | Same test. Passes for what it perturbs; `deliver` reads true state at decision time (below), and none of those reads is perturbed. |
| OWN-3 | PASS (unit only) | `test_OWN3…` on hand-built views: value drops with defender on lane, rises when moved off. "Not seen" case covered only by the stale-track test. Not exercised through the runtime. |
| OWN-4 | WEAK | Test replays 60 sampled decisions and re-applies the rule; ID links are `startswith` string checks. "100% of intents" not checked (sample is first 60 + every 397th). Belief revision -> observation(s) link is one id prefix; the sensor frames that produced a track are not referenced. No stochastic draws exist. |
| OWN-5 | WEAK / FAIL in part | Test compares engine `pass_plan`, shot `release`, `arrow_draw` against the *set* of all (athlete,target) intents in the run, not per command; `chains` is capped at 260 (matchport.py:473); shot aim, restart receiver and release window are not checked. Engine-made choices exist (see findings 3-6). |
| OWN-6 | WEAK | Test checks only `track.captured_ms <= delivered_ms` and unique observation ids. `decided_ms >= delivered_ms` is true by construction (same `now`); cadence and `not_before` are not tested; there is no `not_before` field. |
| OWN-7 | WEAK | Assertions sit under `if tr is not None:` (test_sprint.py:294) so the test passes vacuously if the track is absent. No check that age/uncertainty grow; `Track` has no uncertainty field. Track x,y is extrapolated to now by `bel.at(t)` (matchport.py:137) while `captured_ms` stays old. |
| BR-1 | PASS | Test scans `Import` and `ImportFrom`; my own scan agrees. |
| BR-2 | PASS | Substring scan of the listed symbols; none present. |
| BR-3 | NOT TESTED; FAIL as worded | No BR-3 test. `decide(view, belief)` takes two arguments (cognition.py:157); the requirement is one function of an `AthleteView` + immutable config. `BeliefState` is built by the runtime (`deliver`), not by cognition, so belief update lives outside the cognition module. No module-level mutable state found. |
| BR-4 | PASS (40 samples, not "each view") | Subprocess replay byte-identical; forbidden-module list checked in the child. |
| BR-5 | WEAK | Test only lists dataclass field names. No perturbation test. Motor hooks are closures over the engine, not a separable MC with a signature. |
| BR-6 | WEAK | Same replay as OWN-4. Sample is deterministic (first 12 + every 397th), not random; "reconstruct knowledge from trace" is re-running `decide` on the recorded view+belief. |
| BR-7 | WEAK / FAIL in part | Class traps verified for 5 Match methods + 3 Policy methods. But legacy `Match.c4c_keepers` is saved and called every step (matchport.py:52, 367); legacy `e.ready` is called (236); `targets_dead`, `update_archers`, `auto_substitutions`, `make_pass`, `make_shot` are untrapped B0 code that still runs. |

## Leaks and violations (file:line)

1. **True engine state read at decision time in `MatchPort.deliver`** (matchport.py:146-160): own exact `a.x, a.y` (155), `s.ball.carrier == pid` (156), `s.possession_ms` and `s.game_ms` (149), `s.phase`, `s.restart` team/xy and taker flag incl. engine-chosen `m.restart_taker` (148-151), team quiver `q.loaded`/`q.last_release` (159-160), `a.posture` (160). These are unfiltered, zero-latency, zero-noise. Some are arguably proprioception/public signals, but `possession_ms` is a rules timer (U-2 open) and drives a +5.0 shoot bonus (cognition.py:224). None is covered by the poison test.
2. **Public identity of unseen bodies**: `self.public` gives team/role for every player (matchport.py:116-117, 139); acceptable only if uniform role is canon.
3. **Keeper saves are planned by the B0 planner**, not the athlete: `_keeper_motor` runs `_orig_keepers` (matchport.py:367); cognition only emits `keeper_save` with an aim that the planner does not use. A keeper with `c4c_launch` set keeps executing regardless of its current intent (363, 378). Marked PROVISIONAL in code; still an OWN-5 violation.
4. **Dead-ball positioning and restart taker are chosen by the engine**: `core_src/match.py:104` `targets_dead` picks the taker (nearest eligible) and all dead-ball targets; it is not hooked. `home`/`keeper_set` intents in dead phases are not what moves the players.
5. **Archer locomotion is engine-owned and uses the true ball x**: `core_src/match.py:808-814` `update_archers`; `_targets` excludes archers (matchport.py:229).
6. **`_ready` fallback** (matchport.py:235): after 3000 ms the engine restart proceeds without any athlete choice; `_restart_receiver` then returns None (240). What the engine does with None was not traced.
7. **Ingress leaks truth as feedback**: `unknown_target` / `infeasible` rejections come from true `s.players[...].active` and `s.ball.carrier` (matchport.py:194-197) and feed `banned` in cognition.
8. **Shot preparation calls legacy `m.make_shot(p)`** (matchport.py:294) and passes go through `m.make_pass` (283, 296); release velocity/lead are engine-planned. In my 60 s run no shot was ever released (5 intents, 0 releases), so the shot path's intent-vs-release identity is unexercised by any evidence.
9. Engine-forced `release kind=loose` and substitutions occur with no intent/outcome record.
10. Dead code: `if not failed or True:` (cognition.py:216).

## Not verified

- Internals of `prism_archer_v0.ArcherPrism` (whether `deliver`/`bget` are honest about latency and occlusion); whether `bel.t` is capture time.
- Whether `make_pass` can retarget inside the engine (`pass_ranked` is stubbed to `[]`; match.py:656, 879 not read in full).
- Engine behaviour when `_restart_receiver` returns None.
- Full-length match; cross-process determinism beyond the suite's own test.
- The 23 missing inventory files' hashes; branches other than 2abe497/HEAD.
