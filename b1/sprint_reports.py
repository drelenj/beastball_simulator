"""Generate SPRINT30_IMPLEMENTATION_REPORT.md and SPRINT30_OWNER_BRIEFING.md from recorded evidence."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
git = lambda *a: subprocess.run(['git', *a], cwd=ROOT, text=True, capture_output=True).stdout.strip()
S = json.loads((ROOT / 'b1/evidence_sprint30/summary.json').read_text())
SRC, BR = '8d98234', 'experiment/prism-sprint-30'
URL = 'https://github.com/drelenj/beastball_simulator'
code = git('rev-parse', 'HEAD')
files = git('diff', '--name-status', SRC, 'HEAD').splitlines()
log = (ROOT / 'SPRINT30_TIMING.log').read_text().strip().splitlines()
m, ms, rp, t = S['match_seed1'], S['multi_seed'], S['replay'], S['tests']
review = ROOT / 'b1/evidence_sprint30/INDEPENDENT_REVIEW.md'
tests_line = '; '.join(f"`{k}`: {v['ran']} -> {v['verdict']}" + (f" (not ok: {len(v['not_ok'])})" if v['not_ok'] else '') for k, v in t.items())
notok = [x for v in t.values() for x in v['not_ok']]
g1 = {}
for r in S['g1'] + S.get('g1_close', []):
    g1[r['terminal']] = g1.get(r['terminal'], 0) + 1
MILE = [
 ('M1 decision-to-outcome (one athlete + G1)', 'IMPLEMENTED as PRIMITIVE, TESTED (sprint tests)', 'Existing M1 slice reused unchanged. G1 closed by a new 3-athlete scenario where carrier, receiver and defender all decide through the same boundary; catch/interception/out-of-play decided by engine physics. Not the governed 100-seed G1 matrix (that exists separately at c083ae9 and was not used).'),
 ('M2 plans, communication, receiver cognition', 'PARTIAL (PRIMITIVE) / mostly MISSING', 'Receivers and loose-ball pursuit decide from own perception. Plan layer, PlanStageActivation, ReactionGate, communication channel, give-and-go: MISSING.'),
 ('M3 all roles under the boundary', 'IMPLEMENTED as PRIMITIVE, TESTED (sprint tests)', 'Field, Keeper and Archer cognition all run from own AthleteView/BeliefState; legacy controller trapped at class level. Keeper/Archer are PROVISIONAL; Keeper save execution delegates to the B0 kernel; no per-role conformance sets.'),
 ('M4 rules state, restarts, full match', 'PARTIAL (PRIMITIVE)', 'Full B0-P4-DEFAULT match (2 x 120 s, ruleset 1.0.1) runs to FINAL with scoring, clock, periods, restarts, fouls all enforced by the frozen B0 engine. No B1 rules-state table or rule-event ledger; restart placement and substitutions are engine procedures; canon gates U-1..U-4, R-RS, SELF-1 open. 4 x 600 s league profile not run.'),
 ('M5 gates A/B/C, performance, acceptance bundle', 'MISSING', 'Only determinism replay and a small multi-seed smoke run exist. No behavioural gates, no B0-vs-B1 distributions, no performance budget.'),
]
common = f"""- Branch: `{BR}` ({URL}/tree/{BR})
- Source commit: `{SRC}` (branch `b1/m1-decision-outcome`; its tip had moved to `c083ae9`, not used)
- Code+evidence commit these reports were generated from: `{code}` (the report commit follows it; see `git log`)
- Frozen B0: `2abe497`, no B0 file changed (`git diff --name-status 2abe497 HEAD -- . ':!b1'` shows additions only)
- Measured clock (`SPRINT30_TIMING.log`): first `{log[0]}`, last `{log[-1]}`
"""
repro = """```
pip install scipy numpy
python -m b1.match_run --seed 1 --out /tmp/match_seed1.json
python -m b1.match_run --scenario g1 --seed 1
python -m unittest b1.test_sprint -v && python -m unittest b1.test_m1
python -m b1.sprint_evidence 2 3 4 && python -m b1.sprint_reports
```"""
I = ['# SPRINT30 IMPLEMENTATION REPORT', '', 'Experimental build. Status words used: DESIGN COMPLETE / IMPLEMENTED / TESTED / ACCEPTED. **Nothing is ACCEPTED.**', '', common,
     '## Changed files (vs source commit)', '', '```', *files, '(plus the report files committed after this was generated)', '```', '',
     '## Pipeline as built', '',
     '`engine state -> PRISM sensor per athlete (B0 ArcherPrism: FOV, latency, noise, memory) -> AthleteView + BeliefState -> cognition.decide -> ActionIntent -> ingress -> MotorCommand -> B0 physics (Match.step) -> PhysicalOutcome -> own-action feedback into the next decision`', '',
     '## Architectural decisions', '',
     '1. **B0 `Match.step` is the physics/rules stepper.** It is not edited. Every legacy tactical entry point it calls is replaced on the instance by a B1 command reader (`_ball_motor`, `_archer_motor`, `_keeper_motor`, `_targets`, `_restart_receiver`) and the original functions are replaced by traps on the loaded classes (`carrier_decision`, `arrow_decisions`, `c4c2_decide`/`pocket_decide`, `c4c2_targets`, `route_receiver`, `c4c2_inbound`, `penalty_targets`, `Policy.targets/pass_choice/pass_ranked`).',
     '2. **One sensor per athlete** (lazy, seeded by seed+athlete id), ticked every 100 ms; the ball is one more sensed body (PRIMITIVE). Decisions fire per athlete at its own perception latency and decision interval.',
     '3. **Cognition is a pure module** (`b1/cognition.py`, imports only `dataclasses`, `math`); views/beliefs are frozen dataclasses and JSON round-trip.',
     '4. **Motor cannot change kind/target/receiver:** `pass_ranked` returns `[]` so the engine cannot substitute a receiver; shot aim point and arrow aim come from the intent.',
     '5. **Feedback:** released / interrupted / release_failed / rejected_* statuses return only to the acting athlete; a failed kind is excluded from its next decision. World results (pass_completed, pass_intercepted, goal_for, ...) are trace-only.',
     '6. **Causal IDs:** `s30/<ms>/<athlete>/obs` -> `/decision` -> `/intent` -> `/command`; outcomes carry the command id.',
     '7. **Determinism:** trace hash = SHA-256 over every decision row (id, kind, target, aim, admission, command id) and every outcome; state hash over final state.', '',
     '## Milestone status (experiment evidence, not acceptance)', '', '| milestone | status | notes |', '|---|---|---|', *[f'| {a} | {b} | {c} |' for a, b, c in MILE], '',
     '## Deviations from specs', '', '- BR-3 (two-argument `decide`), BA-7 (slot-grid positions), O4 action-resource model reduced to ball/bow/locomotion with one pending command, O5 IDs simplified, CFG-5 (unresolved values) not implemented, public signals without latency. Full list: `SPRINT30_LIMITATIONS.md`.', '',
     '## Tests run', '', f'- {tests_line}', *[f'  - NOT OK: `{x}`' for x in notok],
     f"- Deterministic replay seed 1 (two processes): identical = **{rp['identical']}**",
     f"- End-to-end match seed 1: `{m.get('status')}`, {m.get('result')}, {m.get('decisions_total')} decisions {m.get('decisions_by_role')}",
     f"- Additional full-match seeds: attempted {ms['attempted']}, completed {ms['completed']}, failed {ms['failed']}",
     f'- G1 scenarios (24 runs: 12 open + 12 contested) terminals: {g1}',
     f"- Independent review by a fresh agent: {'`b1/evidence_sprint30/INDEPENDENT_REVIEW.md`' if review.exists() else 'NOT COMPLETED in time'}", '',
     '## Tests not run', '', '- 4 x 600 s league profile, RULES_V03 profile, 100-seed matrices, behavioural gates, performance budget, B0-vs-B1 comparison.', '',
     '## Known defects / incomplete milestone requirements', '', 'See `SPRINT30_LIMITATIONS.md` (all PRIMITIVE modules, canon gates, defects) and the independent review.', '', '## Reproduce', '', repro, '']
(ROOT / 'SPRINT30_IMPLEMENTATION_REPORT.md').write_text('\n'.join(I))
O = ['# SPRINT30 OWNER BRIEFING', '', '**Nothing is ACCEPTED. This is experiment evidence for your review.**', '', common,
     '## 1. What was accomplished', '',
     f"A complete, runnable, primitive PRISM pipeline: all 24 on-field athletes (10 field players, Keeper, Archer per side, plus substitutes as they enter) each decide from their own delayed, noisy, field-of-view-limited perception, and the frozen B0 engine executes their commands. One full match ran to the final whistle: {m.get('result')} with {m.get('decisions_total')} athlete decisions. The same seed run twice gave identical hashes: {rp['identical']}.", '',
     'Run it: `pip install scipy numpy && python -m b1.match_run --seed 1 --out /tmp/match_seed1.json`', '',
     '## 2. What B1 can actually do now', '',
     '- Field players carry, pass, shoot, press the carrier, pursue loose balls and receive passes; catches, interceptions, tackles, goals and fouls are decided by the B0 physics and rules, never by the decision code.',
     '- Keepers position and can issue a save intent; Archers draw and release at the believed opposing carrier (both PROVISIONAL).',
     '- The legacy tactical controller is trapped: calling it raises an error, and the match completes without it.', '',
     '## 3. What remains unimplemented or unproven', '', '| milestone | status | notes |', '|---|---|---|', *[f'| {a} | {b} | {c} |' for a, b, c in MILE], '',
     'Every decision rule is a hand-set primitive, so the scores say nothing yet about how real PRISM athletes would play. Seed-1 match: Keepers issued 1 save intent; Archers released 50 arrows with 0 freezes.', '',
     '## 4. What is blocking the next step', '', '- Your canon decisions: U-1..U-4 (Keeper zone, zone clock, restarts), R-RS (ruleset 1.0.1 vs 1.0.2), SELF-1 (Archer foul mapping).',
     '- Reconciling this sprint with the governed G1 work at `c083ae9`.', '- The B0 inventory guard lists 23 files that are not in git, so it fails on any clean checkout.', '',
     '## 5. Recommended action', '', 'Review `SPRINT30_LIMITATIONS.md` and the independent review; decide the canon items; then follow `SPRINT30_UNLIMITED_STRATEGY.md` (keep the skeleton and boundary tests, replace primitives in milestone order). Do not merge this branch.', '',
     '## Tests', '', f'- {tests_line}', *[f'  - NOT OK: `{x}`' for x in notok],
     f"- Matches: seed 1 completed; additional seeds attempted {ms['attempted']}, completed {ms['completed']}, failed {ms['failed']}.", '',
     '## Reports', '', *[f'- {URL}/blob/{BR}/{f}' for f in ('SPRINT30_OWNER_BRIEFING.md', 'SPRINT30_IMPLEMENTATION_REPORT.md', 'SPRINT30_TEST_REPORT.md', 'SPRINT30_LIMITATIONS.md', 'SPRINT30_UNLIMITED_STRATEGY.md', 'SPRINT30_EXECUTION_STRATEGY.md', 'b1/evidence_sprint30/INDEPENDENT_REVIEW.md', 'b1/SPRINT30_README.md')], '']
(ROOT / 'SPRINT30_OWNER_BRIEFING.md').write_text('\n'.join(O))
print('reports written from', code)
