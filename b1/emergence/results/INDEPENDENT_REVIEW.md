# EMERGENCE-1 independent review (reviewer did not write the code)

Commit 39d5025, branch experiment/emergence-1. Nothing here is ACCEPTED. Budget: 8 min, CPU-limited
(search running), so evidence is code reading plus five 8-simulated-second probes on seed 3.

## Commands run
- `git diff c64d92e HEAD -- b1/cognition.py b1/matchport.py`; full read of `params.py`, `positioning.py`, `harness.py`, `search.py`, `metrics.py`.
- Pure probe: AST import scan; `PolicyParams` with 7 / NaN / inf / bool / str / negative / unknown field; `choose_position` with a believed opponent moved, weights zeroed, iterated alone.
- Match probe: `run_match(3, None, 8000, False, policies={'A':P1,'B':P2})`, same with `B:P3`, then `B:P2` again in the same process with an `on_view` poison (all true bodies and ball moved, both `port.policies` entries swapped, `decide` re-run, state restored) on 300 decisions.
- Decision probe: one captured `position` view: believed opponent moved, all tracks aged, `slot` changed, JSON round trip in a subprocess.

## Verdicts (new code only)
| ID | Verdict | Evidence / limit |
|---|---|---|
| OWN-1 | PASS (limited) | 300 poisoned re-decisions, 0 records differ; trace hash equals the unpoisoned run. The record holds no candidates or term scores, so "byte-identical record" covers less than the check asks. |
| OWN-2 | PASS (limited) | Same probe: true bodies/ball moved, view fixed, selection unchanged. |
| OWN-3 | WEAK | Opponent term only: moving a believed opponent moved the aim (61.6,42.0 -> 65.8,40.2); `pos_opp_att=pos_lane=0` removed the effect. Ball, goal, spread, edge terms not probed. |
| OWN-4 | FAIL | `cognition.py:214` discards the score and candidate count; the record has only `['position', mode, aim, 1.0]`. Candidates and per-term scores are not recorded. |
| OWN-5 | NOT TESTED | Ingress target vs intent aim not checked. `home` chosen 0 times in 879 decisions. The "fallback flag" the check names does not exist. |
| OWN-6 | PASS (limited) | `deliver` precedes `decide` in the loop; min per-athlete gap 200 ms over 8 s. |
| OWN-7 | PASS (limited) | `mates`/`opps` come from `fresh` tracks only; with all tracks aged the athlete chose `search`. |
| BR-1 | PASS | `positioning.py` imports `math`; `params.py` imports `dataclasses`. |
| BR-2 | PASS | Read in full: no engine symbols, no RNG, module state is the immutable `STEP`/`DIRS`/`BOUNDS`. |
| BR-3 | WEAK | Params arrive as a view field, no global or closure. But one object is shared by the port and every teammate view and `object.__setattr__` mutates it (probe succeeded). |
| BR-4 | PASS (1 sample) | Subprocess `view_from_json` -> `decide`: identical record, no simulator module loaded. |
| BR-5 | PASS (by grep) | `policies` is read only in `deliver` (`matchport.py:235`) and `run_match` header/result. |
| BR-6 | NOT TESTED | No 50-sample reconstruction. With `telemetry=False` (what the harness uses) no view is stored, so it cannot be done from harness output at all. |
| BR-7 | NOT TESTED | No full match run; no trap fired in 8 s. |

Parameter injection: bounds/NaN/inf/bool/str/unknown rejected: PASS. Teammates identical: PASS (2 distinct
objects across the run, A always P1, B always P2). Own preferences only: PASS (first 12 team-A decisions at
t=300 ms identical for B=P2 vs B=P3; team-A records identical over the first 400 views). No mid-match change:
PASS over 8 s (id and hash constant). Determinism: same-process repeat after a different match gave the same
hash (8 s only); serial vs parallel and full length NOT TESTED. Logged vector equals used vector: WEAK (below).

