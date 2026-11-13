# SPRINT45 IMPLEMENTATION REPORT

Experimental build. Status words: DESIGN COMPLETE / IMPLEMENTED / TESTED / ACCEPTED. **Nothing is ACCEPTED.**

- Branch: `experiment/prism-sprint-45` (https://github.com/drelenj/beastball_simulator/tree/experiment/prism-sprint-45)
- Source commits: Base A `4b19719` (`b1/m1-decision-outcome`) merged with Round 1 `99cf83a` (`experiment/prism-sprint-30`), `git merge --no-ff`, no conflicts
- Code+evidence commit these reports were generated from: `f59f6c06c990a09c3a26d1086791c59aca2a11d5` (the report commit follows it; see `git log`)
- Frozen B0 `2abe497`: no B0 file changed (`git diff --name-status 2abe497 HEAD -- . ':!b1'` shows additions only)
- Measured clock (`SPRINT45_TIMING.log`): first `2026-11-13T05:20:31Z PHASE_A_START`, last `2026-11-13T05:42:38Z PHASE_D_START_FEATURE_FREEZE_EVIDENCE_RUN`

## 0. Integration result (Phase B step 0)

- Branch created from `4b19719` (the prompt names its parent `77604e1` in Phase A and `4b19719` in section 2 and Phase B; `4b19719` was used) and pushed empty first.
- Round 1 merged cleanly. Before any Round 2 change: `pytest -q b1` gave 51 passed, 1 failed (the known inventory guard), and the seed-1 match reproduced Round 1 exactly (9-3, 42,143 decisions, trace hash `02b95a47...`).
- Nothing from Round 1 was lost. No Codex test was changed; `core.py` and `runtime.py` are unmodified.

## Changed files (vs Base A)

```
A	SPRINT30_EXECUTION_STRATEGY.md
A	SPRINT30_IMPLEMENTATION_REPORT.md
A	SPRINT30_LIMITATIONS.md
A	SPRINT30_OWNER_BRIEFING.md
A	SPRINT30_TEST_REPORT.md
A	SPRINT30_TIMING.log
A	SPRINT30_UNLIMITED_STRATEGY.md
A	SPRINT45_EXECUTION_STRATEGY.md
A	SPRINT45_LIMITATIONS.md
A	SPRINT45_TIMING.log
A	SPRINT45_UNLIMITED_STRATEGY.md
A	b1/SPRINT30_README.md
A	b1/SPRINT45_README.md
A	b1/cognition.py
A	b1/evidence_sprint30/INDEPENDENT_REVIEW.md
A	b1/evidence_sprint30/g1_seed1.json
A	b1/evidence_sprint30/match_seed1.json
A	b1/evidence_sprint30/summary.json
A	b1/evidence_sprint30/summary_before_archer_interlock.json
A	b1/evidence_sprint30/tests_test_m1.txt
A	b1/evidence_sprint30/tests_test_sprint.txt
A	b1/evidence_sprint45/INDEPENDENT_REVIEW.md
A	b1/match_run.py
A	b1/matchport.py
A	b1/possession.py
A	b1/registry.py
A	b1/sprint30/OWN_BR_CHECKLIST.md
A	b1/sprint45/CANON_NOTES.md
A	b1/sprint45/REVIEW_FINDINGS.md
A	b1/sprint45_evidence.py
A	b1/sprint45_reports.py
A	b1/sprint_evidence.py
A	b1/sprint_reports.py
A	b1/test_possession.py
A	b1/test_sprint.py
A	b1/test_sprint45.py
(plus report files committed after this was generated)
```

## Architectural decisions

1. **One pipeline.** `cognition.decide` delegates carry-vs-pass and defender pursuit/lane sub-decisions to Base A `core.decide`; pass releases execute through Base A `PhysicalExecutionPort._release_due` (pass-release-v1, 60 degree bound) via a duck-typed adapter. The Round 1 use of the B0 pass planner on true receiver state is removed.
2. **Possession/rules-state layer** `b1/possession.py`: pure module, authoritative, fed only by engine events in `MatchPort._feed_rules` (carrier, CONTESTED mode, touch, release, strip, boundary, restart, goal, period). It never reads beliefs. Its public state reaches athletes only inside the latency-delayed snapshot as rules signals.
3. **Ruleset 1.0.2** is set through the B0 engine configuration switch on the B1 match instance only.
4. **Archer legality is a belief decision.** The motor has no true-state check; cognition filters targets and can `abort_draw`; a wrong belief becomes an engine foul.
5. **Keeper protection** from the view only (Keeper track inside own zone while his team has passive possession): no press, no Archer target; breaches counted in the ledger.
6. **Zone violations** found by the layer are enforced through a B0 restart award (provisional spot).
7. **View construction never reads live state** for self or public data: it raises if no snapshot older than the latency exists.
8. **Outcome causes come from engine events**; a score change during a flight without a matching goal event is `unknown:`.

## Milestone status (experiment evidence, not acceptance)

| milestone | status | notes |
|---|---|---|
| M1 decision-to-outcome (one athlete + G1) | IMPLEMENTED (Base A, provisional; NOT accepted, H3 open) | Base A code and its 25 tests are kept unchanged and pass. Its `core.decide` and pass-release-v1 release code now also run inside the N-athlete loop. |
| M2 plans, communication, receiver cognition | PARTIAL (PRIMITIVE) | Receiver cognition (pass call, intercept of the believed ball path) and one lossless team shout exist. Plan layer, PlanStageActivation, ReactionGate, real communication channel, give-and-go: MISSING. |
| M3 all roles under the boundary | PARTIAL (PRIMITIVE) | Field, Keeper and Archer decide from own view/belief; Archer legality is belief-driven (true-state interlock removed); Keeper protection respected in cognition. Still engine-owned: Keeper save execution (C4c kernel), Archer platform movement, contact micro-behaviour, restart placement, substitutions. |
| M4 rules state, restarts, full match | PARTIAL (PRIMITIVE) | New authoritative possession/rules-state layer (R-01..R-22 as transitions, unit-tested) runs in every match and feeds zone violations to B0 restarts; ruleset 1.0.2 on the B1 instance. Scoring, fouls, other restarts and the clock remain B0 state; KP breaches recorded only; KP-08/KP-OG missing; 4 x 600 s profile not run. |
| M5 gates A/B/C, performance, acceptance bundle | MISSING | Only replay determinism and a small multi-seed smoke run. No behavioural gates, no paired statistics, no performance budget. |

## Deviations from specs

- See `SPRINT45_LIMITATIONS.md`: BR-3, BA-7, record-only KP breaches, provisional RST-1 spot, touch source, public signals, engine-owned procedures.

## Tests run

- `python3 -m pytest -q b1`: **1 failed, 93 passed, 23 subtests passed in 73.62s (0:01:13)**; per file {'b1/test_g1.py': 7, 'b1/test_m1.py': 18, 'b1/test_possession.py': 30, 'b1/test_sprint.py': 29, 'b1/test_sprint45.py': 9}
  - NOT OK: `FAILED b1/test_sprint.py::EngineIntegration::test_frozen_B0_file_identity - R...`
- Deterministic replay seed 1 (two processes): identical = **True**
- End-to-end match seed 1: `final`, {'winner': 'A', 'method': 'shootout', 'score': {'A': 8, 'B': 8}, 'shootout': {'A': 1, 'B': 0}}, 56011 decisions {'archer': 4377, 'field': 48123, 'keeper': 3511}
- Rules ledger seed 1: 543 entries, by row {'R-02': 95, 'R-03': 88, 'R-06': 59, 'R-07': 4, 'R-08': 19, 'R-09': 10, 'R-10': 32, 'R-12': 1, 'R-14': 72, 'R-17': 3, 'R-18': 90, 'R-20': 70}, violations enforced 1
- Pass releases seed 1: {'bound_deg': 60.0, 'max_correction_deg': 39.184, 'recomputed': 59, 'rejected_geometry': 0, 'releases_recorded': 59}; pass outcomes {'pass_completed': 9, 'pass_completed_other': 13, 'pass_dead:boundary': 15, 'pass_dead:restart_awarded': 3, 'pass_intercepted': 16}; unattributed outcomes (`unknown`): 2
- Additional full-match seeds: attempted 3, completed 3, failed 0
- G1 scenarios, 12 seeds each: open {'pass_completed': 12}; defender on lane {'pass_completed': 10, 'pass_intercepted': 2}
- Independent review by a fresh agent: `b1/evidence_sprint45/INDEPENDENT_REVIEW.md`. It ran before the last fixes (no live-state fallback in `deliver`, non-vacuous primitives test, extended poison test, violation enforcement); those are NOT re-reviewed. Its OWN-5 FAIL (engine procedures still choosing for athletes) and BR-3 FAIL stand.

## Tests not run

- 4 x 600 s profile, 100-seed matrices, paired sign tests, behavioural gates, performance budget, B0-vs-B1 comparison, regeneration of the Base A G1 matrix.

## Known defects / incomplete milestone requirements

See `SPRINT45_LIMITATIONS.md` and the independent review.

## Reproduce

```
pip install scipy numpy pytest
python3 -m pytest -q b1
python -m b1.match_run --seed 1 --out /tmp/match_seed1.json
python -m b1.sprint45_evidence 2 3 4 && python -m b1.sprint45_reports
```