## Constants that are not parameters
| Constant | Where | Biases what can emerge? |
|---|---|---|
| Value 1.0 of the position option | `cognition.py:221` | Yes, strongly. The positioning score never competes with pursue/press/pass; the 9 `pos_*` weights only pick where, never whether. |
| STEP 6 m, 9 candidates (stay + 8) | `positioning.py:9-11` | Yes. Greedy one-step horizon; nothing farther than 6 m is ever compared. |
| Caps: opponent 10, teammate 12, `_nearest` default 30, lane 10 | `:15,28,53,58,59` | Yes. Spacing has no gradient beyond 12 m, marking none beyond 10 m; these fix the scale of "good" spacing. |
| 0.1 scale on distance terms, but not on the edge/zone penalty | `:50-59,64` | Yes. Fixes the exchange rate between distances and the penalty; `pos_edge_zone` can rescale it. |
| Edge band 6 m, clamp 3..97 | `:45-46,60-61` | Yes. Outer 3 m unreachable by positioning. |
| Zone penalty 1, both Keeper zones | `:62-63` | Yes. Alone in `def` mode with defaults an athlete converges to exactly (20, 50), the zone rim on the goal axis: a built-in attractor. |
| Goal at (own_goal_x + 100*sign, 50) | `:42,52,57` | Yes. Goal pulls aim at the centre point only. |
| `none` mode = mean of the two ball weights, no goal/opponent terms | `:49` | Yes. Before first possession only ball, spread and edge act. |
| Teammates = role `field` only; opponents = all but archers | `cognition.py:218-219` | Yes. Keepers never count for spread; hard-coded role knowledge. |
| Mode from `signals.passive_team` | `cognition.py:208-209` | Yes. Two-phase attack/defend split is imposed, not learned. |
| DIRS order, tie threshold 1e-12 | `positioning.py:10,66` | Mild. Ties resolve to "stay"; all-zero weights give a stationary team. |
| Restart branch uses `restart_xy` as the "ball" | `cognition.py:293-294` | Mild. Fixed rule, not a weight. |

## Violations and defects
1. `cognition.py:214` — per-candidate scores discarded; OWN-4 fails by the checklist's own wording.
2. `params.py:58,68` — `as_dict`/`key` round to 4 decimals. `PolicyParams(bias_pass=1e-5)` and `(4e-5)` are unequal but log and hash identically (`matchport.py:628,712`, record at `cognition.py:425`). The search is unaffected (`clip` rounds), direct callers are not.
3. `cognition.py:132-142` — `home_position` (reads `view.slot`) is still defined and registered (`registry.py:4`); `'home'`, `'mark'`, `'support'` remain in `LOCOMOTION` (`matchport.py:21`). No caller in `decide`; changing `slot` did not change a decision. Dead but importable. `cognition.py:289` `ref` is now a dead variable.
4. `matchport.py:61` — unknown team keys in `policies` (e.g. `'a'`) are ignored and the team silently gets DEFAULT. `cognition.py:77,443` — a missing policy silently becomes DEFAULT; `from_dict` fills absent fields with defaults.
5. `search.py:28-29` — rows whose status is not `final` are dropped from the standings. A vector that crashes or stalls matches loses no points; entrants are ranked on total points over unequal `played`.
6. `search.py:69` — stopping rule is wall-clock, so the number of generations depends on machine load; a search run is not reproducible end to end.
7. `search.py:72,86` — one match seed per generation; elites chosen from 2 matches per pairing. `best_label` reflects the last generation only. `search.py:44` — exact ties go to the alphabetically first label, i.e. `baseline`.
8. `harness.py:67` — `matches.jsonl` is opened in append mode; a second search run reuses ids such as `1000:45:baseline>g0m1` for different vectors in the same file.
9. `harness.py:41-45`, `metrics.py:34-35,61-62` — metric import failure and hook exceptions are swallowed with no counter; `metric_errors` covers `finalize` only. Metrics can be silently partial.
10. `harness.py:78` — forked workers play up to 8 matches each while `MatchPort.__init__` rewrites module globals and `os.environ` (`matchport.py:47-58`). No leak seen in my A,B,A repeat at 8 s; not shown at full length.

Fitness (`search.standings`) uses only status, score and winner: a pure match result apart from item 5.
Metrics collector: no writes to the port by reading; `on_decision`/`on_step` receive the live port, so the
read-only property is by convention, not enforced.

## Not verified
Full-length matches, the test suite, serial vs parallel hashes, trace hash with vs without the collector,
OWN-5 ingress equality, BR-6, BR-7, every positioning term other than the opponent ones, `readout.py`/`final.py`.
